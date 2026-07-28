#!/usr/bin/env python3
"""Validate and copy the dependency-free HI Inspector static bundle."""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
from html.parser import HTMLParser


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site" / "inspector"
PUBLIC_CANONICAL = "https://senyo888.github.io/humidity-intelligence/inspector/"
OFFICIAL_LOGO = ROOT / "assets" / "logo.png"
OFFICIAL_LOGO_REFERENCE = "../assets/logo.png"
FILES = (
    "app.mjs",
    "handoff.mjs",
    "index.html",
    "inspection-session.mjs",
    "parser.mjs",
    "styles.css",
)
FORBIDDEN_CAPABILITIES = (
    "fetch(",
    "xmlhttprequest",
    "websocket",
    "eventsource",
    "sendbeacon",
    "serviceworker",
    "localstorage",
    "sessionstorage",
    "indexeddb",
    "document.cookie",
    "document.execcommand",
    "http://",
    "https://",
    "<form",
    "@import",
    "url(",
)


class _ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []
        self.images: list[tuple[str, str, str | None, str | None, str | None]] = []
        self.csp = ""
        self.referrer = ""
        self.robots = ""
        self.inline_script_text = ""
        self._in_script_without_src = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        if tag == "link" and values.get("href"):
            self.references.append(("link", values["href"]))
        if tag == "img" and values.get("src"):
            self.images.append(
                (
                    values["src"],
                    values.get("alt") or "",
                    values.get("width"),
                    values.get("height"),
                    values.get("aria-hidden"),
                )
            )
        if tag == "script":
            source = values.get("src")
            if source:
                self.references.append(("script", source))
            else:
                self._in_script_without_src = True
        if tag == "meta":
            name = (values.get("name") or "").lower()
            http_equiv = (values.get("http-equiv") or "").lower()
            content = values.get("content") or ""
            if http_equiv == "content-security-policy":
                self.csp = content
            elif name == "referrer":
                self.referrer = content
            elif name == "robots":
                self.robots = content

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_script_without_src = False

    def handle_data(self, data: str) -> None:
        if self._in_script_without_src:
            self.inline_script_text += data


def validate_sources(source: pathlib.Path | None = None) -> None:
    source = source or SOURCE
    if (
        not OFFICIAL_LOGO.is_file()
        or OFFICIAL_LOGO.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n"
    ):
        raise RuntimeError("Official HI logo asset is missing or is not a PNG")
    actual = sorted(path.name for path in source.iterdir() if path.is_file())
    if actual != sorted(FILES):
        raise RuntimeError(
            f"Static source allowlist mismatch: expected {sorted(FILES)}, got {actual}"
        )

    sources = {
        filename: (source / filename).read_text(encoding="utf-8")
        for filename in FILES
    }
    if sources["index.html"].count(PUBLIC_CANONICAL) != 1:
        raise RuntimeError(
            "Inspector HTML must contain exactly one public canonical URL"
        )
    scan_sources = {
        **sources,
        "index.html": sources["index.html"].replace(PUBLIC_CANONICAL, "", 1),
    }
    combined = "\n".join(scan_sources.values()).lower()
    for token in FORBIDDEN_CAPABILITIES:
        if token in combined:
            raise RuntimeError(f"Forbidden Inspector capability or reference: {token}")

    app_source = sources["app.mjs"]
    executable_sources = {
        filename: contents
        for filename, contents in sources.items()
        if filename.endswith(".mjs")
    }
    clipboard_modules = [
        filename
        for filename, contents in executable_sources.items()
        if "navigator.clipboard" in contents
    ]
    if (
        clipboard_modules != ["app.mjs"]
        or sum(
            contents.count("navigator.clipboard")
            for contents in executable_sources.values()
        )
        != 1
        or sum(
            contents.count("clipboard.writeText")
            for contents in executable_sources.values()
        )
        != 2
        or app_source.count("navigator.clipboard") != 1
        or app_source.count("clipboard.writeText") != 2
        or app_source.count("() => clipboard.writeText(copyText)") != 1
        or any(
            re.search(r"\bclipboard\.(?!writeText\b)[A-Za-z_]\w*", contents)
            for contents in executable_sources.values()
        )
    ):
        raise RuntimeError(
            "Inspector clipboard use exceeds the explicit handoff write allowlist"
        )

    parser = _ReferenceParser()
    parser.feed(sources["index.html"])
    if sorted(parser.references) != [
        ("link", OFFICIAL_LOGO_REFERENCE),
        ("link", PUBLIC_CANONICAL),
        ("link", "styles.css"),
        ("script", "app.mjs"),
    ]:
        raise RuntimeError(
            f"Inspector HTML references are not allowlisted: {parser.references}"
        )
    if parser.images != [
        (OFFICIAL_LOGO_REFERENCE, "", "40", "40", "true")
    ]:
        raise RuntimeError(
            f"Inspector official-logo markup is not allowlisted: {parser.images}"
        )
    if parser.inline_script_text.strip():
        raise RuntimeError("Inline scripts are not permitted")
    for directive in (
        "default-src 'none'",
        "img-src 'self'",
        "connect-src 'none'",
        "worker-src 'none'",
        "form-action 'none'",
        "base-uri 'none'",
    ):
        if directive not in parser.csp:
            raise RuntimeError(f"Inspector CSP is missing: {directive}")
    if "frame-ancestors" in parser.csp:
        raise RuntimeError(
            "frame-ancestors is not valid in a meta-delivered CSP"
        )
    if parser.referrer != "no-referrer":
        raise RuntimeError("Inspector must use a no-referrer policy")
    if set(parser.robots.split(",")) != {
        "noindex",
        "nofollow",
        "noarchive",
        "nosnippet",
    }:
        raise RuntimeError("Inspector must remain non-indexable")


def build(destination: pathlib.Path) -> None:
    validate_sources()
    destination = destination.resolve()
    if (
        destination == ROOT
        or destination == SOURCE
        or SOURCE in destination.parents
    ):
        raise RuntimeError("Build destination must be outside the source tree")
    if destination.exists() and not destination.is_dir():
        raise RuntimeError("Build destination must be a directory")
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError("Build destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
        shutil.copyfile(SOURCE / filename, destination / filename)

    logo_destination = (destination / OFFICIAL_LOGO_REFERENCE).resolve()
    try:
        logo_destination.relative_to(destination.parent)
    except ValueError as err:
        raise RuntimeError(
            "Inspector logo reference must stay inside the build root"
        ) from err
    logo_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OFFICIAL_LOGO, logo_destination)
    if logo_destination.read_bytes() != OFFICIAL_LOGO.read_bytes():
        raise RuntimeError("Built Inspector logo does not match the official asset")

    print(
        "HI Inspector static build passed: "
        f"{len(FILES)} files plus official logo -> {destination}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "destination",
        type=pathlib.Path,
        help="explicit empty output directory for the validated static bundle",
    )
    args = parser.parse_args()
    build(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
