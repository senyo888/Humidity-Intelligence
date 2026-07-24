"""Cleanup helpers for Humidity Intelligence."""

from __future__ import annotations

import logging
import re
import stat
from pathlib import Path
from typing import Iterable, List

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)
_GENERATED_FILENAME_RE = re.compile(
    r"^humidity_intelligence_[A-Za-z0-9._-]+\.(?:json|yaml)$"
)


def _generated_file_path(hass: HomeAssistant, filename: str) -> Path:
    """Return a confined direct child path for one HI-owned generated file."""
    if (
        not isinstance(filename, str)
        or Path(filename).name != filename
        or not _GENERATED_FILENAME_RE.fullmatch(filename)
    ):
        raise ValueError(f"Invalid Humidity Intelligence cleanup target: {filename!r}")

    config_root = Path(hass.config.path()).resolve()
    path = Path(hass.config.path(filename))
    if path.parent.resolve() != config_root:
        raise ValueError(f"Cleanup target is outside the Home Assistant config root: {filename}")
    return path


def list_generated_files(entry: ConfigEntry) -> List[str]:
    """Return generated filenames (relative to /config) for an entry."""
    layouts = entry.data.get("ui_layouts") or []
    if not layouts:
        layouts = ["v2_mobile", "v2_tablet", "v1_mobile", "view_cards_button"]

    filenames = set()
    base = "humidity_intelligence_cards"
    for layout in layouts:
        filenames.add(f"{base}_{layout}.yaml")
        filenames.add(f"{base}_{entry.entry_id}_{layout}.yaml")
    # Legacy or single-file outputs
    filenames.add("humidity_intelligence_cards.json")
    filenames.add("humidity_intelligence_cards.yaml")
    # The root self-check remains entry-owned. Caller-selectable report exports use
    # the separately confined export-directory cleanup contract.
    filenames.add("humidity_intelligence_self_check.json")
    return sorted(filenames)


def list_all_generated_files(entries: Iterable[ConfigEntry]) -> List[str]:
    files = set()
    for entry in entries:
        for name in list_generated_files(entry):
            files.add(name)
    return sorted(files)


def plan_generated_file_removal(
    hass: HomeAssistant,
    filenames: Iterable[str],
) -> List[str]:
    """Validate all candidates and return existing regular files only."""
    candidates = list(dict.fromkeys(filenames))
    paths = [(name, _generated_file_path(hass, name)) for name in candidates]
    planned: List[str] = []
    for name, path in paths:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue
        except OSError as err:
            raise ValueError(f"Unable to inspect cleanup target {name}: {err}") from err
        if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
            raise ValueError(
                f"Cleanup target must be a regular non-symlink file: {name}"
            )
        planned.append(name)
    return planned


def remove_files(hass: HomeAssistant, filenames: Iterable[str]) -> List[str]:
    """Remove planned generated files and return any names that failed."""
    failed: List[str] = []
    for name in filenames:
        try:
            path = _generated_file_path(hass, name)
            metadata = path.lstat()
            if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
                raise OSError("target is not a regular non-symlink file")
            path.unlink()
        except FileNotFoundError:
            continue
        except (OSError, ValueError) as err:
            _LOGGER.warning("Unable to remove generated file %s: %s", name, err)
            failed.append(name)
    return failed


async def remove_dashboard(hass: HomeAssistant, dashboard_id: str | None) -> bool:
    """Remove a dashboard and report whether the requested deletion succeeded."""
    if not dashboard_id:
        return True
    try:
        from homeassistant.components.lovelace import dashboard as lovelace_dashboard
        await lovelace_dashboard.async_delete_dashboard(hass, dashboard_id=dashboard_id)
    except Exception:
        _LOGGER.exception("Unable to remove generated dashboard %s", dashboard_id)
        return False
    return True
