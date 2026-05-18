"""Direct sanity checks for HI slope sensor startup behavior."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types
from types import SimpleNamespace


ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = "hi_slope_testpkg"


def _install_homeassistant_stubs() -> None:
    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    sensor_mod = types.ModuleType("homeassistant.components.sensor")
    config_entries = types.ModuleType("homeassistant.config_entries")
    core = types.ModuleType("homeassistant.core")
    helpers = types.ModuleType("homeassistant.helpers")
    device_registry = types.ModuleType("homeassistant.helpers.device_registry")
    event = types.ModuleType("homeassistant.helpers.event")
    util = types.ModuleType("homeassistant.util")
    const = types.ModuleType("homeassistant.const")

    class HomeAssistant:
        pass

    class ConfigEntry:
        pass

    class DeviceInfo(dict):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    class SensorEntity:
        def __init__(self):
            self.entity_id = None

        def async_write_ha_state(self):
            return None

    class SensorStateClass:
        MEASUREMENT = "measurement"

    class UnitOfTemperature:
        CELSIUS = "°C"
        FAHRENHEIT = "°F"

    def async_track_state_change_event(*args, **kwargs):
        return lambda: None

    def async_track_time_interval(*args, **kwargs):
        return lambda: None

    def slugify(value):
        import re

        return re.sub(r"^_+|_+$", "", re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()))

    core.HomeAssistant = HomeAssistant
    config_entries.ConfigEntry = ConfigEntry
    device_registry.DeviceInfo = DeviceInfo
    sensor_mod.SensorEntity = SensorEntity
    sensor_mod.SensorStateClass = SensorStateClass
    event.async_track_state_change_event = async_track_state_change_event
    event.async_track_time_interval = async_track_time_interval
    util.slugify = slugify
    const.UnitOfTemperature = UnitOfTemperature

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.components"] = components
    sys.modules["homeassistant.components.sensor"] = sensor_mod
    sys.modules["homeassistant.config_entries"] = config_entries
    sys.modules["homeassistant.core"] = core
    sys.modules["homeassistant.helpers"] = helpers
    sys.modules["homeassistant.helpers.device_registry"] = device_registry
    sys.modules["homeassistant.helpers.event"] = event
    sys.modules["homeassistant.util"] = util
    sys.modules["homeassistant.const"] = const


def _install_package_scaffold() -> None:
    pkg = types.ModuleType(PKG)
    pkg.__path__ = [str(ROOT)]
    sys.modules[PKG] = pkg

    sensors_pkg = types.ModuleType(f"{PKG}.sensors")
    sensors_pkg.__path__ = [str(ROOT / "sensors")]
    sys.modules[f"{PKG}.sensors"] = sensors_pkg

    helpers_pkg = types.ModuleType(f"{PKG}.helpers")
    helpers_pkg.__path__ = [str(ROOT / "helpers")]
    sys.modules[f"{PKG}.helpers"] = helpers_pkg


def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_slope_module():
    _install_homeassistant_stubs()
    _install_package_scaffold()
    _load_module(f"{PKG}.const", ROOT / "const.py")
    _load_module(f"{PKG}.helpers.parsing", ROOT / "helpers" / "parsing.py")
    return _load_module(f"{PKG}.sensors.slope", ROOT / "sensors" / "slope.py")


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
    class units:
        temperature_unit = "°C"


class _FakeHass:
    def __init__(self, states):
        self.states = _FakeStates(states)
        self.data = {}
        self.config = _FakeConfig()


def test_slope_entities_are_seeded_immediately_on_setup():
    slope_mod = _load_slope_module()
    entry = SimpleNamespace(
        entry_id="entry123",
        data={
            "telemetry": [
                {
                    "entity_id": "sensor.wirelesstag_willow_s_room_temperature",
                    "sensor_type": "temperature",
                    "room": "Willow's Room",
                }
            ],
            "slope": {
                "mode": "hi_calculates",
                "source_entities": ["sensor.wirelesstag_willow_s_room_temperature"],
            },
        },
        options={},
    )
    hass = _FakeHass(
        {
            "sensor.wirelesstag_willow_s_room_temperature": _FakeState(
                "20.21",
                {"unit_of_measurement": "°C"},
            )
        }
    )

    sensors, slope_sources, slope_map = slope_mod.build_slope_entities(hass, entry)

    assert slope_sources == ["sensor.wirelesstag_willow_s_room_temperature"]
    assert slope_map == {
        "sensor.wirelesstag_willow_s_room_temperature": "sensor.hi_willow_s_room_temperature_slope"
    }
    assert len(sensors) == 1
    sensor = sensors[0]
    assert sensor._attr_native_value == 0.0
    assert sensor._attr_extra_state_attributes == {
        "source_entity": "sensor.wirelesstag_willow_s_room_temperature",
        "window_minutes": 60,
        "sample_count": 2,
    }


if __name__ == "__main__":
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for name, test in tests:
        test()
    print(f"{len(tests)} slope sanity checks passed.")
