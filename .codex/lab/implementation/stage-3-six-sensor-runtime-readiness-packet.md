# HA Lab Stage 3 Six-Sensor Runtime Readiness Packet

> **For agentic workers:** This packet records the approved Stage 3 read-only
> runtime-readiness check for the six-sensor HA Lab telemetry surface. It does not
> authorize helper mutation, availability toggles, service calls, generated dashboard
> changes, runtime code changes, staging, commit, push, or release claims.

**Status:** read-only execution rerun and passed on 2026-06-09.

**Current verdict:** `PASS`.

Reason: the approved 108 helper/wrapper entities are present and readable, and the
runtime truth surface now exposes the canonical PM25 aggregate entities after the
v2.0.7 beta PM2.5 aggregate fix.

Previous 2026-06-06 verdict: `CONFIGURATION_NOT_READY`.

Previous reason: the approved 108 helper/wrapper entities were present and readable,
but `sensor.humidity_intelligence_hi_house_pm25_average` was missing from the runtime
truth surface in the then-current HA Lab configuration.

## Approval

Senyo approved immediate Stage 3 implementation and read-only HA Lab execution in the
current Codex thread on 2026-06-06:

```yaml
final_verdict: READY_FOR_SENYO_REVIEW
implementation_allowed_now: true
ha_lab_execution_allowed_now: true
requires_future_exact_execution_approval: false
```

## Scope

Allowed by this packet:

- implement the local Stage 3 read-only tool:
  `.codex/lab/tools/ha_lab_stage_3_six_sensor_readiness.py`
- implement matching local tests:
  `.codex/lab/tests/test_ha_lab_stage_3_six_sensor_readiness.py`
- perform targeted `GET` reads only
- write a redacted local report under `.codex/lab/reports/`

Blocked by this packet:

- Home Assistant service calls
- helper mutation
- availability toggle mutation
- switch restoration
- scenario execution
- CO pressure
- dashboard/YAML mutation
- fake outputs
- output validation
- runtime code changes
- public documentation changes
- release-readiness claims

## Execution Evidence

Current Stage 3 PASS report:

```text
.codex/lab/reports/2026-06-09T18-29-19Z-stage-3-six-sensor-runtime-readiness.md
```

Previous Stage 3 configuration-not-ready report:

```text
.codex/lab/reports/2026-06-06T14-39-27Z-stage-3-six-sensor-runtime-readiness.md
```

Current report summary:

- Sensor wrappers: `36/36`
- Value helpers: `36/36`
- Availability controls: `36/36`
- Expected helper/wrapper entities: `108/108`
- `sensor.hi_diagnostics`: `ok`
- `switch.humidity_intelligence_hi_air_co_emergency_active`: `off`
- `sensor.humidity_intelligence_hi_air_control_mode`: `normal`
- `sensor.humidity_intelligence_hi_house_voc_average`: present and numeric
- `sensor.humidity_intelligence_hi_house_pm25_average`: present and numeric
- `sensor.humidity_intelligence_hi_level1_pm25_average`: present and numeric
- `sensor.humidity_intelligence_hi_level2_pm25_average`: present and numeric
- `sensor.humidity_intelligence_hi_house_pm2_5_average`: absent as expected
- Fake `fan.hi_lab_fake_*` entities: absent for exact checked IDs
- `sensor.hi_lab_aqi_01`: absent

## Runtime, UI, Migration, And Release Impact

- Production runtime impact: none.
- Entity semantics changed: no.
- Service contract changed: no.
- Generated dashboards/UI affected: no.
- Migration required: no.
- Home Assistant restart required: no.
- Home Assistant reload required: no.
- Deterministic lane-ordering risk: none from this read-only check.
- UI truth consistency risk: none from this read-only check.
- Release authority: none.

## Follow-Up Boundary

The 2026-06-06 correction was configuration/runtime-readiness work, not helper
creation. The missing `sensor.humidity_intelligence_hi_house_pm25_average` runtime
truth was recorded as a required v2.0.7 proposal:

```text
.codex/governance/proposals/drafts/2026-06-06-v207-pm25-house-aggregate-runtime-truth.md
```

The current green baseline now lives in:

```text
.codex/lab/baselines/current-first-slice-runtime-baseline.md
```

STOP: Stage 3 PASS evidence is recorded. Further HA Lab mutation, restart, reload,
dashboard mutation, helper mutation, output validation, push, tag, release, PR
creation, or stable Home Assistant access remains blocked until a new exact operation
packet is approved.
