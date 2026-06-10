"""Direct sanity checks for HI config/options-flow UX contracts."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import pathlib
import sys
import types
from types import SimpleNamespace


ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = "hi_config_flow_testpkg"


def _install_homeassistant_stubs() -> None:
    """Install lightweight Home Assistant stubs for config-flow imports."""
    ha = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")
    config_entries = types.ModuleType("homeassistant.config_entries")
    const = types.ModuleType("homeassistant.const")
    components = types.ModuleType("homeassistant.components")
    lovelace = types.ModuleType("homeassistant.components.lovelace")
    data_entry_flow = types.ModuleType("homeassistant.data_entry_flow")
    helpers = types.ModuleType("homeassistant.helpers")
    area_registry = types.ModuleType("homeassistant.helpers.area_registry")
    entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
    selector = types.ModuleType("homeassistant.helpers.selector")
    lovelace_const = types.ModuleType("homeassistant.components.lovelace.const")
    voluptuous = types.ModuleType("voluptuous")

    class HomeAssistant:
        pass

    class UnitOfTemperature:
        CELSIUS = "degC"
        FAHRENHEIT = "degF"

    class ConfigEntry:
        pass

    class _BaseFlow:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__()

        def async_show_form(self, **kwargs):
            return {"type": "form", **kwargs}

        def async_show_menu(self, **kwargs):
            return {"type": "menu", **kwargs}

        def async_create_entry(self, **kwargs):
            return {"type": "create_entry", **kwargs}

        def async_abort(self, **kwargs):
            return {"type": "abort", **kwargs}

    class ConfigFlow(_BaseFlow):
        async def async_set_unique_id(self, unique_id):
            self._unique_id = unique_id

        def _abort_if_unique_id_configured(self):
            return None

    class OptionsFlow(_BaseFlow):
        pass

    class _Registry:
        def async_get(self, _key):
            return None

    class _SchemaKey:
        def __init__(self, key, default=None):
            self.key = key
            self.default = default

        def __hash__(self):
            try:
                return hash((self.key, self.default))
            except TypeError:
                return hash((self.key, repr(self.default)))

        def __eq__(self, other):
            return (
                isinstance(other, _SchemaKey)
                and self.key == other.key
                and self.default == other.default
            )

    class Schema:
        def __init__(self, schema):
            self.schema = schema

        def __call__(self, value):
            return value

    class SelectOptionDict(dict):
        def __init__(self, *, value, label):
            super().__init__(value=value, label=label)

    class _SelectorConfig:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class _Selector:
        def __init__(self, config=None):
            self.config = config

    def section(schema, options):
        return {"schema": schema, "options": dict(options)}

    core.HomeAssistant = HomeAssistant
    const.UnitOfTemperature = UnitOfTemperature
    config_entries.ConfigEntry = ConfigEntry
    config_entries.ConfigFlow = ConfigFlow
    config_entries.OptionsFlow = OptionsFlow
    data_entry_flow.section = section
    area_registry.async_get = lambda _hass: _Registry()
    entity_registry.async_get = lambda _hass: _Registry()
    lovelace_const.LOVELACE_DATA = "lovelace"

    selector.SelectOptionDict = SelectOptionDict
    selector.SelectSelector = _Selector
    selector.SelectSelectorConfig = _SelectorConfig
    selector.SelectSelectorMode = SimpleNamespace(DROPDOWN="dropdown")
    selector.BooleanSelector = _Selector
    selector.EntitySelector = _Selector
    selector.EntitySelectorConfig = _SelectorConfig
    selector.TextSelector = _Selector
    selector.TextSelectorConfig = _SelectorConfig
    selector.TextSelectorType = SimpleNamespace(TEXT="text")
    selector.NumberSelector = _Selector
    selector.NumberSelectorConfig = _SelectorConfig
    selector.NumberSelectorMode = SimpleNamespace(SLIDER="slider", BOX="box")

    voluptuous.Schema = Schema
    voluptuous.Optional = _SchemaKey
    voluptuous.Required = _SchemaKey

    helpers.area_registry = area_registry
    helpers.entity_registry = entity_registry
    helpers.selector = selector

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.core"] = core
    sys.modules["homeassistant.config_entries"] = config_entries
    sys.modules["homeassistant.const"] = const
    sys.modules["homeassistant.components"] = components
    sys.modules["homeassistant.components.lovelace"] = lovelace
    sys.modules["homeassistant.data_entry_flow"] = data_entry_flow
    sys.modules["homeassistant.helpers"] = helpers
    sys.modules["homeassistant.helpers.area_registry"] = area_registry
    sys.modules["homeassistant.helpers.entity_registry"] = entity_registry
    sys.modules["homeassistant.helpers.selector"] = selector
    sys.modules["homeassistant.components.lovelace.const"] = lovelace_const
    sys.modules["voluptuous"] = voluptuous


def _install_package_scaffold() -> None:
    pkg = types.ModuleType(PKG)
    pkg.__path__ = [str(ROOT)]
    sys.modules[PKG] = pkg

    helpers = types.ModuleType(f"{PKG}.helpers")
    helpers.__path__ = [str(ROOT / "helpers")]
    sys.modules[f"{PKG}.helpers"] = helpers


def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_config_flow_module():
    _install_homeassistant_stubs()
    _install_package_scaffold()
    _load_module(f"{PKG}.const", ROOT / "const.py")
    _load_module(f"{PKG}.helpers.parsing", ROOT / "helpers" / "parsing.py")
    _load_module(f"{PKG}.helpers.drift", ROOT / "helpers" / "drift.py")
    _load_module(
        f"{PKG}.helpers.frontend_dependencies",
        ROOT / "helpers" / "frontend_dependencies.py",
    )
    _load_module(
        f"{PKG}.helpers.zone_validation",
        ROOT / "helpers" / "zone_validation.py",
    )
    return _load_module(f"{PKG}.config_flow", ROOT / "config_flow.py")


def _schema_default(result: dict, field: str):
    for key in result["data_schema"].schema:
        if getattr(key, "key", key) == field:
            return getattr(key, "default", None)
    raise AssertionError(f"{field!r} not present in schema")


def _schema_select_values(result: dict, field: str):
    for key, selector_obj in result["data_schema"].schema.items():
        if getattr(key, "key", key) == field:
            return [
                option["value"]
                for option in getattr(selector_obj.config, "options", [])
            ]
    raise AssertionError(f"{field!r} not present in schema")


def _schema_select_labels(result: dict, field: str):
    for key, selector_obj in result["data_schema"].schema.items():
        if getattr(key, "key", key) == field:
            return [
                option["label"]
                for option in getattr(selector_obj.config, "options", [])
            ]
    raise AssertionError(f"{field!r} not present in schema")


def _schema_has_field(result: dict, field: str) -> bool:
    return any(getattr(key, "key", key) == field for key in result["data_schema"].schema)


def _advanced_schema_has_field(result: dict, field: str) -> bool:
    for key, section_obj in result["data_schema"].schema.items():
        if getattr(key, "key", key) != "show_advanced_options":
            continue
        section_schema = section_obj["schema"]
        return any(
            getattr(section_key, "key", section_key) == field
            for section_key in section_schema.schema
        )
    raise AssertionError("'show_advanced_options' not present in schema")


def _option_labels(options):
    return [option["label"] for option in options]


def _base_telemetry():
    return [
        {
            "entity_id": "sensor.kitchen_humidity",
            "sensor_type": "humidity",
            "friendly_name": "Kitchen humidity",
            "level": "level1",
            "room": "Kitchen",
        },
        {
            "entity_id": "sensor.kitchen_temperature",
            "sensor_type": "temperature",
            "friendly_name": "Kitchen temperature",
            "level": "level1",
            "room": "Kitchen",
        },
    ]


def test_setup_add_sensor_cancel_requires_confirmation_and_preserves_entries():
    config_flow = _load_config_flow_module()
    flow = config_flow.HumidityIntelligenceConfigFlow()
    flow.hass = SimpleNamespace()
    existing = {
        "entity_id": "sensor.kitchen_humidity",
        "sensor_type": "humidity",
        "friendly_name": "Kitchen",
        "level": "level1",
        "room": "Kitchen",
    }
    flow._telemetry = [dict(existing)]
    flow._data["telemetry"] = flow._telemetry

    result = asyncio.run(flow.async_step_telemetry_add({"action": "cancel"}))

    assert result["type"] == "form"
    assert result["step_id"] == "cancel_confirm"
    assert _schema_select_values(result, "action") == ["return", "close"]
    assert _schema_select_labels(result, "action") == [
        "Cancel close / return to setup",
        "Close without saving",
    ]

    returned = asyncio.run(flow.async_step_cancel_confirm({"action": "return"}))

    assert returned["type"] == "form"
    assert returned["step_id"] == "telemetry"
    assert flow._telemetry == [existing]
    assert flow._data["telemetry"] == [existing]

    closed = asyncio.run(flow.async_step_cancel_confirm({"action": "close"}))

    assert closed["type"] == "abort"
    assert closed["reason"] == "user_cancelled"


def test_options_add_sensor_cancel_requires_confirmation_and_preserves_options():
    config_flow = _load_config_flow_module()
    existing = {
        "entity_id": "sensor.kitchen_humidity",
        "sensor_type": "humidity",
        "friendly_name": "Kitchen",
        "level": "level1",
        "room": "Kitchen",
    }
    entry = SimpleNamespace(data={"telemetry": [dict(existing)]}, options={})
    flow = config_flow.HumidityIntelligenceOptionsFlow(entry)
    flow.hass = SimpleNamespace()

    result = asyncio.run(flow.async_step_options_telemetry_add({"action": "cancel"}))

    assert result["type"] == "form"
    assert result["step_id"] == "options_cancel_confirm"
    assert _schema_select_values(result, "action") == ["return", "close"]
    assert _schema_select_labels(result, "action") == [
        "Cancel close / return to options",
        "Close without saving",
    ]

    returned = asyncio.run(flow.async_step_options_cancel_confirm({"action": "return"}))

    assert returned["type"] == "form"
    assert returned["step_id"] == "options_telemetry"
    assert flow._options == {}

    closed = asyncio.run(flow.async_step_options_cancel_confirm({"action": "close"}))

    assert closed["type"] == "abort"
    assert closed["reason"] == "user_cancelled"


def test_zone2_setup_defaults_to_level2_and_trigger_labels_name_zone_and_level():
    config_flow = _load_config_flow_module()
    flow = config_flow.HumidityIntelligenceConfigFlow()
    flow.hass = SimpleNamespace()

    result = asyncio.run(flow.async_step_zone2())
    labels = _option_labels(config_flow._zone_trigger_options("level2", "zone2"))

    assert _schema_default(result, "level") == "level2"
    assert labels
    assert all("(Zone 2 / Level 2" in label for label in labels)
    assert all("Level 1" not in label for label in labels)


def test_each_zone_exposes_both_level_choices_and_preserves_explicit_selection():
    config_flow = _load_config_flow_module()
    flow = config_flow.HumidityIntelligenceConfigFlow()
    flow.hass = SimpleNamespace()

    zone1_form = asyncio.run(flow.async_step_zone1())
    zone2_form = asyncio.run(flow.async_step_zone2())
    asyncio.run(
        flow.async_step_zone1(
            {
                "enabled": True,
                "level": "level2",
                "rooms": [],
                "triggers": [],
                "outputs": [],
            }
        )
    )
    asyncio.run(
        flow.async_step_zone2(
            {
                "enabled": True,
                "level": "level1",
                "rooms": [],
                "triggers": [],
                "outputs": [],
            }
        )
    )

    assert _schema_select_values(zone1_form, "level") == ["level1", "level2"]
    assert _schema_select_values(zone2_form, "level") == ["level1", "level2"]
    assert flow._data["zones"]["zone1"]["level"] == "level2"
    assert flow._data["zones"]["zone2"]["level"] == "level1"


def test_options_new_zone2_defaults_to_level2_and_preserves_trigger_ownership():
    config_flow = _load_config_flow_module()
    entry = SimpleNamespace(
        data={
            "telemetry": [
                {
                    "entity_id": "sensor.bedroom_humidity",
                    "sensor_type": "humidity",
                    "level": "level2",
                    "room": "Bedroom",
                }
            ],
            "zones": {},
        },
        options={},
    )
    flow = config_flow.HumidityIntelligenceOptionsFlow(entry)
    flow.hass = SimpleNamespace()
    flow._pending_zone_key = "zone2"

    form = asyncio.run(flow.async_step_options_zone_edit())
    labels = _option_labels(config_flow._zone_trigger_options("level2", "zone2"))
    saved = asyncio.run(
        flow.async_step_options_zone_edit(
            {
                "enabled": True,
                "rooms": ["Bedroom"],
                "triggers": ["humidity_high"],
                "outputs": ["fan.zone2"],
            }
        )
    )

    assert _schema_default(form, "level") == "level2"
    assert all("(Zone 2 / Level 2" in label for label in labels)
    assert saved["step_id"] == "options_zones"
    assert flow._options["zones"]["zone2"]["level"] == "level2"
    assert flow._options["zones"]["zone2"]["triggers"] == ["humidity_high"]


def test_frontend_dependency_page_excludes_drift_helper_status_and_keeps_card_deps_truthful():
    config_flow = _load_config_flow_module()
    const = sys.modules[f"{PKG}.const"]
    strings = json.loads((ROOT / "strings.json").read_text())
    translations = json.loads((ROOT / "translations" / "en.json").read_text())

    dependency_source = (ROOT / "config_flow.py").read_text().split(
        "async def _render_dependency_status", 1
    )[1].split("def _entry_section", 1)[0]
    dependency_names = [dependency["name"] for dependency in const.DEPENDENCIES]
    generated_card_text = "\n".join(
        (ROOT / path).read_text()
        for path in ("ui/cards/v1_mobile.yaml", "ui/cards/v2_mobile.yaml", "ui/cards/v2_tablet.yaml")
    )

    assert "humidity_drift_dependency_status" not in dependency_source
    assert "_render_drift_statistics_status" not in dependency_source
    for payload in (strings, translations):
        setup_description = payload["config"]["step"]["dependencies"]["description"]
        options_description = payload["options"]["step"]["options_dependencies"]["description"]
        assert "House Humidity Mean 7d" not in setup_description
        assert "House Humidity Mean 7d" not in options_description
        assert "drift statistics helper status" not in setup_description
        assert "drift statistics helper status" not in options_description

    assert "mod-card" in dependency_names
    assert "type: custom:mod-card" in generated_card_text
    assert "bubble-card" not in dependency_names
    assert "custom:bubble-card" not in generated_card_text


def test_walkthrough_placeholders_are_supplied_by_config_and_options_flow_results():
    config_flow = _load_config_flow_module()
    walkthrough_url = config_flow.CONFIGURATION_WALKTHROUGH_URL

    setup_flow = config_flow.HumidityIntelligenceConfigFlow()
    setup_flow.hass = SimpleNamespace(data={})
    dependencies = asyncio.run(setup_flow.async_step_dependencies())
    ui_install = asyncio.run(setup_flow.async_step_ui_install())

    entry = SimpleNamespace(data={}, options={})
    options_flow = config_flow.HumidityIntelligenceOptionsFlow(entry)
    options_flow.hass = SimpleNamespace(data={})
    options_dependencies = asyncio.run(options_flow.async_step_options_dependencies())

    for result in (dependencies, ui_install, options_dependencies):
        placeholders = result["description_placeholders"]
        assert placeholders["walkthrough_url"] == walkthrough_url


def test_setup_surfaces_link_to_configuration_walkthrough():
    config_source = (ROOT / "config_flow.py").read_text()
    strings = json.loads((ROOT / "strings.json").read_text())
    translations = json.loads((ROOT / "translations" / "en.json").read_text())
    walkthrough_url = "https://github.com/senyo888/humidity-intelligence/wiki/Configuration-Walkthrough"

    for payload in (strings, translations):
        setup_description = payload["config"]["step"]["dependencies"]["description"]
        options_description = payload["options"]["step"]["options_dependencies"]["description"]
        ui_install_description = payload["config"]["step"]["ui_install"]["description"]

        assert "Configuration Walkthrough" in setup_description
        assert "{walkthrough_url}" in setup_description
        assert walkthrough_url not in setup_description
        assert "Configuration Walkthrough" in options_description
        assert "{walkthrough_url}" in options_description
        assert walkthrough_url not in options_description
        assert "Next step: Configuration Walkthrough" in ui_install_description
        assert "{walkthrough_url}" in ui_install_description
        assert walkthrough_url not in ui_install_description

    assert walkthrough_url in config_source
    assert config_source.count('"walkthrough_url": CONFIGURATION_WALKTHROUGH_URL') == 3


def test_setup_gates_flattens_advanced_section_and_preserves_visible_values():
    config_flow = _load_config_flow_module()
    flow = config_flow.HumidityIntelligenceConfigFlow()
    flow.hass = SimpleNamespace()

    result = asyncio.run(
        flow.async_step_gates(
            {
                "enable_time_gate": True,
                "start_time": "07:30",
                "end_time": "21:15",
                "outside_action": "pause",
                "alert_only_mode": True,
                "target_profile": "custom",
                "temperature_comfort_mode": "custom",
                "enable_presence_gate": False,
                "presence_entities": [],
                "show_advanced_options": {
                    "engine_interval_minutes": 9,
                    "auto_refresh_ui_on_startup": False,
                    "show_output_entity_details": True,
                    "custom_target_low": 42.5,
                    "custom_target_high": 58.5,
                    "temperature_comfort_custom_low": 18.5,
                    "temperature_comfort_custom_high": 22.5,
                },
            }
        )
    )

    assert result["step_id"] == "telemetry"
    assert flow._data["time_gate"] == {
        "enabled": True,
        "start": "07:30",
        "end": "21:15",
        "outside_action": "pause",
    }
    assert flow._data["alert_only_mode"] is True
    assert flow._data["target_profile"] == "custom"
    assert flow._data["temperature_comfort_mode"] == "custom"
    assert flow._data["presence_gate"] == {
        "enabled": False,
        "entities": [],
        "present_states": [],
        "away_states": [],
    }
    assert flow._data["engine_interval_minutes"] == 9
    assert flow._data["auto_refresh_ui_on_startup"] is False
    assert flow._data["show_output_entity_details"] is True
    assert flow._data["custom_target_low"] == 42.5
    assert flow._data["custom_target_high"] == 58.5
    assert flow._data["temperature_comfort_custom_low"] == 18.5
    assert flow._data["temperature_comfort_custom_high"] == 22.5


def test_options_gates_flattens_advanced_section_and_preserves_visible_values():
    config_flow = _load_config_flow_module()
    entry = SimpleNamespace(data={}, options={})
    flow = config_flow.HumidityIntelligenceOptionsFlow(entry)
    flow.hass = SimpleNamespace()

    result = asyncio.run(
        flow.async_step_options_gates(
            {
                "enable_time_gate": True,
                "start_time": "06:45",
                "end_time": "23:00",
                "outside_action": "safe_state",
                "alert_only_mode": True,
                "target_profile": "winter",
                "enable_presence_gate": False,
                "presence_entities": [],
                "show_advanced_options": {
                    "engine_interval_minutes": 11,
                    "auto_refresh_ui_on_startup": False,
                    "show_output_entity_details": False,
                    "custom_target_low": 44.0,
                    "custom_target_high": 59.0,
                },
            }
        )
    )

    assert result["step_id"] == "init"
    assert flow._options["time_gate"] == {
        "enabled": True,
        "start": "06:45",
        "end": "23:00",
        "outside_action": "safe_state",
    }
    assert flow._options["presence_gate"] == {
        "enabled": False,
        "entities": [],
        "present_states": [],
        "away_states": [],
    }
    assert flow._options["alert_only_mode"] is True
    assert flow._options["target_profile"] == "winter"
    assert flow._options["engine_interval_minutes"] == 11
    assert flow._options["auto_refresh_ui_on_startup"] is False
    assert flow._options["show_output_entity_details"] is False
    assert flow._options["custom_target_low"] == 44.0
    assert flow._options["custom_target_high"] == 59.0


def test_options_thresholds_preserve_existing_zones_and_ignore_missing_zone_thresholds():
    config_flow = _load_config_flow_module()
    zone1 = {
        "enabled": True,
        "level": "level1",
        "rooms": ["Kitchen"],
        "triggers": ["humidity_high"],
        "outputs": ["fan.kitchen"],
        "thresholds": {
            "humidity_high": 6,
            "condensation_risk": 3,
            "mould_risk": 1,
            "air_quality_bad": 72,
        },
    }
    entry = SimpleNamespace(
        data={
            "zones": {"zone1": dict(zone1)},
            "temperature_comfort_mode": "auto",
            "temperature_comfort_custom_low": 19.5,
            "temperature_comfort_custom_high": 21.0,
        },
        options={},
    )
    flow = config_flow.HumidityIntelligenceOptionsFlow(entry)
    flow.hass = SimpleNamespace()

    form = asyncio.run(flow.async_step_options_thresholds())
    result = asyncio.run(
        flow.async_step_options_thresholds(
            {
                "temperature_comfort_mode": "custom",
                "show_advanced_options": {
                    "temperature_comfort_custom_low": 18.0,
                    "temperature_comfort_custom_high": 22.0,
                },
            }
        )
    )

    assert result["step_id"] == "init"
    assert _schema_has_field(form, "temperature_comfort_mode")
    assert _advanced_schema_has_field(form, "zone1_threshold_humidity_high")
    assert not _advanced_schema_has_field(form, "zone2_threshold_humidity_high")
    assert flow._options["temperature_comfort_mode"] == "custom"
    assert flow._options["temperature_comfort_custom_low"] == 18.0
    assert flow._options["temperature_comfort_custom_high"] == 22.0
    assert set(flow._options["zones"]) == {"zone1"}
    assert flow._options["zones"]["zone1"]["thresholds"] == zone1["thresholds"]


def test_setup_alert_add_flattens_advanced_section_and_preserves_visible_values():
    config_flow = _load_config_flow_module()
    flow = config_flow.HumidityIntelligenceConfigFlow()
    flow.hass = SimpleNamespace()
    flow._telemetry = _base_telemetry()

    result = asyncio.run(
        flow.async_step_alert_add(
            {
                "enabled": False,
                "trigger_type": "humidity_danger",
                "room": "Kitchen",
                "lights": ["light.hi_alert"],
                "show_advanced_options": {
                    "power_entity": "switch.hi_alert_power",
                    "flash_mode": "white",
                    "duration": 45,
                },
            }
        )
    )

    assert result["step_id"] == "alerts"
    assert flow._data["alerts"] == flow._alerts
    assert flow._alerts == [
        {
            "enabled": False,
            "trigger_type": "humidity_danger",
            "threshold": None,
            "room": "Kitchen",
            "lights": ["light.hi_alert"],
            "power_entity": "switch.hi_alert_power",
            "flash_mode": "white",
            "duration": 45,
        }
    ]


def test_options_alert_edit_flattens_advanced_section_and_preserves_visible_values():
    config_flow = _load_config_flow_module()
    entry = SimpleNamespace(
        data={
            "telemetry": _base_telemetry(),
            "alerts": [
                {
                    "enabled": True,
                    "trigger_type": "co_emergency",
                    "threshold": 15,
                    "room": None,
                    "lights": ["light.old_alert"],
                    "power_entity": "switch.old_power",
                    "flash_mode": "red",
                    "duration": 10,
                }
            ],
        },
        options={},
    )
    flow = config_flow.HumidityIntelligenceOptionsFlow(entry)
    flow.hass = SimpleNamespace()
    flow._pending_alert_index = 0

    result = asyncio.run(
        flow.async_step_options_alert_edit(
            {
                "enabled": False,
                "trigger_type": "co_emergency",
                "lights": ["light.new_alert"],
                "show_advanced_options": {
                    "threshold": 25,
                    "power_entity": "switch.new_power",
                    "flash_mode": "white",
                    "duration": 55,
                },
            }
        )
    )

    assert result["step_id"] == "options_alerts"
    assert flow._options["alerts"] == [
        {
            "enabled": False,
            "trigger_type": "co_emergency",
            "threshold": 25,
            "room": None,
            "lights": ["light.new_alert"],
            "power_entity": "switch.new_power",
            "flash_mode": "white",
            "duration": 55,
        }
    ]


if __name__ == "__main__":
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for name, test in tests:
        test()
    print(f"{len(tests)} config-flow sanity checks passed.")
