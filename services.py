"""Service handlers for Humidity Intelligence."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import tempfile
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import CONF_SHOW_OUTPUT_ENTITY_DETAILS, DEFAULT_SHOW_OUTPUT_ENTITY_DETAILS, DOMAIN
from .helpers.cleanup import list_all_generated_files, list_generated_files, remove_files, remove_dashboard
from .helpers.drift import humidity_drift_dependency_status, humidity_drift_warning
from .helpers.frontend_dependencies import (
    async_frontend_dependency_status,
    frontend_dependency_not_inspectable,
)
from .helpers.seasonal import resolve_target_profile
from .helpers.zone_validation import detect_zone_mapping_duplicates, summarize_zone_mapping_duplicates

_LOGGER = logging.getLogger(__name__)

SERVICE_FLASH_LIGHTS = "flash_lights"
SERVICE_REFRESH_UI = "refresh_ui"
SERVICE_DUMP_DIAGNOSTICS = "dump_diagnostics"
SERVICE_SELF_CHECK = "self_check"
SERVICE_V205_RELEASE_CHECK = "v205_release_check"
SERVICE_DUMP_CARDS = "dump_cards"
SERVICE_CREATE_DASHBOARD = "create_dashboard"
SERVICE_VIEW_CARDS = "view_cards"
SERVICE_PURGE_FILES = "purge_files"
SERVICE_PAUSE_CONTROL = "pause_control"
SERVICE_RESUME_CONTROL = "resume_control"
_FLASH_LIGHT_LOCKS_KEY = "_flash_light_locks"

_ALLOWED_LAYOUTS = {"v2_mobile", "v2_tablet", "v1_mobile", "view_cards_button"}
_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_SAFE_DASHBOARD_PATH_RE = re.compile(r"^[a-z0-9_-]{1,64}$")
_V205_RELEASE_CHECK_COMPATIBLE_VERSION_RE = re.compile(
    r"^2\.0\.(?:5|6(?:-(?:beta|rc)\.[1-9]\d*)?)$"
)
_SENSITIVE_ATTR_EXACT = {
    "access_token",
    "token",
    "refresh_token",
    "password",
    "api_key",
    "authorization",
    "latitude",
    "longitude",
    "gps_accuracy",
    "address",
    "email",
    "phone",
    "device_id",
    "unique_id",
    "mac",
    "ssid",
    "ip",
}
_SENSITIVE_ATTR_PARTIAL = (
    "token",
    "secret",
    "password",
    "api_key",
    "apikey",
    "access_key",
    "authorization",
    "bearer",
    "latitude",
    "longitude",
    "gps_",
    "address",
    "email",
    "phone",
    "device_id",
    "unique_id",
    "mac_",
    "_mac",
    "ssid",
    "ip_address",
)


def _validate_layout(value: str) -> str:
    text = str(value).strip()
    if text not in _ALLOWED_LAYOUTS:
        raise vol.Invalid(
            f"Unsupported layout '{text}'. Allowed: {', '.join(sorted(_ALLOWED_LAYOUTS))}"
        )
    return text


def _validate_safe_filename(value: str) -> str:
    text = str(value).strip()
    if not text:
        raise vol.Invalid("Filename cannot be empty")
    if "/" in text or "\\" in text or ".." in text:
        raise vol.Invalid("Filename must not include directory traversal or separators")
    if not _SAFE_FILENAME_RE.fullmatch(text):
        raise vol.Invalid("Filename contains invalid characters")
    return text


def _validate_dashboard_url_path(value: str) -> str:
    text = str(value).strip().lower()
    if not _SAFE_DASHBOARD_PATH_RE.fullmatch(text):
        raise vol.Invalid(
            "Dashboard URL path must use only lowercase letters, numbers, '_' or '-'"
        )
    return text


def _validate_rgb_color(value) -> List[int]:
    """Accept service/YAML RGB colors and normalize them to a plain list."""
    if isinstance(value, tuple):
        values = list(value)
    else:
        values = cv.ensure_list(value)
    values = [vol.Coerce(int)(item) for item in values]
    if len(values) < 3:
        raise vol.Invalid("RGB color must include red, green, and blue values")
    for item in values[:3]:
        if item < 0 or item > 255:
            raise vol.Invalid("RGB color values must be between 0 and 255")
    return values[:3]


def _validate_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "on", "1"}:
            return True
        if lowered in {"false", "no", "off", "0"}:
            return False
    raise vol.Invalid("Expected a boolean value")


SERVICE_FLASH_SCHEMA = vol.Schema({
    vol.Optional("power_entity"): cv.entity_id,
    vol.Optional("lights", default=[]): cv.entity_ids,
    vol.Optional("color", default=[255, 0, 0]): _validate_rgb_color,
    vol.Optional("duration", default=10): vol.All(vol.Coerce(int), vol.Range(min=1, max=300)),
    vol.Optional("flash_count", default=None): vol.Any(
        None,
        vol.All(vol.Coerce(int), vol.Range(min=1, max=240)),
    ),
})
SERVICE_REFRESH_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
})
SERVICE_DUMP_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
    vol.Optional("filename", default="humidity_intelligence_diagnostics.json"): _validate_safe_filename,
})
SERVICE_SELF_CHECK_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
})
SERVICE_V205_RELEASE_CHECK_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
    vol.Optional("filename", default="humidity_intelligence_v205_release_check.json"): _validate_safe_filename,
    vol.Optional("write_test_exports", default=False): _validate_bool,
})
SERVICE_DUMP_CARDS_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
    vol.Optional("filename"): _validate_safe_filename,
    vol.Optional("layout"): _validate_layout,
})
SERVICE_CREATE_DASHBOARD_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
    vol.Optional("layout", default="v2_mobile"): _validate_layout,
    vol.Optional("title", default="Humidity Intelligence"): cv.string,
    vol.Optional("url_path", default="humidity-intelligence"): _validate_dashboard_url_path,
})
SERVICE_VIEW_CARDS_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
    vol.Optional("filename"): _validate_safe_filename,
    vol.Optional("layout"): _validate_layout,
})
SERVICE_PURGE_FILES_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
})
SERVICE_PAUSE_CONTROL_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
    vol.Optional("minutes", default=60): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
})
SERVICE_RESUME_CONTROL_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
})


async def async_register_services(hass: HomeAssistant) -> None:
    """Register services for the integration."""

    async def handle_flash(call: ServiceCall) -> None:
        power_entity = call.data.get("power_entity")
        lights = _dedupe_lights(call.data.get("lights") or [])
        color_list = call.data.get("color") or [255, 0, 0]
        duration = max(1, int(call.data.get("duration", 10)))
        flash_count = call.data.get("flash_count")
        color = tuple(color_list[:3]) if len(color_list) >= 3 else (255, 0, 0)

        if not lights:
            _LOGGER.debug("No lights provided to flash_lights; skipping light flash.")
            return

        locks = _light_flash_locks(hass, lights)
        acquired_locks: List[asyncio.Lock] = []
        try:
            for lock in locks:
                await lock.acquire()
                acquired_locks.append(lock)

            initial_states = _capture_light_states(hass, lights)

            if power_entity:
                domain = power_entity.split(".")[0]
                if hass.services.has_service(domain, "turn_on"):
                    try:
                        await hass.services.async_call(domain, "turn_on", {"entity_id": power_entity}, blocking=True)
                        await asyncio.sleep(0.5)
                    except Exception:
                        _LOGGER.exception("Failed to turn on alert power entity %s", power_entity)

            supports_color = {light: _supports_color(hass.states.get(light)) for light in lights}

            await _flash_lights(hass, lights, color, duration, flash_count, supports_color)
            await _restore_lights(hass, initial_states)
        finally:
            for lock in reversed(acquired_locks):
                try:
                    lock.release()
                except RuntimeError:
                    continue

    hass.services.async_register(DOMAIN, SERVICE_FLASH_LIGHTS, handle_flash, schema=SERVICE_FLASH_SCHEMA)

    async def handle_refresh(call: ServiceCall) -> None:
        from .ui.register import async_build_entity_mapping, async_register_cards

        entry_id = call.data.get("entry_id")
        entries = []
        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry:
                entries = [entry]
        else:
            entries = hass.config_entries.async_entries(DOMAIN)

        for entry in entries:
            mapping = await async_build_entity_mapping(hass, entry.entry_id)
            cards = await async_register_cards(hass, entry.entry_id, mapping=mapping)
            hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
            hass.data[DOMAIN][entry.entry_id]["entity_map"] = mapping
            hass.data[DOMAIN][entry.entry_id]["cards"] = cards

    hass.services.async_register(DOMAIN, SERVICE_REFRESH_UI, handle_refresh, schema=SERVICE_REFRESH_SCHEMA)

    async def handle_dump(call: ServiceCall) -> None:
        try:
            entry_id = call.data.get("entry_id")
            filename = call.data.get("filename", "humidity_intelligence_diagnostics.json")
            entries = []
            if entry_id:
                entry = hass.config_entries.async_get_entry(entry_id)
                if entry:
                    entries = [entry]
            else:
                entries = hass.config_entries.async_entries(DOMAIN)

            frontend_dependencies = await async_frontend_dependency_status(hass)
            payload = {}
            for entry in entries:
                data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
                entity_map = data.get("entity_map", {})
                state_dump = {}
                for ent in entity_map.values():
                    state = hass.states.get(ent)
                    if state is None:
                        continue
                    state_dump[ent] = {
                        "state": state.state,
                        "attributes": _redact_sensitive_attributes(dict(state.attributes)),
                    }
                payload[entry.entry_id] = {
                    "config": _to_jsonable(data.get("config", {})),
                    "options": _to_jsonable(data.get("options", {})),
                    "diagnostics_summary": _build_diagnostics_summary(
                        hass,
                        data.get("config", {}),
                        data.get("options", {}),
                        entity_map,
                        data,
                        frontend_dependencies=frontend_dependencies,
                    ),
                    "entity_map": _to_jsonable(entity_map),
                    "cards": list((data.get("cards") or {}).keys()),
                    "states": state_dump,
                }

            path = hass.config.path(filename)
            await hass.async_add_executor_job(_write_json, path, payload)
        except Exception as err:
            _LOGGER.exception("Failed to write diagnostics JSON")
            raise HomeAssistantError(f"Failed to write diagnostics JSON: {err}") from err

    hass.services.async_register(DOMAIN, SERVICE_DUMP_DIAGNOSTICS, handle_dump, schema=SERVICE_DUMP_SCHEMA)

    async def handle_self_check(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        entries = []
        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry:
                entries = [entry]
        else:
            entries = hass.config_entries.async_entries(DOMAIN)

        report = {}
        for entry in entries:
            data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
            mapping = data.get("entity_map", {})
            missing_entities = []
            for ent in mapping.values():
                if hass.states.get(ent) is None:
                    missing_entities.append(ent)
            frontend_dependencies = await async_frontend_dependency_status(hass)
            drift_dependency = humidity_drift_dependency_status(hass)

            report[entry.entry_id] = {
                "missing_entities": missing_entities,
                "frontend_dependency_resources": frontend_dependencies,
                "humidity_drift_7d": drift_dependency,
                "telemetry_count": len(entry.data.get("telemetry", [])),
                "unresolved_placeholders": data.get("unresolved_placeholders", []),
                "unresolved_placeholders_by_card": data.get("unresolved_placeholders_by_card", {}),
            }

        path = hass.config.path("humidity_intelligence_self_check.json")
        await hass.async_add_executor_job(_write_json, path, report)

    hass.services.async_register(DOMAIN, SERVICE_SELF_CHECK, handle_self_check, schema=SERVICE_SELF_CHECK_SCHEMA)

    async def handle_v205_release_check(call: ServiceCall) -> None:
        from .ui.register import async_build_entity_mapping, async_register_cards

        entry_id = call.data.get("entry_id")
        filename = call.data.get("filename", "humidity_intelligence_v205_release_check.json")
        write_test_exports = bool(call.data.get("write_test_exports", False))
        entries = []
        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry:
                entries = [entry]
        else:
            entries = hass.config_entries.async_entries(DOMAIN)

        manifest_version = await _async_read_manifest_version(hass)
        report: Dict[str, Any] = {
            "check": SERVICE_V205_RELEASE_CHECK,
            "status": "pass",
            "entries": {},
        }
        frontend_dependencies = await async_frontend_dependency_status(hass)

        if not entries:
            report["status"] = "fail"
            report["entries"] = {}
            report["checks"] = [
                {
                    "id": "config_entry",
                    "status": "fail",
                    "message": "No Humidity Intelligence config entry was found.",
                }
            ]
        else:
            entry_reports = []
            for entry in entries:
                mapping = await async_build_entity_mapping(hass, entry.entry_id)
                cards = await async_register_cards(hass, entry.entry_id, mapping=mapping)
                domain_data = hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
                domain_data["entity_map"] = mapping
                domain_data["cards"] = cards

                unscoped_written: List[str] = []
                scoped_written: List[str] = []
                if write_test_exports:
                    slug = _safe_report_slug(entry.entry_id)
                    base = f"humidity_intelligence_v205_release_check_cards_{slug}" if len(entries) > 1 else "humidity_intelligence_v205_release_check_cards"
                    scoped_base = f"{base}_scoped"
                    unscoped_written = await _dump_cards_to_file(hass, entry.entry_id, base, layout=None)
                    scoped_written = await _dump_cards_to_file(hass, entry.entry_id, scoped_base, layout="v2_tablet")

                entry_report = _build_v205_release_check_entry_report(
                    hass,
                    entry,
                    domain_data,
                    manifest_version=manifest_version,
                    frontend_dependencies=frontend_dependencies,
                    write_test_exports=write_test_exports,
                    unscoped_written=unscoped_written,
                    scoped_written=scoped_written,
                )
                report["entries"][entry.entry_id] = entry_report
                entry_reports.append(entry_report)

            report["status"] = _combined_check_status(entry_reports)

        path = hass.config.path(filename)
        await hass.async_add_executor_job(_write_json, path, report)
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Humidity Intelligence v2.0.5 Release Check",
                "message": f"{report['status'].upper()}: report written to /config/{filename}",
            },
            blocking=False,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_V205_RELEASE_CHECK,
        handle_v205_release_check,
        schema=SERVICE_V205_RELEASE_CHECK_SCHEMA,
    )

    async def handle_dump_cards(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        filename = call.data.get("filename")
        layout = call.data.get("layout")
        await _dump_cards_to_file(hass, entry_id, filename, layout=layout)

    hass.services.async_register(DOMAIN, SERVICE_DUMP_CARDS, handle_dump_cards, schema=SERVICE_DUMP_CARDS_SCHEMA)

    async def handle_create_dashboard(call: ServiceCall) -> None:
        from .ui.register import async_build_entity_mapping, async_register_cards
        from homeassistant.components.lovelace import dashboard as lovelace_dashboard

        entry_id = call.data.get("entry_id")
        layout = call.data.get("layout", "v2_mobile")
        title = call.data.get("title", "Humidity Intelligence")
        url_path = call.data.get("url_path", "humidity-intelligence")

        entry = None
        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None:
            entries = hass.config_entries.async_entries(DOMAIN)
            entry = entries[0] if entries else None
        if entry is None:
            return

        mapping = await async_build_entity_mapping(hass, entry.entry_id)
        cards = await async_register_cards(hass, entry.entry_id, mapping=mapping)
        yaml_str = cards.get(layout)
        if not yaml_str:
            return

        filename = f"dashboards/{url_path}.yaml"
        path = hass.config.path(filename)
        await hass.async_add_executor_job(_write_text, path, yaml_str)

        # Best-effort dashboard creation; if HA API changes, this will no-op.
        try:
            await lovelace_dashboard.async_create_dashboard(
                hass,
                dashboard_id=url_path,
                title=title,
                mode="yaml",
                filename=filename,
                icon="mdi:water-percent",
                show_in_sidebar=True,
                require_admin=False,
            )
        except Exception:
            _LOGGER.exception("Unable to auto-create dashboard. YAML written to %s", filename)

    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_DASHBOARD,
        handle_create_dashboard,
        schema=SERVICE_CREATE_DASHBOARD_SCHEMA,
    )

    async def handle_view_cards(call: ServiceCall) -> None:
        filename = call.data.get("filename")
        layout = call.data.get("layout")
        written = await _dump_cards_to_file(hass, call.data.get("entry_id"), filename, layout=layout)
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Humidity Intelligence Cards",
                "message": _format_cards_message(written),
            },
            blocking=False,
        )

    hass.services.async_register(DOMAIN, SERVICE_VIEW_CARDS, handle_view_cards, schema=SERVICE_VIEW_CARDS_SCHEMA)

    async def handle_purge_files(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        entries = []
        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry:
                entries = [entry]
        else:
            entries = hass.config_entries.async_entries(DOMAIN)

        if not entries:
            return

        files = list_all_generated_files(entries)
        dashboards = [e.data.get("ui_dashboard_id") for e in entries if e.data.get("ui_dashboard_id")]
        message_lines = [f"/config/{f}" for f in files]
        for dash in dashboards:
            message_lines.append(f"Dashboard: {dash}")
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Humidity Intelligence Cleanup",
                "message": "Purging generated files:\n" + "\n".join(message_lines),
            },
            blocking=False,
        )
        await hass.async_add_executor_job(remove_files, hass, files)
        for entry in entries:
            await remove_dashboard(hass, entry.data.get("ui_dashboard_id"))

    hass.services.async_register(DOMAIN, SERVICE_PURGE_FILES, handle_purge_files, schema=SERVICE_PURGE_FILES_SCHEMA)

    async def handle_pause_control(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        minutes = int(call.data.get("minutes", 60))
        entries = []
        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry:
                entries = [entry]
        else:
            entries = hass.config_entries.async_entries(DOMAIN)

        if not entries:
            raise HomeAssistantError("No Humidity Intelligence config entry found")

        for entry in entries:
            data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
            timer = (data.get("hi_timers") or {}).get("air_control_pause")
            if timer is None:
                raise HomeAssistantError("Pause timer is not available yet")
            await timer.async_start(timedelta(minutes=minutes))
            engine = data.get("automation_engine")
            if engine:
                await engine.async_request_evaluate()

    hass.services.async_register(
        DOMAIN,
        SERVICE_PAUSE_CONTROL,
        handle_pause_control,
        schema=SERVICE_PAUSE_CONTROL_SCHEMA,
    )

    async def handle_resume_control(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        entries = []
        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry:
                entries = [entry]
        else:
            entries = hass.config_entries.async_entries(DOMAIN)

        if not entries:
            raise HomeAssistantError("No Humidity Intelligence config entry found")

        for entry in entries:
            data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
            timer = (data.get("hi_timers") or {}).get("air_control_pause")
            if timer is None:
                raise HomeAssistantError("Pause timer is not available yet")
            await timer.async_cancel()
            engine = data.get("automation_engine")
            if engine:
                await engine.async_request_evaluate()

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESUME_CONTROL,
        handle_resume_control,
        schema=SERVICE_RESUME_CONTROL_SCHEMA,
    )


async def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister services for the integration."""
    if hass.services.has_service(DOMAIN, SERVICE_FLASH_LIGHTS):
        hass.services.async_remove(DOMAIN, SERVICE_FLASH_LIGHTS)
    if hass.services.has_service(DOMAIN, SERVICE_REFRESH_UI):
        hass.services.async_remove(DOMAIN, SERVICE_REFRESH_UI)
    if hass.services.has_service(DOMAIN, SERVICE_DUMP_DIAGNOSTICS):
        hass.services.async_remove(DOMAIN, SERVICE_DUMP_DIAGNOSTICS)
    if hass.services.has_service(DOMAIN, SERVICE_SELF_CHECK):
        hass.services.async_remove(DOMAIN, SERVICE_SELF_CHECK)
    if hass.services.has_service(DOMAIN, SERVICE_V205_RELEASE_CHECK):
        hass.services.async_remove(DOMAIN, SERVICE_V205_RELEASE_CHECK)
    if hass.services.has_service(DOMAIN, SERVICE_DUMP_CARDS):
        hass.services.async_remove(DOMAIN, SERVICE_DUMP_CARDS)
    if hass.services.has_service(DOMAIN, SERVICE_CREATE_DASHBOARD):
        hass.services.async_remove(DOMAIN, SERVICE_CREATE_DASHBOARD)
    if hass.services.has_service(DOMAIN, SERVICE_VIEW_CARDS):
        hass.services.async_remove(DOMAIN, SERVICE_VIEW_CARDS)
    if hass.services.has_service(DOMAIN, SERVICE_PURGE_FILES):
        hass.services.async_remove(DOMAIN, SERVICE_PURGE_FILES)
    if hass.services.has_service(DOMAIN, SERVICE_PAUSE_CONTROL):
        hass.services.async_remove(DOMAIN, SERVICE_PAUSE_CONTROL)
    if hass.services.has_service(DOMAIN, SERVICE_RESUME_CONTROL):
        hass.services.async_remove(DOMAIN, SERVICE_RESUME_CONTROL)


def _write_json(path: str, payload: dict) -> None:
    import json

    tmp_dir = os.path.dirname(path) or "."
    os.makedirs(tmp_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".hi_diag_", suffix=".json", dir=tmp_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _write_text(path: str, payload: str) -> None:
    from pathlib import Path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(payload)


async def _async_read_manifest_version(hass: HomeAssistant) -> Optional[str]:
    def _read_version() -> Optional[str]:
        path = os.path.join(os.path.dirname(__file__), "manifest.json")
        with open(path, "r", encoding="utf-8") as manifest:
            data = json.load(manifest)
        version = data.get("version")
        return str(version) if version is not None else None

    try:
        return await hass.async_add_executor_job(_read_version)
    except Exception:
        _LOGGER.exception("Unable to read Humidity Intelligence manifest version")
        return None


def _to_jsonable(value):
    """Convert HA/runtime objects into JSON-serializable primitives."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if hasattr(value, "items"):
        try:
            return {str(k): _to_jsonable(v) for k, v in value.items()}
        except (AttributeError, TypeError, ValueError):
            pass
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except (AttributeError, TypeError, ValueError):
            pass
    return str(value)


def _redact_sensitive_attributes(attributes: dict) -> dict:
    redacted = {}
    for key, value in attributes.items():
        key_text = str(key)
        key_norm = key_text.lower()
        if key_norm in _SENSITIVE_ATTR_EXACT or any(part in key_norm for part in _SENSITIVE_ATTR_PARTIAL):
            redacted[key_text] = "[REDACTED]"
        else:
            redacted[key_text] = _to_jsonable(value)
    return redacted


def _build_diagnostics_summary(
    hass: HomeAssistant,
    config: dict,
    options: dict,
    entity_map: dict,
    runtime_data: dict,
    *,
    frontend_dependencies: Optional[dict] = None,
) -> dict:
    """Build a support-focused, truth-only diagnostics summary."""
    effective = dict(config or {})
    effective.update(dict(options or {}))
    telemetry = effective.get("telemetry", []) if isinstance(effective, dict) else []
    zones = effective.get("zones", {}) if isinstance(effective, dict) else {}
    alerts = effective.get("alerts", []) if isinstance(effective, dict) else []
    profile = resolve_target_profile(effective)
    duplicates = detect_zone_mapping_duplicates(telemetry, zones if isinstance(zones, dict) else {})
    unavailable = _unavailable_configured_entities(hass, effective, entity_map)
    drift_dependency = humidity_drift_dependency_status(hass)
    drift_dependency_warning = humidity_drift_warning(drift_dependency)
    warnings = []
    duplicate_summary = summarize_zone_mapping_duplicates(duplicates)
    if duplicate_summary:
        warnings.append(duplicate_summary)
    if unavailable:
        warnings.append(f"{len(unavailable)} configured/mapped entity references are missing, unknown, or unavailable.")
    if drift_dependency_warning:
        warnings.append(drift_dependency_warning)
    if not telemetry:
        warnings.append("No telemetry sensors are configured.")
    if not zones and not effective.get("alert_only_mode"):
        warnings.append("No control zones are configured.")

    summary = {
        "target_profile": {
            "mode": effective.get("target_profile", "auto"),
            "active_profile": profile.key,
            "active_season": profile.label,
            "target_low": profile.low,
            "target_high": profile.high,
            "high_risk": profile.high_risk,
            "custom_target_low": effective.get("custom_target_low"),
            "custom_target_high": effective.get("custom_target_high"),
        },
        "temperature_comfort": {
            "mode": effective.get("temperature_comfort_mode", "auto"),
            "custom_low": effective.get("temperature_comfort_custom_low"),
            "custom_high": effective.get("temperature_comfort_custom_high"),
        },
        "zone_mappings": _zone_mapping_summary(zones),
        "zone_mapping_duplicates": duplicates,
        "alert_mappings": _alert_mapping_summary(alerts),
        "active_alert_resolution": runtime_data.get("alert_telemetry", []),
        "visual_alerts": _visual_alert_summary(alerts),
        "humidity_drift_7d": drift_dependency,
        "unavailable_or_unknown_entities": unavailable,
        "warnings": warnings,
    }
    if frontend_dependencies is not None:
        summary["frontend_dependency_resources"] = frontend_dependencies

    return _to_jsonable(summary)


def _build_v205_release_check_entry_report(
    hass: HomeAssistant,
    entry: Any,
    runtime_data: dict,
    *,
    manifest_version: Optional[str],
    frontend_dependencies: Optional[dict] = None,
    write_test_exports: bool = False,
    unscoped_written: Optional[List[str]] = None,
    scoped_written: Optional[List[str]] = None,
) -> dict:
    """Build a truth-only v2.0.5 release-validation report for one entry."""
    cards = runtime_data.get("cards", {}) or {}
    entity_map = runtime_data.get("entity_map", {}) or {}
    effective = _effective_entry_config(entry)
    checks: List[Dict[str, Any]] = []
    manifest_status, manifest_message = _v205_release_check_manifest_status(manifest_version)

    _add_check(
        checks,
        "manifest_version",
        manifest_status,
        manifest_message,
    )

    show_output_details = bool(
        effective.get(CONF_SHOW_OUTPUT_ENTITY_DETAILS, DEFAULT_SHOW_OUTPUT_ENTITY_DETAILS)
    )
    _add_check(
        checks,
        "show_output_entity_details_option",
        "pass",
        "show_output_entity_details resolved as a generated-card visibility option.",
        {
            "configured": CONF_SHOW_OUTPUT_ENTITY_DETAILS in effective,
            "resolved_value": show_output_details,
        },
    )

    required_layouts = {"v2_mobile", "v2_tablet", "v1_mobile", "view_cards_button"}
    cached_layouts = set(cards)
    missing_layouts = sorted(required_layouts - cached_layouts)
    _add_check(
        checks,
        "cached_layouts",
        "pass" if not missing_layouts else "fail",
        "All expected generated card layouts are cached." if not missing_layouts else "Generated card layout cache is incomplete.",
        {"cached_layouts": sorted(cached_layouts), "missing_layouts": missing_layouts},
    )

    visibility_failures = _output_details_visibility_failures(cards, show_output_details)
    _add_check(
        checks,
        "output_details_visibility",
        "pass" if not visibility_failures else "fail",
        "Generated V2 output details visibility matches show_output_entity_details.",
        {"show_output_entity_details": show_output_details, "failures": visibility_failures},
    )

    unresolved = runtime_data.get("unresolved_placeholders_by_card") or {}
    if not unresolved:
        unresolved = runtime_data.get("unresolved_placeholders") or []
    _add_check(
        checks,
        "unresolved_placeholders",
        "pass" if not unresolved else "fail",
        "No unresolved placeholders are recorded for generated cards." if not unresolved else "Generated cards have unresolved placeholders.",
        {"unresolved": unresolved},
    )

    card_sanity_failures = _generated_card_text_sanity_failures(cards)
    _add_check(
        checks,
        "generated_cards_text_sanity",
        "pass" if not card_sanity_failures else "fail",
        "Generated card YAML text has no obvious empty containers, invalid conditionals, or leftover HI markers.",
        {"failures": card_sanity_failures},
    )

    if write_test_exports:
        unscoped_layouts = _layouts_from_written_paths(unscoped_written or [])
        scoped_layouts = _layouts_from_written_paths(scoped_written or [])
        _add_check(
            checks,
            "dump_cards_unscoped_export_all",
            "pass" if required_layouts <= unscoped_layouts else "fail",
            "Unscoped dump_cards exported every cached/generated layout.",
            {"written": list(unscoped_written or []), "layouts": sorted(unscoped_layouts)},
        )
        _add_check(
            checks,
            "dump_cards_scoped_export_single_layout",
            "pass" if scoped_layouts == {"v2_tablet"} else "fail",
            "Scoped dump_cards exported only the selected v2_tablet layout.",
            {"written": list(scoped_written or []), "layouts": sorted(scoped_layouts)},
        )
    else:
        _add_check(
            checks,
            "dump_cards_export_contract",
            "skip",
            "Set write_test_exports: true to write test card exports and verify scoped/unscoped dump_cards behavior in Home Assistant.",
        )

    if frontend_dependencies is None:
        frontend_dependencies = frontend_dependency_not_inspectable(
            "Frontend dependency status was not supplied by the service handler."
        )
    _add_check(
        checks,
        "frontend_dependencies_reported",
        "pass",
        "Optional frontend dependency resource status was reported without blocking backend validation.",
        frontend_dependencies,
    )

    drift_dependency = humidity_drift_dependency_status(hass)
    _add_check(
        checks,
        "house_humidity_drift_7d_dependency",
        "pass" if drift_dependency.get("available") else "warn",
        "House humidity drift 7d statistics dependency is available."
        if drift_dependency.get("available")
        else "House humidity drift 7d is unavailable until its statistics dependency reports a numeric value.",
        drift_dependency,
    )

    unavailable = _unavailable_configured_entities(hass, effective, entity_map)
    _add_check(
        checks,
        "configured_entity_availability",
        "pass" if not unavailable else "warn",
        "All configured/mapped entity references are currently available." if not unavailable else "Some configured/mapped entity references are missing, unknown, or unavailable.",
        {"unavailable_or_unknown_entities": unavailable},
    )

    return {
        "status": _combined_check_status([{"status": check["status"]} for check in checks]),
        "entry_id": getattr(entry, "entry_id", None),
        "checks": checks,
    }


def _v205_release_check_manifest_status(manifest_version: Optional[str]) -> Tuple[str, str]:
    version = manifest_version or "unknown"
    if manifest_version and _V205_RELEASE_CHECK_COMPATIBLE_VERSION_RE.fullmatch(manifest_version):
        return (
            "pass",
            f"Manifest version is {version}; v205_release_check is compatible with the v2.0.5/v2.0.6 maintenance line.",
        )
    return (
        "fail",
        f"Manifest version is {version}; expected 2.0.5 or a v2.0.6 beta/rc/stable version.",
    )


def _effective_entry_config(entry: Any) -> dict:
    effective = dict(getattr(entry, "data", None) or {})
    effective.update(dict(getattr(entry, "options", None) or {}))
    return effective


def _add_check(
    checks: List[Dict[str, Any]],
    check_id: str,
    status: str,
    message: str,
    details: Optional[Any] = None,
) -> None:
    row: Dict[str, Any] = {"id": check_id, "status": status, "message": message}
    if details is not None:
        row["details"] = _to_jsonable(details)
    checks.append(row)


def _combined_check_status(items: List[dict]) -> str:
    statuses = [item.get("status") for item in items]
    if any(status == "fail" for status in statuses):
        return "fail"
    if any(status == "warn" for status in statuses):
        return "warn"
    return "pass"


def _output_details_visibility_failures(cards: dict, show_output_details: bool) -> List[str]:
    failures: List[str] = []
    for layout in ("v2_mobile", "v2_tablet"):
        card = str(cards.get(layout, ""))
        has_output_panel = "name: Outputs" in card or "entity: input_boolean.air_control_output_expanded" in card or "entity: switch.hi_input_air_control_output_expanded" in card
        if show_output_details and not has_output_panel:
            failures.append(f"{layout}: output details panel expected but not found")
        if not show_output_details and has_output_panel:
            failures.append(f"{layout}: output details panel present while disabled")
    return failures


def _generated_card_text_sanity_failures(cards: dict) -> List[str]:
    failures: List[str] = []
    for layout, card in (cards or {}).items():
        text = str(card)
        if "cards: []" in text:
            failures.append(f"{layout}: empty cards list")
        if "# hi:output-details" in text:
            failures.append(f"{layout}: output-details marker was not stripped")
        if re.search(r"type:\s*conditional\s*\n\s*(?:conditions:\s*\[\]|card:\s*(?:\n|$))", text):
            failures.append(f"{layout}: invalid conditional block")
    return failures


def _layouts_from_written_paths(paths: List[str]) -> set[str]:
    layouts = set()
    for path in paths:
        text = str(path)
        for layout in _ALLOWED_LAYOUTS:
            if text.endswith(f"_{layout}.yaml") or f"_{layout}." in text:
                layouts.add(layout)
    return layouts


_async_frontend_dependency_status = async_frontend_dependency_status
_frontend_dependency_not_inspectable = frontend_dependency_not_inspectable


def _safe_report_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(value or "entry"))[:48] or "entry"


def _zone_mapping_summary(zones: dict) -> dict:
    summary = {}
    if not isinstance(zones, dict):
        return summary
    for key, zone in zones.items():
        if not isinstance(zone, dict):
            continue
        summary[str(key)] = {
            "enabled": bool(zone.get("enabled")),
            "level": zone.get("level"),
            "rooms": list(zone.get("rooms") or []),
            "outputs": list(zone.get("outputs") or []),
            "output_level": zone.get("output_level"),
            "boost_output_level": zone.get("boost_output_level"),
            "triggers": list(zone.get("triggers") or []),
            "thresholds": dict(zone.get("thresholds") or {}),
        }
    return summary


def _alert_mapping_summary(alerts: list) -> list:
    rows = []
    for idx, alert in enumerate(alerts or [], start=1):
        if not isinstance(alert, dict):
            continue
        rows.append({
            "index": idx,
            "enabled": bool(alert.get("enabled", True)),
            "trigger_type": alert.get("trigger_type"),
            "room": alert.get("room"),
            "threshold": alert.get("threshold"),
            "visual_lights": list(alert.get("lights") or []),
            "power_entity": alert.get("power_entity"),
            "flash_mode": alert.get("flash_mode", "red"),
            "duration": alert.get("duration", 10),
        })
    return rows


def _visual_alert_summary(alerts: list) -> list:
    return [
        {
            "index": row["index"],
            "trigger_type": row["trigger_type"],
            "room": row["room"],
            "lights": row["visual_lights"],
            "power_entity": row["power_entity"],
            "flash_mode": row["flash_mode"],
            "flash_count": 10,
            "repeat_minutes": 30,
            "restore_state": True,
        }
        for row in _alert_mapping_summary(alerts)
        if row.get("visual_lights")
    ]


def _unavailable_configured_entities(hass: HomeAssistant, config: dict, entity_map: dict) -> list:
    entity_ids = set()
    for item in config.get("telemetry", []) or []:
        if isinstance(item, dict) and item.get("entity_id"):
            entity_ids.add(item["entity_id"])
    for entity_id in config.get("presence_gate", {}).get("entities", []) or []:
        entity_ids.add(entity_id)
    for section_name in ("zones", "aq", "humidifiers"):
        section = config.get(section_name, {})
        if isinstance(section, dict):
            for row in section.values():
                if not isinstance(row, dict):
                    continue
                for entity_id in row.get("outputs", []) or []:
                    entity_ids.add(entity_id)
    for alert in config.get("alerts", []) or []:
        if not isinstance(alert, dict):
            continue
        for entity_id in alert.get("lights", []) or []:
            entity_ids.add(entity_id)
        if alert.get("power_entity"):
            entity_ids.add(alert["power_entity"])
    for entity_id in (entity_map or {}).values():
        if entity_id:
            entity_ids.add(entity_id)

    missing = []
    for entity_id in sorted(entity_ids):
        state = hass.states.get(entity_id)
        if state is None:
            missing.append({"entity_id": entity_id, "status": "missing"})
            continue
        if str(state.state).lower() in {"unknown", "unavailable"}:
            missing.append({"entity_id": entity_id, "status": str(state.state).lower()})
    return missing


async def _dump_cards_to_file(
    hass: HomeAssistant,
    entry_id: str | None,
    filename: str | None,
    layout: str | None = None,
) -> List[str]:
    entries = []
    if entry_id:
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry:
            entries = [entry]
    else:
        entries = hass.config_entries.async_entries(DOMAIN)

    written: List[str] = []
    for entry in entries:
        data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
        cards = data.get("cards", {}) or {}
        for name, card_yaml in cards.items():
            if layout and name != layout:
                continue
            target = _build_cards_filename(filename, name, entry.entry_id, len(entries) > 1)
            path = hass.config.path(target)
            await hass.async_add_executor_job(_write_text, path, card_yaml)
            written.append(f"/config/{target}")
    return written


def _build_cards_filename(
    base: str | None,
    layout: str,
    entry_id: str,
    multiple: bool,
) -> str:
    prefix = base or "humidity_intelligence_cards"
    if prefix.endswith(".yaml"):
        prefix = prefix[:-5]
    if prefix.endswith(".yml"):
        prefix = prefix[:-4]
    if multiple:
        return f"{prefix}_{entry_id}_{layout}.yaml"
    return f"{prefix}_{layout}.yaml"


def _format_cards_message(paths: List[str]) -> str:
    if not paths:
        return "No cards were generated."
    if len(paths) == 1:
        return f"Card written to {paths[0]}. Open in File Editor to copy YAML."
    lines = "\n".join(paths)
    return f"Cards written:\n{lines}\n\nOpen any file in File Editor to copy YAML."


def _supports_color(state) -> bool:
    if state is None:
        return False
    modes = state.attributes.get("supported_color_modes") or []
    return "rgb" in modes or "hs" in modes


def _dedupe_lights(lights: List[str]) -> List[str]:
    ordered: List[str] = []
    seen = set()
    for light in lights:
        if light in seen:
            continue
        ordered.append(light)
        seen.add(light)
    return ordered


def _light_flash_locks(hass: HomeAssistant, lights: List[str]) -> List[asyncio.Lock]:
    domain_data = hass.data.setdefault(DOMAIN, {})
    locks: Dict[str, asyncio.Lock] = domain_data.setdefault(_FLASH_LIGHT_LOCKS_KEY, {})
    return [locks.setdefault(light, asyncio.Lock()) for light in sorted(set(lights))]


def _capture_light_states(hass: HomeAssistant, lights: List[str]) -> Dict[str, Dict[str, Any]]:
    captured: Dict[str, Dict[str, Any]] = {}
    for light in lights:
        state = hass.states.get(light)
        captured[light] = {
            "state": state.state if state is not None else None,
            "attributes": dict(state.attributes) if state is not None else {},
        }
    return captured


async def _flash_lights(
    hass: HomeAssistant,
    lights: List[str],
    color: Tuple[int, int, int],
    duration: int,
    flash_count: Optional[int],
    supports_color: dict,
) -> None:
    interval = 0.5
    if flash_count is None:
        flash_count = max(1, int(duration / interval))

    for _ in range(flash_count):
        for light in lights:
            data = {"entity_id": light, "brightness": 255}
            if supports_color.get(light):
                data["rgb_color"] = color
            try:
                await hass.services.async_call("light", "turn_on", data, blocking=True)
            except Exception:
                _LOGGER.exception("Failed to turn on flashing light %s", light)
        await asyncio.sleep(interval)
        for light in lights:
            try:
                await hass.services.async_call("light", "turn_off", {"entity_id": light}, blocking=True)
            except Exception:
                _LOGGER.exception("Failed to turn off flashing light %s", light)
        await asyncio.sleep(interval)


async def _restore_lights(hass: HomeAssistant, states: Dict[str, Dict[str, Any]]) -> None:
    for entity_id, snapshot in states.items():
        initial_state = snapshot.get("state")
        if initial_state is None:
            continue
        if initial_state == "on":
            data = {"entity_id": entity_id}
            attrs = snapshot.get("attributes") or {}
            if "brightness" in attrs:
                data["brightness"] = attrs.get("brightness")
            if "rgb_color" in attrs:
                data["rgb_color"] = attrs.get("rgb_color")
            if "hs_color" in attrs:
                data["hs_color"] = attrs.get("hs_color")
            if "color_temp" in attrs:
                data["color_temp"] = attrs.get("color_temp")
            if "effect" in attrs:
                data["effect"] = attrs.get("effect")
            try:
                await hass.services.async_call("light", "turn_on", data, blocking=True)
            except Exception:
                _LOGGER.exception("Failed to restore light state for %s", entity_id)
        else:
            try:
                await hass.services.async_call("light", "turn_off", {"entity_id": entity_id}, blocking=True)
            except Exception:
                _LOGGER.exception("Failed to restore light off state for %s", entity_id)
