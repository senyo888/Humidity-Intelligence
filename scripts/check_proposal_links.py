#!/usr/bin/env python3
"""Validate clickable local file links in proposal Markdown surfaces."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


PROPOSAL_SURFACES = (
    Path("PROPOSALS.md"),
    Path(".codex/governance/proposals"),
    Path("sandbox/v2.1"),
)

ROOT_FILE_NAMES = {
    "AGENTS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "DESIGN_BRIEF.md",
    "PROJECT_SUMMARY.md",
    "PROPOSALS.md",
    "README.md",
    "ROADMAP.md",
    "SECURITY.md",
}

LOCAL_ONLY_EXACT = {"AGENTS.local.md"}
LOCAL_ONLY_PREFIXES = (
    ".codex/private/",
    "/config/",
)

PATH_PREFIXES = (
    ".codex/",
    "assets/",
    "automations/",
    "docs/",
    "helpers/",
    "sandbox/",
    "scripts/",
    "sensors/",
    "tests 2/",
    "ui/",
    "ui-gallery/",
)

COMMAND_PREFIXES = (
    "$ ",
    "cat ",
    "cp ",
    "find ",
    "git ",
    "mkdir ",
    "python ",
    "python3 ",
    "rg ",
    "rsync ",
    "sed ",
    "test ",
)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
URL_RE = re.compile(r"\b(?:https?|mailto):[^\s<>)]+")
METADATA_KEY_RE = re.compile(r"^[a-z_][a-z0-9_]*:\s*")
PATH_RE = re.compile(
    r"(?<![\w/@:.-])"
    r"(?P<path>"
    r"tests 2/[A-Za-z0-9_./<>-]+/?"
    r"|(?:\.codex|assets|automations|docs|helpers|sandbox|scripts|sensors|ui|ui-gallery)"
    r"/[A-Za-z0-9_./<>-]+/?"
    r"|[A-Za-z0-9_.-]+\.md"
    r")"
)


@dataclass(frozen=True)
class Finding:
    kind: str
    path: str
    line: int
    message: str


def proposal_markdown_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for surface in PROPOSAL_SURFACES:
        candidate = root / surface
        if candidate.is_file() and candidate.suffix == ".md":
            files.add(candidate)
        elif candidate.is_dir():
            files.update(path for path in candidate.rglob("*.md") if path.is_file())
    return sorted(files)


def _mask_span(line: str, start: int, end: int) -> str:
    return line[:start] + (" " * (end - start)) + line[end:]


def _looks_like_standalone_path(value: str) -> bool:
    stripped = value.strip().rstrip(".,;:")
    if not stripped:
        return False
    if any(char.isspace() for char in stripped):
        return False
    return _is_candidate_path(stripped)


def _mask_inline_code(line: str) -> str:
    masked = line
    for match in reversed(list(INLINE_CODE_RE.finditer(line))):
        if _looks_like_standalone_path(match.group(1)):
            continue
        masked = _mask_span(masked, match.start(), match.end())
    return masked


def _mask_markdown_links(line: str) -> str:
    masked = line
    for match in reversed(list(MARKDOWN_LINK_RE.finditer(line))):
        masked = _mask_span(masked, match.start(), match.end())
    return masked


def _mask_urls(line: str) -> str:
    masked = line
    for match in reversed(list(URL_RE.finditer(line))):
        masked = _mask_span(masked, match.start(), match.end())
    return masked


def _is_command_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(COMMAND_PREFIXES)


def _is_candidate_path(value: str) -> bool:
    path = value.strip().strip("`").rstrip(".,;:)")
    if not path:
        return False
    if path in LOCAL_ONLY_EXACT:
        return False
    if path.startswith(LOCAL_ONLY_PREFIXES):
        return False
    if path.startswith(("http://", "https://", "mailto:", "urn:")):
        return False
    if path.startswith("/"):
        return False
    if path in ROOT_FILE_NAMES:
        return True
    if path.startswith(PATH_PREFIXES):
        return True
    return path.endswith(".md")


def _strip_candidate_token(value: str) -> str:
    return value.strip("`").rstrip(".,;:)")


def _metadata_line_numbers(lines: list[str]) -> set[int]:
    ignored: set[int] = set()
    started = False
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            if started:
                ignored.add(index)
                continue
            ignored.add(index)
            continue
        if stripped.startswith("#") or FENCE_RE.match(line):
            break
        if METADATA_KEY_RE.match(stripped) or stripped.startswith("- "):
            started = True
            ignored.add(index)
            continue
        break
    return ignored if started else set()


def _iter_prose_lines(path: Path) -> list[tuple[int, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    metadata_lines = _metadata_line_numbers(lines)
    result: list[tuple[int, str]] = []
    in_fence = False
    for index, line in enumerate(lines, start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or index in metadata_lines or _is_command_line(line):
            continue
        result.append((index, line))
    return result


def _local_link_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if not target:
        return None
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", 1)[0]
    if not target:
        return None
    if "://" in target or target.startswith(("mailto:", "urn:", "#", "/config/")):
        return None
    return unquote(target)


def _check_markdown_links(root: Path, path: Path, line_no: int, line: str) -> list[Finding]:
    findings: list[Finding] = []
    rel_doc = path.relative_to(root).as_posix()
    for match in MARKDOWN_LINK_RE.finditer(line):
        target = _local_link_target(match.group(1))
        if target is None:
            continue
        if target.startswith("/"):
            findings.append(
                Finding(
                    "broken-link",
                    rel_doc,
                    line_no,
                    f"Local Markdown link must be relative, not absolute: {target}",
                )
            )
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            findings.append(
                Finding(
                    "broken-link",
                    rel_doc,
                    line_no,
                    f"Local Markdown link escapes the repository: {target}",
                )
            )
            continue
        if not resolved.exists():
            findings.append(
                Finding(
                    "broken-link",
                    rel_doc,
                    line_no,
                    f"Local Markdown link does not resolve from this file: {target}",
                )
            )
    return findings


def _check_bare_paths(root: Path, path: Path, line_no: int, line: str) -> list[Finding]:
    masked = _mask_urls(_mask_markdown_links(_mask_inline_code(line)))
    findings: list[Finding] = []
    rel_doc = path.relative_to(root).as_posix()
    for match in PATH_RE.finditer(masked):
        candidate = _strip_candidate_token(match.group("path"))
        if not _is_candidate_path(candidate):
            continue
        if _resolve_candidate(root, path, candidate) is None:
            continue
        findings.append(
            Finding(
                "bare-path",
                rel_doc,
                line_no,
                f"Use a Markdown link for navigational repo path: {candidate}",
            )
        )
    return findings


def _resolve_candidate(root: Path, source_path: Path, candidate: str) -> Path | None:
    if candidate in ROOT_FILE_NAMES:
        targets = [root / candidate]
    elif candidate.startswith(PATH_PREFIXES):
        targets = [root / candidate]
    else:
        targets = [source_path.parent / candidate]
        proposal_root = root / ".codex" / "governance" / "proposals"
        if "/" not in candidate and candidate.endswith(".md"):
            try:
                source_path.relative_to(proposal_root)
            except ValueError:
                pass
            else:
                targets.append(proposal_root / candidate)

    for target in targets:
        try:
            resolved = target.resolve()
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        if resolved.is_file():
            return resolved
    return None


def check_files(root: Path, files: list[Path]) -> list[Finding]:
    resolved_root = root.resolve()
    findings: list[Finding] = []
    for file_path in files:
        if file_path.is_absolute():
            path = file_path.resolve()
        else:
            path = (resolved_root / file_path).resolve()
        for line_no, line in _iter_prose_lines(path):
            findings.extend(_check_markdown_links(resolved_root, path, line_no, line))
            findings.extend(_check_bare_paths(resolved_root, path, line_no, line))
    return findings


def _format_findings(findings: list[Finding]) -> str:
    return "\n".join(
        f"{finding.path}:{finding.line}: {finding.kind}: {finding.message}"
        for finding in findings
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate proposal Markdown links and bare navigational paths."
    )
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    files = proposal_markdown_files(root)
    findings = check_files(root, files)
    if findings:
        print(_format_findings(findings), file=sys.stderr)
        print(
            f"Proposal link validation failed: {len(findings)} finding(s) across {len(files)} file(s).",
            file=sys.stderr,
        )
        return 1
    print(
        f"Proposal link validation OK: scanned {len(files)} proposal Markdown file(s); "
        "no bare navigational repo paths or broken local links found."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
