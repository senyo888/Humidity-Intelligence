"""Regression checks for the non-blocking HA Lab governance boundary."""

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class HALabAdvisoryGovernanceTests(unittest.TestCase):
    def test_public_authority_surfaces_make_ha_lab_non_blocking(self) -> None:
        required_phrases = {
            "AGENTS.md": "HA Lab evidence is optional and non-blocking",
            "ARCHITECTURE.md": "none of those states is a promotion or release veto",
            "README.md": "does not block promotion",
            "docs/release-governance.md": "HA Lab is therefore never a promotion or release blocker",
        }
        for relative_path, phrase in required_phrases.items():
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(phrase, text)

    def test_pr_template_does_not_make_ha_lab_a_checkbox_gate(self) -> None:
        template = (ROOT / ".github" / "pull_request_template.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Optional and non-blocking", template)
        self.assertNotIn("- [ ] HA Lab", template)

    def test_hard_release_gate_list_excludes_ha_lab(self) -> None:
        governance = (ROOT / "docs" / "release-governance.md").read_text(
            encoding="utf-8"
        )
        hard_gates = governance.split("## Hard Release Gates", 1)[1].split(
            "## Enforcement", 1
        )[0]
        self.assertIn("HA Lab is deliberately absent from the hard-gate list", hard_gates)
        self.assertNotIn("\n- HA Lab", hard_gates)


if __name__ == "__main__":
    unittest.main()
