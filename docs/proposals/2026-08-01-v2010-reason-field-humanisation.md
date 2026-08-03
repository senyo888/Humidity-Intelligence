# Humidity Intelligence Reason Field Humanisation — House-Agent Implementation Proposal

## Metadata

```yaml
proposal_id: HI-PROP-20260801-001
proposal_urn: urn:hi:proposal:20260801:001:v2010-reason-field-humanisation
title: Humidity Intelligence Reason Field Humanisation
created: 2026-08-01
category: runtime-ui-contract
target_version: v2.0.10
implementation_version: 2.0.10-beta.5
current_candidate_version: 2.0.10-beta.5
current_candidate_manifest_status: exact_local_identity_authorized
authority_status: implementation_and_ha_lab_validation_authorized
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
phase3_local_commit_status: committed_historical
beta3_amendment_status: local_implementation_approved_all_four_roles
beta3_local_commit_series: package_layout_coderabbit_reason_copy_hacs_brand_repair
beta3_package_layout: custom_components/humidity_intelligence
beta3_hacs_content_in_root: removed
beta3_hacs_brand_layout: custom_components/humidity_intelligence/brand
beta3_hacs_brand_repair_review: approved_all_four_roles
beta3_hacs_run_30712596944: failed_brand_path_at_50cf630
beta3_hassfest_run_30712596947: passed_at_50cf630
beta3_version_governance_run_30712596942: passed_at_50cf630
beta3_humidifier_response_model: self_contained_backend_lines
beta3_coderabbit_docstring_check: disabled_config_only
beta2_soak_status: superseded_incomplete_historical_evidence
external_actions_authorized: false
beta3_implemented_diff_review: approved_all_four_roles
aetherbite_beta3_review: approved
bella_beta3_review: approved
aetherwing_beta3_review: approved
aethercore_beta3_review: approved
beta3_ha_lab_status: superseded_incomplete_historical_evidence
beta4_amendment: alert-lane-headlines-and-severity-language
beta4_implementation_status: committed_exact_deployed
beta4_implemented_diff_review: approved_all_four_roles
aetherbite_beta4_review: approve_beta4_copy
bella_beta4_review: approve_beta4_local_commit
aetherwing_beta4_review: approve_beta4_local_commit
aethercore_beta4_review: no_governance_objection_appropriately_bounded
beta4_ha_lab_status: exact_deployment_stage_b3_t0_pass_playback_pending
beta4_soak_status: historical_proposal_checkpoint_1_of_9_current_state_not_assessed
beta4_exact_head_validation: passed
beta5_amendment: current-air-control-status-chip-clarity
beta5_implementation_status: exact_local_candidate_validated_pending_commit
beta5_implemented_diff_review: approved_all_four_roles_exact_identity
beta5_aetherbite_review: approve_status_chip_candidate_for_local_closeout
beta5_bella_review: approve_local_working_tree
beta5_aetherwing_review: approve_local_ui_diff_release_blocked_pending_exact_identity_and_live_playback
beta5_aethercore_review: no_governance_objection_appropriately_bounded_and_maintainable
beta5_identity_aetherbite_review: approve_mechanical_identity_and_copy_for_local_commit
beta5_identity_bella_review: approve_exact_local_commit_readiness
beta5_identity_aetherwing_review: approve_exact_local_commit_after_proposal_link_fix
beta5_identity_aethercore_review: approve_exact_local_commit_after_scope_bookkeeping
beta5_ha_lab_status: pending_exact_remote_ref_and_controller_deploy
beta5_soak_status: not_started
beta5_mobile_tablet_playback: authorized_pending_exact_deployment
beta5_review_base_head: fad159e3b2f91e5407e06d2407a51bcaf3c5e410
beta5_manifest_identity: 2.0.10-beta.5
beta5_candidate_identity: 2.0.10-beta.5
beta5_version_bump_authorized: true
beta5_runtime_control_changed: false
beta5_entity_contract_changed: false
beta5_card_presentation_changed: true
beta5_generated_templates_changed: true
beta5_manual_card_replacement_required: true
beta5_config_migration_required: false
beta5_external_actions_authorized: ha_lab_deploy_restart_manual_card_playback_and_soak_only
beta5_gallery_preview_status: unchanged_not_beta5_visual_evidence
beta5_review_scope_file_count: 15
beta5_non_proposal_patch_sha256: 14715e505501bd4d17322191323ed0dee226107649d380f5b708de8cf056cb83
phase3_review_candidate_tracked_patch_sha256: ced86d8d377ad64a2e4f427d5341d55591fb0f8ea5ec55c030de0f97642b2869
phase3_review_candidate_untracked_tar_sha256: 45f1dcc62bec051b9a61e1a001d3bb019cb56febb1ab2c7f743897cea2bd3039
phase3_post_candidate_edits: validation-status-record-plus-ignored-service-field-copy
registered_dashboard_validation: deferred_unsupported_path_removed
ha_lab_validated: beta4_stage_b3_t0_pass_beta5_pending_exact_remote_ref
release_candidate_validated: beta5_local_pass_external_ci_and_live_evidence_pending
implemented_in: pending_exact_local_git_commit_from_this_reviewed_tree
cumulative_entity_contract_changed: true
cumulative_entity_contract_change: additive-versioned-attribute
service_contract_changed: true
service_contract_change: create_dashboard_guidance_only_fail_safe
config_flow_choice_changed: true
config_schema_changed: false
stored_data_changed: false
legacy_create_dashboard_token: ignored_export_only
dashboard_delete_ownership: removed
lane_order_risk: low
ui_truth_risk: low_after_static_beta5_renderer_validation_live_mobile_tablet_playback_pending
stable_runtime_risk: low_unreleased_beta5_exact_head_and_live_playback_pending
breaking_reason_state_replacement: deferred_requires_separate_v2_1_proposal
```

## Executive Recommendation And Feasibility

**Verdict: feasible with low control risk and low residual UI-truth risk after the
atomic card cutover.** The additive backend-owned `display_reason` attribute is now
implemented on the existing reason sensor before beta.5; the technical state is
retained as a compatibility and diagnostic surface, and the new attribute remains the
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

**Status: `REVIEW_REQUIRED`.** Phase 1, Phase 2, and the bounded Phase 3 dashboard
compatibility fail-safe are approved historical implementation slices. Beta.3
established the conventional package boundary, CodeRabbit configuration,
self-contained humidifier wording, and component-local brand repair. Its incomplete
HA Lab soak is preserved as superseded historical evidence. Beta.4 added the
backend-owned alert-language catalogue and has exact-head CI, package deployment, one
full restart, Stage B, Stage 3, and T+0 evidence; the last proposal-local soak record
is 1/9 and must not be presented as current without a fresh operational check.

The current working tree adds a beta.5-candidate V2 status-chip refinement. Humidity
Danger chips omit only their trailing measurement/threshold segment, humidifier chips
use self-identifying labels and concise Home Assistant-observed `On` wording, and an
active Zone 1/2 lane plus humidifier telemetry renders as two independently scrollable
status groups. This changes no backend reason, alert telemetry, entity semantics,
lane order, service dispatch, configuration, or stored data. The maintainer has now
authorized the exact `2.0.10-beta.5` manifest identity, local commit, HA Lab package
deployment/restart, lab-only Manual-card replacement, Mobile/Tablet playback, and a
fresh soak. Beta.4 deployment, playback, and soak evidence do not validate beta.5.
Push remains unauthorized, and the governed controller cannot deploy beta.5 until the
exact local commit is available through its allowlisted remote Patch 1 profile. PR
activity, promotion, tag, release, Stable access, and output writes remain blocked.

## Beta.3 Approved Amendment

The maintainer reset the current beta boundary to `2.0.10-beta.3` for three bounded,
separately reviewable corrections:

1. move the exact installable integration payload to
   `custom_components/humidity_intelligence/`, remove HACS `content_in_root`, and
   validate the tracked package directly;
2. make every material humidifier explanation independently recognizable as
   `Humidifier response — {resolved label}: ...`, including when AQ, a zone, a gate,
   or safety truth owns the dynamic headline; and
3. disable only CodeRabbit's generic docstring-coverage pre-merge check instead of
   adding low-value bulk docstrings to established code.

The HACS layout change is a repository-admission requirement for the active HACS
review. It does not change the installed Home Assistant destination, integration
domain, entity registry, config schema, stored data, service semantics, lane order,
or generated-card bytes. The package contains the same 52 installable files; repo-only
documentation, tests, scripts, gallery examples, site, and legacy material stay
outside the installed component. The two existing component-root brand images move,
byte-for-byte, into Home Assistant's supported component-local `brand/` directory.
This preserves the 52-file count and payload content but intentionally changes those
two relative paths. The repository-root brand pair remains the authoring source, and
the component pair is its parity-checked release/install mirror.

At `50cf630`, version-governance run `30712596942` and Hassfest run `30712596947`
passed, while HACS run `30712596944` failed only because
`custom_components/humidity_intelligence/brand/icon.png` was absent. The house-agent
cross-review rejected a 54-file duplicate component. Bella and Aetherbite preferred
deleting the repository-root mirror; Aetherwing and AetherCore preferred retaining it
for this bounded correction. The reconciled decision keeps it without treating it as
installed truth and enforces byte parity in validation.

The humidifier amendment is presentation-only. Configured HI level labels remain
authoritative, with the existing safe fallback labels used only when no configured
label is available. Each material line owns its context because the bounded presenter
may retain or omit lines independently. A long configured label may therefore split
one environmental statement and one response statement, with both lines repeating
the same `Humidifier response — {label}:` prefix and both remaining within the
200-character line cap. This uses the existing scrollable reason window; it adds no
frontend-authored heading, card condition, schema field, or layout dependency.

The `requested` truth definition is unchanged: it is emitted only when the recorded
dispatch evidence proves that HI handed the service request to Home Assistant without
an immediate exception. Failed or absent dispatch must never say `HI sent`. Observed
on/platform-idle copy folds the physical-moisture caveat into the same response line;
inactive isolation continues to use the single existing global isolation notice.
Existing reconciliation evidence that proves an unsupported/missing service blocks
dispatch is presented as `blocked`; missing, unknown, or unavailable output-state
evidence is `unavailable`. Both state plainly that HI did not send the request.

The incomplete beta.2 soak for exact commit `0d942efe` is preserved as historical
beta.2 evidence and marked superseded, not failed or transferred. Beta.3 later
received separate HA Lab deployment/restart authority; its incomplete soak is now
historical and superseded by beta.4. No beta.2 or beta.3 evidence transfers to later
candidates. No release, PR reply, re-review request, or promotion is authorized by
this amendment.

## Beta.4 Alert-Language Amendment

The maintainer approved a bounded catalogue refinement after beta.3 entered HA Lab
soak. A selected lane must be explicit in the headline, while the first explanation
sentence must identify the alert classification in plain language:

- zone and air-quality headlines use `{friendly label} response lane selected` and
  `Air quality response lane selected`;
- humidity uses `High humidity alert lane selected`, followed by `Danger alert:` and
  the active seasonal high-risk threshold;
- mould uses `Mould alert lane selected`, followed by `Risk alert:` or `Danger alert:`;
- condensation uses `Condensation alert lane selected`, followed by `Risk alert:` or
  `Danger alert:`; and
- CO keeps its unsoftened safety identity as `Carbon monoxide emergency lane selected`.

Room, zone, level, and output names remain backend-resolved, sanitized labels. Visible
mould prose translates the internal ordinal into Normal, Watch, Risk, or Danger. It
does not expose phrases such as `level is 2`; the existing bounded numeric
`measured`/`threshold` arguments remain unchanged for deterministic traceability and
future localisation. Watch is descriptive environmental context only and does not
add or reorder an alert lane. Alert source, selected-output, held-selection,
conflict-resolution, unmapped, degraded, and isolation lines use the same calm,
direct voice without weakening safety truth.

For high humidity, threshold resolution retains the target-profile label as one
private presentation fact on the same internal alert snapshot. The presenter does not
resolve the profile again after awaited output work, and the private fact is filtered
before `alert_telemetry` publication; profile wording therefore cannot cross a month
boundary or widen the public telemetry shape.

This amendment changes only backend presentation strings, the manifest beta identity,
documentation, and exact regression fixtures. It does not change `hi.reason.v1`,
reason entity state, `full_reason`, alert thresholds, risk calculation, lane
resolution, output selection, or service dispatch. Entity identity, state, schema,
and structured truth semantics are unchanged; backend presentation text changes
intentionally. Card YAML, config, and stored data remain unchanged. Beta.3 remains an
immutable historical deployed evidence identity. Beta.4 exact-head CI, package
deployment, restart, Stage B, Stage 3, and T+0 have passed; controlled alert scenario
playback and completion of the exact beta.4 soak remain required before promotion.

## Beta.5 Current Air Control Status-Chip Amendment

The maintainer approved a bounded presentation correction after beta.4 deployment:

- shorten only Humidity Danger companion chips by removing their trailing
  `measurement >= threshold` segment while retaining `Humidity Danger`, the resolved
  room, and the mapped zone when present;
- keep the complete `active_alert_context`, structured `alert_telemetry`, and
  backend-owned humanised reason unchanged;
- name humidifier chips `Downstairs Humidifier` and `Upstairs Humidifier` so the
  telemetry family is clear without relying on positional context;
- render backend reconciliation state `output_on` as `On`, meaning Home Assistant has
  observed the configured output on, not that the device accepted a request or is
  physically producing moisture; and
- when Zone 1 or Zone 2 and humidifier telemetry are active together, render separate
  independently scrollable `Ventilation status` and `Humidifier status` groups. Each
  group has an accessibility label and every humidifier chip remains visually
  self-identifying. Other runtime modes retain one `Current Air Control status` row.

The shortening rule is explicitly gated to `Humidity Danger`; other present or future
alert contexts remain verbatim even if their text contains comparison syntax. The
four canonical V2 surfaces—Mobile, Tablet, and both matching gallery cards—carry one
identical status renderer. The change is frontend presentation only: it does not
modify the reason presenter, entity state or attributes, alert resolution, thresholds,
lane selection, output selection, dispatch/reconciliation, timers, configuration, or
stored data.

The next release identity is `2.0.10-beta.5` because beta.4 already has exact
deployment evidence and must not be overwritten. The manifest has been advanced under
explicit maintainer authority. Existing pasted Manual cards remain static and require
`refresh_ui`, then `dump_cards` or `view_cards`,
followed by complete YAML replacement in the existing HI Manual card. Public package
installation or rollback follows the normal full Home Assistant restart boundary;
there is no config, options, registry, helper, or stored-data migration.

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
- no technical-details expander through beta.5;
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
| Zone 1/2 | `Trigger detail: Humidity delta 8.2% >= threshold 6%` | **Bathroom response lane selected.** “Humidity is 8.2 percentage points above the home average; response starts at a difference of 6 percentage points.” The leading text is the configured friendly zone label, not a hard-coded room. |
| AQ trigger | `Stage: Air-quality assist running` plus operators | **Air quality response lane selected.** “Downstairs: PM2.5 is 48 µg/m³, at or above the 25 µg/m³ threshold.” |
| AQ run window | Same as an active trigger | **Air quality response lane selected.** “Downstairs AQ run window remains active after the latest trigger.” Do not claim the trigger is still active. |
| High humidity alert | `Stage: Alert lane active` plus source IDs/details | **High humidity alert lane selected.** “Danger alert: humidity in Bathroom is 68.0%, at or above the high-risk threshold of 66% for the active Summer profile.” “Bathroom is assigned to Zone 2 for this response.” |
| Mould risk alert | `Mould risk level is 2, at or above the 2 risk threshold` | **Mould alert lane selected.** “Risk alert: mould conditions in Bathroom have reached the Risk range for the Summer profile.” |
| Mould risk crossed into danger | Numeric ordinal comparison | **Mould alert lane selected.** “Risk alert: mould conditions in Bathroom are in the Danger range for the Summer profile; this response starts at Risk.” |
| Mould danger alert | Numeric ordinal comparison | **Mould alert lane selected.** “Danger alert: mould conditions in Bathroom have reached the Danger range for the Summer profile.” |
| Condensation risk/danger | Raw spread and internal lane terms | **Condensation alert lane selected.** “Risk alert: the dew-point gap in Bathroom is 3.0°C, at or below the Summer Risk point of 4°C.” Use `Danger alert:` and `Danger point` for the danger lane. |
| Alert conflict/hold | Internal priority detail | “HI selected this alert using the fixed alert and zone priority order.” or “This alert remains selected until it clears.” |
| Unmapped/degraded alert | Long degraded notice, sometimes repeated | **Monitoring with limited alert response** (`attention: degraded`). “Another active alert has no usable zone-output mapping, so HI did not select an automatic boost for it.” |
| CO emergency | “forced to 100%” even when isolation can suppress calls | **Carbon monoxide emergency lane selected.** State the highest reading and threshold; then `selected`, `blocked`, or `unmapped` output truth. State the two-minute below-clear-threshold hold. |
| Fan isolation | Repeated suffix and card stage | “Fan-output isolation is active; fan service calls are suppressed.” Once only. |
| Humidifier demand | Demand and device action can blur | “Humidifier response — Upstairs: Winter profile: demand is active at 51.4%; start 54.0%, stop 55.0%.” |
| Humidifier dispatch | Often described as output activity | “Humidifier response — Upstairs: HI sent the output-on request to Home Assistant; confirmation is pending.” `requested` means proved HA service-layer dispatch only. |
| Humidifier observed on | Broad active wording plus a detached caveat | “Humidifier response — Upstairs: Home Assistant reports the output on and humidifying; moisture output is not measured.” |
| Platform idle disagreement | Can be hidden by `idle` suppression | “Humidifier response — Upstairs: Home Assistant reports the output on but its humidifier action is idle; moisture output is not measured.” |
| Retry/fault/degraded | Technical reconciliation terms | “Humidifier response — Upstairs: A Home Assistant output-on service call failed; a bounded retry is active.” / “Humidifier response — Upstairs: HI exhausted its bounded confirmation attempts; output activity is not confirmed.” / “Humidifier response — Upstairs: HI cannot confirm how the humidifier output responded.” |
| Stop confirmation | Demand-off can look complete | “Humidifier response — Upstairs: Humidification demand is inactive. HI sent the output-off request to Home Assistant; confirmation is pending.” |

## Architecture Options Considered

| Option | Advantages | Costs and risks | Decision |
| --- | --- | --- | --- |
| Rewrite the existing reason state | Smallest apparent entity surface; new cards read state directly | Breaking for automations, templates, support tooling, state-length handling, and mixed-version cards; removes technical fallback | Reject for v2.0.x; reserve for v2.1 governance |
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
  headline: Zone 1 response lane selected
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

The current fail-closed control effect is preserved through beta.4, but unavailable-only
evidence must not be presented as confirmed absence:

- any configured source reports present: the gate passes;
- every usable configured source explicitly reports away: `presence_away`;
- no source reports present and at least one source is missing, unknown, or
  unavailable: `presence_unavailable` with `attention: degraded`;
- both blocking outcomes keep the current gate effect; and
- CO emergency continues to bypass the gate.

No cached last-known presence state or new configurable unknown policy is introduced
in beta.4.

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
- For beta.5 specifically, replacing only the complete Manual-card YAML does not
  require a backend restart or config-entry reload. After saving the card, reload the
  frontend or hard-refresh only if stale content remains.
- Installing or rolling back a versioned beta.5 package requires the normal full Home
  Assistant restart so the running integration and generated templates share the
  exact package identity. Export generation and Manual-card save are separate writes
  requiring their own operational authority.
- No config/options schema, stored data, entity registry, or helper migration is
  introduced. Legacy `create_dashboard` selections and `ui_dashboard_id` values remain
  inert without rewrite or retry loops.
- No new frontend dependency is introduced.

## Exact Implementation Scope

Beta.5-only tracked delta:

- [v2_mobile.yaml](../../custom_components/humidity_intelligence/ui/cards/v2_mobile.yaml)
  and [v2_tablet.yaml](../../custom_components/humidity_intelligence/ui/cards/v2_tablet.yaml):
  concise Humidity Danger and humidifier chip presentation plus deterministic split
  status groups;
- [mobile gallery YAML](../../ui-gallery/default-v2-mobile-aq/card.yaml) and
  [tablet gallery YAML](../../ui-gallery/default-v2-tablet-zone-2/card.yaml): exact
  renderer parity with the canonical generated-card templates;
- [test_reason_card_renderer.mjs](<../../tests 2/test_reason_card_renderer.mjs>),
  [test_runtime_card_sanity.py](<../../tests 2/test_runtime_card_sanity.py>), and
  [test_humidifier_reconciliation.py](<../../tests 2/test_humidifier_reconciliation.py>):
  executable renderer parity, humidity-only truncation, non-humidity preservation,
  split/single-row behavior, and concise observed-state assertions; and
- [CHANGELOG.md](../../CHANGELOG.md),
  [manifest.json](../../custom_components/humidity_intelligence/manifest.json),
  [release-governance.md](../release-governance.md), component UI guidance, support
  guidance, gallery guidance, and this proposal: exact user refresh, truth, restart,
  migration, version identity, evidence transfer, and live playback boundaries; and
- [README.md](../../README.md): public chip terminology aligned to concise `On` while
  retaining backend `output_on` and the no-physical-moisture-production boundary.

There is no beta.5 Python runtime, reason contract, entity, diagnostics schema,
service, config-flow, translation, stored-data, or output-control change.

Essential beta.4 scope, including the completed beta.2 and beta.3 reason slices:

Beta.4-only tracked delta:

- [automations/engine.py](../../custom_components/humidity_intelligence/automations/engine.py): presentation-only family headlines, severity-first alert
  prose, human mould ranges, sanitized bounded labels, exact threshold-profile
  provenance, and no shared alert-telemetry shape change;
- [manifest.json](../../custom_components/humidity_intelligence/manifest.json),
  [CHANGELOG.md](../../CHANGELOG.md), [README.md](../../README.md),
  [release-governance.md](../release-governance.md), and this proposal: beta.4
  identity, restart/cache/migration truth, evidence reset, rollback, and wording
  catalogue; and
- the air-control, runtime-card, humidifier, reason-contract, diagnostics, and
  JavaScript renderer fixtures: exact family/severity/Watch/fallback/label/privacy and
  invariance coverage.

There is no beta.4 card YAML, gallery, sensor, diagnostics-schema, service,
config-flow, translation, configuration, or stored-data change. The remaining list
below preserves the cumulative reason-experience implementation history rather than
claiming those historical files changed again in beta.4.

- [custom_components/humidity_intelligence/helpers/reason_presentation.py](../../custom_components/humidity_intelligence/helpers/reason_presentation.py):
  frozen fact/line types, exact schema builder,
  validator, bounds, label sanitizer, raw-ID prohibition, and privacy-safe diagnostic
  metadata.
- [custom_components/humidity_intelligence/automations/engine.py](../../custom_components/humidity_intelligence/automations/engine.py):
  structured gate/trigger facts and final-cycle presentation
  factories for every approved runtime family. Presentation collection and validation
  stay inside a failure-isolated publication boundary.
- [custom_components/humidity_intelligence/sensors/core.py](../../custom_components/humidity_intelligence/sensors/core.py):
  expose only a validated `display_reason` on the existing Air
  Control Reason entity.
- `custom_components/humidity_intelligence/diagnostics.py`: publish
  schema/status/family/variant/attention/truncation/line-count
  metadata only, never rendered text or label-bearing arguments.
- [custom_components/humidity_intelligence/ui/cards/v2_mobile.yaml](../../custom_components/humidity_intelligence/ui/cards/v2_mobile.yaml),
  [custom_components/humidity_intelligence/ui/cards/v2_tablet.yaml](../../custom_components/humidity_intelligence/ui/cards/v2_tablet.yaml),
  [ui-gallery/default-v2-mobile-aq/card.yaml](../../ui-gallery/default-v2-mobile-aq/card.yaml), and
  [ui-gallery/default-v2-tablet-zone-2/card.yaml](../../ui-gallery/default-v2-tablet-zone-2/card.yaml): atomically replace the normal reason composer with exact-schema rendering and
  escaped legacy fallback.
- [ui-gallery/default-v2-mobile-aq/preview.png](../../ui-gallery/default-v2-mobile-aq/preview.png) and
  [ui-gallery/default-v2-tablet-zone-2/preview.png](../../ui-gallery/default-v2-tablet-zone-2/preview.png): deterministic browser captures using exact contract fixtures, the retained
  60-pixel scroll region, and the current passive Stability Score tile. These are
  documentation examples, not Phase 3 HA playback evidence.
- [custom_components/humidity_intelligence/ui/README.md](../../custom_components/humidity_intelligence/ui/README.md),
  [ui-gallery/README.md](../../ui-gallery/README.md), and both gallery example
  READMEs: document the sole-authority, fallback, Manual-card replacement,
  HA-managed dashboard, and cache/restart boundaries.
- `tests 2/test_reason_presentation.py`, engine/entity simulations,
  humidifier-reconciliation tests, diagnostics tests, and runtime-card sanity tests.
- `tests 2/test_reason_card_renderer.mjs`: execute valid, malformed, future-schema,
  Unicode-boundary, raw-ID, HTML-escaping, size-bound, and atomic-fallback behavior
  across all four V2 renderers. Run with
  `node "tests 2/test_reason_card_renderer.mjs"`; this command is a beta.4 release
  gate even before it is wired into repository CI.
- `custom_components/humidity_intelligence/manifest.json`,
  [CHANGELOG.md](../../CHANGELOG.md), [README.md](../../README.md),
  [ARCHITECTURE.md](../../ARCHITECTURE.md), release governance,
  and this proposal.
- [custom_components/humidity_intelligence/services.py](../../custom_components/humidity_intelligence/services.py),
  [custom_components/humidity_intelligence/__init__.py](../../custom_components/humidity_intelligence/__init__.py),
  [custom_components/humidity_intelligence/config_flow.py](../../custom_components/humidity_intelligence/config_flow.py),
  [custom_components/humidity_intelligence/helpers/cleanup.py](../../custom_components/humidity_intelligence/helpers/cleanup.py),
  [custom_components/humidity_intelligence/services.yaml](../../custom_components/humidity_intelligence/services.yaml),
  [custom_components/humidity_intelligence/strings.json](../../custom_components/humidity_intelligence/strings.json),
  and
  [custom_components/humidity_intelligence/translations/en.json](../../custom_components/humidity_intelligence/translations/en.json):
  retain the legacy
  service as a fail-safe, remove automatic creation/deletion, ignore old setup tokens,
  and describe the HA-managed Manual-card workflow.
- `tests 2/test_runtime_card_sanity.py` and `tests 2/test_config_flow_sanity.py`: prove
  authorization-before-guidance, zero dashboard side effects, legacy-token continuity,
  dashboard retention during cleanup, and removal of unsupported API references.

Worthwhile follow-ons, explicitly outside beta.4: localisation resources, a technical
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
3. **Generated/export boundary and compatibility fail-safe — complete.** Fresh generation/export parity, Manual-card
   structure, exact-path discovery, cache-only refresh, compatibility-service zero-
   side-effect failure, legacy-token continuity, and file-only cleanup passed.
   Registered or YAML-mode dashboards remain unchanged and their lifecycle is deferred.
4. **Beta.3 package/copy/config amendment — complete and separately deployed.** The
   package commit moves the exact component and proves parity;
   the config-only commit disables the generic CodeRabbit docstring check; the final
   reason commit makes humidifier response lines self-contained without changing
   cards, control, entities, or stored data.
5. **Beta.4 alert-language amendment — implemented, committed, and exact-deployed.** Apply the
   explicit response-lane headlines, family alert headlines, severity-first visible
   prose, human mould ranges, source/action/hold/conflict wording, beta identity,
   proposal, changelog, and exact regression fixtures without changing the schema or
   control behavior.
6. **Beta.5 status-chip refinement — exact local identity validated.** Keep the four V2
   renderers identical, shorten only Humidity Danger measurement suffixes, preserve
   every other alert context, use self-identifying humidifier labels and concise
   observed-state copy, and split zone/humidifier status groups without changing
   backend truth or runtime control.
7. **Exact-commit supported-HA and HA Lab validation — beta.4 operational deployment gate
   passed; playback pending.** Exact beta.4 package deployment, full HA Lab restart,
   Stage B, Stage 3, and a fresh T+0 passed. The proposal records a historical 1/9
   soak checkpoint; its current operational state was not assessed in this repo-only
   task. That evidence is beta.4-only. Beta.5 package deployment, full restart,
   Mobile/Tablet save-load and playback, and a fresh soak are now authorized, but the
   controller requires the exact commit on its remote Patch 1 profile and push remains
   unauthorized. Do not reuse beta.1 through beta.4 acceptance.
8. **Promotion review — pending.** Bella, Aetherwing, AetherCore, maintainer README approval,
   exact-head release sanity, live playback, and exact-candidate soak acceptance remain
   mandatory before RC or stable promotion.

Each phase is independently reviewable and rollback-safe. Phase 1 acceptance was the
gate for Phase 2; Phase 3 offline export/fail-safe evidence must not be inferred from
static gallery captures. Each beta amendment remains an exact candidate boundary and
exact-commit HA Lab playback remains separate.

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
- separately authorized beta.5 Mobile/Tablet playback and soak against the exact
  commit/version.

Beta.1 through beta.4 evidence remain historical evidence for their exact commits.
They are not acceptance evidence for the beta.5 status-chip candidate.

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
memory-auditor test could not start because its ignored-local helper source is absent
from this worktree. That known
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

The tracked memory-auditor test remains non-runnable because its ignored-local helper
source is absent from this worktree. This is an
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

## Beta.3 Cumulative Validation Record

The locally implemented beta.3 tree passed:

- 385 tracked pytest checks plus 123 subtests, excluding only
  `test_hi_memory_usage_auditor.py` because its intentionally ignored local helper is
  absent from this worktree;
- all 33 humidifier reconciliation scenarios, including every material reconciliation
  state, unavailable/blocked dispatch evidence, configured-label bounds, deterministic
  line splitting, concurrent AQ, and exact-once gate/CO isolation truth;
- all seven executable V2 reason-renderer cases;
- component compilation, version governance for `2.0.10-beta.3`, workflow and
  CodeRabbit YAML parsing, Inspector fixture freshness, proposal links, documentation
  previews, and diff whitespace checks;
- 52-file beta.2-to-beta.3 package count and content parity, with the engine proven
  byte-identical in the package-only commit and the two existing brand assets moved
  to the required component-local paths; and
- 91 ignored-local HA Lab tooling tests plus offline 52-file assembly for both the
  conventional beta.3 package and explicit legacy-root beta.2 rollback package.

The first cumulative review found and corrected three material truth issues: known
service unavailability now says no request was sent and uses `blocked`; inactive
humidifier isolation remains visible exactly once through gate and CO early exits; and
relocated UI README previews resolve to tracked assets. Proposal phase/status wording
was also made commit-local and internally consistent.

Official results at `50cf630`: version governance and Hassfest passed; HACS failed its
brands check. The bounded brand repair subsequently reached pushed exact beta.3 commit
`85ab542`; beta.3 was separately deployed/restarted in HA Lab and began a fresh exact
soak. That operational evidence is beta.3-only, incomplete, and now superseded by the
exact beta.4 deployment; it does not validate the beta.4 wording candidate. No PR
reply, re-review request, tag, or release is claimed here.

## Beta.4 Local Validation Record

The local beta.4 wording candidate passed 387 tracked pytest checks plus 123 subtests,
excluding only `test_hi_memory_usage_auditor.py` because its intentionally ignored
local helper is absent from this checkout. The run includes every environmental alert
family, explicit Risk/Danger copy, Danger-range evidence on a selected Risk mould
alert, bounded long labels, retained numeric mould arguments, CO emergency, configured
zone labels, runtime invariance, diagnostics, cards, package/version governance, and
documentation. All 27 executable JavaScript checks passed, including the seven V2
reason-renderer cases and 20 Inspector cases. Component compilation and
`git diff --check` also passed.

Exact-head HACS, Hassfest, and version-governance workflows passed for pushed commit
`fad159e`. Sanitized controller evidence confirms the direct 52-file beta.4 package,
one full restart, Stage B `13/13`, diagnostics `ok`, and Stage 3 `108/108`. A fresh
exact-deployment T+0 passed all eight read-only checks; the proposal-local checkpoint
was therefore 1/9. Its current operational state was not assessed in this repo-only
task. The observed live reason was calm normal-state truth,
so alert, degraded, CO-emergency, conflict, isolation, and humidifier variants remain
test-backed rather than live-playback-backed. Supported-HA/frontend save-load and
bounded alert scenario playback are not claimed. No stable-instance access, PR
activity, re-review request, tag, release, or promotion occurred.

## Beta.5 Local Validation Record

The beta.5-candidate working tree passed 387 tracked pytest checks plus 123 subtests,
excluding only `test_hi_memory_usage_auditor.py` because its intentionally ignored
local helper is absent from this checkout. The two modified Python regression modules
passed 142 focused checks. The executable V2 renderer suite passed 13/13, including
four-surface status-renderer parity, mapped and unmapped Humidity Danger shortening,
explicit preservation of a non-humidity context containing `>=`, two rows for an
active zone plus humidifier telemetry, one row outside a zone lane, escaped reason
rendering, schema bounds, privacy rejection, and atomic fallback.

Component compilation, branch/version governance for the authorized
`2.0.10-beta.5` manifest, proposal-link validation, `git diff --check`, and the
tracked Gitleaks scan passed. The full JavaScript pass was 33/33 across the V2
renderer and Inspector. This proves the local beta.5 candidate only; GitHub HACS,
Hassfest, and exact-head CI require the future remote commit and were not claimed.
No Home Assistant instance or dashboard was accessed or mutated during this local
gate. Live
Mobile/Tablet rendering, touch scrolling, two-row spacing, chip overflow, card
overlap, frontend cache behavior, and complete Manual-card save/load remain pending
separate operational authority.

## Home Assistant Lab Playback Expectations

Against the exact beta.5 commit/version created from this reviewed tree, first re-prove the beta.5 package and
perform the normal full Home Assistant restart. Back up and replace the complete card
on a lab-only dashboard under separate write authority. Then capture sanitized
evidence for calm normal, disabled, manual, pause, time gate, confirmed-away presence, unavailable presence,
telemetry loss/recovery, Zone 1/2, AQ trigger and retained run window, actionable and
unmapped/degraded alerts, alert conflict/hold, CO trigger and clear hold, fan and
humidifier isolation, and every humidifier reconciliation state. Verify:

- sensor state and legacy attributes remain available;
- `display_reason` is valid, below 4 KiB, at most eight lines, and contains no raw ID;
- Mobile and Tablet show the same ordered text and preserve scrolling;
- a zone plus humidifier state shows separate, non-overlapping ventilation and
  humidifier groups with `Downstairs Humidifier · On` or
  `Upstairs Humidifier · On` as applicable;
- Humidity Danger chips stop after alert type, room, and mapped zone while the reason
  and backend alert telemetry retain the measurement and threshold;
- a non-humidity alert context containing comparison syntax remains complete;
- isolation, unavailable states, long labels, horizontal overflow, touch and keyboard
  scrolling, HTML escaping, accessibility labels, and reason/card boundaries remain
  usable on both form factors;
- presentation failure or unsupported schema falls back atomically;
- service calls, helper/timer truth, reconciliation, and deterministic lane order
  match the control baseline; and
- restart/import and frontend/dashboard cache behavior match the documented boundary.

HA Lab package deployment/restart and lab-dashboard export/save are separate
operational authorities. Playback is advisory evidence only and does not authorize
Stable access, output writes, promotion, tag, or release.

## Release And Version Recommendation

Use `2.0.10-beta.5` for the next exact candidate. Beta.3 established the conventional
HACS package boundary and beta.4 established the backend-owned alert catalogue plus
its own deployment evidence. The new four-surface status renderer changes public UI
bytes and Manual-card copy, so beta.4 playback and soak acceptance cannot transfer.
Do not overwrite beta.4. The authorized manifest now says beta.5; bind CI, package
hashes, live playback, and a new soak to the exact beta.5 commit. The governed HA Lab
controller resolves only the allowlisted remote Patch 1 ref, so local commit authority
does not imply push authority or permit deployment from the developer checkout.

Do not move this to v2.1 merely because presentation is substantial: beta.5 keeps the
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

Beta.3 received a fresh cumulative review against the exact staged reason tree:

- **Aetherbite — `APPROVE_REASON_COMMIT_FINAL`.** Challenged every not-attempted
  dispatch category, mixed-output ambiguity, inactive-isolation ownership, long-label
  splitting, and scroll density. Resolution: capability failures are `blocked`,
  missing/unavailable state evidence is `unavailable`, no skipped request says
  `HI sent`, and every retained line remains independently labelled and bounded.
- **Bella — `APPROVE`.** Challenged reliance on lane-level failure state and the
  possibility that producer deduplication could hide isolation truth. Resolution:
  presentation reads matching output ownership, intent, and dispatch evidence; gate
  and CO early exits retain exactly one backend-owned humidifier-isolation notice.
- **Aetherwing — `APPROVED_FOR_LOCAL_COMMIT`.** Challenged shared-output wording,
  evidence precedence, maximum line length, and hidden runtime drift. Resolution:
  known exceptions outrank requested evidence, the longest reviewed line remains
  below 200 characters, and dispatch/retry/lane-order traces remain unchanged.
- **AetherCore — `APPROVE_BETA3_CUMULATIVE_LOCAL_WITH_MECHANICAL_CLOSEOUT`.**
  Challenged whether refined `blocked`/`unavailable` truth or gate/CO notices exceeded
  presentation scope. Resolution: the new helper is read-only, service-free, and
  changes only `display_reason`; the three-commit topology and external boundaries
  are proven.

Beta.4 received a fresh role-separated review against the final local wording tree:

- **Aetherbite — `APPROVE_BETA4_COPY`.** Challenged the technical tone of `response
  lane selected` and tested Bella's concern that generic family headlines could hide
  severity. Resolution: the maintainer's selected catalogue remains authoritative;
  `Risk alert:` or `Danger alert:` is the first readable body text in the existing
  scroll window. Aetherbite's clearer crossed-range wording—`this response starts at
  Risk`—was adopted.
- **Bella — `APPROVE_BETA4_LOCAL_COMMIT`.** Challenged malformed mould thresholds,
  duplicate label resolution, generic-headline specificity, and profile provenance.
  Resolution: Watch/Risk/Danger/fractional paths have exact tests; one bounded room
  label is reused; crossed-range copy separates selected response from observed
  conditions; and the exact threshold profile is retained privately then excluded
  from public telemetry.
- **Aetherwing — `APPROVE_BETA4_LOCAL_COMMIT`.** Found and blocked an initial public
  humidity `profile_label` leak, then challenged separate profile resolution across a
  month boundary. Resolution: the label comes from the exact profile object that
  calculates the threshold, the presenter does not resolve it again, public
  `alert_telemetry` filters the private fact, and regression proves both provenance
  and unchanged public shape. No lane, threshold, dispatch, output, timer, config,
  stored-data, card, restart/cache, or migration drift remains.
- **AetherCore — `NO_GOVERNANCE_OBJECTION — APPROPRIATELY_BOUNDED_FOR_LOCAL_COMMIT`.**
  Challenged stale lifecycle truth, missing Watch coverage, over-broad entity claims,
  cumulative-versus-beta.4 scope, and rollback evidence continuity. Resolution: local
  planning truth is current; exact delta and tests are recorded; presentation changes
  are distinguished from stable structured semantics; and rollback requires a fresh
  soak re-anchor.

Beta.5 received a fresh role-separated review against the 13-file local working tree:

- **Aetherbite — `APPROVE_BETA5_STATUS_CHIP_CANDIDATE_FOR_LOCAL_CLOSEOUT`.**
  Challenged whether “labelled row” implied a visible heading and whether the shorter
  alert chip remained understandable on mobile. Resolution: docs now say second row
  or accessibility-labelled row; every humidifier chip is visually self-identifying;
  and Humidity Danger retains alert type, room, and mapped zone while complete
  measurement truth remains in the reason and backend telemetry.
- **Bella — `APPROVE_BETA5_LOCAL_WORKING_TREE`.** Challenged whether frontend
  shortening weakened backend-owned truth and found stale root README `Output on`
  wording. Resolution: the projection is exact-prefix-gated, fails open, escapes the
  result, and leaves every backend surface unchanged; README now maps chip `On`
  explicitly to backend `output_on` without claiming physical moisture production.
- **Aetherwing — `APPROVE_BETA5_LOCAL_UI_DIFF / RELEASE_BLOCKED_PENDING_EXACT_IDENTITY_AND_LIVE_PLAYBACK`.**
  Challenged the English-format dependency, frontend compatibility, exact identity,
  and missing rendered evidence. Resolution: the rule is bounded to Humidity Danger,
  all other contexts remain verbatim, the four renderers are identical, and exact
  beta.5 package/restart plus Mobile/Tablet Manual-card playback and a fresh soak are
  mandatory later gates. Direct hostile transformed-chip escaping remains a
  nonblocking test-hardening follow-on because the shared chip sink already escapes
  dynamic text.
- **AetherCore — `NO_GOVERNANCE_OBJECTION — APPROPRIATELY_BOUNDED_AND_MAINTAINABLE_AS_FINAL_BETA5_AMENDMENT`.**
  Challenged cumulative metadata, stale beta.3/beta.4 lifecycle wording, missing
  package-versus-card rollback, preview ambiguity, and treating backend deployment as
  UI playback. Resolution: version-scoped metadata, immutable evidence, exact base
  HEAD/scope/digest, separate write authorities, unchanged-preview limits, rollback,
  and the two-gate live-validation boundary are explicit.

No beta.5 blocker remains unresolved. One accepted future-facing limitation remains:
the concise Humidity Danger chip depends on the current English
`active_alert_context` format. Do not extend that parsing to other alert families or
localisation; if the requirement grows, add a backend-owned concise presentation
field through a separately reviewed contract change. The unchanged gallery images are
historical illustrations and are not beta.5 rendered evidence.

No disagreement remains unresolved. Aetherbite still prefers `ventilation lane` as a
future domestic alternative to `response lane`, but explicitly approved retaining the
maintainer-selected wording in this bounded beta.4 catalogue. Bella's concern about
generic alert-family headlines is reconciled by the maintainer's explicit direction
and the mandatory severity-first first line.

The first cumulative review also found stale relocated preview links and proposal
lifecycle wording; both were corrected before commit-specific approval. There is no
unresolved product, runtime, packaging, privacy, or governance disagreement.

All four beta.4 approvals cover the reviewed tree plus this mechanical verdict/status
bookkeeping. Any later behavioral change requires renewed review.

There is no unresolved product or runtime disagreement. The accepted density trade-off is
that a long action sentence can begin below the tablet's initial 60-pixel fold; it
remains keyboard/touch scrollable and the UI does not summarize or reconstruct it.
Phase 3 registered/YAML-mode dashboard mutation is explicitly deferred, not treated as
successful validation. Beta.4 playback evidence does not transfer; separately
authorized exact-commit live playback remains required before beta.5 can be considered
for release.

## Maintainer Decisions

Jules has approved every design decision needed to begin implementation:

- additive `display_reason` authority and exact schema/bounds;
- `requested` service-layer definition;
- label precedence and absolute raw-ID prohibition;
- calm neutral visibility and no beta.5 technical expander;
- HA-managed dashboard creation plus whole-card replacement for existing HI Manual
  cards, with registered/YAML-mode dashboard lifecycle deferred;
- degraded fail-closed unavailable-presence presentation;
- beta.5 placement with v2.1 reserved for a breaking reason-state replacement;
- a backend-owned, self-contained `Humidifier response — {resolved label}:` prefix
  instead of a card-authored or standalone second heading;
- conventional HACS packaging for the active repository-admission requirement;
- disabling only CodeRabbit's generic docstring-coverage pre-merge check; and
- family-level alert-lane headlines with Risk/Danger stated in the first visible
  sentence, `High humidity` naming, and human mould ranges without removing numeric
  structured arguments; and
- beta.5 status-chip clarity: Humidity Danger-only suffix shortening,
  `Downstairs/Upstairs Humidifier · On`, and separate zone/humidifier status groups
  while retaining complete backend telemetry and reason truth.

No additional product decision is required for Phase 1, Phase 2, the bounded Phase 3
compatibility amendment, the beta.3 package/copy/config amendments, or the beta.4
alert-language amendment. Local
implementation, beta.5 version identity, local commit, HA Lab deployment/restart,
lab-only Manual-card replacement, Mobile/Tablet playback, and fresh soak are
authorized. Push remains a separate authority and is required before the controller
can resolve the new exact commit. Stable access, output writes, PR reply, re-review
request, promotion, tag, and release remain blocked. Before release promotion, Jules
must accept the exact final evidence and release boundary.

## Rollback

Rollback remains migration-free:

- an old card ignores `display_reason`;
- a new card falls back when the backend lacks it;
- presenter failure removes the current-cycle attribute and preserves the technical
  reason; and
- no entity, registry, stored-data, or service cleanup is required.

Beta.3 and beta.4 are immutable exact deployed evidence identities. Before beta.5 is
deployed, rollback of this amendment is the reviewable reversal of its
card, test, documentation, and manifest delta while leaving beta.4 untouched. After beta.5 is
deployed or distributed, restore a complete known-good package through a separately
governed rollback build; do not rewrite beta.4 history or attach beta.5 evidence to
it. The conventional component layout remains unchanged.

Preserve both the exact beta.4 package and the complete pre-beta.5 Manual-card YAML.
Package rollback does not replace a beta.5 card already pasted into Home Assistant;
UI rollback requires whole-card replacement with the backed-up YAML, save, then a
frontend reload if cached content remains. No entity-registry, helper, configuration,
or stored-data cleanup is involved.

Rollback restores package identity only, not soak continuity. A beta.5 deployment
starts a new evidence window; returning to beta.4 requires an explicit re-anchor or
fresh T+0 rather than silently resuming any earlier sample sequence.

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

`REVIEW_REQUIRED — BETA5_EXACT_LOCAL_COMMIT_AUTHORIZED / REMOTE_REF_AND_LIVE_MOBILE_TABLET_EVIDENCE_REQUIRED`

Phase 1, Phase 2, and Phase 3 remain approved historical implementation slices.
Beta.3's package, configuration, reason, and brand corrections remain its immutable
historical identity. Beta.4's alert-language amendment has exact deployment, Stage B,
Stage 3, and T+0 evidence that remains beta.4-only. The beta.5 status-chip amendment
now has explicit manifest, local-commit, HA Lab deployment/restart, lab-card playback,
and soak authority. The governed controller requires the exact commit on its
allowlisted remote Patch 1 ref; push is not authorized, so package deployment cannot
begin from the local checkout. Stable access, output writes, PR reply, re-review
request, PR creation, tag, and release promotion remain unauthorized.
