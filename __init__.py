"""Humidity Intelligence integration for Home Assistant."""

from __future__ import annotations

import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_AUTO_REFRESH_UI_ON_STARTUP,
    DEFAULT_AUTO_REFRESH_UI_ON_STARTUP,
    DOMAIN,
    STARTUP_UI_REFRESH_DELAY_SECONDS,
)
from .services import SERVICE_REFRESH_UI, async_register_services, async_unregister_services
from .helpers.cleanup import list_generated_files, remove_files, remove_dashboard
from .ui.register import async_register_cards, async_build_entity_mapping
from .automations import async_setup_entry as async_setup_automations
from .automations import async_unload_entry as async_unload_automations

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Humidity Intelligence integration via YAML."""
    if DOMAIN in config:
        _LOGGER.warning(
            "Configuration via YAML is deprecated for %s; please use the configuration UI.",
            DOMAIN,
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Humidity Intelligence from a config entry."""
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    effective_config = _effective_entry_config(entry)
    hass.data.setdefault(DOMAIN, {})
    entry_data = hass.data[DOMAIN].setdefault(entry.entry_id, {})
    entry_data.update({
        "config": effective_config,
        "options": entry.options,
    })

    await async_register_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "switch"])
    await async_setup_automations(hass, entry)

    # Prepare UI card YAML for this entry using entity mapping.
    try:
        mapping = await async_build_entity_mapping(hass, entry.entry_id)
        cards = await async_register_cards(hass, entry.entry_id, mapping=mapping)
    except Exception:
        _LOGGER.exception("Failed to build UI mapping/cards for entry %s", entry.entry_id)
        mapping = {}
        cards = {}
    hass.data[DOMAIN][entry.entry_id]["cards"] = cards
    hass.data[DOMAIN][entry.entry_id]["entity_map"] = mapping
    hass.async_create_task(_async_refresh_and_dump_cards(hass, entry.entry_id))
    _async_register_startup_ui_refresh(hass, entry)

    ui_layouts = entry.data.get("ui_layouts") or []
    if ui_layouts and not entry.data.get("ui_install_done"):
        await hass.services.async_call(
            DOMAIN,
            "dump_cards",
            {"entry_id": entry.entry_id},
            blocking=False,
        )
        dashboard_id = "humidity-intelligence"
        if "create_dashboard" in ui_layouts:
            await hass.services.async_call(
                DOMAIN,
                "create_dashboard",
                {
                    "entry_id": entry.entry_id,
                    "layout": "v2_mobile" if "v2_mobile" in ui_layouts else "v2_tablet",
                    "title": "Humidity Intelligence",
                    "url_path": dashboard_id,
                },
                blocking=False,
            )
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Humidity Intelligence UI Cards",
                "message": (
                    "Cards written to /config/humidity_intelligence_cards_<layout>.yaml. "
                    "Open File Editor, copy the YAML for your chosen layout(s), and paste into a Manual card."
                ),
            },
            blocking=False,
        )
        data = dict(entry.data)
        data["ui_install_done"] = True
        if "create_dashboard" in ui_layouts:
            data["ui_dashboard_id"] = dashboard_id
        hass.config_entries.async_update_entry(entry, data=data)
    _LOGGER.info("Humidity Intelligence v2 entry %s set up", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor", "switch"])
    await async_unload_automations(hass, entry)
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    if unsub := data.get("startup_ui_refresh_unsub"):
        unsub()
    data.pop("startup_ui_refresh_scheduled", None)
    task = data.pop("startup_ui_refresh_task", None)
    if isinstance(task, asyncio.Task):
        task.cancel()
    if unsub := data.get("core_unsub"):
        unsub()
    if unsub := data.get("slope_unsub"):
        unsub()
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    await async_unregister_services(hass)
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove config entry data and generated files."""
    files = list_generated_files(entry)
    dashboard_id = entry.data.get("ui_dashboard_id")
    message_lines = [f"/config/{f}" for f in files]
    if dashboard_id:
        message_lines.append(f"Dashboard: {dashboard_id}")
    await hass.services.async_call(
        "persistent_notification",
        "create",
        {
            "title": "Humidity Intelligence Cleanup",
            "message": "Removing generated files:\n" + "\n".join(message_lines),
        },
        blocking=False,
    )
    await hass.async_add_executor_job(remove_files, hass, files)
    await remove_dashboard(hass, dashboard_id)


async def _async_refresh_and_dump_cards(hass: HomeAssistant, entry_id: str) -> None:
    """Rebuild mapping and rewrite card files after startup."""
    try:
        await hass.services.async_call(
            DOMAIN,
            "refresh_ui",
            {"entry_id": entry_id},
            blocking=True,
        )
        await hass.services.async_call(
            DOMAIN,
            "dump_cards",
            {"entry_id": entry_id},
            blocking=True,
        )
    except Exception:
        _LOGGER.exception(
            "Failed startup refresh/dump for Humidity Intelligence entry %s",
            entry_id,
        )


def _async_register_startup_ui_refresh(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Refresh HI UI mapping once Home Assistant has finished startup."""
    if not _entry_auto_refresh_ui_on_startup(entry):
        _LOGGER.debug(
            "HI entry %s startup UI refresh skipped: option disabled.",
            entry.entry_id,
        )
        return

    if _hass_already_started(hass):
        _LOGGER.debug(
            "HI entry %s startup UI refresh skipped: Home Assistant is already running.",
            entry.entry_id,
        )
        return

    data = hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    if data.get("startup_ui_refresh_unsub") or data.get("startup_ui_refresh_scheduled"):
        _LOGGER.debug(
            "HI entry %s startup UI refresh skipped: listener/task already exists.",
            entry.entry_id,
        )
        return

    @callback
    def _handle_started(_event) -> None:
        data.pop("startup_ui_refresh_unsub", None)
        data["startup_ui_refresh_scheduled"] = True

        async def _run_startup_ui_refresh() -> None:
            try:
                await _async_delayed_startup_ui_refresh(hass, entry.entry_id)
            finally:
                data.pop("startup_ui_refresh_scheduled", None)
                data.pop("startup_ui_refresh_task", None)

        # EVENT_HOMEASSISTANT_STARTED can be fired from outside the event-loop
        # thread during startup; create_task may return None on some HA builds.
        task = hass.create_task(_run_startup_ui_refresh())
        if isinstance(task, asyncio.Task):
            data["startup_ui_refresh_task"] = task
        _LOGGER.debug(
            "HI entry %s startup UI refresh scheduled after Home Assistant started.",
            entry.entry_id,
        )

    data["startup_ui_refresh_unsub"] = hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STARTED,
        _handle_started,
    )
    _LOGGER.debug(
        "HI entry %s startup UI refresh listener registered.",
        entry.entry_id,
    )


async def _async_delayed_startup_ui_refresh(hass: HomeAssistant, entry_id: str) -> None:
    """Run the startup UI refresh after a short availability delay."""
    try:
        await asyncio.sleep(STARTUP_UI_REFRESH_DELAY_SECONDS)
        if entry_id not in hass.data.get(DOMAIN, {}):
            _LOGGER.debug(
                "HI entry %s startup UI refresh skipped: integration data is no longer loaded.",
                entry_id,
            )
            return
        if not hass.config_entries.async_get_entry(entry_id):
            _LOGGER.debug(
                "HI entry %s startup UI refresh skipped: config entry is no longer loaded.",
                entry_id,
            )
            return

        await hass.services.async_call(
            DOMAIN,
            SERVICE_REFRESH_UI,
            {"entry_id": entry_id},
            blocking=True,
        )
        _LOGGER.debug("HI entry %s startup UI refresh completed.", entry_id)
    except asyncio.CancelledError:
        _LOGGER.debug("HI entry %s startup UI refresh cancelled.", entry_id)
        raise
    except Exception:
        _LOGGER.exception("HI entry %s startup UI refresh failed.", entry_id)


def _entry_auto_refresh_ui_on_startup(entry: ConfigEntry) -> bool:
    """Resolve startup UI refresh option with a default-on fallback."""
    return bool(
        _effective_entry_config(entry).get(
            CONF_AUTO_REFRESH_UI_ON_STARTUP,
            DEFAULT_AUTO_REFRESH_UI_ON_STARTUP,
        )
    )


def _hass_already_started(hass: HomeAssistant) -> bool:
    """Return true when setup is running after the startup event has passed."""
    state = getattr(hass, "state", None)
    return state == "running" or getattr(state, "value", None) == "running"


def _effective_entry_config(entry: ConfigEntry) -> dict:
    config = dict(entry.data or {})
    options = dict(entry.options or {})
    config.update(options)
    return config


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change so runtime lanes immediately honor updates."""
    previous_cfg = (
        hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("config", {}) or {}
    )
    prev_alert_only = bool(previous_cfg.get("alert_only_mode", _entry_alert_only_mode(entry)))
    next_alert_only = _entry_alert_only_mode(entry)
    await hass.config_entries.async_reload(entry.entry_id)
    if prev_alert_only == next_alert_only:
        return

    _LOGGER.info(
        "HI entry %s alert-only mode changed to %s; regenerating UI card exports.",
        entry.entry_id,
        next_alert_only,
    )
    await _async_refresh_and_dump_cards(hass, entry.entry_id)
    await hass.services.async_call(
        "persistent_notification",
        "create",
        {
            "title": "Humidity Intelligence UI Updated",
            "message": (
                "Alert-only mode changed. Updated card files were written to "
                "/config/humidity_intelligence_cards_<layout>.yaml. "
                "Re-copy/paste the layout YAML into your Manual card to apply control visibility changes."
            ),
        },
        blocking=False,
    )


def _entry_alert_only_mode(entry: ConfigEntry) -> bool:
    options = getattr(entry, "options", None) or {}
    if "alert_only_mode" in options:
        return bool(options.get("alert_only_mode"))
    data = getattr(entry, "data", None) or {}
    return bool(data.get("alert_only_mode", False))
