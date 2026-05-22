"""Native Home Assistant diagnostics for Humidity Intelligence."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ALERT_HANDLING_ENABLED,
    CONF_AUTO_REFRESH_UI_ON_STARTUP,
    CONF_SHOW_OUTPUT_ENTITY_DETAILS,
    CONF_SHOW_TEMPERATURE_CHIPS,
    DEFAULT_ALERT_HANDLING_ENABLED,
    DEFAULT_AUTO_REFRESH_UI_ON_STARTUP,
    DEFAULT_SHOW_OUTPUT_ENTITY_DETAILS,
    DEFAULT_SHOW_TEMPERATURE_CHIPS,
    DOMAIN,
    SLOPE_MODE_NONE,
)
from .helpers.drift import humidity_drift_dependency_status, humidity_drift_warning
from .helpers.frontend_dependencies import (
    async_frontend_dependency_status,
    frontend_dependency_not_inspectable,
)
from .helpers.local_versions import async_local_version_status, cached_local_version_status
from .helpers.seasonal import resolve_target_profile, resolve_temperature_comfort_profile
from .helpers.zone_validation import detect_zone_mapping_duplicates, summarize_zone_mapping_duplicates

TO_REDACT = (
    "access_key",
    "access_token",
    "address",
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "client_secret",
    "device_id",
    "device_ids",
    "email",
    "external_url",
    "gps_accuracy",
    "host",
    "host_name",
    "hostname",
    "internal_url",
    "ip",
    "ip_address",
    "latitude",
    "long_lived_access_token",
    "longitude",
    "mac",
    "mac_address",
    "password",
    "phone",
    "postal_code",
    "postcode",
    "refresh_token",
    "secret",
    "secrets",
    "ssid",
    "street",
    "street_address",
    "token",
    "unique_id",
    "unique_ids",
    "url",
    "user",
    "username",
    "webhook_id",
    "webhook_url",
)

_SENSITIVE_KEY_PARTS = (
    "access_token",
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "client_secret",
    "address",
    "external_url",
    "device_id",
    "internal_url",
    "host_name",
    "hostname",
    "ip_address",
    "latitude",
    "longitude",
    "long_lived_access_token",
    "mac_address",
    "password",
    "refresh_token",
    "secret",
    "street_address",
    "token",
    "unique_id",
    "webhook",
)
_URL_RE = re.compile(r"(?i)\b(?:https?|wss?|mqtt)://[^\s)>\"]+")
_BEARER_RE = re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{8,}")
_QUERY_SECRET_RE = re.compile(
    r"(?i)([?&](?:access_token|api_key|apikey|auth|key|password|secret|signature|sig|token)=)[^&#\s]+"
)
_SAFE_STATE_ATTRIBUTES = {
    "device_class",
    "display",
    "friendly_name",
    "humidity",
    "mode",
    "percentage",
    "preset_mode",
    "target_humidity",
    "unit_of_measurement",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return redacted diagnostics for a Humidity Intelligence config entry."""

    runtime_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    effective = _effective_entry_config(entry)
    entity_map = runtime_data.get("entity_map") or {}
    frontend_dependencies = await _safe_frontend_dependency_status(hass)
    local_version_status = await async_local_version_status(hass)
    manifest_version = await _async_read_manifest_version(hass)
    diagnostics_summary = _diagnostics_summary(
        hass,
        effective,
        entity_map,
        runtime_data,
        frontend_dependencies=frontend_dependencies,
        local_version_status=local_version_status,
    )

    payload = {
        "integration": {
            "domain": DOMAIN,
            "integration_version": manifest_version,
            "home_assistant_version": HA_VERSION,
            "diagnostics_schema": 1,
            "native_home_assistant_diagnostics": True,
            "runtime_control_changed_by_diagnostics": False,
        },
        "config_entry": {
            "entry_id": getattr(entry, "entry_id", None),
            "title": getattr(entry, "title", None),
            "data": getattr(entry, "data", {}) or {},
            "options": getattr(entry, "options", {}) or {},
        },
        "configuration": {
            "summary": _configuration_summary(effective),
            "options_summary": _options_summary(effective),
            "enabled_feature_areas": _enabled_feature_areas(effective),
            "selected_entities": _selected_entities(effective),
        },
        "runtime": _runtime_summary(
            hass,
            effective,
            runtime_data,
            entity_map,
            diagnostics_summary,
        ),
        "frontend": {
            "dependency_status": frontend_dependencies,
            "status_source": "shared Lovelace resource inspection when available",
            "optional_backend_dependency": False,
        },
        "generated_ui": _generated_ui_summary(effective, runtime_data),
        "diagnostics_summary": diagnostics_summary,
        "privacy": {
            "redaction": "Home Assistant async_redact_data plus HI URL/token/key sanitising.",
            "review_reminder": (
                "The bundle is designed to redact sensitive values, but users should review it before "
                "attaching it to a public GitHub issue."
            ),
        },
    }

    sanitized = _sanitize_sensitive(_to_jsonable(payload))
    return async_redact_data(sanitized, TO_REDACT)


async def _safe_frontend_dependency_status(hass: HomeAssistant) -> dict[str, Any]:
    try:
        return await async_frontend_dependency_status(hass)
    except Exception as err:
        return frontend_dependency_not_inspectable(
            f"Frontend dependency status could not be inspected: {err}"
        )


async def _async_read_manifest_version(hass: HomeAssistant) -> str | None:
    def _read_version() -> str | None:
        path = os.path.join(os.path.dirname(__file__), "manifest.json")
        with open(path, "r", encoding="utf-8") as manifest:
            version = json.load(manifest).get("version")
        return str(version) if version is not None else None

    try:
        return await hass.async_add_executor_job(_read_version)
    except Exception:
        return None


def _effective_entry_config(entry: ConfigEntry) -> dict[str, Any]:
    effective = dict(getattr(entry, "data", None) or {})
    effective.update(dict(getattr(entry, "options", None) or {}))
    return effective


def _configuration_summary(config: dict[str, Any]) -> dict[str, Any]:
    telemetry = _list(config.get("telemetry"))
    zones = _dict(config.get("zones"))
    aq = _dict(config.get("aq"))
    humidifiers = _dict(config.get("humidifiers"))
    alerts = _list(config.get("alerts"))
    return {
        "telemetry_count": len(telemetry),
        "zone_count": len([zone for zone in zones.values() if isinstance(zone, dict) and zone.get("enabled")]),
        "aq_lane_count": len([row for row in aq.values() if isinstance(row, dict) and row.get("enabled", True)]),
        "humidifier_lane_count": len(
            [row for row in humidifiers.values() if isinstance(row, dict) and row.get("enabled", True)]
        ),
        "alert_rule_count": len([row for row in alerts if isinstance(row, dict) and row.get("enabled", True)]),
        "alert_only_mode": bool(config.get("alert_only_mode", False)),
    }


def _options_summary(config: dict[str, Any]) -> dict[str, Any]:
    slope = _dict(config.get("slope"))
    return {
        CONF_AUTO_REFRESH_UI_ON_STARTUP: bool(
            config.get(CONF_AUTO_REFRESH_UI_ON_STARTUP, DEFAULT_AUTO_REFRESH_UI_ON_STARTUP)
        ),
        CONF_ALERT_HANDLING_ENABLED: bool(
            config.get(CONF_ALERT_HANDLING_ENABLED, DEFAULT_ALERT_HANDLING_ENABLED)
        ),
        CONF_SHOW_OUTPUT_ENTITY_DETAILS: bool(
            config.get(CONF_SHOW_OUTPUT_ENTITY_DETAILS, DEFAULT_SHOW_OUTPUT_ENTITY_DETAILS)
        ),
        CONF_SHOW_TEMPERATURE_CHIPS: bool(
            config.get(CONF_SHOW_TEMPERATURE_CHIPS, slope.get(CONF_SHOW_TEMPERATURE_CHIPS, DEFAULT_SHOW_TEMPERATURE_CHIPS))
        ),
        "engine_interval_minutes": config.get("engine_interval_minutes"),
        "target_profile": config.get("target_profile", config.get("target_profile_mode", "auto")),
        "temperature_comfort_mode": config.get("temperature_comfort_mode", "auto"),
        "slope_mode": slope.get("mode"),
    }


def _enabled_feature_areas(config: dict[str, Any]) -> dict[str, bool]:
    zones = _dict(config.get("zones"))
    aq = _dict(config.get("aq"))
    humidifiers = _dict(config.get("humidifiers"))
    alerts = _list(config.get("alerts"))
    slope = _dict(config.get("slope"))
    alert_only_mode = bool(config.get("alert_only_mode", False))
    return {
        "telemetry": bool(_list(config.get("telemetry"))),
        "zone_control": not alert_only_mode and any(
            isinstance(zone, dict) and zone.get("enabled") for zone in zones.values()
        ),
        "air_quality": not alert_only_mode and any(
            isinstance(row, dict) and row.get("enabled", True) for row in aq.values()
        ),
        "humidifiers": not alert_only_mode and any(
            isinstance(row, dict) and row.get("enabled", True) for row in humidifiers.values()
        ),
        "alert_handling": bool(config.get(CONF_ALERT_HANDLING_ENABLED, DEFAULT_ALERT_HANDLING_ENABLED)),
        "visual_alerts": any(
            isinstance(alert, dict) and (alert.get("lights") or alert.get("power_entity"))
            for alert in alerts
        ),
        "temperature_slope": bool(slope and slope.get("mode") != SLOPE_MODE_NONE),
        "generated_ui": bool(config.get("ui_layouts")),
        "alert_only_mode": alert_only_mode,
    }


def _selected_entities(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "telemetry": [
            {
                "entity_id": item.get("entity_id"),
                "sensor_type": item.get("sensor_type"),
                "level": item.get("level"),
                "room": item.get("room"),
                "friendly_name": item.get("friendly_name"),
            }
            for item in _list(config.get("telemetry"))
            if isinstance(item, dict)
        ],
        "presence_gate": list(_dict(config.get("presence_gate")).get("entities") or []),
        "zones": {
            key: {
                "enabled": bool(zone.get("enabled")),
                "level": zone.get("level"),
                "rooms": list(zone.get("rooms") or []),
                "outputs": list(zone.get("outputs") or []),
            }
            for key, zone in _dict(config.get("zones")).items()
            if isinstance(zone, dict)
        },
        "air_quality": _lane_outputs(config.get("aq")),
        "humidifiers": _lane_outputs(config.get("humidifiers")),
        "alerts": [
            {
                "index": idx,
                "enabled": bool(alert.get("enabled", True)),
                "trigger_type": alert.get("trigger_type"),
                "room": alert.get("room"),
                "lights": list(alert.get("lights") or []),
                "power_entity": alert.get("power_entity"),
            }
            for idx, alert in enumerate(_list(config.get("alerts")), start=1)
            if isinstance(alert, dict)
        ],
        "slope": {
            "mode": _dict(config.get("slope")).get("mode"),
            "source_entities": list(_dict(config.get("slope")).get("source_entities") or []),
            "provided_sensors": list(_dict(config.get("slope")).get("provided_sensors") or []),
        },
    }


def _runtime_summary(
    hass: HomeAssistant,
    config: dict[str, Any],
    runtime_data: dict[str, Any],
    entity_map: dict[str, Any],
    diagnostics_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "current_state": {
            "runtime_mode": runtime_data.get("runtime_mode"),
            "runtime_mode_display": runtime_data.get("runtime_mode_display"),
            "reason_text": runtime_data.get("runtime_reason_full") or runtime_data.get("runtime_reason"),
            "reason_truncated": bool(runtime_data.get("runtime_reason_truncated")),
        },
        "active_lane": runtime_data.get("runtime_mode"),
        "active_mode": runtime_data.get("runtime_mode_display"),
        "active_alert_resolution": runtime_data.get("alert_telemetry", []),
        "gate_states": _gate_states(hass, config, runtime_data),
        "output_states": _output_states(hass, config),
        "mapped_runtime_entities": _mapped_entity_states(hass, entity_map),
        "unavailable_or_unknown_entities": _unavailable_configured_entities(hass, config, entity_map),
        "warnings": diagnostics_summary.get("warnings", []),
        "recent_hi_warnings_errors": {
            "status": "not_available",
            "reason": "Home Assistant log history is not exposed through native config-entry diagnostics.",
            "diagnostic_warnings": diagnostics_summary.get("warnings", []),
        },
    }


def _gate_states(
    hass: HomeAssistant,
    config: dict[str, Any],
    runtime_data: dict[str, Any],
) -> dict[str, Any]:
    presence_gate = _dict(config.get("presence_gate"))
    time_gate = _dict(config.get("time_gate"))
    booleans = _dict(runtime_data.get("hi_input_booleans"))
    timers = _dict(runtime_data.get("hi_timers"))
    return {
        "time_gate": {
            "enabled": bool(time_gate.get("enabled")),
            "start": time_gate.get("start"),
            "end": time_gate.get("end"),
            "outside_action": time_gate.get("outside_action"),
        },
        "presence_gate": {
            "enabled": bool(presence_gate.get("enabled")),
            "entities": [_entity_state(hass, entity_id) for entity_id in presence_gate.get("entities") or []],
            "present_states": list(presence_gate.get("present_states") or []),
            "away_states": list(presence_gate.get("away_states") or []),
        },
        "control_switches": {
            key: {
                "entity_id": getattr(entity, "entity_id", None),
                "is_on": bool(getattr(entity, "is_on", False)),
            }
            for key, entity in booleans.items()
        },
        "pause_timers": {
            key: {
                "entity_id": getattr(timer, "entity_id", None),
                "state": _timer_state(timer),
            }
            for key, timer in timers.items()
        },
    }


def _output_states(hass: HomeAssistant, config: dict[str, Any]) -> dict[str, Any]:
    fan_outputs = set()
    for section_name in ("zones", "aq"):
        for row in _dict(config.get(section_name)).values():
            if isinstance(row, dict):
                fan_outputs.update(row.get("outputs") or [])

    humidifier_outputs = set()
    for row in _dict(config.get("humidifiers")).values():
        if isinstance(row, dict):
            humidifier_outputs.update(row.get("outputs") or [])

    visual_alert_outputs = set()
    for alert in _list(config.get("alerts")):
        if not isinstance(alert, dict):
            continue
        visual_alert_outputs.update(alert.get("lights") or [])
        if alert.get("power_entity"):
            visual_alert_outputs.add(alert["power_entity"])

    return {
        "fan_outputs": [_entity_state(hass, entity_id) for entity_id in sorted(fan_outputs)],
        "humidifier_outputs": [_entity_state(hass, entity_id) for entity_id in sorted(humidifier_outputs)],
        "visual_alert_outputs": [_entity_state(hass, entity_id) for entity_id in sorted(visual_alert_outputs)],
    }


def _mapped_entity_states(hass: HomeAssistant, entity_map: dict[str, Any]) -> dict[str, Any]:
    rows = {}
    for key, entity_id in sorted((entity_map or {}).items()):
        if not entity_id:
            continue
        rows[str(key)] = _entity_state(hass, str(entity_id))
    return rows


def _entity_state(hass: HomeAssistant, entity_id: str) -> dict[str, Any]:
    state = hass.states.get(entity_id)
    if state is None:
        return {"entity_id": entity_id, "status": "missing"}
    attrs = {
        key: value
        for key, value in dict(getattr(state, "attributes", {}) or {}).items()
        if key in _SAFE_STATE_ATTRIBUTES
    }
    return {
        "entity_id": entity_id,
        "status": str(getattr(state, "state", "unknown")).lower(),
        "state": getattr(state, "state", None),
        "attributes": attrs,
    }


def _generated_ui_summary(config: dict[str, Any], runtime_data: dict[str, Any]) -> dict[str, Any]:
    cards = _dict(runtime_data.get("cards"))
    unresolved = runtime_data.get("unresolved_placeholders") or []
    unresolved_by_card = runtime_data.get("unresolved_placeholders_by_card") or {}
    return {
        "configured_layouts": list(config.get("ui_layouts") or []),
        "cached_layouts": sorted(cards.keys()),
        "cached_layout_sizes": {str(name): len(str(card)) for name, card in cards.items()},
        "unresolved_placeholders_count": len(unresolved),
        "unresolved_placeholders_sample": list(unresolved)[:20],
        "unresolved_placeholders_by_card_count": len(unresolved_by_card),
        "show_output_entity_details": bool(
            config.get(CONF_SHOW_OUTPUT_ENTITY_DETAILS, DEFAULT_SHOW_OUTPUT_ENTITY_DETAILS)
        ),
    }


def _diagnostics_summary(
    hass: HomeAssistant,
    config: dict[str, Any],
    entity_map: dict[str, Any],
    runtime_data: dict[str, Any],
    *,
    frontend_dependencies: dict[str, Any],
    local_version_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    telemetry = _list(config.get("telemetry"))
    zones = _dict(config.get("zones"))
    alerts = _list(config.get("alerts"))
    target_profile = resolve_target_profile(config)
    comfort_profile = resolve_temperature_comfort_profile(config)
    duplicates = detect_zone_mapping_duplicates(telemetry, zones)
    duplicate_summary = summarize_zone_mapping_duplicates(duplicates)
    unavailable = _unavailable_configured_entities(hass, config, entity_map)
    drift_dependency = humidity_drift_dependency_status(hass)
    drift_dependency_warning = humidity_drift_warning(drift_dependency)
    warnings = []
    if duplicate_summary:
        warnings.append(duplicate_summary)
    if unavailable:
        warnings.append(f"{len(unavailable)} configured/mapped entity references are missing, unknown, or unavailable.")
    if drift_dependency_warning:
        warnings.append(drift_dependency_warning)
    if not telemetry:
        warnings.append("No telemetry sensors are configured.")
    if not zones and not config.get("alert_only_mode"):
        warnings.append("No control zones are configured.")

    return {
        "target_profile": {
            "mode": config.get("target_profile", config.get("target_profile_mode", "auto")),
            "active_profile": target_profile.key,
            "active_season": target_profile.label,
            "target_low": target_profile.low,
            "target_high": target_profile.high,
            "high_risk": target_profile.high_risk,
            "custom_target_low": config.get("custom_target_low"),
            "custom_target_high": config.get("custom_target_high"),
        },
        "temperature_comfort": {
            "mode": config.get("temperature_comfort_mode", "auto"),
            "active_profile": comfort_profile.key,
            "active_label": comfort_profile.label,
            "target_low": comfort_profile.low,
            "target_high": comfort_profile.high,
            "custom_low": config.get("temperature_comfort_custom_low"),
            "custom_high": config.get("temperature_comfort_custom_high"),
        },
        "zone_mappings": _zone_mapping_summary(zones),
        "zone_mapping_duplicates": duplicates,
        "alert_mappings": _alert_mapping_summary(alerts),
        "active_alert_resolution": runtime_data.get("alert_telemetry", []),
        "visual_alerts": _visual_alert_summary(alerts),
        "humidity_drift_7d": drift_dependency,
        "frontend_dependency_resources": frontend_dependencies,
        "local_version_preservation": local_version_status or cached_local_version_status(hass),
        "unavailable_or_unknown_entities": unavailable,
        "warnings": warnings,
    }


def _zone_mapping_summary(zones: dict[str, Any]) -> dict[str, Any]:
    summary = {}
    for key, zone in (zones or {}).items():
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


def _alert_mapping_summary(alerts: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for idx, alert in enumerate(alerts or [], start=1):
        if not isinstance(alert, dict):
            continue
        rows.append(
            {
                "index": idx,
                "enabled": bool(alert.get("enabled", True)),
                "trigger_type": alert.get("trigger_type"),
                "room": alert.get("room"),
                "threshold": alert.get("threshold"),
                "visual_lights": list(alert.get("lights") or []),
                "power_entity": alert.get("power_entity"),
                "flash_mode": alert.get("flash_mode", "red"),
                "duration": alert.get("duration", 10),
            }
        )
    return rows


def _visual_alert_summary(alerts: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for alert in _alert_mapping_summary(alerts):
        if not alert.get("visual_lights"):
            continue
        rows.append(
            {
                "index": alert["index"],
                "trigger_type": alert["trigger_type"],
                "room": alert["room"],
                "lights": alert["visual_lights"],
                "power_entity": alert["power_entity"],
                "flash_mode": alert["flash_mode"],
                "flash_count": 10,
                "repeat_minutes": 30,
                "restore_state": True,
            }
        )
    return rows


def _unavailable_configured_entities(
    hass: HomeAssistant,
    config: dict[str, Any],
    entity_map: dict[str, Any],
) -> list[dict[str, Any]]:
    entity_ids = set()
    for item in _list(config.get("telemetry")):
        if isinstance(item, dict) and item.get("entity_id"):
            entity_ids.add(str(item["entity_id"]))
    entity_ids.update(str(entity_id) for entity_id in _dict(config.get("presence_gate")).get("entities") or [])
    for section_name in ("zones", "aq", "humidifiers"):
        for row in _dict(config.get(section_name)).values():
            if isinstance(row, dict):
                entity_ids.update(str(entity_id) for entity_id in row.get("outputs") or [])
    for alert in _list(config.get("alerts")):
        if not isinstance(alert, dict):
            continue
        entity_ids.update(str(entity_id) for entity_id in alert.get("lights") or [])
        if alert.get("power_entity"):
            entity_ids.add(str(alert["power_entity"]))
    entity_ids.update(str(entity_id) for entity_id in (entity_map or {}).values() if entity_id)

    unavailable = []
    for entity_id in sorted(entity_ids):
        state = hass.states.get(entity_id)
        if state is None:
            unavailable.append({"entity_id": entity_id, "status": "missing"})
            continue
        if str(getattr(state, "state", "")).lower() in {"unknown", "unavailable"}:
            unavailable.append({"entity_id": entity_id, "status": str(state.state).lower()})
    return unavailable


def _lane_outputs(value: Any) -> dict[str, list[str]]:
    rows = {}
    for key, row in _dict(value).items():
        if isinstance(row, dict):
            rows[str(key)] = list(row.get("outputs") or [])
    return rows


def _timer_state(timer: Any) -> Any:
    native_value = getattr(timer, "native_value", None)
    if native_value is not None:
        return native_value
    return getattr(timer, "state", None)


def _sanitize_sensitive(value: Any, *, key: str | None = None) -> Any:
    if key is not None and _sensitive_key(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(item_key): _sanitize_sensitive(item_value, key=str(item_key)) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [_sanitize_sensitive(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_sensitive(item) for item in value]
    if isinstance(value, str):
        return _sanitize_string(value)
    return value


def _sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return lowered in TO_REDACT or any(part in lowered for part in _SENSITIVE_KEY_PARTS)


def _sanitize_string(value: str) -> str:
    text = _BEARER_RE.sub("Bearer [REDACTED]", value)
    text = _QUERY_SECRET_RE.sub(lambda match: f"{match.group(1)}[REDACTED]", text)
    return _URL_RE.sub("[REDACTED_URL]", text)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if hasattr(value, "items"):
        try:
            return {str(key): _to_jsonable(item) for key, item in value.items()}
        except (AttributeError, TypeError, ValueError):
            pass
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except (AttributeError, TypeError, ValueError):
            pass
    return str(value)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
