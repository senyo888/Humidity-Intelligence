"""Regression checks for GitHub workflow configuration."""

from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIRST_INTERACTION_V3_SHA = "1c4688942c71f71d4f5502a26ea67c331730fa4d"
ACTIONS_CHECKOUT_V6_SHA = "df4cb1c069e1874edd31b4311f1884172cec0e10"
HACS_ACTION_MAIN_SHA = "1ebf01c408f29afcb6406bd431bc98fd8cbb15aa"
MUTABLE_ACTION_REF_RE = re.compile(
    r"^\s*uses:\s*[^@\s]+@(main|master|v?\d+(?:\.\d+){0,2})\s*(?:#.*)?$",
    re.MULTILINE,
)


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

    def test_hacs_validation_actions_are_pinned_to_reviewed_commits(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "hacs.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn(f"actions/checkout@{ACTIONS_CHECKOUT_V6_SHA} # v6", workflow)
        self.assertIn(f"hacs/action@{HACS_ACTION_MAIN_SHA} # main", workflow)
        self.assertNotIn("actions/checkout@v6", workflow)
        self.assertNotIn("hacs/action@main", workflow)

    def test_workflow_actions_do_not_use_mutable_refs(self) -> None:
        mutable_refs = []
        for workflow_path in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
            workflow = workflow_path.read_text(encoding="utf-8")
            for match in MUTABLE_ACTION_REF_RE.finditer(workflow):
                line_number = workflow[: match.start()].count("\n") + 1
                relative_path = workflow_path.relative_to(ROOT)
                mutable_refs.append(
                    f"{relative_path}:{line_number}: {match.group(0).strip()}"
                )

        self.assertEqual([], mutable_refs)


if __name__ == "__main__":
    unittest.main()
