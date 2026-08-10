"""Tests for the local HI memory usage auditor."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "local" / "hi_memory_usage_auditor.py"


def _load_auditor():
    spec = importlib.util.spec_from_file_location("hi_memory_usage_auditor", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["hi_memory_usage_auditor"] = module
    spec.loader.exec_module(module)
    return module


def _write(path: pathlib.Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


class HiMemoryUsageAuditorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.auditor = _load_auditor()

    def test_render_report_is_review_only_and_detects_candidate_from_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self._seed_minimal_repo(root)
            _write(
                root / ".codex" / "reports" / "handoffs" / "memory_candidate.md",
                "\n".join(
                    [
                        "Read memory surface: .codex/memories/project/canon.md",
                        "memory_update_candidate: target=.codex/memories/project/release_lessons.md "
                        "| text=Use report-only dry runs before scheduled issue-triage mutation. "
                        "| evidence=Repeated automation run notes confirmed report-only handling. "
                        "| reviewer=Bella",
                    ]
                ),
            )

            report = self.auditor.render_audit_report(
                root=root,
                generated_at=datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc),
            )

        self.assertIn("# HI Memory Usage Audit", report)
        self.assertIn("Mode: report-only / dry-run", report)
        self.assertIn("Root `PROPOSALS.md`: unchanged by this report", report)
        self.assertIn("`.codex/memories/`: read-only; no writes performed", report)
        self.assertIn("target_file: .codex/memories/project/release_lessons.md", report)
        self.assertIn("status: pending-review", report)
        self.assertIn("approved-manifest-only", report)

    def test_privacy_rejects_absolute_paths_tokens_and_private_entities(self) -> None:
        reasons = self.auditor.privacy_rejection_reasons(
            "Use /Users/example/private and HA_TOKEN=abc with sensor.example_private_humidity."
        )

        self.assertIn("machine-specific absolute path", reasons)
        self.assertIn("secret or token reference", reasons)
        self.assertIn("private entity id", reasons)

    def test_apply_approved_manifest_is_exact_and_memory_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            target = root / ".codex" / "memories" / "project" / "release_lessons.md"
            _write(target, "# Release Lessons\n")

            candidate = "- Keep memory updates exact, approved, and reviewable.\n"
            manifest = {
                "approved_by": "Senyo",
                "entries": [
                    {
                        "target_file": ".codex/memories/project/release_lessons.md",
                        "candidate_text": candidate,
                        "status": "accepted-by-maintainer",
                        "text_sha256": hashlib.sha256(candidate.encode("utf-8")).hexdigest(),
                    }
                ],
            }
            manifest_path = root / "approved_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            dry_result = self.auditor.apply_approved_manifest(root, manifest_path, dry_run=True)
            self.assertEqual(dry_result[0]["action"], "would_apply")
            self.assertNotIn(candidate, target.read_text(encoding="utf-8"))

            apply_result = self.auditor.apply_approved_manifest(root, manifest_path, dry_run=False)
            self.assertEqual(apply_result[0]["action"], "applied")
            self.assertIn(candidate, target.read_text(encoding="utf-8"))

            manifest["entries"][0]["text_sha256"] = "bad"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                self.auditor.apply_approved_manifest(root, manifest_path, dry_run=False)

            manifest["entries"][0]["target_file"] = "README.md"
            manifest["entries"][0]["text_sha256"] = hashlib.sha256(
                candidate.encode("utf-8")
            ).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside .codex/memories"):
                self.auditor.apply_approved_manifest(root, manifest_path, dry_run=False)

    def test_render_report_parks_candidate_already_present_in_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self._seed_minimal_repo(root)
            candidate = (
                "For scheduled issue-triage work, preserve report-only dry runs and "
                "manual GitHub mutation boundaries unless a maintainer explicitly approves "
                "a wider operation packet."
            )
            _write(
                root / ".codex" / "memories" / "project" / "release_lessons.md",
                f"# Release\n- {candidate}\n",
            )
            _write(
                root / ".codex" / "reports" / "issue_triage" / "daily_issue_triage.md",
                "Command: scripts/issue_triage.py --dry-run\n"
                "No GitHub issues were closed, edited, labelled, assigned, or commented on.\n",
            )

            report = self.auditor.render_audit_report(
                root=root,
                generated_at=datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc),
            )

        self.assertIn("status: parked", report)
        self.assertIn("already exists in target memory", report)

    def _seed_minimal_repo(self, root: pathlib.Path) -> None:
        for name in ["DESIGN_BRIEF.md", "AGENTS.md", "AGENTS.local.md", "PROPOSALS.md"]:
            _write(root / name, f"# {name}\n")
        _write(root / ".codex" / "memories" / "project" / "canon.md", "# Project Canon\n")
        _write(root / ".codex" / "memories" / "project" / "architecture.md", "# Architecture\n")
        _write(root / ".codex" / "memories" / "project" / "release_lessons.md", "# Release\n")
        _write(root / ".codex" / "memories" / "shared" / "terminology.md", "# Terms\n")
        for pet in ["Bella", "Aetherwing", "Aetherbite", "AetherCore"]:
            _write(root / ".codex" / "memories" / "pets" / pet / "memory.md", f"# {pet}\n")
        _write(root / ".codex" / "governance" / "proposals" / "drafts.md", "# Drafts\n")


if __name__ == "__main__":
    unittest.main()
