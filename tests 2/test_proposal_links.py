"""Regression checks for proposal Markdown file-path links."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_proposal_links.py"


def _load_proposal_links():
    spec = importlib.util.spec_from_file_location("check_proposal_links", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["check_proposal_links"] = module
    spec.loader.exec_module(module)
    return module


class ProposalLinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.links = _load_proposal_links()

    def test_detects_bare_navigational_repo_path_in_prose(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            doc = root / "PROPOSALS.md"
            target = root / ".codex" / "governance" / "proposals" / "drafts.md"
            target.parent.mkdir(parents=True)
            target.write_text("# Drafts\n", encoding="utf-8")
            doc.write_text(
                "Drafts live at .codex/governance/proposals/drafts.md.\n",
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "bare-path")
        self.assertIn(".codex/governance/proposals/drafts.md", findings[0].message)

    def test_detects_bare_same_directory_markdown_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            doc = root / "sandbox" / "v2.1" / "safe" / "README.md"
            target = doc.parent / "current_air_control_truth_fixtures.md"
            doc.parent.mkdir(parents=True)
            target.write_text("# Fixtures\n", encoding="utf-8")
            doc.write_text(
                "Fixture: current_air_control_truth_fixtures.md.\n",
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "bare-path")
        self.assertIn("current_air_control_truth_fixtures.md", findings[0].message)

    def test_detects_flat_governance_ledger_from_nested_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            ledger = root / ".codex" / "governance" / "proposals" / "drafts.md"
            doc = ledger.parent / "drafts" / "README.md"
            doc.parent.mkdir(parents=True)
            ledger.write_text("# Drafts\n", encoding="utf-8")
            doc.write_text(
                "Link every file from drafts.md.\n",
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "bare-path")
        self.assertIn("drafts.md", findings[0].message)

    def test_allows_markdown_link_and_ignores_code_command_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            doc = root / "PROPOSALS.md"
            target = root / ".codex" / "governance" / "proposals" / "drafts.md"
            target.parent.mkdir(parents=True)
            target.write_text("# Drafts\n", encoding="utf-8")
            doc.write_text(
                textwrap.dedent(
                    """\
                    proposal_id: HI-PROP-20260601-001
                    evidence_file: .codex/governance/proposals/drafts.md

                    Drafts live at [.codex/governance/proposals/drafts.md](.codex/governance/proposals/drafts.md).

                    Run `rg -n ".codex/governance/proposals/drafts.md" PROPOSALS.md`.

                    ```bash
                    python3 scripts/check_proposal_links.py
                    ```
                    """
                ),
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(findings, [])

    def test_detects_broken_relative_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            doc = root / ".codex" / "governance" / "proposals" / "AGENTS.md"
            doc.parent.mkdir(parents=True)
            doc.write_text(
                "Template: [missing.md](missing.md).\n",
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "broken-link")
        self.assertIn("missing.md", findings[0].message)

    def test_ignores_bare_directory_category_in_prose(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            doc = root / "PROPOSALS.md"
            directory = root / "docs" / "governance"
            directory.mkdir(parents=True)
            doc.write_text(
                "This gate does not apply to small reversible docs/governance changes.\n",
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
