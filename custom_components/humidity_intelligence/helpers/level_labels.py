"""Display-only level label resolution for UI and diagnostics surfaces."""

from __future__ import annotations

import re
from typing import Any, Mapping

from ..const import (
    CONF_LEVEL1_LABEL,
    CONF_LEVEL2_LABEL,
    CONF_LEVEL_LABELS,
    LEVEL_LABEL_FALLBACKS,
    LEVEL_LABEL_MAX_LENGTH,
)


def level_label_config_from_form(
    fields: Mapping[str, Any] | None,
    existing: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Build stored labels while preserving existing values for absent fields."""
    values = fields if isinstance(fields, Mapping) else {}
    labels = level_label_field_values(existing)
    if CONF_LEVEL1_LABEL in values:
        labels["level1"] = clean_level_label(values.get(CONF_LEVEL1_LABEL))
    if CONF_LEVEL2_LABEL in values:
        labels["level2"] = clean_level_label(values.get(CONF_LEVEL2_LABEL))
    return labels


def resolve_level_label_details(
    config: Mapping[str, Any] | None,
    options: Mapping[str, Any] | None = None,
) -> dict[str, dict[str, str]]:
    """Resolve display labels with deterministic fallback provenance."""
    effective: dict[str, Any] = {}
    if isinstance(config, Mapping):
        effective.update(config)
    if isinstance(options, Mapping):
        effective.update(options)

    configured = effective.get(CONF_LEVEL_LABELS)
    configured_labels = configured if isinstance(configured, Mapping) else {}

    details: dict[str, dict[str, str]] = {}
    for level, fallback in LEVEL_LABEL_FALLBACKS.items():
        label = clean_level_label(configured_labels.get(level))
        if label:
            details[level] = {"label": label, "source": "config"}
        else:
            details[level] = {"label": fallback, "source": "fallback"}
    return details


def level_label_field_values(
    config: Mapping[str, Any] | None,
    options: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Return sanitized configured labels only, leaving fallback labels implicit."""
    effective: dict[str, Any] = {}
    if isinstance(config, Mapping):
        effective.update(config)
    if isinstance(options, Mapping):
        effective.update(options)

    configured = effective.get(CONF_LEVEL_LABELS)
    configured_labels = configured if isinstance(configured, Mapping) else {}
    return {
        level: clean_level_label(configured_labels.get(level))
        for level in LEVEL_LABEL_FALLBACKS
    }


def resolve_level_labels(
    config: Mapping[str, Any] | None,
    options: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Return the compact level-to-label map generated cards consume."""
    return {
        level: detail["label"]
        for level, detail in resolve_level_label_details(config, options).items()
    }


def level_label(
    level: Any,
    config: Mapping[str, Any] | None,
    options: Mapping[str, Any] | None = None,
) -> str:
    """Return one display label, falling back to the raw level for unknown values."""
    labels = resolve_level_labels(config, options)
    key = str(level or "").strip()
    return labels.get(key) or key or "Unassigned level"


def clean_level_label(value: Any) -> str:
    """Sanitize a level display label without assigning semantic meaning."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = re.sub(r"[\r\n\t'\"\\`<>{}\[\]:#]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:LEVEL_LABEL_MAX_LENGTH]
