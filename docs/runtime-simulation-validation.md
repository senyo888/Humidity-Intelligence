# Runtime Simulation Validation

This maintainer validation harness proves backend-owned Air Control Mode truth with
deterministic fake telemetry. It is production validation infrastructure, not a
v2.1 display fixture, not HA Lab evidence, and not a Home Assistant runtime
service.

## Scope

The harness in `tests 2/hi_runtime_fixtures.py` creates a fresh fake Home
Assistant runtime for each scenario, feeds configured telemetry entities into
`HIAutomationEngine`, refreshes the computed core sensors, and reads the
`HI Air Control Mode` and `HI Air Control Reason` sensors.

It covers:

- baseline normal telemetry
- all configured humidity unavailable or unknown
- all configured temperature unavailable or unknown
- distinct Kitchen, Hallway, and Bedroom room values for zone delta pressure
- Level 1 IAQ pressure independent of zone pressure
- disabled/manual/global gates
- CO ppm defaulting clear at `0`
- opt-in CO emergency pressure
- per-run reset back to baseline telemetry

## Run

Use the direct harness when local pytest collection is blocked by missing Home
Assistant test dependencies:

```bash
python3 "tests 2/test_air_control_mode_simulation.py"
```

Expected local pass output:

```text
10 air-control mode simulation checks passed.
```

Where full test dependencies are available, this file can also be run through
pytest:

```bash
python3 -m pytest -q "tests 2/test_air_control_mode_simulation.py"
```

## Safety Boundaries

- Fake telemetry is test-only Python data.
- The harness does not create helpers, services, automations, dashboards, or
  persistent Home Assistant entities.
- Fan and humidifier output isolation defaults on, so fake scenarios do not
  write fake fan outputs by default.
- CO pressure cannot be triggered accidentally. A CO value at or above the
  emergency threshold requires `co_pressure=True` in the scenario.
- Each run constructs a fresh fake runtime, so scenario state does not leak into
  the next case.

## Release Interpretation

Passing this harness proves the backend engine can consume simulated telemetry
and that the exposed Air Control Mode/Reason sensors reflect the selected
runtime mode for the covered scenarios.

It does not replace:

- full Home Assistant install/update validation
- startup log review
- HACS packaging/preflight checks
- generated dashboard export and visual checks
- physical device/output validation
