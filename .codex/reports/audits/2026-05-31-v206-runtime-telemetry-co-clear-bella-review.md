# Bella Review - V2.0.6 Runtime Telemetry And CO Clear Fixes

Status: Bella review completed for narrow v2.0.6 implementation.

## Verdict

Approved after correction. The fix belongs in v2.0.6 because it affects runtime
integrity, CO emergency clear timing, and backend entity truth.

## Findings Corrected

1. Unrelated test drift was present in the old work-folder diff.
   - Risk: committing unrelated temperature-comfort test removals would mix release
     scopes and weaken reviewability.
   - Correction: canonical transplant includes only the three targeted runtime
     regressions.

2. Proposal wording used local absolute checkout paths.
   - Risk: private/local machine paths could leak into branch history.
   - Correction: canonical proposal uses portable checkout wording and public-safe
     file references.

3. Canonical release-truth docs did not yet include the runtime contract.
   - Risk: runtime behavior, entity semantics, and release notes would drift.
   - Correction: `CHANGELOG.md`, `DESIGN_BRIEF.md`, and `README.md` now describe the
     degraded telemetry mode and timed CO clear behavior.

## Runtime Review

- CO emergency remains above gates, pause, manual override, and normal control locks.
- Missing required telemetry is checked only after CO, control lock, global gate, and
  pause handling.
- The degraded telemetry guard runs before alert, humidifier, zone, and AQ lanes.
- Temperature telemetry is only required when configured.
- No service contract change is introduced.

## UI Truth Review

Generated dashboards remain display surfaces. The backend may publish
`telemetry_unavailable`; cards that show runtime mode should reflect that backend
truth. No card-template mutation is required.

## Required Release Notes

- Runtime impact: CO clear is time-bounded by an engine-scheduled recheck.
- Entity semantics changed: yes, `sensor.humidity_intelligence_hi_air_control_mode`
  may report `telemetry_unavailable`.
- UI impact: display-only backend truth update; no generated-card template change.
- Migration: none.
- Restart or reload: required after deploying changed runtime source.
