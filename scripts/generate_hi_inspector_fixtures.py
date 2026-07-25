#!/usr/bin/env python3
"""Generate deterministic, sanitized HI Inspector contract fixtures."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import pathlib
import sys
from types import SimpleNamespace
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests 2" / "fixtures" / "hi_inspector"
SYNTHETIC_ENTRY_ID = "0123456789abcdef0123456789abcdef"
PRIVATE_SENTINELS = (
    "REDACTION_FIXTURE",
    "alice:pass",
    "user:pass",
    "person.alice",
    "sensor.kitchen",
    "sensor.hall",
    "sensor.bed",
    "fan.kitchen",
    "/Users/",
    "\\Users\\",
)


def _load_test_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load fixture source: {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _native_fixture() -> dict[str, Any]:
    tests = _load_test_module(
        "hi_inspector_native_fixture_source",
        "tests 2/test_diagnostics.py",
    )
    diagnostics = tests._load_diagnostics_module()
    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(
            tests._sample_hass(),
            tests._sample_entry(),
        )
    )

    # Keep only the exact backend-produced fields that exercise the Gate 1
    # allowlist. The fixture does not reimplement or amend backend truth.
    return {
        "integration": payload["integration"],
        "configuration": {
            "summary": payload["configuration"]["summary"],
            "enabled_feature_areas": payload["configuration"][
                "enabled_feature_areas"
            ],
        },
        "runtime": {
            "active_lane": payload["runtime"]["active_lane"],
            "current_state": payload["runtime"]["current_state"],
            "gate_states": payload["runtime"]["gate_states"],
            "mapped_runtime_entities": payload["runtime"][
                "mapped_runtime_entities"
            ],
            "output_states": payload["runtime"]["output_states"],
            "unavailable_or_unknown_entities": payload["runtime"][
                "unavailable_or_unknown_entities"
            ],
        },
        "generated_ui": payload["generated_ui"],
        "diagnostics_summary": {
            "warnings": payload["diagnostics_summary"]["warnings"],
        },
        "privacy": payload["privacy"],
    }


def _dump_fixture() -> dict[str, Any]:
    tests = _load_test_module(
        "hi_inspector_dump_fixture_source",
        "tests 2/test_runtime_card_sanity.py",
    )
    services = tests._load_services_module()
    config = {
        **tests._base_entry_data(),
        "temperature_comfort_mode": "custom",
        "temperature_comfort_custom_low": 19.0,
        "temperature_comfort_custom_high": 23.0,
    }
    entry = SimpleNamespace(
        entry_id=SYNTHETIC_ENTRY_ID,
        data=config,
        options={},
    )
    entity_map = {
        "air_control_mode": "sensor.fixture_mode",
        "air_control_reason": "sensor.fixture_reason",
        "fan_output": "fan.fixture_output",
        "optional_output": "fan.fixture_missing",
    }
    hass = tests._FakeHass(
        entry,
        {
            "sensor.fixture_mode": tests._FakeState("normal"),
            "sensor.fixture_reason": tests._FakeState("Fixture reason"),
            "fan.fixture_output": tests._FakeState("unavailable"),
        },
    )
    runtime_data = hass.data[services.DOMAIN][SYNTHETIC_ENTRY_ID]
    runtime_data.update(
        {
            "cards": {
                "v2_mobile": "type: entities\n",
                "v2_tablet": "type: entities\n",
            },
            "config": config,
            "entity_map": entity_map,
            "options": {},
        }
    )
    diagnostics = services._build_diagnostics_summary(
        hass,
        config,
        {},
        entity_map,
        runtime_data,
        frontend_dependencies={
            "status": "not_inspectable",
            "reason": "Synthetic fixture",
        },
        local_version_status={"status": "not_configured"},
    )
    payload = {
        SYNTHETIC_ENTRY_ID: {
            "configuration_summary": services._support_configuration_summary(
                config,
                {},
            ),
            "diagnostics_summary": services._support_safe_diagnostics_summary(
                diagnostics
            ),
            "entity_map_summary": services._support_entity_map_summary(entity_map),
            "cards": list(runtime_data["cards"]),
            "state_summary": services._support_state_summary(
                hass,
                entity_map.values(),
            ),
        }
    }
    return services.redact_diagnostics_payload(payload)


def generate_fixtures() -> dict[str, dict[str, Any]]:
    native = _native_fixture()
    envelope = {
        "home_assistant": {
            "version": native["integration"]["home_assistant_version"],
        },
        "custom_components": {
            "humidity_intelligence": {
                "version": native["integration"]["integration_version"],
            }
        },
        "integration_manifest": {
            "domain": "humidity_intelligence",
        },
        "issues": [],
        "setup_times": {},
        "data": native,
    }
    fixtures = {
        "dump_summary.json": _dump_fixture(),
        "native_schema1.json": native,
        "native_schema1_envelope.json": envelope,
    }
    _assert_public_safe(fixtures)
    return fixtures


def _render(value: dict[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _assert_public_safe(fixtures: dict[str, dict[str, Any]]) -> None:
    rendered = "\n".join(_render(value) for value in fixtures.values())
    for sentinel in PRIVATE_SENTINELS:
        if sentinel.lower() in rendered.lower():
            raise RuntimeError(
                f"Generated fixture contains blocked private sentinel: {sentinel}"
            )


def _check(fixtures: dict[str, dict[str, Any]]) -> int:
    failures: list[str] = []
    for filename, payload in fixtures.items():
        path = FIXTURE_ROOT / filename
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
            continue
        if path.read_text(encoding="utf-8") != _render(payload):
            failures.append(f"stale {path.relative_to(ROOT)}")
    unexpected = sorted(
        path.name
        for path in FIXTURE_ROOT.glob("*.json")
        if path.name not in fixtures
    )
    failures.extend(f"unexpected fixture {name}" for name in unexpected)
    if failures:
        print("HI Inspector fixture check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"HI Inspector fixtures current: {len(fixtures)}")
    return 0


def _write(fixtures: dict[str, dict[str, Any]]) -> None:
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    for filename, payload in fixtures.items():
        (FIXTURE_ROOT / filename).write_text(
            _render(payload),
            encoding="utf-8",
        )
    print(f"Generated HI Inspector fixtures: {len(fixtures)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="fail when tracked fixtures do not match backend-generated output",
    )
    mode.add_argument(
        "--stdout",
        choices=(
            "dump_summary.json",
            "native_schema1.json",
            "native_schema1_envelope.json",
        ),
        help="render one fixture without writing",
    )
    args = parser.parse_args()

    fixtures = generate_fixtures()
    if args.check:
        return _check(fixtures)
    if args.stdout:
        print(_render(fixtures[args.stdout]), end="")
        return 0
    _write(fixtures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
