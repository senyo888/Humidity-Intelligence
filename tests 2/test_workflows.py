"""Regression checks for GitHub workflow configuration."""

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIRST_INTERACTION_V3_SHA = "1c4688942c71f71d4f5502a26ea67c331730fa4d"


class WorkflowConfigurationTests(unittest.TestCase):
    def test_first_interaction_v3_is_pinned_and_uses_supported_input_names(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "first-interaction.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn(f"actions/first-interaction@{FIRST_INTERACTION_V3_SHA} # v3", workflow)
        self.assertNotIn("actions/first-interaction@v3", workflow)
        self.assertIn("repo_token:", workflow)
        self.assertIn("issue_message:", workflow)
        self.assertIn("pr_message:", workflow)
        self.assertNotIn("repo-token:", workflow)
        self.assertNotIn("issue-message:", workflow)
        self.assertNotIn("pr-message:", workflow)


if __name__ == "__main__":
    unittest.main()
