"""Direct backend simulation checks for HI Air Control Mode sensor truth."""

from __future__ import annotations

from hi_runtime_fixtures import (
    AIR_CONTROL_MODE_ENTITY_ID,
    AIR_CONTROL_REASON_ENTITY_ID,
    run_air_control_simulation,
)


def _assert_mode(result, expected_mode: str, expected_display: str, *reason_parts: str) -> None:
    assert result.mode_entity_id == AIR_CONTROL_MODE_ENTITY_ID
    assert result.reason_entity_id == AIR_CONTROL_REASON_ENTITY_ID
    assert result.mode_sensor_state == expected_mode
    assert result.mode_sensor_attrs["display"] == expected_display
    assert result.runtime_mode == expected_mode
    for part in reason_parts:
        assert part in result.reason_sensor_state or part in (result.reason_sensor_attrs.get("full_reason") or "")


def test_normal_baseline_publishes_normal_air_control_mode_without_output_writes():
    result = run_air_control_simulation()

    _assert_mode(result, "normal", "NORMAL", "no lane currently needs to run")
    assert result.fan_service_calls == []
    assert result.co_pressure_opted_in is False
    assert result.telemetry["sensor.hi_fixture_co_ppm"] == 0


def test_runtime_simulation_resets_to_baseline_between_runs():
    pressured = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_kitchen_humidity": 61,
            "sensor.hi_fixture_level1_iaq": 70,
        }
    )
    baseline = run_air_control_simulation()

    assert pressured.mode_sensor_state != baseline.mode_sensor_state
    _assert_mode(baseline, "normal", "NORMAL", "no lane currently needs to run")
    assert baseline.telemetry["sensor.hi_fixture_kitchen_humidity"] == 50
    assert baseline.telemetry["sensor.hi_fixture_level1_iaq"] == 90
    assert baseline.telemetry["sensor.hi_fixture_co_ppm"] == 0


def test_required_humidity_unavailable_publishes_telemetry_unavailable():
    result = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_kitchen_humidity": "unavailable",
            "sensor.hi_fixture_hallway_humidity": "unknown",
            "sensor.hi_fixture_bedroom_humidity": "unavailable",
        }
    )

    _assert_mode(result, "telemetry_unavailable", "TELEMETRY UNAVAILABLE", "Required humidity telemetry is unavailable")
    assert result.lower_lane_trace == []
    assert result.fan_service_calls == []


def test_configured_temperature_unavailable_publishes_telemetry_unavailable():
    result = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_kitchen_temperature": "unavailable",
            "sensor.hi_fixture_hallway_temperature": "unknown",
            "sensor.hi_fixture_bedroom_temperature": "unavailable",
        }
    )

    _assert_mode(result, "telemetry_unavailable", "TELEMETRY UNAVAILABLE", "Required temperature telemetry is unavailable")
    assert result.lower_lane_trace == []
    assert result.fan_service_calls == []


def test_zone_pressure_uses_distinct_room_and_house_values_to_select_zone1():
    result = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_kitchen_humidity": 61,
            "sensor.hi_fixture_hallway_humidity": 45,
            "sensor.hi_fixture_bedroom_humidity": 45,
        }
    )

    _assert_mode(result, "cooking", "Zone 1", "Humidity delta")
    assert result.runtime_mode == "cooking"
    assert result.fan_service_calls == []
    assert result.lower_lane_trace == ["_handle_alerts", "_handle_humidifiers", "_handle_zone_by_key:zone1"]


def test_zone2_pressure_is_representable_when_zone1_is_idle():
    result = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_kitchen_humidity": 45,
            "sensor.hi_fixture_hallway_humidity": 45,
            "sensor.hi_fixture_bedroom_humidity": 61,
        }
    )

    _assert_mode(result, "bathroom", "Zone 2", "Humidity delta")
    assert result.fan_service_calls == []
    assert result.lower_lane_trace == [
        "_handle_alerts",
        "_handle_humidifiers",
        "_handle_zone_by_key:zone1",
        "_handle_zone_by_key:zone2",
    ]


def test_aq_pressure_is_independent_when_zone_lanes_are_idle():
    result = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_level1_iaq": 70,
        }
    )

    _assert_mode(result, "air_quality", "AIR QUALITY", "AQ is active", "Trigger detail")
    assert result.fan_service_calls == []
    assert result.lower_lane_trace == [
        "_handle_alerts",
        "_handle_humidifiers",
        "_handle_zone_by_key:zone1",
        "_handle_zone_by_key:zone2",
        "_handle_aq",
    ]


def test_disabled_and_manual_gates_dominate_lower_lane_pressure():
    disabled = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_kitchen_humidity": 61,
            "sensor.hi_fixture_level1_iaq": 70,
        },
        boolean_overrides={"air_control_enabled": False},
    )
    manual = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_kitchen_humidity": 61,
            "sensor.hi_fixture_level1_iaq": 70,
        },
        boolean_overrides={"air_control_manual_override": True},
    )

    assert disabled.mode_sensor_state == "disabled"
    assert disabled.mode_sensor_attrs["display"] == "DISABLED"
    assert "System control is disabled" in disabled.reason_sensor_state
    assert disabled.lower_lane_trace == []
    assert manual.mode_sensor_state == "manual_override"
    assert manual.mode_sensor_attrs["display"] == "MANUAL OVERRIDE"
    assert "Manual override is enabled" in manual.reason_sensor_state
    assert manual.lower_lane_trace == []


def test_global_gate_publishes_global_gate_mode_before_lower_lanes():
    result = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_kitchen_humidity": 61,
            "sensor.hi_fixture_level1_iaq": 70,
        },
        config_overrides={
            "presence_gate": {
                "enabled": True,
                "entities": ["binary_sensor.hi_fixture_presence"],
                "present_states": ["on"],
                "away_states": ["off"],
            }
        },
        state_overrides={
            "binary_sensor.hi_fixture_presence": "off",
        },
    )

    _assert_mode(result, "global_gate", "GLOBAL GATE", "Presence gate is active")
    assert result.lower_lane_trace == []


def test_co_emergency_pressure_is_opt_in_and_overrides_manual_gate():
    result = run_air_control_simulation(
        telemetry_overrides={
            "sensor.hi_fixture_co_ppm": 16,
            "sensor.hi_fixture_kitchen_humidity": 61,
            "sensor.hi_fixture_level1_iaq": 70,
        },
        boolean_overrides={"air_control_manual_override": True},
        co_pressure=True,
    )

    _assert_mode(result, "co_emergency", "CO EMERGENCY", "CO emergency protection is active")
    assert result.co_pressure_opted_in is True
    assert result.lower_lane_trace == []
    assert result.fan_service_calls == []


if __name__ == "__main__":
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for name, test in tests:
        test()
    print(f"{len(tests)} air-control mode simulation checks passed.")
