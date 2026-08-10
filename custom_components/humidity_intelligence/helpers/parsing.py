"""Parsing helpers for telemetry normalization and unit safety."""

from __future__ import annotations

import math
import re
from typing import Any, Optional, Tuple

from homeassistant.const import UnitOfTemperature

_UNKNOWN_STATE_VALUES = {"", "unknown", "unavailable", "none", "null"}
_NUMBER_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")

_TEMP_UNIT_C = {
    "c",
    "degc",
    "celsius",
    "°c",
    str(UnitOfTemperature.CELSIUS).lower(),
}
_TEMP_UNIT_F = {
    "f",
    "degf",
    "fahrenheit",
    "°f",
    str(UnitOfTemperature.FAHRENHEIT).lower(),
}


def parse_numeric(value: Any) -> Optional[float]:
    """Parse a numeric value from scalar/string telemetry."""
    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None

    text = str(value).strip()
    if text.lower() in _UNKNOWN_STATE_VALUES:
        return None

    text = text.replace(",", "")
    try:
        parsed = float(text)
    except (TypeError, ValueError):
        match = _NUMBER_RE.search(text)
        if not match:
            return None
        try:
            parsed = float(match.group(0))
        except (TypeError, ValueError):
            return None

    return parsed if math.isfinite(parsed) else None


def normalize_temperature_unit(unit: Any) -> Optional[str]:
    """Normalize temperature unit text to 'celsius' or 'fahrenheit'."""
    if unit is None:
        return None
    text = str(unit).strip().lower()
    if text in _TEMP_UNIT_C:
        return "celsius"
    if text in _TEMP_UNIT_F:
        return "fahrenheit"
    return None


def hass_temperature_unit(hass: Any) -> str:
    """Return HA configured temperature unit, defaulting to Celsius."""
    configured = (
        getattr(getattr(getattr(hass, "config", None), "units", None), "temperature_unit", None)
    )
    normalized = normalize_temperature_unit(configured)
    if normalized == "fahrenheit":
        return str(UnitOfTemperature.FAHRENHEIT)
    return str(UnitOfTemperature.CELSIUS)


def parse_temperature(
    value: Any,
    unit: Any = None,
    fallback_unit: Any = None,
) -> Tuple[Optional[float], Optional[str]]:
    """Parse incoming temperature and normalize to Celsius."""
    parsed = parse_numeric(value)
    if parsed is None:
        return None, "non_numeric"

    normalized = normalize_temperature_unit(unit) or normalize_temperature_unit(fallback_unit)
    if normalized is None:
        return None, "unit_mismatch"

    if normalized == "fahrenheit":
        return (parsed - 32.0) * (5.0 / 9.0), None
    return parsed, None


def format_temperature(value_c: Optional[float], display_unit: Any) -> Optional[float]:
    """Format Celsius value into display unit for diagnostics/UI rendering."""
    if value_c is None:
        return None
    normalized = normalize_temperature_unit(display_unit) or "celsius"
    if normalized == "fahrenheit":
        return round((value_c * 9.0 / 5.0) + 32.0, 1)
    return round(value_c, 1)
