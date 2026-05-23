"""Repair issue support for Humidity Intelligence drift dependencies."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers import issue_registry as ir

from ..const import DOMAIN
from .drift import (
    HOUSE_HUMIDITY_MEAN_7D_ENTITY,
    HOUSE_HUMIDITY_MEAN_7D_REPAIR_ISSUE,
    humidity_drift_dependency_status,
)


async def async_update_humidity_drift_repair_issue(hass: Any) -> None:
    """Create or clear the missing Statistics helper repair issue."""
    status = humidity_drift_dependency_status(hass)
    if status.get("repair_kind") == "missing_helper":
        ir.async_create_issue(
            hass,
            DOMAIN,
            HOUSE_HUMIDITY_MEAN_7D_REPAIR_ISSUE,
            is_fixable=False,
            is_persistent=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=HOUSE_HUMIDITY_MEAN_7D_REPAIR_ISSUE,
            translation_placeholders={
                "dependency_entity": status.get(
                    "dependency_entity",
                    HOUSE_HUMIDITY_MEAN_7D_ENTITY,
                ),
                "source_entity": status.get("source_entity")
                or "the registered HI House Average Humidity entity",
            },
        )
        return

    ir.async_delete_issue(hass, DOMAIN, HOUSE_HUMIDITY_MEAN_7D_REPAIR_ISSUE)
