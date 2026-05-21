"""Humidity drift dependency helpers."""

from __future__ import annotations

from typing import Any, Optional, Tuple

from .parsing import parse_numeric

HOUSE_HUMIDITY_MEAN_7D_ENTITY = "sensor.house_humidity_mean_7d"
HOUSE_HUMIDITY_DRIFT_7D_NAME = "HI House Humidity Drift 7d"
HOUSE_HUMIDITY_DRIFT_EXPECTED_SOURCE = (
    "Home Assistant statistics sensor holding the 7-day mean of HI house average humidity."
)
HOUSE_HUMIDITY_DRIFT_MIGRATION_HINT = (
    "V2 preserves the legacy drift calculation and expects the canonical statistics "
    "entity sensor.house_humidity_mean_7d to exist and report a numeric mean."
)


def numeric_entity_status(hass: Any, entity_id: Optional[str]) -> Tuple[Optional[float], dict[str, Any]]:
    """Return a numeric value plus a structured availability status for an entity."""
    if not entity_id:
        return None, {
            "entity_id": entity_id,
            "status": "not_configured",
            "available": False,
        }

    state = hass.states.get(entity_id)
    if state is None:
        return None, {
            "entity_id": entity_id,
            "status": "missing",
            "available": False,
        }

    raw_state = str(getattr(state, "state", "")).strip()
    lowered = raw_state.lower()
    if lowered in {"unknown", "unavailable"}:
        return None, {
            "entity_id": entity_id,
            "status": lowered,
            "state": raw_state,
            "available": False,
        }

    value = parse_numeric(raw_state)
    if value is None:
        return None, {
            "entity_id": entity_id,
            "status": "non_numeric",
            "state": raw_state,
            "available": False,
        }

    return value, {
        "entity_id": entity_id,
        "status": "ok",
        "state": raw_state,
        "numeric_value": value,
        "available": True,
    }


def humidity_drift_dependency_status(hass: Any) -> dict[str, Any]:
    """Describe the legacy statistics dependency required by house humidity drift."""
    mean, status = numeric_entity_status(hass, HOUSE_HUMIDITY_MEAN_7D_ENTITY)
    dependency_status = str(status.get("status") or "unknown")
    available = dependency_status == "ok"
    row: dict[str, Any] = {
        "required_for": HOUSE_HUMIDITY_DRIFT_7D_NAME,
        "dependency_entity": HOUSE_HUMIDITY_MEAN_7D_ENTITY,
        "dependency_status": dependency_status,
        "available": available,
        "expected_source": HOUSE_HUMIDITY_DRIFT_EXPECTED_SOURCE,
        "migration_hint": HOUSE_HUMIDITY_DRIFT_MIGRATION_HINT,
    }
    if status.get("state") is not None:
        row["dependency_state"] = status.get("state")
    if mean is not None:
        row["mean_7d"] = mean
    return row


def humidity_drift_warning(status: dict[str, Any]) -> Optional[str]:
    """Return a concise diagnostics warning when the drift dependency is unavailable."""
    if status.get("available"):
        return None
    dependency_status = status.get("dependency_status") or "unknown"
    dependency_entity = status.get("dependency_entity") or HOUSE_HUMIDITY_MEAN_7D_ENTITY
    return (
        f"{HOUSE_HUMIDITY_DRIFT_7D_NAME} is unavailable because required statistics "
        f"dependency {dependency_entity} is {dependency_status}."
    )


def house_drift_unavailable_attributes(
    current_house_humidity: Optional[float],
    dependency_status: dict[str, Any],
) -> dict[str, Any]:
    """Build recorder-safe attributes explaining why house drift has no value."""
    blocking_reasons = []
    if current_house_humidity is None:
        blocking_reasons.append("current_house_humidity_unavailable")
    if not dependency_status.get("available"):
        blocking_reasons.append(f"statistics_dependency_{dependency_status.get('dependency_status') or 'unknown'}")

    attrs: dict[str, Any] = {
        "status": "unavailable",
        "reason": blocking_reasons[0] if blocking_reasons else "unavailable",
        "blocking_reasons": blocking_reasons,
        "current_house_humidity": current_house_humidity,
        "required_dependency": dependency_status.get("dependency_entity") or HOUSE_HUMIDITY_MEAN_7D_ENTITY,
        "dependency_status": dependency_status.get("dependency_status"),
        "expected_source": dependency_status.get("expected_source") or HOUSE_HUMIDITY_DRIFT_EXPECTED_SOURCE,
        "migration_hint": dependency_status.get("migration_hint") or HOUSE_HUMIDITY_DRIFT_MIGRATION_HINT,
    }
    if dependency_status.get("dependency_state") is not None:
        attrs["dependency_state"] = dependency_status.get("dependency_state")
    return attrs
