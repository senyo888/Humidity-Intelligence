"""Confined filesystem operations for HI-owned report and UI exports."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json
import logging
import os
import re
import secrets
import stat
import threading
from typing import Any, Callable, ContextManager, Iterable, Iterator, Mapping, TextIO


REPORT_EXPORT_DIRECTORY_COMPONENTS = ("humidity_intelligence", "exports")
REPORT_EXPORT_RELATIVE_DIRECTORY = "humidity_intelligence/exports"
UI_EXPORT_DIRECTORY_COMPONENTS = ("humidity_intelligence", "ui")
UI_EXPORT_RELATIVE_DIRECTORY = "humidity_intelligence/ui"
DEFAULT_DIAGNOSTICS_REPORT_FILENAME = "humidity_intelligence_diagnostics.json"
DEFAULT_DIAGNOSTICS_REPORT_RELATIVE_PATH = (
    f"{REPORT_EXPORT_RELATIVE_DIRECTORY}/{DEFAULT_DIAGNOSTICS_REPORT_FILENAME}"
)
DEFAULT_SELF_CHECK_REPORT_FILENAME = "humidity_intelligence_self_check.json"
DEFAULT_SELF_CHECK_REPORT_RELATIVE_PATH = (
    f"{REPORT_EXPORT_RELATIVE_DIRECTORY}/{DEFAULT_SELF_CHECK_REPORT_FILENAME}"
)

_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_SAFE_UI_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,255}$")
_OWNED_REPORT_FILENAME_PREFIX = "humidity_intelligence_"
_OWNED_REPORT_FILENAME_SUFFIX = ".json"
_OWNED_UI_FILENAME_SUFFIX = ".yaml"
_TEMP_CREATE_ATTEMPTS = 128
_REPORT_OPERATION_LOCK = threading.Lock()
_LOGGER = logging.getLogger(__name__)


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


def validate_owned_ui_filename(value: str) -> str:
    """Validate one direct generated-UI YAML basename."""
    if (
        not isinstance(value, str)
        or not _SAFE_UI_FILENAME_RE.fullmatch(value)
        or ".." in value
        or not value.endswith(_OWNED_UI_FILENAME_SUFFIX)
    ):
        raise ReportExportError(
            "UI export filename must be a safe direct .yaml basename"
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
    artifact_label: str = "report",
) -> int | None:
    flags = _directory_open_flags(nofollow=True)
    try:
        return os.open(component, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        if not create:
            return None
        try:
            os.mkdir(component, mode=0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
        except (NotImplementedError, OSError, TypeError) as err:
            raise ReportExportError(
                f"Unable to create owned {artifact_label} directory component "
                f"{component!r}: {err}"
            ) from err
        try:
            return os.open(component, flags, dir_fd=parent_fd)
        except (NotImplementedError, OSError, TypeError) as err:
            raise ReportExportError(
                f"Unable to verify owned {artifact_label} directory component "
                f"{component!r}: {err}"
            ) from err
    except (NotImplementedError, OSError, TypeError) as err:
        raise ReportExportError(
            f"Owned {artifact_label} directory component {component!r} is unsafe: {err}"
        ) from err


@contextmanager
def _open_owned_export_directory(
    config_root: str | os.PathLike[str],
    directory_components: tuple[str, ...],
    *,
    create: bool,
    artifact_label: str,
) -> Iterator[int | None]:
    _require_secure_primitives()
    opened_fds: list[int] = []
    try:
        current_fd = _open_config_root(config_root)
        opened_fds.append(current_fd)
        for component in directory_components:
            next_fd = _open_directory_component(
                current_fd,
                component,
                create=create,
                artifact_label=artifact_label,
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


def _open_report_export_directory(
    config_root: str | os.PathLike[str],
    *,
    create: bool,
) -> ContextManager[int | None]:
    return _open_owned_export_directory(
        config_root,
        REPORT_EXPORT_DIRECTORY_COMPONENTS,
        create=create,
        artifact_label="report",
    )


def _open_ui_export_directory(
    config_root: str | os.PathLike[str],
    *,
    create: bool,
) -> ContextManager[int | None]:
    return _open_owned_export_directory(
        config_root,
        UI_EXPORT_DIRECTORY_COMPONENTS,
        create=create,
        artifact_label="UI export",
    )


def _stat_regular_file(
    directory_fd: int,
    filename: str,
    *,
    allow_absent: bool,
    artifact_label: str = "report",
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
        raise ReportExportError(
            f"Owned {artifact_label} changed before operation: {filename}"
        )
    except (NotImplementedError, OSError, TypeError) as err:
        raise ReportExportError(
            f"Unable to inspect owned {artifact_label} {filename!r} securely: {err}"
        ) from err
    if not stat.S_ISREG(metadata.st_mode):
        raise ReportExportError(
            f"Owned {artifact_label} target must be a regular non-symlink file: "
            f"{filename}"
        )
    return metadata


def _fstat_directory(
    directory_fd: int,
    *,
    artifact_label: str = "report",
) -> os.stat_result:
    try:
        metadata = os.fstat(directory_fd)
    except OSError as err:
        raise ReportExportError(
            f"Unable to inspect owned {artifact_label} directory descriptor: {err}"
        ) from err
    if not stat.S_ISDIR(metadata.st_mode):
        raise ReportExportError(
            f"Owned {artifact_label} directory descriptor is not a directory"
        )
    return metadata


def _verify_current_export_location(
    config_root: str | os.PathLike[str],
    held_directory_fd: int,
    *,
    filename: str,
    expected_file_identity: tuple[int, int] | None,
    open_directory: Callable[..., ContextManager[int | None]] = _open_report_export_directory,
    artifact_label: str = "report",
) -> None:
    """Prove the held directory still owns the advertised current path."""
    held_directory = _fstat_directory(
        held_directory_fd,
        artifact_label=artifact_label,
    )
    with open_directory(config_root, create=False) as current_fd:
        if current_fd is None:
            raise ReportExportError(
                f"Owned {artifact_label} directory changed during the filesystem operation"
            )
        current_directory = _fstat_directory(
            current_fd,
            artifact_label=artifact_label,
        )
        if (
            current_directory.st_dev,
            current_directory.st_ino,
        ) != (
            held_directory.st_dev,
            held_directory.st_ino,
        ):
            raise ReportExportError(
                f"Owned {artifact_label} directory changed during the filesystem operation"
            )

        current_file = _stat_regular_file(
            current_fd,
            filename,
            allow_absent=expected_file_identity is None,
            artifact_label=artifact_label,
        )
        if expected_file_identity is None:
            if current_file is not None:
                raise ReportExportError(
                    f"Owned {artifact_label} unexpectedly reappeared during cleanup: "
                    f"{filename}"
                )
            return
        if current_file is None or (
            current_file.st_dev,
            current_file.st_ino,
        ) != expected_file_identity:
            raise ReportExportError(
                f"Owned {artifact_label} changed at the advertised destination: "
                f"{filename}"
            )


def _create_temporary_artifact(
    directory_fd: int,
    *,
    prefix: str,
    suffix: str,
    mode: int,
    artifact_label: str,
) -> tuple[int, str]:
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | os.O_NOFOLLOW
        | os.O_CLOEXEC
    )
    for _attempt in range(_TEMP_CREATE_ATTEMPTS):
        filename = f"{prefix}{secrets.token_hex(12)}{suffix}"
        try:
            descriptor = os.open(
                filename,
                flags,
                mode,
                dir_fd=directory_fd,
            )
        except FileExistsError:
            continue
        except (NotImplementedError, OSError, TypeError) as err:
            raise ReportExportError(
                f"Unable to create a confined temporary {artifact_label} file: {err}"
            ) from err
        return descriptor, filename
    raise ReportExportError(
        f"Unable to allocate a unique temporary {artifact_label} file"
    )


def _unlink_temporary_report(
    directory_fd: int,
    filename: str,
    *,
    expected_device: int,
    expected_inode: int,
    artifact_label: str = "report",
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
            f"Unable to inspect temporary {artifact_label} {filename!r}: {err}"
        ) from err
    identity_changed = (metadata.st_dev, metadata.st_ino) != (
        expected_device,
        expected_inode,
    )
    if identity_changed:
        raise ReportExportError(
            f"Temporary {artifact_label} changed during cleanup; refusing to unlink it"
        )
    try:
        os.unlink(filename, dir_fd=directory_fd)
    except FileNotFoundError:
        return
    except (NotImplementedError, OSError, TypeError) as err:
        raise ReportExportError(
            f"Unable to remove temporary {artifact_label} file {filename!r}: {err}"
        ) from err


def write_owned_report(
    config_root: str | os.PathLike[str],
    filename: str,
    payload: Mapping[str, Any],
) -> str:
    """Atomically write one validated report inside the owned export directory."""
    validate_owned_report_filename(filename)

    def _serialize(stream: TextIO) -> None:
        json.dump(payload, stream, indent=2, sort_keys=True)

    with _REPORT_OPERATION_LOCK:
        return _write_owned_artifact_locked(
            config_root,
            filename,
            serialize=_serialize,
            open_directory=_open_report_export_directory,
            relative_directory=REPORT_EXPORT_RELATIVE_DIRECTORY,
            temporary_prefix=".hi_report_",
            temporary_suffix=".tmp",
            temporary_mode=0o600,
            artifact_label="report",
        )


def write_owned_ui_export(
    config_root: str | os.PathLike[str],
    filename: str,
    payload: str,
) -> str:
    """Atomically write one generated YAML file inside the owned UI directory."""
    validate_owned_ui_filename(filename)
    if not isinstance(payload, str):
        raise ReportExportError("UI export payload must be text")

    def _serialize(stream: TextIO) -> None:
        stream.write(payload)

    with _REPORT_OPERATION_LOCK:
        return _write_owned_artifact_locked(
            config_root,
            filename,
            serialize=_serialize,
            open_directory=_open_ui_export_directory,
            relative_directory=UI_EXPORT_RELATIVE_DIRECTORY,
            temporary_prefix=".hi_ui_",
            temporary_suffix=".tmp",
            temporary_mode=0o644,
            artifact_label="UI export",
        )


def _write_owned_artifact_locked(
    config_root: str | os.PathLike[str],
    filename: str,
    *,
    serialize: Callable[[TextIO], None],
    open_directory: Callable[..., ContextManager[int | None]],
    relative_directory: str,
    temporary_prefix: str,
    temporary_suffix: str,
    temporary_mode: int,
    artifact_label: str,
) -> str:
    """Write one artifact while serializing in-process replacements."""
    with open_directory(config_root, create=True) as directory_fd:
        if directory_fd is None:
            raise ReportExportError(
                f"Owned {artifact_label} directory could not be created"
            )

        temporary_fd, temporary_name = _create_temporary_artifact(
            directory_fd,
            prefix=temporary_prefix,
            suffix=temporary_suffix,
            mode=temporary_mode,
            artifact_label=artifact_label,
        )
        temporary_identity = os.fstat(temporary_fd)
        if not stat.S_ISREG(temporary_identity.st_mode):
            os.close(temporary_fd)
            raise ReportExportError(
                f"Temporary {artifact_label} descriptor is not a regular file"
            )
        temporary_exists = True
        try:
            stream = os.fdopen(os.dup(temporary_fd), "w", encoding="utf-8")
            with stream:
                serialize(stream)
                stream.flush()
                os.fsync(stream.fileno())

            named_temporary = _stat_regular_file(
                directory_fd,
                temporary_name,
                allow_absent=False,
                artifact_label=artifact_label,
            )
            if named_temporary is None or (
                named_temporary.st_dev,
                named_temporary.st_ino,
            ) != (
                temporary_identity.st_dev,
                temporary_identity.st_ino,
            ):
                raise ReportExportError(
                    f"Temporary {artifact_label} changed before atomic replacement"
                )
            _stat_regular_file(
                directory_fd,
                filename,
                allow_absent=True,
                artifact_label=artifact_label,
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
                    f"Unable to atomically replace owned {artifact_label} "
                    f"{filename!r}: {err}"
                ) from err
            temporary_exists = False
            final_metadata = _stat_regular_file(
                directory_fd,
                filename,
                allow_absent=False,
                artifact_label=artifact_label,
            )
            if final_metadata is None or (
                final_metadata.st_dev,
                final_metadata.st_ino,
            ) != (
                temporary_identity.st_dev,
                temporary_identity.st_ino,
            ):
                raise ReportExportError(
                    f"Owned {artifact_label} changed during atomic replacement"
                )
            try:
                os.fsync(directory_fd)
            except (OSError, TypeError) as err:
                raise ReportExportError(
                    f"Owned {artifact_label} was replaced but directory sync failed: "
                    f"{err}"
                ) from err
            _verify_current_export_location(
                config_root,
                directory_fd,
                filename=filename,
                expected_file_identity=(
                    temporary_identity.st_dev,
                    temporary_identity.st_ino,
                ),
                open_directory=open_directory,
                artifact_label=artifact_label,
            )
        finally:
            try:
                os.close(temporary_fd)
            except OSError:
                pass
            if temporary_exists:
                try:
                    _unlink_temporary_report(
                        directory_fd,
                        temporary_name,
                        expected_device=temporary_identity.st_dev,
                        expected_inode=temporary_identity.st_ino,
                        artifact_label=artifact_label,
                    )
                except ReportExportError:
                    _LOGGER.warning(
                        "Unable to remove temporary %s file after a failed write",
                        artifact_label,
                        exc_info=True,
                    )

    return f"{relative_directory}/{filename}"


def plan_default_diagnostics_report_removal(
    config_root: str | os.PathLike[str],
) -> list[ReportRemovalPlan]:
    """Return the exact removable default diagnostics export, if present."""
    return _plan_owned_report_removal(
        config_root,
        DEFAULT_DIAGNOSTICS_REPORT_FILENAME,
        DEFAULT_DIAGNOSTICS_REPORT_RELATIVE_PATH,
    )


def plan_default_self_check_report_removal(
    config_root: str | os.PathLike[str],
) -> list[ReportRemovalPlan]:
    """Return the exact removable fixed self-check export, if present."""
    return _plan_owned_report_removal(
        config_root,
        DEFAULT_SELF_CHECK_REPORT_FILENAME,
        DEFAULT_SELF_CHECK_REPORT_RELATIVE_PATH,
    )


def _plan_owned_report_removal(
    config_root: str | os.PathLike[str],
    filename: str,
    relative_path: str,
) -> list[ReportRemovalPlan]:
    """Return an identity-bound removal plan for one exact owned report."""
    validate_owned_report_filename(filename)
    with _open_report_export_directory(config_root, create=False) as directory_fd:
        if directory_fd is None:
            return []
        metadata = _stat_regular_file(
            directory_fd,
            filename,
            allow_absent=True,
        )
        if metadata is None:
            return []
        directory_metadata = _fstat_directory(directory_fd)
    return [
        ReportRemovalPlan(
            relative_path=relative_path,
            directory_device=directory_metadata.st_dev,
            directory_inode=directory_metadata.st_ino,
            device=metadata.st_dev,
            inode=metadata.st_ino,
        )
    ]


def plan_owned_ui_export_removal(
    config_root: str | os.PathLike[str],
    filenames: Iterable[str],
) -> list[ReportRemovalPlan]:
    """Return identity-bound plans for exact generated UI files that exist."""
    candidates = sorted(dict.fromkeys(filenames))
    for filename in candidates:
        validate_owned_ui_filename(filename)
    with _open_ui_export_directory(config_root, create=False) as directory_fd:
        if directory_fd is None:
            return []
        directory_metadata = _fstat_directory(
            directory_fd,
            artifact_label="UI export",
        )
        plans: list[ReportRemovalPlan] = []
        for filename in candidates:
            metadata = _stat_regular_file(
                directory_fd,
                filename,
                allow_absent=True,
                artifact_label="UI export",
            )
            if metadata is None:
                continue
            plans.append(
                ReportRemovalPlan(
                    relative_path=f"{UI_EXPORT_RELATIVE_DIRECTORY}/{filename}",
                    directory_device=directory_metadata.st_dev,
                    directory_inode=directory_metadata.st_ino,
                    device=metadata.st_dev,
                    inode=metadata.st_ino,
                )
            )
    return plans


def remove_default_diagnostics_report(
    config_root: str | os.PathLike[str],
    plan: ReportRemovalPlan,
) -> bool:
    """Remove only the default diagnostics export after descriptor revalidation."""
    return _remove_owned_report(
        config_root,
        plan,
        filename=DEFAULT_DIAGNOSTICS_REPORT_FILENAME,
        relative_path=DEFAULT_DIAGNOSTICS_REPORT_RELATIVE_PATH,
    )


def remove_default_self_check_report(
    config_root: str | os.PathLike[str],
    plan: ReportRemovalPlan,
) -> bool:
    """Remove only the fixed self-check export after descriptor revalidation."""
    return _remove_owned_report(
        config_root,
        plan,
        filename=DEFAULT_SELF_CHECK_REPORT_FILENAME,
        relative_path=DEFAULT_SELF_CHECK_REPORT_RELATIVE_PATH,
    )


def remove_owned_ui_export(
    config_root: str | os.PathLike[str],
    plan: ReportRemovalPlan,
) -> bool:
    """Remove one exact planned generated UI export."""
    prefix = f"{UI_EXPORT_RELATIVE_DIRECTORY}/"
    if (
        not isinstance(plan, ReportRemovalPlan)
        or not plan.relative_path.startswith(prefix)
    ):
        raise ReportExportError("Invalid owned UI export removal plan")
    filename = plan.relative_path[len(prefix) :]
    validate_owned_ui_filename(filename)
    return _remove_owned_artifact(
        config_root,
        plan,
        filename=filename,
        relative_path=plan.relative_path,
        open_directory=_open_ui_export_directory,
        artifact_label="UI export",
    )


def _remove_owned_report(
    config_root: str | os.PathLike[str],
    plan: ReportRemovalPlan,
    *,
    filename: str,
    relative_path: str,
) -> bool:
    """Remove one exact planned owned report after descriptor revalidation."""
    return _remove_owned_artifact(
        config_root,
        plan,
        filename=filename,
        relative_path=relative_path,
        open_directory=_open_report_export_directory,
        artifact_label="report",
    )


def _remove_owned_artifact(
    config_root: str | os.PathLike[str],
    plan: ReportRemovalPlan,
    *,
    filename: str,
    relative_path: str,
    open_directory: Callable[..., ContextManager[int | None]],
    artifact_label: str,
) -> bool:
    """Remove one exact planned artifact after descriptor revalidation."""
    if (
        not isinstance(plan, ReportRemovalPlan)
        or plan.relative_path != relative_path
    ):
        raise ReportExportError(
            f"Invalid owned {artifact_label} removal plan: {relative_path}"
        )
    with _REPORT_OPERATION_LOCK:
        return _remove_owned_artifact_locked(
            config_root,
            plan,
            filename=filename,
            open_directory=open_directory,
            artifact_label=artifact_label,
        )


def _remove_owned_artifact_locked(
    config_root: str | os.PathLike[str],
    plan: ReportRemovalPlan,
    *,
    filename: str,
    open_directory: Callable[..., ContextManager[int | None]],
    artifact_label: str,
) -> bool:
    """Remove the planned artifact while excluding in-process writes."""
    with open_directory(config_root, create=False) as directory_fd:
        if directory_fd is None:
            return False
        directory_metadata = _fstat_directory(
            directory_fd,
            artifact_label=artifact_label,
        )
        if (
            directory_metadata.st_dev,
            directory_metadata.st_ino,
        ) != (
            plan.directory_device,
            plan.directory_inode,
        ):
            raise ReportExportError(
                f"Owned {artifact_label} directory changed after cleanup preview"
            )

        expected = _stat_regular_file(
            directory_fd,
            filename,
            allow_absent=True,
            artifact_label=artifact_label,
        )
        if expected is None:
            return False
        if (expected.st_dev, expected.st_ino) != (plan.device, plan.inode):
            raise ReportExportError(
                f"Owned {artifact_label} changed after cleanup preview: {filename}"
            )

        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
        try:
            report_fd = os.open(
                filename,
                flags,
                dir_fd=directory_fd,
            )
        except FileNotFoundError:
            return False
        except (NotImplementedError, OSError, TypeError) as err:
            raise ReportExportError(
                f"Unable to open owned {artifact_label} {filename!r} securely: "
                f"{err}"
            ) from err
        try:
            opened = os.fstat(report_fd)
            if not stat.S_ISREG(opened.st_mode):
                raise ReportExportError(
                    f"Owned {artifact_label} is no longer a regular file: {filename}"
                )
            if (opened.st_dev, opened.st_ino) != (plan.device, plan.inode):
                raise ReportExportError(
                    f"Owned {artifact_label} changed after cleanup preview: {filename}"
                )
            current = _stat_regular_file(
                directory_fd,
                filename,
                allow_absent=False,
                artifact_label=artifact_label,
            )
            if current is None or (
                current.st_dev,
                current.st_ino,
            ) != (
                plan.device,
                plan.inode,
            ):
                raise ReportExportError(
                    f"Owned {artifact_label} changed during cleanup: {filename}"
                )
            try:
                os.unlink(
                    filename,
                    dir_fd=directory_fd,
                )
                os.fsync(directory_fd)
            except (NotImplementedError, OSError, TypeError) as err:
                raise ReportExportError(
                    f"Unable to remove owned {artifact_label} {filename!r}: {err}"
                ) from err
            _verify_current_export_location(
                config_root,
                directory_fd,
                filename=filename,
                expected_file_identity=None,
                open_directory=open_directory,
                artifact_label=artifact_label,
            )
        finally:
            try:
                os.close(report_fd)
            except OSError:
                pass
    return True
