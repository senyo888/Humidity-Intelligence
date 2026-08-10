"""Direct tests for local HI-only snapshot tooling."""

from __future__ import annotations

import asyncio
import errno
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile
import types
from datetime import datetime, timezone
from types import SimpleNamespace


ROOT = pathlib.Path(__file__).resolve().parents[1]
INTEGRATION_ROOT = ROOT / "custom_components" / "humidity_intelligence"
PKG = "hi_local_versions_testpkg"
FIXED_NOW = datetime(2026, 5, 22, 13, 4, 55, tzinfo=timezone.utc)


def _install_package_scaffold() -> None:
    pkg = types.ModuleType(PKG)
    pkg.__path__ = [str(ROOT)]
    sys.modules[PKG] = pkg

    helpers = types.ModuleType(f"{PKG}.helpers")
    helpers.__path__ = [str(INTEGRATION_ROOT / "helpers")]
    sys.modules[f"{PKG}.helpers"] = helpers


def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_local_versions_module():
    _install_package_scaffold()
    _load_module(f"{PKG}.const", INTEGRATION_ROOT / "const.py")
    return _load_module(f"{PKG}.helpers.local_versions", INTEGRATION_ROOT / "helpers" / "local_versions.py")


def _write(path: pathlib.Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _write_manifest(folder: pathlib.Path, *, domain: str = "humidity_intelligence", version: str | None = "2.0.5") -> None:
    payload = {"domain": domain, "name": "Humidity Intelligence"}
    if version is not None:
        payload["version"] = version
    _write(folder / "manifest.json", json.dumps(payload, sort_keys=True))


def _create_active_tree(config_root: pathlib.Path, *, version: str = "2.0.5") -> pathlib.Path:
    active = config_root / "custom_components" / "humidity_intelligence"
    _write_manifest(active, version=version)
    _write(active / "__init__.py", "# active package\n")
    _write(active / "services.py", "SERVICE = 'fixture'\n")
    _write(active / "__pycache__" / "ignored.pyc", "compiled")
    _write(active / ".DS_Store", "ignored")
    return active


def _config_path(root: pathlib.Path):
    def path(*parts: str) -> str:
        return str(root.joinpath(*parts))

    return path


def _create_snapshot(module, config_root: pathlib.Path, **kwargs):
    return module.create_local_backup_sync(
        _config_path(config_root),
        now=kwargs.pop("now", FIXED_NOW),
        nonce=kwargs.pop("nonce", "nonce"),
        home_assistant_version=kwargs.pop("home_assistant_version", "2026.5.2"),
        **kwargs,
    )


def _snapshot_root(config_root: pathlib.Path) -> pathlib.Path:
    return config_root / "humidity_intelligence_local_snapshots"


def _snapshot_dirs(config_root: pathlib.Path) -> list[pathlib.Path]:
    root = _snapshot_root(config_root) / "snapshots"
    if not root.exists():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir())


def _snapshot_meta(path: pathlib.Path) -> dict:
    return json.loads((path / "snapshot.json").read_text(encoding="utf-8"))


def _assert_error_category(err: Exception, category: str) -> None:
    assert getattr(err, "category", None) == category


def test_create_snapshot_writes_metadata_files_and_no_host_paths():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        _create_active_tree(config_root)

        result = _create_snapshot(module, config_root)

        assert result["success"] is True
        assert result["manifest_version"] == "2.0.5"
        assert result["snapshot_id"].startswith("2.0.5_2026-05-22T130455Z_")
        assert result["file_count"] == 3
        assert result["total_bytes"] > 0
        assert result["retained_count"] == 1
        assert result["deleted_snapshots"] == []

        snapshot_dir = _snapshot_dirs(config_root)[0]
        assert snapshot_dir.name == result["snapshot_id"]
        assert (snapshot_dir / "humidity_intelligence" / "manifest.json").exists()
        assert not (snapshot_dir / "humidity_intelligence" / "__pycache__").exists()
        assert not (snapshot_dir / "humidity_intelligence" / ".DS_Store").exists()
        assert not list((_snapshot_root(config_root) / "tmp").glob("*.partial"))

        metadata = _snapshot_meta(snapshot_dir)
        assert metadata["schema"] == 1
        assert metadata["domain"] == "humidity_intelligence"
        assert metadata["source"] == "/config/custom_components/humidity_intelligence"
        assert metadata["manifest_domain"] == "humidity_intelligence"
        assert metadata["manifest_version"] == "2.0.5"
        assert metadata["home_assistant_version"] == "2026.5.2"
        assert metadata["created_by"] == "humidity_intelligence.create_local_backup"
        assert metadata["running_code_unchanged_until_restart"] is True
        assert metadata["content_hash"].startswith("sha256:")

        files = json.loads((snapshot_dir / "files.json").read_text(encoding="utf-8"))
        rendered = json.dumps({"metadata": metadata, "files": files}, sort_keys=True)
        assert str(config_root) not in rendered
        assert "__pycache__" not in rendered
        assert ".DS_Store" not in rendered


def test_create_rejects_missing_active_folder():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            _create_snapshot(module, pathlib.Path(tmp))
        except module.LocalVersionError as err:
            _assert_error_category(err, "active_folder_missing")
        else:
            raise AssertionError("Missing active folder should fail")


def test_create_rejects_missing_corrupt_wrong_domain_and_versionless_manifest():
    module = _load_local_versions_module()
    cases = [
        ("manifest_missing", lambda active: None),
        ("manifest_corrupt", lambda active: _write(active / "manifest.json", "{not-json")),
        ("manifest_domain_mismatch", lambda active: _write_manifest(active, domain="other_domain")),
        ("manifest_version_missing", lambda active: _write_manifest(active, version=None)),
    ]

    for category, setup in cases:
        with tempfile.TemporaryDirectory() as tmp:
            config_root = pathlib.Path(tmp)
            active = config_root / "custom_components" / "humidity_intelligence"
            active.mkdir(parents=True)
            setup(active)
            try:
                _create_snapshot(module, config_root)
            except module.LocalVersionError as err:
                _assert_error_category(err, category)
            else:
                raise AssertionError(f"{category} should fail")


def test_create_reports_unwritable_root_and_enospc_without_leaving_partial(monkeypatch=None):
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        _create_active_tree(config_root)
        (_snapshot_root(config_root)).write_text("not a directory", encoding="utf-8")

        try:
            _create_snapshot(module, config_root)
        except module.LocalVersionError as err:
            _assert_error_category(err, "snapshot_root_unwritable")
        else:
            raise AssertionError("Snapshot root path conflict should fail")

    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        _create_active_tree(config_root)
        original_copy2 = module.shutil.copy2

        def raise_enospc(src, dst):
            raise OSError(errno.ENOSPC, "No space left on device")

        module.shutil.copy2 = raise_enospc
        try:
            try:
                _create_snapshot(module, config_root)
            except module.LocalVersionError as err:
                _assert_error_category(err, "filesystem_no_space")
            else:
                raise AssertionError("ENOSPC should fail")
        finally:
            module.shutil.copy2 = original_copy2

        tmp_root = _snapshot_root(config_root) / "tmp"
        assert not list(tmp_root.glob("*.partial"))


def test_read_only_filesystem_error_category_is_stable():
    module = _load_local_versions_module()

    err = module._local_version_os_error(
        OSError(errno.EROFS, "Read-only file system"),
        "snapshot_root_unwritable",
        "Local HI-only snapshot root is not writable.",
    )

    assert err.category == "filesystem_permission"


def test_stale_partial_cleanup_is_scoped_to_snapshot_tmp_root():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        _create_active_tree(config_root)
        tmp_root = _snapshot_root(config_root) / "tmp"
        stale = tmp_root / "old.partial"
        fresh = tmp_root / "fresh.partial"
        outside = config_root / "custom_components" / "humidity_intelligence.partial"
        stale.mkdir(parents=True)
        fresh.mkdir(parents=True)
        outside.mkdir(parents=True)
        old_time = FIXED_NOW.timestamp() - (module.STALE_PARTIAL_SECONDS + 60)
        fresh_time = FIXED_NOW.timestamp()
        for path, stamp in ((stale, old_time), (fresh, fresh_time), (outside, old_time)):
            pathlib.Path(path / "marker").write_text("x", encoding="utf-8")
            shutil.os.utime(path, (stamp, stamp))

        result = _create_snapshot(module, config_root)

        assert result["partial_snapshots_cleaned"] == ["old.partial"]
        assert not stale.exists()
        assert fresh.exists()
        assert outside.exists()


def test_duplicate_snapshot_id_is_rejected():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        _create_active_tree(config_root)
        first = _create_snapshot(module, config_root)

        try:
            _create_snapshot(module, config_root)
        except module.LocalVersionError as err:
            _assert_error_category(err, "duplicate_snapshot_id")
        else:
            raise AssertionError("Duplicate snapshot ID should fail")

        assert [path.name for path in _snapshot_dirs(config_root)] == [first["snapshot_id"]]


def test_bad_copied_hash_is_rejected_and_partial_is_removed():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        _create_active_tree(config_root)
        original_copy2 = module.shutil.copy2

        def corrupt_copy(src, dst):
            result = original_copy2(src, dst)
            if pathlib.Path(dst).name == "services.py":
                pathlib.Path(dst).write_text("corrupted after copy\n", encoding="utf-8")
            return result

        module.shutil.copy2 = corrupt_copy
        try:
            try:
                _create_snapshot(module, config_root)
            except module.LocalVersionError as err:
                _assert_error_category(err, "copied_hash_mismatch")
            else:
                raise AssertionError("Copied hash mismatch should fail")
        finally:
            module.shutil.copy2 = original_copy2

        assert not _snapshot_dirs(config_root)
        assert not list((_snapshot_root(config_root) / "tmp").glob("*.partial"))


def test_active_tree_change_during_copy_is_rejected():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        _create_active_tree(config_root)
        original_copy2 = module.shutil.copy2

        def change_source_then_copy(src, dst):
            if pathlib.Path(src).name == "services.py":
                pathlib.Path(src).write_text("changed during copy\n", encoding="utf-8")
            return original_copy2(src, dst)

        module.shutil.copy2 = change_source_then_copy
        try:
            try:
                _create_snapshot(module, config_root)
            except module.LocalVersionError as err:
                _assert_error_category(err, "copied_hash_mismatch")
            else:
                raise AssertionError("Active source change should fail copied hash verification")
        finally:
            module.shutil.copy2 = original_copy2

        assert not _snapshot_dirs(config_root)


def test_retention_deletes_oldest_unpinned_snapshots_and_preserves_latest():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        active = _create_active_tree(config_root)

        ids = []
        for idx, second in enumerate((1, 2, 3), start=1):
            _write(active / "payload.txt", "x" * idx)
            result = _create_snapshot(
                module,
                config_root,
                now=datetime(2026, 5, 22, 13, 4, second, tzinfo=timezone.utc),
                nonce=f"nonce{idx}",
                retain_count=2,
            )
            ids.append(result["snapshot_id"])

        assert [path.name for path in _snapshot_dirs(config_root)] == ids[-2:]

    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        active = _create_active_tree(config_root)

        for idx, second in enumerate((1, 2), start=1):
            _write(active / "payload.txt", "x" * (1024 * idx))
            result = _create_snapshot(
                module,
                config_root,
                now=datetime(2026, 5, 22, 13, 5, second, tzinfo=timezone.utc),
                nonce=f"byte{idx}",
                retain_count=5,
                max_total_bytes=1500,
            )

        assert [path.name for path in _snapshot_dirs(config_root)] == [result["snapshot_id"]]


def test_list_saved_versions_reports_valid_invalid_latest_and_size():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        active = _create_active_tree(config_root)
        first = _create_snapshot(
            module,
            config_root,
            now=datetime(2026, 5, 22, 13, 1, 1, tzinfo=timezone.utc),
            nonce="one",
        )
        _write(active / "payload.txt", "new")
        second = _create_snapshot(
            module,
            config_root,
            now=datetime(2026, 5, 22, 13, 2, 1, tzinfo=timezone.utc),
            nonce="two",
        )
        invalid = _snapshot_root(config_root) / "snapshots" / "invalid_snapshot"
        invalid.mkdir(parents=True)

        result = module.list_saved_versions_sync(_config_path(config_root))

        assert result["success"] is True
        assert [item["snapshot_id"] for item in result["valid_snapshots"]] == [
            first["snapshot_id"],
            second["snapshot_id"],
        ]
        assert result["latest_snapshot"]["snapshot_id"] == second["snapshot_id"]
        assert result["retained_count"] == 2
        assert result["total_size"] > 0
        assert result["invalid_snapshots"][0]["snapshot_id"] == "invalid_snapshot"
        assert result["invalid_snapshots"][0]["error_category"] == "snapshot_metadata_missing"


class _FakeConfig:
    def __init__(self, root: pathlib.Path):
        self._root = root

    def path(self, *parts):
        return str(self._root.joinpath(*parts))


class _FakeHass:
    def __init__(self, root: pathlib.Path):
        self.config = _FakeConfig(root)
        self.data = {}
        self.executor_calls = 0

    async def async_add_executor_job(self, func, *args):
        self.executor_calls += 1
        await asyncio.sleep(0)
        return func(*args)


def test_async_helpers_use_executor_and_global_lock_for_rapid_calls():
    module = _load_local_versions_module()
    with tempfile.TemporaryDirectory() as tmp:
        config_root = pathlib.Path(tmp)
        _create_active_tree(config_root)
        hass = _FakeHass(config_root)

        async def run_two():
            results = await asyncio.gather(
                module.async_create_local_backup(hass, now=FIXED_NOW, nonce="same"),
                module.async_create_local_backup(hass, now=FIXED_NOW, nonce="same"),
                return_exceptions=True,
            )
            listed = await module.async_list_saved_versions(hass)
            return results, listed

        results, listed = asyncio.run(run_two())
        successes = [item for item in results if isinstance(item, dict) and item.get("success")]
        failures = [item for item in results if isinstance(item, module.LocalVersionError)]

        assert len(successes) == 1
        assert len(failures) == 1
        assert failures[0].category == "duplicate_snapshot_id"
        assert hass.executor_calls >= 3
        assert module.LOCAL_VERSION_LOCK_KEY in hass.data["humidity_intelligence"]
        assert listed["retained_count"] == 1


def test_helper_is_runtime_isolated_and_services_are_documented():
    module = _load_local_versions_module()
    helper_source = (INTEGRATION_ROOT / "helpers" / "local_versions.py").read_text(encoding="utf-8")
    services_source = (INTEGRATION_ROOT / "services.py").read_text(encoding="utf-8")
    services_yaml = (INTEGRATION_ROOT / "services.yaml").read_text(encoding="utf-8")

    assert "automations.engine" not in helper_source
    assert "async_request_evaluate" not in helper_source
    assert "ui.register" not in helper_source
    assert "create_local_backup_sync" in helper_source
    assert "list_saved_versions_sync" in helper_source

    assert 'SERVICE_CREATE_LOCAL_BACKUP = "create_local_backup"' in services_source
    assert 'SERVICE_LIST_SAVED_VERSIONS = "list_saved_versions"' in services_source
    assert "async_create_local_backup" in services_source
    assert "async_list_saved_versions" in services_source
    assert "SERVICE_CREATE_LOCAL_BACKUP" in services_source.split("async_unregister_services", 1)[1]
    assert "SERVICE_LIST_SAVED_VERSIONS" in services_source.split("async_unregister_services", 1)[1]

    assert "create_local_backup:" in services_yaml
    assert "list_saved_versions:" in services_yaml
    assert "local HI-only snapshot" in services_yaml
    assert "not a Home Assistant backup" in services_yaml
    assert "does not change running code" in services_yaml


if __name__ == "__main__":
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for name, test in tests:
        test()
    print(f"{len(tests)} local version sanity checks passed.")
