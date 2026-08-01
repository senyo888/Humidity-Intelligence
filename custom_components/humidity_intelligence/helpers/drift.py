"""Humidity drift dependency helpers."""

from __future__ import annotations

from typing import Any, Optional, Tuple

from ..const import DOMAIN
from .parsing import parse_numeric

HOUSE_HUMIDITY_MEAN_7D_ENTITY = "sensor.house_humidity_mean_7d"
HOUSE_HUMIDITY_MEAN_7D_NAME = "House Humidity Mean 7d"
HOUSE_AVG_HUMIDITY_UNIQUE_SUFFIX = "house_avg_humidity"
HOUSE_HUMIDITY_MEAN_7D_REPAIR_ISSUE = "house_humidity_mean_7d_missing"
HOUSE_HUMIDITY_DRIFT_7D_NAME = "HI House Humidity Drift 7d"
HOUSE_HUMIDITY_MIN_AGE_COVERAGE_RATIO = 0.85
HOUSE_HUMIDITY_DRIFT_EXPECTED_SOURCE = (
    "Home Assistant statistics sensor holding the 7-day mean of HI house average humidity."
)
HOUSE_HUMIDITY_DRIFT_MIGRATION_HINT = (
    "Create a Statistics helper named House Humidity Mean 7d using the registered "
    "HI House Average Humidity entity as the source. Use state characteristic mean "
    "and max age 7 days. The helper entity ID must be sensor.house_humidity_mean_7d; "
    "rename the entity ID manually if Home Assistant creates a different one. Drift "
    "stays unavailable until recorder/statistics history coverage is sufficient."
)


def _parse_bool(value: Any) -> Optional[bool]:
    """Parse Home Assistant boolean-ish metadata without treating unknown as false."""
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "yes", "on", "1"}:
        return True
    if text in {"false", "no", "off", "0"}:
        return False
    return None


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

    row = {
        "entity_id": entity_id,
        "status": "ok",
        "state": raw_state,
        "numeric_value": value,
        "available": True,
    }
    attrs = getattr(state, "attributes", {}) or {}
    if isinstance(attrs, dict):
        if "age_coverage_ratio" in attrs:
            coverage = parse_numeric(attrs.get("age_coverage_ratio"))
            if coverage is not None:
                row["age_coverage_ratio"] = coverage
        if "source_value_valid" in attrs:
            source_valid = _parse_bool(attrs.get("source_value_valid"))
            if source_valid is not None:
                row["source_value_valid"] = source_valid
    return value, row


def _first_hi_entry_id(hass: Any) -> Optional[str]:
    """Resolve the first HI config-entry id without assuming a full HA runtime."""
    config_entries = getattr(hass, "config_entries", None)
    async_entries = getattr(config_entries, "async_entries", None)
    if callable(async_entries):
        try:
            entries = async_entries(DOMAIN)
        except (AttributeError, TypeError, ValueError):
            entries = []
        if entries:
            entry_id = getattr(entries[0], "entry_id", None)
            if entry_id:
                return str(entry_id)

    data = getattr(hass, "data", {})
    domain_data = data.get(DOMAIN, {}) if isinstance(data, dict) else {}
    if isinstance(domain_data, dict) and domain_data:
        return str(next(iter(domain_data)))
    return None


def _registered_house_avg_humidity_entity(hass: Any) -> Optional[str]:
    """Return the registered HI house-average humidity entity id when available."""
    entry_id = _first_hi_entry_id(hass)
    if not entry_id:
        return None
    try:
        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(hass)
        if registry is None:
            return None
        return registry.async_get_entity_id(
            "sensor",
            DOMAIN,
            f"hi_{entry_id}_{HOUSE_AVG_HUMIDITY_UNIQUE_SUFFIX}",
        )
    except (AttributeError, ImportError, TypeError, ValueError):
        return None


def _source_entity_status(hass: Any) -> dict[str, Any]:
    """Describe the registered house-average humidity source used by setup guidance."""
    source_entity = _registered_house_avg_humidity_entity(hass)
    if not source_entity:
        return {
            "source_entity": None,
            "source_entity_status": "unresolved",
        }
    _value, status = numeric_entity_status(hass, source_entity)
    return {
        "source_entity": source_entity,
        "source_entity_status": status.get("status") or "unresolved",
    }


def _repair_status_for_dependency(dependency_status: str) -> dict[str, Any]:
    """Return repair/status guidance without changing drift semantics."""
    if dependency_status == "ok":
        return {
            "repair_required": False,
            "repair_kind": "none",
        }
    if dependency_status == "missing":
        return {
            "repair_required": True,
            "repair_kind": "missing_helper",
            "repair_issue_id": HOUSE_HUMIDITY_MEAN_7D_REPAIR_ISSUE,
            "repair_summary": (
                "House humidity drift needs the House Humidity Mean 7d "
                "Statistics helper."
            ),
            "repair_steps": [
                "Create a Home Assistant Statistics helper named House Humidity Mean 7d.",
                "Use the registered HI House Average Humidity entity as the source.",
                "Set state characteristic to mean.",
                "Set max age to 7 days.",
                "Rename the helper entity ID to sensor.house_humidity_mean_7d if Home Assistant creates a different entity ID.",
                "Wait for Home Assistant to collect enough samples; do not fabricate history.",
            ],
            "history_status": "not_ready_or_unavailable",
        }
    if dependency_status in {"unknown", "unavailable"}:
        return {
            "repair_required": False,
            "repair_kind": "helper_not_ready_or_unavailable",
            "repair_summary": (
                "The House Humidity Mean 7d Statistics helper exists but is not "
                "reporting a numeric 7-day mean yet."
            ),
            "history_status": "not_ready_or_unavailable",
        }
    if dependency_status == "history_not_ready":
        return {
            "repair_required": False,
            "repair_kind": "history_not_ready",
            "repair_summary": (
                "The House Humidity Mean 7d Statistics helper exists but has not "
                "collected enough recorder/statistics coverage for 7-day drift yet."
            ),
            "history_status": "not_ready_or_unavailable",
        }
    if dependency_status == "source_not_valid":
        return {
            "repair_required": False,
            "repair_kind": "helper_source_not_valid",
            "repair_summary": (
                "The House Humidity Mean 7d Statistics helper exists but Home "
                "Assistant reports its source value is not currently valid."
            ),
            "history_status": "not_ready_or_unavailable",
        }
    if dependency_status == "non_numeric":
        return {
            "repair_required": False,
            "repair_kind": "helper_misconfigured_or_non_numeric",
            "repair_summary": (
                "The House Humidity Mean 7d Statistics helper exists but its "
                "state is not numeric."
            ),
        }
    return {
        "repair_required": False,
        "repair_kind": "helper_not_ready_or_unavailable",
        "history_status": "not_ready_or_unavailable",
        }


def _statistics_readiness_status(status: dict[str, Any]) -> str:
    """Resolve Statistics helper readiness without changing drift math."""
    source_valid = status.get("source_value_valid")
    if source_valid is False:
        return "source_not_valid"

    coverage = status.get("age_coverage_ratio")
    if coverage is not None and coverage < HOUSE_HUMIDITY_MIN_AGE_COVERAGE_RATIO:
        return "history_not_ready"

    return str(status.get("status") or "unknown")


def humidity_drift_dependency_status(hass: Any) -> dict[str, Any]:
    """Describe the legacy statistics dependency required by house humidity drift."""
    mean, status = numeric_entity_status(hass, HOUSE_HUMIDITY_MEAN_7D_ENTITY)
    dependency_status = str(status.get("status") or "unknown")
    if dependency_status == "ok":
        dependency_status = _statistics_readiness_status(status)
    available = dependency_status == "ok"
    row: dict[str, Any] = {
        "required_for": HOUSE_HUMIDITY_DRIFT_7D_NAME,
        "dependency_entity": HOUSE_HUMIDITY_MEAN_7D_ENTITY,
        "dependency_status": dependency_status,
        "available": available,
        "expected_source": HOUSE_HUMIDITY_DRIFT_EXPECTED_SOURCE,
        "migration_hint": HOUSE_HUMIDITY_DRIFT_MIGRATION_HINT,
    }
    row.update(_source_entity_status(hass))
    row.update(_repair_status_for_dependency(dependency_status))
    if status.get("state") is not None:
        row["dependency_state"] = status.get("state")
    if status.get("age_coverage_ratio") is not None:
        row["age_coverage_ratio"] = status.get("age_coverage_ratio")
        row["required_age_coverage_ratio"] = HOUSE_HUMIDITY_MIN_AGE_COVERAGE_RATIO
    if status.get("source_value_valid") is not None:
        row["source_value_valid"] = status.get("source_value_valid")
    if mean is not None and available:
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
    if dependency_status.get("age_coverage_ratio") is not None:
        attrs["age_coverage_ratio"] = dependency_status.get("age_coverage_ratio")
    if dependency_status.get("required_age_coverage_ratio") is not None:
        attrs["required_age_coverage_ratio"] = dependency_status.get("required_age_coverage_ratio")
    if dependency_status.get("source_value_valid") is not None:
        attrs["source_value_valid"] = dependency_status.get("source_value_valid")
    if dependency_status.get("source_entity") is not None:
        attrs["source_entity"] = dependency_status.get("source_entity")
    if dependency_status.get("source_entity_status") is not None:
        attrs["source_entity_status"] = dependency_status.get("source_entity_status")
    attrs["repair_required"] = bool(dependency_status.get("repair_required"))
    if dependency_status.get("repair_kind") is not None:
        attrs["repair_kind"] = dependency_status.get("repair_kind")
    if dependency_status.get("repair_summary") is not None:
        attrs["repair_summary"] = dependency_status.get("repair_summary")
    if dependency_status.get("history_status") is not None:
        attrs["history_status"] = dependency_status.get("history_status")
    return attrs
