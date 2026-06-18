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


if __name__ == "__main__":
    unittest.main()
