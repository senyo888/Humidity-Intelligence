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
            doc = root / "docs" / "proposals" / "proposal.md"
            target = root / "docs" / "release-governance.md"
            target.parent.mkdir(parents=True)
            doc.parent.mkdir(parents=True)
            target.write_text("# Release\n", encoding="utf-8")
            doc.write_text(
                "Release rules live at docs/release-governance.md.\n",
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "bare-path")
        self.assertIn("docs/release-governance.md", findings[0].message)

    def test_detects_bare_same_directory_markdown_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            doc = root / "docs" / "proposals" / "safe" / "README.md"
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

    def test_detects_local_only_governance_link_from_public_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            doc = root / "docs" / "proposals" / "proposal.md"
            ledger = root / ".codex" / "governance" / "proposals" / "drafts.md"
            doc.parent.mkdir(parents=True)
            ledger.parent.mkdir(parents=True)
            ledger.write_text("# Drafts\n", encoding="utf-8")
            doc.write_text(
                "Draft: [.codex/governance/proposals/drafts.md](../../.codex/governance/proposals/drafts.md).\n",
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "local-only-link")
        self.assertIn(".codex/governance/proposals/drafts.md", findings[0].message)

    def test_allows_markdown_link_and_ignores_code_command_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            doc = root / "docs" / "proposals" / "proposal.md"
            target = root / "ARCHITECTURE.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            doc.parent.mkdir(parents=True)
            target.write_text("# Architecture\n", encoding="utf-8")
            doc.write_text(
                textwrap.dedent(
                    """\
                    proposal_id: HI-PROP-20260601-001
                    evidence_file: ARCHITECTURE.md

                    Architecture lives at [ARCHITECTURE.md](../../ARCHITECTURE.md).

                    Run `rg -n "ARCHITECTURE.md" docs/proposals`.

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
            doc = root / "docs" / "proposals" / "proposal.md"
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
            doc = root / "docs" / "proposals" / "proposal.md"
            directory = root / "docs" / "governance"
            directory.mkdir(parents=True)
            doc.parent.mkdir(parents=True)
            doc.write_text(
                "This gate does not apply to small reversible docs/governance changes.\n",
                encoding="utf-8",
            )

            findings = self.links.check_files(root, [doc])

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
