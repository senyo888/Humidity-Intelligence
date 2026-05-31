"""Automation engine for Humidity Intelligence."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval

from ..const import (
    ALERT_THRESHOLD_BOUNDS,
    ALERT_TRIGGER_DEFS,
    ROOM_SCOPED_ALERT_TRIGGERS,
    DOMAIN,
    ENGINE_INTERVAL_MAX,
    ENGINE_INTERVAL_MIN,
    ENGINE_INTERVAL_MINUTES_DEFAULT,
    FAN_OUTPUT_LEVEL_AUTO,
    FAN_OUTPUT_LEVEL_STEPS,
    CONF_ALERT_HANDLING_ENABLED,
    DEFAULT_ALERT_HANDLING_ENABLED,
    HUMIDIFIER_RECOVERY_IN_BAND_DEFAULT,
    STARTUP_SENSOR_RECHECK_SECONDS,
    ZONE_OUTPUT_LEVEL_BOOST_DEFAULT,
    ZONE_OUTPUT_LEVEL_DEFAULT,
    ZONE_OUTPUT_LEVEL_MAX,
    ZONE_OUTPUT_LEVEL_MIN,
)
from ..services import SERVICE_FLASH_LIGHTS
from ..helpers.parsing import hass_temperature_unit, parse_numeric, parse_temperature
from ..helpers.seasonal import (
    condensation_risk as seasonal_condensation_risk,
    humidity_state as seasonal_humidity_state,
    mould_level as seasonal_mould_level,
    resolve_target_profile,
)

CO_EMERGENCY_START = 15
CO_EMERGENCY_CLEAR = 10
CO_EMERGENCY_CLEAR_HOLD = timedelta(minutes=2)
_RISK_ORDER = {"OK": 0, "Watch": 1, "Risk": 2, "Danger": 3, "Unknown": -1}
_ALERT_PRIORITY = {
    "humidity_danger": 10,
    "mould_danger": 20,
    "mould_risk": 30,
    "condensation_danger": 40,
    "condensation_risk": 50,
    "co_emergency": 0,
}
_BUILT_IN_ZONE_ALERT_TRIGGERS = (
    "humidity_danger",
    "mould_danger",
    "mould_risk",
    "condensation_danger",
    "condensation_risk",
)
HUMIDITY_ALERT_FLASH_COUNT = 10
HUMIDITY_ALERT_REPEAT_MINUTES = 30
_EVALUATION_SWITCH_SOURCE_KEYS = {
    "air_control_enabled",
    "air_control_manual_override",
    "air_isolate_fan_outputs",
    "air_isolate_humidifier_outputs",
}
_EVALUATION_TIMER_SOURCE_KEYS = {
    "air_control_pause",
}

_LOGGER = logging.getLogger(__name__)

_MAX_STATE_LENGTH = 255
_TRUNCATION_SUFFIX = " [full in attribute]"


class HIAutomationEngine:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.telemetry = self._cfg("telemetry", [])
        self.time_gate = self._cfg("time_gate", {})
        self.presence_gate = self._cfg("presence_gate", {})
        self.zones = self._cfg("zones", {})
        self.humidifiers = self._cfg("humidifiers", {})
        self.aq = self._cfg("aq", {})
        self.alerts = self._cfg("alerts", [])
        self.alert_handling_enabled = bool(
            self._cfg(CONF_ALERT_HANDLING_ENABLED, DEFAULT_ALERT_HANDLING_ENABLED)
        )
        self.alert_only_mode = bool(self._cfg("alert_only_mode", False))
        self._unsub = None
        self._periodic = None
        self._aq_tasks: Dict[str, asyncio.Task] = {}
        self._aq_trigger_active: Dict[str, bool] = {}
        self._visual_alert_tasks: Dict[Tuple[str, str, str], asyncio.Task] = {}
        self._visual_alert_active: set[Tuple[str, str, str]] = set()
        self._startup_recheck_task: Optional[asyncio.Task] = None
        self._co_clear_recheck_task: Optional[asyncio.Task] = None
        self._last_alert: Dict[int, datetime] = {}
        self._active_alert_identity: Optional[Tuple[str, str, str]] = None
        self._co_emergency_active = False
        self._co_below_since: Optional[datetime] = None
        self._evaluate_lock: Optional[asyncio.Lock] = None
        self._evaluate_pending = False
        configured_interval = None
        if entry.options:
            configured_interval = entry.options.get("engine_interval_minutes")
        if configured_interval is None:
            configured_interval = entry.data.get(
                "engine_interval_minutes",
                ENGINE_INTERVAL_MINUTES_DEFAULT,
            )
        self.engine_interval_minutes = _bounded_int(
            configured_interval,
            ENGINE_INTERVAL_MIN,
            ENGINE_INTERVAL_MAX,
            ENGINE_INTERVAL_MINUTES_DEFAULT,
        )
        if self.alert_only_mode:
            self.zones = {}
            self.humidifiers = {}
            self.aq = {}
            _LOGGER.info(
                "HI entry %s is running in alert-only mode; zone/humidifier/AQ output lanes are disabled.",
                entry.entry_id,
            )

    def _cfg(self, key: str, default: Any) -> Any:
        if self.entry.options and key in self.entry.options:
            return self.entry.options.get(key, default)
        return self.entry.data.get(key, default)

    async def async_start(self) -> None:
        sources = self._evaluation_sources()
        self._unsub = async_track_state_change_event(self.hass, sources, self._handle_change)
        self._periodic = async_track_time_interval(
            self.hass,
            self._periodic_check,
            timedelta(minutes=self.engine_interval_minutes),
        )
        await self.async_request_evaluate()
        self._schedule_startup_recheck()

    async def async_stop(self) -> None:
        if self._unsub:
            self._unsub()
        if self._periodic:
            self._periodic()
        if self._startup_recheck_task and not self._startup_recheck_task.done():
            self._startup_recheck_task.cancel()
        self._startup_recheck_task = None
        self._cancel_co_clear_recheck()
        for task in self._aq_tasks.values():
            task.cancel()
        for task in self._visual_alert_tasks.values():
            task.cancel()
        self._visual_alert_tasks.clear()
        self._visual_alert_active.clear()

    async def _handle_change(self, event) -> None:
        await self.async_request_evaluate()

    async def _periodic_check(self, now) -> None:
        await self.async_request_evaluate()

    async def async_request_evaluate(self) -> None:
        """Request an immediate evaluation cycle."""
        evaluate_lock = self._get_evaluate_lock()
        if evaluate_lock.locked():
            self._evaluate_pending = True
            _LOGGER.debug(
                "HI entry %s evaluation already running; queued one follow-up cycle.",
                self.entry.entry_id,
            )
            return
        async with evaluate_lock:
            while True:
                self._evaluate_pending = False
                await self._evaluate()
                if not self._evaluate_pending:
                    break

    def _get_evaluate_lock(self) -> asyncio.Lock:
        if self._evaluate_lock is None:
            self._evaluate_lock = asyncio.Lock()
        return self._evaluate_lock

    def _schedule_startup_recheck(self) -> None:
        if self._startup_recheck_task and not self._startup_recheck_task.done():
            self._startup_recheck_task.cancel()

        async def _startup_recheck() -> None:
            try:
                await asyncio.sleep(STARTUP_SENSOR_RECHECK_SECONDS)
                await self.async_request_evaluate()
            except asyncio.CancelledError:
                return

        self._startup_recheck_task = asyncio.create_task(_startup_recheck())

    async def _evaluate(self) -> None:
        try:
            target_profile = self._active_target_profile()
            house_humidity = self._level_avg("humidity", None)
            humidity_class = seasonal_humidity_state(house_humidity, target_profile)
            _LOGGER.debug(
                "HI entry %s active target profile: %s (low=%.1f high=%.1f high_risk=%.1f)",
                self.entry.entry_id,
                target_profile.label,
                target_profile.low,
                target_profile.high,
                target_profile.high_risk,
            )
            _LOGGER.debug(
                "HI entry %s seasonal adjustments applied: condensation danger<=%.1f risk<=%.1f watch<=%.1f; mould spread danger<=%.1f risk<=%.1f; mould excess risk>=%.1f danger>=%.1f",
                self.entry.entry_id,
                target_profile.condensation_danger_spread,
                target_profile.condensation_risk_spread,
                target_profile.condensation_watch_spread,
                target_profile.mould_spread_danger,
                target_profile.mould_spread_risk,
                target_profile.mould_excess_risk,
                target_profile.mould_excess_danger,
            )
            _LOGGER.debug(
                "HI entry %s humidity badge classification: %s (humidity=%s)",
                self.entry.entry_id,
                humidity_class,
                f"{house_humidity:.1f}%" if house_humidity is not None else "unknown",
            )

            # Absolute top-priority lane: CO emergency must bypass gates,
            # pause, manual override, and normal control locks.
            if self._co_emergency_active and self._co_clear_ready():
                self._co_emergency_active = False
                self._co_below_since = None
                self._cancel_co_clear_recheck()
            if self._co_emergency_triggered():
                await self._sync_visual_alert_tasks([])
                await self._apply_co_emergency()
                await self._set_runtime_reason(
                    self._with_isolation_notice(
                        "CO emergency protection is active, so all configured ventilation outputs are forced to 100%."
                    )
                )
                return
            await self._set_bool("air_co_emergency_active", self._co_emergency_active)

            control_lock_reason = self._control_lock_reason()
            if control_lock_reason:
                await self._sync_visual_alert_tasks([])
                await self._return_to_normal()
                await self._set_runtime_reason(self._with_isolation_notice(control_lock_reason))
                return

            gates_ok, gate_reason = self._gate_status()
            if not gates_ok:
                await self._sync_visual_alert_tasks([])
                action = self.time_gate.get("outside_action", "safe_state")
                if action == "safe_state":
                    await self._return_to_normal()
                    await self._set_runtime_mode("global_gate", "GLOBAL GATE")
                    await self._set_runtime_reason(
                        self._with_isolation_notice(
                            gate_reason
                            or "Global gate is blocking automation, so outputs were moved to a safe state."
                        )
                    )
                else:
                    await self._set_runtime_mode("global_gate", "GLOBAL GATE")
                    await self._set_runtime_reason(
                        self._with_isolation_notice(
                            gate_reason
                            or "Global gate is blocking automation; no output changes were applied."
                        )
                    )
                return
            if self._pause_active():
                await self._sync_visual_alert_tasks([])
                await self._return_to_normal()
                await self._set_runtime_reason(
                    self._with_isolation_notice(
                        "Pause is active, so automation is temporarily standing down."
                    )
                )
                return
            missing_required_telemetry = self._missing_required_telemetry(house_humidity)
            if missing_required_telemetry:
                telemetry_label = " and ".join(missing_required_telemetry)
                telemetry_verb = "is" if len(missing_required_telemetry) == 1 else "are"
                await self._sync_visual_alert_tasks([])
                await self._return_to_normal()
                await self._set_runtime_mode("telemetry_unavailable", "TELEMETRY UNAVAILABLE")
                await self._set_runtime_reason(
                    self._with_isolation_notice(
                        f"Required {telemetry_label} telemetry {telemetry_verb} unavailable, so automation is standing down instead of running zone, alert, AQ, or humidifier lanes."
                    )
                )
                return

            # Alert lane is high priority and suppresses all lower lanes.
            alert_active, alert_details = await self._handle_alerts()
            if alert_active:
                selected_alert = alert_details[0] if alert_details else {}
                selected_outputs = selected_alert.get("outputs", []) if selected_alert else []
                await self._deactivate_non_alert_activity(exclude_zone_outputs=selected_outputs)
                if selected_outputs and selected_alert.get("boost_level"):
                    await self._set_fan_outputs_level(selected_outputs, selected_alert["boost_level"])
                await self._set_runtime_mode("alert", "ALERT")
                await self._set_runtime_reason(
                    self._with_isolation_notice(
                        self._build_runtime_reason(
                            runtime_mode="alert",
                            alert_labels=alert_details,
                            zone1_active=False,
                            zone2_active=False,
                            aq_active=False,
                            zone1_detail=None,
                            zone2_detail=None,
                            aq_details=[],
                            humidifier_details=[],
                        )
                    )
                )
                return

            # Humidifiers are independent from zone/AQ lane order.
            humidifier_details = await self._handle_humidifiers()

            # Requested lane order: zone1 -> zone2 -> AQ. Only the selected
            # ventilation lane may write fan outputs in a cycle.
            zone1_active, zone1_mode, zone1_detail = await self._handle_zone_by_key("zone1")
            zone2_active = False
            zone2_mode = None
            zone2_detail = None
            if zone1_active:
                await self._set_zone_outputs_auto(exclude=zone1_detail.get("outputs", []) if zone1_detail else [])
            else:
                zone2_active, zone2_mode, zone2_detail = await self._handle_zone_by_key("zone2")
                if zone2_active:
                    await self._set_zone_outputs_auto(exclude=zone2_detail.get("outputs", []) if zone2_detail else [])
            zone_outputs_active = zone1_active or zone2_active

            # AQ lane only runs when no alert or zone lane is active.
            aq_active = False
            aq_details: List[Dict[str, Any]] = []
            if not alert_active and not zone_outputs_active:
                aq_active, aq_details = await self._handle_aq()
            else:
                await self._deactivate_aq_activity(set_fan_auto=not zone_outputs_active)

            if not (zone1_active or zone2_active):
                await self._set_zone_outputs_auto(exclude=self._active_aq_outputs() if aq_active else None)

            runtime_mode = "normal"
            runtime_display = "NORMAL"
            if alert_active:
                runtime_mode = "alert"
                runtime_display = "ALERT"
            elif zone1_active:
                runtime_mode = zone1_mode or "cooking"
                runtime_display = self._zone_display_label("zone1", runtime_mode)
            elif zone2_active:
                runtime_mode = zone2_mode or "bathroom"
                runtime_display = self._zone_display_label("zone2", runtime_mode)
            elif aq_active:
                runtime_mode = "air_quality"
                runtime_display = "AIR QUALITY"
            await self._set_runtime_mode(runtime_mode, runtime_display)
            await self._set_runtime_reason(
                self._with_isolation_notice(
                    self._build_runtime_reason(
                        runtime_mode=runtime_mode,
                        alert_labels=alert_details,
                        zone1_active=zone1_active,
                        zone2_active=zone2_active,
                        aq_active=aq_active,
                        zone1_detail=zone1_detail,
                        zone2_detail=zone2_detail,
                        aq_details=aq_details,
                        humidifier_details=humidifier_details,
                    )
                )
            )
        except Exception:
            _LOGGER.exception("Unhandled error in HI automation evaluation cycle")
        finally:
            self._refresh_core_entities()

    def _control_lock_reason(self) -> Optional[str]:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        booleans = data.get("hi_input_booleans", {})
        if booleans.get("air_control_enabled") and not booleans["air_control_enabled"].is_on:
            return "System control is disabled, so all automation lanes are idle."
        if booleans.get("air_control_manual_override") and booleans["air_control_manual_override"].is_on:
            return "Manual override is enabled, so HI automation is standing down."
        return None

    def _gate_status(self) -> Tuple[bool, Optional[str]]:
        if self.time_gate.get("enabled"):
            now = datetime.now().time()
            start = _parse_time(self.time_gate.get("start"))
            end = _parse_time(self.time_gate.get("end"))
            if start and end:
                in_window = _time_in_window(now, start, end)
                if not in_window:
                    action = self.time_gate.get("outside_action", "no_action")
                    if action == "no_action":
                        return True, None
                    return (
                        False,
                        f"Time gate is outside {start.strftime('%H:%M')} - {end.strftime('%H:%M')}; action '{action}' is active.",
                    )
        if self.presence_gate.get("enabled"):
            entities = self.presence_gate.get("entities", [])
            present_states = set(self.presence_gate.get("present_states", []))
            away_states = set(self.presence_gate.get("away_states", []))
            if entities and present_states:
                for entity_id in entities:
                    state = self.hass.states.get(entity_id)
                    if not state:
                        continue
                    if state.state in present_states:
                        return True, None
                    if away_states and state.state in away_states:
                        continue
                return (
                    False,
                    f"Presence gate is active (no entity in present states). Snapshot: {self._presence_snapshot(entities)}.",
                )
        return True, None

    def _presence_snapshot(self, entities: List[str]) -> str:
        parts: List[str] = []
        for entity_id in entities:
            state = self.hass.states.get(entity_id)
            name = self._entity_display_name(entity_id)
            parts.append(f"{name}={state.state if state else 'unknown'}")
        return ", ".join(parts) if parts else "no presence entities configured"

    def _evaluation_sources(self) -> List[str]:
        sources = [t["entity_id"] for t in self.telemetry if t.get("entity_id")]
        sources.extend(self.presence_gate.get("entities", []) or [])
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        booleans = data.get("hi_input_booleans", {})
        timers = data.get("hi_timers", {})
        for key, entity in booleans.items():
            if key not in _EVALUATION_SWITCH_SOURCE_KEYS:
                continue
            entity_id = getattr(entity, "entity_id", None)
            if entity_id:
                sources.append(entity_id)
        for key, entity in timers.items():
            if key not in _EVALUATION_TIMER_SOURCE_KEYS:
                continue
            entity_id = getattr(entity, "entity_id", None)
            if entity_id:
                sources.append(entity_id)
        return sorted(set(sources))

    def _has_telemetry_type(self, sensor_type: str) -> bool:
        return any(item.get("sensor_type") == sensor_type for item in self.telemetry)

    def _missing_required_telemetry(self, house_humidity: Optional[float]) -> List[str]:
        missing: List[str] = []
        if house_humidity is None:
            missing.append("humidity")
        if self._has_telemetry_type("temperature") and self._level_avg("temperature", None) is None:
            missing.append("temperature")
        return missing

    def _co_emergency_triggered(self) -> bool:
        start_threshold, _, _ = self._co_emergency_settings()
        co_values = self._collect_values("co")
        if any(val >= start_threshold for val in co_values):
            self._co_emergency_active = True
            return True
        return self._co_emergency_active

    def _co_clear_ready(self) -> bool:
        _, clear_threshold, _ = self._co_emergency_settings()
        co_values = self._collect_values("co")
        if not co_values:
            self._cancel_co_clear_recheck()
            return False
        now = datetime.now()
        if all(val < clear_threshold for val in co_values):
            if not self._co_below_since:
                self._co_below_since = now
            ready = now - self._co_below_since >= CO_EMERGENCY_CLEAR_HOLD
            if not ready:
                self._schedule_co_clear_recheck(now)
            return ready
        self._co_below_since = None
        self._cancel_co_clear_recheck()
        return False

    def _schedule_co_clear_recheck(self, now: datetime) -> None:
        if self._co_clear_recheck_task and not self._co_clear_recheck_task.done():
            return
        if self._co_below_since is None:
            return
        remaining = CO_EMERGENCY_CLEAR_HOLD - (now - self._co_below_since)
        delay = max(0.0, remaining.total_seconds())

        async def _co_clear_recheck() -> None:
            task = asyncio.current_task()
            try:
                await asyncio.sleep(delay)
                await self.async_request_evaluate()
            except asyncio.CancelledError:
                return
            finally:
                if self._co_clear_recheck_task is task:
                    self._co_clear_recheck_task = None

        self._co_clear_recheck_task = asyncio.create_task(_co_clear_recheck())

    def _cancel_co_clear_recheck(self) -> None:
        if self._co_clear_recheck_task and not self._co_clear_recheck_task.done():
            self._co_clear_recheck_task.cancel()
        self._co_clear_recheck_task = None

    async def _apply_co_emergency(self) -> None:
        _, _, outputs = self._co_emergency_settings()
        await self._deactivate_aq_activity(set_fan_auto=False)
        await self._deactivate_humidifier_activity(turn_off_outputs=True)
        await self._clear_alert_activity_switches()
        await self._set_bool("air_co_emergency_active", True)
        all_outputs = self._all_fan_outputs()
        outputs_to_auto = [entity_id for entity_id in all_outputs if entity_id not in outputs]
        await self._set_fan_outputs_auto(outputs_to_auto)
        await self._set_fan_outputs_level(outputs, "100")
        await self._set_runtime_mode("co_emergency", "CO EMERGENCY")

    async def _handle_alerts(self) -> Tuple[bool, List[Dict[str, Any]]]:
        active_details: List[Dict[str, Any]] = []
        alert_switch_states = {
            idx: False for idx in range(max(len(self.alerts), 5))
        }
        if not self.alert_handling_enabled:
            await self._sync_alert_activity_switches({})
            self._active_alert_identity = None
            self._record_alert_resolution([])
            _LOGGER.debug(
                "HI alert handling is disabled for entry %s; non-CO alert lane skipped.",
                self.entry.entry_id,
            )
            await self._sync_visual_alert_tasks([])
            return False, []
        for idx, alert in enumerate(self.alerts):
            if not alert.get("enabled", True):
                continue
            detail = self._alert_detail(idx, alert)
            triggered = detail is not None
            alert_switch_states[idx] = triggered
            if not triggered:
                continue
            active_details.append(detail)
        await self._sync_alert_activity_switches(alert_switch_states)
        await self._sync_visual_alert_tasks(active_details)
        inferred_details = self._inferred_alert_details(active_details)
        if inferred_details:
            _LOGGER.debug(
                "HI inferred %s built-in alert candidate(s) for entry %s.",
                len(inferred_details),
                self.entry.entry_id,
            )
            active_details.extend(inferred_details)
        active_details.sort(
            key=lambda item: (
                item.get("priority", 999),
                item.get("zone_priority", 999),
                item.get("index", 999),
            )
        )
        selected_alert = self._select_alert_detail(active_details)
        if selected_alert:
            active_details = [selected_alert] + [
                detail for detail in active_details if detail is not selected_alert
            ]
        self._record_alert_resolution(active_details)
        return selected_alert is not None, active_details

    def _alert_triggered(self, alert: Dict[str, Any]) -> bool:
        return self._alert_detail(0, alert) is not None

    def _select_alert_detail(self, details: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the actionable alert to control outputs, holding it until it clears."""
        actionable = [detail for detail in details if _alert_can_control(detail)]
        if not actionable:
            if details:
                _LOGGER.debug(
                    "HI alert candidate(s) found for entry %s but none can safely control outputs; automation will continue to the next lane.",
                    self.entry.entry_id,
                )
            self._active_alert_identity = None
            return None

        best = actionable[0]
        current = None
        if self._active_alert_identity:
            for detail in actionable:
                if _alert_identity(detail) == self._active_alert_identity:
                    current = detail
                    break

        selected = best
        if current and int(best.get("priority", 999)) >= int(current.get("priority", 999)):
            selected = current
            if selected is not best:
                selected["held_until_clear"] = True
                _LOGGER.debug(
                    "HI holding alert selection for entry %s until clear: selected=%s; best_candidate=%s",
                    self.entry.entry_id,
                    selected.get("companion") or selected.get("label"),
                    best.get("companion") or best.get("label"),
                )
        else:
            selected.pop("held_until_clear", None)

        self._active_alert_identity = _alert_identity(selected)
        return selected

    def _inferred_alert_details(self, configured_details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build alert candidates from HI's own risk model without duplicating explicit rows."""
        active_keys = {
            (str(detail.get("trigger_type") or ""), str(detail.get("room") or "").lower())
            for detail in configured_details
        }
        inferred: List[Dict[str, Any]] = []
        base_index = len(self.alerts)
        for offset, trigger_type in enumerate(_BUILT_IN_ZONE_ALERT_TRIGGERS):
            detail = self._alert_detail(
                base_index + offset,
                {
                    "enabled": True,
                    "trigger_type": trigger_type,
                    "room": None,
                    "threshold": None,
                    "_inferred": True,
                },
            )
            if not detail:
                continue
            key = (str(detail.get("trigger_type") or ""), str(detail.get("room") or "").lower())
            if key in active_keys:
                continue
            detail["source"] = "built_in_risk_model"
            detail["label"] = f"Built-in {detail.get('label')}"
            inferred.append(detail)
        return inferred

    def _alert_detail(self, idx: int, alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ttype = alert.get("trigger_type")
        room_scope = self._alert_room_scope(alert)
        if ttype == "condensation_danger":
            room, sensor = self._matching_condensation_room("Danger", room_scope)
            if room:
                return self._build_alert_detail(idx, alert, sensor=sensor, room=room)
            return None
        if ttype == "condensation_risk":
            room, sensor = self._matching_condensation_room("Risk", room_scope)
            if room:
                return self._build_alert_detail(idx, alert, sensor=sensor, room=room)
            return None
        if ttype == "mould_danger":
            room, sensor = self._matching_mould_room("Danger", room_scope)
            if room:
                return self._build_alert_detail(idx, alert, sensor=sensor, room=room)
            return None
        if ttype == "mould_risk":
            room, sensor = self._matching_mould_room("Risk", room_scope)
            if room:
                return self._build_alert_detail(idx, alert, sensor=sensor, room=room)
            return None
        if ttype == "humidity_danger":
            profile = self._active_target_profile()
            threshold = float(profile.high_risk)
            match = self._matching_humidity_sensor(threshold, room_scope)
            if match:
                sensor, room, value = match
                detail = self._build_alert_detail(idx, alert, sensor=sensor, room=room)
                detail["measured"] = f"{value:.1f}% >= active {profile.label} high-risk threshold {threshold:g}%"
                detail["threshold"] = threshold
                detail["threshold_source"] = f"active profile ({profile.label})"
                detail["source_summary"] = _alert_source_summary(
                    trigger_type=ttype,
                    room=room,
                    zone=detail.get("zone"),
                    measured=f"{value:.1f}%",
                    threshold=f"{threshold:g}% threshold",
                )
                return detail
            return None
        if ttype == "co_emergency":
            threshold = _safe_alert_threshold("co_emergency", alert.get("threshold"), float(CO_EMERGENCY_START))
            values = self._collect_values("co")
            if any(val >= threshold for val in values):
                return self._build_alert_detail(idx, alert, sensor=None, room=None)
        return None

    def _build_alert_detail(
        self,
        idx: int,
        alert: Dict[str, Any],
        *,
        sensor: Optional[str],
        room: Optional[str],
    ) -> Dict[str, Any]:
        trigger_type = str(alert.get("trigger_type") or "unknown")
        zone_key, zone = self._zone_for_room(room)
        boost_level = None
        outputs: List[str] = []
        zone_label = None
        degraded_reasons: List[str] = []
        if room and not zone_key:
            degraded_reasons.append(f"No enabled zone maps room '{room}'.")
        if zone_key and zone:
            outputs = list(zone.get("outputs", []) or [])
            zone_label = "Zone 1" if zone_key == "zone1" else "Zone 2" if zone_key == "zone2" else zone_key
            boost_level = _normalize_fan_level(
                zone.get("boost_output_level", ZONE_OUTPUT_LEVEL_BOOST_DEFAULT),
                ZONE_OUTPUT_LEVEL_BOOST_DEFAULT,
            )
            if not outputs:
                degraded_reasons.append(f"{zone_label} has no fan outputs configured.")
        if trigger_type in ROOM_SCOPED_ALERT_TRIGGERS and not sensor:
            degraded_reasons.append("Originating telemetry sensor could not be resolved.")
        label = self._alert_label(idx, alert, resolved_room=room)
        alert_kind, severity = _alert_kind_and_severity(trigger_type)
        companion = _alert_companion_label(alert_kind, severity, room, zone_label)
        return {
            "index": idx,
            "label": label,
            "companion": companion,
            "trigger_type": trigger_type,
            "alert_type": alert_kind,
            "severity": severity,
            "sensor": sensor,
            "room": room,
            "zone_key": zone_key,
            "zone": zone_label,
            "zone_priority": _zone_priority(zone_key),
            "outputs": outputs,
            "boost_level": boost_level,
            "priority": _alert_priority(trigger_type),
            "source": "configured_alert" if not alert.get("_inferred") else "built_in_risk_model",
            "degraded": bool(degraded_reasons),
            "degraded_reasons": degraded_reasons,
            "source_summary": _alert_source_summary(
                trigger_type=trigger_type,
                room=room,
                zone=zone_label,
                measured=None,
                threshold=None,
            ),
            "visual_alert": {
                "configured": bool(alert.get("lights")),
                "lights": list(alert.get("lights", []) or []),
                "power_entity": alert.get("power_entity"),
                "flash_mode": alert.get("flash_mode") or "red",
                "duration": alert.get("duration", 10),
                "flash_count": HUMIDITY_ALERT_FLASH_COUNT,
                "repeat_minutes": HUMIDITY_ALERT_REPEAT_MINUTES,
                "restore_state": True,
            },
        }

    def _record_alert_resolution(self, details: List[Dict[str, Any]]) -> None:
        data = self.hass.data.setdefault(DOMAIN, {}).setdefault(self.entry.entry_id, {})
        if not details:
            data["active_alert_context"] = "None"
            data["alert_telemetry"] = []
            return
        selected = details[0]
        data["active_alert_context"] = selected.get("source_summary") or selected.get("companion") or selected.get("label") or "Alert"
        data["alert_telemetry"] = details
        _LOGGER.debug(
            "HI alert resolved for entry %s: selected=%s; source=%s; sensor=%s; room=%s; zone=%s; outputs=%s; boost=%s",
            self.entry.entry_id,
            selected.get("companion") or selected.get("label"),
            selected.get("source"),
            selected.get("sensor"),
            selected.get("room"),
            selected.get("zone"),
            selected.get("outputs"),
            selected.get("boost_level"),
        )
        if len(details) > 1:
            _LOGGER.debug(
                "HI alert conflict resolved for entry %s: selected=%s; candidates=%s",
                self.entry.entry_id,
                selected.get("companion"),
                [
                    {
                        "alert": item.get("companion"),
                        "priority": item.get("priority"),
                        "zone": item.get("zone"),
                        "zone_priority": item.get("zone_priority"),
                    }
                    for item in details
                ],
            )
        if selected.get("degraded"):
            _LOGGER.debug(
                "HI alert degraded mode for entry %s: %s",
                self.entry.entry_id,
                "; ".join(selected.get("degraded_reasons", [])),
            )

    async def _sync_visual_alert_tasks(self, active_details: List[Dict[str, Any]]) -> None:
        active_identities = {
            _alert_identity(detail)
            for detail in active_details
            if self._visual_alert_configured(detail)
        }
        self._visual_alert_active = active_identities
        for identity, task in list(self._visual_alert_tasks.items()):
            if identity not in active_identities:
                task.cancel()
                self._visual_alert_tasks.pop(identity, None)
        for detail in active_details:
            if not self._visual_alert_configured(detail):
                if detail.get("trigger_type") in _BUILT_IN_ZONE_ALERT_TRIGGERS:
                    _LOGGER.debug(
                        "Alert %s triggered with no target lights configured; skipping visual flash task.",
                        int(detail.get("index", 0)) + 1,
                    )
                continue
            identity = _alert_identity(detail)
            existing = self._visual_alert_tasks.get(identity)
            if existing and not existing.done():
                continue
            task = asyncio.create_task(self._visual_alert_loop(identity, dict(detail)))
            self._visual_alert_tasks[identity] = task
            await asyncio.sleep(0)

    def _visual_alert_configured(self, detail: Dict[str, Any]) -> bool:
        visual = detail.get("visual_alert") if isinstance(detail, dict) else {}
        return bool(isinstance(visual, dict) and visual.get("lights"))

    async def _visual_alert_loop(
        self,
        identity: Tuple[str, str, str],
        detail: Dict[str, Any],
    ) -> None:
        try:
            while identity in self._visual_alert_active:
                visual = detail.get("visual_alert") or {}
                lights = list(visual.get("lights") or [])
                if not lights:
                    return
                flash_payload = {
                    "lights": lights,
                    "color": [255, 0, 0] if visual.get("flash_mode") == "red" else [255, 255, 255],
                    "duration": visual.get("duration", 10),
                    "flash_count": HUMIDITY_ALERT_FLASH_COUNT,
                }
                power_entity = visual.get("power_entity")
                if power_entity:
                    flash_payload["power_entity"] = power_entity
                try:
                    await self.hass.services.async_call(
                        DOMAIN,
                        SERVICE_FLASH_LIGHTS,
                        flash_payload,
                        blocking=False,
                    )
                except Exception:
                    _LOGGER.exception(
                        "Alert flash service call failed for alert identity %s",
                        identity,
                    )
                await asyncio.sleep(timedelta(minutes=HUMIDITY_ALERT_REPEAT_MINUTES).total_seconds())
        except asyncio.CancelledError:
            return
        finally:
            current = self._visual_alert_tasks.get(identity)
            if current is asyncio.current_task():
                self._visual_alert_tasks.pop(identity, None)

    async def _handle_zone_by_key(self, zone_key: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        zone = self.zones.get(zone_key, {})
        if not zone.get("enabled"):
            return False, None, None

        triggers = zone.get("triggers", [])
        level = zone.get("level")
        outputs = zone.get("outputs", [])
        if not triggers or not outputs:
            return False, None, None

        run_level, trigger_details = self._zone_trigger_level(triggers, zone, level)
        if not run_level:
            return False, None, None

        await self._set_fan_outputs_level(outputs, run_level)
        zone_mode = self._zone_mode_from_zone(zone_key, zone)
        return (
            True,
            zone_mode,
            {
                "zone_key": zone_key,
                "ui_label": self._zone_display_label(zone_key, zone_mode),
                "outputs": outputs,
                "output_level": run_level,
                "triggers": trigger_details,
            },
        )

    def _zone_trigger_level(self, triggers: List[str], zone: Dict[str, Any], level: Optional[str]) -> Tuple[Optional[str], List[str]]:
        profile = self._active_target_profile()
        normal_level = _normalize_fan_level(
            zone.get("output_level", ZONE_OUTPUT_LEVEL_DEFAULT),
            ZONE_OUTPUT_LEVEL_DEFAULT,
        )
        boost_level = _normalize_fan_level(
            zone.get("boost_output_level", ZONE_OUTPUT_LEVEL_BOOST_DEFAULT),
            ZONE_OUTPUT_LEVEL_BOOST_DEFAULT,
        )
        if _fan_level_rank(boost_level) < _fan_level_rank(normal_level):
            boost_level = normal_level
        selected_level: Optional[str] = None
        trigger_details: List[str] = []
        for trig in triggers:
            threshold = zone.get("thresholds", {}).get(trig)
            if trig == "humidity_high":
                zone_rooms = zone.get("rooms", [])
                room_avg = self._rooms_avg("humidity", zone_rooms)
                house_avg = self._level_avg("humidity", None)
                try:
                    threshold_val = float(threshold) if threshold is not None else None
                except (TypeError, ValueError):
                    threshold_val = None
                if room_avg is not None and house_avg is not None and threshold_val is not None:
                    delta = room_avg - house_avg
                    if delta >= threshold_val:
                        selected_level = _max_fan_level(selected_level, normal_level)
                        trigger_details.append(
                            f"Humidity delta {delta:.1f}% >= threshold {threshold_val:g}%"
                        )
            elif trig == "air_quality_bad":
                iaq = self._level_avg("iaq", level)
                threshold_val = _to_float(threshold)
                if iaq is not None and threshold_val is not None and iaq <= threshold_val:
                    selected_level = _max_fan_level(selected_level, normal_level)
                    trigger_details.append(f"IAQ {iaq:.1f} <= threshold {threshold_val:g}")
            elif trig == "condensation_risk":
                spread = self._worst_spread()
                threshold_val = _to_float(threshold)
                if threshold_val is None:
                    threshold_val = 4.0
                adjusted_threshold = profile.condensation_risk_spread + (threshold_val - 4.0)
                adjusted_threshold = max(0.5, min(12.0, adjusted_threshold))
                if spread is not None and spread <= adjusted_threshold:
                    selected_level = _max_fan_level(selected_level, boost_level)
                    trigger_details.append(
                        "Dew-point spread "
                        f"{spread:.1f} degC <= seasonal threshold {adjusted_threshold:g} degC "
                        f"(profile {profile.label}, user baseline {threshold_val:g} degC)"
                    )
            elif trig == "mould_risk":
                risk_level = self._worst_mould_level()
                threshold_val = _to_float(threshold)
                if threshold_val is not None and risk_level >= threshold_val:
                    selected_level = _max_fan_level(selected_level, boost_level)
                    trigger_details.append(
                        f"Mould risk level {risk_level} >= threshold {threshold_val:g}"
                    )
        return selected_level, trigger_details

    async def _handle_aq(self) -> Tuple[bool, List[Dict[str, Any]]]:
        active = False
        active_details: List[Dict[str, Any]] = []
        configured_levels = set(self.aq.keys())
        for level in ("level1", "level2"):
            if level in configured_levels:
                continue
            await self._cancel_aq_task(level)
            await self._set_aq_level_active(level, False)
            await self._clear_aq_level_timer(level)
            self._aq_trigger_active[level] = False

        for level, cfg in self.aq.items():
            if not cfg.get("enabled"):
                await self._cancel_aq_task(level)
                await self._set_aq_level_active(level, False)
                await self._clear_aq_level_timer(level)
                self._aq_trigger_active[level] = False
                continue
            outputs = cfg.get("outputs", [])
            if not outputs:
                await self._cancel_aq_task(level)
                await self._set_aq_level_active(level, False)
                await self._clear_aq_level_timer(level)
                self._aq_trigger_active[level] = False
                continue
            task = self._aq_tasks.get(level)
            running = bool(task and not task.done())
            trigger_details = self._aq_trigger_details(level, cfg)
            triggered = bool(trigger_details)
            previously_triggered = self._aq_trigger_active.get(level, False)
            if triggered:
                active = True
                if not running or not previously_triggered:
                    await self._start_aq(level, cfg)
                    running = True
            elif not running:
                await self._cancel_aq_task(level)
                await self._set_aq_level_active(level, False)
                await self._clear_aq_level_timer(level)
            self._aq_trigger_active[level] = triggered
            if running or triggered:
                active = True
                active_details.append({
                    "level": level,
                    "outputs": cfg.get("outputs", []),
                    "output_level": _normalize_fan_level(
                        cfg.get("output_level", ZONE_OUTPUT_LEVEL_DEFAULT),
                        ZONE_OUTPUT_LEVEL_DEFAULT,
                    ),
                    "run_duration": _bounded_int(cfg.get("run_duration", 30), 1, 24 * 60, 30),
                    "triggers": trigger_details
                    or ["AQ run window is still active from a recent trigger."],
                })
        return active, active_details

    def _aq_trigger_details(self, level: str, cfg: Dict[str, Any]) -> List[str]:
        details: List[str] = []
        triggers = cfg.get("triggers", [])
        thresholds = cfg.get("thresholds", {})
        for trig in triggers:
            threshold = thresholds.get(trig)
            if trig == "iaq_bad":
                val = self._level_avg("iaq", level)
                threshold_val = _to_float(threshold)
                if val is not None and threshold_val is not None and val <= threshold_val:
                    details.append(f"IAQ {val:.1f} <= threshold {threshold_val:g}")
            if trig == "pm25_high":
                val = self._level_avg("pm25", level)
                threshold_val = _to_float(threshold)
                if val is not None and threshold_val is not None and val >= threshold_val:
                    details.append(f"PM2.5 {val:.1f} >= threshold {threshold_val:g}")
            if trig == "voc_bad":
                val = self._level_avg("voc", level)
                threshold_val = _to_float(threshold)
                if val is not None and threshold_val is not None and val >= threshold_val:
                    details.append(f"VOC {val:.1f} >= threshold {threshold_val:g}")
            if trig == "co2_high":
                val = self._level_avg("co2", level)
                threshold_val = _to_float(threshold)
                if val is not None and threshold_val is not None and val >= threshold_val:
                    details.append(f"CO2 {val:.1f} >= threshold {threshold_val:g}")
            if trig == "co_warning":
                val = self._level_avg("co", level)
                threshold_val = _to_float(threshold)
                if val is not None and threshold_val is not None and val >= threshold_val:
                    details.append(f"CO {val:.1f} >= threshold {threshold_val:g}")
        return details

    async def _start_aq(self, level: str, cfg: Dict[str, Any]) -> None:
        outputs = cfg.get("outputs", [])
        output_level = _normalize_fan_level(
            cfg.get("output_level", ZONE_OUTPUT_LEVEL_DEFAULT),
            ZONE_OUTPUT_LEVEL_DEFAULT,
        )
        duration = _bounded_int(cfg.get("run_duration", 30), 1, 24 * 60, 30) * 60
        await self._set_fan_outputs_level(outputs, output_level)
        await self._set_aq_level_active(level, True)
        await self._set_aq_level_timer(level, duration)

        if task := self._aq_tasks.get(level):
            task.cancel()

        async def _timer() -> None:
            await asyncio.sleep(duration)
            if self._aq_trigger_details(level, cfg):
                await self._start_aq(level, cfg)
            else:
                reserved = self._aq_outputs_reserved_by_other_levels(level)
                outputs_to_auto = [entity_id for entity_id in outputs if entity_id not in reserved]
                await self._set_fan_outputs_auto(outputs_to_auto)
                await self._set_aq_level_active(level, False)
                await self._clear_aq_level_timer(level)
                self._aq_trigger_active[level] = False
                await self.async_request_evaluate()

        self._aq_tasks[level] = asyncio.create_task(_timer())

    async def _handle_humidifiers(self) -> List[Dict[str, Any]]:
        active_details: List[Dict[str, Any]] = []
        profile = self._active_target_profile()
        configured_levels = set(self.humidifiers.keys())
        for level in ("level1", "level2"):
            if level in configured_levels:
                continue
            await self._set_bool(self._humidifier_active_key(level), False)

        for level, cfg in self.humidifiers.items():
            active_key = self._humidifier_active_key(level)
            outputs = cfg.get("outputs", [])
            if not cfg.get("enabled"):
                await self._set_humidifier_outputs_state(outputs, False)
                await self._set_bool(active_key, False)
                continue
            if not outputs:
                await self._set_bool(active_key, False)
                continue
            avg = self._level_avg("humidity", level)
            if avg is None:
                await self._set_bool(active_key, False)
                continue
            band_adjust = _to_float(cfg.get("band_adjust", 0))
            if band_adjust is None:
                band_adjust = 0.0
            recovery_in_band = _to_float(cfg.get("recovery_in_band", HUMIDIFIER_RECOVERY_IN_BAND_DEFAULT))
            if recovery_in_band is None:
                recovery_in_band = float(HUMIDIFIER_RECOVERY_IN_BAND_DEFAULT)
            recovery_in_band = max(1.0, min(8.0, recovery_in_band))
            low = profile.low + band_adjust
            high = profile.high + band_adjust
            high_risk = profile.high_risk + band_adjust
            recovery_off = min(high, low + recovery_in_band)
            currently_active = self._bool_is_on(active_key)
            lane_label = "downstairs" if level == "level1" else "upstairs"
            if avg <= low:
                action = "hold_on"
                if not currently_active:
                    await self._set_humidifier_outputs_state(outputs, True)
                    await self._set_bool(active_key, True)
                    action = "turn_on"
                _LOGGER.debug(
                    "HI entry %s humidifier trigger: lane=%s humidity=%.1f start<=%.1f stop>=%.1f target=%.1f-%.1f season=%s action=%s",
                    self.entry.entry_id,
                    lane_label,
                    avg,
                    low,
                    recovery_off,
                    low,
                    high,
                    profile.label,
                    action,
                )
                active_details.append({
                    "level": level,
                    "lane": lane_label,
                    "season": profile.label,
                    "profile": profile.key,
                    "status": "active",
                    "action": action,
                    "humidity": avg,
                    "low": low,
                    "high": high,
                    "high_risk": high_risk,
                    "recovery_off": recovery_off,
                    "outputs": outputs,
                    "trigger_condition": f"{avg:.1f}% <= start threshold {low:.1f}%",
                    "recovery_behavior": (
                        f"Stop when humidity recovers to {recovery_off:.1f}% "
                        f"(inside target band {low:.1f}-{high:.1f}%)."
                    ),
                })
            elif avg >= recovery_off:
                action = "hold_off"
                if currently_active:
                    await self._set_humidifier_outputs_state(outputs, False)
                    await self._set_bool(active_key, False)
                    action = "turn_off"
                _LOGGER.debug(
                    "HI entry %s humidifier stop: lane=%s humidity=%.1f start<=%.1f stop>=%.1f target=%.1f-%.1f season=%s action=%s",
                    self.entry.entry_id,
                    lane_label,
                    avg,
                    low,
                    recovery_off,
                    low,
                    high,
                    profile.label,
                    action,
                )
            else:
                if currently_active:
                    _LOGGER.debug(
                        "HI entry %s humidifier recovering: lane=%s humidity=%.1f start<=%.1f stop>=%.1f target=%.1f-%.1f season=%s",
                        self.entry.entry_id,
                        lane_label,
                        avg,
                        low,
                        recovery_off,
                        low,
                        high,
                        profile.label,
                    )
                    active_details.append({
                        "level": level,
                        "lane": lane_label,
                        "season": profile.label,
                        "profile": profile.key,
                        "status": "recovering",
                        "action": "hold_on",
                        "humidity": avg,
                        "low": low,
                        "high": high,
                        "high_risk": high_risk,
                        "recovery_off": recovery_off,
                        "outputs": outputs,
                        "trigger_condition": (
                            f"{avg:.1f}% is between start {low:.1f}% and stop {recovery_off:.1f}%"
                        ),
                        "recovery_behavior": (
                            f"Lane stays on until humidity reaches {recovery_off:.1f}% to avoid short-cycling."
                        ),
                    })
        return active_details

    async def _return_to_normal(self) -> None:
        await self._clear_alert_activity_switches()
        await self._set_zone_outputs_auto()
        await self._deactivate_aq_activity(set_fan_auto=True)
        await self._deactivate_humidifier_activity(turn_off_outputs=True)
        await self._set_runtime_mode("normal", "NORMAL")
        await self._set_runtime_reason(
            self._with_isolation_notice(
                "All lanes are idle, so outputs have returned to normal automatic behavior."
            )
        )

    async def _deactivate_non_alert_activity(self, exclude_zone_outputs: Optional[List[str]] = None) -> None:
        await self._deactivate_aq_activity(
            set_fan_auto=True,
            exclude_outputs=exclude_zone_outputs,
        )
        await self._set_zone_outputs_auto(exclude=exclude_zone_outputs)
        await self._deactivate_humidifier_activity(turn_off_outputs=True)

    async def _deactivate_humidifier_activity(self, *, turn_off_outputs: bool) -> None:
        for cfg in self.humidifiers.values():
            outputs = cfg.get("outputs", [])
            if turn_off_outputs:
                await self._set_humidifier_outputs_state(outputs, False)
        await self._set_bool("air_downstairs_humidifier_active", False)
        await self._set_bool("air_upstairs_humidifier_active", False)

    async def _deactivate_aq_activity(
        self,
        *,
        set_fan_auto: bool,
        exclude_outputs: Optional[List[str]] = None,
    ) -> None:
        excluded = set(exclude_outputs or [])
        for level, task in list(self._aq_tasks.items()):
            if task and not task.done():
                task.cancel()
            self._aq_tasks.pop(level, None)

        for cfg in self.aq.values():
            outputs = cfg.get("outputs", [])
            if set_fan_auto:
                outputs = [entity_id for entity_id in outputs if entity_id not in excluded]
                await self._set_fan_outputs_auto(outputs)
        self._aq_trigger_active = {}
        await self._set_bool("air_aq_upstairs_active", False)
        await self._set_bool("air_aq_downstairs_active", False)
        await self._clear_timer("air_aq_upstairs_run")
        await self._clear_timer("air_aq_downstairs_run")

    async def _clear_alert_activity_switches(self) -> None:
        await self._sync_alert_activity_switches({})

    async def _sync_alert_activity_switches(self, states: Dict[int, bool]) -> None:
        for idx in range(max(len(self.alerts), 5)):
            await self._set_bool(self._alert_switch_key(idx), bool(states.get(idx, False)))

    async def _cancel_aq_task(self, level: str) -> None:
        task = self._aq_tasks.pop(level, None)
        if task and not task.done():
            task.cancel()
        self._aq_trigger_active[level] = False

    def _alert_switch_key(self, idx: int) -> str:
        return f"air_alert_{idx + 1}_active"

    def _alert_label(
        self,
        idx: int,
        alert: Dict[str, Any],
        *,
        resolved_room: Optional[str] = None,
    ) -> str:
        trigger_type = str(alert.get("trigger_type") or "unknown")
        trigger_label = ALERT_TRIGGER_DEFS.get(trigger_type, {}).get(
            "label",
            trigger_type.replace("_", " ").title(),
        )
        threshold = alert.get("threshold")
        threshold_suffix = ""
        if trigger_type == "humidity_danger":
            profile = self._active_target_profile()
            threshold_suffix = f" @ active {profile.label} high-risk {profile.high_risk:g}"
        elif threshold not in (None, "") and trigger_type == "co_emergency":
            default_threshold = (
                float(CO_EMERGENCY_START)
            )
            threshold = _safe_alert_threshold(trigger_type, threshold, default_threshold)
            threshold_suffix = f" @ {threshold}"
        room_scope = resolved_room or self._alert_room_scope(alert)
        room_suffix = f" in {room_scope}" if room_scope else ""
        return f"Alert {idx + 1}: {trigger_label}{threshold_suffix}{room_suffix}"

    def _alert_room_scope(self, alert: Dict[str, Any]) -> Optional[str]:
        trigger_type = str(alert.get("trigger_type") or "")
        if trigger_type not in ROOM_SCOPED_ALERT_TRIGGERS:
            return None
        raw = str(alert.get("room") or "").strip()
        if not raw:
            return None
        raw_key = raw.lower()
        for item in self.telemetry:
            room = str(item.get("room") or "").strip()
            if not room:
                continue
            if room.lower() == raw_key:
                return room
        return raw

    def _room_condensation_danger(self, room: str) -> bool:
        rh = self._rooms_avg("humidity", [room])
        temp = self._rooms_avg("temperature", [room])
        if rh is None or temp is None:
            _LOGGER.debug(
                "Room-scoped condensation alert skipped for %s: missing humidity/temperature telemetry.",
                room,
            )
            return False
        dp = _dew_point(temp, rh)
        if dp is None:
            return False
        spread = temp - dp
        profile = self._active_target_profile()
        return seasonal_condensation_risk(spread, profile) == "Danger"

    def _room_mould_danger(self, room: str) -> bool:
        rh = self._rooms_avg("humidity", [room])
        temp = self._rooms_avg("temperature", [room])
        if rh is None or temp is None:
            _LOGGER.debug(
                "Room-scoped mould alert skipped for %s: missing humidity/temperature telemetry.",
                room,
            )
            return False
        dp = _dew_point(temp, rh)
        if dp is None:
            return False
        spread = temp - dp
        profile = self._active_target_profile()
        return seasonal_mould_level(rh, spread, profile) >= 3

    def _matching_humidity_sensor(
        self,
        threshold: float,
        room_scope: Optional[str],
    ) -> Optional[Tuple[str, str, float]]:
        matches: List[Tuple[str, str, float]] = []
        room_filter = room_scope.lower().strip() if room_scope else None
        for item in self.telemetry:
            if item.get("sensor_type") != "humidity":
                continue
            room = str(item.get("room") or "").strip()
            if room_filter and room.lower() != room_filter:
                continue
            entity_id = item.get("entity_id")
            value = _get_float(self.hass, entity_id, sensor_type="humidity")
            if entity_id and room and value is not None and value >= threshold:
                matches.append((entity_id, room, value))
        if not matches:
            return None
        return max(matches, key=lambda item: item[2])

    def _matching_condensation_room(
        self,
        severity: str,
        room_scope: Optional[str],
    ) -> Tuple[Optional[str], Optional[str]]:
        profile = self._active_target_profile()
        target_rank = _RISK_ORDER.get(severity, 2)
        candidates: List[Tuple[int, float, str, Optional[str]]] = []
        for room, sensors in _room_map(self.telemetry).items():
            if room_scope and room.lower().strip() != room_scope.lower().strip():
                continue
            rh = _get_float(self.hass, sensors.get("humidity"), sensor_type="humidity")
            temp = _get_float(self.hass, sensors.get("temperature"), sensor_type="temperature")
            if rh is None or temp is None:
                _LOGGER.debug(
                    "Condensation alert skipped for %s: missing humidity/temperature telemetry.",
                    room,
                )
                continue
            dp = _dew_point(temp, rh)
            if dp is None:
                continue
            spread = temp - dp
            risk = seasonal_condensation_risk(spread, profile)
            rank = _RISK_ORDER.get(risk, -1)
            if rank >= target_rank:
                candidates.append((rank, -spread, room, sensors.get("humidity")))
        if not candidates:
            return None, None
        _rank, _spread, room, sensor = max(candidates, key=lambda item: (item[0], item[1]))
        return room, sensor

    def _matching_mould_room(
        self,
        severity: str,
        room_scope: Optional[str],
    ) -> Tuple[Optional[str], Optional[str]]:
        profile = self._active_target_profile()
        target_rank = _RISK_ORDER.get(severity, 2)
        candidates: List[Tuple[int, float, str, Optional[str]]] = []
        for room, sensors in _room_map(self.telemetry).items():
            if room_scope and room.lower().strip() != room_scope.lower().strip():
                continue
            rh = _get_float(self.hass, sensors.get("humidity"), sensor_type="humidity")
            temp = _get_float(self.hass, sensors.get("temperature"), sensor_type="temperature")
            if rh is None or temp is None:
                _LOGGER.debug(
                    "Mould alert skipped for %s: missing humidity/temperature telemetry.",
                    room,
                )
                continue
            dp = _dew_point(temp, rh)
            if dp is None:
                continue
            spread = temp - dp
            risk = seasonal_mould_level(rh, spread, profile)
            if risk >= target_rank:
                candidates.append((risk, rh, room, sensors.get("humidity")))
        if not candidates:
            return None, None
        _rank, _rh, room, sensor = max(candidates, key=lambda item: (item[0], item[1]))
        return room, sensor

    def _zone_for_room(self, room: Optional[str]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        if not room:
            return None, None
        room_key = room.lower().strip()
        matches: List[Tuple[int, str, Dict[str, Any]]] = []
        for zone_key, zone in self.zones.items():
            if not isinstance(zone, dict) or not zone.get("enabled"):
                continue
            rooms = [str(item).lower().strip() for item in zone.get("rooms", []) or []]
            if room_key in rooms:
                matches.append((_zone_priority(zone_key), zone_key, zone))
        if not matches:
            return None, None
        matches.sort(key=lambda item: item[0])
        if len(matches) > 1:
            _LOGGER.debug(
                "HI alert room-zone ambiguity for %s resolved to %s by zone priority.",
                room,
                matches[0][1],
            )
        return matches[0][1], matches[0][2]

    def _build_runtime_reason(
        self,
        *,
        runtime_mode: str,
        alert_labels: List[Any],
        zone1_active: bool,
        zone2_active: bool,
        aq_active: bool,
        zone1_detail: Optional[Dict[str, Any]],
        zone2_detail: Optional[Dict[str, Any]],
        aq_details: List[Dict[str, Any]],
        humidifier_details: List[Dict[str, Any]],
    ) -> str:
        base_reason = ""
        if runtime_mode == "alert" and alert_labels:
            base_reason = self._format_alert_detail(alert_labels)
        elif runtime_mode == "cooking":
            if zone1_detail:
                zone_label = zone1_detail.get("ui_label") or "Zone 1"
                base_reason = self._format_zone_detail(zone1_detail, str(zone_label))
            else:
                base_reason = "Zone 1 extraction is active."
        elif runtime_mode == "bathroom":
            if zone2_detail:
                zone_label = zone2_detail.get("ui_label") or "Zone 2"
                base_reason = self._format_zone_detail(zone2_detail, str(zone_label))
            else:
                base_reason = "Zone 2 extraction is active."
        elif runtime_mode == "air_quality" and aq_active:
            base_reason = self._format_aq_detail(aq_details)
        else:
            house_humidity = self._level_avg("humidity", None)
            if house_humidity is not None:
                base_reason = (
                    "System is armed and monitoring telemetry. "
                    f"Current house humidity is {house_humidity:.1f}% and no lane currently needs to run."
                )
            else:
                base_reason = "System is armed and monitoring telemetry. No automation lane currently needs to run."

        notices: List[str] = []
        humidifier_reason = self._format_humidifier_detail(humidifier_details) if humidifier_details else ""
        if humidifier_reason:
            notices.append(humidifier_reason)
        if runtime_mode != "alert":
            alert_notice = self._format_nonblocking_alert_notice(alert_labels)
            if alert_notice:
                notices.append(alert_notice)
        if notices:
            return f"{base_reason} {' '.join(notices)}".strip()
        return base_reason

    def _format_zone_detail(self, detail: Dict[str, Any], zone_label: str) -> str:
        outputs = self._format_output_entities(detail.get("outputs", []))
        run_level = _fan_level_text(detail.get("output_level"))
        trigger_summary = "; ".join(detail.get("triggers", [])) or "configured trigger condition met"
        return (
            f"{zone_label} is active at {run_level} on {outputs}. "
            f"Trigger detail: {trigger_summary}."
        )

    def _format_alert_detail(self, details: List[Any]) -> str:
        if not details:
            return "Alert response is active. All lower-priority lanes are paused until the alert clears."
        if not isinstance(details[0], dict):
            return (
                f"Alert response is active ({'; '.join(str(item) for item in details)}). "
                "All lower-priority lanes are paused until the alert clears."
            )
        selected = details[0]
        segments = [
            f"Alert response is active ({selected.get('companion') or selected.get('label')})."
        ]
        sensor = selected.get("sensor") or "unknown"
        room = selected.get("room") or "unknown"
        zone = selected.get("zone") or "unmapped"
        segments.append(f"Originating sensor: {sensor}; room: {room}; resolved zone: {zone}.")
        if selected.get("outputs") and selected.get("boost_level"):
            outputs = self._format_output_entities(selected.get("outputs", []))
            run_level = _fan_level_text(selected.get("boost_level"))
            segments.append(
                f"Selected {zone} boost level {run_level} on {outputs} because alerts override zone, AQ, and normal lanes."
            )
            if selected.get("held_until_clear"):
                segments.append(
                    "Boost selection is being held until this originating alert clears; equal-priority candidates wait their turn."
                )
            else:
                segments.append(
                    "Boost selection will be held while this originating alert remains active, then the next priority is evaluated."
                )
        else:
            segments.append("Degraded mode: no zone boost was applied because the alert could not be safely mapped to configured zone outputs.")
        if selected.get("threshold_source") and selected.get("threshold") is not None:
            threshold = selected.get("threshold")
            unit = "%" if selected.get("trigger_type") == "humidity_danger" else ""
            segments.append(
                f"Threshold source: {selected['threshold_source']}; threshold {threshold:g}{unit}."
            )
        if selected.get("measured"):
            segments.append(f"Trigger detail: {selected['measured']}.")
        if len(details) > 1:
            candidates = "; ".join(
                str(item.get("companion") or item.get("label")) for item in details
            )
            if any(not _alert_can_control(item) for item in details[1:] if isinstance(item, dict)):
                segments.append(
                    f"Conflict detected across active alerts; selected the next actionable mapped alert after skipping degraded candidates. Candidates: {candidates}."
                )
            elif selected.get("held_until_clear"):
                segments.append(
                    f"Conflict detected across active alerts; held the existing actionable alert until clear. Candidates: {candidates}."
                )
            else:
                segments.append(
                    f"Conflict detected across active alerts; resolved deterministically by alert hierarchy then zone priority. Candidates: {candidates}."
                )
        if selected.get("degraded_reasons"):
            segments.append("Mapping issues: " + "; ".join(selected.get("degraded_reasons", [])))
        skipped_notice = self._format_skipped_alert_notice(details[1:])
        if skipped_notice:
            segments.append(skipped_notice)
        segments.append("Overridden logic: zone automation, AQ, and normal lanes are paused until the selected alert clears.")
        return " ".join(segments)

    def _format_nonblocking_alert_notice(self, details: List[Any]) -> str:
        if not details or not isinstance(details[0], dict):
            return ""
        skipped_notice = self._format_skipped_alert_notice(
            [detail for detail in details if not _alert_can_control(detail)]
        )
        if not skipped_notice:
            return ""
        return (
            f"{skipped_notice} Automation continued to the next eligible priority "
            "instead of applying a blind boost."
        )

    def _format_skipped_alert_notice(self, details: List[Dict[str, Any]]) -> str:
        skipped = [detail for detail in details if not _alert_can_control(detail)]
        if not skipped:
            return ""
        parts = []
        for detail in skipped[:3]:
            label = str(detail.get("companion") or detail.get("label") or "Alert")
            reasons = detail.get("degraded_reasons") or []
            if reasons:
                parts.append(f"{label} ({'; '.join(str(reason) for reason in reasons)})")
            else:
                parts.append(f"{label} (no mapped zone boost output)")
        suffix = "" if len(skipped) <= 3 else f"; plus {len(skipped) - 3} more"
        return f"Skipped alert candidate(s): {'; '.join(parts)}{suffix}."

    def _format_aq_detail(self, details: List[Dict[str, Any]]) -> str:
        if not details:
            return "Air-quality assist is active."
        segments: List[str] = []
        for item in details:
            level = "Downstairs" if item.get("level") == "level1" else "Upstairs"
            outputs = self._format_output_entities(item.get("outputs", []))
            run_level = _fan_level_text(item.get("output_level"))
            triggers = "; ".join(item.get("triggers", []))
            segments.append(
                f"{level} AQ is active at {run_level} on {outputs}. Trigger detail: {triggers}."
            )
        return " ".join(segments)

    def _format_humidifier_detail(self, details: List[Dict[str, Any]]) -> str:
        if not details:
            return ""

        active = [item for item in details if item.get("status") in {"active", "recovering"}]
        if not active:
            return ""

        if len(active) >= 2:
            segments: List[str] = ["Humidifier: downstairs and upstairs lanes are active."]
        else:
            lane = "downstairs" if active[0].get("level") == "level1" else "upstairs"
            status = "recovering" if str(active[0].get("status") or "") == "recovering" else "running"
            segments = [f"Humidifier: {lane} lane is {status}."]

        for item in active:
            level = "Downstairs" if item.get("level") == "level1" else "Upstairs"
            humidity = _to_float(item.get("humidity"))
            low = _to_float(item.get("low"))
            high = _to_float(item.get("high"))
            recovery_off = _to_float(item.get("recovery_off"))
            status = str(item.get("status") or "active")

            if humidity is None or low is None or high is None or recovery_off is None:
                segments.append(f"{level}: humidity data is unavailable.")
                continue

            if status == "recovering":
                segments.append(
                    f"{level}: {humidity:.1f}% (target {low:.1f}-{high:.1f}%). "
                    f"Holding on until {recovery_off:.1f}% to avoid short-cycling."
                )
            else:
                segments.append(
                    f"{level}: {humidity:.1f}% is at or below the {low:.1f}% start point "
                    f"(target {low:.1f}-{high:.1f}%). It will stop at {recovery_off:.1f}%."
                )
        return " ".join(segments)

    def _entity_display_name(self, entity_id: str) -> str:
        state = self.hass.states.get(entity_id)
        if state is not None:
            friendly_name = state.attributes.get("friendly_name")
            if friendly_name:
                return str(friendly_name)
        return entity_id

    def _format_output_entities(self, entity_ids: List[str]) -> str:
        entities = [entity_id for entity_id in entity_ids if entity_id]
        if not entities:
            return "no outputs configured"
        return ", ".join(self._entity_display_name(entity_id) for entity_id in entities)

    def _co_emergency_settings(self) -> Tuple[float, float, List[str]]:
        start_threshold = float(CO_EMERGENCY_START)
        configured_thresholds: List[float] = []

        for alert in self.alerts:
            if not alert.get("enabled", True):
                continue
            if alert.get("trigger_type") != "co_emergency":
                continue
            threshold = _safe_alert_threshold("co_emergency", alert.get("threshold"), float(CO_EMERGENCY_START))
            configured_thresholds.append(threshold)

        if configured_thresholds:
            start_threshold = min(configured_thresholds)

        clear_threshold = max(0.0, start_threshold - 5.0)
        if clear_threshold >= start_threshold:
            clear_threshold = max(0.0, start_threshold - 1.0)

        return start_threshold, clear_threshold, self._all_fan_outputs()

    def _humidifier_active_key(self, level: str) -> str:
        return f"air_{'downstairs' if level == 'level1' else 'upstairs'}_humidifier_active"

    def _active_humidifier_levels(self) -> List[str]:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        booleans = data.get("hi_input_booleans", {})
        active: List[str] = []
        if booleans.get("air_downstairs_humidifier_active") and booleans["air_downstairs_humidifier_active"].is_on:
            active.append("Downstairs")
        if booleans.get("air_upstairs_humidifier_active") and booleans["air_upstairs_humidifier_active"].is_on:
            active.append("Upstairs")
        return active

    async def _set_aq_level_active(self, level: str, is_active: bool) -> None:
        key = f"air_aq_{'upstairs' if level == 'level2' else 'downstairs'}_active"
        await self._set_bool(key, is_active)

    async def _set_aq_level_timer(self, level: str, duration_seconds: int) -> None:
        key = f"air_aq_{'upstairs' if level == 'level2' else 'downstairs'}_run"
        await self._set_timer(key, duration_seconds)

    async def _clear_aq_level_timer(self, level: str) -> None:
        key = f"air_aq_{'upstairs' if level == 'level2' else 'downstairs'}_run"
        await self._clear_timer(key)

    async def _set_bool(self, key: str, value: bool) -> None:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        booleans = data.get("hi_input_booleans", {})
        entity = booleans.get(key)
        if entity:
            if bool(getattr(entity, "is_on", False)) == bool(value):
                return
            if value:
                await entity.async_turn_on()
            else:
                await entity.async_turn_off()

    async def _set_timer(self, key: str, duration_seconds: int) -> None:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        timers = data.get("hi_timers", {})
        entity = timers.get(key)
        if entity:
            await entity.async_start(timedelta(seconds=duration_seconds))

    async def _clear_timer(self, key: str) -> None:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        timers = data.get("hi_timers", {})
        entity = timers.get(key)
        if entity:
            await entity.async_cancel()

    async def _set_runtime_mode(self, mode: str, display: Optional[str] = None) -> None:
        data = self.hass.data.setdefault(DOMAIN, {}).setdefault(self.entry.entry_id, {})
        data["runtime_mode"] = mode
        data["runtime_mode_display"] = display or mode.replace("_", " ").upper()

    async def _set_runtime_reason(self, reason: str) -> None:
        data = self.hass.data.setdefault(DOMAIN, {}).setdefault(self.entry.entry_id, {})
        safe_reason, full_reason = _state_safe_reason(reason)
        data["runtime_reason"] = safe_reason
        data["runtime_reason_full"] = full_reason
        data["runtime_reason_truncated"] = bool(full_reason)

    def _bool_is_on(self, key: str) -> bool:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        booleans = data.get("hi_input_booleans", {})
        entity = booleans.get(key)
        return bool(entity and getattr(entity, "is_on", False))

    def _fan_outputs_isolated(self) -> bool:
        return self._bool_is_on("air_isolate_fan_outputs")

    def _humidifier_outputs_isolated(self) -> bool:
        return self._bool_is_on("air_isolate_humidifier_outputs")

    async def _set_fan_outputs_level(self, outputs: List[str], level: Any) -> None:
        if self._fan_outputs_isolated():
            return
        await _apply_fan_level(self.hass, outputs, level)

    async def _set_fan_outputs_auto(self, outputs: List[str]) -> None:
        if self._fan_outputs_isolated():
            return
        await _set_fan_auto(self.hass, outputs)

    async def _set_humidifier_outputs_state(self, outputs: List[str], on: bool) -> None:
        if self._humidifier_outputs_isolated():
            return
        await _set_humidifier_state(self.hass, outputs, on)

    def _aq_outputs_reserved_by_other_levels(self, level: str) -> set[str]:
        reserved: set[str] = set()
        for other_level, cfg in self.aq.items():
            if other_level == level:
                continue
            task = self._aq_tasks.get(other_level)
            if task and not task.done():
                reserved.update(cfg.get("outputs", []))
        return reserved

    def _with_isolation_notice(self, reason: str) -> str:
        notices: List[str] = []
        if self._fan_outputs_isolated():
            notices.append("Fan outputs are isolated for testing (service calls suppressed).")
        if self._humidifier_outputs_isolated():
            notices.append("Humidifier outputs are isolated for testing (service calls suppressed).")
        if not notices:
            return reason
        return f"{reason} {' '.join(notices)}"

    def _zone_mode_from_zone(self, zone_key: str, zone: Dict[str, Any]) -> str:
        zone_key_lower = str(zone_key).lower()
        if "zone1" in zone_key_lower:
            return "cooking"
        if "zone2" in zone_key_lower:
            return "bathroom"

        rooms = [str(r).lower() for r in zone.get("rooms", []) if r]
        if any("kitchen" in room for room in rooms):
            return "cooking"
        if any(("bath" in room) or ("toilet" in room) or ("shower" in room) for room in rooms):
            return "bathroom"
        return "zone"

    def _zone_display_label(self, zone_key: str, mode: str) -> str:
        zone = self.zones.get(zone_key, {}) if isinstance(self.zones, dict) else {}
        configured = str(zone.get("ui_label") or "").strip()
        if configured:
            return configured[:40]
        if mode == "cooking":
            return "Cooking"
        if mode == "bathroom":
            return "Bathroom"
        if "zone1" in str(zone_key).lower():
            return "Zone 1"
        if "zone2" in str(zone_key).lower():
            return "Zone 2"
        return "Zone"

    def _pause_active(self) -> bool:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        timer = (data.get("hi_timers") or {}).get("air_control_pause")
        if timer:
            return timer.native_value == "active"
        state = self.hass.states.get("sensor.hi_air_control_pause")
        return bool(state and state.state == "active")

    async def _set_zone_outputs_auto(self, exclude: Optional[List[str]] = None) -> None:
        outputs = self._all_zone_outputs()
        if exclude:
            excluded = set(exclude)
            outputs = [entity_id for entity_id in outputs if entity_id not in excluded]
        await self._set_fan_outputs_auto(outputs)

    def _active_aq_outputs(self) -> List[str]:
        outputs: List[str] = []
        for level, cfg in self.aq.items():
            task = self._aq_tasks.get(level)
            if task and not task.done():
                outputs.extend(cfg.get("outputs", []))
        return list(set(outputs))

    def _refresh_core_entities(self) -> None:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        for sensor in data.get("core_sensors", []) or []:
            try:
                sensor.update_from_hass()
                sensor.async_write_ha_state()
            except Exception:
                _LOGGER.debug("Failed refreshing core sensor %s", getattr(sensor, "entity_id", "unknown"), exc_info=True)
        for sensor in data.get("core_binary_sensors", []) or []:
            try:
                sensor.update_from_hass()
                sensor.async_write_ha_state()
            except Exception:
                _LOGGER.debug("Failed refreshing core binary sensor %s", getattr(sensor, "entity_id", "unknown"), exc_info=True)

    def _all_zone_outputs(self) -> List[str]:
        outputs: List[str] = []
        for zone in self.zones.values():
            outputs.extend(zone.get("outputs", []))
        return list(set(outputs))

    def _all_fan_outputs(self) -> List[str]:
        outputs = self._all_zone_outputs()
        for cfg in self.aq.values():
            outputs.extend(cfg.get("outputs", []))
        return list(set(outputs))

    def _collect_values(self, sensor_type: str, room_scope: Optional[str] = None) -> List[float]:
        values: List[float] = []
        room_filter = room_scope.lower().strip() if room_scope else None
        for item in self.telemetry:
            if item.get("sensor_type") != sensor_type:
                continue
            if room_filter:
                item_room = str(item.get("room") or "").strip().lower()
                if item_room != room_filter:
                    continue
            val = _get_float(self.hass, item.get("entity_id"), sensor_type=sensor_type)
            if val is not None:
                values.append(val)
        return values

    def _level_avg(self, sensor_type: str, level: Optional[str]) -> Optional[float]:
        vals: List[float] = []
        for item in self.telemetry:
            if item.get("sensor_type") != sensor_type:
                continue
            if level and item.get("level") != level:
                continue
            val = _get_float(self.hass, item.get("entity_id"), sensor_type=sensor_type)
            if val is not None:
                vals.append(val)
        if not vals:
            return None
        return round(sum(vals) / len(vals), 1)

    def _rooms_avg(self, sensor_type: str, rooms: List[str]) -> Optional[float]:
        if not rooms:
            return None
        room_set = {room.lower() for room in rooms if room}
        vals: List[float] = []
        for item in self.telemetry:
            if item.get("sensor_type") != sensor_type:
                continue
            room = (item.get("room") or "").lower()
            if room not in room_set:
                continue
            val = _get_float(self.hass, item.get("entity_id"), sensor_type=sensor_type)
            if val is not None:
                vals.append(val)
        if not vals:
            return None
        return round(sum(vals) / len(vals), 1)

    def _worst_spread(self) -> Optional[float]:
        spreads: List[float] = []
        rooms = _room_map(self.telemetry)
        for room, sensors in rooms.items():
            rh = _get_float(self.hass, sensors.get("humidity"), sensor_type="humidity")
            temp = _get_float(self.hass, sensors.get("temperature"), sensor_type="temperature")
            if rh is None or temp is None:
                continue
            dp = _dew_point(temp, rh)
            if dp is None:
                continue
            spreads.append(temp - dp)
        return min(spreads) if spreads else None

    def _worst_mould_level(self) -> int:
        rooms = _room_map(self.telemetry)
        profile = self._active_target_profile()
        level = 0
        for room, sensors in rooms.items():
            rh = _get_float(self.hass, sensors.get("humidity"), sensor_type="humidity")
            temp = _get_float(self.hass, sensors.get("temperature"), sensor_type="temperature")
            if rh is None or temp is None:
                continue
            dp = _dew_point(temp, rh)
            if dp is None:
                continue
            spread = temp - dp
            risk = seasonal_mould_level(rh, spread, profile)
            level = max(level, risk)
        return level

    def _active_target_profile(self):
        return resolve_target_profile(self._effective_config())

    def _effective_config(self) -> Dict[str, Any]:
        config = dict(getattr(self.entry, "data", None) or {})
        config.update(dict(getattr(self.entry, "options", None) or {}))
        return config


def _get_float(
    hass: HomeAssistant,
    entity_id: Optional[str],
    *,
    sensor_type: Optional[str] = None,
) -> Optional[float]:
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None:
        return None
    raw_state = str(state.state).strip()
    if raw_state.lower() in ("unknown", "unavailable"):
        return None
    if sensor_type == "temperature":
        value_c, _reason = parse_temperature(
            state.state,
            state.attributes.get("unit_of_measurement"),
            hass_temperature_unit(hass),
        )
        return value_c
    return parse_numeric(raw_state)


def _room_map(telemetry: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    rooms: Dict[str, Dict[str, str]] = {}
    for item in telemetry:
        room = item.get("room")
        if not room:
            continue
        rooms.setdefault(room, {})[item.get("sensor_type")] = item.get("entity_id")
    return rooms


def _dew_point(temp_c: float, rh: float) -> Optional[float]:
    if rh <= 0:
        return None
    import math
    a = 17.62
    b = 243.12
    gamma = (a * temp_c / (b + temp_c)) + math.log(rh / 100.0)
    return (b * gamma) / (a - gamma)


def _parse_time(value) -> Optional[datetime.time]:
    if value is None:
        return None
    if hasattr(value, "hour"):
        return value
    try:
        parts = str(value).split(":")
        return datetime.strptime(f"{int(parts[0]):02d}:{int(parts[1]):02d}", "%H:%M").time()
    except Exception:
        return None


def _time_in_window(now, start, end) -> bool:
    if start <= end:
        return start <= now <= end
    # Overnight window
    return now >= start or now <= end


def _normalize_fan_level(value: Any, fallback: Any) -> str:
    raw = value if value is not None else fallback
    if isinstance(raw, str):
        text = raw.strip().lower()
        if text == FAN_OUTPUT_LEVEL_AUTO:
            return FAN_OUTPUT_LEVEL_AUTO
        if text.endswith("%"):
            text = text[:-1]
        try:
            raw = int(float(text))
        except (TypeError, ValueError):
            raw = None
    try:
        numeric = int(raw)
    except (TypeError, ValueError):
        numeric = int(fallback) if str(fallback).isdigit() else ZONE_OUTPUT_LEVEL_DEFAULT
    if numeric <= 0:
        return FAN_OUTPUT_LEVEL_AUTO
    if numeric >= 100:
        return "100"
    nearest = min(FAN_OUTPUT_LEVEL_STEPS, key=lambda step: abs(step - numeric))
    return str(nearest)


def _fan_level_rank(level: Optional[str]) -> int:
    if not level:
        return 0
    normalized = _normalize_fan_level(level, ZONE_OUTPUT_LEVEL_DEFAULT)
    if normalized == FAN_OUTPUT_LEVEL_AUTO:
        return 0
    try:
        return int(normalized)
    except (TypeError, ValueError):
        return 0


def _max_fan_level(current: Optional[str], candidate: str) -> str:
    if current is None:
        return candidate
    return candidate if _fan_level_rank(candidate) >= _fan_level_rank(current) else current


def _fan_level_text(level: Any) -> str:
    normalized = _normalize_fan_level(level, ZONE_OUTPUT_LEVEL_DEFAULT)
    if normalized == FAN_OUTPUT_LEVEL_AUTO:
        return "Auto"
    return f"{normalized}%"


def _alert_can_control(detail: Dict[str, Any]) -> bool:
    return bool(
        detail
        and not detail.get("degraded")
        and detail.get("outputs")
        and detail.get("boost_level")
    )


def _alert_identity(detail: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        str(detail.get("trigger_type") or ""),
        str(detail.get("sensor") or ""),
        str(detail.get("room") or ""),
    )


def _alert_priority(trigger_type: str) -> int:
    return _ALERT_PRIORITY.get(str(trigger_type or ""), 999)


def _zone_priority(zone_key: Optional[str]) -> int:
    if zone_key == "zone1":
        return 1
    if zone_key == "zone2":
        return 2
    return 999


def _alert_kind_and_severity(trigger_type: str) -> Tuple[str, str]:
    text = str(trigger_type or "alert").lower()
    if "mould" in text:
        kind = "Mould"
    elif "condensation" in text:
        kind = "Condensation"
    elif "humidity" in text:
        kind = "Humidity"
    elif "co" in text:
        kind = "CO"
    else:
        kind = "Alert"
    if "danger" in text:
        severity = "Danger"
    elif "risk" in text:
        severity = "Risk"
    elif "emergency" in text:
        severity = "Emergency"
    else:
        severity = "Active"
    return kind, severity


def _alert_companion_label(
    kind: str,
    severity: str,
    room: Optional[str],
    zone_label: Optional[str],
) -> str:
    base = f"{kind} {severity}".strip()
    if room and zone_label:
        return f"{base} - {room} ({zone_label})"
    if room:
        return f"{base} - {room} (unmapped zone)"
    if zone_label:
        return f"{base} - {zone_label}"
    return base


def _alert_source_summary(
    *,
    trigger_type: str,
    room: Optional[str],
    zone: Optional[str],
    measured: Optional[str],
    threshold: Optional[str],
) -> str:
    kind, severity = _alert_kind_and_severity(trigger_type)
    parts = [f"{kind} {severity}".strip()]
    if room:
        parts.append(str(room))
    if zone:
        parts.append(str(zone))
    if measured and threshold:
        parts.append(f"{measured} >= {threshold}")
    return " · ".join(part for part in parts if part)


async def _apply_fan_level(hass: HomeAssistant, entities: List[str], level: Any) -> None:
    normalized = _normalize_fan_level(level, ZONE_OUTPUT_LEVEL_DEFAULT)
    if normalized == FAN_OUTPUT_LEVEL_AUTO:
        await _set_fan_auto(hass, entities)
        return
    await _set_fan_percentage(hass, entities, int(normalized))


def _coerce_fan_percentage(value: Any) -> int:
    pct = _bounded_int(value, 0, 100, ZONE_OUTPUT_LEVEL_DEFAULT)
    if pct <= 0:
        return 0
    if pct >= 100:
        return 100
    return min(FAN_OUTPUT_LEVEL_STEPS, key=lambda step: abs(step - pct))


async def _set_fan_percentage(hass: HomeAssistant, entities: List[str], pct: int) -> None:
    pct = _coerce_fan_percentage(pct)
    for entity_id in entities:
        domain = entity_id.split(".")[0]
        state = hass.states.get(entity_id)
        if domain == "fan":
            if not hass.services.has_service("fan", "turn_on") or not hass.services.has_service("fan", "set_percentage"):
                _LOGGER.debug("Skipping fan percentage for %s; service unavailable", entity_id)
                continue
            current_pct = state.attributes.get("percentage") if state else None
            if state and state.state == "on" and current_pct is not None:
                try:
                    if int(current_pct) == int(pct):
                        continue
                except (TypeError, ValueError):
                    pass
            try:
                if not state or state.state != "on":
                    await hass.services.async_call("fan", "turn_on", {"entity_id": entity_id}, blocking=False)
                await hass.services.async_call(
                    "fan",
                    "set_percentage",
                    {"entity_id": entity_id, "percentage": pct},
                    blocking=False,
                )
            except Exception:
                _LOGGER.exception("Failed to set fan percentage for %s", entity_id)
        elif domain == "switch":
            service = "turn_on" if pct > 0 else "turn_off"
            if not hass.services.has_service("switch", service):
                _LOGGER.debug("Skipping switch update for %s; service %s unavailable", entity_id, service)
                continue
            if state and ((pct > 0 and state.state == "on") or (pct <= 0 and state.state == "off")):
                continue
            try:
                await hass.services.async_call("switch", service, {"entity_id": entity_id}, blocking=False)
            except Exception:
                _LOGGER.exception("Failed to set switch %s via %s", entity_id, service)


async def _set_fan_auto(hass: HomeAssistant, entities: List[str]) -> None:
    for entity_id in entities:
        domain = entity_id.split(".")[0]
        state = hass.states.get(entity_id)
        if domain == "fan":
            if not hass.services.has_service("fan", "set_preset_mode"):
                _LOGGER.debug("Skipping fan auto for %s; set_preset_mode unavailable", entity_id)
                continue
            preset_mode = str(state.attributes.get("preset_mode", "")).lower() if state else ""
            if preset_mode == "auto":
                continue
            try:
                await hass.services.async_call(
                    "fan",
                    "set_preset_mode",
                    {"entity_id": entity_id, "preset_mode": "auto"},
                    blocking=False,
                )
            except Exception:
                _LOGGER.exception("Failed to set fan %s to auto", entity_id)
        elif domain == "switch":
            if not hass.services.has_service("switch", "turn_off"):
                _LOGGER.debug("Skipping switch turn_off for %s; service unavailable", entity_id)
                continue
            if state and state.state == "off":
                continue
            try:
                await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=False)
            except Exception:
                _LOGGER.exception("Failed to turn off switch %s", entity_id)


async def _set_humidifier_state(hass: HomeAssistant, entities: List[str], on: bool) -> None:
    for entity_id in entities:
        domain = entity_id.split(".")[0]
        service = "turn_on" if on else "turn_off"
        if not hass.services.has_service(domain, service):
            continue
        state = hass.states.get(entity_id)
        if state and ((on and state.state == "on") or ((not on) and state.state == "off")):
            continue
        try:
            await hass.services.async_call(domain, service, {"entity_id": entity_id}, blocking=False)
        except Exception:
            _LOGGER.exception("Failed to call %s.%s for %s", domain, service, entity_id)


def _bounded_int(value: Any, min_value: int, max_value: int, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(min_value, min(max_value, parsed))


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_alert_threshold(trigger_type: str, value: Any, fallback: float) -> float:
    bounds = ALERT_THRESHOLD_BOUNDS.get(trigger_type, {})
    min_value = _to_float(bounds.get("min"))
    max_value = _to_float(bounds.get("max"))
    default_value = _to_float(bounds.get("default"))

    if default_value is None:
        default_value = fallback
    if min_value is None:
        min_value = default_value
    if max_value is None:
        max_value = default_value

    threshold = _to_float(value)
    if threshold is None:
        threshold = _to_float(fallback)
    if threshold is None:
        threshold = default_value
    return max(min_value, min(max_value, threshold))


def _state_safe_reason(reason: Any) -> Tuple[str, Optional[str]]:
    text = str(reason or "").strip()
    if not text:
        return "", None
    if len(text) <= _MAX_STATE_LENGTH:
        return text, None

    # Keep sensor state within HA's state length while preserving full context in attributes.
    head_limit = _MAX_STATE_LENGTH - len(_TRUNCATION_SUFFIX) - 3
    if head_limit < 0:
        head_limit = 0
    head = text[:head_limit].rstrip()
    if head.endswith("."):
        state = f"{head}..{_TRUNCATION_SUFFIX}"
    else:
        state = f"{head}...{_TRUNCATION_SUFFIX}"
    if len(state) > _MAX_STATE_LENGTH:
        state = state[:_MAX_STATE_LENGTH]
    return state, text
