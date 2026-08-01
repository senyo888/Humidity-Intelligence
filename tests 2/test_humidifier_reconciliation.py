"""Failing-first and regression checks for humidifier output reconciliation."""

from __future__ import annotations

import asyncio
import copy
from datetime import datetime, timedelta
from pathlib import Path
from types import MethodType, SimpleNamespace

from test_runtime_card_sanity import (
    ENTRY_ID,
    _FakeHass,
    _FakeState,
    _base_entry_data,
    _load_services_module,
    _load_target_modules,
)

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_ROOT = ROOT / "custom_components" / "humidity_intelligence"


def _entry_with_humidifiers(humidifiers):
    data = _base_entry_data()
    data["alert_handling_enabled"] = False
    data["alerts"] = []
    data["zones"] = {}
    data["aq"] = {}
    data["humidifiers"] = humidifiers
    return SimpleNamespace(entry_id=ENTRY_ID, data=data, options={})


def _states(*, level1=40, level2=40, outputs=None):
    values = {
        "sensor.kitchen_h": _FakeState(level1),
        "sensor.hall_h": _FakeState(level1),
        "sensor.bed_h": _FakeState(level2),
        "sensor.kitchen_t": _FakeState(21),
        "sensor.hall_t": _FakeState(21),
        "sensor.bed_t": _FakeState(20),
        "sensor.l1_iaq": _FakeState(90),
        "sensor.co_val": _FakeState(0),
    }
    values.update(outputs or {})
    return values


def _humidifier_calls(hass, *, entity_id=None, service=None):
    calls = [
        call
        for call in hass.services.calls
        if call[0] in {"humidifier", "fan", "switch"}
        and (entity_id is None or call[2].get("entity_id") == entity_id)
        and (service is None or call[1] == service)
    ]
    return calls


def test_restored_demand_with_observed_output_off_dispatches_reconciliation():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["humidifier.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(
                level1=47,
                outputs={"humidifier.level1": _FakeState("off")},
            ),
        )
        demand = hass.data["humidity_intelligence"][ENTRY_ID]["hi_input_booleans"][
            "air_downstairs_humidifier_active"
        ]
        demand.is_on = True
        engine = engine_mod.HIAutomationEngine(hass, entry)
        try:
            await engine._evaluate()
            assert demand.is_on
            assert len(
                _humidifier_calls(
                    hass,
                    entity_id="humidifier.level1",
                    service="turn_on",
                )
            ) == 1
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            assert runtime["humidifier_status"]["lanes"]["level1"]["demand"] == "requested"
            assert runtime["humidifier_status"]["lanes"]["level1"][
                "reconciliation"
            ] in {"requested", "retrying"}
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_shared_output_uses_aggregated_demand_and_one_write_per_cycle():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["humidifier.shared"],
                    "band_adjust": 0,
                },
                "level2": {
                    "enabled": True,
                    "outputs": ["humidifier.shared"],
                    "band_adjust": 0,
                },
            }
        )
        hass = _FakeHass(
            entry,
            _states(outputs={"humidifier.shared": _FakeState("off")}),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        try:
            await engine._evaluate()
            assert len(
                _humidifier_calls(
                    hass,
                    entity_id="humidifier.shared",
                    service="turn_on",
                )
            ) == 1

            hass.states._values["humidifier.shared"] = _FakeState("on")
            await engine._evaluate()
            hass.states._values["sensor.kitchen_h"] = _FakeState(55)
            hass.states._values["sensor.hall_h"] = _FakeState(55)
            await engine._evaluate()

            assert not _humidifier_calls(
                hass,
                entity_id="humidifier.shared",
                service="turn_off",
            )
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            assert runtime["humidifier_status"]["lanes"]["level1"]["demand"] == "inactive"
            assert runtime["humidifier_status"]["lanes"]["level2"]["demand"] == "requested"
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_two_independent_lane_outputs_dispatch_once_each():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                },
                "level2": {
                    "enabled": True,
                    "outputs": ["humidifier.level2"],
                    "band_adjust": 0,
                },
            }
        )
        hass = _FakeHass(
            entry,
            _states(
                outputs={
                    "switch.level1": _FakeState("off"),
                    "humidifier.level2": _FakeState("off"),
                }
            ),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        try:
            await engine._evaluate()
            assert len(
                _humidifier_calls(
                    hass,
                    entity_id="switch.level1",
                    service="turn_on",
                )
            ) == 1
            assert len(
                _humidifier_calls(
                    hass,
                    entity_id="humidifier.level2",
                    service="turn_on",
                )
            ) == 1
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            assert runtime["humidifier_status"]["lanes"]["level1"]["demand"] == "requested"
            assert runtime["humidifier_status"]["lanes"]["level2"]["demand"] == "requested"
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_configured_output_is_an_evaluation_source_but_demand_helper_is_not():
    engine_mod, _register_mod = _load_target_modules()
    entry = _entry_with_humidifiers(
        {
            "level1": {
                "enabled": True,
                "outputs": ["switch.level1"],
                "band_adjust": 0,
            }
        }
    )
    hass = _FakeHass(entry, _states(outputs={"switch.level1": _FakeState("off")}))
    for key, entity in hass.data["humidity_intelligence"][ENTRY_ID][
        "hi_input_booleans"
    ].items():
        entity.entity_id = f"switch.hi_{key}"
    engine = engine_mod.HIAutomationEngine(hass, entry)

    sources = engine._evaluation_sources()

    assert "switch.level1" in sources
    assert "switch.hi_air_downstairs_humidifier_active" not in sources


def test_missing_unknown_and_unavailable_outputs_do_not_receive_turn_on():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        for entity_id, state in (
            ("switch.missing", None),
            ("switch.unknown", _FakeState("unknown")),
            ("switch.unavailable", _FakeState("unavailable")),
            ("light.unsupported", _FakeState("off")),
        ):
            entry = _entry_with_humidifiers(
                {
                    "level1": {
                        "enabled": True,
                        "outputs": [entity_id],
                        "band_adjust": 0,
                    }
                }
            )
            output_states = {} if state is None else {entity_id: state}
            hass = _FakeHass(entry, _states(outputs=output_states))
            engine = engine_mod.HIAutomationEngine(hass, entry)
            try:
                await engine._evaluate()
                assert not [
                    call
                    for call in hass.services.calls
                    if call[2].get("entity_id") == entity_id
                ]
                runtime = hass.data["humidity_intelligence"][ENTRY_ID]
                assert runtime["humidifier_status"]["lanes"]["level1"][
                    "reconciliation"
                ] in {"degraded", "unknown"}
            finally:
                await engine.async_stop()

    asyncio.run(run())


def test_level_telemetry_loss_remains_degraded_when_house_average_is_available():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(
                level1="unavailable",
                level2=45,
                outputs={"switch.level1": _FakeState("off")},
            ),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        try:
            await engine._evaluate()

            assert not _humidifier_calls(
                hass,
                entity_id="switch.level1",
                service="turn_on",
            )
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            lane = runtime["humidifier_status"]["lanes"]["level1"]
            assert lane["demand"] == "inactive"
            assert lane["environmental_state"] == "unknown"
            assert lane["reconciliation"] == "degraded"
            assert lane["observed"] == "off"
            assert runtime["humidifier_status"]["overall"] == "degraded"
            summary = runtime["humidifier_reconciliation"]["summary"]
            assert summary["degraded_lanes"] == 1
            assert summary["unknown_lanes"] == 1
            assert runtime["humidifier_reconciliation"]["outputs"]["output_1"][
                "reconciliation"
            ] == "matched_off"
            display = runtime["runtime_display_reason"]
            display_text = " ".join(line["text"] for line in display["lines"])
            assert (
                "humidity data is unavailable, so HI cannot assess humidifier demand"
                in display_text
            )
            assert "Output reconciliation is degraded" not in display_text
            helper = runtime["hi_input_booleans"][
                "air_downstairs_humidifier_active"
            ]
            assert not helper.is_on
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_missing_humidifier_output_has_mapping_specific_display_truth():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": [],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(entry, _states())
        engine = engine_mod.HIAutomationEngine(hass, entry)
        try:
            await engine._evaluate()
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            lane = runtime["humidifier_status"]["lanes"]["level1"]
            assert lane["failure_category"] == "no_outputs"
            assert lane["reconciliation"] == "degraded"
            assert not _humidifier_calls(hass)
            display_text = " ".join(
                line["text"]
                for line in runtime["runtime_display_reason"]["lines"]
            )
            assert (
                "no humidifier output is configured, so no command was sent"
                in display_text
            )
            assert "Output reconciliation is degraded" not in display_text
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_normal_ventilation_mode_can_coexist_with_humidifier_demand():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["humidifier.level1"],
                    "band_adjust": 0,
                }
            }
        )
        entry.data["level_labels"] = {
            "level1": "Ground Floor",
            "level2": "Loft",
        }
        hass = _FakeHass(
            entry,
            _states(outputs={"humidifier.level1": _FakeState("on")}),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        try:
            await engine._evaluate()
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            assert runtime["runtime_mode"] == "normal"
            reason = runtime.get("runtime_reason_full") or runtime["runtime_reason"]
            assert "no ventilation lane currently needs to run" in reason
            assert "Home Assistant reports" in reason
            assert "physical moisture" in reason.lower()
            display = runtime["runtime_display_reason"]
            assert display["family"] == "normal"
            display_text = " ".join(
                [display["headline"]]
                + [line["text"] for line in display["lines"]]
            )
            assert "Output observed on" in display_text
            assert "Physical moisture output is not independently confirmed" in display_text
            assert "Ground Floor" in display_text
            assert "Downstairs" not in display_text
            assert "humidifier.level1" not in display_text
            assert len(display["lines"]) <= 6
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_reason_line_truncation_retains_material_truth_in_original_order():
    engine_mod, _register_mod = _load_target_modules()
    entry = _entry_with_humidifiers({})
    hass = _FakeHass(entry, _states())
    engine = engine_mod.HIAutomationEngine(hass, entry)
    secondary = [
        engine_mod.ReasonLine(
            "next",
            "system",
            f"normal.secondary_{index}",
            "selected",
            f"Secondary explanation {index}.",
        )
        for index in range(4)
    ]
    material = [
        engine_mod.ReasonLine(
            "why", "safety", "alert.safety_truth", "observed", "Safety truth."
        ),
        engine_mod.ReasonLine(
            "notice", "system", "alert.degraded_truth", "unmapped", "Degraded truth."
        ),
        engine_mod.ReasonLine(
            "notice", "ventilation", "isolation.fan_outputs", "blocked", "Isolation truth."
        ),
        engine_mod.ReasonLine(
            "action", "ventilation", "zone.output_selected", "selected", "Action truth."
        ),
        engine_mod.ReasonLine(
            "notice", "humidifier", "humidifier.output_on", "observed", "Observation truth."
        ),
        engine_mod.ReasonLine(
            "notice", "humidifier", "humidifier.retry_failed", "failed", "Failure truth."
        ),
    ]

    facts = engine._make_reason_facts(
        "normal",
        "monitoring",
        "neutral",
        "Monitoring",
        secondary + material,
    )
    codes = [line.code for line in facts.lines]

    assert facts.truncated is True
    assert len(facts.lines) == 8
    for line in material:
        assert line.code in codes
    assert codes == [
        line.code for line in secondary + material if line.code in set(codes)
    ]


def test_full_cycle_presenter_failures_do_not_change_humidifier_reconciliation():
    async def execute(failure_stage=None):
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(level1=40, outputs={"switch.level1": _FakeState("off")}),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        engine._monotonic = lambda: 1000.0
        scheduled = []
        engine._schedule_humidifier_retry = (
            lambda entity_id, when: scheduled.append((entity_id, when))
        )
        original_presenter = engine_mod.build_display_reason

        if failure_stage == "fact_collection":
            def fail_facts(self, *_args, **_kwargs):
                raise RuntimeError("fixture fact-collection failure")

            engine._runtime_display_facts = MethodType(fail_facts, engine)
        elif failure_stage == "presenter":
            def fail_presenter(_facts):
                raise RuntimeError("fixture presenter failure")

            engine_mod.build_display_reason = fail_presenter

        try:
            await engine._evaluate()
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            output = next(
                iter(runtime["humidifier_reconciliation"]["outputs"].values())
            )
            helper = runtime["hi_input_booleans"][
                "air_downstairs_humidifier_active"
            ]
            return {
                "calls": copy.deepcopy(hass.services.calls),
                "scheduled": list(scheduled),
                "technical_reason": runtime.get("runtime_reason_full")
                or runtime.get("runtime_reason"),
                "humidifier_status": copy.deepcopy(runtime["humidifier_status"]),
                "output_truth": {
                    key: copy.deepcopy(output.get(key))
                    for key in (
                        "desired",
                        "observed",
                        "reconciliation",
                        "dispatch_result",
                        "last_command_intent",
                        "attempts",
                        "maximum_attempts",
                        "failure_category",
                        "fault_latched",
                    )
                },
                "helper_active": helper.is_on,
                "display_present": "runtime_display_reason" in runtime,
            }
        finally:
            engine_mod.build_display_reason = original_presenter
            await engine.async_stop()

    async def run():
        baseline = await execute()
        fact_failure = await execute("fact_collection")
        presenter_failure = await execute("presenter")

        assert baseline["display_present"] is True
        for failure in (fact_failure, presenter_failure):
            assert failure["display_present"] is False
            assert {
                key: value
                for key, value in failure.items()
                if key != "display_present"
            } == {
                key: value
                for key, value in baseline.items()
                if key != "display_present"
            }

    asyncio.run(run())


def test_failed_display_publication_clears_stale_contract_and_keeps_new_technical_reason():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers({})
        hass = _FakeHass(entry, _states())
        engine = engine_mod.HIAutomationEngine(hass, entry)
        facts = engine_mod.ReasonFacts(
            family="normal",
            variant="monitoring",
            attention="neutral",
            headline="Monitoring",
            lines=(
                engine_mod.ReasonLine(
                    "why",
                    "system",
                    "normal.no_higher_priority_lane",
                    "selected",
                    "No higher-priority ventilation lane is selected.",
                ),
            ),
        )
        try:
            await engine._set_runtime_reason(
                "First technical reason.",
                display_facts_factory=lambda: facts,
            )
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            assert runtime["runtime_display_reason"]["headline"] == "Monitoring"

            def fail_fact_collection():
                raise RuntimeError("fixture presenter failure")

            await engine._set_runtime_reason(
                "Second technical reason.",
                display_facts_factory=fail_fact_collection,
            )

            assert runtime["runtime_reason"] == "Second technical reason."
            assert runtime["runtime_reason_full"] is None
            assert "runtime_display_reason" not in runtime
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_global_gates_alert_and_co_move_active_output_to_desired_off_truth():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        for scenario in (
            "control_disabled",
            "manual_override",
            "pause",
            "presence_gate",
            "time_gate",
            "telemetry_unavailable",
            "alert",
            "co_emergency",
        ):
            entry = _entry_with_humidifiers(
                {
                    "level1": {
                        "enabled": True,
                        "outputs": ["humidifier.level1"],
                        "band_adjust": 0,
                    }
                }
            )
            hass = _FakeHass(
                entry,
                _states(
                    outputs={"humidifier.level1": _FakeState("on")},
                ),
            )
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            helper = runtime["hi_input_booleans"][
                "air_downstairs_humidifier_active"
            ]
            helper.is_on = True
            engine = engine_mod.HIAutomationEngine(hass, entry)

            if scenario == "control_disabled":
                runtime["hi_input_booleans"]["air_control_enabled"].is_on = False
            elif scenario == "manual_override":
                runtime["hi_input_booleans"][
                    "air_control_manual_override"
                ].is_on = True
            elif scenario == "pause":
                runtime["hi_timers"]["air_control_pause"].native_value = "active"
            elif scenario == "presence_gate":
                engine.presence_gate = {
                    "enabled": True,
                    "entities": ["binary_sensor.home_presence"],
                    "present_states": ["on"],
                    "away_states": ["off"],
                }
                hass.states._values["binary_sensor.home_presence"] = _FakeState(
                    "off"
                )
            elif scenario == "time_gate":
                outside_start = (datetime.now() + timedelta(hours=1)).time()
                outside_end = (datetime.now() + timedelta(hours=2)).time()
                engine.time_gate = {
                    "enabled": True,
                    "start": outside_start,
                    "end": outside_end,
                    "outside_action": "safe_state",
                }
            elif scenario == "telemetry_unavailable":
                for entity_id in (
                    "sensor.kitchen_h",
                    "sensor.hall_h",
                    "sensor.bed_h",
                ):
                    hass.states._values[entity_id] = _FakeState("unavailable")
            elif scenario == "alert":
                async def active_alert():
                    return True, [
                        {
                            "label": "Humidity Danger",
                            "trigger_type": "humidity_danger",
                            "outputs": [],
                        }
                    ]

                engine._handle_alerts = active_alert
            else:
                engine._co_emergency_triggered = lambda: True

            try:
                await engine._evaluate()

                output = runtime["humidifier_reconciliation"]["outputs"][
                    "output_1"
                ]
                assert output["desired"] == "off", scenario
                assert output["observed"] == "on", scenario
                assert output["reconciliation"] == "stopping", scenario
                assert not helper.is_on, scenario
                assert len(
                    _humidifier_calls(
                        hass,
                        entity_id="humidifier.level1",
                        service="turn_off",
                    )
                ) == 1, scenario
                display = runtime["runtime_display_reason"]
                display_text = " ".join(
                    [display["headline"]]
                    + [line["text"] for line in display["lines"]]
                )
                assert "HI sent the output-off request to Home Assistant" in display_text, scenario
                assert "humidifier.level1" not in display_text, scenario
            finally:
                await engine.async_stop()

    asyncio.run(run())


def test_output_on_is_observed_without_duplicate_dispatch_and_idle_is_honest():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["humidifier.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(
                outputs={
                    "humidifier.level1": _FakeState(
                        "on",
                        {"action": "idle"},
                    )
                }
            ),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        try:
            await engine._evaluate()
            assert not _humidifier_calls(hass, entity_id="humidifier.level1")
            lane = hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_status"
            ]["lanes"]["level1"]
            assert lane["demand"] == "requested"
            assert lane["observed"] == "on"
            assert lane["platform_action"] == "idle"
            assert lane["reconciliation"] == "platform_idle"
            display = hass.data["humidity_intelligence"][ENTRY_ID][
                "runtime_display_reason"
            ]
            display_text = " ".join(line["text"] for line in display["lines"])
            assert "Output observed on; platform action idle" in display_text
            assert "Physical moisture output is not independently confirmed" in display_text
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_long_demand_output_stop_requests_prompt_reconciliation():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(outputs={"switch.level1": _FakeState("on")}),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        engine._schedule_humidifier_retry = lambda _entity_id, _when: None
        try:
            await engine._evaluate()
            assert not _humidifier_calls(hass, entity_id="switch.level1")
            hass.states._values["switch.level1"] = _FakeState("off")
            await engine._evaluate()
            assert len(
                _humidifier_calls(
                    hass,
                    entity_id="switch.level1",
                    service="turn_on",
                )
            ) == 1
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_retry_schedule_is_bounded_and_fault_latches_without_hammering():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(outputs={"switch.level1": _FakeState("off")}),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        clock = [0.0]
        engine._monotonic = lambda: clock[0]
        engine._schedule_humidifier_retry = lambda _entity_id, _when: None
        try:
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 1

            clock[0] = 29.0
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 1

            clock[0] = 30.0
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 2

            clock[0] = 149.0
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 2

            clock[0] = 150.0
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 3

            clock[0] = 165.0
            await engine._evaluate()
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 3
            output = hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert output["fault_latched"] is True
            assert output["failure_category"] == "retry_exhausted"
            assert output["attempts"] == 3

            hass.states._values["switch.level1"] = _FakeState("on")
            clock[0] = 180.0
            await engine._evaluate()
            output = hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert output["reconciliation"] == "output_on"
            assert output["fault_latched"] is False
            assert output["attempts"] == 3

            hass.states._values["switch.level1"] = _FakeState("off")
            clock[0] = 200.0
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 3
            output = hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert output["fault_latched"] is True
            assert output["attempts"] == 3

            hass.states._values["sensor.kitchen_h"] = _FakeState(55)
            hass.states._values["sensor.hall_h"] = _FakeState(55)
            clock[0] = 210.0
            await engine._evaluate()
            output = hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert output["desired"] == "off"
            assert output["attempts"] == 0
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_observed_recovery_preserves_retry_budget_until_demand_clears():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(outputs={"switch.level1": _FakeState("off")}),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        clock = [0.0]
        engine._monotonic = lambda: clock[0]
        engine._schedule_humidifier_retry = lambda _entity_id, _when: None
        try:
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 1

            hass.states._values["switch.level1"] = _FakeState("on")
            clock[0] = 5.0
            await engine._evaluate()
            output = hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert output["attempts"] == 1
            assert output["reconciliation"] == "output_on"

            hass.states._values["switch.level1"] = _FakeState("off")
            clock[0] = 300.0
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 2
            output = hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert output["attempts"] == 2
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_retry_cleanup_does_not_cancel_the_waking_evaluation_task():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers({})
        hass = _FakeHass(entry, _states())
        engine = engine_mod.HIAutomationEngine(hass, entry)
        current = asyncio.current_task()
        assert current is not None
        engine._humidifier_retry_tasks["switch.level1"] = current
        engine._cancel_humidifier_retry("switch.level1")
        await asyncio.sleep(0)
        assert "switch.level1" not in engine._humidifier_retry_tasks
        assert not current.cancelled()

    asyncio.run(run())


def test_service_unavailable_and_exception_degrade_without_false_confirmation():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                }
            }
        )

        unavailable_hass = _FakeHass(
            entry,
            _states(outputs={"switch.level1": _FakeState("off")}),
        )
        unavailable_hass.services.has_service = lambda _domain, _service: False
        unavailable_engine = engine_mod.HIAutomationEngine(unavailable_hass, entry)
        try:
            await unavailable_engine._evaluate()
            output = unavailable_hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert not _humidifier_calls(unavailable_hass)
            assert output["dispatch_result"] == "service_unavailable"
            assert output["last_dispatch_utc"] is None
            assert output["reconciliation"] == "degraded"
            assert output["attempts"] == 0
        finally:
            await unavailable_engine.async_stop()

        exception_hass = _FakeHass(
            entry,
            _states(outputs={"switch.level1": _FakeState("off")}),
        )

        async def fail_dispatch(_domain, _service, data=None, blocking=False):
            assert blocking is False
            raise RuntimeError("fixture service failure")

        exception_hass.services.async_call = fail_dispatch
        exception_engine = engine_mod.HIAutomationEngine(exception_hass, entry)
        exception_engine._schedule_humidifier_retry = (
            lambda _entity_id, _when: None
        )
        try:
            await exception_engine._evaluate()
            output = exception_hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert output["dispatch_result"] == "exception"
            assert output["last_dispatch_utc"] is not None
            assert output["failure_category"] == "dispatch_exception"
            assert output["attempts"] == 1
            assert output["reconciliation"] == "retrying"
            display = exception_hass.data["humidity_intelligence"][ENTRY_ID][
                "runtime_display_reason"
            ]
            display_text = " ".join(line["text"] for line in display["lines"])
            assert "Home Assistant output-on service call failed" in display_text
            assert "sent" not in display_text.lower()
        finally:
            await exception_engine.async_stop()

    asyncio.run(run())


def test_supported_output_domains_use_nonblocking_domain_safe_commands():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        for domain in ("humidifier", "fan", "switch"):
            entity_id = f"{domain}.level1"
            entry = _entry_with_humidifiers(
                {
                    "level1": {
                        "enabled": True,
                        "outputs": [entity_id],
                        "band_adjust": 0,
                    }
                }
            )
            hass = _FakeHass(
                entry,
                _states(outputs={entity_id: _FakeState("off")}),
            )
            engine = engine_mod.HIAutomationEngine(hass, entry)
            try:
                await engine._evaluate()
                assert _humidifier_calls(
                    hass,
                    entity_id=entity_id,
                    service="turn_on",
                ) == [(domain, "turn_on", {"entity_id": entity_id}, False)]
            finally:
                await engine.async_stop()

    asyncio.run(run())


def test_unknown_output_with_no_demand_gets_one_best_effort_off_only():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(
                level1=55,
                level2=55,
                outputs={"switch.level1": _FakeState("unknown")},
            ),
        )
        engine = engine_mod.HIAutomationEngine(hass, entry)
        clock = [0.0]
        engine._monotonic = lambda: clock[0]
        engine._schedule_humidifier_retry = lambda _entity_id, _when: None
        try:
            await engine._evaluate()
            await engine._evaluate()
            assert len(
                _humidifier_calls(
                    hass,
                    entity_id="switch.level1",
                    service="turn_off",
                )
            ) == 1
            clock[0] = 15.0
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 1
            output = hass.data["humidity_intelligence"][ENTRY_ID][
                "humidifier_reconciliation"
            ]["outputs"]["output_1"]
            assert output["reconciliation"] == "degraded"
            assert output["failure_category"] == "confirmation_timeout"
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_isolation_preserves_demand_and_defers_retry_budget_until_released():
    async def run():
        engine_mod, _register_mod = _load_target_modules()
        entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.level1"],
                    "band_adjust": 0,
                }
            }
        )
        hass = _FakeHass(
            entry,
            _states(outputs={"switch.level1": _FakeState("off")}),
        )
        isolation = hass.data["humidity_intelligence"][ENTRY_ID][
            "hi_input_booleans"
        ]["air_isolate_humidifier_outputs"]
        isolation.is_on = True
        engine = engine_mod.HIAutomationEngine(hass, entry)
        engine._schedule_humidifier_retry = lambda _entity_id, _when: None
        try:
            await engine._evaluate()
            runtime = hass.data["humidity_intelligence"][ENTRY_ID]
            assert runtime["humidifier_status"]["lanes"]["level1"]["demand"] == "requested"
            assert runtime["humidifier_status"]["lanes"]["level1"][
                "reconciliation"
            ] == "isolated"
            assert not _humidifier_calls(hass)

            isolation.is_on = False
            await engine._evaluate()
            assert len(_humidifier_calls(hass, entity_id="switch.level1")) == 1
            output = runtime["humidifier_reconciliation"]["outputs"]["output_1"]
            assert output["attempts"] == 1
        finally:
            await engine.async_stop()

    asyncio.run(run())


def test_cross_family_and_cross_entry_ownership_suppress_writes():
    async def run():
        engine_mod, _register_mod = _load_target_modules()

        cross_family_entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["fan.shared"],
                    "band_adjust": 0,
                }
            }
        )
        cross_family_entry.data["zones"] = {
            "zone1": {
                "enabled": True,
                "outputs": ["fan.shared"],
            }
        }
        cross_family_hass = _FakeHass(
            cross_family_entry,
            _states(outputs={"fan.shared": _FakeState("off")}),
        )
        cross_family_engine = engine_mod.HIAutomationEngine(
            cross_family_hass,
            cross_family_entry,
        )
        try:
            result = await cross_family_engine._reconcile_humidifier_outputs(
                {"fan.shared": {"level1"}}
            )
            assert not _humidifier_calls(cross_family_hass)
            assert result["fan.shared"]["ownership_conflict"] == "cross_family_ownership"
            assert result["fan.shared"]["reconciliation"] == "degraded"
        finally:
            await cross_family_engine.async_stop()

        primary_entry = _entry_with_humidifiers(
            {
                "level1": {
                    "enabled": True,
                    "outputs": ["switch.shared"],
                    "band_adjust": 0,
                }
            }
        )
        primary_hass = _FakeHass(
            primary_entry,
            _states(outputs={"switch.shared": _FakeState("off")}),
        )
        primary_engine = engine_mod.HIAutomationEngine(primary_hass, primary_entry)
        other_entry = SimpleNamespace(
            entry_id="entry-other",
            data=dict(primary_entry.data),
            options={},
        )
        other_engine = engine_mod.HIAutomationEngine(primary_hass, other_entry)
        primary_hass.data["humidity_intelligence"]["entry-other"] = {
            "automation_engine": other_engine
        }
        try:
            result = await primary_engine._reconcile_humidifier_outputs(
                {"switch.shared": {"level1"}}
            )
            assert not _humidifier_calls(primary_hass)
            assert result["switch.shared"]["ownership_conflict"] == "cross_entry_ownership"
            assert result["switch.shared"]["reconciliation"] == "degraded"

            await other_engine.async_stop()
            result = await primary_engine._reconcile_humidifier_outputs(
                {"switch.shared": {"level1"}}
            )
            assert result["switch.shared"]["ownership_conflict"] is None
            assert result["switch.shared"]["reconciliation"] == "requested"
            assert len(
                _humidifier_calls(
                    primary_hass,
                    entity_id="switch.shared",
                    service="turn_on",
                )
            ) == 1
        finally:
            await primary_engine.async_stop()
            await other_engine.async_stop()

    asyncio.run(run())


def test_sanitized_support_truth_drops_entity_ids_and_preserves_categories():
    services_mod = _load_services_module()
    value = {
        "schema": 1,
        "summary": {
            "requested_lanes": 1,
            "degraded_lanes": 0,
            "unknown_lanes": 0,
            "faulted_outputs": 1,
            "degraded_outputs": 0,
            "unknown_outputs": 0,
        },
        "outputs": {
            "output_1": {
                "domain": "humidifier",
                "owners": ["level1"],
                "configured_owners": ["level1"],
                "desired": "on",
                "observed": "off",
                "reconciliation": "fault_latched",
                "failure_category": "retry_exhausted",
                "fault_latched": True,
            },
            "humidifier.private_bedroom": {
                "desired": "on",
                "observed": "off",
            },
        },
    }

    sanitized = services_mod._support_humidifier_reconciliation_summary(value)

    assert sanitized["summary"]["requested_lanes"] == 1
    assert sanitized["outputs"]["output_1"]["reconciliation"] == "fault_latched"
    assert "private_bedroom" not in str(sanitized)
    assert "physical moisture production" in sanitized["truth_boundary"]


def test_release_check_warns_on_degraded_humidifier_truth_without_physical_claim():
    services_mod = _load_services_module()
    entry = _entry_with_humidifiers({})
    hass = _FakeHass(entry, _states())
    runtime_data = {
        "cards": {},
        "entity_map": {},
        "humidifier_reconciliation": {
            "schema": 1,
            "summary": {
                "requested_lanes": 1,
                "degraded_lanes": 0,
                "unknown_lanes": 0,
                "matched_outputs": 0,
                "retrying_outputs": 0,
                "faulted_outputs": 0,
                "degraded_outputs": 1,
                "unknown_outputs": 0,
                "isolated_outputs": 0,
                "ownership_conflicts": 0,
            },
            "outputs": {
                "output_1": {
                    "domain": "switch",
                    "owners": ["level1"],
                    "configured_owners": ["level1"],
                    "desired": "on",
                    "observed": "off",
                    "reconciliation": "degraded",
                    "failure_category": "service_unavailable",
                }
            },
        },
    }

    report = services_mod._build_v205_release_check_entry_report(
        hass,
        entry,
        runtime_data,
        manifest_version="2.0.10-beta.1",
        frontend_dependencies={"status": "not_inspectable"},
    )
    check = {
        item["id"]: item
        for item in report["checks"]
    }["humidifier_reconciliation_truth"]

    assert check["status"] == "warn"
    assert "Home Assistant evidence only" in check["message"]
    assert "entity_id" not in str(check["details"])


def test_release_check_warns_when_enabled_humidifier_truth_is_not_available():
    services_mod = _load_services_module()
    entry = _entry_with_humidifiers(
        {
            "level1": {
                "enabled": True,
                "outputs": ["switch.level1"],
                "band_adjust": 0,
            }
        }
    )
    hass = _FakeHass(entry, _states())

    report = services_mod._build_v205_release_check_entry_report(
        hass,
        entry,
        {"cards": {}, "entity_map": {}},
        manifest_version="2.0.10-beta.1",
        frontend_dependencies={"status": "not_inspectable"},
    )
    check = {
        item["id"]: item
        for item in report["checks"]
    }["humidifier_reconciliation_truth"]

    assert check["status"] == "warn"
    assert check["details"]["status"] == "not_available"
    assert "not available yet" in check["message"]


def test_v2_templates_and_gallery_use_backend_humidifier_and_reason_truth():
    paths = (
        INTEGRATION_ROOT / "ui" / "cards" / "v2_mobile.yaml",
        INTEGRATION_ROOT / "ui" / "cards" / "v2_tablet.yaml",
        ROOT / "ui-gallery" / "default-v2-mobile-aq" / "card.yaml",
        ROOT / "ui-gallery" / "default-v2-tablet-zone-2" / "card.yaml",
    )
    for path in paths:
        source = path.read_text()
        assert "attributes?.humidifier_status" in source
        assert "Humidifier ${label} · ${text}" in source
        assert "Humidifier assist running" not in source
        assert "reasonState?.attributes?.display_reason" in source
        assert "displayReason.schema !== 'hi.reason.v1'" in source
        assert "displayReason.lines.map((line) => escapeHtml(line.text))" in source
        assert "output confirmation pending" not in source
        assert "Home Assistant reports the configured output on" not in source


if __name__ == "__main__":
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for name, test in tests:
        test()
    print(f"{len(tests)} humidifier reconciliation checks passed.")
