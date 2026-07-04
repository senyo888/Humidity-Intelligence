# Humidity Intelligence Architecture Contract

This is the public architecture contract for Humidity Intelligence. It records the
durable runtime and documentation rules that contributors, reviewers, and release
checks can rely on from tracked repository files.

Maintainers may keep deeper planning notes in ignored local files such as
`DESIGN_BRIEF.md`, `PROJECT_SUMMARY.md`, `ROADMAP.md`, or `PROPOSALS.md`. Those
files are not required for public contributor correctness and must not become release
authority unless their sanitized value is promoted into tracked documentation.

## Runtime Authority

Humidity Intelligence is a deterministic Home Assistant environmental control engine.
It resolves one selected ventilation lane per evaluation cycle and exposes the reason
through Home Assistant entities, diagnostics, and generated dashboards.

Runtime behavior is owned by tracked integration code, tracked tests, tracked service
schemas, tracked generated-card templates, and release documentation. Ignored local
planning notes may inform maintainer review, but they do not override tracked runtime
truth.

## Deterministic Lane Order

Ventilation lane priority is fixed:

1. CO emergency
2. Humidity danger
3. Mould danger
4. Mould risk
5. Condensation danger
6. Condensation risk
7. Zone 1
8. Zone 2
9. Air quality
10. Normal

CO emergency is always highest priority. Humidity, mould, and condensation alert lanes
must resolve source, room, and zone before applying zone-bound control. If an alert
candidate cannot be mapped safely, Humidity Intelligence must skip blind output writes,
surface degraded context, and continue explainably.

Humidifier lanes remain independent from ventilation lane resolution.

## Season-Aware Targets

Humidity danger and comfort interpretation are profile-relative. Runtime thresholds
must be derived from the active seasonal or custom target profile, not from stale static
alert values.

Temperature comfort display follows the same principle: UI colors and chips should use
backend comfort truth instead of card-only assumptions.

## UI Truth Contract

Generated dashboards are presentation surfaces, not decision engines.

They may render:

- selected runtime lane
- gate, pause, override, and disabled states
- active alert context
- degraded or unmapped alert context
- configured telemetry and output availability
- diagnostics and generated-card validation results

They must not invent entities, infer lane decisions independently, hide degraded
inputs, or imply output control that the backend did not select.

Current Air Control chips are display surfaces only. They must not create, reorder, or
alter lane decisions. Red control-row styling is reserved for selected alert or CO
runtime truth; environmental risk readings may still show risk colors in telemetry
chips without implying a selected command lane.

## Safe Degradation

Unknown, unavailable, incomplete, or unmapped inputs must degrade safely and
explainably. Missing outputs or failed optional service calls must be logged, skipped,
and exposed without crashing the control loop.

Optional frontend cards and UI dependencies must never block backend functionality.

## Home Assistant And HACS Boundaries

Config flow, options flow, entity registry behavior, services, translations,
diagnostics, and generated files must remain compatible with supported Home Assistant
versions.

Avoid blocking filesystem, network, or slow I/O work in async Home Assistant paths.
Keep service schemas explicit and error messages actionable. Keep `hacs.json` limited
to HACS-supported keys and keep integration metadata in `manifest.json`.

## Documentation And Release Boundaries

When architecture, runtime behavior, security posture, release flow, contributor
expectations, documentation expectations, generated UI truth, or entity semantics
change, update the relevant tracked public docs in the same work.

Release truth must remain in tracked repository files, release notes, and Home
Assistant metadata. Private maintenance evidence and ignored local planning surfaces
may support review, while release approval, runtime behavior, and tracked validation
stay with the canonical repository surfaces.
