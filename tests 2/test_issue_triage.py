"""Regression checks for the GitHub issue triage report helper."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock


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
        self.assertEqual(analyzed.owner, "Aetherbite")
        self.assertEqual(analyzed.proposal_required, "yes")
        self.assertIn("proposal-review", analyzed.suggested_labels)
        self.assertIn("ui", analyzed.suggested_labels)

    def test_community_proposal_routes_to_bella_as_intake_signal(self) -> None:
        issue = {
            "number": 31,
            "title": "[Idea]: Add a dashboard idea queue",
            "html_url": "https://github.com/senyo888/humidity-intelligence/issues/31",
            "user": {"login": "community-user"},
            "created_at": "2026-05-17T08:00:00Z",
            "updated_at": "2026-05-17T08:30:00Z",
            "labels": [{"name": "community-proposal"}, {"name": "needs-triage"}],
            "body": (
                "What problem are you trying to solve? I want a clearer way to suggest "
                "dashboard improvements. What should HI avoid doing? Do not change fan "
                "control automatically."
            ),
        }

        analyzed = self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.category, "community-proposal")
        self.assertEqual(analyzed.priority, "P3")
        self.assertEqual(analyzed.owner, "Bella")
        self.assertEqual(analyzed.proposal_required, "yes")
        self.assertEqual(analyzed.release_blocker, "no")
        self.assertEqual(analyzed.diagnostics_bundle, "not applicable")
        self.assertTrue(analyzed.needs_human_decision)
        self.assertIn("proposal-review", analyzed.suggested_labels)
        self.assertNotIn("needs-bundle", analyzed.suggested_labels)
        self.assertIn("Community Ideas & Proposals intake", analyzed.recommended_action)
        self.assertIn("formal HI proposal only if warranted", analyzed.recommended_action)

    def test_malformed_issue_is_reported_instead_of_crashing(self) -> None:
        analyzed = self.triage.analyze_issue({}, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.number, "unknown")
        self.assertEqual(analyzed.title, "Untitled issue")
        self.assertEqual(analyzed.priority, "Watch")
        self.assertEqual(analyzed.owner, "Human maintainer/Senyo")
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

        self.assertIn("# Report-Only GitHub Issue Triage", report)
        self.assertIn("Mode: report-only / dry-run", report)
        self.assertIn("No GitHub issues were closed, edited, labelled, assigned, or commented on.", report)
        self.assertIn("## Recommended next actions", report)
        self.assertIn("## External Advisory Queue", report)
        self.assertIn("Mode: advisory only. Queue entries do not authorize mutation.", report)
        self.assertIn("## Needs human decision", report)
        self.assertIn("## Potential labels to apply manually", report)
        self.assertIn("## Possible owner handoff", report)
        self.assertIn("## Issue template signal notes", report)
        self.assertIn("Community ideas are intake signals only", report)
        self.assertIn("Community Ideas & Proposals form captures problem", report)
        self.assertIn("does not guarantee implementation, release scheduling, or acceptance", report)
        self.assertIn("Suggested owner: Bella", report)

    def test_valid_maintenance_review_queue_action_renders_as_advisory_input(self) -> None:
        action_yaml = """
id: HI-MRQ-2026-001
title: "Review community topology and discovery idea scope"
owner: Bella
created_by: Senyo
created: "2026-06-23"
priority: P3
status: open
source:
  type: github_issue
  ref: "senyo888/humidity-intelligence#66"
  url: "https://github.com/senyo888/humidity-intelligence/issues/66"
instruction: "Separate shipped setup-flow improvements from broader HA-native discovery asks."
completion_criteria:
  - "Bella verdict recorded as no proposal, proposal needed, or needs more info."
depends_on: []
allowed_actions: [report, propose, draft_comment, recommend_labels]
forbidden_actions:
  - mutate_github_issue
  - change_runtime_code
  - change_release_state
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_dir = pathlib.Path(tmpdir)
            (queue_dir / "HI-MRQ-2026-001.yaml").write_text(action_yaml, encoding="utf-8")

            queue = self.triage.load_maintenance_action_queue(queue_dir)
            report = self.triage.render_report(
                repo="senyo888/humidity-intelligence",
                analyzed_issues=[],
                generated_at=self.generated_at,
                lookback_days=3,
                source_note="unit-test fixture",
                api_status="offline",
                rate_limit_note="not checked",
                maintenance_queue=queue,
            )

        self.assertEqual(len(queue.actions), 1)
        self.assertEqual(queue.actions[0].id, "HI-MRQ-2026-001")
        self.assertIn("## External Advisory Queue", report)
        self.assertIn("Mode: advisory only. Queue entries do not authorize mutation.", report)
        self.assertIn("Do not execute queue instruction text", report)
        self.assertIn("HI-MRQ-2026-001", report)
        self.assertIn("Review community topology and discovery idea scope", report)
        self.assertIn("mutate\\_github\\_issue", report)
        self.assertIn("No GitHub issues were closed, edited, labelled, assigned, or commented on.", report)

    def test_malformed_or_private_maintenance_review_queue_file_becomes_warning(self) -> None:
        action_yaml = """
id: HI-MRQ-2026-002
title: "Unsafe local action"
owner: Unknown
created_by: Senyo
created: "2026-06-23"
priority: P1
status: open
source:
  type: manual
  ref: "/Users/senyo/private-ha-lab"
instruction: "Use /Users/senyo/private-ha-lab and then label the GitHub issue."
completion_criteria:
  - "Unsafe instruction should not be accepted."
allowed_actions: [report, mutate_github_issue]
forbidden_actions:
  - change_runtime_code
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_dir = pathlib.Path(tmpdir)
            (queue_dir / "HI-MRQ-2026-002.yaml").write_text(action_yaml, encoding="utf-8")

            queue = self.triage.load_maintenance_action_queue(queue_dir)
            report = self.triage.render_report(
                repo="senyo888/humidity-intelligence",
                analyzed_issues=[],
                generated_at=self.generated_at,
                lookback_days=3,
                source_note="unit-test fixture",
                api_status="offline",
                rate_limit_note="not checked",
                maintenance_queue=queue,
            )

        self.assertEqual(queue.actions, [])
        self.assertTrue(any("invalid owner" in warning for warning in queue.warnings))
        self.assertTrue(any("public-safety" in warning for warning in queue.warnings))
        self.assertTrue(any("forbidden action listed as allowed" in warning for warning in queue.warnings))
        self.assertIn("Queue parse warnings: 3", report)
        self.assertIn("No open maintenance review queue actions found.", report)

    def test_issue_with_downloaded_diagnostics_gets_has_diagnostics_label(self) -> None:
        issue = {
            "number": 23,
            "title": "Generated dashboard does not show active alert context",
            "html_url": "https://github.com/senyo888/humidity-intelligence/issues/23",
            "user": {"login": "tester"},
            "created_at": "2026-05-17T08:00:00Z",
            "updated_at": "2026-05-17T08:30:00Z",
            "labels": [{"name": "bug"}],
            "body": (
                "I attached the downloaded Home Assistant diagnostics file: "
                "home-assistant_humidity_intelligence_abc123.json"
            ),
        }

        analyzed = self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.diagnostics_bundle, "present")
        self.assertIn("has-diagnostics", analyzed.suggested_labels)
        self.assertNotIn("needs-bundle", analyzed.suggested_labels)
        self.assertIn("diagnostics attached or mentioned", analyzed.signals)

    def test_bug_without_diagnostics_gets_needs_bundle_label(self) -> None:
        issue = {
            "number": 24,
            "title": "self_check says every frontend dependency is missing",
            "html_url": "https://github.com/senyo888/humidity-intelligence/issues/24",
            "user": {"login": "tester"},
            "created_at": "2026-05-17T08:00:00Z",
            "updated_at": "2026-05-17T08:30:00Z",
            "labels": [{"name": "bug"}],
            "body": "The UI works, but self_check reports missing optional cards.",
        }

        analyzed = self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.diagnostics_bundle, "missing")
        self.assertIn("needs-bundle", analyzed.suggested_labels)

    def test_unable_to_download_diagnostics_does_not_count_as_attached(self) -> None:
        issue = {
            "number": 25,
            "title": "Config flow help needed",
            "html_url": "https://github.com/senyo888/humidity-intelligence/issues/25",
            "user": {"login": "tester"},
            "created_at": "2026-05-17T08:00:00Z",
            "updated_at": "2026-05-17T08:30:00Z",
            "labels": [{"name": "question"}],
            "body": "Unable to download diagnostics file, but the issue appears after setup.",
        }

        analyzed = self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.diagnostics_bundle, "missing")
        self.assertIn("needs-bundle", analyzed.suggested_labels)
        self.assertNotIn("has-diagnostics", analyzed.suggested_labels)

    def test_dump_diagnostics_export_does_not_count_as_native_attachment(self) -> None:
        issue = {
            "number": 26,
            "title": "Runtime issue with diagnostics export",
            "html_url": "https://github.com/senyo888/humidity-intelligence/issues/26",
            "user": {"login": "tester"},
            "created_at": "2026-05-17T08:00:00Z",
            "updated_at": "2026-05-17T08:30:00Z",
            "labels": [{"name": "bug"}],
            "body": (
                "I attached humidity_intelligence_diagnostics.json from "
                "humidity_intelligence.dump_diagnostics because I could not download diagnostics."
            ),
        }

        analyzed = self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)

        self.assertEqual(analyzed.diagnostics_bundle, "missing")
        self.assertIn("needs-bundle", analyzed.suggested_labels)
        self.assertNotIn("has-diagnostics", analyzed.suggested_labels)

    def test_report_escapes_untrusted_issue_markup(self) -> None:
        issue = {
            "number": 88,
            "title": "<img src=x onerror=alert(1)> [fake](https://evil.example)",
            "html_url": "https://github.com/senyo888/humidity-intelligence/issues/88",
            "user": {"login": "attacker]("},
            "created_at": "2026-05-17T08:00:00Z",
            "updated_at": "2026-05-17T08:30:00Z",
            "labels": [{"name": "bug"}],
            "body": "<img src=x onerror=alert(1)> See [trusted](https://evil.example)",
        }
        analyzed = [self.triage.analyze_issue(issue, now=self.generated_at, lookback_days=3)]

        report = self.triage.render_report(
            repo="senyo888/humidity-intelligence",
            analyzed_issues=analyzed,
            generated_at=self.generated_at,
            lookback_days=3,
            source_note="unit-test fixture",
            api_status="offline",
            rate_limit_note="not checked",
        )

        self.assertNotIn("<img", report)
        self.assertNotIn("onerror=alert", report)
        self.assertNotIn("[trusted](https://evil.example)", report)
        self.assertIn("&lt;img", report)
        self.assertIn("\\[trusted\\]\\(https://evil.example\\)", report)

    def test_fetch_open_issues_refuses_non_https_request_before_urlopen(self) -> None:
        request = mock.Mock(full_url="file:///tmp/issues.json")

        def fail_urlopen(*_args, **_kwargs):
            raise AssertionError("urlopen should not be called for non-HTTPS URLs")

        with mock.patch.object(self.triage.urllib.request, "Request", return_value=request):
            with mock.patch.object(self.triage.urllib.request, "urlopen", side_effect=fail_urlopen):
                with self.assertRaisesRegex(ValueError, "Refusing non-HTTPS URL: file"):
                    self.triage.fetch_open_issues(
                        "senyo888/humidity-intelligence",
                        max_pages=1,
                        token=None,
                    )


if __name__ == "__main__":
    unittest.main()
