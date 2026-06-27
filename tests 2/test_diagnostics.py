"""Direct tests for native Home Assistant diagnostics support."""

from __future__ import annotations

import asyncio
import copy
import importlib.util
import json
import pathlib
import sys
import types
from types import SimpleNamespace


ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = "hi_diag_testpkg"


def _install_homeassistant_stubs() -> None:
    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    diagnostics_mod = types.ModuleType("homeassistant.components.diagnostics")
    lovelace = types.ModuleType("homeassistant.components.lovelace")
    lovelace_const = types.ModuleType("homeassistant.components.lovelace.const")
    core = types.ModuleType("homeassistant.core")
    config_entries = types.ModuleType("homeassistant.config_entries")
    const = types.ModuleType("homeassistant.const")

    class HomeAssistant:
        pass

    class ConfigEntry:
        pass

    class UnitOfTemperature:
        CELSIUS = "°C"
        FAHRENHEIT = "°F"

    def async_redact_data(data, to_redact):
        redact = {str(item).lower() for item in to_redact}

        def redact_value(value):
            if isinstance(value, dict):
                return {
                    key: "[REDACTED]" if str(key).lower() in redact else redact_value(item)
                    for key, item in value.items()
                }
            if isinstance(value, list):
                return [redact_value(item) for item in value]
            return value

        return redact_value(data)

    diagnostics_mod.async_redact_data = async_redact_data
    core.HomeAssistant = HomeAssistant
    config_entries.ConfigEntry = ConfigEntry
    const.__version__ = "2026.5.2"
    const.UnitOfTemperature = UnitOfTemperature
    lovelace_const.LOVELACE_DATA = "lovelace"

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.components"] = components
    sys.modules["homeassistant.components.diagnostics"] = diagnostics_mod
    sys.modules["homeassistant.components.lovelace"] = lovelace
    sys.modules["homeassistant.components.lovelace.const"] = lovelace_const
    sys.modules["homeassistant.core"] = core
    sys.modules["homeassistant.config_entries"] = config_entries
    sys.modules["homeassistant.const"] = const


def _install_package_scaffold() -> None:
    pkg = types.ModuleType(PKG)
    pkg.__path__ = [str(ROOT)]
    sys.modules[PKG] = pkg

    for sub in ("helpers",):
        mod = types.ModuleType(f"{PKG}.{sub}")
        mod.__path__ = [str(ROOT / sub)]
        sys.modules[f"{PKG}.{sub}"] = mod


def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_diagnostics_module():
    _install_homeassistant_stubs()
    _install_package_scaffold()
    _load_module(f"{PKG}.const", ROOT / "const.py")
    level_labels_path = ROOT / "helpers" / "level_labels.py"
    if level_labels_path.exists():
        _load_module(f"{PKG}.helpers.level_labels", level_labels_path)
    _load_module(f"{PKG}.helpers.frontend_dependencies", ROOT / "helpers" / "frontend_dependencies.py")
    _load_module(f"{PKG}.helpers.seasonal", ROOT / "helpers" / "seasonal.py")
    _load_module(f"{PKG}.helpers.zone_validation", ROOT / "helpers" / "zone_validation.py")
    return _load_module(f"{PKG}.diagnostics", ROOT / "diagnostics.py")


class _FakeState:
    def __init__(self, state, attrs=None):
        self.state = str(state)
        self.attributes = attrs or {}


class _FakeStates:
    def __init__(self, values):
        self._values = dict(values)

    def get(self, entity_id):
        return self._values.get(entity_id)


class _FakeConfig:
    safe_mode = False

    def path(self, *parts):
        return str(ROOT.joinpath(*parts))


class _FakeHass:
    def __init__(self, states, runtime_data):
        self.config = _FakeConfig()
        self.states = _FakeStates(states)
        self.data = {
            "humidity_intelligence": {"entry123": runtime_data},
            "lovelace": SimpleNamespace(resources=_FakeResources()),
        }

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class _FakeResources:
    loaded = True

    async def async_items(self):
        return [
            {"url": "/hacsfiles/button-card/button-card.js?v=abc123"},
            {"url": "https://user:pass@example.invalid/card-mod.js?token=REDACTION_FIXTURE"},
        ]


def _sample_entry():
    return SimpleNamespace(
        entry_id="entry123",
        title="Humidity Intelligence",
        data={
            "telemetry": [
                {
                    "entity_id": "sensor.kitchen_humidity",
                    "sensor_type": "humidity",
                    "room": "Kitchen",
                    "level": "level1",
                    "friendly_name": "Kitchen humidity",
                    "api_key": "REDACTION_FIXTURE_API_KEY",
                },
            ],
            "zones": {
                "zone1": {
                    "enabled": True,
                    "level": "level1",
                    "rooms": ["Kitchen"],
                    "outputs": ["fan.kitchen_extract"],
                    "output_level": 66,
                    "boost_output_level": 100,
                    "triggers": ["humidity_high"],
                }
            },
            "presence_gate": {
                "enabled": True,
                "entities": ["person.alice"],
                "present_states": ["home"],
                "away_states": ["not_home"],
                "webhook_url": "https://user:pass@example.invalid/hook",
                "device_id": "REDACTION_FIXTURE_DEVICE_ID",
                "unique_id": "REDACTION_FIXTURE_UNIQUE_ID",
            },
            "alerts": [
                {
                    "enabled": True,
                    "trigger_type": "humidity_danger",
                    "room": "Kitchen",
                    "lights": ["light.alert"],
                    "power_entity": "switch.alert_power",
                }
            ],
            "latitude": 51.5,
            "longitude": -0.12,
            "address": "REDACTION_FIXTURE_ADDRESS",
            "host": "REDACTION_FIXTURE_HOST",
            "ip": "REDACTION_FIXTURE_IP",
            "mac_address": "REDACTION_FIXTURE_MAC",
            "ssid": "REDACTION_FIXTURE_SSID",
            "password": "REDACTION_FIXTURE_PASSWORD",
        },
        options={
            "target_profile": "winter",
            "show_output_entity_details": False,
            "access_token": "REDACTION_FIXTURE_ACCESS_TOKEN",
            "external_url": "https://alice:pass@example.invalid/path?access_token=REDACTION_FIXTURE",
        },
    )


def _sample_hass():
    runtime_data = {
        "config": _sample_entry().data,
        "options": _sample_entry().options,
        "entity_map": {
            "air_control_mode": "sensor.air_control_mode",
            "air_control_reason": "sensor.air_control_reason",
            "zone_output": "fan.kitchen_extract",
        },
        "cards": {"v2_tablet": "type: custom:button-card\n", "v2_mobile": "type: entities\n"},
        "runtime_mode": "alert",
        "runtime_mode_display": "ALERT",
        "runtime_reason": "Humidity danger in Kitchen.",
        "runtime_reason_full": None,
        "runtime_reason_truncated": False,
        "alert_telemetry": [
            {
                "trigger_type": "humidity_danger",
                "room": "Kitchen",
                "zone": "zone1",
                "outputs": ["fan.kitchen_extract"],
                "boost_level": "100",
            }
        ],
        "unresolved_placeholders": [],
        "unresolved_placeholders_by_card": {},
    }
    return _FakeHass(
        {
            "sensor.kitchen_humidity": _FakeState("72", {"unit_of_measurement": "%"}),
            "sensor.air_control_mode": _FakeState("alert", {"display": "ALERT"}),
            "sensor.air_control_reason": _FakeState("Humidity danger in Kitchen."),
            "person.alice": _FakeState("unknown"),
            "fan.kitchen_extract": _FakeState("unavailable", {"preset_mode": "auto"}),
        },
        runtime_data,
    )


def test_native_diagnostics_payload_contains_support_sections():
    diagnostics = _load_diagnostics_module()

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(_sample_hass(), _sample_entry())
    )

    assert payload["integration"]["domain"] == "humidity_intelligence"
    assert payload["integration"]["home_assistant_version"] == "2026.5.2"
    assert payload["configuration"]["selected_entity_summary"]["telemetry"]["count"] == 1
    assert payload["configuration"]["enabled_feature_areas"]["zone_control"] is True
    assert payload["runtime"]["active_lane"] == "alert"
    assert payload["runtime"]["gate_states"]["presence_gate"]["entity_status"]["by_status"]["unknown"] == 1
    assert payload["runtime"]["output_states"]["fan_outputs"]["by_status"]["unavailable"] == 1
    assert payload["frontend"]["dependency_status"]
    assert payload["generated_ui"]["cached_layouts"] == ["v2_mobile", "v2_tablet"]


def test_manifest_declares_diagnostics_component_for_native_support():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    declared = set(manifest.get("dependencies", [])) | set(
        manifest.get("after_dependencies", [])
    )

    assert "diagnostics" in declared


def test_native_diagnostics_redacts_sensitive_keys_and_url_values():
    diagnostics = _load_diagnostics_module()

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(_sample_hass(), _sample_entry())
    )
    rendered = json.dumps(payload, sort_keys=True)

    assert "REDACTION_FIXTURE_API_KEY" not in rendered
    assert "REDACTION_FIXTURE_ACCESS_TOKEN" not in rendered
    assert "REDACTION_FIXTURE_PASSWORD" not in rendered
    assert "alice:pass" not in rendered
    assert "user:pass" not in rendered
    assert "51.5" not in rendered
    assert "-0.12" not in rendered
    assert "REDACTION_FIXTURE_ADDRESS" not in rendered
    assert "REDACTION_FIXTURE_HOST" not in rendered
    assert "REDACTION_FIXTURE_IP" not in rendered
    assert "REDACTION_FIXTURE_MAC" not in rendered
    assert "REDACTION_FIXTURE_SSID" not in rendered
    assert "REDACTION_FIXTURE_DEVICE_ID" not in rendered
    assert "REDACTION_FIXTURE_UNIQUE_ID" not in rendered
    assert "sensor.kitchen_humidity" not in rendered
    assert "[REDACTED]" in rendered


def test_native_diagnostics_uses_sanitized_counts_status_not_raw_private_ids():
    diagnostics = _load_diagnostics_module()

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(_sample_hass(), _sample_entry())
    )
    rendered = json.dumps(payload, sort_keys=True)

    assert "sensor.kitchen_humidity" not in rendered
    assert "fan.kitchen_extract" not in rendered
    assert "person.alice" not in rendered
    assert "Kitchen" not in rendered
    assert "/hacsfiles/button-card/button-card.js" not in rendered
    assert "https://user:pass@example.invalid/card-mod.js" not in rendered

    selected = payload["configuration"]["selected_entity_summary"]
    assert selected["telemetry"]["count"] == 1
    assert selected["zones"]["zone1"]["output_count"] == 1
    assert selected["presence_gate"]["entity_count"] == 1
    assert selected["alerts"][0]["visual_light_count"] == 1
    assert selected["alerts"][0]["has_power_entity"] is True

    unavailable = payload["runtime"]["unavailable_or_unknown_entities"]
    assert unavailable["count"] == 4
    assert unavailable["by_status"]["missing"] == 2
    assert unavailable["by_status"]["unknown"] == 1
    assert unavailable["by_status"]["unavailable"] == 1


def test_native_diagnostics_sanitizes_duplicate_zone_mapping_evidence():
    diagnostics = _load_diagnostics_module()
    entry = _sample_entry()
    entry.data = copy.deepcopy(entry.data)
    entry.data["zones"]["zone2"] = {
        "enabled": True,
        "level": "level1",
        "rooms": ["Kitchen"],
        "outputs": ["fan.second_private_extract"],
        "triggers": ["humidity_high"],
    }
    hass = _sample_hass()
    hass.data["humidity_intelligence"][entry.entry_id]["config"] = entry.data

    payload = asyncio.run(diagnostics.async_get_config_entry_diagnostics(hass, entry))
    rendered = json.dumps(payload, sort_keys=True)

    assert "sensor.kitchen_humidity" not in rendered
    assert "Kitchen" not in rendered
    assert payload["diagnostics_summary"]["zone_mapping_duplicates"] == {
        "count": 1,
        "pairs": {"zone1:zone2": {"entity_count": 1}},
    }
    assert (
        "1 duplicate zone mapping pair includes 1 overlapping telemetry source."
        in payload["diagnostics_summary"]["warnings"]
    )


def test_diagnostics_redacts_credential_style_keys():
    diagnostics = _load_diagnostics_module()

    payload = diagnostics.redact_diagnostics_payload(
        {
            "credential": "REDACTION_FIXTURE_CREDENTIAL",
            "credentials": {"raw": "REDACTION_FIXTURE_CREDENTIALS"},
            "credential_json": "{\"token\":\"REDACTION_FIXTURE_JSON\"}",
            "safe_label": "Kitchen",
        }
    )
    rendered = json.dumps(payload, sort_keys=True)

    assert "REDACTION_FIXTURE_CREDENTIAL" not in rendered
    assert "REDACTION_FIXTURE_CREDENTIALS" not in rendered
    assert "REDACTION_FIXTURE_JSON" not in rendered
    assert payload["safe_label"] == "Kitchen"
    assert payload["credential"] == "[REDACTED]"


def test_unavailable_entities_are_reported_without_crashing():
    diagnostics = _load_diagnostics_module()
    hass = _sample_hass()
    hass.data["humidity_intelligence"]["entry123"]["entity_map"]["missing"] = "sensor.missing_entity"

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(hass, _sample_entry())
    )

    unavailable = payload["runtime"]["unavailable_or_unknown_entities"]
    assert unavailable["count"] == 5
    assert unavailable["by_status"]["missing"] == 3
    assert unavailable["by_status"]["unknown"] == 1
    assert unavailable["by_status"]["unavailable"] == 1


def test_native_diagnostics_reports_house_drift_statistics_dependency():
    diagnostics = _load_diagnostics_module()

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(_sample_hass(), _sample_entry())
    )

    drift = payload["diagnostics_summary"]["humidity_drift_7d"]
    assert drift["required_for"] == "HI House Humidity Drift 7d"
    assert drift["dependency_entity"] == "sensor.house_humidity_mean_7d"
    assert drift["dependency_status"] == "missing"
    assert drift["available"] is False
    assert drift["repair_kind"] == "missing_helper"
    assert drift["repair_required"] is True
    assert any("HI House Humidity Drift 7d" in warning for warning in payload["runtime"]["warnings"])


def test_native_diagnostics_reports_blocked_pm25_normalization():
    diagnostics = _load_diagnostics_module()
    hass = _sample_hass()
    hass.data["humidity_intelligence"]["entry123"]["pm25_entity_id_normalization"] = {
        "changed": {},
        "blocked": [
            {
                "unique_suffix": "house_pm25_average",
                "current_entity_id": "sensor.hi_house_pm2_5_average",
                "target_entity_id": "sensor.hi_house_pm25_average",
                "reason": "target_exists",
            }
        ],
    }

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(hass, _sample_entry())
    )

    pm25 = payload["diagnostics_summary"]["pm25_entity_id_normalization"]
    assert pm25["status"] == "blocked"
    assert pm25["blocked_count"] == 1
    assert pm25["blocked_reasons"] == ["target_exists"]
    assert any("PM25 aggregate entity ID normalization is blocked" in warning for warning in payload["runtime"]["warnings"])


def test_native_diagnostics_distinguishes_existing_not_ready_drift_helper():
    diagnostics = _load_diagnostics_module()
    hass = _sample_hass()
    hass.states._values["sensor.house_humidity_mean_7d"] = _FakeState("unknown")

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(hass, _sample_entry())
    )

    drift = payload["diagnostics_summary"]["humidity_drift_7d"]
    assert drift["dependency_status"] == "unknown"
    assert drift["repair_kind"] == "helper_not_ready_or_unavailable"
    assert drift["repair_required"] is False
    assert drift["history_status"] == "not_ready_or_unavailable"


def test_native_diagnostics_reports_low_statistics_coverage_as_history_not_ready():
    diagnostics = _load_diagnostics_module()
    hass = _sample_hass()
    hass.states._values["sensor.house_humidity_mean_7d"] = _FakeState(
        50,
        {
            "age_coverage_ratio": 0.03,
            "source_value_valid": True,
        },
    )

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(hass, _sample_entry())
    )

    drift = payload["diagnostics_summary"]["humidity_drift_7d"]
    assert drift["dependency_status"] == "history_not_ready"
    assert drift["available"] is False
    assert drift["repair_kind"] == "history_not_ready"
    assert drift["repair_required"] is False
    assert drift["age_coverage_ratio"] == 0.03
    assert drift["required_age_coverage_ratio"] == 0.85
    assert drift["source_value_valid"] is True
    assert any("history_not_ready" in warning for warning in payload["runtime"]["warnings"])


def test_native_diagnostics_reports_temperature_comfort_warm_boundary():
    diagnostics = _load_diagnostics_module()
    entry = _sample_entry()
    entry.options["temperature_comfort_mode"] = "custom"
    entry.options["temperature_comfort_custom_low"] = 18.5
    entry.options["temperature_comfort_custom_high"] = 22.0

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(_sample_hass(), entry)
    )

    comfort = payload["diagnostics_summary"]["temperature_comfort"]
    assert comfort["mode"] == "custom"
    assert comfort["active_profile"] == "custom"
    assert comfort["target_low"] == 18.5
    assert comfort["target_high"] == 22.0
    assert comfort["warm_high"] == 23.0
    assert comfort["watch_high"] == 23.0


def test_native_diagnostics_reports_canonical_level_label_sources():
    diagnostics = _load_diagnostics_module()
    entry = _sample_entry()
    entry.options["level_labels"] = {
        "level1": "  Ground <Floor>  ",
        "level2": "",
    }

    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(_sample_hass(), entry)
    )

    assert payload["configuration"]["options_summary"]["level_labels"] == {
        "level1": {"label": "Ground Floor", "source": "config"},
        "level2": {"label": "Level 2", "source": "fallback"},
    }
    assert payload["diagnostics_summary"]["level_labels"] == {
        "level1": {"label": "Ground Floor", "source": "config"},
        "level2": {"label": "Level 2", "source": "fallback"},
    }


def test_to_redact_covers_required_sensitive_terms():
    diagnostics = _load_diagnostics_module()
    redacted = {str(item).lower() for item in diagnostics.TO_REDACT}

    for key in (
        "token",
        "secret",
        "password",
        "api_key",
        "webhook_url",
        "url",
        "access_token",
        "latitude",
        "longitude",
        "username",
        "host",
        "ip",
        "mac_address",
        "ssid",
        "address",
        "credential",
        "credentials",
        "credential_json",
        "device_id",
        "unique_id",
    ):
        assert key in redacted


if __name__ == "__main__":
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for name, test in tests:
        test()
    print(f"{len(tests)} diagnostics sanity checks passed.")
