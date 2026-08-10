"""Zone mapping validation helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Set

_TRACKED_SENSOR_TYPES = {"humidity", "temperature", "iaq", "pm25", "voc", "co2", "co"}


def detect_zone_mapping_duplicates(
    telemetry: List[Dict[str, Any]],
    zones: Dict[str, Dict[str, Any]],
) -> Dict[str, List[str]]:
    """Find overlapping telemetry entity mappings across enabled zones."""
    zone_sources: Dict[str, Set[str]] = {}
    for zone_key in ("zone1", "zone2"):
        zone_cfg = zones.get(zone_key)
        if not isinstance(zone_cfg, dict):
            continue
        if not zone_cfg.get("enabled"):
            continue
        zone_sources[zone_key] = _zone_sensor_sources(telemetry, zone_cfg)

    duplicates: Dict[str, List[str]] = {}
    keys = sorted(zone_sources.keys())
    for idx, left in enumerate(keys):
        for right in keys[idx + 1 :]:
            overlap = sorted(zone_sources[left].intersection(zone_sources[right]))
            if overlap:
                duplicates[f"{left}:{right}"] = overlap
    return duplicates


def summarize_zone_mapping_duplicates(duplicates: Dict[str, List[str]]) -> str:
    """Create a concise warning string for duplicate zone mappings."""
    if not duplicates:
        return ""
    sections: List[str] = []
    for pair_key, entities in sorted(duplicates.items()):
        left, right = pair_key.split(":", 1)
        section = f"{left}/{right}: {', '.join(entities)}"
        sections.append(section)
    return "; ".join(sections)


def summarize_zone_mapping_duplicate_counts(duplicates: Dict[str, List[str]]) -> Dict[str, Any]:
    """Summarize duplicate zone mappings without exposing entity IDs."""
    return {
        "count": len(duplicates or {}),
        "pairs": {
            str(pair_key): {"entity_count": len(entities or [])}
            for pair_key, entities in sorted((duplicates or {}).items())
        },
    }


def summarize_zone_mapping_duplicate_count_warning(duplicates: Dict[str, List[str]]) -> str:
    """Create a privacy-safe warning string for duplicate zone mappings."""
    if not duplicates:
        return ""
    pair_count = len(duplicates)
    source_count = sum(len(entities or []) for entities in duplicates.values())
    pair_word = "pair" if pair_count == 1 else "pairs"
    source_word = "source" if source_count == 1 else "sources"
    return (
        f"{pair_count} duplicate zone mapping {pair_word} includes "
        f"{source_count} overlapping telemetry {source_word}."
    )


def _zone_sensor_sources(telemetry: List[Dict[str, Any]], zone: Dict[str, Any]) -> Set[str]:
    level = str(zone.get("level") or "").strip()
    rooms = {
        str(room).strip().lower()
        for room in (zone.get("rooms") or [])
        if str(room).strip()
    }
    sources: Set[str] = set()
    for item in telemetry:
        sensor_type = str(item.get("sensor_type") or "").strip().lower()
        if sensor_type not in _TRACKED_SENSOR_TYPES:
            continue

        entity_id = str(item.get("entity_id") or "").strip()
        if not entity_id:
            continue

        if level and str(item.get("level") or "").strip() != level:
            continue

        room = str(item.get("room") or "").strip().lower()
        if rooms and room not in rooms:
            continue

        sources.add(entity_id)
    return sources
