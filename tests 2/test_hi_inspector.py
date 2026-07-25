"""Static contract tests for the tracked HI Inspector sandbox."""

from __future__ import annotations

import importlib.util
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site" / "inspector"
BUILD_SCRIPT = ROOT / "scripts" / "build_hi_inspector.py"
FIXTURES = ROOT / "tests 2" / "fixtures" / "hi_inspector"
EXPECTED_SOURCE_FILES = {
    "app.mjs",
    "handoff.mjs",
    "index.html",
    "inspection-session.mjs",
    "parser.mjs",
    "styles.css",
}
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
PRIVATE_SENTINELS = (
    "REDACTION_FIXTURE",
    "alice:pass",
    "user:pass",
    "person.alice",
    "sensor.kitchen",
    "sensor.hall",
    "sensor.bed",
    "fan.kitchen",
    "/Users/",
    "\\Users\\",
)


class _InspectorHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.labels: list[str] = []
        self.references: list[str] = []
        self.metas: dict[str, str] = {}
        self.http_equiv: dict[str, str] = {}
        self.live_regions = 0
        self.focus_targets = 0
        self.file_inputs = 0
        self.file_input_tabindexes: list[str | None] = []
        self.drop_zone_roles: list[str | None] = []
        self.drop_zone_tabindexes: list[str | None] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "label" and values.get("for"):
            self.labels.append(values["for"])
        if tag == "link" and values.get("href"):
            self.references.append(values["href"])
        if tag == "script" and values.get("src"):
            self.references.append(values["src"])
        if tag == "meta":
            if values.get("name"):
                self.metas[values["name"].lower()] = values.get("content") or ""
            if values.get("http-equiv"):
                self.http_equiv[
                    values["http-equiv"].lower()
                ] = values.get("content") or ""
        if values.get("aria-live"):
            self.live_regions += 1
        if values.get("tabindex") == "-1":
            self.focus_targets += 1
        if tag == "input" and values.get("type") == "file":
            self.file_inputs += 1
            self.file_input_tabindexes.append(values.get("tabindex"))
        if values.get("id") == "drop-zone":
            self.drop_zone_roles.append(values.get("role"))
            self.drop_zone_tabindexes.append(values.get("tabindex"))


class HiInspectorStaticTests(unittest.TestCase):
    def test_source_bundle_is_dependency_free_and_allowlisted(self) -> None:
        self.assertEqual(
            {path.name for path in SOURCE.iterdir() if path.is_file()},
            EXPECTED_SOURCE_FILES,
        )
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(SOURCE.iterdir())
            if path.is_file()
        ).lower()
        for capability in FORBIDDEN_CAPABILITIES:
            self.assertNotIn(capability, combined)
        self.assertNotIn("console.", combined)
        self.assertNotIn("innerhtml", combined)
        self.assertNotIn(".openai", combined)

    def test_html_has_local_only_security_and_accessibility_contract(self) -> None:
        source = (SOURCE / "index.html").read_text(encoding="utf-8")
        parser = _InspectorHtmlParser()
        parser.feed(source)

        self.assertEqual(parser.references, ["styles.css", "app.mjs"])
        self.assertEqual(parser.file_inputs, 1)
        self.assertEqual(parser.file_input_tabindexes, ["-1"])
        self.assertEqual(parser.drop_zone_roles, ["button"])
        self.assertEqual(parser.drop_zone_tabindexes, ["0"])
        self.assertIn("diagnostics-file", parser.labels)
        self.assertIn("diagnostics-file", parser.ids)
        self.assertIn("error-state", parser.ids)
        self.assertIn("results", parser.ids)
        self.assertGreaterEqual(parser.live_regions, 3)
        self.assertGreaterEqual(parser.focus_targets, 2)
        self.assertEqual(parser.metas["referrer"], "no-referrer")
        self.assertEqual(
            set(parser.metas["robots"].split(",")),
            {"noindex", "nofollow", "noarchive", "nosnippet"},
        )
        csp = parser.http_equiv["content-security-policy"]
        for directive in (
            "default-src 'none'",
            "connect-src 'none'",
            "worker-src 'none'",
            "form-action 'none'",
            "base-uri 'none'",
        ):
            self.assertIn(directive, csp)
        self.assertNotIn("frame-ancestors", csp)

    def test_copy_is_explicit_about_local_beta_and_authority_boundaries(self) -> None:
        source = (SOURCE / "index.html").read_text(encoding="utf-8")
        for phrase in (
            "HI Support Bundle Inspector",
            "Local beta sandbox",
            "Inspector version <strong>0.2.0-gate2</strong>",
            "Supported native diagnostics schema <strong>1</strong>",
            "No diagnostic-content upload or network request, API",
            "static host would",
            "receive normal page-request metadata",
            "Home Assistant and the HI backend remain authoritative",
            "does not diagnose HI",
            "does not",
            "prove",
            "Native Home Assistant diagnostics remain the preferred support",
            "not published support availability",
            "Pasting it into GitHub creates normal GitHub",
            "Nothing is copied unless you activate the button",
            "not a diagnostics attachment",
        ):
            self.assertIn(phrase, source)
        self.assertNotIn("Preflight", source)
        self.assertNotIn("support form", source.lower())

    def test_relative_assets_resolve_under_nested_static_base(self) -> None:
        base = pathlib.PurePosixPath("/humidity-intelligence/inspector/")
        for reference in (
            "styles.css",
            "app.mjs",
            "handoff.mjs",
            "inspection-session.mjs",
        ):
            resolved = base / reference
            self.assertEqual(
                resolved,
                pathlib.PurePosixPath(
                    f"/humidity-intelligence/inspector/{reference}"
                ),
            )
            self.assertTrue((SOURCE / reference).is_file())

    def test_app_invalidates_pending_file_reads(self) -> None:
        source = (SOURCE / "app.mjs").read_text(encoding="utf-8")
        self.assertIn(
            "const inspectionToken = inspectionSession.begin();",
            source,
        )
        self.assertIn(
            "const readResult = await readTextForInspection(",
            source,
        )
        self.assertGreaterEqual(
            source.count("inspectionSession.isCurrent(inspectionToken)"),
            6,
        )
        self.assertIn("inspectionSession.invalidate();", source)
        self.assertIn('handoffText.value = "";', source)
        self.assertIn("currentHandoffText = \"\";", source)

    def test_clipboard_is_limited_to_explicit_handoff_write(self) -> None:
        source = (SOURCE / "app.mjs").read_text(encoding="utf-8")
        self.assertEqual(source.count("navigator.clipboard"), 1)
        self.assertEqual(source.count("clipboard.writeText"), 2)
        self.assertEqual(
            source.count("() => clipboard.writeText(copyText)"),
            1,
        )
        self.assertNotIn("clipboard.read", source)
        self.assertNotIn("document.execCommand", source)
        self.assertIn("selectHandoffForManualCopy", source)
        self.assertIn("settleRevisionBoundEffect", source)
        self.assertIn('result.status === "success"', source)
        self.assertIn('result.status === "error"', source)
        self.assertIn("press Ctrl+C or Cmd+C", source)

    def test_build_rejects_clipboard_access_in_non_app_modules(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "hi_inspector_builder_test",
            BUILD_SCRIPT,
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)

        for filename in ("handoff.mjs", "parser.mjs"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tempdir:
                mutated = pathlib.Path(tempdir) / "inspector"
                shutil.copytree(SOURCE, mutated)
                target = mutated / filename
                target.write_text(
                    target.read_text(encoding="utf-8")
                    + "\nnavigator.clipboard.writeText('forbidden');\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    RuntimeError,
                    "clipboard use exceeds",
                ):
                    builder.validate_sources(mutated)

    def test_handoff_ui_is_readonly_and_explicit(self) -> None:
        source = (SOURCE / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="handoff-text"', source)
        self.assertIn("readonly", source)
        self.assertIn('id="copy-handoff"', source)
        self.assertIn("Copy allowlisted handoff", source)
        self.assertIn('id="copy-status" role="status"', source)

    def test_support_docs_do_not_overclaim_local_name_redaction(self) -> None:
        for path in (ROOT / "README.md", ROOT / "docs" / "support.md"):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                normalized = " ".join(source.split())
                self.assertIn(
                    "user-configured display and level labels may remain",
                    normalized,
                )
                self.assertIn(
                    "Review the complete file before uploading it to a public issue",
                    normalized,
                )

    def test_optional_handoff_failure_does_not_hide_valid_result(self) -> None:
        source = (SOURCE / "app.mjs").read_text(encoding="utf-8")
        self.assertIn("if (handoff.ok)", source)
        self.assertIn(
            "The optional support handoff is unavailable for this result. "
            "The Inspector result remains valid.",
            source,
        )
        self.assertNotIn("showError(handoff.error)", source)
        self.assertLess(
            source.index("if (handoff.ok)"),
            source.index("renderReport(parsed.report);"),
        )

    def test_mobile_result_grid_contains_wide_table(self) -> None:
        source = (SOURCE / "styles.css").read_text(encoding="utf-8")
        self.assertIn(
            ".results,\n.result-grid,\n.result-card,\n.table-wrap {\n"
            "  min-width: 0;\n"
            "  max-width: 100%;\n"
            "}",
            source,
        )
        self.assertIn("overflow-x: auto;", source)
        self.assertIn("overscroll-behavior-inline: contain;", source)

    def test_fixture_generator_matches_backend_contract(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "generate_hi_inspector_fixtures.py"),
                "--check",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("fixtures current: 3", completed.stdout)

    def test_fixtures_are_synthetic_and_public_safe(self) -> None:
        self.assertEqual(
            {path.name for path in FIXTURES.glob("*.json")},
            {
                "dump_summary.json",
                "native_schema1.json",
                "native_schema1_envelope.json",
            },
        )
        rendered = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(FIXTURES.glob("*.json"))
        )
        for sentinel in PRIVATE_SENTINELS:
            self.assertNotIn(sentinel.lower(), rendered.lower())
        self.assertNotIn("file://", rendered.lower())

    def test_static_build_copies_only_validated_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            destination = pathlib.Path(tempdir) / "inspector"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_hi_inspector.py"),
                    str(destination),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stdout + completed.stderr,
            )
            self.assertEqual(
                {path.name for path in destination.iterdir()},
                EXPECTED_SOURCE_FILES,
            )
            for filename in EXPECTED_SOURCE_FILES:
                self.assertEqual(
                    (destination / filename).read_bytes(),
                    (SOURCE / filename).read_bytes(),
                )

    def test_static_build_refuses_source_tree_destination(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_hi_inspector.py"),
                str(SOURCE),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("outside the source tree", completed.stderr)

    def test_parser_uses_bounded_iterative_walk(self) -> None:
        source = (SOURCE / "parser.mjs").read_text(encoding="utf-8")
        self.assertIn("const stack =", source)
        self.assertIn("while (stack.length > 0)", source)
        self.assertIn("maxDepth", source)
        self.assertIn("maxNodes", source)
        self.assertIn("maxKeys", source)
        self.assertNotIn("eval(", source)
        self.assertNotIn("new Function", source)


if __name__ == "__main__":
    unittest.main()
