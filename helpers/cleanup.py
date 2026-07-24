"""Cleanup helpers for Humidity Intelligence."""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Iterable, List

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)
_GENERATED_UI_LAYOUTS = (
    "v1_mobile",
    "v2_mobile",
    "v2_tablet",
    "view_cards_button",
)


def safe_artifact_entry_slug(value: str) -> str:
    """Return a deterministic collision-resistant filename token for an entry."""
    text = str(value or "entry")
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", text)[:48] or "entry"
    if safe == text and len(text) <= 48:
        return safe

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{safe}_{digest}"


def build_generated_card_filename(
    base: str | None,
    layout: str,
    entry_id: str,
    multiple: bool,
) -> str:
    """Build one stable generated-card basename."""
    prefix = base or "humidity_intelligence_cards"
    if prefix.endswith(".yaml"):
        prefix = prefix[:-5]
    if prefix.endswith(".yml"):
        prefix = prefix[:-4]
    if multiple:
        return f"{prefix}_{safe_artifact_entry_slug(entry_id)}_{layout}.yaml"
    return f"{prefix}_{layout}.yaml"


def list_owned_ui_filenames(
    entries: Iterable[ConfigEntry],
    *,
    multiple_installation: bool,
    include_unqualified_defaults: bool,
) -> List[str]:
    """Return the exact default and release-test UI basenames owned by entries."""
    entries = list(entries)
    filenames = set()
    if include_unqualified_defaults:
        for layout in _GENERATED_UI_LAYOUTS:
            filenames.add(
                build_generated_card_filename(
                    None,
                    layout,
                    "",
                    False,
                )
            )
        release_base = "humidity_intelligence_v205_release_check_cards"
        for layout in _GENERATED_UI_LAYOUTS:
            filenames.add(
                build_generated_card_filename(
                    release_base,
                    layout,
                    "",
                    False,
                )
            )
        filenames.add(
            build_generated_card_filename(
                f"{release_base}_scoped",
                "v2_tablet",
                "",
                False,
            )
        )
    for entry in entries:
        entry_id = str(entry.entry_id)
        naming_modes = {multiple_installation}
        if not multiple_installation:
            naming_modes.add(True)
        for naming_mode in naming_modes:
            for layout in _GENERATED_UI_LAYOUTS:
                filenames.add(
                    build_generated_card_filename(
                        None,
                        layout,
                        entry_id,
                        naming_mode,
                    )
                )

            release_base = "humidity_intelligence_v205_release_check_cards"
            for layout in _GENERATED_UI_LAYOUTS:
                filenames.add(
                    build_generated_card_filename(
                        release_base,
                        layout,
                        entry_id,
                        naming_mode,
                    )
                )
            filenames.add(
                build_generated_card_filename(
                    f"{release_base}_scoped",
                    "v2_tablet",
                    entry_id,
                    naming_mode,
                )
            )
    return sorted(filenames)


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
