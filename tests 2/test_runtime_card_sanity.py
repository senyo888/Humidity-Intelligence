"""Regression sanity checks for HI runtime lane ordering and card rendering."""

from __future__ import annotations

import asyncio
import importlib.util
import pathlib
import sys
import tempfile
import types
from types import MethodType, SimpleNamespace


ROOT = pathlib.Path(__file__).resolve().parents[1]
ENTRY_ID = "entry123"
PKG = "hi_testpkg"


def _install_homeassistant_stubs() -> None:
    """Install lightweight Home Assistant stubs into sys.modules."""
    ha = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")
    config_entries = types.ModuleType("homeassistant.config_entries")
    const = types.ModuleType("homeassistant.const")
    exceptions = types.ModuleType("homeassistant.exceptions")
    helpers = types.ModuleType("homeassistant.helpers")
    config_validation = types.ModuleType("homeassistant.helpers.config_validation")
    event = types.ModuleType("homeassistant.helpers.event")
    entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
    voluptuous = types.ModuleType("voluptuous")

    class HomeAssistant:
        pass

    class ServiceCall:
        def __init__(self, data=None):
            self.data = data or {}

    class ConfigEntry:
        pass

    class HomeAssistantError(Exception):
        pass

    class UnitOfTemperature:
        CELSIUS = "°C"
        FAHRENHEIT = "°F"

    class Invalid(Exception):
        pass

    class _SchemaKey:
        def __init__(self, key, default=None):
            self.key = key
            self.default = default

        def __hash__(self):
            try:
                return hash((self.key, self.default))
            except TypeError:
                return hash((self.key, repr(self.default)))

    class Schema:
        def __init__(self, schema):
            self.schema = schema

        def __call__(self, value):
            return value

    def _ensure_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    def _coerce(kind):
        return lambda value: kind(value)

    def _range(min=None, max=None):
        def validate(value):
            if min is not None and value < min:
                raise Invalid("value below range")
            if max is not None and value > max:
                raise Invalid("value above range")
            return value

        return validate

    def _all(*validators):
        def validate(value):
            for validator in validators:
                value = validator(value)
            return value

        return validate

    def _any(*validators):
        def validate(value):
            for validator in validators:
                if validator is None and value is None:
                    return value
                if callable(validator):
                    try:
                        return validator(value)
                    except Exception:
                        continue
            raise Invalid("no validator accepted value")

        return validate

    def async_track_state_change_event(*args, **kwargs):
        return lambda: None

    def async_track_time_interval(*args, **kwargs):
        return lambda: None

    core.HomeAssistant = HomeAssistant
    core.ServiceCall = ServiceCall
    config_entries.ConfigEntry = ConfigEntry
    exceptions.HomeAssistantError = HomeAssistantError
    const.UnitOfTemperature = UnitOfTemperature
    const.PERCENTAGE = "%"
    config_validation.entity_id = str
    config_validation.entity_ids = _ensure_list
    config_validation.ensure_list = _ensure_list
    config_validation.string = str
    event.async_track_state_change_event = async_track_state_change_event
    event.async_track_time_interval = async_track_time_interval
    entity_registry.async_get = lambda hass: None
    voluptuous.Schema = Schema
    voluptuous.Optional = _SchemaKey
    voluptuous.Required = _SchemaKey
    voluptuous.Invalid = Invalid
    voluptuous.Coerce = _coerce
    voluptuous.Range = _range
    voluptuous.All = _all
    voluptuous.Any = _any

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.core"] = core
    sys.modules["homeassistant.config_entries"] = config_entries
    sys.modules["homeassistant.const"] = const
    sys.modules["homeassistant.exceptions"] = exceptions
    sys.modules["homeassistant.helpers"] = helpers
    sys.modules["homeassistant.helpers.config_validation"] = config_validation
    sys.modules["homeassistant.helpers.event"] = event
    sys.modules["homeassistant.helpers.entity_registry"] = entity_registry
    sys.modules["voluptuous"] = voluptuous


def _install_package_scaffold() -> None:
    """Create importable package namespace used for file-based module loading."""
    pkg = types.ModuleType(PKG)
    pkg.__path__ = [str(ROOT)]
    sys.modules[PKG] = pkg

    for sub in ("automations", "ui", "helpers"):
        mod = types.ModuleType(f"{PKG}.{sub}")
        mod.__path__ = [str(ROOT / sub)]
        sys.modules[f"{PKG}.{sub}"] = mod

    services = types.ModuleType(f"{PKG}.services")
    services.SERVICE_FLASH_LIGHTS = "flash_lights"
    sys.modules[f"{PKG}.services"] = services


def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_target_modules():
    _install_homeassistant_stubs()
    _install_package_scaffold()

    _load_module(f"{PKG}.const", ROOT / "const.py")
    engine_mod = _load_module(f"{PKG}.automations.engine", ROOT / "automations" / "engine.py")
    register_mod = _load_module(f"{PKG}.ui.register", ROOT / "ui" / "register.py")
    return engine_mod, register_mod


def _load_services_module():
    _install_homeassistant_stubs()
    _install_package_scaffold()
    _load_module(f"{PKG}.const", ROOT / "const.py")
    return _load_module(f"{PKG}.services", ROOT / "services.py")


class _FakeState:
    def __init__(self, state, attrs=None):
        self.state = str(state)
        self.attributes = attrs or {}


class _FakeStates:
    def __init__(self, values):
        self._values = dict(values)

    def get(self, entity_id):
        return self._values.get(entity_id)

    def is_state(self, entity_id, state):
        st = self._values.get(entity_id)
        return bool(st and st.state == state)


class _FakeServices:
    def __init__(self):
        self.calls = []

    def has_service(self, domain, service):
        return True

    async def async_call(self, domain, service, data=None, blocking=False):
        self.calls.append((domain, service, dict(data or {}), bool(blocking)))


class _FlashServiceRegistry:
    def __init__(self, states):
        self.states = states
        self.calls = []
        self.handlers = {}

    def has_service(self, domain, service):
        return True

    def async_register(self, domain, service, handler, schema=None):
        self.handlers[(domain, service)] = handler

    async def async_call(self, domain, service, data=None, blocking=False):
        payload = dict(data or {})
        self.calls.append((domain, service, payload, bool(blocking)))
        if domain == "light":
            entity_id = payload.get("entity_id")
            current = self.states.get(entity_id)
            attrs = dict(current.attributes) if current is not None else {}
            if service == "turn_on":
                attrs.update({key: value for key, value in payload.items() if key != "entity_id"})
                self.states._values[entity_id] = _FakeState("on", attrs)
            elif service == "turn_off":
                self.states._values[entity_id] = _FakeState("off", attrs)


class _FlashHass:
    def __init__(self, states):
        self.states = _FakeStates(states)
        self.services = _FlashServiceRegistry(self.states)
        self.data = {}


class _FakeBool:
    def __init__(self, initial=False):
        self.is_on = bool(initial)
        self.on_calls = 0
        self.off_calls = 0

    async def async_turn_on(self):
        self.on_calls += 1
        self.is_on = True

    async def async_turn_off(self):
        self.off_calls += 1
        self.is_on = False


class _FakeTimer:
    def __init__(self):
        self.native_value = "idle"

    async def async_start(self, duration):
        self.native_value = "active"

    async def async_cancel(self):
        self.native_value = "idle"


class _FakeConfigEntries:
    def __init__(self, entry):
        self._entry = entry

    def async_get_entry(self, entry_id):
        return self._entry if entry_id == self._entry.entry_id else None

    def async_entries(self, _domain):
        return [self._entry]


class _FakeRegistry:
    def async_get_entity_id(self, domain, _integration, unique_id):
        suffix = unique_id.split("_", 2)[-1]
        return f"{domain}.hi_{suffix}"


class _FakeHass:
    def __init__(self, entry, states):
        self.services = _FakeServices()
        self.states = _FakeStates(states)
        self.config_entries = _FakeConfigEntries(entry)
        self.data = {
            "humidity_intelligence": {
                entry.entry_id: {
                    "hi_input_booleans": {
                        "air_control_enabled": _FakeBool(True),
                        "air_control_manual_override": _FakeBool(False),
                        "air_isolate_fan_outputs": _FakeBool(False),
                        "air_isolate_humidifier_outputs": _FakeBool(False),
                        "air_co_emergency_active": _FakeBool(False),
                        "air_downstairs_humidifier_active": _FakeBool(False),
                        "air_upstairs_humidifier_active": _FakeBool(False),
                        "air_aq_downstairs_active": _FakeBool(False),
                        "air_aq_upstairs_active": _FakeBool(False),
                        "air_alert_1_active": _FakeBool(False),
                        "air_alert_2_active": _FakeBool(False),
                        "air_alert_3_active": _FakeBool(False),
                        "air_alert_4_active": _FakeBool(False),
                        "air_alert_5_active": _FakeBool(False),
                    },
                    "hi_timers": {
                        "air_control_pause": _FakeTimer(),
                        "air_aq_downstairs_run": _FakeTimer(),
                        "air_aq_upstairs_run": _FakeTimer(),
                    },
                }
            }
        }

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class _DumpCardsConfig:
    def __init__(self, root):
        self._root = pathlib.Path(root)

    def path(self, filename):
        return str(self._root / filename)


class _DumpCardsConfigEntries:
    def __init__(self, entries):
        self._entries = list(entries)

    def async_get_entry(self, entry_id):
        for entry in self._entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def async_entries(self, _domain):
        return list(self._entries)


class _DumpCardsHass:
    def __init__(self, tmpdir, entries, cards_by_entry):
        self.config = _DumpCardsConfig(tmpdir)
        self.config_entries = _DumpCardsConfigEntries(entries)
        self.data = {
            "humidity_intelligence": {
                entry_id: {"cards": cards}
                for entry_id, cards in cards_by_entry.items()
            }
        }

    async def async_add_executor_job(self, func, *args):
        return func(*args)


def _wrap_async_method(obj, method_name: str, trace: list[str]) -> None:
    original = getattr(obj, method_name)

    async def wrapped(self, *args, **kwargs):
        if method_name == "_handle_zone_by_key" and args:
            trace.append(f"{method_name}:{args[0]}")
        else:
            trace.append(method_name)
        return await original(*args, **kwargs)

    setattr(obj, method_name, MethodType(wrapped, obj))


def _base_entry_data():
    return {
        "target_profile": "winter",
        "telemetry": [
            {"entity_id": "sensor.kitchen_h", "sensor_type": "humidity", "level": "level1", "room": "Kitchen"},
            {"entity_id": "sensor.hall_h", "sensor_type": "humidity", "level": "level1", "room": "Hallway"},
            {"entity_id": "sensor.bed_h", "sensor_type": "humidity", "level": "level2", "room": "Bedroom"},
            {"entity_id": "sensor.kitchen_t", "sensor_type": "temperature", "level": "level1", "room": "Kitchen"},
            {"entity_id": "sensor.hall_t", "sensor_type": "temperature", "level": "level1", "room": "Hallway"},
            {"entity_id": "sensor.bed_t", "sensor_type": "temperature", "level": "level2", "room": "Bedroom"},
            {"entity_id": "sensor.l1_iaq", "sensor_type": "iaq", "level": "level1", "room": "Hallway"},
            {"entity_id": "sensor.co_val", "sensor_type": "co", "level": "level1", "room": "Kitchen"},
        ],
        "zones": {
            "zone1": {
                "enabled": True,
                "level": "level1",
                "rooms": ["Kitchen"],
                "outputs": ["fan.zone1"],
                "triggers": ["humidity_high"],
                "thresholds": {"humidity_high": 5},
                "ui_label": "Cooking",
            },
            "zone2": {
                "enabled": True,
                "level": "level2",
                "rooms": ["Bedroom"],
                "outputs": ["fan.zone2"],
                "triggers": ["humidity_high"],
                "thresholds": {"humidity_high": 2},
                "ui_label": "Bathroom",
            },
        },
        "humidifiers": {
            "level1": {"enabled": True, "outputs": ["humidifier.l1"], "band_adjust": 0},
        },
        "aq": {
            "level1": {
                "enabled": True,
                "outputs": ["fan.aq1"],
                "triggers": ["iaq_bad"],
                "thresholds": {"iaq_bad": 75},
                "output_level": 66,
                "run_duration": 10,
            }
        },
        "alerts": [
            {
                "enabled": True,
                "trigger_type": "humidity_danger",
                "room": "Kitchen",
                "power_entity": "switch.alert_power",
                "lights": ["light.alert"],
                "flash_mode": "red",
                "duration": 10,
            }
        ],
    }


async def _run_runtime_assertions(engine_mod) -> None:
    HIAutomationEngine = engine_mod.HIAutomationEngine

    # CO emergency preemption: must short-circuit lower lanes.
    entry = SimpleNamespace(entry_id=ENTRY_ID, data=_base_entry_data(), options={})
    hass_co = _FakeHass(
        entry,
        {
            "sensor.kitchen_h": _FakeState(75),
            "sensor.hall_h": _FakeState(60),
            "sensor.bed_h": _FakeState(68),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(40),
            "sensor.co_val": _FakeState(16),
        },
    )
    engine_co = HIAutomationEngine(hass_co, entry)
    co_trace = []
    for method in ("_handle_alerts", "_handle_humidifiers", "_handle_zone_by_key", "_handle_aq"):
        _wrap_async_method(engine_co, method, co_trace)
    await engine_co._evaluate()

    assert co_trace == []
    assert hass_co.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "co_emergency"

    # CO emergency should respect configured threshold, but use existing configured
    # ventilation outputs instead of alert-specific output overrides.
    entry_co_cfg_data = _base_entry_data()
    entry_co_cfg_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "co_emergency",
            "threshold": 20,
            "outputs": ["fan.legacy_co_only"],
            "lights": ["light.alert"],
            "power_entity": "switch.alert_power",
            "flash_mode": "red",
            "duration": 10,
        }
    ]
    entry_co_cfg = SimpleNamespace(entry_id=ENTRY_ID, data=entry_co_cfg_data, options={})
    hass_co_cfg = _FakeHass(
        entry_co_cfg,
        {
            "sensor.kitchen_h": _FakeState(60),
            "sensor.hall_h": _FakeState(60),
            "sensor.bed_h": _FakeState(60),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(40),
            "sensor.co_val": _FakeState(21),  # above configured CO threshold (20)
        },
    )
    engine_co_cfg = HIAutomationEngine(hass_co_cfg, entry_co_cfg)
    await engine_co_cfg._evaluate()
    assert hass_co_cfg.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "co_emergency"
    co_percentage_outputs = {
        data.get("entity_id")
        for domain, service, data, _ in hass_co_cfg.services.calls
        if domain == "fan" and service == "set_percentage"
    }
    assert {"fan.zone1", "fan.zone2", "fan.aq1"} <= co_percentage_outputs
    assert "fan.legacy_co_only" not in co_percentage_outputs

    # Safe-threshold enforcement: CO emergency threshold is clamped to minimum safe value.
    # With threshold configured as 1 and CO at 8, emergency should not trigger.
    entry_co_guard_data = _base_entry_data()
    entry_co_guard_data["zones"]["zone1"]["enabled"] = False
    entry_co_guard_data["zones"]["zone2"]["enabled"] = False
    entry_co_guard_data["aq"] = {}
    entry_co_guard_data["humidifiers"] = {}
    entry_co_guard_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "co_emergency",
            "threshold": 1,  # below safe floor, should clamp up.
            "lights": ["light.alert"],
            "power_entity": "switch.alert_power",
            "flash_mode": "red",
            "duration": 10,
        }
    ]
    entry_co_guard = SimpleNamespace(entry_id=ENTRY_ID, data=entry_co_guard_data, options={})
    hass_co_guard = _FakeHass(
        entry_co_guard,
        {
            "sensor.kitchen_h": _FakeState(60),
            "sensor.hall_h": _FakeState(60),
            "sensor.bed_h": _FakeState(60),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(40),
            "sensor.co_val": _FakeState(8),
        },
    )
    engine_co_guard = HIAutomationEngine(hass_co_guard, entry_co_guard)
    await engine_co_guard._evaluate()
    assert hass_co_guard.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") != "co_emergency"

    # Alert lane is now exclusive: no humidifier/zone/AQ handling should run.
    entry2 = SimpleNamespace(entry_id=ENTRY_ID, data=_base_entry_data(), options={})
    hass = _FakeHass(
        entry2,
        {
            "sensor.kitchen_h": _FakeState(90),
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(45),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(70),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine = HIAutomationEngine(hass, entry2)
    trace = []
    for method in ("_handle_alerts", "_handle_humidifiers", "_handle_zone_by_key", "_handle_aq"):
        _wrap_async_method(engine, method, trace)
    await engine._evaluate()

    assert trace == ["_handle_alerts"]
    assert "_handle_aq" not in trace

    calls = hass.services.calls
    assert any(domain == "humidity_intelligence" and service == "flash_lights" for domain, service, *_ in calls)
    assert not hass.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_downstairs_humidifier_active"].is_on
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone1"
        and data.get("percentage") == 100
        for domain, service, data, _ in calls
    )
    assert not any(
        domain == "fan" and service == "set_percentage" and data.get("entity_id") in {"fan.zone2", "fan.aq1"}
        for domain, service, data, _ in calls
    )

    # Runtime mode priority should prefer alert while alert lane is active.
    assert hass.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "alert"
    assert hass.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_alert_1_active"].is_on
    alert_switch = hass.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_alert_1_active"]
    assert alert_switch.on_calls == 1
    assert alert_switch.off_calls == 0
    alert_reason = hass.data["humidity_intelligence"][ENTRY_ID].get("runtime_reason", "")
    assert "Alert response is active" in alert_reason
    assert "resolved zone" in alert_reason or "Degraded mode" in alert_reason
    await engine._evaluate()
    assert alert_switch.on_calls == 1
    assert alert_switch.off_calls == 0
    hass.states._values["sensor.kitchen_h"] = _FakeState(45)
    hass.states._values["sensor.hall_h"] = _FakeState(45)
    hass.states._values["sensor.bed_h"] = _FakeState(45)
    hass.states._values["sensor.l1_iaq"] = _FakeState(90)
    await engine._evaluate()
    assert alert_switch.on_calls == 1
    assert alert_switch.off_calls == 1
    assert hass.data["humidity_intelligence"][ENTRY_ID].get("active_alert_context") == "None"
    await engine._evaluate()
    assert alert_switch.on_calls == 1
    assert alert_switch.off_calls == 1

    # Room-scoped humidity danger alert should only trigger for the selected room.
    entry_room_alert_data = _base_entry_data()
    entry_room_alert_data["aq"] = {}
    entry_room_alert_data["humidifiers"] = {}
    entry_room_alert_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "humidity_danger",
            "room": "Kitchen",
            "lights": ["light.alert"],
            "duration": 10,
        }
    ]
    entry_room_alert = SimpleNamespace(entry_id=ENTRY_ID, data=entry_room_alert_data, options={})
    hass_room_alert = _FakeHass(
        entry_room_alert,
        {
            "sensor.kitchen_h": _FakeState(82),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_room_alert = HIAutomationEngine(hass_room_alert, entry_room_alert)
    await engine_room_alert._evaluate()
    assert hass_room_alert.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "alert"
    room_alert_reason = hass_room_alert.data["humidity_intelligence"][ENTRY_ID].get("runtime_reason", "")
    assert "Humidity Danger" in room_alert_reason
    assert "Kitchen" in room_alert_reason
    assert "sensor.kitchen_h" in room_alert_reason
    assert "resolved zone: Zone 1" in room_alert_reason
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone1"
        and data.get("percentage") == 100
        for domain, service, data, _ in hass_room_alert.services.calls
    )

    entry_zone_alert_data = _base_entry_data()
    entry_zone_alert_data["aq"] = {}
    entry_zone_alert_data["humidifiers"] = {}
    entry_zone_alert_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "humidity_danger",
            "room": "Kitchen",
            "lights": [],
        }
    ]
    entry_zone_alert = SimpleNamespace(entry_id=ENTRY_ID, data=entry_zone_alert_data, options={})
    hass_zone_alert = _FakeHass(
        entry_zone_alert,
        {
            "sensor.kitchen_h": _FakeState(72),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(45),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_zone_alert = HIAutomationEngine(hass_zone_alert, entry_zone_alert)
    await engine_zone_alert._evaluate()
    assert hass_zone_alert.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "alert"
    assert hass_zone_alert.data["humidity_intelligence"][ENTRY_ID].get("active_alert_context") == (
        "Humidity Danger · Kitchen · Zone 1 · 72.0% >= 62% threshold"
    )
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone1"
        and data.get("percentage") == 100
        for domain, service, data, _ in hass_zone_alert.services.calls
    )

    # New v2.0.4 risk alerts should bind to the originating room's zone boost.
    entry_condensation_risk_data = _base_entry_data()
    entry_condensation_risk_data["target_profile"] = "custom"
    entry_condensation_risk_data["custom_target_low"] = 40
    entry_condensation_risk_data["custom_target_high"] = 79
    entry_condensation_risk_data["aq"] = {}
    entry_condensation_risk_data["humidifiers"] = {}
    entry_condensation_risk_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "condensation_risk",
            "room": "Bedroom",
            "lights": [],
        }
    ]
    entry_condensation_risk = SimpleNamespace(
        entry_id=ENTRY_ID,
        data=entry_condensation_risk_data,
        options={},
    )
    hass_condensation_risk = _FakeHass(
        entry_condensation_risk,
        {
            "sensor.kitchen_h": _FakeState(45),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(77),
            "sensor.kitchen_t": _FakeState(22),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(20),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_condensation_risk = HIAutomationEngine(hass_condensation_risk, entry_condensation_risk)
    await engine_condensation_risk._evaluate()
    assert hass_condensation_risk.data["humidity_intelligence"][ENTRY_ID].get("active_alert_context") == (
        "Condensation Risk · Bedroom · Zone 2"
    )
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone2"
        and data.get("percentage") == 100
        for domain, service, data, _ in hass_condensation_risk.services.calls
    )

    # Alert hierarchy should beat zone priority: mould risk in Zone 2 outranks
    # condensation risk in Zone 1.
    entry_alert_hierarchy_data = _base_entry_data()
    entry_alert_hierarchy_data["target_profile"] = "custom"
    entry_alert_hierarchy_data["custom_target_low"] = 40
    entry_alert_hierarchy_data["custom_target_high"] = 79
    entry_alert_hierarchy_data["aq"] = {}
    entry_alert_hierarchy_data["humidifiers"] = {}
    entry_alert_hierarchy_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "condensation_risk",
            "room": "Kitchen",
            "lights": [],
        },
        {
            "enabled": True,
            "trigger_type": "mould_risk",
            "room": "Bedroom",
            "lights": [],
        },
    ]
    entry_alert_hierarchy = SimpleNamespace(
        entry_id=ENTRY_ID,
        data=entry_alert_hierarchy_data,
        options={},
    )
    hass_alert_hierarchy = _FakeHass(
        entry_alert_hierarchy,
        {
            "sensor.kitchen_h": _FakeState(77),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(83),
            "sensor.kitchen_t": _FakeState(20),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(20),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_alert_hierarchy = HIAutomationEngine(hass_alert_hierarchy, entry_alert_hierarchy)
    await engine_alert_hierarchy._evaluate()
    hierarchy_data = hass_alert_hierarchy.data["humidity_intelligence"][ENTRY_ID]
    assert hierarchy_data.get("active_alert_context") == "Mould Risk · Bedroom · Zone 2"
    assert "Conflict detected" in hierarchy_data.get("runtime_reason_full", "")
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone2"
        and data.get("percentage") == 100
        for domain, service, data, _ in hass_alert_hierarchy.services.calls
    )

    # Same-priority alerts should resolve by zone priority: Zone 1 before Zone 2.
    entry_zone_priority_data = _base_entry_data()
    entry_zone_priority_data["target_profile"] = "custom"
    entry_zone_priority_data["custom_target_low"] = 40
    entry_zone_priority_data["custom_target_high"] = 79
    entry_zone_priority_data["aq"] = {}
    entry_zone_priority_data["humidifiers"] = {}
    entry_zone_priority_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "mould_risk",
            "room": "Kitchen",
            "lights": [],
        },
        {
            "enabled": True,
            "trigger_type": "mould_risk",
            "room": "Bedroom",
            "lights": [],
        },
    ]
    entry_zone_priority = SimpleNamespace(entry_id=ENTRY_ID, data=entry_zone_priority_data, options={})
    hass_zone_priority = _FakeHass(
        entry_zone_priority,
        {
            "sensor.kitchen_h": _FakeState(83),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(83),
            "sensor.kitchen_t": _FakeState(20),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(20),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_zone_priority = HIAutomationEngine(hass_zone_priority, entry_zone_priority)
    await engine_zone_priority._evaluate()
    assert hass_zone_priority.data["humidity_intelligence"][ENTRY_ID].get("active_alert_context") == (
        "Mould Risk · Kitchen · Zone 1"
    )
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone1"
        and data.get("percentage") == 100
        for domain, service, data, _ in hass_zone_priority.services.calls
    )

    # Unknown/unavailable source telemetry should not trigger blind boost.
    entry_alert_degraded_data = _base_entry_data()
    entry_alert_degraded_data["aq"] = {}
    entry_alert_degraded_data["humidifiers"] = {}
    entry_alert_degraded_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "condensation_risk",
            "room": "Bedroom",
            "lights": [],
        }
    ]
    entry_alert_degraded = SimpleNamespace(entry_id=ENTRY_ID, data=entry_alert_degraded_data, options={})
    hass_alert_degraded = _FakeHass(
        entry_alert_degraded,
        {
            "sensor.kitchen_h": _FakeState(45),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState("unavailable"),
            "sensor.kitchen_t": _FakeState(22),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState("unknown"),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_alert_degraded = HIAutomationEngine(hass_alert_degraded, entry_alert_degraded)
    await engine_alert_degraded._evaluate()
    degraded_data = hass_alert_degraded.data["humidity_intelligence"][ENTRY_ID]
    assert degraded_data.get("runtime_mode") != "alert"
    assert degraded_data.get("active_alert_context") == "None"
    assert not any(
        domain == "fan" and service == "set_percentage"
        for domain, service, _data, _ in hass_alert_degraded.services.calls
    )

    # Disabled alert handling should skip non-CO internally calculated alerts.
    entry_alert_disabled_data = _base_entry_data()
    entry_alert_disabled_data["alert_handling_enabled"] = False
    entry_alert_disabled = SimpleNamespace(entry_id=ENTRY_ID, data=entry_alert_disabled_data, options={})
    hass_alert_disabled = _FakeHass(
        entry_alert_disabled,
        {
            "sensor.kitchen_h": _FakeState(90),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(45),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_alert_disabled = HIAutomationEngine(hass_alert_disabled, entry_alert_disabled)
    alert_active, alert_details = await engine_alert_disabled._handle_alerts()
    assert alert_active is False
    assert alert_details == []

    # Unmapped alert candidates should be reported, skipped for boost, and
    # allow the next eligible lane to run.
    entry_unmapped_alert_data = _base_entry_data()
    entry_unmapped_alert_data["zones"]["zone1"]["rooms"] = ["Hallway"]
    entry_unmapped_alert_data["zones"]["zone2"]["rooms"] = ["Bedroom"]
    entry_unmapped_alert_data["humidifiers"] = {}
    entry_unmapped_alert_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "humidity_danger",
            "room": "Kitchen",
            "lights": [],
        }
    ]
    entry_unmapped_alert = SimpleNamespace(
        entry_id=ENTRY_ID,
        data=entry_unmapped_alert_data,
        options={},
    )
    hass_unmapped_alert = _FakeHass(
        entry_unmapped_alert,
        {
            "sensor.kitchen_h": _FakeState(90),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(45),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(70),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_unmapped_alert = HIAutomationEngine(hass_unmapped_alert, entry_unmapped_alert)
    await engine_unmapped_alert._evaluate()
    unmapped_data = hass_unmapped_alert.data["humidity_intelligence"][ENTRY_ID]
    unmapped_reason = unmapped_data.get("runtime_reason_full", "")
    assert unmapped_data.get("runtime_mode") == "air_quality"
    assert "Skipped alert candidate" in unmapped_reason
    assert "No enabled zone maps room 'Kitchen'" in unmapped_reason
    assert not any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") in {"fan.zone1", "fan.zone2"}
        and data.get("percentage") == 100
        for domain, service, data, _ in hass_unmapped_alert.services.calls
    )

    # Humidity danger with no explicit threshold should use active profile high-risk.
    entry_room_alert_dynamic_data = _base_entry_data()
    entry_room_alert_dynamic_data["aq"] = {}
    entry_room_alert_dynamic_data["humidifiers"] = {}
    entry_room_alert_dynamic_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "humidity_danger",
            "room": "Kitchen",
            "lights": ["light.alert"],
            "duration": 10,
        }
    ]
    entry_room_alert_dynamic = SimpleNamespace(
        entry_id=ENTRY_ID,
        data=entry_room_alert_dynamic_data,
        options={},
    )
    hass_room_alert_dynamic = _FakeHass(
        entry_room_alert_dynamic,
        {
            "sensor.kitchen_h": _FakeState(64),  # winter high-risk default is 62
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_room_alert_dynamic = HIAutomationEngine(hass_room_alert_dynamic, entry_room_alert_dynamic)
    await engine_room_alert_dynamic._evaluate()
    assert hass_room_alert_dynamic.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "alert"
    dynamic_reason = hass_room_alert_dynamic.data["humidity_intelligence"][ENTRY_ID].get("runtime_reason_full", "")
    assert "Threshold source: active profile" in dynamic_reason
    assert "sensor.kitchen_h" in dynamic_reason
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone1"
        and data.get("percentage") == 100
        for domain, service, data, _ in hass_room_alert_dynamic.services.calls
    )
    assert any(
        domain == "humidity_intelligence" and service == "flash_lights"
        for domain, service, *_ in hass_room_alert_dynamic.services.calls
    )
    dynamic_flash_calls = [
        data
        for domain, service, data, _ in hass_room_alert_dynamic.services.calls
        if domain == "humidity_intelligence" and service == "flash_lights"
    ]
    assert dynamic_flash_calls
    assert all(data.get("flash_count") == 10 for data in dynamic_flash_calls)
    assert all("power_entity" not in data for data in dynamic_flash_calls)
    assert all(isinstance(data.get("color"), list) for data in dynamic_flash_calls)
    assert all(len(data.get("color")) == 3 for data in dynamic_flash_calls)
    assert all(
        all(isinstance(channel, int) for channel in data.get("color"))
        for data in dynamic_flash_calls
    )
    assert len(engine_room_alert_dynamic._visual_alert_tasks) == 1
    await engine_room_alert_dynamic._evaluate()
    dynamic_flash_calls_after_repeat_eval = [
        data
        for domain, service, data, _ in hass_room_alert_dynamic.services.calls
        if domain == "humidity_intelligence" and service == "flash_lights"
    ]
    assert len(dynamic_flash_calls_after_repeat_eval) == len(dynamic_flash_calls)
    assert len(engine_room_alert_dynamic._visual_alert_tasks) == 1
    await engine_room_alert_dynamic.async_stop()

    # Alerts without target lights should still activate runtime alert mode,
    # but skip light flash service calls cleanly.
    entry_room_alert_no_lights_data = _base_entry_data()
    entry_room_alert_no_lights_data["aq"] = {}
    entry_room_alert_no_lights_data["humidifiers"] = {}
    entry_room_alert_no_lights_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "humidity_danger",
            "room": "Kitchen",
            "duration": 10,
        }
    ]
    entry_room_alert_no_lights = SimpleNamespace(
        entry_id=ENTRY_ID,
        data=entry_room_alert_no_lights_data,
        options={},
    )
    hass_room_alert_no_lights = _FakeHass(
        entry_room_alert_no_lights,
        {
            "sensor.kitchen_h": _FakeState(82),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_room_alert_no_lights = HIAutomationEngine(
        hass_room_alert_no_lights,
        entry_room_alert_no_lights,
    )
    await engine_room_alert_no_lights._evaluate()
    assert hass_room_alert_no_lights.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "alert"
    assert not any(
        domain == "humidity_intelligence" and service == "flash_lights"
        for domain, service, *_ in hass_room_alert_no_lights.services.calls
    )

    entry_room_alert_miss_data = _base_entry_data()
    entry_room_alert_miss_data["zones"]["zone1"]["enabled"] = False
    entry_room_alert_miss_data["zones"]["zone2"]["enabled"] = False
    entry_room_alert_miss_data["aq"] = {}
    entry_room_alert_miss_data["humidifiers"] = {}
    entry_room_alert_miss_data["alerts"] = [
        {
            "enabled": True,
            "trigger_type": "humidity_danger",
            "room": "Hallway",
            "lights": ["light.alert"],
            "duration": 10,
        }
    ]
    entry_room_alert_miss = SimpleNamespace(entry_id=ENTRY_ID, data=entry_room_alert_miss_data, options={})
    hass_room_alert_miss = _FakeHass(
        entry_room_alert_miss,
        {
            "sensor.kitchen_h": _FakeState(50),
            "sensor.hall_h": _FakeState(45),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_room_alert_miss = HIAutomationEngine(hass_room_alert_miss, entry_room_alert_miss)
    await engine_room_alert_miss._evaluate()
    assert hass_room_alert_miss.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") != "alert"

    # Zone label and fan-step enforcement: custom UI label should be surfaced,
    # and unsupported percentages should snap to the nearest supported level.
    entry_label_data = _base_entry_data()
    entry_label_data["alert_handling_enabled"] = False
    entry_label_data["zones"]["zone1"]["ui_label"] = "Kitchen Extract"
    entry_label_data["zones"]["zone1"]["output_level"] = 64
    entry_label_data["zones"]["zone2"]["enabled"] = False
    entry_label_data["aq"] = {}
    entry_label = SimpleNamespace(entry_id=ENTRY_ID, data=entry_label_data, options={})
    hass_label = _FakeHass(
        entry_label,
        {
            "sensor.kitchen_h": _FakeState(90),
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_label = HIAutomationEngine(hass_label, entry_label)
    await engine_label._evaluate()

    assert hass_label.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "cooking"
    assert hass_label.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode_display") == "Kitchen Extract"
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone1"
        and data.get("percentage") == 66
        for domain, service, data, _ in hass_label.services.calls
    )

    # Zone lane priority must select one ventilation lane per cycle:
    # zone1 beats zone2 and zone2 must not write its fan output.
    entry_zone_select_data = _base_entry_data()
    entry_zone_select_data["alert_handling_enabled"] = False
    entry_zone_select_data["humidifiers"] = {}
    entry_zone_select_data["aq"] = {}
    entry_zone_select = SimpleNamespace(entry_id=ENTRY_ID, data=entry_zone_select_data, options={})
    hass_zone_select = _FakeHass(
        entry_zone_select,
        {
            "sensor.kitchen_h": _FakeState(90),
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(90),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_zone_select = HIAutomationEngine(hass_zone_select, entry_zone_select)
    await engine_zone_select._evaluate()

    assert hass_zone_select.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "cooking"
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone1"
        and data.get("percentage") == 66
        for domain, service, data, _ in hass_zone_select.services.calls
    )
    assert not any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.zone2"
        for domain, service, data, _ in hass_zone_select.services.calls
    )

    # AQ-only scenario: no alert and no zone should allow AQ lane execution.
    entry3_data = _base_entry_data()
    entry3_data["zones"]["zone1"]["enabled"] = False
    entry3_data["zones"]["zone2"]["enabled"] = False
    entry3_data["alert_handling_enabled"] = False
    # Overlap AQ output with a zone output to ensure AQ is not immediately reset to auto.
    entry3_data["aq"]["level1"]["outputs"] = ["fan.zone1"]
    entry3 = SimpleNamespace(entry_id=ENTRY_ID, data=entry3_data, options={})
    hass_aq = _FakeHass(
        entry3,
        {
            "sensor.kitchen_h": _FakeState(40),
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(40),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(70),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_aq = HIAutomationEngine(hass_aq, entry3)
    aq_trace = []
    for method in ("_handle_alerts", "_handle_humidifiers", "_handle_zone_by_key", "_handle_aq"):
        _wrap_async_method(engine_aq, method, aq_trace)
    await engine_aq._evaluate()

    assert "_handle_aq" in aq_trace
    assert any(
        domain == "fan" and service == "set_percentage" and data.get("entity_id") == "fan.zone1"
        for domain, service, data, _ in hass_aq.services.calls
    )
    assert not any(
        domain == "fan" and service == "set_preset_mode" and data.get("entity_id") == "fan.zone1"
        for domain, service, data, _ in hass_aq.services.calls
    )
    assert hass_aq.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "air_quality"
    aq_reason = hass_aq.data["humidity_intelligence"][ENTRY_ID].get("runtime_reason", "")
    assert "AQ is active" in aq_reason or "Air-quality assist is active" in aq_reason
    assert "Trigger detail:" in aq_reason

    # AQ auto level should use fan preset mode instead of percentage service.
    entry_aq_auto_data = _base_entry_data()
    entry_aq_auto_data["zones"]["zone1"]["enabled"] = False
    entry_aq_auto_data["zones"]["zone2"]["enabled"] = False
    entry_aq_auto_data["alert_handling_enabled"] = False
    entry_aq_auto_data["aq"]["level1"]["output_level"] = "auto"
    entry_aq_auto = SimpleNamespace(entry_id=ENTRY_ID, data=entry_aq_auto_data, options={})
    hass_aq_auto = _FakeHass(
        entry_aq_auto,
        {
            "sensor.kitchen_h": _FakeState(40),
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(40),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(70),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_aq_auto = HIAutomationEngine(hass_aq_auto, entry_aq_auto)
    await engine_aq_auto._evaluate()
    assert any(
        domain == "fan" and service == "set_preset_mode" and data.get("entity_id") == "fan.aq1"
        for domain, service, data, _ in hass_aq_auto.services.calls
    )
    assert not any(
        domain == "fan" and service == "set_percentage" and data.get("entity_id") == "fan.aq1"
        for domain, service, data, _ in hass_aq_auto.services.calls
    )

    # Independent AQ lanes sharing one output: both can run; newest trigger wins output level.
    entry_shared_aq_data = _base_entry_data()
    entry_shared_aq_data["zones"]["zone1"]["enabled"] = False
    entry_shared_aq_data["zones"]["zone2"]["enabled"] = False
    entry_shared_aq_data["alert_handling_enabled"] = False
    entry_shared_aq_data["telemetry"].append(
        {"entity_id": "sensor.l2_iaq", "sensor_type": "iaq", "level": "level2", "room": "Bedroom"}
    )
    entry_shared_aq_data["aq"] = {
        "level1": {
            "enabled": True,
            "outputs": ["fan.shared"],
            "triggers": ["iaq_bad"],
            "thresholds": {"iaq_bad": 75},
            "output_level": 33,
            "run_duration": 10,
        },
        "level2": {
            "enabled": True,
            "outputs": ["fan.shared"],
            "triggers": ["iaq_bad"],
            "thresholds": {"iaq_bad": 75},
            "output_level": 100,
            "run_duration": 10,
        },
    }
    entry_shared_aq = SimpleNamespace(entry_id=ENTRY_ID, data=entry_shared_aq_data, options={})
    hass_shared_aq = _FakeHass(
        entry_shared_aq,
        {
            "sensor.kitchen_h": _FakeState(40),
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(40),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(70),   # level1 triggers first
            "sensor.l2_iaq": _FakeState(90),   # level2 idle initially
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_shared_aq = HIAutomationEngine(hass_shared_aq, entry_shared_aq)
    await engine_shared_aq._evaluate()
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.shared"
        and data.get("percentage") == 33
        for domain, service, data, _ in hass_shared_aq.services.calls
    )
    # New level2 trigger arrives later: shared output should move to level2 setting.
    hass_shared_aq.states._values["sensor.l2_iaq"] = _FakeState(70)
    await engine_shared_aq._evaluate()
    assert hass_shared_aq.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_aq_downstairs_active"].is_on
    assert hass_shared_aq.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_aq_upstairs_active"].is_on
    assert any(
        domain == "fan"
        and service == "set_percentage"
        and data.get("entity_id") == "fan.shared"
        and data.get("percentage") == 100
        for domain, service, data, _ in hass_shared_aq.services.calls
    )

    # Shared humidifier output follows last trigger transition while lanes remain independent.
    entry_shared_humid_data = _base_entry_data()
    entry_shared_humid_data["zones"]["zone1"]["enabled"] = False
    entry_shared_humid_data["zones"]["zone2"]["enabled"] = False
    entry_shared_humid_data["alert_handling_enabled"] = False
    entry_shared_humid_data["aq"] = {}
    entry_shared_humid_data["humidifiers"] = {
        "level1": {"enabled": True, "outputs": ["humidifier.shared"], "band_adjust": 0},
        "level2": {"enabled": True, "outputs": ["humidifier.shared"], "band_adjust": 0},
    }
    entry_shared_humid = SimpleNamespace(entry_id=ENTRY_ID, data=entry_shared_humid_data, options={})
    hass_shared_humid = _FakeHass(
        entry_shared_humid,
        {
            "sensor.kitchen_h": _FakeState(40),  # level1 below low -> on
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(40),      # level2 below low -> on
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(90),
            "sensor.co_val": _FakeState(4),
        },
    )
    engine_shared_humid = HIAutomationEngine(hass_shared_humid, entry_shared_humid)
    await engine_shared_humid._evaluate()
    assert hass_shared_humid.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_downstairs_humidifier_active"].is_on
    assert hass_shared_humid.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_upstairs_humidifier_active"].is_on
    humid_reason = hass_shared_humid.data["humidity_intelligence"][ENTRY_ID].get("runtime_reason", "")
    assert "Humidifier:" in humid_reason
    assert "status=" not in humid_reason
    assert "action=" not in humid_reason
    assert "Trigger:" not in humid_reason
    assert "Recovery:" not in humid_reason
    # Level1 recovers: its off transition becomes the newest command on shared output.
    hass_shared_humid.states._values["sensor.kitchen_h"] = _FakeState(55)
    hass_shared_humid.states._values["sensor.hall_h"] = _FakeState(55)
    await engine_shared_humid._evaluate()
    assert any(
        domain == "humidifier"
        and service == "turn_off"
        and data.get("entity_id") == "humidifier.shared"
        for domain, service, data, _ in hass_shared_humid.services.calls
    )
    assert not hass_shared_humid.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_downstairs_humidifier_active"].is_on
    assert hass_shared_humid.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_upstairs_humidifier_active"].is_on

    # Testing isolation toggles suppress output service calls while logic state still updates.
    entry_isolated_data = _base_entry_data()
    entry_isolated_data["alert_handling_enabled"] = False
    entry_isolated_data["zones"]["zone2"]["enabled"] = False
    entry_isolated_data["aq"] = {}
    entry_isolated = SimpleNamespace(entry_id=ENTRY_ID, data=entry_isolated_data, options={})
    hass_isolated = _FakeHass(
        entry_isolated,
        {
            "sensor.kitchen_h": _FakeState(90),
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(40),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(90),
            "sensor.co_val": _FakeState(4),
        },
    )
    hass_isolated.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_isolate_fan_outputs"].is_on = True
    hass_isolated.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_isolate_humidifier_outputs"].is_on = True
    engine_isolated = HIAutomationEngine(hass_isolated, entry_isolated)
    await engine_isolated._evaluate()
    assert hass_isolated.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "cooking"
    isolated_reason = hass_isolated.data["humidity_intelligence"][ENTRY_ID].get("runtime_reason", "")
    assert "isolated for testing" in isolated_reason
    assert not any(
        domain in {"fan", "switch", "humidifier"} and service in {"set_percentage", "set_preset_mode", "turn_on", "turn_off"}
        for domain, service, data, _ in hass_isolated.services.calls
    )

    # Stale AQ state from an old level config must be cleared (prevents AQ badge/mode drift).
    entry4_data = _base_entry_data()
    entry4_data["zones"]["zone1"]["enabled"] = False
    entry4_data["zones"]["zone2"]["enabled"] = False
    entry4_data["alert_handling_enabled"] = False
    entry4_data["aq"] = {
        "level1": {
            "enabled": False,
            "outputs": ["fan.aq1"],
            "triggers": ["iaq_bad"],
            "thresholds": {"iaq_bad": 75},
            "output_level": 66,
            "run_duration": 10,
        }
    }
    entry4 = SimpleNamespace(entry_id=ENTRY_ID, data=entry4_data, options={})
    hass_stale = _FakeHass(
        entry4,
        {
            "sensor.kitchen_h": _FakeState(50),
            "sensor.hall_h": _FakeState(50),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    hass_stale.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_aq_upstairs_active"].is_on = True
    engine_stale = HIAutomationEngine(hass_stale, entry4)
    engine_stale._aq_tasks["level2"] = asyncio.create_task(asyncio.sleep(3600))
    await engine_stale._evaluate()

    assert not hass_stale.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_aq_upstairs_active"].is_on
    assert "level2" not in engine_stale._aq_tasks
    assert hass_stale.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "normal"

    # Global gate should publish dedicated runtime mode for UI chip/border sync.
    entry_gate_data = _base_entry_data()
    entry_gate_data["alert_handling_enabled"] = False
    entry_gate_data["zones"]["zone1"]["enabled"] = False
    entry_gate_data["zones"]["zone2"]["enabled"] = False
    entry_gate_data["aq"] = {}
    entry_gate_data["humidifiers"] = {}
    entry_gate_data["presence_gate"] = {
        "enabled": True,
        "entities": ["binary_sensor.home_presence"],
        "present_states": ["on"],
        "away_states": ["off"],
    }
    entry_gate = SimpleNamespace(entry_id=ENTRY_ID, data=entry_gate_data, options={})
    hass_gate = _FakeHass(
        entry_gate,
        {
            "sensor.kitchen_h": _FakeState(50),
            "sensor.hall_h": _FakeState(50),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
            "binary_sensor.home_presence": _FakeState("off"),
        },
    )
    engine_gate = HIAutomationEngine(hass_gate, entry_gate)
    await engine_gate._evaluate()
    assert hass_gate.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode") == "global_gate"
    assert hass_gate.data["humidity_intelligence"][ENTRY_ID].get("runtime_mode_display") == "GLOBAL GATE"
    gate_reason = hass_gate.data["humidity_intelligence"][ENTRY_ID].get("runtime_reason", "")
    assert "Presence gate is active" in gate_reason

    # Disabled humidifier lanes should clear stale active state and turn outputs off.
    entry5_data = _base_entry_data()
    entry5_data["zones"]["zone1"]["enabled"] = False
    entry5_data["zones"]["zone2"]["enabled"] = False
    entry5_data["alert_handling_enabled"] = False
    entry5_data["aq"] = {}
    entry5_data["humidifiers"]["level1"]["enabled"] = False
    entry5 = SimpleNamespace(entry_id=ENTRY_ID, data=entry5_data, options={})
    hass_humid = _FakeHass(
        entry5,
        {
            "sensor.kitchen_h": _FakeState(40),
            "sensor.hall_h": _FakeState(40),
            "sensor.bed_h": _FakeState(40),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    hass_humid.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_downstairs_humidifier_active"].is_on = True
    engine_humid = HIAutomationEngine(hass_humid, entry5)
    await engine_humid._evaluate()

    assert not hass_humid.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_downstairs_humidifier_active"].is_on
    assert any(
        domain == "humidifier" and service == "turn_off" and data.get("entity_id") == "humidifier.l1"
        for domain, service, data, _ in hass_humid.services.calls
    )

    # Humidifier off threshold should recover inside target band (low + 4%), not only at high target.
    entry6_data = _base_entry_data()
    entry6_data["zones"]["zone1"]["enabled"] = False
    entry6_data["zones"]["zone2"]["enabled"] = False
    entry6_data["alert_handling_enabled"] = False
    entry6_data["aq"] = {}
    entry6 = SimpleNamespace(entry_id=ENTRY_ID, data=entry6_data, options={})
    hass_humid_band = _FakeHass(
        entry6,
        {
            "sensor.kitchen_h": _FakeState(50),
            "sensor.hall_h": _FakeState(50),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(23),
            "sensor.hall_t": _FakeState(22),
            "sensor.bed_t": _FakeState(21),
            "sensor.l1_iaq": _FakeState(85),
            "sensor.co_val": _FakeState(4),
        },
    )
    # Simulate humidifier already running; at 50% in winter, it should now shut off at low+4.
    hass_humid_band.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_downstairs_humidifier_active"].is_on = True
    engine_humid_band = HIAutomationEngine(hass_humid_band, entry6)
    await engine_humid_band._evaluate()
    assert not hass_humid_band.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"]["air_downstairs_humidifier_active"].is_on
    assert any(
        domain == "humidifier" and service == "turn_off" and data.get("entity_id") == "humidifier.l1"
        for domain, service, data, _ in hass_humid_band.services.calls
    )

    # Runtime reason state must stay within HA state limit and preserve full text.
    long_reason = "X" * 400
    await engine_humid_band._set_runtime_reason(long_reason)
    stored = hass_humid_band.data["humidity_intelligence"][ENTRY_ID]
    assert isinstance(stored.get("runtime_reason"), str)
    assert len(stored.get("runtime_reason")) <= 255
    assert stored.get("runtime_reason_full") == long_reason
    assert stored.get("runtime_reason_truncated") is True

    # Re-entrant requests caused by helper state changes should be coalesced
    # instead of recursively running overlapping evaluation cycles.
    entry_reentry = SimpleNamespace(entry_id=ENTRY_ID, data=_base_entry_data(), options={})
    hass_reentry = _FakeHass(entry_reentry, {})
    engine_reentry = HIAutomationEngine(hass_reentry, entry_reentry)
    reentry_calls = []

    async def fake_evaluate():
        reentry_calls.append("run")
        if len(reentry_calls) == 1:
            await engine_reentry.async_request_evaluate()

    engine_reentry._evaluate = fake_evaluate
    await engine_reentry.async_request_evaluate()
    assert reentry_calls == ["run", "run"]

    # Internal status helpers should not be tracked as evaluation sources; they
    # are outputs of the engine, not inputs that should retrigger the engine.
    for key, entity in hass_reentry.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"].items():
        entity.entity_id = f"switch.hi_{key}"
    sources = engine_reentry._evaluation_sources()
    assert "switch.hi_air_control_enabled" in sources
    assert "switch.hi_air_alert_1_active" not in sources
    assert "switch.hi_air_aq_downstairs_active" not in sources
    assert "switch.hi_air_downstairs_humidifier_active" not in sources

    # Cleanup background AQ tasks.
    for task in list(engine._aq_tasks.values()):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    for task in list(engine_aq._aq_tasks.values()):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    for task in list(engine_stale._aq_tasks.values()):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    for task in list(engine_aq_auto._aq_tasks.values()):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    for task in list(engine_shared_aq._aq_tasks.values()):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def _contains_v2_border_pill_sync_logic(yaml_text: str) -> bool:
    chip_tokens = [
        "const red =",
        "const gateActive =",
        "const zone1 =",
        "const zone2 =",
        "const aqActive =",
        "if (red) return '#ef4444'",
        "if (gateActive) return '#f59e0b'",
        "if (zone1) return '#38bdf8'",
        "if (zone2) return '#4ade80'",
        "if (aqActive) return '#a855f7'",
    ]
    border_tokens = [
        "if (red) return '1px solid rgba(239,68,68",
        "if (gateActive) return '1px solid rgba(245,158,11",
        "if (zone1) return '1px solid rgba(56,189,248",
        "if (zone2) return '1px solid rgba(74,222,128",
        "if (aqActive) return '1px solid rgba(168,85,247",
    ]
    return all(token in yaml_text for token in chip_tokens) and all(
        token in yaml_text for token in border_tokens
    )


def _has_empty_cards_block(yaml_text: str) -> bool:
    lines = yaml_text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() != "cards:":
            continue
        indent = len(line) - len(line.lstrip(" \t"))
        next_idx = idx + 1
        while next_idx < len(lines) and not lines[next_idx].strip():
            next_idx += 1
        if next_idx >= len(lines):
            return True
        next_indent = len(lines[next_idx]) - len(lines[next_idx].lstrip(" \t"))
        if next_indent <= indent:
            return True
    return False


def _has_invalid_conditional_block(yaml_text: str) -> bool:
    lines = yaml_text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() != "- type: conditional":
            continue

        base_indent = len(line) - len(line.lstrip(" \t"))
        end = idx + 1
        while end < len(lines):
            nxt = lines[end]
            if not nxt.strip():
                end += 1
                continue
            nxt_indent = len(nxt) - len(nxt.lstrip(" \t"))
            if nxt_indent <= base_indent and nxt.lstrip().startswith("- "):
                break
            end += 1

        block = lines[idx:end]
        top_level_indent = base_indent + 2
        conditions_idx = None
        card_idx = None
        for rel, bline in enumerate(block[1:], start=1):
            stripped = bline.lstrip(" \t")
            indent = len(bline) - len(stripped)
            if indent != top_level_indent:
                continue
            if stripped.startswith("conditions:") and conditions_idx is None:
                conditions_idx = rel
            if stripped.startswith("card:") and card_idx is None:
                card_idx = rel

        if conditions_idx is None or card_idx is None:
            return True

        conditions_indent = top_level_indent
        has_condition_item = False
        for rel in range(conditions_idx + 1, len(block)):
            bline = block[rel]
            if not bline.strip():
                continue
            indent = len(bline) - len(bline.lstrip(" \t"))
            if indent <= conditions_indent:
                break
            if bline.lstrip(" \t").startswith("- "):
                has_condition_item = True
                break
        if not has_condition_item:
            return True

        card_indent = top_level_indent
        has_card_body = False
        for rel in range(card_idx + 1, len(block)):
            bline = block[rel]
            if not bline.strip():
                continue
            indent = len(bline) - len(bline.lstrip(" \t"))
            if indent <= card_indent:
                break
            has_card_body = True
            break
        if not has_card_body:
            return True
    return False


async def _run_card_assertions(register_mod) -> None:
    sys.modules["homeassistant.helpers.entity_registry"].async_get = lambda hass: _FakeRegistry()

    entry = SimpleNamespace(
        entry_id=ENTRY_ID,
        data={
            "telemetry": [
                {"entity_id": "sensor.kitchen_h", "sensor_type": "humidity", "level": "level1", "room": "Kitchen"},
                {"entity_id": "sensor.hall_h", "sensor_type": "humidity", "level": "level1", "room": "Hallway"},
                {"entity_id": "sensor.bed_h", "sensor_type": "humidity", "level": "level2", "room": "Bedroom"},
                {"entity_id": "sensor.willow_h", "sensor_type": "humidity", "level": "level2", "room": "Willow Room"},
                {"entity_id": "sensor.bath_h", "sensor_type": "humidity", "level": "level1", "room": "Bathroom"},
                {"entity_id": "sensor.kitchen_t", "sensor_type": "temperature", "level": "level1", "room": "Kitchen"},
                {"entity_id": "sensor.bed_t", "sensor_type": "temperature", "level": "level2", "room": "Bedroom"},
                {"entity_id": "sensor.l1_iaq", "sensor_type": "iaq", "level": "level1", "room": "Hallway"},
                {"entity_id": "sensor.l2_iaq", "sensor_type": "iaq", "level": "level2", "room": "Bedroom"},
                {"entity_id": "sensor.l1_pm25", "sensor_type": "pm25", "level": "level1", "room": "Hallway"},
                {"entity_id": "sensor.l2_pm25", "sensor_type": "pm25", "level": "level2", "room": "Bedroom"},
                {"entity_id": "sensor.l1_voc", "sensor_type": "voc", "level": "level1", "room": "Hallway"},
                {"entity_id": "sensor.l2_voc", "sensor_type": "voc", "level": "level2", "room": "Bedroom"},
                {"entity_id": "sensor.l1_co", "sensor_type": "co", "level": "level1", "room": "Hallway"},
                {"entity_id": "sensor.l2_co", "sensor_type": "co", "level": "level2", "room": "Bedroom"},
            ],
            "zones": {
                "zone1": {"level": "level1", "rooms": ["Bathroom", "Kitchen"], "outputs": ["fan.zone1"]},
                "zone2": {"level": "level2", "rooms": ["Bedroom"], "outputs": ["fan.zone2"]},
            },
            "humidifiers": {
                "level1": {"outputs": ["humidifier.l1"]},
                "level2": {"outputs": ["humidifier.l2"]},
            },
            "alerts": [{"lights": ["light.alert1"]}],
            "temperature_comfort_mode": "auto",
            "slope": {
                "mode": "hi_calculates",
                "source_entities": ["sensor.kitchen_t", "sensor.bed_t"],
                "show_temperature_chips": True,
            },
        },
        options={},
    )
    hass = _FakeHass(entry, {})
    hass.config_entries = _FakeConfigEntries(entry)

    mapping = await register_mod.async_build_entity_mapping(hass, ENTRY_ID)
    cards = await register_mod.async_register_cards(hass, ENTRY_ID, mapping)
    mobile = cards.get("v2_mobile", "")
    tablet = cards.get("v2_tablet", "")

    assert hass.data["humidity_intelligence"][ENTRY_ID].get("unresolved_placeholders_by_card", {}) == {}
    assert mobile.startswith("# Humidity Intelligence V2 Mobile Dashboard YAML")
    assert tablet.startswith("# Humidity Intelligence V2 Tablet Dashboard YAML")
    assert "Call the service humidity_intelligence.dump_cards" in mobile
    assert "Dashboard Manual card" in tablet

    room_placeholders = [
        "sensor.bedroom_humidity",
        "sensor.hallway_humidity",
        "sensor.kids_room_humidity",
        "sensor.living_room_humidity",
        "sensor.toilet_humidity",
        "sensor.bathroom_humidity",
    ]
    for placeholder in room_placeholders:
        assert mapping.get(placeholder)
        assert placeholder not in cards.get("v1_mobile", "")
    assert mapping.get("sensor.hi_diagnostics")

    for card in (mobile, tablet):
        assert "Kitchen Δ slope" not in card
        assert "sensor.air_control_kitchen_slope_delta" not in card
        assert "sensor.air_control_bathroom_humidity_delta" not in card
        assert "sensor.air_control_kitchen_humidity_delta" not in card
        assert "House PM2.5" in card
        assert "House VOC" in card
        assert "House CO" in card
        assert "House Temp" in card
        assert "Upstairs Temp" in card
        assert "Downstairs Temp" in card
        assert "show_temperature_chips" in card
        assert "slope_map" in card
        assert "sensor.hi_house_temperature_comfort_low" in card
        assert "sensor.hi_house_temperature_comfort_high" in card
        assert "tempColor(tempValueC(entity))" in card
        assert "slopeEntityFor(item)" in card
        assert "states['sensor.hi_diagnostics']" in card
        assert "CHIPSET_SCROLL_RESET_DELAY_MS = 15000" in card
        assert "data-scroll-reset-delay-ms" in card
        assert "activeAlertNames.forEach" not in card
        assert "sensor.hi_level2_avg_temperature" in card
        assert "sensor.hi_level1_avg_temperature" in card
        assert card.index("House AVG") < card.index("Upstairs AVG") < card.index("Downstairs AVG")
        assert card.index("House IAQ") < card.index("Upstairs IAQ") < card.index("Downs.. IAQ")

    assert _contains_v2_border_pill_sync_logic(mobile)
    assert _contains_v2_border_pill_sync_logic(tablet)
    # Outputs should only include configured alert placeholders.
    assert "input_boolean.air_alert_2_active" not in mobile
    assert "light.alert_2" not in mobile
    assert "name: Alert 2 Active" not in mobile
    assert "name: Alert light 2" not in mobile
    assert "air_bathroom_alert_77" not in mobile
    assert "air_bathroom_alert_81" not in mobile
    assert "air_bathroom_alert_77" not in tablet
    assert "air_bathroom_alert_81" not in tablet
    assert "input_boolean.air_isolate_fan_outputs" not in mobile
    assert "input_boolean.air_isolate_humidifier_outputs" not in mobile
    assert "input_boolean.air_isolate_fan_outputs" not in tablet
    assert "input_boolean.air_isolate_humidifier_outputs" not in tablet
    assert not _has_empty_cards_block(mobile)
    assert not _has_empty_cards_block(tablet)
    assert not _has_invalid_conditional_block(mobile)
    assert not _has_invalid_conditional_block(tablet)


async def _run_output_detail_visibility_assertions(register_mod) -> None:
    sys.modules["homeassistant.helpers.entity_registry"].async_get = lambda hass: _FakeRegistry()

    hidden_data = _base_entry_data()
    hidden_data["show_output_entity_details"] = False
    hidden_entry = SimpleNamespace(entry_id=ENTRY_ID, data=hidden_data, options={})
    hidden_hass = _FakeHass(hidden_entry, {})
    hidden_mapping = await register_mod.async_build_entity_mapping(hidden_hass, ENTRY_ID)
    hidden_cards = await register_mod.async_register_cards(hidden_hass, ENTRY_ID, hidden_mapping)

    for card in (hidden_cards.get("v2_mobile", ""), hidden_cards.get("v2_tablet", "")):
        assert "name: Outputs" not in card
        assert "entity: switch.hi_input_air_control_output_expanded" not in card
        assert "entity: input_boolean.air_control_output_expanded" not in card
        assert "hi:output-details" not in card
        assert not _has_empty_cards_block(card)
        assert not _has_invalid_conditional_block(card)

    shown_data = _base_entry_data()
    shown_data["show_output_entity_details"] = True
    shown_entry = SimpleNamespace(entry_id=ENTRY_ID, data=shown_data, options={})
    shown_hass = _FakeHass(shown_entry, {})
    shown_mapping = await register_mod.async_build_entity_mapping(shown_hass, ENTRY_ID)
    shown_cards = await register_mod.async_register_cards(shown_hass, ENTRY_ID, shown_mapping)

    for card in (shown_cards.get("v2_mobile", ""), shown_cards.get("v2_tablet", "")):
        assert "name: Outputs" in card
        assert "air_control_output_expanded" in card
        assert "hi:output-details" not in card


async def _run_alert_only_card_assertions(register_mod) -> None:
    sys.modules["homeassistant.helpers.entity_registry"].async_get = lambda hass: _FakeRegistry()

    entry = SimpleNamespace(
        entry_id=ENTRY_ID,
        data={
            "alert_only_mode": True,
            "telemetry": [
                {"entity_id": "sensor.kitchen_h", "sensor_type": "humidity", "level": "level1", "room": "Kitchen"},
                {"entity_id": "sensor.kitchen_t", "sensor_type": "temperature", "level": "level1", "room": "Kitchen"},
            ],
            "zones": {},
            "humidifiers": {},
            "alerts": [],
        },
        options={},
    )
    hass = _FakeHass(entry, {})
    hass.config_entries = _FakeConfigEntries(entry)

    mapping = await register_mod.async_build_entity_mapping(hass, ENTRY_ID)
    cards = await register_mod.async_register_cards(hass, ENTRY_ID, mapping)
    mobile = cards.get("v2_mobile", "")
    tablet = cards.get("v2_tablet", "")

    assert "entity: input_boolean.air_control_enabled" not in mobile
    assert "entity: timer.air_control_pause" not in mobile
    assert "entity: input_boolean.air_control_output_expanded" not in mobile
    assert "- entity: fan.kitchen_air" not in mobile
    assert "- entity: humidifier.downstairs_humidifier" not in mobile
    assert "Monitor + alerts only (no automation output controls configured)." in mobile
    assert "Monitor + alerts only (no automation output controls configured)." in tablet
    assert not _has_empty_cards_block(mobile)
    assert not _has_invalid_conditional_block(mobile)


def test_runtime_lane_order_and_service_simulation():
    engine_mod, _ = _load_target_modules()
    asyncio.run(_run_runtime_assertions(engine_mod))


def test_card_render_sanity_and_placeholder_resolution():
    _, register_mod = _load_target_modules()
    asyncio.run(_run_card_assertions(register_mod))


def test_output_detail_visibility_option_prunes_v2_cards():
    _, register_mod = _load_target_modules()
    asyncio.run(_run_output_detail_visibility_assertions(register_mod))


def test_card_render_hides_controls_in_alert_only_mode():
    _, register_mod = _load_target_modules()
    asyncio.run(_run_alert_only_card_assertions(register_mod))


def test_temperature_normalization_respects_source_units():
    engine_mod, _ = _load_target_modules()
    entry = SimpleNamespace(entry_id=ENTRY_ID, data={}, options={})
    hass = _FakeHass(
        entry,
        {
            "sensor.temp_f": _FakeState(68, {"unit_of_measurement": "°F"}),
            "sensor.temp_c": _FakeState(20, {"unit_of_measurement": "°C"}),
            "sensor.temp_no_unit": _FakeState(21),
        },
    )

    from_f = engine_mod._get_float(hass, "sensor.temp_f", sensor_type="temperature")
    from_c = engine_mod._get_float(hass, "sensor.temp_c", sensor_type="temperature")
    from_missing_unit = engine_mod._get_float(hass, "sensor.temp_no_unit", sensor_type="temperature")

    assert from_f is not None and abs(from_f - 20.0) < 0.05
    assert from_c is not None and abs(from_c - 20.0) < 0.05
    assert from_missing_unit is not None and abs(from_missing_unit - 21.0) < 0.05


async def _registered_flash_handler(services_mod, hass):
    await services_mod.async_register_services(hass)
    return hass.services.handlers[(services_mod.DOMAIN, services_mod.SERVICE_FLASH_LIGHTS)]


def _light_service_calls(hass):
    return [
        (service, data)
        for domain, service, data, _blocking in hass.services.calls
        if domain == "light"
    ]


async def _run_visual_flash_restore_assertions(services_mod) -> None:
    original_sleep = services_mod.asyncio.sleep

    async def fast_sleep(_delay):
        await original_sleep(0)

    services_mod.asyncio.sleep = fast_sleep
    try:
        attrs = {
            "supported_color_modes": ["rgb"],
            "brightness": 77,
            "rgb_color": (1, 2, 3),
        }
        payload = {
            "lights": ["light.alert"],
            "color": [255, 0, 0],
            "duration": 10,
            "flash_count": 10,
        }

        hass_on = _FlashHass({"light.alert": _FakeState("on", attrs)})
        handler_on = await _registered_flash_handler(services_mod, hass_on)
        await handler_on(SimpleNamespace(data=payload))
        on_calls = _light_service_calls(hass_on)
        assert [service for service, _data in on_calls[:20]] == ["turn_on", "turn_off"] * 10
        assert len(on_calls) == 21
        assert on_calls[-1][0] == "turn_on"
        assert on_calls[-1][1]["brightness"] == 77
        assert on_calls[-1][1]["rgb_color"] == (1, 2, 3)
        assert hass_on.states.get("light.alert").state == "on"

        hass_off = _FlashHass({"light.alert": _FakeState("off", attrs)})
        handler_off = await _registered_flash_handler(services_mod, hass_off)
        await handler_off(SimpleNamespace(data=payload))
        off_calls = _light_service_calls(hass_off)
        assert [service for service, _data in off_calls[:20]] == ["turn_on", "turn_off"] * 10
        assert len(off_calls) == 21
        assert off_calls[-1][0] == "turn_off"
        assert hass_off.states.get("light.alert").state == "off"

        hass_overlap = _FlashHass({"light.alert": _FakeState("on", attrs)})
        handler_overlap = await _registered_flash_handler(services_mod, hass_overlap)
        await asyncio.gather(
            handler_overlap(SimpleNamespace(data=payload)),
            handler_overlap(SimpleNamespace(data=payload)),
        )
        overlap_services = [service for service, _data in _light_service_calls(hass_overlap)]
        one_sequence = ["turn_on", "turn_off"] * 10 + ["turn_on"]
        assert overlap_services == one_sequence + one_sequence
        assert hass_overlap.states.get("light.alert").state == "on"
    finally:
        services_mod.asyncio.sleep = original_sleep


def test_visual_alert_flash_restores_initial_light_state_and_serializes_overlap():
    services_mod = _load_services_module()
    asyncio.run(_run_visual_flash_restore_assertions(services_mod))


def test_startup_ui_refresh_contract_is_wired():
    init_source = (ROOT / "__init__.py").read_text()
    const_source = (ROOT / "const.py").read_text()
    config_source = (ROOT / "config_flow.py").read_text()
    strings_source = (ROOT / "strings.json").read_text()
    services_source = (ROOT / "services.yaml").read_text()

    assert "EVENT_HOMEASSISTANT_STARTED" in init_source
    assert ".async_listen_once(" in init_source
    assert "@callback" in init_source
    assert "hass.create_task(_run_startup_ui_refresh())" in init_source
    assert ".add_done_callback(" not in init_source
    assert "startup_ui_refresh_scheduled" in init_source
    assert "SERVICE_REFRESH_UI" in init_source
    assert "STARTUP_UI_REFRESH_DELAY_SECONDS" in init_source
    assert "blocking=True" in init_source
    assert "auto_refresh_ui_on_startup" in const_source
    assert "show_output_entity_details" in const_source
    assert "CONF_AUTO_REFRESH_UI_ON_STARTUP" in config_source
    assert "DEFAULT_AUTO_REFRESH_UI_ON_STARTUP" in config_source
    assert "CONF_SHOW_OUTPUT_ENTITY_DETAILS" in config_source
    assert "DEFAULT_SHOW_OUTPUT_ENTITY_DETAILS" in config_source
    assert "ADVANCED_OPTIONS_FIELD" in config_source
    assert "show_advanced_options" in config_source
    assert '"show_advanced_options": "Show advanced tuning"' in strings_source
    assert "show_output_entity_details" in strings_source
    assert "Show output entity details" in strings_source
    assert "['v2_tablet']" in config_source or 'default=["v2_tablet"]' in config_source
    assert "async_step_options_thresholds" in config_source
    assert "zone1_threshold_humidity_high" in strings_source
    assert "temperature_comfort_mode" in strings_source
    assert "auto_refresh_ui_on_startup" in strings_source
    assert "recommended defaults" in config_source
    assert "recommended thresholds" in strings_source
    assert "automatically shortly after Home Assistant startup" in services_source
    assert "_entry_show_output_entity_details" in init_source
    assert "output entity details" in init_source


def test_options_gates_keeps_custom_targets_behind_advanced():
    config_source = (ROOT / "config_flow.py").read_text()
    method_source = config_source.split("async def async_step_options_gates", 1)[1].split(
        "async def async_step_options_presence_states", 1
    )[0]
    visible_schema_source = method_source.split("if gates_advanced:", 1)[0]
    advanced_schema_source = method_source.split("if gates_advanced:", 1)[1]

    assert 'vol.Optional("target_profile"' in visible_schema_source
    assert 'vol.Optional("custom_target_low"' not in visible_schema_source
    assert 'vol.Optional("custom_target_high"' not in visible_schema_source
    assert 'vol.Optional("custom_target_low"' in advanced_schema_source
    assert 'vol.Optional("custom_target_high"' in advanced_schema_source


def test_options_thresholds_only_persists_real_zone_configs():
    config_source = (ROOT / "config_flow.py").read_text()
    method_source = config_source.split("async def async_step_options_thresholds", 1)[1].split(
        "async def async_step_options_sensors", 1
    )[0]

    assert "_configured_zone_items(zones)" in method_source
    assert 'for zone_key in ("zone1", "zone2")' not in method_source
    assert "zones[zone_key] = zone" in method_source
    assert "zone[\"thresholds\"] = thresholds" in method_source


def test_advanced_reveal_remembers_submitted_visible_values():
    config_source = (ROOT / "config_flow.py").read_text()

    assert "_remember_advanced_input" in config_source
    for step_id in (
        '"gates"',
        '"slope"',
        "zone_key",
        '"zone_thresholds"',
        "step_key",
        '"aq_thresholds"',
        '"alert_add"',
        '"options_gates"',
        '"options_thresholds"',
        '"options_zone_edit"',
        '"options_humidifier_edit"',
        '"options_aq_edit"',
        '"options_alert_add"',
        '"options_alert_edit"',
        '"options_slope"',
    ):
        assert f"_remember_advanced_input(self._advanced_inputs, {step_id}, user_input)" in config_source


def test_readme_uses_manifest_version_badge_not_static_ha_compatibility_badge():
    readme_source = (ROOT / "README.md").read_text()

    assert "dynamic/json" in readme_source
    assert "manifest.json" in readme_source
    assert "query=%24.version" in readme_source
    assert "Home%20Assistant-2026.4.3%2B" not in readme_source


def test_dump_cards_without_layout_exports_all_cached_layouts():
    services_mod = _load_services_module()
    entry = SimpleNamespace(entry_id=ENTRY_ID)
    cards = {
        "v2_mobile": "mobile-card",
        "v2_tablet": "tablet-card",
        "v1_mobile": "legacy-card",
        "view_cards_button": "button-card",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        hass = _DumpCardsHass(tmpdir, [entry], {ENTRY_ID: cards})
        written = asyncio.run(
            services_mod._dump_cards_to_file(
                hass,
                entry_id=None,
                filename="humidity_intelligence_cards",
                layout=None,
            )
        )

        assert written == [
            "/config/humidity_intelligence_cards_v2_mobile.yaml",
            "/config/humidity_intelligence_cards_v2_tablet.yaml",
            "/config/humidity_intelligence_cards_v1_mobile.yaml",
            "/config/humidity_intelligence_cards_view_cards_button.yaml",
        ]
        for layout, yaml in cards.items():
            path = pathlib.Path(tmpdir) / f"humidity_intelligence_cards_{layout}.yaml"
            assert path.read_text() == yaml


def test_dump_cards_with_layout_exports_only_requested_layout():
    services_mod = _load_services_module()
    entry = SimpleNamespace(entry_id=ENTRY_ID)
    cards = {
        "v2_mobile": "mobile-card",
        "v2_tablet": "tablet-card",
        "v1_mobile": "legacy-card",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        hass = _DumpCardsHass(tmpdir, [entry], {ENTRY_ID: cards})
        written = asyncio.run(
            services_mod._dump_cards_to_file(
                hass,
                entry_id=None,
                filename="humidity_intelligence_cards",
                layout="v2_tablet",
            )
        )

        assert written == ["/config/humidity_intelligence_cards_v2_tablet.yaml"]
        assert (pathlib.Path(tmpdir) / "humidity_intelligence_cards_v2_tablet.yaml").read_text() == "tablet-card"
        assert not (pathlib.Path(tmpdir) / "humidity_intelligence_cards_v2_mobile.yaml").exists()
        assert not (pathlib.Path(tmpdir) / "humidity_intelligence_cards_v1_mobile.yaml").exists()


def test_alert_configuration_contract_uses_internal_sources():
    const_source = (ROOT / "const.py").read_text()
    config_source = (ROOT / "config_flow.py").read_text()
    services_source = (ROOT / "services.py").read_text()
    strings_source = (ROOT / "strings.json").read_text()
    translation_source = (ROOT / "translations" / "en.json").read_text()

    for source in (const_source, config_source, strings_source, translation_source):
        assert '"custom_binary"' not in source
        assert '"custom_trigger"' not in source
        assert "custom_trigger_required" not in source

    assert "Internal HI alert source" in strings_source
    assert "Visual Indicator Rule" in strings_source
    assert "Frontend Dependencies" in strings_source
    assert "Frontend Dependencies" in translation_source
    assert "frontend dependencies" in strings_source
    assert "frontend dependencies" in translation_source
    assert "frontend_dependency_resources" in services_source
    assert '"dependency_resources"' not in services_source
    assert "CONF_SHOW_TEMPERATURE_CHIPS" in const_source
    assert "DEFAULT_SHOW_TEMPERATURE_CHIPS" in const_source
    assert "show_temperature_chips" in config_source
    assert "Show temperature chip row in Air Control" in strings_source
    assert "Show temperature chip row in Air Control" in translation_source
    assert "Humidity Intelligence target profile mode" in strings_source
    assert "Humidity custom target low" in strings_source
    assert "HI target profile mode" not in strings_source
    assert "HI custom target low" not in strings_source
    assert "diagnostics_summary" in services_source
    assert "visual_alerts" in services_source
    assert "active_alert_resolution" in services_source
    sensor_source = (ROOT / "sensor.py").read_text()
    assert '"config": _sanitize_json(config)' not in sensor_source
    assert '"entity_map": _sanitize_json(entity_map)' not in sensor_source
    assert '"alert_telemetry": _sanitize_json(alert_telemetry)' not in sensor_source
    assert "_compact_diagnostics_summary" in sensor_source
    assert "Use service humidity_intelligence.dump_diagnostics" in sensor_source
    assert "HUMIDITY_ALERT_FLASH_COUNT = 10" in (ROOT / "automations" / "engine.py").read_text()
    assert "HUMIDITY_ALERT_REPEAT_MINUTES = 30" in (ROOT / "automations" / "engine.py").read_text()
    assert "alert_remove" in config_source
    assert "options_alert_remove" in config_source
    assert "Remove alert visual rule" in strings_source
    assert "alert_handling_enabled" in strings_source
    assert "Boost settings should normally be higher" in config_source
    assert "existing configured ventilation outputs" in strings_source


def test_level_average_ignores_unknown_unavailable_and_non_numeric_states():
    engine_mod, _ = _load_target_modules()
    entry_data = _base_entry_data()
    entry_data["telemetry"].extend(
        [
            {"entity_id": "sensor.l1_iaq_unavailable", "sensor_type": "iaq", "level": "level1", "room": "Kitchen"},
            {"entity_id": "sensor.l1_iaq_text", "sensor_type": "iaq", "level": "level1", "room": "Kitchen"},
            {"entity_id": "sensor.l1_iaq_bad", "sensor_type": "iaq", "level": "level1", "room": "Kitchen"},
        ]
    )
    entry = SimpleNamespace(entry_id=ENTRY_ID, data=entry_data, options={})
    hass = _FakeHass(
        entry,
        {
            "sensor.l1_iaq": _FakeState("unknown"),
            "sensor.l1_iaq_unavailable": _FakeState("unavailable"),
            "sensor.l1_iaq_text": _FakeState("57.2"),
            "sensor.l1_iaq_bad": _FakeState("not_a_number"),
        },
    )

    engine = engine_mod.HIAutomationEngine(hass, entry)
    assert engine._level_avg("iaq", "level1") == 57.2


if __name__ == "__main__":
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for name, test in tests:
        test()
    print(f"{len(tests)} direct sanity checks passed.")
