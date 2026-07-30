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

Humidifier control has separate truth layers:

- effective lane demand after runtime gates and before humidifier-output isolation
- command intent and dispatch result
- Home Assistant-observed output state
- optional platform action when the entity domain exposes it
- isolated, retrying, degraded, unknown, or fault-latched reconciliation state

The existing humidifier-active helper entities represent effective demand only.
They do not prove command completion, an `on` output, or physical moisture
production. Configured humidifier outputs are observed directly and are aggregated
before writes; when both humidifier lanes share an output, demand is OR-owned and the
engine emits at most one non-conflicting command for that output per evaluation.

Output state-change events request coalesced evaluation and the configured engine
interval remains the periodic reconciliation safety net. Reconciliation is bounded:
one immediate dispatch, two delayed retries, then a visible fault latch until demand
changes or observed output truth recovers. Missing, unknown, unavailable, unsupported,
isolated, cross-family-owned, or active cross-entry-owned outputs suppress blind
turn-on behavior. A generic Home Assistant `on` state is only observed output truth;
even an optional humidifier action attribute is platform-reported evidence, not proof
of physical moisture production.

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

## External Service Authority

External Home Assistant calls to `pause_control`, `resume_control`,
`create_dashboard`, `purge_files`, `dump_diagnostics`, `self_check`,
`v205_release_check`, `dump_cards`, `view_cards`, `flash_lights`, and
`create_local_backup` require an admin user context whether they target one config
entry or all entries. The read-only `list_saved_versions` service is also admin-gated
because it exposes package-local snapshot inventory through a persistent
notification. An `entry_id` narrows a target only; it is not an authorization bypass.

Contextless background automation/script calls are intentionally rejected. Supported
external use originates from an authenticated admin UI or API session; any future
automated trusted route requires separate design approval.

First-run dashboard creation may use a trusted internal setup helper only after the
user explicitly selects dashboard creation in config flow. First-run card export,
option-triggered regeneration, and release-check test exports use a separate trusted
internal card exporter so admin-gating the public `dump_cards` and `view_cards`
handlers does not break integration-owned continuity. Startup refresh remains
cache-only and does not claim a filesystem export. Neither helper is exposed as a
contextless service bypass. The config entry records a dashboard identifier only
after registration succeeds. Dashboard creation authorization is separate from later
dashboard visibility.

Runtime-owned visual alerts call a separate trusted internal flashing helper after
the deterministic engine has selected an alert lane. The public `flash_lights`
service is admin-gated and is not the engine's control path; it cannot create,
reorder, or override a lane decision.

Generated-artifact purge must validate its full fixed target set before mutation,
show the exact existing file and configured dashboard targets in a completed blocking
notification before deletion, reject paths outside the direct owned basename set and
non-regular filesystem objects, and report partial failures truthfully.

Caller-selectable diagnostics and release-check report basenames must match
`humidity_intelligence_*.json` and are written only inside the owned
`<config>/humidity_intelligence/exports/` directory. Directory verification,
creation, temporary writes, atomic replacement, cleanup, and report purge stay
descriptor-relative, reject symlink/non-regular targets, and fail closed without a
config-root fallback. In-process writes are serialized; concurrent same-name calls
produce complete JSON and the last atomic replacement wins without promising caller
invocation order. The fixed self-check report uses the same writer and exact
`<config>/humidity_intelligence/exports/humidity_intelligence_self_check.json`
destination. Entry-scoped purge owns no export report. Only an unscoped all-entry
purge may remove the exact default diagnostics and fixed self-check exports;
release-check, custom, and legacy config-root reports remain retained.

Generated card YAML is written only inside
`<config>/humidity_intelligence/ui/`. Directory verification, creation, temporary
writes, atomic replacement, and cleanup are descriptor-relative and no-follow,
reject symlink and non-regular targets, revalidate directory/file identity, and fail
closed without a config-root fallback. Same-name writes are serialized. Multi-entry
installations use entry-qualified filenames; single-entry installations retain the
unqualified default names. Exact default/per-entry card and release-check test-card
exports are purge-owned. Custom card names and legacy root YAML are retained.
Adding a second entry re-exports every loaded entry with qualified names; removing
back to one entry re-exports the remaining entry with unqualified names. Superseded
owned-UI names are retained non-destructively, are no longer refreshed by HI, and
remain externally readable until an exact purge. Config-entry removal owns only the
removed entry's exact default/release-test UI exports and registered dashboard; it
does not own reports, custom card exports, or legacy root files. When removal returns
a multi-entry installation to one entry, the remaining entry's qualified files stay
retained while fresh unqualified exports are written.
Registered Lovelace dashboard YAML remains separately owned at
`<config>/dashboards/<url_path>.yaml`.

Dynamic state or attribute text rendered through generated-card HTML must be escaped
at the HTML sink. The V1 Mobile presentation remains available but deprecated through
v2.0.9; any removal requires a separately approved v2.1 migration contract.

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
