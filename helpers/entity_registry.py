"""Entity registry helper functions for Humidity Intelligence."""

from __future__ import annotations

import logging
from typing import Callable, Optional, Tuple

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import async_generate_entity_id

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PM25_AGGREGATE_UNIQUE_SUFFIXES = (
    "house_pm25_average",
    "level1_pm25_average",
    "level2_pm25_average",
)


def normalize_pm25_aggregate_entity_ids(hass: HomeAssistant, entry_id: str) -> dict[str, str]:
    """Normalize legacy PM2.5 aggregate entity IDs to canonical PM25 slugs."""
    registry = er.async_get(hass)
    changed: dict[str, str] = {}

    for suffix in PM25_AGGREGATE_UNIQUE_SUFFIXES:
        unique_id = f"hi_{entry_id}_{suffix}"
        entity_id = registry.async_get_entity_id("sensor", DOMAIN, unique_id)
        if not entity_id or "pm2_5" not in entity_id:
            continue

        target_entity_id = entity_id.replace("pm2_5", "pm25")
        if registry.async_get(target_entity_id):
            _LOGGER.warning(
                "Skipping PM2.5 aggregate entity ID normalization for %s because %s already exists",
                entity_id,
                target_entity_id,
            )
            continue

        try:
            registry.async_update_entity(entity_id, new_entity_id=target_entity_id)
        except Exception:
            _LOGGER.exception(
                "Failed to normalize PM2.5 aggregate entity ID %s to %s",
                entity_id,
                target_entity_id,
            )
            continue

        changed[entity_id] = target_entity_id

    return changed


async def adopt_or_create_entity_id(
    hass: HomeAssistant,
    domain: str,
    suggested_object_id: str,
    unique_id: str,
    compatible: Optional[Callable[[er.RegistryEntry], bool]] = None,
) -> Tuple[str, Optional[er.RegistryEntry], bool]:
    """Adopt existing entity or create a new unique entity_id.

    Returns (entity_id, registry_entry, adopted).
    """
    registry = er.async_get(hass)

    # Prefer existing entry with matching unique_id
    existing_id = registry.async_get_entity_id(domain, DOMAIN, unique_id)
    if existing_id:
        entry = registry.async_get(existing_id)
        return existing_id, entry, True

    candidate_id = f"{domain}.{suggested_object_id}"
    existing_entry = registry.async_get(candidate_id)
    if existing_entry and (compatible(existing_entry) if compatible else True):
        _LOGGER.debug("Adopting existing entity %s", candidate_id)
        return existing_entry.entity_id, existing_entry, True

    # Generate a unique entity ID and register
    entity_id = async_generate_entity_id(f"{domain}.{{}}", suggested_object_id, hass=hass)
    entry = registry.async_get_or_create(
        domain=domain,
        platform=DOMAIN,
        suggested_object_id=entity_id.split(".", 1)[1],
        unique_id=unique_id,
    )
    return entry.entity_id, entry, False
