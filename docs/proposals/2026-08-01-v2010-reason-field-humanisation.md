# Humidity Intelligence Reason Field Humanisation — House-Agent Implementation Proposal

## Metadata

```yaml
proposal_id: HI-PROP-20260801-001
proposal_urn: urn:hi:proposal:20260801:001:v2010-reason-field-humanisation
title: Humidity Intelligence Reason Field Humanisation
created: 2026-08-01
category: runtime-ui-contract
target_version: v2.0.10
implementation_version: 2.0.10-beta.2
authority_status: implementation_authorized
state: REVIEW
owner: Jules
risk_level: medium
runtime_impact: additive-presentation-plus-dashboard-service-and-cleanup-fail-safe
affected_surfaces:
  - runtime-reason-presentation
  - air-control-reason-entity
  - generated-v2-ui
  - gallery-examples
  - public-docs
  - dashboard-service-compatibility
  - generated-artifact-cleanup
rollback_defined: true
bella_design_approved: true
aetherbite_copy_design_approved: true
aetherwing_design_validated: true
aethercore_design_validated: true
maintainer_design_approved: true
implemented_diff_review: approved_phase3_all_four_roles
bella_implemented_diff_review: approved_phase1
aetherbite_implemented_diff_review: approved_phase1
aetherwing_implemented_diff_review: approved_phase1
aethercore_implemented_diff_review: approved_phase1
phase1_tracked_patch_sha256: 08136cd51cdf95f2cfc48b3f42a5c9a2db8c3cfce3f2426b481db7f75b46a17a
phase1_untracked_tar_sha256: c3a73e30693e769d4567c9d50f12056fd016bbc79fcfba20da8a437c1a494696
phase2_authorized: true
phase2_implementation_status: implemented
phase2_implemented_diff_review: approved
bella_phase2_review: approved_post_amendment
aetherbite_phase2_review: approved
aetherwing_phase2_review: approved
aethercore_phase2_review: approved
gallery_preview_status: deterministic_capture_reviewed
phase2_copy_amendment: singular_generic_output_definite_article
phase2_copy_amendment_scope: presentation_text_and_exact_regression_only
phase2_copy_amendment_review: approved_all_four_roles
phase2_tracked_patch_sha256: c7c1c55505878481b5c0000202d949dc31327805624a21d83e5601471924d3ef
phase2_untracked_tar_sha256: 208a910bffc25bf7266a25f0fe074c90723bbdd045d5be28e7c6e3e77bf03371
phase3_authorized: true
phase3_amendment: dashboard-compatibility-fail-safe
phase3_validation_status: offline_passed_supported_ha_loader_and_playback_deferred_phase4
phase3_implemented_diff_review: approved_all_four_roles
aetherbite_phase3_review: approved
bella_phase3_review: approved
aetherwing_phase3_review: approved
aethercore_phase3_review: approved
local_commit_status: ready
phase3_review_candidate_tracked_patch_sha256: ced86d8d377ad64a2e4f427d5341d55591fb0f8ea5ec55c030de0f97642b2869
phase3_review_candidate_untracked_tar_sha256: 45f1dcc62bec051b9a61e1a001d3bb019cb56febb1ab2c7f743897cea2bd3039
phase3_post_candidate_edits: validation-status-record-plus-ignored-service-field-copy
registered_dashboard_validation: deferred_unsupported_path_removed
ha_lab_validated: not_run
release_candidate_validated: not_run
implemented_in: null
entity_contract_changed: true
entity_contract_change: additive-versioned-attribute
service_contract_changed: true
service_contract_change: create_dashboard_guidance_only_fail_safe
config_flow_choice_changed: true
config_schema_changed: false
stored_data_changed: false
legacy_create_dashboard_token: ignored_export_only
dashboard_delete_ownership: removed
lane_order_risk: low
ui_truth_risk: low_after_atomic_card_cutover_pending_phase4_ha_lab_playback
stable_runtime_risk: low_unreleased_pending_phase4_supported_ha_validation
breaking_reason_state_replacement: deferred_requires_separate_v2_1_proposal
```

## Executive Recommendation And Feasibility

**Verdict: feasible with low control risk and low residual UI-truth risk after the
atomic card cutover.** The additive backend-owned `display_reason` attribute is now
implemented on the existing reason sensor for `2.0.10-beta.2`; the technical state is
retained as a compatibility and diagnostic surface, and the new attribute is the
only normal V2 reason-area authority across all four reviewed V2 card surfaces.

This is deliberately not a v2.1 change. It does not replace or reinterpret the entity
state, add stored configuration, alter entity identity, or change deterministic lane
priority. Any future breaking reason-state replacement requires a separate v2.1
proposal and migration contract; it is not authorized or scheduled here.

Phase 1 delivered the backend schema, presenter, publication, sensor attributes,
diagnostics metadata, tests, version identity, and public documentation. Phase 2
then cut over V2 Mobile, Tablet, and both matching gallery cards atomically, with a
strict executable renderer contract, deterministic gallery captures, and separate
house-agent review. The split keeps rollback evidence clear and prevents runtime and
frontend truth changes from being reviewed as one opaque patch.

**Status: `REVIEW_REQUIRED`.** Phase 1 and Phase 2 are approved. Bella has now closed
the bounded post-amendment acknowledgement. Phase 3 is authorized and its repository
implementation includes a release-blocking dashboard compatibility fail-safe found
during validation. Offline validation has passed; fresh implemented-diff verdicts are
the remaining local commit gate. Exact-commit supported-HA loading and HA Lab playback,
push, PR, promotion, tag, and release remain separate later authorities.

## Decision

Add a bounded, backend-owned `display_reason` attribute to the existing Current Air
Control Reason entity. The attribute uses the `hi.reason.v1` contract and becomes the
sole normal presentation authority for the V2 Mobile and Tablet reason area.

The existing entity identity, state, `full_reason`, truncation behavior, and
`humidifier_status` remain backward compatible. Cards fall back to the escaped legacy
reason when the new attribute is absent, invalid, or from an unsupported schema.

The maintainer approved:

- `display_reason` as the sole normal V2 reason-area authority;
- the `hi.reason.v1` schema with `scope`, `truth`, bounded `args`, a six-line target,
  an eight-line hard limit, and a 4 KiB serialized limit;
- `requested` to mean a Home Assistant service-layer dispatch without an immediate
  service-call exception, not device acceptance or physical actuation;
- configured HI label, Home Assistant friendly-name, then generic-label precedence;
- no raw entity IDs in the new contract;
- a visible calm/neutral explanation;
- no technical-details expander in beta.2;
- explicit user replacement of the complete YAML inside an existing HI Manual card;
  registered/YAML-mode dashboard documents remain Home Assistant-managed and unchanged;
- a distinct degraded `presence_unavailable` presentation while preserving the
  existing fail-closed gate effect; and
- v2.1 as the future governed boundary for any breaking replacement of the reason
  state.

## Problem

The current V2 reason area has two explanation authorities:

1. backend technical reason composition; and
2. card-authored `Stage:`, risk, timer, isolation, and `Engine:` lines.

This creates duplication and allows frontend wording to overstate runtime truth. The
current cards can describe configured ventilation outputs as purifiers, suppress a
meaningful humidifier `platform_idle` disagreement because it contains the word
`idle`, and present cooking/bathroom timer claims that are not owned by the reviewed
engine lifecycle.

The v2.0.10 humidifier reconciliation wording is the model for the new contract. It
separates environmental demand, command dispatch, Home Assistant-observed state,
platform action, retry/fault/isolation truth, and physical-output caveats before
forming human sentences.

## Verified Current-State Diagnosis

The diagnosis was re-proved against `senyo888-patch-1` at
`cb46c19bf205166973614bfa6152bca614a3bc16` before the implementation branch was
created.

- [`_build_runtime_reason` at baseline `cb46c19b`](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/automations/engine.py#L2246) owns the legacy runtime-reason composition;
  [`_format_zone_detail` at the same baseline](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/automations/engine.py#L2308) still formats zone detail with internal `Trigger
  detail` wording and technical comparisons, while [`_with_isolation_notice`](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/automations/engine.py#L2631)
  appends output-isolation notices to the same technical string.
- [`_compute_reason` at baseline `cb46c19b`](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/sensors/core.py#L707) publishes that state, optional `full_reason`, truncation
  marker, and `humidifier_status`. It is therefore the correct compatibility point
  for one additive validated presentation attribute.
- At baseline, [`ui/cards/v2_mobile.yaml`](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/ui/cards/v2_mobile.yaml#L747) and
  [`ui/cards/v2_tablet.yaml`](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/ui/cards/v2_tablet.yaml#L566) began a second, frontend-authored explanation model. The cards suppressed
  calm text through `greenNoise` (Mobile line 890; Tablet line 709), created `Stage:`
  copy (Mobile line 915; Tablet line 734), and appended `Engine:` copy (Mobile line
  974; Tablet line 793).
- The reason window already scrolled at baseline: both canonical cards used a
  60-pixel maximum height with vertical overflow ([Mobile line 1446](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/ui/cards/v2_mobile.yaml#L1446),
  [Tablet line 1265](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/ui/cards/v2_tablet.yaml#L1265)). The six-line target is therefore a comprehension and mobile-density target,
  not an assumption that all content is simultaneously visible.
- Matching gallery examples duplicated the same JavaScript composition at baseline,
  for example [Mobile AQ line 748](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/ui-gallery/default-v2-mobile-aq/card.yaml#L748) and
  [Tablet Zone 2 line 567](https://github.com/senyo888/humidity-intelligence/blob/cb46c19bf205166973614bfa6152bca614a3bc16/ui-gallery/default-v2-tablet-zone-2/card.yaml#L567). Generated and gallery truth could drift unless all four surfaces changed
  together.
- `tests 2/test_air_control_mode_simulation.py` and
  `tests 2/test_humidifier_reconciliation.py` provide direct engine/entity playback;
  `tests 2/test_runtime_card_sanity.py` is the existing cross-card parity gate.

The hypothesis is confirmed: the current reason area has two voices and can repeat
gate/isolation truth, expose engineering vocabulary, overstate fan action as device
activity, and hide a useful neutral explanation. The humidifier copy feels more
trustworthy because its sentences follow distinct evidence states instead of
inferring one broad status from demand alone.

## Content Contract

The reason area answers, in deterministic order:

1. what HI selected or what state currently holds;
2. why, with human-readable measurements and thresholds;
3. what HI requested, blocked, or deliberately withheld;
4. what Home Assistant observed, when an observed-state contract exists; and
5. what changes the decision, only when the backend genuinely knows.

Approved vocabulary:

- `selected`: the backend selected the current lane, mode, or behavior;
- `requested`: HI handed a validated service request to Home Assistant without an
  immediate service-layer exception;
- `blocked`: an explicit gate, isolation, ownership rule, missing mapping, or service
  error prevented the request;
- `observed`: Home Assistant exposed a usable mapped entity state;
- `unavailable`: required evidence has no usable current value;
- `not mapped`: no confirmed mapping exists; and
- `not confirmed`: the available evidence cannot prove the claim.

Do not use `running`, `forced`, `working`, `safe`, `healthy`, `all clear`, `resolved`,
or predictive exit wording without evidence supporting that exact meaning.

## Agreed House Style

- Calm, direct, domestic, technically transparent, and safety-aware.
- Lead with the selected state, then the measured reason, then the action or
  deliberate non-action, then observed/reconciliation truth, then a genuine exit
  condition.
- Prefer one complete sentence per line. Avoid lane jargon, entity IDs, comparison
  operators, raw thresholds without units, and repeated isolation notices.
- Use `HI` when naming an intentional system action. Use `Home Assistant` only for
  service dispatch or observed platform truth. Use `physical` only to state a
  measurement caveat, never to imply device acceptance.
- Keep thresholds and measurements when they explain the decision. Translate `>=`
  and `<=` into `at or above` and `at or below`.
- Always show the neutral explanation. Neutral does not mean healthy, safe, or all
  clear; it means HI is monitoring and no ventilation response is selected.
- State an exit condition only when the backend owns it, such as a timer ending, a
  CO clear hold, or a configured stop threshold. Do not predict sensor recovery.

## Representative Current-To-Proposed Wording Matrix

| Runtime family | Current pattern | Proposed backend headline and key lines |
| --- | --- | --- |
| Normal | `Stage:` may be suppressed; long engine summary follows | **Monitoring.** “HI is monitoring; no ventilation response is selected.” Add concurrent humidifier or isolation truth only when relevant. |
| Alert-only normal | Card-authored `Monitor + alerts only` stage | **Monitoring alerts.** “Monitor + Alerts Only mode is active; HI is monitoring alerts without automatic zone, air-quality, or humidifier output control.” |
| Disabled | `Stage: ... idle` plus engine reason | **Automatic control disabled.** “HI is not making automatic control decisions.” |
| Manual override | `Stage: Manual override` plus engine reason | **Manual override active.** “HI is not making automatic control decisions.” |
| Pause | `Stage: Paused.` plus timer/engine fragments | **Automatic control paused.** “Automatic control is paused.” “Pause remains active until the pause timer ends.” |
| Time gate | `Stage: Time gate hold` plus technical window string | **Time gate active.** “The current time is outside the configured 22:00–06:00 window.” “Automatic control is blocked; HI selected the configured gate output reset.” |
| Presence away | `Presence gate away (system disarmed)` | **Presence gate active.** “All configured presence sources explicitly report away.” Do not say disarmed unless that is an owned backend state. |
| Presence unavailable | Often collapses into away wording | **Presence status unavailable.** “All configured presence sources are unknown or unavailable.” “Occupancy cannot be confirmed.” |
| Required telemetry | Technical unavailable list | **Required telemetry unavailable.** “Required humidity telemetry is unavailable.” “HI did not continue with zone, alert, air-quality, or humidifier decisions.” |
| Zone 1/2 | `Trigger detail: Humidity delta 8.2% >= threshold 6%` | **Zone 1 response selected.** “Humidity is 8.2 percentage points above the home average; response starts at a difference of 6 percentage points.” “Output selection: 66% for Kitchen Extractor.” |
| AQ trigger | `Stage: Air-quality assist running` plus operators | **Air quality response selected.** “Downstairs: PM2.5 is 48 µg/m³, at or above the 25 µg/m³ threshold.” “Downstairs output selection: 66% for the configured air-quality ventilation output.” |
| AQ run window | Same as an active trigger | **Air quality response selected.** “Downstairs AQ run window remains active after the latest trigger.” Do not claim the trigger is still active. |
| Actionable alert | `Stage: Alert lane active` plus source IDs/details | **Humidity danger selected.** “The selected reading is 68.0%, at or above the active 66% threshold.” “Output selection: 100% for the configured alert ventilation output.” |
| Alert conflict/hold | Internal priority detail | “Selection followed deterministic alert and zone priority.” or “The existing actionable alert remains selected until it clears.” |
| Unmapped/degraded alert | Long degraded notice, sometimes repeated | **Monitoring with limited alert response** (`attention: degraded`). “Another active alert could not be mapped to a configured zone output; automatic boost was not selected for it.” |
| CO emergency | “forced to 100%” even when isolation can suppress calls | **Carbon monoxide emergency selected.** State the highest reading and threshold; then `selected`, `blocked`, or `unmapped` output truth. State the two-minute below-clear-threshold hold. |
| Fan isolation | Repeated suffix and card stage | “Fan-output isolation is active; fan service calls are suppressed.” Once only. |
| Humidifier demand | Demand and device action can blur | “Upstairs: 51.4% is at or below the 54% start threshold; demand is active.” |
| Humidifier dispatch | Often described as output activity | “HI sent the output-on request to Home Assistant; confirmation is pending.” `requested` means successful HA service-layer dispatch only. |
| Humidifier observed on | Broad active wording | “Output observed on.” Then: “Physical moisture output is not independently confirmed.” |
| Platform idle disagreement | Can be hidden by `idle` suppression | “Output observed on; platform action idle.” Preserve the physical-output caveat. |
| Retry/fault/degraded | Technical reconciliation terms | “HI sent a bounded reconciliation retry to Home Assistant; confirmation is pending.” / “Reconciliation fault is latched after bounded attempts.” / “Output reconciliation is degraded; activity is not confirmed.” |
| Stop confirmation | Demand-off can look complete | “Upstairs: humidification demand is inactive. HI sent the output-off request to Home Assistant; output-off confirmation is pending.” |

## Architecture Options Considered

| Option | Advantages | Costs and risks | Decision |
| --- | --- | --- | --- |
| Rewrite the existing reason state | Smallest apparent entity surface; new cards read state directly | Breaking for automations, templates, support tooling, state-length handling, and mixed-version cards; removes technical fallback | Reject for beta.2; reserve for v2.1 governance |
| Add versioned `display_reason` attribute | Backend-owned UI truth, atomic fallback, additive entity semantics, bounded/localisation-ready structure, no new entity | Attribute size and frontend validation must be governed; legacy and presentation surfaces coexist | **Recommended and approved** |
| Add a new presentation entity | Strong separation and independent state size | New entity-registry/migration/support surface; cards must coordinate two entities; more availability drift | Reject as unnecessary |
| Humanise only in card JavaScript | No Python change | Preserves two authorities, duplicates logic across generated/manual/gallery cards, cannot prove dispatch/observation truth, poor localisation path | Reject |
| Replace state and add a technical attribute | Cleaner long-term public state | Still breaking and forces every technical consumer to migrate at once | Reconsider only in v2.1 |

The versioned attribute is the only option that satisfies backend ownership and
mixed-version rollback without a new registry surface. `hi.reason.v1` is an exact
schema sentinel; unsupported versions receive complete legacy fallback rather than
partial rendering.

## `hi.reason.v1` Schema

```yaml
display_reason:
  schema: hi.reason.v1
  locale: en
  family: zone
  variant: humidity_delta
  attention: active
  truncated: false
  headline: Zone 1 response selected
  lines:
    - role: why
      scope: ventilation
      code: zone.humidity_delta_above_start
      truth: observed
      text: Kitchen humidity is 8.2 percentage points above the home average; the configured start point is 6.0.
      args:
        value: 8.2
        threshold: 6.0
        unit: percentage_points
        room_label: Kitchen
    - role: action
      scope: ventilation
      code: output.level_selected
      truth: selected
      text: Output selection: 100% for Kitchen Extractor.
      args:
        level: 100
        output_label: Kitchen Extractor
```

Allowed presentation values:

- `attention`: `neutral`, `active`, `hold`, `degraded`, `critical`, `unknown`;
- `role`: `why`, `action`, `next`, `notice`;
- `scope`: `system`, `safety`, `ventilation`, `humidifier`;
- `truth`: `selected`, `blocked`, `requested`, `observed`, `unavailable`,
  `unmapped`, `not_confirmed`, `failed`.

`family`, `variant`, `attention`, `scope`, and `truth` describe presentation truth.
They must never feed lane selection, output dispatch, or card-authored control logic.
Schema-1 cards render final backend-authored `headline` and `lines[*].text`; they do
not assemble prose from `args`.

Bounds:

- target six lines and hard maximum eight;
- 120 Unicode characters for the headline;
- 200 Unicode characters per line;
- 64 Unicode characters per dynamic label;
- six scalar allowlisted arguments per line;
- maximum 4 KiB UTF-8 serialized contract;
- deterministic line and argument order; and
- no raw entity IDs, device IDs, arbitrary mappings, timestamps, ticking countdowns,
  HTML, or Markdown.

When bounded aggregation is necessary, retain safety, degraded, isolation, action,
and observation truth before secondary explanation and set `truncated: true`.

## Presence Unavailable Policy

The current fail-closed control effect is preserved in beta.2, but unavailable-only
evidence must not be presented as confirmed absence:

- any configured source reports present: the gate passes;
- every usable configured source explicitly reports away: `presence_away`;
- no source reports present and at least one source is missing, unknown, or
  unavailable: `presence_unavailable` with `attention: degraded`;
- both blocking outcomes keep the current gate effect; and
- CO emergency continues to bypass the gate.

No cached last-known presence state or new configurable unknown policy is introduced
in beta.2.

## Runtime Boundary

The presenter runs after authoritative control work:

1. resolve the ventilation lane and concurrent humidifier truth;
2. complete helper, timer, reconciliation, and service-call work;
3. publish `runtime_mode`;
4. publish the existing technical reason unchanged;
5. build and validate `display_reason` from an immutable bounded fact snapshot;
6. clear current-cycle presentation data on presenter failure; and
7. refresh entities through the existing path.

The final fact collector may read already-finalized in-memory runtime truth and
current Home Assistant labels/states after control work, but it must not call
services, schedule work, mutate control truth, or participate in lane selection. The
pure schema presenter accepts only the immutable fact snapshot and performs no Home
Assistant access. A fact-collection, sanitization, validation, or serialization
exception must not escape the reason-publication boundary or leave stale presentation
data.

## Card Contract

V2 Mobile, Tablet, and the matching canonical gallery cards:

- validate exact `hi.reason.v1` support;
- render the backend headline and ordered line text;
- escape every rendered value at the HTML sink;
- retain the existing 60-pixel scrollable reason window;
- always show the calm neutral explanation;
- remove normal card-authored Stage, risk, timer, isolation, and Engine composition;
- remove the `greenNoise` suppression path; and
- fall back atomically to escaped `full_reason`, escaped state, then `Reason
  unavailable`.

Unknown or malformed schemas receive complete legacy fallback. Cards must not attempt
partial or family-based reconstruction.

V1 Mobile remains unchanged.

## Label And Privacy Boundary

Presentation-label precedence:

1. sanitized configured HI display label;
2. sanitized Home Assistant `friendly_name` when it materially explains the action;
3. a generic description such as `the configured ventilation output` or
   `2 configured outputs`.

Raw entity IDs are forbidden in `text` and `args`. Local labels may appear in local
Home Assistant state, but public fixtures, gallery examples, docs, screenshots, and
tests must use canonical or sanitized examples.

Diagnostics and support reports expose only contract availability, schema, family,
variant, attention, validation state, truncation state, and line count. They do not
copy rendered text or label-bearing arguments.

## Dashboard, Restart, And Migration Impact

- V2 generated templates and gallery examples change.
- Existing Manual cards require fresh export and re-paste.
- HI exports card fragments, not complete dashboard documents. Existing registered or
  YAML-mode dashboard files remain unchanged and must not be overwritten with an
  export. Create/open a dashboard through Home Assistant, then add a Manual card or
  replace the complete YAML inside an existing HI Manual card.
- `refresh_ui` is cache-only. `view_cards` writes the export and reports the exact path.
- The compatibility-only `create_dashboard` service remains registered and admin-gated
  but performs no mapping, rendering, Lovelace import, notification, or filesystem
  mutation; it returns the supported Manual-card steps as a deterministic error.
- Full Home Assistant restart is required after installing updated Python files.
- Config-entry reload alone is not sufficient to import replaced modules.
- No config/options schema, stored data, entity registry, or helper migration is
  introduced. Legacy `create_dashboard` selections and `ui_dashboard_id` values remain
  inert without rewrite or retry loops.
- No new frontend dependency is introduced.

## Exact Implementation Scope

Essential beta.2 scope:

- [helpers/reason_presentation.py](../../helpers/reason_presentation.py): frozen fact/line types, exact schema builder,
  validator, bounds, label sanitizer, raw-ID prohibition, and privacy-safe diagnostic
  metadata.
- [automations/engine.py](../../automations/engine.py): structured gate/trigger facts and final-cycle presentation
  factories for every approved runtime family. Presentation collection and validation
  stay inside a failure-isolated publication boundary.
- [sensors/core.py](../../sensors/core.py): expose only a validated `display_reason` on the existing Air
  Control Reason entity.
- `diagnostics.py`: publish schema/status/family/variant/attention/truncation/line-count
  metadata only, never rendered text or label-bearing arguments.
- [ui/cards/v2_mobile.yaml](../../ui/cards/v2_mobile.yaml), [ui/cards/v2_tablet.yaml](../../ui/cards/v2_tablet.yaml),
  [ui-gallery/default-v2-mobile-aq/card.yaml](../../ui-gallery/default-v2-mobile-aq/card.yaml), and
  [ui-gallery/default-v2-tablet-zone-2/card.yaml](../../ui-gallery/default-v2-tablet-zone-2/card.yaml): atomically replace the normal reason composer with exact-schema rendering and
  escaped legacy fallback.
- [ui-gallery/default-v2-mobile-aq/preview.png](../../ui-gallery/default-v2-mobile-aq/preview.png) and
  [ui-gallery/default-v2-tablet-zone-2/preview.png](../../ui-gallery/default-v2-tablet-zone-2/preview.png): deterministic browser captures using exact contract fixtures, the retained
  60-pixel scroll region, and the current passive Stability Score tile. These are
  documentation examples, not Phase 3 HA playback evidence.
- [ui/README.md](../../ui/README.md), [ui-gallery/README.md](../../ui-gallery/README.md), and both gallery example
  READMEs: document the sole-authority, fallback, Manual-card replacement,
  HA-managed dashboard, and cache/restart boundaries.
- `tests 2/test_reason_presentation.py`, engine/entity simulations,
  humidifier-reconciliation tests, diagnostics tests, and runtime-card sanity tests.
- `tests 2/test_reason_card_renderer.mjs`: execute valid, malformed, future-schema,
  Unicode-boundary, raw-ID, HTML-escaping, size-bound, and atomic-fallback behavior
  across all four V2 renderers. Run with
  `node "tests 2/test_reason_card_renderer.mjs"`; this command is a beta.2 release
  gate even before it is wired into repository CI.
- `manifest.json`, [CHANGELOG.md](../../CHANGELOG.md), [README.md](../../README.md), [ARCHITECTURE.md](../../ARCHITECTURE.md), release governance,
  and this proposal.
- [services.py](../../services.py), [__init__.py](../../__init__.py),
  [config_flow.py](../../config_flow.py), [helpers/cleanup.py](../../helpers/cleanup.py),
  [services.yaml](../../services.yaml), [strings.json](../../strings.json), and
  [translations/en.json](../../translations/en.json): retain the legacy
  service as a fail-safe, remove automatic creation/deletion, ignore old setup tokens,
  and describe the HA-managed Manual-card workflow.
- `tests 2/test_runtime_card_sanity.py` and `tests 2/test_config_flow_sanity.py`: prove
  authorization-before-guidance, zero dashboard side effects, legacy-token continuity,
  dashboard retention during cleanup, and removal of unsupported API references.

Worthwhile follow-ons, explicitly outside beta.2: localisation resources, a technical
details surface, any supported registered-dashboard document/registration lifecycle,
new presence policy configuration, or a breaking state replacement.

## Runtime, Entity, And Privacy Impact

- Runtime control impact: no lane-priority, threshold, timer, helper, output writer,
  or reconciliation change. One bounded presentation build is added after each final
  reason decision. The only service behavior change is the legacy `create_dashboard`
  safety deprecation and removal of dashboard deletion from cleanup.
- Deterministic lane-order risk: low. Structured trigger facts are collected beside
  the existing legacy detail strings and never feed selection. Failure-injection must
  prove service-call order and lane trace equivalence.
- Entity semantics: additive only. State, `full_reason`, `truncated`, and
  `humidifier_status` retain their current meaning. `display_reason` is optional and
  absent on validation/presentation failure.
- UI-truth risk: medium until all V2 template/gallery surfaces switch together. A
  partial card rollout would retain duplicate authorities; therefore the UI change is
  one atomic slice with mixed-version fallback.
- Privacy: local friendly names may appear in local state after sanitization, but raw
  entity IDs are prohibited in both rendered `text` and `args`. Diagnostics expose
  metadata only. Public fixtures and examples use canonical sanitized labels.
- HTML safety: contract text is plain bounded data. Cards must still escape at the
  HTML sink; validation is not a substitute for output escaping.

## Phase 2 Copy Amendment Provenance

Phase 1 approval remains attached to its frozen tracked patch
`08136cd51cdf95f2cfc48b3f42a5c9a2db8c3cfce3f2426b481db7f75b46a17a`
and untracked archive
`c3a73e30693e769d4567c9d50f12056fd016bbc79fcfba20da8a437c1a494696`.
Those hashes are retained and are not rewritten by this proposal.

Phase 2 preview review exposed one bounded post-Phase-1 copy defect: a singular
generic output summary produced `for configured … output` rather than the approved
`for the configured … output`. The amendment adds the definite article only when
`_presentation_output_summary` has exactly one unlabelled output. Plural summaries
and one/two friendly-name summaries remain unchanged. One exact regression covers
all four paths, and both gallery previews were regenerated afterward.

This amendment changes presentation text only. It does not change a lane, threshold,
service call, retry, reconciliation state, helper, timer, technical reason, entity
contract, generator, dashboard-registration path, migration, or restart boundary.
It is reviewed as part of Phase 2 rather than being hidden inside the original
Phase 1 approval. Bella subsequently approved the amended copy and previews.

## Phase 3 Dashboard Compatibility Fail-Safe Amendment

Phase 3 source inspection found that the legacy creation/deletion path called
module-level `dashboard.async_create_dashboard` and `dashboard.async_delete_dashboard`
functions that are absent from the official Home Assistant
[2026.5.1](https://github.com/home-assistant/core/blob/2026.5.1/homeassistant/components/lovelace/dashboard.py)
and [2026.5.4](https://github.com/home-assistant/core/blob/2026.5.4/homeassistant/components/lovelace/dashboard.py)
Lovelace dashboard source. It also wrote a card fragment beginning `type:` directly
to `/config/dashboards/`, while Home Assistant's documented
[dashboard view configuration](https://www.home-assistant.io/dashboards/views/) uses a
dashboard document rooted at `views:`. The prior test stubs invented those APIs and
therefore masked the defect.

The release-blocking correction is intentionally narrow:

- keep `humidity_intelligence.create_dashboard` registered and admin-gated for call
  compatibility, but return actionable Manual-card guidance before any mapping,
  rendering, Lovelace import, notification, config-entry lookup, or filesystem work;
- keep existing service fields accepted as ignored compatibility inputs;
- remove automatic dashboard creation from new config flow and treat an older stored
  `create_dashboard` token as one-time export-only input;
- leave legacy `ui_dashboard_id` data inert and unmodified;
- remove dashboard lookup/deletion and ownership claims from `purge_files` and config-
  entry removal; and
- do not replace the unsupported path with private storage mutation, an internal
  Lovelace collection, a synthetic WebSocket caller, or a custom panel.

This changes no control lane, reason fact, entity state, option schema, stored data, or
device output. It changes one legacy service from unsafe intended mutation to explicit
fail-safe guidance and requires a full Home Assistant restart after package replacement.
The generated/export boundary remains `refresh_ui` -> `view_cards` -> exact exported
path -> Home Assistant dashboard UI -> Manual card.

## Phased Implementation Plan

1. **Backend contract — complete at the frozen Phase 1 hashes.** Added and tested schema/validator,
   failure-isolated facts, entity publication, diagnostics metadata, beta.2 identity,
   and public architecture/release text without changing cards in that slice. Its
   original approval is preserved; the later singular-generic copy amendment is
   separately recorded and reviewed under Phase 2.
2. **V2 card authority cutover — implemented-diff review.** Replaced Mobile, Tablet,
   and matching gallery reason composers together. Exact `hi.reason.v1` rendering,
   atomic escaped legacy fallback, the existing scroll window, updated deterministic
   previews, executable renderer regression, and the bounded copy amendment are
   present. `greenNoise`, Stage, risk/timer/isolation duplication, and Engine
   composition are absent from the reason block.
3. **Generated/export boundary and compatibility fail-safe — implemented and offline-
   validated; final-diff review pending.** Fresh generation/export parity, Manual-card
   structure, exact-path discovery, cache-only refresh, compatibility-service zero-
   side-effect failure, legacy-token continuity, and file-only cleanup passed.
   Registered or YAML-mode dashboards remain unchanged and their lifecycle is deferred.
4. **Exact-commit supported-HA and HA Lab validation — pending.** Load the committed
   beta.2 package in the supported Home Assistant harness, restart, parse/save/load the
   Manual card, verify service guidance and frontend cache behavior, and run separately
   authorized advisory playback. Do not reuse beta.1 approval.
5. **Promotion review — pending.** Bella, Aetherwing, AetherCore, maintainer README approval,
   and exact-head release sanity remain mandatory before RC or stable promotion.

Each phase is independently reviewable and rollback-safe. Phase 1 acceptance was the
gate for Phase 2; Phase 3 offline export/fail-safe evidence is the local commit gate
and must not be inferred from static gallery captures. Phase 4 exact-commit HA Lab
playback remains separate.

## Validation Gates

Implementation acceptance requires:

- presenter-schema, enum, order, size, label, privacy, and deterministic-serialization
  tests;
- failure injection proving technical reason, mode, lane trace, helper/timer state,
  service-call payload/order, humidifier reconciliation, and retries are unchanged;
- normal, disabled, manual, pause, time/presence gates, presence unavailable,
  telemetry unavailable, Zone 1/2, AQ trigger/run-window, all alert families,
  conflicts, held/degraded/unmapped alerts, alert-only, CO, isolation, and all
  humidifier reconciliation states;
- absent, malformed, and future-schema card fallback;
- HTML-injection and raw-ID fixtures;
- V2 Mobile, Tablet, gallery, generated-export, and Manual fallback parity;
- exported bytes equal the rendered cache, parse as one `type:` card fragment rather
  than a `views:` dashboard document, and preserve single/multi-entry naming;
- admin-before-guidance and zero-side-effect `create_dashboard` behavior, ignored
  legacy first-run tokens, file-only purge/removal, and no unsupported Lovelace APIs or
  `/config/dashboards/` writes;
- compile/import, runtime/card, diagnostics, HACS layout, JSON/YAML, version
  governance, diff, and secret scans; and
- separately authorized HA Lab beta.2 playback against the exact commit/version.

Beta.1 evidence remains historical evidence for its exact humidifier scope. It is not
acceptance evidence for the beta.2 reason contract.

## Phase 2 Validation Record

The final Phase 2 working tree passed:

- 14 reason-presentation contract tests;
- 21 air-control simulations, including exact singular/plural/friendly-name output
  copy and presenter/fact-collection failure isolation;
- 26 humidifier-reconciliation tests;
- 18 diagnostics checks;
- 109 runtime/generated-card checks;
- 20 Inspector JavaScript checks and seven executable V2 reason-renderer checks;
- JSON and YAML parsing, Python compile, proposal-link validation, version
  governance, `git diff --check`, and the repository secret scan.

The full direct test sweep also passed every other runnable suite. The tracked
`test_hi_memory_usage_auditor.py` could not start because its ignored-local source
`scripts/local/hi_memory_usage_auditor.py` is absent from this worktree. That known
local continuity boundary is unrelated to the Phase 2 diff and is recorded as an
explicit exclusion, not reported as a pass.

These are offline/static Phase 2 checks. They do not satisfy Phase 3 fresh export,
Manual-card artifact, compatibility fail-safe, browser-cache, restart, or HA Lab
playback gates.

## Phase 3 Offline Validation Record

The Phase 3 review candidate passed every runnable direct repository suite, including:

- 21 air-control simulations, 26 humidifier-reconciliation checks, 14 reason-
  presentation checks, 18 diagnostics checks, and 109 runtime/card checks;
- 40 config-flow, 31 report-export, 13 local-version, five setup-assist, four slope,
  35 issue-triage, 10 Pages, 22 Inspector Python, and 20 Inspector JavaScript checks;
- seven executable V2 reason-renderer checks, six proposal-link checks, five
  documentation-banner tests, eight version-governance tests, and six workflow tests;
- real sanitized V2 generation followed by owned single-entry export with byte-for-
  byte cache parity; the exported artifact starts with `type: custom:mod-card`, has no
  top-level `views:`, and retains no card-authored `Stage:` or `Engine:` reason voice;
- non-admin rejection, exact admin guidance, arbitrary legacy service-field
  acceptance, zero config-entry/mapping/render/Lovelace/notification/filesystem side
  effects, ignored legacy setup selection, no retry loop, inert legacy dashboard ID,
  and file-only purge/removal behavior;
- Python compile, seven tracked JSON files, 30 tracked YAML syntax trees, HACS root
  layout/manifest keys, version governance, proposal links, `git diff --check`, the
  tracked Gitleaks scan, and a dashboard compatibility source guard.

The tracked memory-auditor test remains non-runnable because its ignored-local source
`scripts/local/hi_memory_usage_auditor.py` is absent from this worktree. This is an
unchanged local continuity exclusion, not a Phase 3 pass. The local environment also
lacks Home Assistant/PyYAML test dependencies, so supported-HA loader acceptance,
frontend save/load, full restart, browser cache behavior, and live Manual-card
playback remain explicit Phase 4 HA Lab gates. No Home Assistant instance or dashboard
was mutated during Phase 3.

The Phase 3 delta from the frozen Phase 2 artifact contains only the authorized
compatibility runtime, service/config-flow/translation, Manual-card banner,
documentation/proposal, and regression files. The review candidate is frozen at
tracked patch `ced86d8d377ad64a2e4f427d5341d55591fb0f8ea5ec55c030de0f97642b2869`
and untracked archive `45f1dcc62bec051b9a61e1a001d3bb019cb56febb1ab2c7f743897cea2bd3039`
before this validation record was appended. Subsequent edits are limited to this
validation/status record and the four ignored-field descriptions in `services.yaml`;
they change no runtime code, schema acceptance, renderer, export, or cleanup behavior.
The final staged tree receives a separate post-review hash outside the self-referential
proposal content.

## Home Assistant Lab Playback Expectations

Against the exact beta.2 commit/version, capture sanitized evidence for calm normal,
disabled, manual, pause, time gate, confirmed-away presence, unavailable presence,
telemetry loss/recovery, Zone 1/2, AQ trigger and retained run window, actionable and
unmapped/degraded alerts, alert conflict/hold, CO trigger and clear hold, fan and
humidifier isolation, and every humidifier reconciliation state. Verify:

- sensor state and legacy attributes remain available;
- `display_reason` is valid, below 4 KiB, at most eight lines, and contains no raw ID;
- Mobile and Tablet show the same ordered text and preserve scrolling;
- presentation failure or unsupported schema falls back atomically;
- service calls, helper/timer truth, reconciliation, and deterministic lane order
  match the control baseline; and
- restart/import and frontend/dashboard cache behavior match the documented boundary.

HA Lab playback is advisory evidence only and requires separate operational
authorization. It does not authorize restart, dashboard mutation, output writes,
promotion, tag, or release.

## Release And Version Recommendation

Use `2.0.10-beta.2`. The work extends the already-unreleased 2.0.10 humidifier truth
model and is compatible by construction, but it is broad enough to invalidate
beta.1 UI/reason evidence. A new beta makes that evidence boundary explicit without
pretending the additive attribute is a stable patch.

Do not move this to v2.1 merely because presentation is substantial: beta.2 keeps the
existing state contract. Reserve v2.1 for the future breaking replacement, removal,
or reinterpretation of that state and its migration path. Use v2.0.11 only if the
2.0.10 line is promoted before this complete change can be validated; that is a
release-timing fallback, not the preferred design boundary.

## House-Agent Cross-Review Record

- **Aetherbite — `APPROVE_PHASE1`.** Led the calm, domestic copy model and required
  evidence-first wording, target six/hard eight lines, and separation of humidifier
  demand, mapping, dispatch, observation, failure, and physical-output truth.
  Challenge: generic degraded wording collapsed unavailable humidity, absent output
  mapping, and reconciliation failure. Resolution: each now has a distinct truthful
  sentence and regression coverage; the final copy/density review passed.
- **Bella — `APPROVE_PHASE1`.** Required the exact schema sentinel, canonical
  validator, backend-owned truth, metadata-only diagnostics, label precedence, and
  the raw-ID prohibition. Challenge: the new degraded humidifier branches could have
  converted unavailable demand evidence into output-failure language. Resolution:
  telemetry loss is `unavailable`, missing mapping is `blocked`, and neither claims
  dispatch, observation, or physical action.
- **Aetherwing — `APPROVE_PHASE1`.** Required immutable facts, failure isolation for
  fact collection and serialization, structured trigger parity, and unchanged
  service/lane traces. Challenge: presenter failure could have altered real
  humidifier dispatch, retry scheduling, reconciliation, helper state, or technical
  reason. Resolution: full-cycle baseline/failure playback proved those surfaces
  identical while only `display_reason` was withheld.
- **AetherCore — `APPROVE_PHASE1`.** Found the proposal bounded and maintainable with
  beta.2 evidence reset and backend/card changes kept as separate review slices.
  Challenge: stale working-tree line anchors could not prove the stated baseline.
  Resolution: the diagnosis now uses commit-pinned `cb46c19b` source anchors and the
  proposal-link check passes.

Phase 2 received a separate cross-review:

- **Aetherbite — `APPROVE_PHASE2`.** Required exact backend sentences without
  frontend `Why:`/`Action:` labels and accepted the headline-first 60-pixel scroll
  hierarchy. Challenge: deterministic preview review exposed the missing definite
  article in singular generic output copy. Resolution: `for the configured … output`
  is now backend-owned; plural and friendly-name paths are regression-tested and the
  previews were regenerated.
- **Bella — `APPROVE_PHASE2`.** Approved the strict exact-key/enums/bounds/privacy
  contract, opaque backend text, escaped atomic fallback, V1 isolation, and backend-
  owned truth. Challenge: static assertions cannot replace executable malformed-
  contract, Unicode, escaping, and fallback coverage. Resolution: the seven-case Node
  renderer suite is a documented beta.2 release gate. Bella later explicitly approved
  the definite-article amendment, corrected previews, and final contract.
- **Aetherwing — `APPROVE_PHASE2`.** Initially returned `CHANGES_REQUIRED` because a
  stale humidifier assertion still expected retired card-authored copy and both
  previews showed an obsolete Pause tile plus invented/omitted backend sentences.
  Resolution: the assertion now protects sole backend authority; deterministic
  captures use exact possible presenter output, the passive Stability Score tile,
  and the real 60-pixel scroll boundary. Final review found no lane, service,
  compatibility, privacy, migration, or UI-truth blocker.
- **AetherCore — `APPROVE_PHASE2` and `APPROVE_PHASE2_COPY_AMENDMENT`.** Required the
  exact Phase 2 artifact list, stage-accurate proposal status, and preservation of
  Phase 1 provenance after the copy fix. Resolution: the original Phase 1 hashes are
  retained; the two-line presentation-only amendment and its four-path regression
  are recorded separately; Phase 3 remains not run.

Phase 3 received independent review before amendment work:

- **Aetherbite — `CHANGES_REQUIRED`, then amendment direction approved.** Challenge:
  a creation-only fix would leave deletion and false ownership claims live. Resolution:
  both paths are neutralized; exact guidance distinguishes new dashboard, existing
  Manual card, and deferred registered/YAML-mode dashboard workflows.
- **Bella — `APPROVE_COMPATIBILITY_CORRECTION / PHASE3_REGISTERED_DASHBOARD_SCOPE_DEFERRED`.**
  Challenge: legacy `ui_dashboard_id` cannot prove ownership. Resolution: it is inert;
  no migration, preview, lookup, or deletion uses it.
- **Aetherwing — `CHANGES_REQUIRED_PHASE3_COMPATIBILITY`.** Challenge: official Home
  Assistant source lacks the stubbed module APIs and the exported `type:` card is not a
  `views:` dashboard document. Resolution: the unsupported write/delete path is removed
  rather than replaced with private API access; generated/export and Manual-card
  validation remain in scope.
- **AetherCore — `APPROVE_AMENDMENT_SCOPE`.** Found the correction bounded and
  maintainable for undistributed beta.2. Challenge: a reason rollback must not restore
  the unsafe dashboard paths. Resolution: rollback retains this fail-safe or uses a
  separately governed safe build.

Fresh final implemented-diff verdicts are recorded:

- **Aetherbite — `APPROVE_PHASE3_FINAL`.** Confirmed all compatibility fields and
  Manual-card copy are truthful and no ignored value implies dashboard work.
- **Bella — `APPROVE_PHASE3_FINAL`.** Confirmed backend reason authority, inert legacy
  IDs, service/cleanup truth, and explicit runtime-impact metadata.
- **Aetherwing — `APPROVE_PHASE3_FINAL`.** Confirmed the unsupported APIs and dashboard
  write are absent, the export is a byte-identical card fragment, and runtime/entity/
  lane semantics remain unchanged.
- **AetherCore — `APPROVE_PHASE3_FINAL`.** Confirmed the bounded beta.2 lifecycle,
  passing live proposal-link gate, explicit post-candidate provenance, validation
  exclusions, rollback safety, and local-commit-only authority.

All four approvals cover the reviewed tree plus this mechanical verdict/status
bookkeeping. Any later behavioral change requires renewed review.

There is no unresolved product or runtime disagreement. The accepted density trade-off is
that a long action sentence can begin below the tablet's initial 60-pixel fold; it
remains keyboard/touch scrollable and the UI does not summarize or reconstruct it.
Phase 3 registered/YAML-mode dashboard mutation is explicitly deferred, not treated as
successful validation. Separately authorized exact-commit HA Lab playback remains
required before beta.2 can be released.

## Maintainer Decisions

Jules has approved every design decision needed to begin implementation:

- additive `display_reason` authority and exact schema/bounds;
- `requested` service-layer definition;
- label precedence and absolute raw-ID prohibition;
- calm neutral visibility and no beta.2 technical expander;
- HA-managed dashboard creation plus whole-card replacement for existing HI Manual
  cards, with registered/YAML-mode dashboard lifecycle deferred;
- degraded fail-closed unavailable-presence presentation; and
- beta.2 placement with v2.1 reserved for a breaking reason-state replacement.

No additional product decision is required for Phase 1, Phase 2, or the bounded Phase
3 compatibility amendment. Phase 3 offline validation and a local commit are
authorized. HA Lab playback, Home Assistant restart or mutation, push, PR, promotion,
tag, and release remain separate authorities. Before release promotion, Jules must
accept the exact final evidence and release boundary.

## Rollback

Rollback remains migration-free:

- an old card ignores `display_reason`;
- a new card falls back when the backend lacks it;
- presenter failure removes the current-cycle attribute and preserves the technical
  reason; and
- no entity, registry, stored-data, or service cleanup is required.

Before any beta.2 package is distributed, a full feature rollback must restore the
beta.1 manifest identity, README, changelog, release-governance wording, and generated
Inspector fixtures in the same reviewed change. After beta.2 has been deployed or
distributed, do not silently reuse beta.1 identity; publish a newly governed build or
an explicitly documented rollback package.

The dashboard compatibility fail-safe is not reverted independently with reason
humanisation. Restoring the former beta.1 tree wholesale would re-enable unsupported
creation/deletion and unsafe card-fragment writes. Any rollback build must retain this
correction or replace it with a separately approved supported lifecycle.

## Explicit Deferrals

- breaking replacement or reinterpretation of the reason state;
- removal of `full_reason` or `humidifier_status`;
- new reason entities, helpers, services, or configuration options;
- localisation runtime or per-user frontend translation;
- technical-details expander;
- V1 redesign/removal;
- registered/YAML-mode dashboard document generation, registration, replacement,
  deletion, or automatic refresh;
- presence unknown-policy configuration;
- cooking/bathroom minimum-runtime implementation; and
- unrelated engine or Current Air Control layout refactoring.

Any future breaking reason-state replacement remains a v2.1-boundary decision that
requires a separately approved proposal and migration contract.

## Final Status

`REVIEW_REQUIRED — PHASE3_OFFLINE_VALIDATED / LOCAL_COMMIT_READY / HA_LAB_REQUIRED`

Phase 1 and Phase 2 implemented diffs are approved by all four roles. Phase 3's
generated/export and dashboard compatibility correction is implemented in the working
tree and has passed the complete runnable offline gate; fresh four-role final-diff
verdicts approve the local commit. HA Lab playback, push, PR, and release promotion
remain pending and are not authorized by this phase.
