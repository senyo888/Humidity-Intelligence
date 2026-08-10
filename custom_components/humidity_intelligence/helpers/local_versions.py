"""Local HI-only snapshot helpers.

This module intentionally does not implement restore, rollback, HACS interception,
startup snapshotting, entity creation, or runtime-engine behavior.
"""

from __future__ import annotations

import asyncio
import errno
import hashlib
import json
import os
import re
import secrets
import shutil
import tempfile
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Any, Callable

from ..const import DOMAIN

try:  # Home Assistant is optional for direct test harnesses.
    from homeassistant.const import __version__ as HA_VERSION
except Exception:  # pragma: no cover - exercised in local direct tests without HA.
    HA_VERSION = "unknown"


SNAPSHOT_ROOT_DIR = "humidity_intelligence_local_snapshots"
SNAPSHOTS_DIR = "snapshots"
TMP_DIR = "tmp"
SNAPSHOT_SCHEMA = 1
LOCAL_VERSION_LOCK_KEY = "_local_versions_lock"
LOCAL_VERSION_STATE_KEY = "local_version_preservation"

DEFAULT_RETAIN_COUNT = 2
MIN_RETAIN_COUNT = 1
MAX_RETAIN_COUNT = 5
DEFAULT_MAX_TOTAL_BYTES = 50 * 1024 * 1024
HARD_MAX_TOTAL_BYTES = 250 * 1024 * 1024
STALE_PARTIAL_SECONDS = 24 * 60 * 60

_SNAPSHOT_ID_SAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")
_EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
_EXCLUDED_FILES = {
    ".DS_Store",
}


class LocalVersionError(Exception):
    """Snapshot tooling failure with a stable category for services/diagnostics."""

    def __init__(self, category: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.category = category
        self.message = message
        self.details = details or {}

    def as_dict(self) -> dict[str, Any]:
        return {
            "success": False,
            "latest_error_category": self.category,
            "message": self.message,
            "details": self.details,
        }


async def async_create_local_backup(
    hass: Any,
    *,
    retain_count: int = DEFAULT_RETAIN_COUNT,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    now: datetime | None = None,
    nonce: str | None = None,
    home_assistant_version: str | None = None,
) -> dict[str, Any]:
    """Create one local HI-only snapshot through a single executor job."""

    lock = _local_version_lock(hass)
    async with lock:
        try:
            result = await hass.async_add_executor_job(
                partial(
                    create_local_backup_sync,
                    hass.config.path,
                    retain_count=retain_count,
                    max_total_bytes=max_total_bytes,
                    now=now,
                    nonce=nonce,
                    home_assistant_version=home_assistant_version or HA_VERSION,
                )
            )
        except LocalVersionError as err:
            _set_cached_local_version_status(hass, _error_status("create", err))
            raise

        _set_cached_local_version_status(hass, _compact_status_from_create(result))
        return result


async def async_list_saved_versions(hass: Any) -> dict[str, Any]:
    """List local HI-only snapshots through a single executor job."""

    lock = _local_version_lock(hass)
    async with lock:
        try:
            result = await hass.async_add_executor_job(
                partial(list_saved_versions_sync, hass.config.path)
            )
        except LocalVersionError as err:
            _set_cached_local_version_status(hass, _error_status("list", err))
            raise

        _set_cached_local_version_status(hass, _compact_status_from_list(result))
        return result


async def async_local_version_status(hass: Any) -> dict[str, Any]:
    """Return compact snapshot status for diagnostics/self-check surfaces."""

    try:
        return _compact_status_from_list(await async_list_saved_versions(hass))
    except LocalVersionError as err:
        return _error_status("status", err)


def cached_local_version_status(hass: Any) -> dict[str, Any]:
    """Return the last known compact status without doing filesystem I/O."""

    return (
        (getattr(hass, "data", {}) or {})
        .get(DOMAIN, {})
        .get(LOCAL_VERSION_STATE_KEY, _not_checked_status())
    )


def create_local_backup_sync(
    config_path: Callable[..., str],
    *,
    retain_count: int = DEFAULT_RETAIN_COUNT,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    now: datetime | None = None,
    nonce: str | None = None,
    home_assistant_version: str = "unknown",
    stale_partial_seconds: int = STALE_PARTIAL_SECONDS,
) -> dict[str, Any]:
    """Create one local HI-only snapshot.

    This function performs blocking filesystem work and must be called from an
    executor when invoked by Home Assistant service handlers.
    """

    created_at = _utc_now(now)
    config_root = _path_from_config(config_path)
    active_root = _active_integration_path(config_path)
    snapshot_root = _snapshot_root(config_path)
    snapshots_root = snapshot_root / SNAPSHOTS_DIR
    tmp_root = snapshot_root / TMP_DIR
    retain_count = _bounded_retain_count(retain_count)
    max_total_bytes = _bounded_max_total_bytes(max_total_bytes)

    manifest = _read_active_manifest(active_root)
    source_manifest = _build_file_manifest(active_root)
    source_hash = _tree_hash(source_manifest)
    snapshot_id = _snapshot_id(manifest["version"], created_at, source_hash)
    partial_id = _safe_id_part(nonce or secrets.token_hex(4))
    partial_dir = tmp_root / f"{snapshot_id}.{partial_id}.partial"
    final_dir = snapshots_root / snapshot_id

    _ensure_snapshot_path(snapshot_root, config_root)
    _ensure_snapshot_path(snapshots_root, snapshot_root)
    _ensure_snapshot_path(tmp_root, snapshot_root)
    _ensure_snapshot_path(partial_dir, snapshot_root)
    _ensure_snapshot_path(final_dir, snapshot_root)
    _ensure_snapshot_dirs(snapshot_root, snapshots_root, tmp_root)
    cleaned_partials = _cleanup_stale_partials(
        tmp_root,
        snapshot_root,
        now=created_at,
        stale_after_seconds=stale_partial_seconds,
    )
    if final_dir.exists():
        raise LocalVersionError(
            "duplicate_snapshot_id",
            f"Local HI-only snapshot already exists: {snapshot_id}",
            details={"snapshot_id": snapshot_id},
        )
    if partial_dir.exists():
        raise LocalVersionError(
            "partial_snapshot_exists",
            f"Partial snapshot path already exists: {partial_dir.name}",
            details={"partial": partial_dir.name},
        )

    try:
        copied_root = partial_dir / DOMAIN
        _copy_and_verify_source(active_root, copied_root, source_manifest)
        copied_manifest = _read_manifest(copied_root / "manifest.json")
        if copied_manifest.get("domain") != DOMAIN or copied_manifest.get("version") != manifest["version"]:
            raise LocalVersionError(
                "copied_manifest_mismatch",
                "Copied manifest no longer matches the active Humidity Intelligence manifest.",
            )
        copied_files = _build_file_manifest(copied_root)
        copied_hash = _tree_hash(copied_files)
        if copied_hash != source_hash:
            raise LocalVersionError(
                "copied_hash_mismatch",
                "Copied file hash does not match the active integration tree captured before copy.",
            )

        metadata = {
            "schema": SNAPSHOT_SCHEMA,
            "domain": DOMAIN,
            "created_at_utc": _format_created_at(created_at),
            "source": f"/config/custom_components/{DOMAIN}",
            "manifest_version": manifest["version"],
            "manifest_domain": manifest["domain"],
            "snapshot_id": snapshot_id,
            "file_count": len(copied_files),
            "total_bytes": sum(row["size"] for row in copied_files),
            "content_hash": f"sha256:{copied_hash}",
            "home_assistant_version": home_assistant_version or "unknown",
            "created_by": f"{DOMAIN}.create_local_backup",
            "running_code_unchanged_until_restart": True,
        }
        files_payload = {
            "schema": SNAPSHOT_SCHEMA,
            "domain": DOMAIN,
            "snapshot_id": snapshot_id,
            "files": copied_files,
        }
        _write_json_atomic(partial_dir / "files.json", files_payload)
        _write_json_atomic(partial_dir / "snapshot.json", metadata)
        _validate_snapshot_dir(partial_dir, expected_snapshot_id=snapshot_id)
        try:
            partial_dir.rename(final_dir)
        except OSError as err:
            raise _local_version_os_error(
                err,
                "snapshot_finalize_failed",
                "Failed to finalize local HI-only snapshot.",
            ) from err
    except Exception:
        if partial_dir.exists():
            _delete_tree_scoped(partial_dir, snapshot_root)
        raise

    retention = _enforce_retention(
        snapshots_root,
        snapshot_root,
        retain_count=retain_count,
        max_total_bytes=max_total_bytes,
        protected_snapshot_id=snapshot_id,
    )
    return {
        "success": True,
        "operation": "create",
        "snapshot_id": snapshot_id,
        "created_at_utc": metadata["created_at_utc"],
        "manifest_version": manifest["version"],
        "file_count": metadata["file_count"],
        "total_bytes": metadata["total_bytes"],
        "content_hash": metadata["content_hash"],
        "retained_snapshots": retention["retained_snapshots"],
        "retained_count": len(retention["retained_snapshots"]),
        "deleted_snapshots": retention["deleted_snapshots"],
        "partial_snapshots_cleaned": cleaned_partials,
        "latest_error_category": None,
        "running_code_unchanged_until_restart": True,
        "retention": {
            "retain_count": retain_count,
            "max_total_bytes": max_total_bytes,
            "hard_max_total_bytes": HARD_MAX_TOTAL_BYTES,
        },
    }


def list_saved_versions_sync(config_path: Callable[..., str]) -> dict[str, Any]:
    """List finalized local HI-only snapshots."""

    snapshot_root = _snapshot_root(config_path)
    snapshots_root = snapshot_root / SNAPSHOTS_DIR
    snapshot_root_exists = snapshot_root.exists()
    snapshot_root_writable = bool(snapshot_root.is_dir() and os.access(snapshot_root, os.W_OK))
    valid: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []

    if snapshot_root.exists() and not snapshot_root.is_dir():
        raise LocalVersionError(
            "snapshot_root_invalid",
            "Local HI-only snapshot root is not a directory.",
        )
    if snapshots_root.exists() and not snapshots_root.is_dir():
        raise LocalVersionError(
            "snapshot_root_invalid",
            "Local HI-only snapshot directory is not a directory.",
        )

    if snapshots_root.is_dir():
        for child in sorted(snapshots_root.iterdir(), key=lambda path: path.name):
            if not child.is_dir():
                continue
            try:
                summary = _validate_snapshot_dir(child)
            except LocalVersionError as err:
                invalid.append(
                    {
                        "snapshot_id": child.name,
                        "error_category": err.category,
                        "message": err.message,
                    }
                )
            else:
                valid.append(summary)

    valid.sort(key=lambda item: (str(item.get("created_at_utc") or ""), str(item.get("snapshot_id") or "")))
    latest = valid[-1] if valid else None
    return {
        "success": True,
        "operation": "list",
        "valid_snapshots": valid,
        "invalid_snapshots": invalid,
        "latest_snapshot": latest,
        "retained_count": len(valid),
        "total_size": sum(int(item.get("total_bytes") or 0) for item in valid),
        "snapshot_root_exists": bool(snapshot_root_exists),
        "snapshot_root_writable": snapshot_root_writable,
        "latest_error_category": None,
        "retention": {
            "retain_count": DEFAULT_RETAIN_COUNT,
            "max_total_bytes": DEFAULT_MAX_TOTAL_BYTES,
            "hard_max_total_bytes": HARD_MAX_TOTAL_BYTES,
        },
    }


def _local_version_lock(hass: Any) -> asyncio.Lock:
    domain_data = hass.data.setdefault(DOMAIN, {})
    lock = domain_data.get(LOCAL_VERSION_LOCK_KEY)
    if lock is None:
        lock = asyncio.Lock()
        domain_data[LOCAL_VERSION_LOCK_KEY] = lock
    return lock


def _set_cached_local_version_status(hass: Any, status: dict[str, Any]) -> None:
    hass.data.setdefault(DOMAIN, {})[LOCAL_VERSION_STATE_KEY] = status


def _not_checked_status() -> dict[str, Any]:
    return {
        "feature_status": "available",
        "status": "not_checked",
        "snapshot_root": f"/config/{SNAPSHOT_ROOT_DIR}",
        "snapshot_root_exists": False,
        "snapshot_root_writable": None,
        "snapshot_count": 0,
        "latest_snapshot_id": None,
        "latest_snapshot_version": None,
        "latest_snapshot_created_at_utc": None,
        "latest_create_status": None,
        "latest_list_status": None,
        "latest_error_category": None,
        "retention": {
            "retain_count": DEFAULT_RETAIN_COUNT,
            "max_total_bytes": DEFAULT_MAX_TOTAL_BYTES,
            "hard_max_total_bytes": HARD_MAX_TOTAL_BYTES,
        },
    }


def _compact_status_from_create(result: dict[str, Any]) -> dict[str, Any]:
    status = _not_checked_status()
    status.update(
        {
            "status": "created",
            "snapshot_root_exists": True,
            "snapshot_root_writable": True,
            "snapshot_count": result.get("retained_count", 0),
            "latest_snapshot_id": result.get("snapshot_id"),
            "latest_snapshot_version": result.get("manifest_version"),
            "latest_snapshot_created_at_utc": result.get("created_at_utc"),
            "latest_create_status": "success",
            "latest_error_category": None,
            "retention": result.get("retention") or status["retention"],
        }
    )
    return status


def _compact_status_from_list(result: dict[str, Any]) -> dict[str, Any]:
    latest = result.get("latest_snapshot") or {}
    status = _not_checked_status()
    status.update(
        {
            "status": "listed",
            "snapshot_root_exists": bool(result.get("snapshot_root_exists")),
            "snapshot_root_writable": result.get("snapshot_root_writable"),
            "snapshot_count": result.get("retained_count", 0),
            "latest_snapshot_id": latest.get("snapshot_id"),
            "latest_snapshot_version": latest.get("manifest_version"),
            "latest_snapshot_created_at_utc": latest.get("created_at_utc"),
            "latest_list_status": "success",
            "latest_error_category": result.get("latest_error_category"),
            "retention": result.get("retention") or status["retention"],
        }
    )
    return status


def _error_status(operation: str, err: LocalVersionError) -> dict[str, Any]:
    status = _not_checked_status()
    status.update(
        {
            "status": "failed",
            f"latest_{operation}_status": "failed",
            "latest_error_category": err.category,
        }
    )
    return status


def _path_from_config(config_path: Callable[..., str]) -> Path:
    try:
        return Path(config_path()).resolve()
    except TypeError:
        return Path(config_path("")).resolve()


def _active_integration_path(config_path: Callable[..., str]) -> Path:
    return Path(config_path("custom_components", DOMAIN)).resolve()


def _snapshot_root(config_path: Callable[..., str]) -> Path:
    return Path(config_path(SNAPSHOT_ROOT_DIR)).resolve()


def _ensure_snapshot_path(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as err:
        raise LocalVersionError(
            "snapshot_path_outside_root",
            "Refusing to write outside the configured local HI-only snapshot root.",
            details={"path": path.name},
        ) from err


def _ensure_snapshot_dirs(snapshot_root: Path, snapshots_root: Path, tmp_root: Path) -> None:
    try:
        snapshot_root.mkdir(parents=True, exist_ok=True)
        snapshots_root.mkdir(parents=True, exist_ok=True)
        tmp_root.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        raise _local_version_os_error(
            err,
            "snapshot_root_unwritable",
            "Local HI-only snapshot root is not writable.",
        ) from err

    _assert_writable(snapshot_root)


def _assert_writable(path: Path) -> None:
    probe = path / ".hi_snapshot_write_test"
    try:
        with open(probe, "w", encoding="utf-8") as handle:
            handle.write("ok")
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as err:
        raise _local_version_os_error(
            err,
            "snapshot_root_unwritable",
            "Local HI-only snapshot root is not writable.",
        ) from err
    finally:
        try:
            if probe.exists():
                probe.unlink()
        except OSError:
            pass


def _read_active_manifest(active_root: Path) -> dict[str, str]:
    if not active_root.exists() or not active_root.is_dir():
        raise LocalVersionError(
            "active_folder_missing",
            "Active Humidity Intelligence custom integration folder was not found.",
        )
    manifest = _read_manifest(active_root / "manifest.json")
    domain = manifest.get("domain")
    version = manifest.get("version")
    if domain != DOMAIN:
        raise LocalVersionError(
            "manifest_domain_mismatch",
            "Active manifest does not belong to Humidity Intelligence.",
            details={"manifest_domain": domain},
        )
    if not version:
        raise LocalVersionError(
            "manifest_version_missing",
            "Active Humidity Intelligence manifest is missing a version.",
        )
    return {"domain": str(domain), "version": str(version)}


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise LocalVersionError(
            "manifest_missing",
            "Humidity Intelligence manifest.json was not found.",
        )
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as err:
        raise LocalVersionError(
            "manifest_corrupt",
            "Humidity Intelligence manifest.json is not valid JSON.",
        ) from err
    except OSError as err:
        raise _local_version_os_error(
            err,
            "manifest_read_failed",
            "Humidity Intelligence manifest.json could not be read.",
        ) from err
    if not isinstance(data, dict):
        raise LocalVersionError(
            "manifest_corrupt",
            "Humidity Intelligence manifest.json must contain a JSON object.",
        )
    return data


def _build_file_manifest(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in _EXCLUDED_DIRS)
        for filename in sorted(filenames):
            if filename in _EXCLUDED_FILES:
                continue
            path = Path(dirpath) / filename
            if path.is_symlink():
                raise LocalVersionError(
                    "source_symlink_unsupported",
                    "Local HI-only snapshots do not follow symlinked integration files.",
                    details={"path": path.relative_to(root).as_posix()},
                )
            try:
                stat = path.stat()
            except OSError as err:
                raise _local_version_os_error(
                    err,
                    "source_file_read_failed",
                    "Failed to stat active Humidity Intelligence integration files.",
                ) from err
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "size": int(stat.st_size),
                    "mtime_ns": int(stat.st_mtime_ns),
                    "sha256": _file_hash(path),
                }
            )
    rows.sort(key=lambda row: row["path"])
    return rows


def _copy_and_verify_source(source_root: Path, copied_root: Path, expected_files: list[dict[str, Any]]) -> None:
    copied_root.mkdir(parents=True, exist_ok=False)
    for row in expected_files:
        source = source_root / row["path"]
        dest = copied_root / row["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(source, dest)
        except OSError as err:
            raise _local_version_os_error(
                err,
                "snapshot_copy_failed",
                "Failed to copy active Humidity Intelligence integration files.",
            ) from err
        if not dest.exists() or _file_hash(dest) != row["sha256"]:
            raise LocalVersionError(
                "copied_hash_mismatch",
                "Copied file content does not match the pre-copy source manifest.",
                details={"path": row["path"]},
            )


def _validate_snapshot_dir(snapshot_dir: Path, *, expected_snapshot_id: str | None = None) -> dict[str, Any]:
    metadata_path = snapshot_dir / "snapshot.json"
    if not metadata_path.exists():
        raise LocalVersionError(
            "snapshot_metadata_missing",
            "Finalized snapshot is missing snapshot.json.",
        )
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise LocalVersionError(
            "snapshot_metadata_corrupt",
            "Finalized snapshot metadata is not valid JSON.",
        ) from err
    except OSError as err:
        raise _local_version_os_error(
            err,
            "snapshot_metadata_read_failed",
            "Finalized snapshot metadata could not be read.",
        ) from err

    if metadata.get("schema") != SNAPSHOT_SCHEMA:
        raise LocalVersionError(
            "snapshot_schema_mismatch",
            "Finalized snapshot metadata schema is not supported.",
        )
    if metadata.get("domain") != DOMAIN or metadata.get("manifest_domain") != DOMAIN:
        raise LocalVersionError(
            "snapshot_domain_mismatch",
            "Finalized snapshot metadata is not for Humidity Intelligence.",
        )
    expected_id = expected_snapshot_id or snapshot_dir.name
    if metadata.get("snapshot_id") != expected_id:
        raise LocalVersionError(
            "snapshot_id_mismatch",
            "Finalized snapshot folder name does not match snapshot metadata.",
        )

    copied_root = snapshot_dir / DOMAIN
    if not copied_root.is_dir():
        raise LocalVersionError(
            "snapshot_package_missing",
            "Finalized snapshot is missing the copied Humidity Intelligence package.",
        )
    manifest = _read_manifest(copied_root / "manifest.json")
    if manifest.get("domain") != DOMAIN:
        raise LocalVersionError(
            "snapshot_manifest_domain_mismatch",
            "Finalized snapshot package manifest is not for Humidity Intelligence.",
        )
    if str(manifest.get("version") or "") != str(metadata.get("manifest_version") or ""):
        raise LocalVersionError(
            "snapshot_manifest_version_mismatch",
            "Finalized snapshot package manifest version does not match snapshot metadata.",
        )

    files = _build_file_manifest(copied_root)
    copied_hash = _tree_hash(files)
    if metadata.get("content_hash") != f"sha256:{copied_hash}":
        raise LocalVersionError(
            "snapshot_hash_mismatch",
            "Finalized snapshot content hash does not match copied files.",
        )
    if int(metadata.get("file_count") or 0) != len(files):
        raise LocalVersionError(
            "snapshot_file_count_mismatch",
            "Finalized snapshot file count does not match copied files.",
        )
    if int(metadata.get("total_bytes") or 0) != sum(row["size"] for row in files):
        raise LocalVersionError(
            "snapshot_total_bytes_mismatch",
            "Finalized snapshot byte count does not match copied files.",
        )

    return {
        "snapshot_id": str(metadata.get("snapshot_id")),
        "created_at_utc": str(metadata.get("created_at_utc")),
        "manifest_version": str(metadata.get("manifest_version")),
        "file_count": int(metadata.get("file_count") or 0),
        "total_bytes": int(metadata.get("total_bytes") or 0),
        "content_hash": str(metadata.get("content_hash")),
        "running_code_unchanged_until_restart": bool(
            metadata.get("running_code_unchanged_until_restart")
        ),
        "pinned": bool(metadata.get("pinned", False)),
    }


def _enforce_retention(
    snapshots_root: Path,
    snapshot_root: Path,
    *,
    retain_count: int,
    max_total_bytes: int,
    protected_snapshot_id: str,
) -> dict[str, list[str]]:
    snapshots: list[dict[str, Any]] = []
    for child in sorted(snapshots_root.iterdir(), key=lambda path: path.name):
        if not child.is_dir():
            continue
        try:
            summary = _validate_snapshot_dir(child)
        except LocalVersionError:
            continue
        summary["path"] = child
        snapshots.append(summary)

    snapshots.sort(key=lambda item: (str(item.get("created_at_utc") or ""), str(item.get("snapshot_id") or "")))
    deleted: list[str] = []

    def current_total() -> int:
        return sum(int(item.get("total_bytes") or 0) for item in snapshots)

    while len(snapshots) > retain_count:
        index = _oldest_deletable_index(snapshots, protected_snapshot_id)
        if index is None:
            break
        item = snapshots.pop(index)
        _delete_tree_scoped(item["path"], snapshot_root)
        deleted.append(item["snapshot_id"])

    while current_total() > max_total_bytes and len(snapshots) > MIN_RETAIN_COUNT:
        index = _oldest_deletable_index(snapshots, protected_snapshot_id)
        if index is None:
            break
        item = snapshots.pop(index)
        _delete_tree_scoped(item["path"], snapshot_root)
        deleted.append(item["snapshot_id"])

    return {
        "retained_snapshots": [str(item["snapshot_id"]) for item in snapshots],
        "deleted_snapshots": deleted,
    }


def _oldest_deletable_index(snapshots: list[dict[str, Any]], protected_snapshot_id: str) -> int | None:
    for index, item in enumerate(snapshots):
        if item.get("pinned"):
            continue
        if item.get("snapshot_id") == protected_snapshot_id and len(snapshots) <= MIN_RETAIN_COUNT:
            continue
        if item.get("snapshot_id") == protected_snapshot_id:
            continue
        return index
    return None


def _cleanup_stale_partials(
    tmp_root: Path,
    snapshot_root: Path,
    *,
    now: datetime,
    stale_after_seconds: int,
) -> list[str]:
    cleaned: list[str] = []
    if not tmp_root.is_dir():
        return cleaned
    now_ts = now.timestamp()
    for child in sorted(tmp_root.iterdir(), key=lambda path: path.name):
        if not child.is_dir() or not child.name.endswith(".partial"):
            continue
        try:
            age = now_ts - child.stat().st_mtime
        except OSError:
            continue
        if age < stale_after_seconds:
            continue
        _delete_tree_scoped(child, snapshot_root)
        cleaned.append(child.name)
    return cleaned


def _delete_tree_scoped(path: Path, snapshot_root: Path) -> None:
    try:
        resolved = path.resolve()
        root = snapshot_root.resolve()
        resolved.relative_to(root)
        if resolved == root:
            raise ValueError("refusing to delete snapshot root")
        shutil.rmtree(resolved)
    except ValueError as err:
        raise LocalVersionError(
            "snapshot_delete_outside_root",
            "Refusing to delete outside the local HI-only snapshot root.",
            details={"path": path.name},
        ) from err
    except OSError as err:
        raise _local_version_os_error(
            err,
            "snapshot_delete_failed",
            "Failed to delete a local HI-only snapshot path.",
        ) from err


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".hi_snapshot_", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except OSError as err:
        raise _local_version_os_error(
            err,
            "snapshot_metadata_write_failed",
            "Failed to write local HI-only snapshot metadata.",
        ) from err
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as err:
        raise _local_version_os_error(
            err,
            "source_file_read_failed",
            "Failed to hash Humidity Intelligence integration files.",
        ) from err
    return digest.hexdigest()


def _tree_hash(files: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in sorted(files, key=lambda item: item["path"]):
        digest.update(str(row["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(row["size"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(row["sha256"]).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _snapshot_id(version: str, created_at: datetime, content_hash: str) -> str:
    return f"{_safe_id_part(version)}_{created_at.strftime('%Y-%m-%dT%H%M%SZ')}_{content_hash[:7]}"


def _safe_id_part(value: str) -> str:
    text = _SNAPSHOT_ID_SAFE_RE.sub("_", str(value or "").strip())
    return text.strip("._-")[:80] or "unknown"


def _utc_now(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _format_created_at(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _bounded_retain_count(value: int) -> int:
    try:
        count = int(value)
    except (TypeError, ValueError):
        count = DEFAULT_RETAIN_COUNT
    return max(MIN_RETAIN_COUNT, min(MAX_RETAIN_COUNT, count))


def _bounded_max_total_bytes(value: int) -> int:
    try:
        size = int(value)
    except (TypeError, ValueError):
        size = DEFAULT_MAX_TOTAL_BYTES
    return max(1, min(HARD_MAX_TOTAL_BYTES, size))


def _local_version_os_error(err: OSError, default_category: str, message: str) -> LocalVersionError:
    if getattr(err, "errno", None) == errno.ENOSPC:
        category = "filesystem_no_space"
    elif getattr(err, "errno", None) in {errno.EACCES, errno.EPERM, errno.EROFS}:
        category = "filesystem_permission"
    elif isinstance(err, (FileExistsError, NotADirectoryError)):
        category = "snapshot_root_unwritable" if default_category == "snapshot_root_unwritable" else default_category
    else:
        category = default_category
    return LocalVersionError(category, message, details={"errno": getattr(err, "errno", None)})
