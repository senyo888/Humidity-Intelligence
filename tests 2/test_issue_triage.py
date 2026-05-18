"""Regression checks for the GitHub issue triage report helper."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "issue_triage.py"


def _load_issue_triage():
    spec = importlib.util.spec_from_file_location("issue_triage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["issue_triage"] = module
    spec.loader.exec_module(module)
    return module


class IssueTriageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.triage = _load_issue_triage()
        self.generated_at = datetime(2026, 5, 17, 9, 0, tzinfo=timezone.utc)

    def test_co_emergency_issue_routes_to_aetherwing_as_release_blocker(self) -> None:
        issue = {
            "number": 42,
            "title": "CO emergency lane does not trigger after HACS install",
            "html_url": "https://github.com/senyo888/humidity-intelligence/issues/42",
            "user": {"login": "tester"},
            "created_at": "2026-05-17T08:00:00Z",
            "updated_at": "2026-05-17T08:30:00Z",
            "labels": [{"name": "bug"}],
            "body": "CO emergency never wins the lane order after installing from HACS.",
        }

        analyzed = self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.category, "runtime")
        self.assertEqual(analyzed.priority, "P0")
        self.assertEqual(analyzed.owner, "Aetherwing")
        self.assertEqual(analyzed.release_blocker, "yes")
        self.assertEqual(analyzed.proposal_required, "no")
        self.assertIn("release-blocker", analyzed.suggested_labels)
        self.assertIn("runtime", analyzed.suggested_labels)

    def test_future_ui_idea_routes_to_aethermite_with_proposal_review(self) -> None:
        issue = {
            "number": 7,
            "title": "Experimental dashboard polish for orchestration display",
            "html_url": "https://github.com/senyo888/humidity-intelligence/issues/7",
            "user": {"login": "designer"},
            "created_at": "2026-05-16T09:00:00Z",
            "updated_at": "2026-05-16T09:00:00Z",
            "labels": [{"name": "enhancement"}],
            "body": "Future idea for a more visual dashboard orchestration layer.",
        }

        analyzed = self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.category, "UI")
        self.assertEqual(analyzed.priority, "P3")
        self.assertEqual(analyzed.owner, "Aethermite")
        self.assertEqual(analyzed.proposal_required, "yes")
        self.assertIn("proposal-review", analyzed.suggested_labels)
        self.assertIn("ui", analyzed.suggested_labels)

    def test_malformed_issue_is_reported_instead_of_crashing(self) -> None:
        analyzed = self.triage.analyze_issue({}, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.number, "unknown")
        self.assertEqual(analyzed.title, "Untitled issue")
        self.assertEqual(analyzed.priority, "Watch")
        self.assertEqual(analyzed.owner, "Human maintainer/Jules")
        self.assertEqual(analyzed.release_blocker, "unknown")
        self.assertEqual(analyzed.confidence, "low")

    def test_report_contains_required_read_only_sections(self) -> None:
        issues = [
            {
                "number": 11,
                "title": "Docs mismatch in v2.0.5 release notes",
                "html_url": "https://github.com/senyo888/humidity-intelligence/issues/11",
                "user": {"login": "reader"},
                "created_at": "2026-05-15T08:00:00Z",
                "updated_at": "2026-05-17T08:00:00Z",
                "labels": [],
                "body": "README says stable release but manifest is beta.",
            }
        ]
        analyzed = [
            self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)
            for issue in issues
        ]

        report = self.triage.render_report(
            repo="senyo888/humidity-intelligence",
            analyzed_issues=analyzed,
            generated_at=self.generated_at,
            lookback_days=3,
            source_note="unit-test fixture",
            api_status="offline",
            rate_limit_note="not checked",
        )

        self.assertIn("Mode: report-only / dry-run", report)
        self.assertIn("No GitHub issues were closed, edited, labelled, assigned, or commented on.", report)
        self.assertIn("## Recommended next actions", report)
        self.assertIn("## Needs human decision", report)
        self.assertIn("## Potential labels to apply manually", report)
        self.assertIn("## Possible owner handoff", report)
        self.assertIn("## Issue template signal notes", report)
        self.assertIn("Suggested owner: Bella", report)


if __name__ == "__main__":
    unittest.main()
