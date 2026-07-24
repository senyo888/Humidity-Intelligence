"""Confined filesystem operations for caller-selectable HI report exports."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json
import os
import re
import secrets
import stat
import threading
from typing import Any, Iterator, Mapping


REPORT_EXPORT_DIRECTORY_COMPONENTS = ("humidity_intelligence", "exports")
REPORT_EXPORT_RELATIVE_DIRECTORY = "humidity_intelligence/exports"
DEFAULT_DIAGNOSTICS_REPORT_FILENAME = "humidity_intelligence_diagnostics.json"
DEFAULT_DIAGNOSTICS_REPORT_RELATIVE_PATH = (
    f"{REPORT_EXPORT_RELATIVE_DIRECTORY}/{DEFAULT_DIAGNOSTICS_REPORT_FILENAME}"
)

_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_OWNED_REPORT_FILENAME_PREFIX = "humidity_intelligence_"
_OWNED_REPORT_FILENAME_SUFFIX = ".json"
_TEMP_CREATE_ATTEMPTS = 128
_REPORT_OPERATION_LOCK = threading.Lock()


class ReportExportError(RuntimeError):
    """Raised when an owned report operation cannot remain safely confined."""


@dataclass(frozen=True)
class ReportRemovalPlan:
    """Identity-bound plan for the exact default diagnostics export."""

    relative_path: str
    directory_device: int
    directory_inode: int
    device: int
    inode: int


def validate_owned_report_filename(value: str) -> str:
    """Validate the exact caller-selectable HI report basename contract."""
    if (
        not isinstance(value, str)
        or not _SAFE_FILENAME_RE.fullmatch(value)
        or ".." in value
        or not value.startswith(_OWNED_REPORT_FILENAME_PREFIX)
        or not value.endswith(_OWNED_REPORT_FILENAME_SUFFIX)
    ):
        raise ReportExportError(
            "Report filename must use humidity_intelligence_*.json"
        )
    return value


def _require_secure_primitives() -> None:
    missing = [
        name
        for name in ("O_CLOEXEC", "O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")
        if not hasattr(os, name)
    ]
    if missing:
        raise ReportExportError(
            "Secure report export is unavailable; missing OS primitive(s): "
            + ", ".join(missing)
        )


def _directory_open_flags(*, nofollow: bool) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC
    if nofollow:
        flags |= os.O_NOFOLLOW
    return flags


def _open_config_root(config_root: str | os.PathLike[str]) -> int:
    try:
        return os.open(os.fspath(config_root), _directory_open_flags(nofollow=False))
    except (NotImplementedError, OSError, TypeError) as err:
        raise ReportExportError(
            f"Unable to open the Home Assistant config directory securely: {err}"
        ) from err


def _open_directory_component(
    parent_fd: int,
    component: str,
    *,
    create: bool,
) -> int | None:
    flags = _directory_open_flags(nofollow=True)
    try:
        return os.open(component, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        if not create:
            return None
        try:
            os.mkdir(component, mode=0o777, dir_fd=parent_fd)
        except FileExistsError:
            pass
        except (NotImplementedError, OSError, TypeError) as err:
            raise ReportExportError(
                f"Unable to create owned report directory component {component!r}: {err}"
            ) from err
        try:
            return os.open(component, flags, dir_fd=parent_fd)
        except (NotImplementedError, OSError, TypeError) as err:
            raise ReportExportError(
                f"Unable to verify owned report directory component {component!r}: {err}"
            ) from err
    except (NotImplementedError, OSError, TypeError) as err:
        raise ReportExportError(
            f"Owned report directory component {component!r} is unsafe: {err}"
        ) from err


@contextmanager
def _open_report_export_directory(
    config_root: str | os.PathLike[str],
    *,
    create: bool,
) -> Iterator[int | None]:
    _require_secure_primitives()
    opened_fds: list[int] = []
    try:
        current_fd = _open_config_root(config_root)
        opened_fds.append(current_fd)
        for component in REPORT_EXPORT_DIRECTORY_COMPONENTS:
            next_fd = _open_directory_component(
                current_fd,
                component,
                create=create,
            )
            if next_fd is None:
                yield None
                return
            opened_fds.append(next_fd)
            current_fd = next_fd
        yield current_fd
    finally:
        for fd in reversed(opened_fds):
            try:
                os.close(fd)
            except OSError:
                pass


def _stat_regular_file(
    directory_fd: int,
    filename: str,
    *,
    allow_absent: bool,
) -> os.stat_result | None:
    try:
        metadata = os.stat(
            filename,
            dir_fd=directory_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        if allow_absent:
            return None
        raise ReportExportError(f"Owned report changed before operation: {filename}")
    except (NotImplementedError, OSError, TypeError) as err:
        raise ReportExportError(
            f"Unable to inspect owned report {filename!r} securely: {err}"
        ) from err
    if not stat.S_ISREG(metadata.st_mode):
        raise ReportExportError(
            f"Owned report target must be a regular non-symlink file: {filename}"
        )
    return metadata


def _fstat_directory(directory_fd: int) -> os.stat_result:
    try:
        metadata = os.fstat(directory_fd)
    except OSError as err:
        raise ReportExportError(
            f"Unable to inspect owned report directory descriptor: {err}"
        ) from err
    if not stat.S_ISDIR(metadata.st_mode):
        raise ReportExportError("Owned report directory descriptor is not a directory")
    return metadata


def _verify_current_export_location(
    config_root: str | os.PathLike[str],
    held_directory_fd: int,
    *,
    filename: str,
    expected_file_identity: tuple[int, int] | None,
) -> None:
    """Prove the held export directory still owns the advertised current path."""
    held_directory = _fstat_directory(held_directory_fd)
    with _open_report_export_directory(config_root, create=False) as current_fd:
        if current_fd is None:
            raise ReportExportError(
                "Owned report directory changed during the filesystem operation"
            )
        current_directory = _fstat_directory(current_fd)
        if (
            current_directory.st_dev,
            current_directory.st_ino,
        ) != (
            held_directory.st_dev,
            held_directory.st_ino,
        ):
            raise ReportExportError(
                "Owned report directory changed during the filesystem operation"
            )

        current_file = _stat_regular_file(
            current_fd,
            filename,
            allow_absent=expected_file_identity is None,
        )
        if expected_file_identity is None:
            if current_file is not None:
                raise ReportExportError(
                    f"Owned report unexpectedly reappeared during cleanup: {filename}"
                )
            return
        if current_file is None or (
            current_file.st_dev,
            current_file.st_ino,
        ) != expected_file_identity:
            raise ReportExportError(
                f"Owned report changed at the advertised destination: {filename}"
            )


def _create_temporary_report(directory_fd: int) -> tuple[int, str]:
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | os.O_NOFOLLOW
        | os.O_CLOEXEC
    )
    for _attempt in range(_TEMP_CREATE_ATTEMPTS):
        filename = f".hi_report_{secrets.token_hex(12)}.tmp"
        try:
            descriptor = os.open(
                filename,
                flags,
                0o600,
                dir_fd=directory_fd,
            )
        except FileExistsError:
            continue
        except (NotImplementedError, OSError, TypeError) as err:
            raise ReportExportError(
                f"Unable to create a confined temporary report file: {err}"
            ) from err
        return descriptor, filename
    raise ReportExportError("Unable to allocate a unique temporary report file")


def _unlink_temporary_report(
    directory_fd: int,
    filename: str,
    *,
    expected_device: int,
    expected_inode: int,
) -> None:
    try:
        metadata = os.stat(
            filename,
            dir_fd=directory_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return
    except (NotImplementedError, OSError, TypeError) as err:
        raise ReportExportError(
            f"Unable to inspect temporary report {filename!r}: {err}"
        ) from err
    identity_changed = (metadata.st_dev, metadata.st_ino) != (
        expected_device,
        expected_inode,
    )
    if identity_changed:
        raise ReportExportError(
            "Temporary report changed during cleanup; refusing to unlink it"
        )
    try:
        os.unlink(filename, dir_fd=directory_fd)
    except FileNotFoundError:
        return
    except (NotImplementedError, OSError, TypeError) as err:
        raise ReportExportError(
            f"Unable to remove temporary report file {filename!r}: {err}"
        ) from err


def write_owned_report(
    config_root: str | os.PathLike[str],
    filename: str,
    payload: Mapping[str, Any],
) -> str:
    """Atomically write one validated report inside the owned export directory."""
    validate_owned_report_filename(filename)
    with _REPORT_OPERATION_LOCK:
        return _write_owned_report_locked(config_root, filename, payload)


def _write_owned_report_locked(
    config_root: str | os.PathLike[str],
    filename: str,
    payload: Mapping[str, Any],
) -> str:
    """Write one report while serializing in-process report replacements."""
    with _open_report_export_directory(config_root, create=True) as directory_fd:
        if directory_fd is None:
            raise ReportExportError("Owned report directory could not be created")

        temporary_fd, temporary_name = _create_temporary_report(directory_fd)
        temporary_identity = os.fstat(temporary_fd)
        if not stat.S_ISREG(temporary_identity.st_mode):
            os.close(temporary_fd)
            raise ReportExportError("Temporary report descriptor is not a regular file")
        temporary_exists = True
        try:
            stream = os.fdopen(os.dup(temporary_fd), "w", encoding="utf-8")
            with stream:
                json.dump(payload, stream, indent=2, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())

            named_temporary = _stat_regular_file(
                directory_fd,
                temporary_name,
                allow_absent=False,
            )
            if named_temporary is None or (
                named_temporary.st_dev,
                named_temporary.st_ino,
            ) != (
                temporary_identity.st_dev,
                temporary_identity.st_ino,
            ):
                raise ReportExportError(
                    "Temporary report changed before atomic replacement"
                )
            _stat_regular_file(
                directory_fd,
                filename,
                allow_absent=True,
            )
            try:
                os.replace(
                    temporary_name,
                    filename,
                    src_dir_fd=directory_fd,
                    dst_dir_fd=directory_fd,
                )
            except (NotImplementedError, OSError, TypeError) as err:
                raise ReportExportError(
                    f"Unable to atomically replace owned report {filename!r}: {err}"
                ) from err
            temporary_exists = False
            final_metadata = _stat_regular_file(
                directory_fd,
                filename,
                allow_absent=False,
            )
            if final_metadata is None or (
                final_metadata.st_dev,
                final_metadata.st_ino,
            ) != (
                temporary_identity.st_dev,
                temporary_identity.st_ino,
            ):
                raise ReportExportError(
                    "Owned report changed during atomic replacement"
                )
            try:
                os.fsync(directory_fd)
            except (OSError, TypeError) as err:
                raise ReportExportError(
                    f"Owned report was replaced but directory sync failed: {err}"
                ) from err
            _verify_current_export_location(
                config_root,
                directory_fd,
                filename=filename,
                expected_file_identity=(
                    temporary_identity.st_dev,
                    temporary_identity.st_ino,
                ),
            )
        finally:
            try:
                os.close(temporary_fd)
            except OSError:
                pass
            if temporary_exists:
                _unlink_temporary_report(
                    directory_fd,
                    temporary_name,
                    expected_device=temporary_identity.st_dev,
                    expected_inode=temporary_identity.st_ino,
                )

    return f"{REPORT_EXPORT_RELATIVE_DIRECTORY}/{filename}"


def plan_default_diagnostics_report_removal(
    config_root: str | os.PathLike[str],
) -> list[ReportRemovalPlan]:
    """Return the exact removable default diagnostics export, if present."""
    with _open_report_export_directory(config_root, create=False) as directory_fd:
        if directory_fd is None:
            return []
        metadata = _stat_regular_file(
            directory_fd,
            DEFAULT_DIAGNOSTICS_REPORT_FILENAME,
            allow_absent=True,
        )
        if metadata is None:
            return []
        directory_metadata = _fstat_directory(directory_fd)
    return [
        ReportRemovalPlan(
            relative_path=DEFAULT_DIAGNOSTICS_REPORT_RELATIVE_PATH,
            directory_device=directory_metadata.st_dev,
            directory_inode=directory_metadata.st_ino,
            device=metadata.st_dev,
            inode=metadata.st_ino,
        )
    ]


def remove_default_diagnostics_report(
    config_root: str | os.PathLike[str],
    plan: ReportRemovalPlan,
) -> bool:
    """Remove only the default diagnostics export after descriptor revalidation."""
    if (
        not isinstance(plan, ReportRemovalPlan)
        or plan.relative_path != DEFAULT_DIAGNOSTICS_REPORT_RELATIVE_PATH
    ):
        raise ReportExportError("Invalid default diagnostics removal plan")
    with _REPORT_OPERATION_LOCK:
        return _remove_default_diagnostics_report_locked(config_root, plan)


def _remove_default_diagnostics_report_locked(
    config_root: str | os.PathLike[str],
    plan: ReportRemovalPlan,
) -> bool:
    """Remove the planned report while excluding in-process report writes."""
    with _open_report_export_directory(config_root, create=False) as directory_fd:
        if directory_fd is None:
            return False
        directory_metadata = _fstat_directory(directory_fd)
        if (
            directory_metadata.st_dev,
            directory_metadata.st_ino,
        ) != (
            plan.directory_device,
            plan.directory_inode,
        ):
            raise ReportExportError(
                "Owned report directory changed after cleanup preview"
            )

        expected = _stat_regular_file(
            directory_fd,
            DEFAULT_DIAGNOSTICS_REPORT_FILENAME,
            allow_absent=True,
        )
        if expected is None:
            return False
        if (expected.st_dev, expected.st_ino) != (plan.device, plan.inode):
            raise ReportExportError(
                "Default diagnostics export changed after cleanup preview"
            )

        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
        try:
            report_fd = os.open(
                DEFAULT_DIAGNOSTICS_REPORT_FILENAME,
                flags,
                dir_fd=directory_fd,
            )
        except FileNotFoundError:
            return False
        except (NotImplementedError, OSError, TypeError) as err:
            raise ReportExportError(
                "Unable to open the default diagnostics export securely: "
                f"{err}"
            ) from err
        try:
            opened = os.fstat(report_fd)
            if not stat.S_ISREG(opened.st_mode):
                raise ReportExportError(
                    "Default diagnostics export is no longer a regular file"
                )
            if (opened.st_dev, opened.st_ino) != (plan.device, plan.inode):
                raise ReportExportError(
                    "Default diagnostics export changed after cleanup preview"
                )
            current = _stat_regular_file(
                directory_fd,
                DEFAULT_DIAGNOSTICS_REPORT_FILENAME,
                allow_absent=False,
            )
            if current is None or (
                current.st_dev,
                current.st_ino,
            ) != (
                plan.device,
                plan.inode,
            ):
                raise ReportExportError(
                    "Default diagnostics export changed during cleanup"
                )
            try:
                os.unlink(
                    DEFAULT_DIAGNOSTICS_REPORT_FILENAME,
                    dir_fd=directory_fd,
                )
                os.fsync(directory_fd)
            except (NotImplementedError, OSError, TypeError) as err:
                raise ReportExportError(
                    f"Unable to remove the default diagnostics export: {err}"
                ) from err
            _verify_current_export_location(
                config_root,
                directory_fd,
                filename=DEFAULT_DIAGNOSTICS_REPORT_FILENAME,
                expected_file_identity=None,
            )
        finally:
            try:
                os.close(report_fd)
            except OSError:
                pass
    return True
