# V2.0.6 Runtime Telemetry And CO Clear Fixes

```yaml
proposal_id: HI-PROP-20260531-001
proposal_urn: urn:hi:proposal:20260531:001:v206-runtime-telemetry-co-clear
title: V2.0.6 Runtime Telemetry And CO Clear Fixes
created: 2026-05-31
category: runtime
target_version: v2.0.6
authority_status: implemented
state: TESTED
owner: Bella
risk_level: high
runtime_impact: runtime-control
affected_surfaces:
  - proposal-governance
  - runtime-control
  - entities
  - release-docs
  - public-docs
  - ha-lab-evidence
rollback_defined: true
expiry_or_review_date: 2026-06-14
bella_approved: true
aetherwing_validated: true
ha_lab_validated: true
release_candidate_validated: false
entity_contract_changed: true
service_contract_changed: false
lane_order_risk: false
stable_runtime_risk: false
```

## Objective

Document and constrain the v2.0.6 runtime fixes discovered during HA Lab Phase 3F
mutation validation:

- CO emergency clear must schedule a recheck at the two-minute clear-hold deadline.
- Required humidity telemetry, and configured temperature telemetry, must degrade to
  explicit `telemetry_unavailable` instead of falling through lower-priority lanes.
- The canonical air-control-mode sensor must be proven through backend-consumed
  deterministic fake telemetry rather than frontend-only display fixtures.

## Bella Review Verdict

Approved for narrow v2.0.6 implementation after correction.

Bella findings corrected before commit:

- The old work-folder test diff contained unrelated temperature-comfort removals.
  Canonical sync must include only the three focused runtime regressions.
- The procedure text used local absolute checkout paths. Canonical wording must stay
  portable and public-safe.
- The canonical docs were missing the runtime contract and release-note truth for the
  new `telemetry_unavailable` entity semantics.

## Authority Boundary

Allowed by this packet:

- Patch `automations/engine.py` for CO clear recheck scheduling and required-telemetry
  stand-down.
- Patch `sensors/core.py` only as needed to keep `HI Air Control Mode` display truth
  aligned with active CO emergency runtime truth.
- Add backend simulation coverage for `sensor.humidity_intelligence_hi_air_control_mode`
  and `sensor.humidity_intelligence_hi_air_control_reason`.
- Add targeted regression coverage in `tests 2/test_runtime_card_sanity.py`.
- Update `CHANGELOG.md`, `DESIGN_BRIEF.md`, and `README.md` with narrow release-truth
  notes.
- Deploy to HA Lab only with timestamped backup, SHA verification, restart, and
  rollback path.
- Run read-only baseline checks, isolated missing-telemetry probes, and approved safe
  mutation scenarios.

Blocked by this packet:

- No wholesale sync from the older work folder.
- No unrelated temperature-comfort, card-template, dashboard export, or generated UI
  changes.
- No new helper or switch entity creation unless a specific HA Lab sensor dependency is
  missing and separately recorded in a mutation report.
- No publication, tag, or release promotion without canonical validation and maintainer
  release approval.
- No CO pressure run by default. CO pressure remains opt-in because prior pressure
  reproduced HA Lab host or transport instability.
- No fake output writes by default from the canonical simulation fixture.

## Implementation Procedure

1. Start from the canonical checkout on the intended `senyo888-patch-1` release branch.
2. Confirm the worktree is clean or that unrelated local changes are explicitly
   identified.
3. Add the focused failing regressions first:
   - CO emergency schedules a clear recheck when CO falls below the clear threshold
     before the two-minute hold has elapsed.
   - Missing required humidity telemetry publishes `telemetry_unavailable` and skips
     alert, humidifier, zone, and AQ handlers.
   - Missing configured temperature telemetry publishes `telemetry_unavailable` and
     skips alert, humidifier, zone, and AQ handlers.
4. Patch `automations/engine.py`:
   - Add a named two-minute CO clear hold constant.
   - Track and cancel a CO clear recheck task.
   - Schedule the recheck for the remaining hold duration instead of waiting for the
     normal engine interval.
   - Add the required-telemetry guard after CO, control lock, global gate, and pause
     checks, and before alert, humidifier, zone, and AQ lanes.
5. Update release-truth docs:
   - `CHANGELOG.md` Unreleased entries.
   - `DESIGN_BRIEF.md` runtime contract.
   - `README.md` release-note bullets.
6. Add deterministic runtime simulation coverage:
   - Kitchen humidity/temperature on level1 zone1.
   - Hallway humidity/temperature as a level1 neutral house peer.
   - Bedroom humidity/temperature on level2 zone2.
   - Level1 IAQ.
   - CO ppm defaulting to 0, with elevated CO rejected unless
     `co_pressure=True`.
7. Validate with direct sanity checks, compile checks, and diff hygiene.
8. Commit only the narrow runtime, test, and release-truth scope.

## Runtime Impact

- CO emergency remains the highest-priority runtime lane.
- Disabled, manual override, pause, and global gate behavior remain authoritative.
- If control is otherwise enabled and required telemetry is unavailable, HI returns
  outputs to the normal safe state and publishes `telemetry_unavailable`.
- Temperature telemetry is required only when temperature telemetry is configured.
- The core mode sensor preserves active `co_emergency` display truth when CO emergency
  runtime truth is active.
- Service contracts do not change.

## UI Impact

Generated dashboards are display surfaces only. Cards that display the backend runtime
mode will show `telemetry_unavailable`; no card template change is required by this
packet.

## Migration And Restart Impact

No migration is required. Home Assistant restart or integration reload is required
after deploying the changed runtime source.

## Rollback

Canonical rollback:

```bash
git revert <runtime-fix-commit>
python3 'tests 2/test_runtime_card_sanity.py'
python3 -m py_compile automations/engine.py
git diff --check
```

HA Lab rollback:

- Restore the timestamped remote `engine.py` backup captured before deployment.
- Verify SHA against the backup.
- Restart HA Core.
- Run the read-only baseline report.
- Restore any approved helper or switch mutations recorded in the mutation report.

## Required Validation

Before release promotion, run:

```bash
python3 'tests 2/test_runtime_card_sanity.py'
python3 'tests 2/test_air_control_mode_simulation.py'
python3 -m py_compile automations/engine.py
python3 -m py_compile sensors/core.py 'tests 2/hi_runtime_fixtures.py' 'tests 2/test_air_control_mode_simulation.py'
git diff --check
```

HA Lab evidence from the original fault investigation remains supporting evidence only:

- Final read-only baseline after reset passed.
- Humidity-unavailable isolated probe held `telemetry_unavailable` and restored to
  normal.
- Configured-temperature-unavailable isolated probe held `telemetry_unavailable` and
  restored to normal.
- Full no-CO mutation matrix remains blocked by HA Lab transport or VM networking
  instability under repeated API pressure until a stable rerun proves otherwise.

Canonical direct simulation evidence added by the implementation:

- Normal baseline resolves to `normal` with CO ppm defaulting to 0.
- All configured humidity unavailable resolves to `telemetry_unavailable`.
- All configured temperature unavailable resolves to `telemetry_unavailable`.
- Distinct Kitchen/Hallway and Bedroom/Hallway values prove zone pressure can be
  represented independently of house peers.
- Level1 IAQ pressure resolves independently to the AQ lane.
- Disabled, manual, and global gates dominate lower pressure lanes.
- Elevated CO remains opt-in and is rejected by the fixture unless
  `co_pressure=True`.
- Opt-in elevated CO proves `sensor.humidity_intelligence_hi_air_control_mode`
  reports `co_emergency` even when a manual override flag is also present.

## 2026-05-31 HA Lab Continuity Addendum

Post-commit HA Lab evidence was recorded for canonical commit `c661238`:

- Stage A package deploy passed source-to-remote SHA verification and recorded a
  timestamped rollback path.
- Stage B post-restart read-only validation passed. The active lab baseline was
  `manual_override`, not `normal`; normal baseline remains covered by the canonical
  backend simulation test.
- Stage C opt-in CO pressure used only the approved CO helper mutation, raised CO to
  20.0, observed `sensor.humidity_intelligence_hi_air_control_mode` as
  `co_emergency` with the expected reason text, reset CO to 0.0, and observed clear
  back to the `manual_override` baseline after the clear hold.

Supporting local HA Lab reports:

- `.codex/lab/reports/2026-05-31T19-08-14Z-stage-a-package-deploy.md`
- `.codex/lab/reports/2026-05-31T19-16-00Z-stage-b-c661238-post-restart-validation.md`
- `.codex/lab/reports/2026-05-31T19-40-20Z-stage-c-c661238-co-pressure-validation.md`

Continuity caveats:

- This proves CO pressure for the recorded HA Lab Stage C scope only; it is not stable
  release authority by itself.
- Stage C did not prove a normal HA Lab baseline because the active baseline was
  `manual_override`.
- Fan isolation was off during Stage C, but no `fan.*` or `humidifier.*` entities were
  present and configured output placeholders were unresolved; residual no-real-output
  risk was explicitly accepted for that run.
- Stage B diagnostics still contained five unrelated unknown/unavailable telemetry
  references. They were not mode-sensor failures and must remain visible as release
  confidence caveats.
- No generated dashboard behavior, service contract, migration, stable Home Assistant
  environment, fake output write, or default CO pressure behavior changed.

## Release Decision

These fixes belong in v2.0.6 before stable release because they affect runtime
integrity and entity truth. Keep them under `Unreleased` until the next v2.0.6 beta,
RC, or stable package is actually cut. Do not retro-edit `2.0.6-beta.1` unless that
build was never published.
