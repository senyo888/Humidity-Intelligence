"""Focused security tests for the owned report export directory."""

from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_ROOT = ROOT / "custom_components" / "humidity_intelligence"


def _load_report_exports():
    path = INTEGRATION_ROOT / "helpers" / "report_exports.py"
    spec = importlib.util.spec_from_file_location("hi_report_exports_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReportExportTests(unittest.TestCase):
    def setUp(self):
        self.exports = _load_report_exports()

    def test_owned_report_filename_contract_matches_service_boundary(self):
        validate = self.exports.validate_owned_report_filename
        self.assertEqual(
            validate("humidity_intelligence_diagnostics.json"),
            "humidity_intelligence_diagnostics.json",
        )
        self.assertEqual(
            validate("humidity_intelligence_.json"),
            "humidity_intelligence_.json",
        )
        for candidate in (
            "configuration.yaml",
            "my_report.json",
            "Humidity_intelligence_report.json",
            "humidity_intelligence_report.JSON",
            " humidity_intelligence_report.json ",
            "humidity_intelligence_..report.json",
            "humidity_intelligence_../secrets.json",
            "humidity_intelligence_reports/report.json",
            "humidity_intelligence_reports\\report.json",
        ):
            with self.subTest(candidate=candidate):
                with self.assertRaises(self.exports.ReportExportError):
                    validate(candidate)

    def test_required_file_disappearance_preserves_the_original_cause(self):
        missing = FileNotFoundError("owned report disappeared")
        with mock.patch.object(self.exports.os, "stat", side_effect=missing):
            with self.assertRaises(self.exports.ReportExportError) as raised:
                self.exports._stat_regular_file(
                    1,
                    "humidity_intelligence_race.json",
                    allow_absent=False,
                )

        self.assertIs(raised.exception.__cause__, missing)

    def test_write_creates_owned_directory_and_leaves_root_report_untouched(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = "humidity_intelligence_diagnostics.json"
            legacy = root / filename
            legacy.write_text('{"legacy": true}\n', encoding="utf-8")

            relative = self.exports.write_owned_report(
                root,
                filename,
                {"status": "first"},
            )
            self.assertEqual(
                relative,
                "humidity_intelligence/exports/humidity_intelligence_diagnostics.json",
            )
            destination = root / relative
            self.assertEqual(
                json.loads(destination.read_text(encoding="utf-8")),
                {"status": "first"},
            )
            self.assertEqual(legacy.read_text(encoding="utf-8"), '{"legacy": true}\n')

            self.exports.write_owned_report(root, filename, {"status": "second"})
            self.assertEqual(
                json.loads(destination.read_text(encoding="utf-8")),
                {"status": "second"},
            )

    def test_directory_permissions_are_not_rewritten(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            exports_dir = root / "humidity_intelligence" / "exports"
            exports_dir.mkdir(parents=True)
            os.chmod(exports_dir, 0o750)
            before_mode = stat.S_IMODE(exports_dir.stat().st_mode)

            with mock.patch.object(
                self.exports.os,
                "chmod",
                side_effect=AssertionError("chmod must not be called"),
            ), mock.patch.object(
                self.exports.os,
                "chown",
                side_effect=AssertionError("chown must not be called"),
                create=True,
            ):
                self.exports.write_owned_report(
                    root,
                    "humidity_intelligence_permissions.json",
                    {"ok": True},
                )

            self.assertEqual(stat.S_IMODE(exports_dir.stat().st_mode), before_mode)

    def test_new_owned_directories_use_restrictive_permissions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            previous_umask = os.umask(0)
            try:
                self.exports.write_owned_report(
                    root,
                    "humidity_intelligence_permissions.json",
                    {"ok": True},
                )
                self.exports.write_owned_ui_export(
                    root,
                    "humidity_intelligence_cards_v2_mobile.yaml",
                    "type: markdown\ncontent: Ready\n",
                )
            finally:
                os.umask(previous_umask)

            for directory in (
                root / "humidity_intelligence",
                root / "humidity_intelligence" / "exports",
                root / "humidity_intelligence" / "ui",
            ):
                with self.subTest(directory=directory):
                    self.assertEqual(
                        stat.S_IMODE(directory.stat().st_mode),
                        0o700,
                    )

    def test_symlinked_components_and_final_symlink_fail_closed(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink support is required")

        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as outside:
            root = Path(tmpdir)
            outside_root = Path(outside)
            (root / "humidity_intelligence").symlink_to(
                outside_root,
                target_is_directory=True,
            )
            with self.assertRaises(self.exports.ReportExportError):
                self.exports.write_owned_report(
                    root,
                    "humidity_intelligence_symlink.json",
                    {"unsafe": True},
                )
            self.assertFalse((outside_root / "exports").exists())

        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as outside:
            root = Path(tmpdir)
            owned = root / "humidity_intelligence"
            owned.mkdir()
            outside_root = Path(outside)
            (owned / "exports").symlink_to(outside_root, target_is_directory=True)
            with self.assertRaises(self.exports.ReportExportError):
                self.exports.write_owned_report(
                    root,
                    "humidity_intelligence_symlink.json",
                    {"unsafe": True},
                )
            self.assertFalse((outside_root / "humidity_intelligence_symlink.json").exists())

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            exports_dir = root / "humidity_intelligence" / "exports"
            exports_dir.mkdir(parents=True)
            victim = root / "victim.json"
            victim.write_text('{"safe": true}\n', encoding="utf-8")
            destination = exports_dir / "humidity_intelligence_symlink.json"
            destination.symlink_to(victim)

            with self.assertRaises(self.exports.ReportExportError):
                self.exports.write_owned_report(
                    root,
                    destination.name,
                    {"unsafe": True},
                )
            self.assertTrue(destination.is_symlink())
            self.assertEqual(victim.read_text(encoding="utf-8"), '{"safe": true}\n')

    def test_regular_file_occupying_directory_component_fails_closed(self):
        for occupied_component in (
            "humidity_intelligence",
            "humidity_intelligence/exports",
        ):
            with self.subTest(component=occupied_component):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    occupied = root / occupied_component
                    occupied.parent.mkdir(parents=True, exist_ok=True)
                    occupied.write_text("not a directory\n", encoding="utf-8")
                    filename = "humidity_intelligence_component.json"

                    with self.assertRaises(self.exports.ReportExportError):
                        self.exports.write_owned_report(
                            root,
                            filename,
                            {"unsafe": True},
                        )

                    self.assertEqual(
                        occupied.read_text(encoding="utf-8"),
                        "not a directory\n",
                    )
                    self.assertFalse((root / filename).exists())

    def test_temporary_name_substitution_cannot_become_final_report(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink support is required")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            exports_dir = root / "humidity_intelligence" / "exports"
            victim = root / "victim.json"
            victim.write_text('{"safe": true}\n', encoding="utf-8")
            filename = "humidity_intelligence_temp_race.json"
            original_dump = self.exports.json.dump

            def replace_temporary_name(payload, stream, **kwargs):
                original_dump(payload, stream, **kwargs)
                temporary = next(exports_dir.glob(".hi_report_*.tmp"))
                temporary.unlink()
                temporary.symlink_to(victim)

            with mock.patch.object(
                self.exports.json,
                "dump",
                side_effect=replace_temporary_name,
            ):
                with self.assertRaises(self.exports.ReportExportError):
                    self.exports.write_owned_report(
                        root,
                        filename,
                        {"unsafe": True},
                    )

            self.assertFalse((exports_dir / filename).exists())
            self.assertEqual(victim.read_text(encoding="utf-8"), '{"safe": true}\n')
            substituted = list(exports_dir.glob(".hi_report_*.tmp"))
            self.assertEqual(len(substituted), 1)
            self.assertTrue(substituted[0].is_symlink())

    def test_final_symlink_inserted_during_replace_is_replaced_not_followed(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink support is required")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            exports_dir = root / "humidity_intelligence" / "exports"
            victim = root / "victim.json"
            victim.write_text('{"safe": true}\n', encoding="utf-8")
            filename = "humidity_intelligence_final_race.json"
            original_replace = self.exports.os.replace

            def insert_symlink_then_replace(src, dst, **kwargs):
                (exports_dir / dst).symlink_to(victim)
                return original_replace(src, dst, **kwargs)

            with mock.patch.object(
                self.exports.os,
                "replace",
                side_effect=insert_symlink_then_replace,
            ):
                self.exports.write_owned_report(
                    root,
                    filename,
                    {"safe": "owned"},
                )

            final = exports_dir / filename
            self.assertTrue(final.is_file())
            self.assertFalse(final.is_symlink())
            self.assertEqual(
                json.loads(final.read_text(encoding="utf-8")),
                {"safe": "owned"},
            )
            self.assertEqual(victim.read_text(encoding="utf-8"), '{"safe": true}\n')

    def test_export_directory_substitution_cannot_produce_false_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            owned_dir = root / "humidity_intelligence"
            exports_dir = owned_dir / "exports"
            moved_dir = owned_dir / "exports_moved"
            filename = "humidity_intelligence_directory_race.json"
            original_dump = self.exports.json.dump

            def replace_directory(payload, stream, **kwargs):
                original_dump(payload, stream, **kwargs)
                exports_dir.rename(moved_dir)
                exports_dir.mkdir()

            with mock.patch.object(
                self.exports.json,
                "dump",
                side_effect=replace_directory,
            ):
                with self.assertRaises(self.exports.ReportExportError):
                    self.exports.write_owned_report(
                        root,
                        filename,
                        {"status": "moved"},
                    )

            self.assertFalse((exports_dir / filename).exists())
            self.assertEqual(
                json.loads((moved_dir / filename).read_text(encoding="utf-8")),
                {"status": "moved"},
            )

    def test_non_regular_destination_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            destination = (
                root
                / "humidity_intelligence"
                / "exports"
                / "humidity_intelligence_directory.json"
            )
            destination.mkdir(parents=True)

            with self.assertRaises(self.exports.ReportExportError):
                self.exports.write_owned_report(
                    root,
                    destination.name,
                    {"unsafe": True},
                )

    def test_unsupported_atomic_replace_fails_without_root_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = "humidity_intelligence_unsupported.json"
            with mock.patch.object(
                self.exports.os,
                "replace",
                side_effect=NotImplementedError("dir_fd replace unavailable"),
            ):
                with self.assertRaises(self.exports.ReportExportError):
                    self.exports.write_owned_report(root, filename, {"ok": False})

            self.assertFalse((root / filename).exists())
            exports_dir = root / "humidity_intelligence" / "exports"
            self.assertTrue(exports_dir.is_dir())
            self.assertEqual(list(exports_dir.iterdir()), [])

    def test_directory_creation_failure_has_no_root_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = "humidity_intelligence_permission.json"
            with mock.patch.object(
                self.exports.os,
                "mkdir",
                side_effect=PermissionError("fixture denied"),
            ):
                with self.assertRaises(self.exports.ReportExportError):
                    self.exports.write_owned_report(root, filename, {"ok": False})

            self.assertFalse((root / filename).exists())
            self.assertFalse((root / "humidity_intelligence").exists())

    def test_failed_json_serialization_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = "humidity_intelligence_serialization.json"
            with self.assertRaises(TypeError):
                self.exports.write_owned_report(
                    root,
                    filename,
                    {"not_json": object()},
                )

            exports_dir = root / "humidity_intelligence" / "exports"
            self.assertTrue(exports_dir.is_dir())
            self.assertEqual(list(exports_dir.iterdir()), [])
            self.assertFalse((root / filename).exists())

    def test_cleanup_failure_does_not_mask_write_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir, mock.patch.object(
            self.exports.json,
            "dump",
            side_effect=ValueError("primary write failure"),
        ), mock.patch.object(
            self.exports,
            "_unlink_temporary_report",
            side_effect=self.exports.ReportExportError("cleanup failure"),
        ), mock.patch.object(
            self.exports._LOGGER,
            "warning",
        ) as warning:
            with self.assertRaisesRegex(ValueError, "primary write failure"):
                self.exports.write_owned_report(
                    Path(tmpdir),
                    "humidity_intelligence_cleanup.json",
                    {"ok": False},
                )

            warning.assert_called_once()

    def test_concurrent_same_name_writes_remain_complete_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = "humidity_intelligence_concurrent.json"
            payloads = [
                {"writer": writer, "content": str(writer) * 1000}
                for writer in range(12)
            ]
            replacement_order = []
            replacement_lock = threading.Lock()
            original_replace = self.exports.os.replace

            def track_replace(src, dst, **kwargs):
                descriptor = os.open(
                    src,
                    os.O_RDONLY,
                    dir_fd=kwargs["src_dir_fd"],
                )
                with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
                    writer = json.load(stream)["writer"]
                with replacement_lock:
                    result = original_replace(src, dst, **kwargs)
                    replacement_order.append(writer)
                    return result

            with mock.patch.object(
                self.exports.os,
                "replace",
                side_effect=track_replace,
            ):
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                    results = list(
                        executor.map(
                            lambda payload: self.exports.write_owned_report(
                                root,
                                filename,
                                payload,
                            ),
                            payloads,
                        )
                    )

            self.assertEqual(
                set(results),
                {"humidity_intelligence/exports/" + filename},
            )
            final_payload = json.loads(
                (
                    root
                    / "humidity_intelligence"
                    / "exports"
                    / filename
                ).read_text(encoding="utf-8")
            )
            self.assertIn(final_payload, payloads)
            self.assertEqual(final_payload["writer"], replacement_order[-1])

    def test_absent_cleanup_plan_does_not_create_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(
                self.exports.plan_default_diagnostics_report_removal(root),
                [],
            )
            self.assertFalse((root / "humidity_intelligence").exists())

    def test_cleanup_owns_only_default_diagnostics_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            default_name = self.exports.DEFAULT_DIAGNOSTICS_REPORT_FILENAME
            release_name = "humidity_intelligence_v205_release_check.json"
            custom_name = "humidity_intelligence_custom.json"
            legacy = root / default_name
            legacy.write_text('{"legacy": true}\n', encoding="utf-8")
            for filename in (default_name, release_name, custom_name):
                self.exports.write_owned_report(root, filename, {"name": filename})

            plans = self.exports.plan_default_diagnostics_report_removal(root)
            self.assertEqual(
                [plan.relative_path for plan in plans],
                [self.exports.DEFAULT_DIAGNOSTICS_REPORT_RELATIVE_PATH],
            )
            self.assertTrue(
                self.exports.remove_default_diagnostics_report(root, plans[0])
            )
            self.assertEqual(
                self.exports.plan_default_diagnostics_report_removal(root),
                [],
            )
            exports_dir = root / "humidity_intelligence" / "exports"
            self.assertTrue((exports_dir / release_name).is_file())
            self.assertTrue((exports_dir / custom_name).is_file())
            self.assertEqual(legacy.read_text(encoding="utf-8"), '{"legacy": true}\n')

    def test_cleanup_rejects_symlinked_report_candidate(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink support is required")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            exports_dir = root / "humidity_intelligence" / "exports"
            exports_dir.mkdir(parents=True)
            victim = root / "victim.json"
            victim.write_text('{"safe": true}\n', encoding="utf-8")
            candidate = exports_dir / self.exports.DEFAULT_DIAGNOSTICS_REPORT_FILENAME
            candidate.symlink_to(victim)

            with self.assertRaises(self.exports.ReportExportError):
                self.exports.plan_default_diagnostics_report_removal(root)
            self.assertEqual(victim.read_text(encoding="utf-8"), '{"safe": true}\n')

    def test_cleanup_rejects_regular_file_replaced_after_preview(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = self.exports.DEFAULT_DIAGNOSTICS_REPORT_FILENAME
            self.exports.write_owned_report(root, filename, {"version": 1})
            plan = self.exports.plan_default_diagnostics_report_removal(root)[0]
            destination = root / plan.relative_path
            destination.unlink()
            destination.write_text('{"version": 2}\n', encoding="utf-8")

            with self.assertRaises(self.exports.ReportExportError):
                self.exports.remove_default_diagnostics_report(root, plan)
            self.assertEqual(
                json.loads(destination.read_text(encoding="utf-8")),
                {"version": 2},
            )

    def test_cleanup_plan_is_bound_to_export_directory_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = self.exports.DEFAULT_DIAGNOSTICS_REPORT_FILENAME
            self.exports.write_owned_report(root, filename, {"version": 1})
            plan = self.exports.plan_default_diagnostics_report_removal(root)[0]
            owned_dir = root / "humidity_intelligence"
            exports_dir = owned_dir / "exports"
            moved_dir = owned_dir / "exports_moved"
            exports_dir.rename(moved_dir)
            exports_dir.mkdir()
            os.link(moved_dir / filename, exports_dir / filename)

            with self.assertRaises(self.exports.ReportExportError):
                self.exports.remove_default_diagnostics_report(root, plan)

            self.assertTrue((moved_dir / filename).is_file())
            self.assertTrue((exports_dir / filename).is_file())

    def test_cleanup_detects_export_directory_replaced_during_delete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = self.exports.DEFAULT_DIAGNOSTICS_REPORT_FILENAME
            self.exports.write_owned_report(root, filename, {"version": 1})
            plan = self.exports.plan_default_diagnostics_report_removal(root)[0]
            owned_dir = root / "humidity_intelligence"
            exports_dir = owned_dir / "exports"
            moved_dir = owned_dir / "exports_moved"
            original_unlink = self.exports.os.unlink

            def replace_directory_after_unlink(path, *args, **kwargs):
                result = original_unlink(path, *args, **kwargs)
                if path == filename:
                    exports_dir.rename(moved_dir)
                    exports_dir.mkdir()
                    (exports_dir / filename).write_text(
                        '{"version": 2}\n',
                        encoding="utf-8",
                    )
                return result

            with mock.patch.object(
                self.exports.os,
                "unlink",
                side_effect=replace_directory_after_unlink,
            ):
                with self.assertRaises(self.exports.ReportExportError):
                    self.exports.remove_default_diagnostics_report(root, plan)

            self.assertFalse((moved_dir / filename).exists())
            self.assertEqual(
                json.loads((exports_dir / filename).read_text(encoding="utf-8")),
                {"version": 2},
            )

    def test_cleanup_and_writer_interleaving_preserves_new_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = self.exports.DEFAULT_DIAGNOSTICS_REPORT_FILENAME
            self.exports.write_owned_report(root, filename, {"version": 1})
            plan = self.exports.plan_default_diagnostics_report_removal(root)[0]
            delete_waiting = threading.Event()
            allow_delete = threading.Event()
            writer_started = threading.Event()
            writer_finished = threading.Event()
            original_unlink = self.exports.os.unlink

            def block_planned_delete(path, *args, **kwargs):
                if path == filename:
                    delete_waiting.set()
                    if not allow_delete.wait(timeout=5):
                        raise AssertionError("delete interleaving fixture timed out")
                return original_unlink(path, *args, **kwargs)

            def write_new_report():
                writer_started.set()
                try:
                    return self.exports.write_owned_report(
                        root,
                        filename,
                        {"version": 2},
                    )
                finally:
                    writer_finished.set()

            with mock.patch.object(
                self.exports.os,
                "unlink",
                side_effect=block_planned_delete,
            ):
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    removal = executor.submit(
                        self.exports.remove_default_diagnostics_report,
                        root,
                        plan,
                    )
                    self.assertTrue(delete_waiting.wait(timeout=5))
                    writer = executor.submit(write_new_report)
                    self.assertTrue(writer_started.wait(timeout=5))
                    try:
                        self.assertFalse(writer_finished.wait(timeout=0.05))
                    finally:
                        allow_delete.set()
                    self.assertTrue(removal.result(timeout=5))
                    writer.result(timeout=5)

            destination = root / self.exports.DEFAULT_DIAGNOSTICS_REPORT_RELATIVE_PATH
            self.assertEqual(
                json.loads(destination.read_text(encoding="utf-8")),
                {"version": 2},
            )

    def test_owned_ui_filename_contract(self):
        validate = self.exports.validate_owned_ui_filename
        self.assertEqual(
            validate("humidity_intelligence_cards_v2_mobile.yaml"),
            "humidity_intelligence_cards_v2_mobile.yaml",
        )
        filesystem_boundary = ("x" * 250) + ".yaml"
        self.assertEqual(validate(filesystem_boundary), filesystem_boundary)
        for candidate in (
            "humidity_intelligence_cards_v2_mobile.yml",
            "humidity_intelligence_cards_v2_mobile.json",
            " humidity_intelligence_cards_v2_mobile.yaml ",
            "humidity_intelligence_..cards.yaml",
            "../humidity_intelligence_cards.yaml",
            "nested/humidity_intelligence_cards.yaml",
            "nested\\humidity_intelligence_cards.yaml",
            ("x" * 251) + ".yaml",
        ):
            with self.subTest(candidate=candidate):
                with self.assertRaises(self.exports.ReportExportError):
                    validate(candidate)

    def test_ui_write_creates_owned_directory_and_retains_legacy_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = "humidity_intelligence_cards_v2_mobile.yaml"
            legacy = root / filename
            legacy.write_text("legacy: true\n", encoding="utf-8")

            relative = self.exports.write_owned_ui_export(
                root,
                filename,
                "type: markdown\ncontent: First\n",
            )

            self.assertEqual(
                relative,
                "humidity_intelligence/ui/" + filename,
            )
            self.assertEqual(
                (root / relative).read_text(encoding="utf-8"),
                "type: markdown\ncontent: First\n",
            )
            self.assertEqual(legacy.read_text(encoding="utf-8"), "legacy: true\n")

    def test_ui_directory_permissions_are_not_rewritten(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ui_dir = root / "humidity_intelligence" / "ui"
            ui_dir.mkdir(parents=True)
            os.chmod(ui_dir, 0o750)
            before_mode = stat.S_IMODE(ui_dir.stat().st_mode)

            with mock.patch.object(
                self.exports.os,
                "chmod",
                side_effect=AssertionError("chmod must not be called"),
            ), mock.patch.object(
                self.exports.os,
                "chown",
                side_effect=AssertionError("chown must not be called"),
                create=True,
            ):
                self.exports.write_owned_ui_export(
                    root,
                    "humidity_intelligence_cards_v2_mobile.yaml",
                    "type: markdown\ncontent: Ready\n",
                )

            self.assertEqual(stat.S_IMODE(ui_dir.stat().st_mode), before_mode)

    def test_ui_write_rejects_symlinks_non_regular_targets_and_directory_substitution(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink support is required")

        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as outside:
            root = Path(tmpdir)
            outside_root = Path(outside)
            owned = root / "humidity_intelligence"
            owned.mkdir()
            (owned / "ui").symlink_to(outside_root, target_is_directory=True)
            with self.assertRaises(self.exports.ReportExportError):
                self.exports.write_owned_ui_export(
                    root,
                    "humidity_intelligence_cards_v2_mobile.yaml",
                    "unsafe: true\n",
                )
            self.assertEqual(list(outside_root.iterdir()), [])

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ui_dir = root / "humidity_intelligence" / "ui"
            ui_dir.mkdir(parents=True)
            victim = root / "victim.yaml"
            victim.write_text("safe: true\n", encoding="utf-8")
            symlink = ui_dir / "humidity_intelligence_cards_v2_mobile.yaml"
            symlink.symlink_to(victim)
            with self.assertRaises(self.exports.ReportExportError):
                self.exports.write_owned_ui_export(
                    root,
                    symlink.name,
                    "unsafe: true\n",
                )
            self.assertEqual(victim.read_text(encoding="utf-8"), "safe: true\n")

            directory = ui_dir / "humidity_intelligence_cards_v2_tablet.yaml"
            directory.mkdir()
            with self.assertRaises(self.exports.ReportExportError):
                self.exports.write_owned_ui_export(
                    root,
                    directory.name,
                    "unsafe: true\n",
                )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            owned = root / "humidity_intelligence"
            ui_dir = owned / "ui"
            moved_dir = owned / "ui_moved"
            filename = "humidity_intelligence_cards_v2_mobile.yaml"

            def substitute_directory(stream):
                stream.write("type: markdown\ncontent: Moved\n")
                ui_dir.rename(moved_dir)
                ui_dir.mkdir()

            original_write = self.exports._write_owned_artifact_locked

            def raced_write(*args, **kwargs):
                kwargs["serialize"] = substitute_directory
                return original_write(*args, **kwargs)

            with mock.patch.object(
                self.exports,
                "_write_owned_artifact_locked",
                side_effect=raced_write,
            ):
                with self.assertRaises(self.exports.ReportExportError):
                    self.exports.write_owned_ui_export(
                        root,
                        filename,
                        "unused\n",
                    )
            self.assertFalse((ui_dir / filename).exists())
            self.assertEqual(
                (moved_dir / filename).read_text(encoding="utf-8"),
                "type: markdown\ncontent: Moved\n",
            )

    def test_ui_write_is_atomic_concurrent_and_uses_non_executable_file_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = "humidity_intelligence_cards_v2_tablet.yaml"
            payloads = [
                f"type: markdown\ncontent: Writer {writer} {'x' * 2000}\n"
                for writer in range(12)
            ]
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                results = list(
                    executor.map(
                        lambda payload: self.exports.write_owned_ui_export(
                            root,
                            filename,
                            payload,
                        ),
                        payloads,
                    )
                )

            self.assertEqual(
                set(results),
                {"humidity_intelligence/ui/" + filename},
            )
            destination = root / results[0]
            self.assertIn(destination.read_text(encoding="utf-8"), payloads)
            self.assertEqual(
                stat.S_IMODE(destination.stat().st_mode) & 0o111,
                0,
            )
            self.assertEqual(
                list(destination.parent.glob(".hi_ui_*.tmp")),
                [],
            )

    def test_ui_atomic_replace_failure_has_no_config_root_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = "humidity_intelligence_cards_v2_mobile.yaml"
            with mock.patch.object(
                self.exports.os,
                "replace",
                side_effect=NotImplementedError("dir_fd replace unavailable"),
            ):
                with self.assertRaises(self.exports.ReportExportError):
                    self.exports.write_owned_ui_export(
                        root,
                        filename,
                        "type: markdown\ncontent: Unsafe\n",
                    )

            self.assertFalse((root / filename).exists())
            ui_dir = root / "humidity_intelligence" / "ui"
            self.assertTrue(ui_dir.is_dir())
            self.assertEqual(list(ui_dir.iterdir()), [])

    def test_ui_cleanup_is_exact_identity_bound_and_retains_custom_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            default_name = "humidity_intelligence_cards_v2_mobile.yaml"
            custom_name = "humidity_intelligence_my_custom_v2_mobile.yaml"
            self.exports.write_owned_ui_export(root, default_name, "default: true\n")
            self.exports.write_owned_ui_export(root, custom_name, "custom: true\n")

            plans = self.exports.plan_owned_ui_export_removal(
                root,
                [default_name],
            )
            self.assertEqual(
                [plan.relative_path for plan in plans],
                ["humidity_intelligence/ui/" + default_name],
            )
            default_path = root / plans[0].relative_path
            default_path.unlink()
            default_path.write_text("replacement: true\n", encoding="utf-8")
            with self.assertRaises(self.exports.ReportExportError):
                self.exports.remove_owned_ui_export(root, plans[0])
            self.assertTrue(
                root.joinpath("humidity_intelligence", "ui", custom_name).is_file()
            )

    def test_self_check_cleanup_owns_only_fixed_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            filename = self.exports.DEFAULT_SELF_CHECK_REPORT_FILENAME
            legacy = root / filename
            legacy.write_text('{"legacy": true}\n', encoding="utf-8")
            self.exports.write_owned_report(root, filename, {"status": "current"})

            plans = self.exports.plan_default_self_check_report_removal(root)
            self.assertEqual(
                [plan.relative_path for plan in plans],
                [self.exports.DEFAULT_SELF_CHECK_REPORT_RELATIVE_PATH],
            )
            self.assertTrue(
                self.exports.remove_default_self_check_report(root, plans[0])
            )
            self.assertEqual(legacy.read_text(encoding="utf-8"), '{"legacy": true}\n')


if __name__ == "__main__":
    unittest.main()
