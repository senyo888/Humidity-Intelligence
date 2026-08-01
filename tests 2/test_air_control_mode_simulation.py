"""Direct backend simulation checks for HI Air Control Mode sensor truth."""

from __future__ import annotations

from types import SimpleNamespace

from hi_runtime_fixtures import (
    AIR_CONTROL_MODE_ENTITY_ID,
    AIR_CONTROL_REASON_ENTITY_ID,
    run_air_control_simulation,
)
from test_runtime_card_sanity import (
    ENTRY_ID as RUNTIME_ENTRY_ID,
    _FakeHass,
    _FakeState,
    _base_entry_data,
    _load_target_modules,
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
    display = result.reason_sensor_attrs["display_reason"]
    assert display["schema"] == "hi.reason.v1"
    assert display["family"] == "normal"
    assert display["variant"] == "monitoring"
    assert display["headline"] == "Monitoring"
    assert "HI is monitoring; no ventilation response is selected." in [
        line["text"] for line in display["lines"]
    ]


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
    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "telemetry"
    assert display["attention"] == "degraded"
    assert "Required humidity telemetry is unavailable." in [
        line["text"] for line in display["lines"]
    ]


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
    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "zone"
    assert display["headline"] == "Zone 1 response selected"
    text = " ".join(line["text"] for line in display["lines"])
    assert "percentage points above the home average" in text
    assert "difference of 5 percentage points" in text
    assert "Fan-output isolation is active" in text
    assert "Trigger detail" not in text
    assert ">=" not in text


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
    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "air_quality"
    text = " ".join(line["text"] for line in display["lines"])
    assert "IAQ is 70" in text
    assert "fan-output isolation suppresses" in text
    assert "Trigger detail" not in text
    assert "<=" not in text


def test_pm25_aq_copy_survives_raw_entity_id_privacy_validation():
    result = run_air_control_simulation(
        telemetry_overrides={"sensor.hi_fixture_level1_pm25": 48},
        config_overrides={
            "aq": {
                "level1": {
                    "triggers": ["pm25_high"],
                    "thresholds": {"pm25_high": 25},
                }
            }
        },
    )

    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "air_quality"
    text = " ".join(line["text"] for line in display["lines"])
    assert "PM2.5 is 48 µg/m³" in text
    assert "sensor.hi_fixture_level1_pm25" not in text


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
    assert disabled.reason_sensor_attrs["display_reason"]["family"] == "disabled"
    assert manual.mode_sensor_state == "manual_override"
    assert manual.mode_sensor_attrs["display"] == "MANUAL OVERRIDE"
    assert "Manual override is enabled" in manual.reason_sensor_state
    assert manual.lower_lane_trace == []
    assert manual.reason_sensor_attrs["display_reason"]["family"] == "manual"


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
    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "gate"
    assert display["variant"] == "presence_away"
    assert display["attention"] == "hold"


def test_pause_publishes_backend_owned_hold_explanation():
    result = run_air_control_simulation(
        timer_overrides={"air_control_pause": "active"},
    )

    assert result.mode_sensor_state == "paused"
    assert result.mode_sensor_attrs["display"] == "PAUSED"
    assert result.runtime_mode == "normal"
    assert "Pause is active" in result.reason_sensor_state
    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "pause"
    assert display["attention"] == "hold"
    assert "Pause remains active until the pause timer ends." in [
        line["text"] for line in display["lines"]
    ]


def test_alert_only_mode_has_backend_owned_capability_explanation():
    result = run_air_control_simulation(
        config_overrides={"alert_only_mode": True},
    )

    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "normal"
    assert display["variant"] == "alert_only_monitoring"
    assert display["headline"] == "Monitoring alerts"
    assert "Monitor + Alerts Only mode is active" in display["lines"][0]["text"]


def test_configured_level_label_is_used_by_backend_aq_copy():
    result = run_air_control_simulation(
        telemetry_overrides={"sensor.hi_fixture_level1_iaq": 70},
        config_overrides={
            "level_labels": {"level1": "Ground Floor", "level2": "Loft"},
        },
    )

    text = " ".join(
        line["text"]
        for line in result.reason_sensor_attrs["display_reason"]["lines"]
    )
    assert "Ground Floor" in text
    assert "Downstairs" not in text


def test_unmapped_active_alert_elevates_normal_presentation_to_degraded():
    result = run_air_control_simulation(
        telemetry_overrides={"sensor.hi_fixture_kitchen_humidity": 70},
        config_overrides={"zones": {"zone1": {"outputs": []}}},
    )

    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "normal"
    assert display["variant"] == "monitoring_with_degraded_alert"
    assert display["attention"] == "degraded"
    assert display["headline"] == "Monitoring with limited alert response"
    text = " ".join(line["text"] for line in display["lines"])
    assert "could not be mapped to a configured zone output" in text


def test_output_summary_uses_exact_singular_plural_and_friendly_name_copy():
    engine_mod, _register_mod = _load_target_modules()
    entry = SimpleNamespace(
        entry_id=RUNTIME_ENTRY_ID,
        data=_base_entry_data(),
        options={},
    )
    hass = _FakeHass(
        entry,
        {
            "fan.named": _FakeState("off", {"friendly_name": "Kitchen Extractor"}),
            "fan.named_second": _FakeState("off", {"friendly_name": "Hall Extractor"}),
        },
    )
    engine = engine_mod.HIAutomationEngine(hass, entry)

    assert engine._presentation_output_summary(
        ["fan.unlabelled"],
        generic="configured zone ventilation output",
    ) == "the configured zone ventilation output"
    assert engine._presentation_output_summary(
        ["fan.unlabelled", "fan.unlabelled_second"],
        generic="configured zone ventilation output",
    ) == "2 configured zone ventilation outputs"
    assert engine._presentation_output_summary(
        ["fan.named"],
        generic="configured zone ventilation output",
    ) == "Kitchen Extractor"
    assert engine._presentation_output_summary(
        ["fan.named", "fan.named_second"],
        generic="configured zone ventilation output",
    ) == "Kitchen Extractor and Hall Extractor"


def test_every_environmental_alert_family_keeps_structured_reason_truth():
    engine_mod, _register_mod = _load_target_modules()
    entry = SimpleNamespace(
        entry_id=RUNTIME_ENTRY_ID,
        data=_base_entry_data(),
        options={},
    )
    hass = _FakeHass(
        entry,
        {
            "sensor.kitchen_h": _FakeState(90),
            "sensor.hall_h": _FakeState(50),
            "sensor.bed_h": _FakeState(50),
            "sensor.kitchen_t": _FakeState(21),
            "sensor.hall_t": _FakeState(21),
            "sensor.bed_t": _FakeState(20),
            "sensor.l1_iaq": _FakeState(90),
            "sensor.co_val": _FakeState(0),
        },
    )
    engine = engine_mod.HIAutomationEngine(hass, entry)
    expected = {
        "humidity_danger": ("at or above", "% threshold"),
        "condensation_danger": ("at or below", "°C Winter danger point"),
        "condensation_risk": ("at or below", "°C Winter risk point"),
        "mould_danger": ("at or above", "danger threshold for the Winter profile"),
        "mould_risk": ("at or above", "risk threshold for the Winter profile"),
    }

    for trigger_type, phrases in expected.items():
        detail = engine._alert_detail(
            0,
            {
                "enabled": True,
                "trigger_type": trigger_type,
                "room": "Kitchen",
                "threshold": None,
            },
        )
        assert detail is not None, trigger_type
        assert detail["measured_value"] is not None, trigger_type
        assert detail["threshold"] is not None, trigger_type
        headline, variant, lines = engine._alert_display_content([detail])
        contract = engine_mod.build_display_reason(
            engine._make_reason_facts(
                "alert",
                variant,
                "critical",
                headline,
                lines,
            )
        )
        text = " ".join(line["text"] for line in contract["lines"])
        for phrase in phrases:
            assert phrase in text, (trigger_type, phrase, text)
        assert "The alert comes from Kitchen and maps to Zone 1." in text
        assert "source room" not in text
        assert "resolved scope" not in text
        assert "sensor." not in text, trigger_type


def test_presence_unavailable_is_degraded_fail_closed_without_claiming_away():
    result = run_air_control_simulation(
        config_overrides={
            "presence_gate": {
                "enabled": True,
                "entities": ["binary_sensor.hi_fixture_presence"],
                "present_states": ["on"],
                "away_states": ["off"],
            }
        },
        state_overrides={"binary_sensor.hi_fixture_presence": "unavailable"},
    )

    _assert_mode(result, "global_gate", "GLOBAL GATE", "Presence gate is active")
    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "gate"
    assert display["variant"] == "presence_unavailable"
    assert display["attention"] == "degraded"
    text = " ".join(line["text"] for line in display["lines"])
    assert "unknown or unavailable" in text
    assert "Occupancy cannot be confirmed" in text
    assert (
        "Automatic control is blocked. Output isolation is on, so HI did not send "
        "the affected reset commands."
    ) in text
    assert "nobody" not in text.lower()
    assert "away" not in text.lower()
    assert result.lower_lane_trace == []


def test_one_present_presence_source_still_allows_control_when_another_is_unavailable():
    result = run_air_control_simulation(
        config_overrides={
            "presence_gate": {
                "enabled": True,
                "entities": [
                    "binary_sensor.hi_fixture_presence",
                    "binary_sensor.hi_fixture_presence_backup",
                ],
                "present_states": ["on"],
                "away_states": ["off"],
            }
        },
        state_overrides={
            "binary_sensor.hi_fixture_presence": "on",
            "binary_sensor.hi_fixture_presence_backup": "unavailable",
        },
    )

    assert result.mode_sensor_state == "normal"
    assert result.reason_sensor_attrs["display_reason"]["family"] == "normal"


def test_incomplete_presence_evidence_is_not_presented_as_confirmed_away():
    result = run_air_control_simulation(
        config_overrides={
            "presence_gate": {
                "enabled": True,
                "entities": [
                    "binary_sensor.hi_fixture_presence",
                    "binary_sensor.hi_fixture_presence_backup",
                ],
                "present_states": ["on"],
                "away_states": ["off"],
            }
        },
        state_overrides={
            "binary_sensor.hi_fixture_presence": "off",
            "binary_sensor.hi_fixture_presence_backup": "unavailable",
        },
    )

    display = result.reason_sensor_attrs["display_reason"]
    assert display["variant"] == "presence_unavailable"
    assert display["attention"] == "degraded"
    text = " ".join(line["text"] for line in display["lines"])
    assert "evidence is incomplete" in text
    assert "away" not in text.lower()


def test_presenter_failure_preserves_runtime_and_legacy_reason_truth():
    scenarios = {
        "normal": {},
        "zone": {
            "telemetry_overrides": {"sensor.hi_fixture_kitchen_humidity": 61},
        },
        "air_quality": {
            "telemetry_overrides": {"sensor.hi_fixture_level1_iaq": 70},
        },
        "actionable_alert": {
            "telemetry_overrides": {
                "sensor.hi_fixture_kitchen_humidity": 70,
                "sensor.hi_fixture_hallway_humidity": 50,
                "sensor.hi_fixture_bedroom_humidity": 50,
            },
        },
        "disabled": {
            "boolean_overrides": {"air_control_enabled": False},
        },
        "manual": {
            "boolean_overrides": {"air_control_manual_override": True},
        },
        "presence_gate": {
            "config_overrides": {
                "presence_gate": {
                    "enabled": True,
                    "entities": ["binary_sensor.hi_fixture_presence"],
                    "present_states": ["on"],
                    "away_states": ["off"],
                }
            },
            "state_overrides": {"binary_sensor.hi_fixture_presence": "off"},
        },
        "pause": {
            "timer_overrides": {"air_control_pause": "active"},
        },
        "telemetry_unavailable": {
            "telemetry_overrides": {
                "sensor.hi_fixture_kitchen_humidity": "unavailable",
                "sensor.hi_fixture_hallway_humidity": "unavailable",
                "sensor.hi_fixture_bedroom_humidity": "unavailable",
            },
        },
        "co_emergency": {
            "telemetry_overrides": {"sensor.hi_fixture_co_ppm": 16},
            "co_pressure": True,
        },
    }

    for scenario, kwargs in scenarios.items():
        normal = run_air_control_simulation(**kwargs)
        assert "display_reason" in normal.reason_sensor_attrs, scenario
        assert len(normal.reason_sensor_attrs["display_reason"]["lines"]) <= 6, scenario
        for failure_stage, failure_kwargs in (
            ("presenter", {"display_presenter_failure": True}),
            ("fact_collection", {"display_fact_failure": True}),
        ):
            failed = run_air_control_simulation(**kwargs, **failure_kwargs)
            context = f"{scenario}:{failure_stage}"

            assert failed.runtime_mode == normal.runtime_mode, context
            assert failed.runtime_display == normal.runtime_display, context
            assert failed.runtime_reason == normal.runtime_reason, context
            assert failed.lower_lane_trace == normal.lower_lane_trace, context
            assert failed.fan_service_calls == normal.fan_service_calls, context
            assert failed.all_service_calls == normal.all_service_calls, context
            assert failed.reason_sensor_state == normal.reason_sensor_state, context
            assert failed.reason_sensor_attrs.get("full_reason") == normal.reason_sensor_attrs.get(
                "full_reason"
            ), context
            assert "display_reason" not in failed.reason_sensor_attrs, context


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
    display = result.reason_sensor_attrs["display_reason"]
    assert display["family"] == "co_emergency"
    assert display["attention"] == "critical"
    text = " ".join(line["text"] for line in display["lines"])
    assert "at or above the 15 ppm threshold" in text
    assert "must remain below 10 ppm for two minutes" in text


if __name__ == "__main__":
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for name, test in tests:
        test()
    print(f"{len(tests)} air-control mode simulation checks passed.")
