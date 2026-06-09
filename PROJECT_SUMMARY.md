# Humidity Intelligence V2 Project Summary

Local working summary for planning, release checks, and reviewer preparation.

This file is intentionally local-only and ignored by Git.

## Current Release State

- Stable release-source version: `2.0.6`.
- Active beta line: `2.0.7-beta.1` on `senyo888-patch-1`.
- Current folder status: retired historical/reference copy. Do not use this folder's
  manifest, changelog, git status, or generated files as release authority.
- Package type: Home Assistant custom integration.
- Distribution target: HACS custom repository, category `integration`.
- Runtime stance: deterministic control, one selected ventilation lane per
  evaluation cycle.
- Stable release history: v2.0.5 is complete and closed; v2.0.6 is the current
  stable maintenance line.
- Future direction: no v2.1 Environmental Stability Intelligence, Stability Score,
  prediction, dashboard-strategy, or Harmonic control feature is implemented in the
  v2.0.6 stable line.
- Public support architecture: the README is the HACS/public front door, tracked docs
  remain the version-controlled support/release/governance layer, and the GitHub Wiki
  is the active public support manual for longer configuration, services, diagnostics,
  generated-dashboard, HACS/update, AQ/CO safety, troubleshooting, and release-validation
  guidance.
- Wiki authority boundary: the Wiki explains backend, service, diagnostics, generated
  dashboard, HACS, and release-documentation truth; it does not own runtime behavior,
  entity semantics, service schemas, generated dashboard logic, diagnostics, HACS
  metadata, migration requirements, release state, or lane-order truth.
- HA Lab status: admitted as Operational Beta Validation Infrastructure. It provides
  advisory beta deploy, runtime-readiness, diagnostics, and generated-card/entity-map
  evidence, but it is not release authority, runtime authority, stable Home Assistant
  authority, or permission for autonomous mutation.

## Local Workspace Structure

- The canonical editable local repo is the GitHub checkout or a git worktree created
  from it.
- The old HI Work folder is retired as an editable source and should be treated as
  historical/reference material only.
- Local planning files are preserved in the canonical checkout as ignored,
  unpublished continuity files.
- Local lab, credential, generated-export, and agent-private files must stay under
  ignored paths.
- Release claims, validation summaries, staging, commits, and publishing must come
  from the canonical checkout or active worktree.

## Completed V2.0.6 Scope

- Promoted integration metadata to stable `2.0.6` in the canonical release-source
  checkout.
- Added degraded `telemetry_unavailable` runtime mode when required humidity or
  configured temperature telemetry is unavailable while control is otherwise enabled.
- Fixed global gate preemption so lower-priority humidity-danger alert switch,
  context, telemetry, and Current Air Control alert truth clear when a gate takes
  authority.
- Fixed CO emergency clearing so HI schedules a recheck at the two-minute clear-hold
  deadline rather than waiting for the next normal control interval.
- Added backend air-control-mode simulation validation for normal, telemetry
  unavailable, zone, AQ, gate, and opt-in CO pressure cases without adding runtime fake
  telemetry paths.
- Fixed setup/options telemetry add/edit Cancel navigation so saved flow data is not
  lost by HI-controlled Cancel actions.
- Fixed Zone 2 setup/options defaults and trigger labels so Zone 2 ownership resolves
  to `level2` unless explicitly changed.
- Added manual local HI-only snapshot services: `create_local_backup` and
  `list_saved_versions`.
- Kept snapshot support package-local and manual only; no restore flow, automatic
  rollback, HACS interception, startup snapshot, or whole-instance backup behavior is
  implemented.
- Added v2.0.6 drift Statistics-helper ownership/readiness reporting, missing-helper
  Repairs guidance, low-history coverage status, invalid-source status, and docs/test
  cleanup.
- Retuned optional Current Air Control temperature chip colours to backend-owned
  seasonal cold, comfort, warm, and hot boundaries.
- Exposed the resolved seasonal warm boundary through comfort sensor attributes and
  diagnostics so generated cards do not hard-code warm thresholds.
- Preserved drift math, lane priority, AQ behavior, humidifier independence, output
  writes, migration behavior, HACS update behavior, and generated-dashboard semantics
  except for displaying backend-owned `telemetry_unavailable` and gate-preemption
  truth.

## Active V2.0.7 Beta Maintenance State

- Manifest version: `2.0.7-beta.1`.
- Current source branch: `senyo888-patch-1`.
- Current HA Lab green evidence commit: `03d18d1` (`Fix PM25 aggregate runtime truth`).
- The PM2.5 aggregate runtime truth fix is implemented and HA Lab Stage 3 now passes.
- Current HA Lab operational beta baseline:
  `.codex/lab/baselines/current-first-slice-runtime-baseline.md`.
- Stage A deploy evidence:
  `.codex/lab/reports/2026-06-09T18-23-00Z-stage-a-package-deploy.md`.
- Stage 3 PASS evidence:
  `.codex/lab/reports/2026-06-09T18-29-19Z-stage-3-six-sensor-runtime-readiness.md`.
- Current HA Lab runtime proof includes canonical PM25 aggregate entities:
  `sensor.humidity_intelligence_hi_house_pm25_average`,
  `sensor.humidity_intelligence_hi_level1_pm25_average`, and
  `sensor.humidity_intelligence_hi_level2_pm25_average` at `5.0`, with old
  `sensor.humidity_intelligence_hi_house_pm2_5_average` absent.
- This is advisory beta evidence only. It does not promote a release or replace Bella,
  Aetherwing, AetherCore, release-candidate validation, stable Home Assistant evidence
  where required, or Senyo approval.

## Completed V2.0.5 Scope

- Setup/options progressive disclosure with essentials first and Advanced tuning
  second.
- Advanced tuning uses in-form collapsible sections so controls open and retract
  immediately without pressing Submit.
- Recommended-default helper wording across relevant configuration pages.
- Advanced-only placement for control-loop timing, startup UI mapping refresh, custom
  target/comfort values, slope source overrides, fan levels, thresholds, lane removal,
  AQ tuning, and visual-alert tuning.
- `show_output_entity_details` as a UI-only generated-card visibility option.
- Cleaner V2 output display by default for new installs.
- `v2_tablet` as the first-install UI export default.
- Canonical `dump_cards` behavior preserved: unscoped exports all cached/generated
  layouts; scoped `layout` exports only the specified layout.
- Runtime lane order, alert hierarchy, CO emergency behavior, humidifier independence,
  and public entity semantics preserved.
- Read-only `v205_release_check` Home Assistant service for validation of
  generated-card visibility, cached layouts, unresolved placeholders, entity
  availability, and scoped/unscoped `dump_cards` behavior.
- Shared frontend dependency truth surface across setup/options, `self_check`,
  `v205_release_check`, and `dump_diagnostics`, using Lovelace resource inspection
  with non-blocking `not_inspectable` fallback.
- Native Home Assistant config-entry diagnostics for redacted GitHub issue
  attachments.
- House humidity drift 7d reports canonical statistics dependency status for
  `sensor.house_humidity_mean_7d` without changing valid drift calculations.
- Calculated temperature slope telemetry resolves registered Home Assistant entity IDs
  when they differ from predicted fallback IDs.

## V2.0.7 PM2.5 Maintenance Closure

- V2.0.7 first required fix: PM2.5 house aggregate runtime truth.
- Triggering evidence: HA Lab Stage 3 six-sensor runtime readiness on 2026-06-06 found
  `sensor.humidity_intelligence_hi_house_voc_average` present and numeric while
  `sensor.humidity_intelligence_hi_house_pm25_average` was missing with HTTP `404`.
- Investigation found the PM2.5 aggregate existed under Home Assistant's generated
  dotted slug shape (`pm2_5`) rather than the canonical HI `pm25` entity ID expected
  by the Stage 3 contract.
- Local implementation now normalizes existing HI PM2.5 aggregate entity IDs from
  `pm2_5` to `pm25` and makes new PM2.5 aggregate names object-ID safe.
- HA Lab Stage A deploy and Stage 3 rerun on 2026-06-09 now provide advisory
  operational beta evidence that the canonical PM25 aggregate entities are present
  and numeric.
- Required outcome: configured PM2.5 telemetry must expose a backend-owned numeric
  house PM2.5 aggregate when usable PM2.5 telemetry exists and degrade explicitly when
  unconfigured, unknown, or unavailable.
- Boundary: generated UI must consume backend aggregate truth only; no frontend
  inferred PM2.5 aggregate, no AQ lane priority change, no lane-order change, and no
  v2.1 feature pull-forward.

## Current Focus

- Keep v2.0.6 stable release docs, support guidance, dashboard exports, and metadata
  aligned with the canonical release-source checkout.
- Keep README-to-Wiki routing, the Wiki Services Reference, public Wiki footer
  navigation, Wiki banner placement, release-governance Wiki status, and PR-template
  Wiki status aligned with repository truth whenever public support/manual guidance
  changes.
- Treat v2.0.5 as completed release history. Do not leave shipped v2.0.5 functionality
  in active roadmap buckets.
- Treat v2.0.6 beta-prep items as stable v2.0.6 release history once they are present
  in the canonical stable changelog and manifest.
- Carry v2.0.7-beta.1 through advisory HA Lab, generated-card/entity-map, Bella,
  Aetherwing, AetherCore, release-readiness, and Senyo review without treating HA Lab
  evidence as release authority.
- Keep v2.1 Environmental Stability Intelligence work behind governance, fixture,
  diagnostics, and opt-in display gates.
- Report normal pytest as locally blocked unless Home Assistant is installed; use the
  direct sanity harness as the local fallback.

## Local Validation Checklist

- Python compile check for changed integration modules.
- Runtime/card sanity checks in `tests 2/test_runtime_card_sanity.py`.
- Current direct sanity expectation for the canonical release-source state:
  `51 direct sanity checks passed`.
- Air-control mode simulation expectation:
  `10 air-control mode simulation checks passed`.
- Native diagnostics direct sanity coverage should be run after diagnostics changes.
- Issue triage direct sanity coverage should be run after issue-template or triage
  changes.
- Manual card export check with `humidity_intelligence.dump_cards` after UI template or
  generated-card behavior changes.
- HACS metadata sanity: `manifest.json`, `hacs.json`, `brand/icon.png`, workflows.
- HACS Integration Preflight from VS Code when available, for release packaging,
  install metadata, manifest/repository hygiene, and HACS workflow sanity.
- Version-governance sanity: `python3 scripts/check_version_governance.py`.
- Future hard release gate: full Bella verification, full AetherCore verification,
  release sanity validation, Home Assistant/runtime validation appropriate to scope,
  and README approval by Senyo before tagging or publication.

## Known Guardrails

- Do not rename the integration.
- Do not introduce private entity IDs.
- Do not add hidden control paths outside the deterministic engine.
- Keep dashboard display aligned with backend telemetry and diagnostics.
- Keep alert chipsets concise: lane/status plus resolved source context only.
- Visual humidity/mould/condensation alerts flash 10 times, restore prior light state,
  then repeat after 30 minutes only while the same alert remains active.
- Keep docs, release notes, and runtime behavior in sync.
