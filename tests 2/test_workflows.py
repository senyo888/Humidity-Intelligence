"""Regression checks for GitHub workflow configuration."""

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class WorkflowConfigurationTests(unittest.TestCase):
    def test_validate_compile_step_accepts_root_content_without_warning(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        hacs = (ROOT / "hacs.json").read_text(encoding="utf-8")

        self.assertIn('"content_in_root": true', hacs)
        self.assertIn('hacs.get("content_in_root")', workflow)
        self.assertIn("python -m compileall -q .", workflow)
        self.assertNotIn("::warning::custom_components/ not found", workflow)
        self.assertIn(
            "custom_components/ not found and hacs.json does not set content_in_root: true.",
            workflow,
        )
    def test_first_interaction_v3_uses_supported_input_names(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "first-interaction.yml").read_text(
            encoding="utf-8"
        )

        if "actions/first-interaction@v3" not in workflow:
            self.skipTest("first-interaction workflow is not using v3")

        self.assertIn("repo_token:", workflow)
        self.assertIn("issue_message:", workflow)
        self.assertIn("pr_message:", workflow)
        self.assertNotIn("repo-token:", workflow)
        self.assertNotIn("issue-message:", workflow)
        self.assertNotIn("pr-message:", workflow)


if __name__ == "__main__":
    unittest.main()
