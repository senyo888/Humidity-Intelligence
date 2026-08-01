"""Bounded backend-owned Current Air Control reason presentation contract."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
import re
from types import MappingProxyType
import unicodedata
from typing import Any, Mapping, Optional, Tuple, Union


DISPLAY_REASON_SCHEMA = "hi.reason.v1"
DISPLAY_REASON_LOCALE = "en"
DISPLAY_REASON_MAX_BYTES = 4096
DISPLAY_REASON_MAX_HEADLINE = 120
DISPLAY_REASON_MAX_LINE_TEXT = 200
DISPLAY_REASON_MAX_LINES = 8
DISPLAY_REASON_TARGET_LINES = 6
DISPLAY_REASON_MAX_ARGS = 6
DISPLAY_REASON_MAX_ARG_TEXT = 64
DISPLAY_REASON_MAX_TOKEN = 64
DISPLAY_REASON_MAX_CODE = 96

DISPLAY_REASON_ATTENTION = frozenset(
    {"neutral", "active", "hold", "degraded", "critical", "unknown"}
)
DISPLAY_REASON_ROLES = frozenset({"why", "action", "next", "notice"})
DISPLAY_REASON_SCOPES = frozenset(
    {"system", "safety", "ventilation", "humidifier"}
)
DISPLAY_REASON_TRUTH = frozenset(
    {
        "selected",
        "blocked",
        "requested",
        "observed",
        "unavailable",
        "unmapped",
        "not_confirmed",
        "failed",
    }
)

_TOKEN_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_CODE_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_ENTITY_ID_RE = re.compile(
    r"(?<![a-z0-9_])(?:[a-z_][a-z0-9_]*)\.[a-z0-9_]+(?![a-z0-9_])"
)
_BENIGN_DOTTED_TOKEN_RE = re.compile(
    r"\b(?:PM2\.5|v\d+(?:\.\d+){1,2})\b",
    re.IGNORECASE,
)
_MARKUP_TRANSLATION = str.maketrans({"<": "", ">": "", "`": ""})

JsonScalar = Union[str, int, float, bool, None]


class ReasonPresentationError(ValueError):
    """Raised when a reason presentation violates the public contract."""


@dataclass(frozen=True)
class ReasonLine:
    """One ordered backend-authored presentation line."""

    role: str
    scope: str
    code: str
    truth: str
    text: str
    args: Mapping[str, JsonScalar] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "args", MappingProxyType(dict(self.args)))


@dataclass(frozen=True)
class ReasonFacts:
    """Immutable final presentation facts supplied after runtime decisions complete."""

    family: str
    variant: str
    attention: str
    headline: str
    lines: Tuple[ReasonLine, ...]
    truncated: bool = False
    locale: str = DISPLAY_REASON_LOCALE

    def __post_init__(self) -> None:
        object.__setattr__(self, "lines", tuple(self.lines))


def sanitize_display_label(value: Any, *, maximum: int = DISPLAY_REASON_MAX_ARG_TEXT) -> str:
    """Return one bounded plain-text local label or an empty unusable result."""

    if value is None:
        return ""
    raw = unicodedata.normalize("NFC", str(value))
    chars = []
    for char in raw:
        if char.isspace():
            chars.append(" ")
            continue
        if unicodedata.category(char).startswith("C"):
            continue
        chars.append(char)
    text = " ".join("".join(chars).translate(_MARKUP_TRANSLATION).split())
    if not text or _contains_raw_entity_id(text):
        return ""
    return text[:maximum].rstrip()


def build_display_reason(facts: ReasonFacts) -> dict[str, Any]:
    """Build and validate one deterministic ``hi.reason.v1`` object."""

    if not isinstance(facts, ReasonFacts):
        raise ReasonPresentationError("display reason facts must use ReasonFacts")
    candidate = {
        "schema": DISPLAY_REASON_SCHEMA,
        "locale": facts.locale,
        "family": facts.family,
        "variant": facts.variant,
        "attention": facts.attention,
        "truncated": facts.truncated,
        "headline": facts.headline,
        "lines": [
            {
                "role": line.role,
                "scope": line.scope,
                "code": line.code,
                "truth": line.truth,
                "text": line.text,
                **({"args": dict(line.args)} if line.args else {}),
            }
            for line in facts.lines
        ],
    }
    return validate_display_reason(candidate)


def validate_display_reason(value: Any) -> dict[str, Any]:
    """Return a newly constructed known-key contract or raise."""

    if not isinstance(value, Mapping):
        raise ReasonPresentationError("display reason must be a mapping")

    required = {
        "schema",
        "locale",
        "family",
        "variant",
        "attention",
        "truncated",
        "headline",
        "lines",
    }
    if set(value) != required:
        raise ReasonPresentationError("display reason has missing or unknown fields")
    if value.get("schema") != DISPLAY_REASON_SCHEMA:
        raise ReasonPresentationError("unsupported display reason schema")
    if value.get("locale") != DISPLAY_REASON_LOCALE:
        raise ReasonPresentationError("unsupported display reason locale")

    family = _validated_token(value.get("family"), "family")
    variant = _validated_token(value.get("variant"), "variant")
    attention = _validated_enum(
        value.get("attention"), DISPLAY_REASON_ATTENTION, "attention"
    )
    if not isinstance(value.get("truncated"), bool):
        raise ReasonPresentationError("truncated must be a boolean")
    headline = _validated_text(
        value.get("headline"), DISPLAY_REASON_MAX_HEADLINE, "headline"
    )

    raw_lines = value.get("lines")
    if not isinstance(raw_lines, list) or not raw_lines:
        raise ReasonPresentationError("display reason lines must be a non-empty list")
    if len(raw_lines) > DISPLAY_REASON_MAX_LINES:
        raise ReasonPresentationError("display reason exceeds the eight-line limit")

    lines = [_validated_line(line) for line in raw_lines]
    validated = {
        "schema": DISPLAY_REASON_SCHEMA,
        "locale": DISPLAY_REASON_LOCALE,
        "family": family,
        "variant": variant,
        "attention": attention,
        "truncated": bool(value["truncated"]),
        "headline": headline,
        "lines": lines,
    }
    serialized = json.dumps(
        validated,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(serialized) > DISPLAY_REASON_MAX_BYTES:
        raise ReasonPresentationError("display reason exceeds the 4 KiB limit")
    return validated


def display_reason_metadata(value: Any) -> dict[str, Any]:
    """Return privacy-safe diagnostics metadata for one presentation contract."""

    if value is None:
        return {
            "status": "missing",
            "schema": None,
            "family": None,
            "variant": None,
            "attention": None,
            "truncated": False,
            "line_count": 0,
        }
    try:
        validated = validate_display_reason(value)
    except ReasonPresentationError:
        return {
            "status": "invalid",
            "schema": None,
            "family": None,
            "variant": None,
            "attention": None,
            "truncated": False,
            "line_count": 0,
        }
    return {
        "status": "valid",
        "schema": DISPLAY_REASON_SCHEMA,
        "family": validated["family"],
        "variant": validated["variant"],
        "attention": validated["attention"],
        "truncated": validated["truncated"],
        "line_count": len(validated["lines"]),
    }


def _validated_line(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ReasonPresentationError("display reason line must be a mapping")
    required = {"role", "scope", "code", "truth", "text"}
    allowed = required | {"args"}
    if not required.issubset(value) or not set(value).issubset(allowed):
        raise ReasonPresentationError("display reason line has missing or unknown fields")

    role = _validated_enum(value.get("role"), DISPLAY_REASON_ROLES, "line role")
    scope = _validated_enum(value.get("scope"), DISPLAY_REASON_SCOPES, "line scope")
    truth = _validated_enum(value.get("truth"), DISPLAY_REASON_TRUTH, "line truth")
    code = value.get("code")
    if not isinstance(code, str) or len(code) > DISPLAY_REASON_MAX_CODE or not _CODE_RE.fullmatch(code):
        raise ReasonPresentationError("line code is invalid")
    text = _validated_text(value.get("text"), DISPLAY_REASON_MAX_LINE_TEXT, "line text")
    validated = {
        "role": role,
        "scope": scope,
        "code": code,
        "truth": truth,
        "text": text,
    }
    if "args" in value:
        validated["args"] = _validated_args(value.get("args"))
    return validated


def _validated_args(value: Any) -> dict[str, JsonScalar]:
    if not isinstance(value, Mapping):
        raise ReasonPresentationError("line args must be a mapping")
    if len(value) > DISPLAY_REASON_MAX_ARGS:
        raise ReasonPresentationError("line args exceed the six-value limit")
    if any(not isinstance(key, str) for key in value):
        raise ReasonPresentationError("line arg key is invalid")
    validated: dict[str, JsonScalar] = {}
    for key in sorted(value):
        if not isinstance(key, str) or not _TOKEN_RE.fullmatch(key):
            raise ReasonPresentationError("line arg key is invalid")
        item = value[key]
        if item is None or isinstance(item, bool) or isinstance(item, int):
            validated[key] = item
        elif isinstance(item, float):
            if not math.isfinite(item):
                raise ReasonPresentationError("line arg float must be finite")
            validated[key] = item
        elif isinstance(item, str):
            text = _validated_text(item, DISPLAY_REASON_MAX_ARG_TEXT, "line arg")
            validated[key] = text
        else:
            raise ReasonPresentationError("line args must contain JSON scalars")
    return validated


def _validated_token(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) > DISPLAY_REASON_MAX_TOKEN or not _TOKEN_RE.fullmatch(value):
        raise ReasonPresentationError(f"{label} is invalid")
    return value


def _validated_enum(value: Any, allowed: frozenset[str], label: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ReasonPresentationError(f"{label} is invalid")
    return value


def _validated_text(value: Any, maximum: int, label: str) -> str:
    if not isinstance(value, str):
        raise ReasonPresentationError(f"{label} must be text")
    if not value or value != " ".join(value.split()):
        raise ReasonPresentationError(f"{label} must be normalized non-empty text")
    if len(value) > maximum:
        raise ReasonPresentationError(f"{label} exceeds its length limit")
    if any(unicodedata.category(char).startswith("C") for char in value):
        raise ReasonPresentationError(f"{label} contains control characters")
    if "<" in value or ">" in value or "`" in value:
        raise ReasonPresentationError(f"{label} contains markup delimiters")
    if _contains_raw_entity_id(value):
        raise ReasonPresentationError(f"{label} contains a raw entity ID")
    return value


def _contains_raw_entity_id(value: str) -> bool:
    scan_value = _BENIGN_DOTTED_TOKEN_RE.sub("", value)
    return bool(_ENTITY_ID_RE.search(scan_value))
