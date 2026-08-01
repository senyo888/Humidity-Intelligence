"""Regression checks for the versioned backend reason-presentation contract."""

from __future__ import annotations

from dataclasses import replace
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "helpers" / "reason_presentation.py"


def _load_module():
    name = "hi_reason_presentation_test"
    sys.modules.pop(name, None)
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load reason presentation module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rp = _load_module()


def _facts(**overrides):
    values = {
        "family": "zone",
        "variant": "humidity_delta",
        "attention": "active",
        "headline": "Zone 1 response selected",
        "lines": (
            rp.ReasonLine(
                role="why",
                scope="ventilation",
                code="zone.humidity_delta_above_start",
                truth="observed",
                text=(
                    "Kitchen humidity is 8.2 percentage points above the home average; "
                    "the configured start point is 6.0."
                ),
                args={
                    "room_label": "Kitchen",
                    "threshold": 6.0,
                    "unit": "percentage_points",
                    "value": 8.2,
                },
            ),
            rp.ReasonLine(
                role="action",
                scope="ventilation",
                code="output.level_selected",
                truth="selected",
                text="Output selection: 100% for Kitchen Extractor.",
                args={"level": 100, "output_label": "Kitchen Extractor"},
            ),
        ),
    }
    values.update(overrides)
    return rp.ReasonFacts(**values)


class ReasonPresentationTests(unittest.TestCase):
    def test_valid_contract_is_deterministic_and_newly_constructed(self) -> None:
        first = rp.build_display_reason(_facts())
        second = rp.validate_display_reason(first)

        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertEqual("hi.reason.v1", first["schema"])
        self.assertEqual(["level", "output_label"], list(first["lines"][1]["args"]))
        self.assertEqual(
            json.dumps(first, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
            json.dumps(second, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        )

    def test_exact_schema_is_required(self) -> None:
        contract = rp.build_display_reason(_facts())
        contract["schema"] = 1
        with self.assertRaises(rp.ReasonPresentationError):
            rp.validate_display_reason(contract)

    def test_unknown_top_level_and_line_fields_are_rejected(self) -> None:
        contract = rp.build_display_reason(_facts())
        contract["debug"] = True
        with self.assertRaises(rp.ReasonPresentationError):
            rp.validate_display_reason(contract)

        contract = rp.build_display_reason(_facts())
        contract["lines"][0]["entity_id"] = "sensor.private"
        with self.assertRaises(rp.ReasonPresentationError):
            rp.validate_display_reason(contract)

    def test_all_enums_are_allowlisted(self) -> None:
        for key, value in (
            ("attention", "urgent"),
            ("family", "Zone 1"),
            ("variant", "bad.variant"),
        ):
            contract = rp.build_display_reason(_facts())
            contract[key] = value
            with self.subTest(key=key), self.assertRaises(rp.ReasonPresentationError):
                rp.validate_display_reason(contract)

        for key, value in (
            ("role", "summary"),
            ("scope", "device"),
            ("truth", "running"),
            ("code", "No spaces allowed"),
        ):
            contract = rp.build_display_reason(_facts())
            contract["lines"][0][key] = value
            with self.subTest(key=key), self.assertRaises(rp.ReasonPresentationError):
                rp.validate_display_reason(contract)

    def test_line_limit_is_hard_eight(self) -> None:
        line = _facts().lines[0]
        self.assertEqual(8, len(rp.build_display_reason(_facts(lines=(line,) * 8))["lines"]))
        with self.assertRaises(rp.ReasonPresentationError):
            rp.build_display_reason(_facts(lines=(line,) * 9))

    def test_headline_line_and_total_size_limits_are_enforced(self) -> None:
        with self.assertRaises(rp.ReasonPresentationError):
            rp.build_display_reason(_facts(headline="H" * 121))
        long_line = replace(_facts().lines[0], text="L" * 201)
        with self.assertRaises(rp.ReasonPresentationError):
            rp.build_display_reason(_facts(lines=(long_line,)))

        large_lines = tuple(
            replace(
                _facts().lines[0],
                code=f"zone.large_line_{index}",
                text=(f"Line {index} " + "é" * 190),
                args={f"label_{slot}": "é" * 64 for slot in range(6)},
            )
            for index in range(8)
        )
        with self.assertRaisesRegex(rp.ReasonPresentationError, "4 KiB"):
            rp.build_display_reason(_facts(lines=large_lines))

    def test_args_are_bounded_flat_finite_scalars(self) -> None:
        line = _facts().lines[0]
        invalid_args = (
            {f"value_{idx}": idx for idx in range(7)},
            {"nested": {"value": 1}},
            {"items": [1, 2]},
            {"value": math.inf},
            {"label": "x" * 65},
        )
        for args in invalid_args:
            with self.subTest(args=args), self.assertRaises(rp.ReasonPresentationError):
                rp.build_display_reason(_facts(lines=(replace(line, args=args),)))

    def test_raw_entity_ids_are_rejected_in_text_and_args(self) -> None:
        line = _facts().lines[0]
        with self.assertRaisesRegex(rp.ReasonPresentationError, "entity ID"):
            rp.build_display_reason(
                _facts(lines=(replace(line, text="Output sensor.private_room is unavailable."),))
            )
        with self.assertRaisesRegex(rp.ReasonPresentationError, "entity ID"):
            rp.build_display_reason(
                _facts(lines=(replace(line, args={"label": "fan.private_extract"}),))
            )
        with self.assertRaisesRegex(rp.ReasonPresentationError, "entity ID"):
            rp.build_display_reason(
                _facts(
                    lines=(
                        replace(
                            line,
                            args={"label": "device_tracker.private_phone"},
                        ),
                    )
                )
            )
        with self.assertRaisesRegex(rp.ReasonPresentationError, "entity ID"):
            rp.build_display_reason(
                _facts(lines=(replace(line, text="Output custom_domain.private is selected."),))
            )

    def test_pm25_measurement_token_is_not_mistaken_for_an_entity_id(self) -> None:
        line = replace(
            _facts().lines[0],
            code="air_quality.pm25_high",
            text="PM2.5 is 48 µg/m³, at or above the 25 µg/m³ threshold.",
            args={"measured": 48, "threshold": 25, "unit": "ug_m3"},
        )
        contract = rp.build_display_reason(
            _facts(family="air_quality", variant="trigger_active", lines=(line,))
        )

        self.assertEqual(
            "PM2.5 is 48 µg/m³, at or above the 25 µg/m³ threshold.",
            contract["lines"][0]["text"],
        )

        for text in ("Schema v2.0 is supported.", "Ground.Floor response selected."):
            with self.subTest(text=text):
                benign = replace(line, text=text)
                rp.build_display_reason(
                    _facts(
                        family="air_quality",
                        variant="trigger_active",
                        lines=(benign,),
                    )
                )

    def test_fact_snapshot_copies_mutable_inputs(self) -> None:
        args = {"value": 8.2}
        lines = [replace(_facts().lines[0], args=args)]
        facts = _facts(lines=lines)
        args["value"] = 99
        lines.clear()

        contract = rp.build_display_reason(facts)
        self.assertEqual(8.2, contract["lines"][0]["args"]["value"])

    def test_plain_text_rejects_markup_controls_and_non_normalized_space(self) -> None:
        line = _facts().lines[0]
        for text in ("<b>Selected</b>", "Line\nBreak", "Double  space", "Bidi\u202eoverride"):
            with self.subTest(text=text), self.assertRaises(rp.ReasonPresentationError):
                rp.build_display_reason(_facts(lines=(replace(line, text=text),)))

    def test_label_sanitizer_removes_markup_bidi_and_raw_ids(self) -> None:
        self.assertEqual("Kitchen Alert", rp.sanitize_display_label("  <Kitchen>\n\u202eAlert  "))
        self.assertEqual("", rp.sanitize_display_label("sensor.private_kitchen"))
        self.assertEqual("", rp.sanitize_display_label("Kitchen sensor.private_kitchen"))
        self.assertEqual(64, len(rp.sanitize_display_label("x" * 100)))

    def test_diagnostics_metadata_never_contains_text_or_args(self) -> None:
        contract = rp.build_display_reason(_facts())
        metadata = rp.display_reason_metadata(contract)

        self.assertEqual(
            {
                "status": "valid",
                "schema": "hi.reason.v1",
                "family": "zone",
                "variant": "humidity_delta",
                "attention": "active",
                "truncated": False,
                "line_count": 2,
            },
            metadata,
        )
        self.assertNotIn("headline", metadata)
        self.assertNotIn("lines", metadata)

    def test_invalid_and_missing_diagnostics_metadata_are_redacted(self) -> None:
        missing = rp.display_reason_metadata(None)
        invalid = rp.display_reason_metadata({"schema": "future"})

        self.assertEqual("missing", missing["status"])
        self.assertEqual("invalid", invalid["status"])
        self.assertIsNone(invalid["schema"])


if __name__ == "__main__":
    unittest.main()
