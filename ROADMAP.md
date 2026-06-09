# Humidity Intelligence Roadmap

Local execution roadmap for Humidity Intelligence V2.

This file is intentionally local-only and ignored by Git. It is a planning and
governance surface, not public release documentation.

## Purpose

Turn current release state, governance proposals, and v2.1 direction into an
implementation-aware roadmap that protects deterministic runtime behavior while
making the next work slices easier to choose, review, validate, and stage.

## Canonical Operating Position

- `DESIGN_BRIEF.md` remains the implementation contract.
- Root `PROPOSALS.md` remains the canonical proposal ledger.
- `.codex/governance/proposals/` holds draft, reviewed, implemented, archived,
  rejected, and historical proposal material.
- Humidity Intelligence remains a deterministic Home Assistant environmental
  control engine.
- Exactly one ventilation lane is selected per evaluation cycle.
- Canonical ventilation priority is: CO emergency -> humidity danger -> mould
  danger -> mould risk -> condensation danger -> condensation risk -> zone 1 ->
  zone 2 -> AQ -> normal.
- Humidifier lanes remain independent from ventilation lane resolution.
- Runtime/UI truth alignment is mandatory: generated dashboards, chips, reason
  panels, diagnostics, and release checks must reflect backend telemetry,
  mappings, configuration, or runtime truth only.
- Humanised wording may make the system easier to read, but it must sit on top of
  raw operational truth. It must not hide selected lane, trigger, source, zone,
  gate state, degraded state, alert state, or missing-data conditions.
- Primary safety and diagnostic truth must remain visible on the primary Current
  Air Control surface when active: selected ventilation lane, CO emergency state,
  alert state, gate/manual/pause state, degraded or missing telemetry,
  unavailable outputs, and suppression reasons. Drill-downs may hold supporting
  detail, but they must not be the only place safety-critical truth appears.
- Guardrail-first architecture wins over novelty, visual polish, and broad
  product ambition.

## Governance State

- V2.0.4 is the implemented historical stabilisation baseline; current front-page
  highlights should describe only the active release while older detail stays in
  release notes or archived sections.
- V2.0.5 is a completed stable release milestone. It is no longer an active
  implementation bucket.
- V2.0.6 is the current stable maintenance release in the canonical release-source
  checkout. It includes runtime truth hardening, v2.0.6 beta maintenance items, and
  stable metadata promotion.
- V2.0.7-beta.1 is the active beta maintenance line on `senyo888-patch-1`. It
  includes the PM2.5 aggregate runtime truth fix and current HA Lab Operational Beta
  Validation Infrastructure evidence from 2026-06-09.
- V2.0.5 and v2.0.6 release publication require the normal release-source, Bella,
  AetherCore, release sanity, README approval, and version-governance gates. Those
  gates remain mandatory for future releases.
- V2.1 Environmental Stability Intelligence is planned only. No v2.1 stability
  score, prediction, outcome-layer, harmonic orchestration, or dashboard-strategy
  feature is implemented in v2.0.6.
- V2.1 AetherCore Phase 1 governance containment is complete as of 2026-05-24.
  This completion is local governance only: proposal pruning, metadata/expiry
  rules, minimal `.codex` governance structure, HA Lab baseline pointer,
  runtime-protection contracts, agent boundary charter, and validation reporting.
  It does not implement v2.1 runtime behavior, Home Assistant mutation, generated
  UI changes, release authority, or standing AetherCore supervision.
- The Aetherbite `Harmonic Air Control Evolution` proposal is a reviewed draft.
  It is coherent as v2.1 exploratory direction, rejected for v2.0.5
  implementation, and not promoted to root `PROPOSALS.md`.
- Release-source truth must come from the canonical local GitHub checkout or a
  worktree created from it. The older HI Work folder is retired as an editable
  source and may be used only as historical/reference material until archived.
- Local-only planning docs may be mirrored for continuity, but they remain ignored,
  unstaged, uncommitted, and unpublished unless publication is explicitly approved.

## Current Release Track

### V2.0.4 - Implemented

Scope now closed:

- Alert binding and zone-bound boost behavior.
- Crash hardening and safe degraded behavior.
- Reason panel truth and companion chip alignment.
- Post-configuration editing parity across sensors, gates, thresholds, zones,
  humidifiers, AQ, alerts, and slope.
- Seasonal humidity targets and temperature comfort handling.
- Temperature slope chip rendering fixes.
- Alert flash RGB payload normalization.
- Visual humidity, mould, and condensation alert repeat behavior: flash 10 times,
  restore prior light state best-effort, then repeat after 30 minutes only while
  the same alert remains active.

Release boundary:

- No Home Assistant 2026.5-only changes.
- No minimum Home Assistant version bump unless unavoidable.
- No new architecture or UX concept should be backported into this track.

### V2.0.5 - Released Stable Milestone

Current state:

- Version track: stable `2.0.5`.
- Implementation status: complete.
- Release status: completed stable milestone. Future changes belong in v2.0.6,
  v2.0.7, or later maintenance/release lines unless explicitly scoped as
  documentation cleanup.

Implemented scope:

- Setup/options progressive disclosure with essentials visible first and tuning in
  Advanced sections.
- Immediate in-form Advanced sections instead of submit-gated reveal behavior.
- Recommended defaults preserved when Advanced fields are untouched or hidden.
- Control loop interval, startup UI refresh, custom target/comfort values, slope
  overrides, optional chip rows, fan levels, thresholds, lane removal, AQ tuning,
  and visual-alert tuning are advanced controls.
- `show_output_entity_details` is a generated-card visibility option only.
- New generated V2 cards default to the cleaner output display unless output
  details are enabled.
- First-install UI export defaults to `v2_tablet`.
- Canonical `dump_cards` behavior is preserved: unscoped calls export all
  cached/generated layouts; scoped `layout` calls export only the requested layout.
- `v205_release_check` is read-only and exists to validate generated-card
  visibility, cached layouts, placeholder status, configured entity availability,
  frontend dependency status, and scoped/unscoped `dump_cards` behavior.
- Frontend dependency truth is shared across setup/options, `self_check`,
  `v205_release_check`, and `dump_diagnostics`.
- Native Home Assistant config-entry diagnostics now provide a redacted,
  user-downloadable GitHub issue attachment path. This is support/triage UX only:
  no runtime lane behavior, entity semantics, output writes, generated dashboard
  behavior, or cloud upload path changed.
- Issue #21 house humidity drift hardening now surfaces the canonical
  `sensor.house_humidity_mean_7d` statistics dependency status in the drift
  sensor, `self_check`, `v205_release_check`, and diagnostics. Valid systems keep
  the same drift calculation.
- Calculated temperature slope diagnostics prefer registered Home Assistant entity
  IDs over predicted fallback IDs.

Preserved semantics:

- No runtime lane behavior change.
- No alert hierarchy change.
- No CO emergency behavior change.
- No humidifier independence change.
- No entity contract change.
- No hidden service path or parallel output writer.
- No automatic GitHub upload or GitHub authentication from Home Assistant.
- No v2.1 feature implementation.

Release validation record:

- The release line preserved deterministic lane ordering, alert hierarchy, CO
  emergency behavior, humidifier independence, entity semantics, and `dump_cards`.
- Native Home Assistant diagnostics, `dump_diagnostics`, `self_check`, and
  `v205_release_check` now carry the same support truths where applicable.
- Issue #21 drift dependency handling and registered slope mapping were completed
  as support/runtime-coherence hardening without changing valid calculations or lane
  behavior.
- README approval by Senyo was confirmed on 2026-05-20.
- Future release tagging/publishing must repeat the hard release gates; do not reuse
  the v2.0.5 signoff as approval for later versions.

### V2.0.6 - Current Stable Maintenance Release

Current state:

- Version track: stable `2.0.6` in the canonical release-source checkout.
- Implementation status: complete in the stable maintenance line.
- Release status: stable release-source truth. This retired HI Work folder may lag in
  metadata and must not be used as release authority.

Implemented scope:

- `telemetry_unavailable` runtime mode for required humidity telemetry or configured
  temperature telemetry unavailability while control is otherwise enabled.
- Safe stand-down behavior for missing required telemetry: outputs return to normal,
  lower-priority alert/humidifier/zone/AQ lanes are skipped, and the mode/reason
  surface degraded truth instead of normal/all-clear.
- Global gate preemption clears stale lower-priority humidity-danger alert switch,
  active alert context, alert telemetry, and Current Air Control alert display truth.
- CO emergency clearing schedules a recheck at the two-minute clear-hold deadline
  instead of waiting for the next normal periodic control interval.
- Backend air-control-mode simulation coverage validates normal, telemetry
  unavailable, zone, AQ, gate, and opt-in CO pressure cases without runtime fake
  telemetry entities.
- Setup/options telemetry add/edit Cancel navigation preserves already-saved flow data.
- Zone 2 setup/options defaults and labels resolve to Zone 2 / Level 2 ownership unless
  explicitly changed.
- Manual local HI-only snapshot services provide `create_local_backup` and
  `list_saved_versions` for advanced package-local maintenance.
- Drift Statistics-helper ownership/readiness reporting adds missing-helper Repairs
  guidance, low-history coverage status, invalid-source status, and readiness fields
  including `age_coverage_ratio`, `required_age_coverage_ratio`,
  `source_value_valid`, `repair_required`, and `repair_kind`.
- Seasonal temperature chip colour semantics use backend-owned cold, comfort, warm,
  and hot boundaries; generated cards consume resolved warm-boundary truth from
  sensors/diagnostics rather than hard-coded seasonal thresholds.

Preserved semantics:

- Deterministic lane order is preserved.
- Alert hierarchy is preserved.
- CO emergency remains highest priority.
- Humidifier independence is preserved.
- AQ behavior is preserved except for being skipped under explicit required-telemetry
  degradation.
- Output-write semantics are preserved except for safe stand-down under
  `telemetry_unavailable`.
- Drift math and `sensor.house_humidity_mean_7d` compatibility are preserved.
- No restore flow, automatic rollback, HACS interception, startup snapshot,
  whole-instance backup, hidden output path, or v2.1 feature is introduced.

Runtime/UI impact:

- Entity semantics changed narrowly: `HI Air Control Mode` may now report
  `telemetry_unavailable` when required telemetry is not usable.
- Generated dashboards must display backend-owned `telemetry_unavailable`,
  gate-preemption, and CO truth. They must not infer a separate frontend state.
- Migration is not required.
- Home Assistant restart/reload is required after updating runtime source.
- Run `humidity_intelligence.dump_cards` or refresh copied dashboard YAML when
  generated Current Air Control output must reflect the stable v2.0.6 card truth.

## Release Validation Pattern

Local validation remains useful, but it is not the final release gate when normal
pytest collection is blocked locally without Home Assistant installed.

Use this order for future release validation:

1. Complete the Codex implementation slice with docs/config sanity in the canonical
   checkout or an active git worktree.
2. Run Bella coherence audit for source-of-truth, release-boundary, and UI truth
   alignment.
3. Run pytest where Home Assistant dependencies are available; otherwise run the
   direct runtime/card sanity harness and report pytest as blocked.
4. Verify `git status`, ignored/local-only boundary coverage, and public-safety
   boundaries before staging. If a retired reference folder was used, import only
   applicable files path-preservingly and freeze that folder again as reference-only.
5. Re-run relevant validation from the same canonical checkout or active worktree.
6. Run HACS Integration Preflight from VS Code when available to check
   HACS/install metadata, `manifest.json`, `hacs.json`, package layout, branding,
   workflow, and repository hygiene. It supports release packaging sanity; it does
   not replace pytest, runtime sanity, Bella coherence review, or Aetherwing
   validation.
7. Install/update in a Home Assistant-capable test environment.
8. Restart Home Assistant and inspect startup logs.
9. Exercise fresh setup, options edits, `dump_cards`, `self_check`, release-check
   services where present, and `dump_diagnostics`.
10. Inspect generated mobile/tablet cards for placeholder, pruning, dependency,
   output-details, and truth-alignment regressions.
11. Record HA Lab advisory beta-validation evidence when a beta deploy, runtime
   activation, Stage 3 runtime-readiness check, or generated-card/entity-map sanity
   check is relevant. HA Lab evidence informs review; it is not release authority,
   runtime authority, stable Home Assistant authority, or permission for autonomous
   mutation.
12. Run AetherCore governance verification for role boundaries, proposal/release
   process coherence, and local/public boundary safety.
13. Confirm README approval for the release being prepared.
14. Run release readiness review after implementation, Bella review, AetherCore
   review, runtime sanity, Home Assistant validation, HACS Preflight findings, and
   README approval evidence are complete.
15. Promote or tag only after manifest, docs, changelog, release notes, and branch
   state all tell the same story.

Minimum local checks by change type:

| Change type | Local checks | Home Assistant checks |
| --- | --- | --- |
| Docs/governance only | Filename/source-of-truth sanity, public-safety scan, release-boundary audit | Not required unless release wording changes user-visible validation claims |
| Generated-card copy/layout | Direct card sanity harness, placeholder/pruning scan, `dump_cards` contract sanity | Export cards, paste/load YAML or generated dashboard, check frontend resource behavior |
| Config/options UX | Compile/config-flow sanity where possible, direct sanity coverage for storage/default behavior | Fresh setup, options edits, restart persistence |
| Diagnostics/services | Compile, JSON-safe output sanity, direct service-output sanity | Run service calls in HA and compare outputs |
| Runtime/control | Compile, direct runtime sanity, targeted regression coverage | Full HA runtime validation and log review |

## Post-V2.0.5 Reclassification

This section closes the former v2.0.5 pull-forward list. Completed release hygiene is
no longer active roadmap work. Remaining ideas are either routine documentation
maintenance or future v2.1+ candidates that require their own proposal, validation
gate, and rollback plan.

| Candidate | Current status | Next valid lane | Boundary |
| --- | --- | --- | --- |
| Release/docs wording correction | Completed for v2.0.5; remains routine hygiene | Docs/governance maintenance | Correct stale facts only; no new behavior claims |
| Output-detail visibility cleanup | Completed in v2.0.5 | None unless a regression appears | `show_output_entity_details` remains UI-only/generated-card visibility |
| Setup/options helper-copy tightening | Completed in v2.0.5 | None unless a regression appears | Strings/docs only; no schema/storage/default drift |
| Native diagnostics and issue-template support flow | Completed in v2.0.5 | Support-doc maintenance | Native HA diagnostics first; `dump_diagnostics` remains a local/full export path |
| Required telemetry degraded mode | Completed in v2.0.6 | Regression/docs maintenance only unless a new runtime defect appears | `telemetry_unavailable` is backend-owned degraded truth; no frontend-inferred normal/all-clear state |
| Global gate stale-alert preemption | Completed in v2.0.6 | Regression/docs maintenance only unless a gate/display defect appears | Gate authority clears or suppresses lower-priority alert helper/context/telemetry truth |
| CO emergency timed clear recheck | Completed in v2.0.6 | Regression/docs maintenance only unless a CO timing defect appears | CO remains highest priority; clear timing is bounded without lowering safety priority |
| Config/options flow coherence | Completed in v2.0.6 | Regression/docs maintenance only unless a new config-flow issue appears | Cancel confirmation preserves saved flow data; Zone 2 defaults/labels identify Level 2 ownership; no lane/entity/UI semantics change |
| Local HI-only snapshot support | Completed in v2.0.6 | Regression/docs maintenance only unless restore is separately approved | Manual create/list services only; no restore, automatic rollback, HACS interception, startup snapshot, or whole-HA backup claim |
| Drift dependency hardening for `sensor.house_humidity_mean_7d` | Completed in v2.0.5; v2.0.6 ownership/readiness follow-up completed | Regression/docs maintenance only unless a new proposal is approved | Preserve current drift semantics; do not synthesize history or create helpers silently |
| Seasonal temperature chip colour semantics | Completed in v2.0.6 | Regression/docs maintenance only unless a new proposal is approved | Backend truth first; no YAML-only threshold table; custom warm thresholds need a separate proposal |
| Registered calculated-slope mapping | Completed in v2.0.5 | Regression tests/support docs only | Prefer registered HA entity IDs before predicted fallback IDs |
| Idle-state copy refinement | Future candidate | V2.1 fixture-backed UI copy | Raw reason/degraded/gated/alert truth must remain visible |
| Readability-only generated-card deduplication | Future candidate | V2.1 generated-card slice | Requires fixtures and no selected-lane/gate/source truth loss |
| Multi-AQ merged display wording | Future candidate | V2.1 generated-card/display experiment | Existing AQ ownership must remain visible or reachable |
| Safer AQ grouping semantics | Future candidate | V2.1 telemetry contract first | No frontend-inferred semantic state |
| Harmonic automation-family phrasing | Future candidate | V2.1 wording/generated-card experiment | Do not collapse lane ownership or humidifier independence |
| Humanised reason narrative | Future candidate | Runtime telemetry contract first | No frontend-only inferred narration |
| Stability Score | Future candidate | V2.1 diagnostics/read-only telemetry | Must not control lanes, gates, alerts, or outputs |
| Deterministic forecast/prediction | Future candidate | V2.1 telemetry contract first | Unavailable rather than guessed when data is weak or missing |
| Functional primary chips | Future candidate | Interaction contract first | Read-only by default; no hidden control path |
| Composite harmonic colors | Future candidate | V2.1 accessibility/display review | Safety/CO/alert states must remain dominant |
| AI-style environmental narration | Rejected | None | No fake AI insight, probabilistic advice, or untraceable text |

Recommended post-v2.0.6 candidates:

- Keep documentation, support, diagnostics wording, generated dashboards, and release
  metadata synchronized with the shipped v2.0.6 behavior.
- Add regression coverage or support guidance only when it protects existing v2.0.6
  contracts.
- Route the PM2.5 house aggregate gap through v2.0.7 maintenance.
- Stage all Environmental Stability Intelligence, Harmonic display, prediction,
  Stability Score, chip interaction, and dashboard-strategy ideas through v2.1 gates.

## V2.0.7 Beta Maintenance

The first required v2.0.7 fix was the PM2.5 house aggregate runtime truth gap found by
HA Lab Stage 3 six-sensor runtime readiness on 2026-06-06. The implementation is now
present in `2.0.7-beta.1` and the current HA Lab Stage 3 rerun passes.

Required proposal:

```text
.codex/governance/proposals/drafts/2026-06-06-v207-pm25-house-aggregate-runtime-truth.md
```

Evidence:

```text
.codex/lab/reports/2026-06-06T14-39-27Z-stage-3-six-sensor-runtime-readiness.md
.codex/lab/reports/2026-06-09T18-23-00Z-stage-a-package-deploy.md
.codex/lab/reports/2026-06-09T18-29-19Z-stage-3-six-sensor-runtime-readiness.md
```

Current verdict:

- six-sensor helper/wrapper surface: `108/108` exact;
- `sensor.humidity_intelligence_hi_house_voc_average`: present and numeric;
- `sensor.humidity_intelligence_hi_house_pm25_average`: present and numeric at `5.0`;
- `sensor.humidity_intelligence_hi_level1_pm25_average`: present and numeric at `5.0`;
- `sensor.humidity_intelligence_hi_level2_pm25_average`: present and numeric at `5.0`;
- `sensor.humidity_intelligence_hi_house_pm2_5_average`: absent with HTTP `404`;
- Stage 3 verdict: `PASS`.

Implementation status:

- local implementation now normalizes existing HI PM2.5 aggregate entity IDs from
  Home Assistant's dotted `pm2_5` slug to canonical `pm25`;
- new PM2.5 aggregate sensor names avoid the dotted slug while preserving PM25
  unique IDs and backend aggregate computation;
- HA Lab deployment and Stage 3 rerun are complete as advisory operational beta
  evidence. Generated-card/entity-map release proof is still separate and should be
  captured if release-readiness review needs UI truth evidence.

Required v2.0.7 outcome:

- configured PM2.5 telemetry must expose the expected HI house PM2.5 aggregate;
- the PM2.5 house aggregate must be numeric when usable PM2.5 telemetry exists;
- unavailable, unknown, or unconfigured PM2.5 telemetry must degrade explicitly;
- generated UI must consume backend aggregate truth only and must not infer PM2.5
  aggregate values in frontend code;
- deterministic lane ordering and AQ lane priority must remain unchanged.

Current HA Lab operational beta baseline:

```text
.codex/lab/baselines/current-first-slice-runtime-baseline.md
.codex/labs/ha-lab/current-baseline.md
.codex/lab/implementation/operational-beta-validation-packet.md
```

Next review gate:

- Record HA Lab advisory status in any PR or release-readiness review.
- Capture generated-card/entity-map sanity evidence if UI truth is in scope.
- Keep HA Lab evidence advisory; do not treat it as release authority or stable Home
  Assistant proof.

## V2.1 AetherCore Phase 1 Governance Completion Notice

Status: complete as local governance containment on 2026-05-24.

Completed scope:

- Proposal pruning and active draft-state clarification.
- Canonical proposal metadata template, state ladder, expiry/review dates, and stale
  draft archive rules.
- Minimal `.codex` governance map, with `drafts.md` preserved as the active draft
  index and root `PROPOSALS.md` preserved as the canonical proposal ledger.
- HA Lab baseline pointer and report supersession rules so lab evidence remains
  advisory evidence only.
- Runtime-protection contracts for lane order, service/entity semantics, humidifier
  independence, alert priority, UI/runtime truth, stable/lab isolation, contract
  change control, and release-validation truths.
- Agent boundary charter for Senyo, Bella, Aetherwing, Aetherbite, and AetherCore.
- Phase 1 validation report confirming no runtime, service/entity, generated UI,
  release metadata, or release-authority change from this governance work.

Completion boundary:

- This does not complete the product-facing `Phase 1 - Low-Risk UI Truth Polish`
  described below.
- This does not promote AetherCore into a standing supervisor, release approver,
  runtime validator, scheduler, watcher, proposal ledger, or implementation owner.
- This does not authorize fake outputs, shadow mode, production telemetry mirroring,
  reusable scenario runners as release proof, stable Home Assistant mutation, or lab
  evidence as release authority.
- Any next phase must be separately scoped with explicit rollback, validation, and
  maintainer approval before implementation or Home Assistant mutation.

## V2.1 Staging Discipline

V2.1 must be staged as controlled slices. Do not collapse wording, generated cards,
telemetry, diagnostics, interactions, and runtime logic into one broad patch.

Phase gates:

- Phase 1 may only consume existing runtime truth.
- Phase 2 defines new read-only telemetry contracts.
- Phase 3 builds dashboard composition and orchestration-display UX on top of
  proven contracts. The UI may explain or group runtime behavior; it must not
  coordinate control.
- Phase 4 stays optional/future-facing until prior contracts and validation exist.

Every v2.1 slice must state:

- Scope.
- Guardrails.
- Current promotion gate.
- Blocked-until conditions.
- Rollback path.
- Likely implementation owner.
- Change type: runtime, generated-card, telemetry, UX-only, diagnostics-only, or
  governance-only.
- Required validation and regression fixtures.
- Whether entity semantics, service outputs, generated dashboards, migrations, or
  release docs are affected.

## V2.1 Risk Reduction Model

V2.1 work must reduce risk by moving through promotion gates. A concept must not jump
directly from proposal text into default UI, runtime entities, service contracts, or
control logic.

Promotion gates:

1. Governance-only contract
   - Define scope, guardrails, non-goals, affected surfaces, validation, and rollback.
   - No source, generated-card, service, entity, or public-doc behavior change.

2. Fixture-only expected outputs
   - Add representative fixtures, expected card/output snapshots, or contract examples.
   - Prove the intended truth shape before changing runtime or generated UI.

3. Diagnostics-only truth surface
   - Expose raw inspectable truth in diagnostics or release-check output first.
   - No new default entities, no generated-card dependency, and no lane-control effect.

4. Read-only telemetry
   - Add explicit telemetry only after diagnostics prove the shape and degraded cases.
   - Telemetry must be JSON-safe, recorder-safe, documented, and unable to affect lane
     selection or output writes.

5. Opt-in generated-card display
   - Render the new interpretation only behind an option, experimental layout, or
     clearly staged generated-card path.
   - Disabling the option must restore the current v2.0.6 display behavior.

6. Default UI promotion
   - Promote only after Home Assistant validation, fixture coverage, generated-card
     sanity, frontend dependency review, and Bella runtime/UI truth audit.

Gate rules:

- No slice may skip gates unless Bella records why the lower gate does not apply.
- Runtime control remains out of scope unless a separate approved proposal changes
  that boundary.
- Do not combine telemetry creation, generated-card display, visual restyling, and
  interaction changes in one patch.
- Any wording that claims "stabilising", "balancing", "orchestration", "intent",
  "prediction", or similar intelligence must identify a backend-owned source or
  be suppressed.
- Prefer diagnostics-only and opt-in display before adding user-visible entity
  contracts.
- Rollback must be explicit before implementation starts.

## V2.1 Foundations

### Phase 1 - Low-Risk UI Truth Polish

Scope:

- Wording-only improvements for existing display states.
- Calmer idle display copy where raw degraded/gated/alert truth remains available.
- Humidify wording cleanup without changing humidifier lane independence.
- Trigger-detail deduplication in generated cards where information is repeated.
- Low-risk generated-card grouping using existing runtime helpers only.
- First small Harmonic experiment only if it is display-only and fixture-backed.

Guardrails:

- No runtime changes.
- No entity state changes.
- No service schema changes.
- No new telemetry contract.
- No frontend-only conclusion such as "stabilising" unless backed by current runtime
  state, reason text, configured telemetry, diagnostics, or explicit existing helper
  state.
- Selected lane, gate, alert, and missing-data truth must remain visible on the
  primary surface; source, isolation, and supporting detail may be reachable.

Risk posture:

- Current allowed gate: fixture-only expected outputs, then opt-in generated-card
  display using existing runtime truth.
- Blocked until: fixture coverage proves primary safety truth remains visible, and
  supporting source, isolation, and degraded detail remains visible or reachable.
- Rollback path: disable the experimental display option or revert the generated-card
  copy/grouping patch; runtime behavior and entity state must be unchanged.

Progress note - 2026-05-28:

- Current Air Control Truth Fixtures are complete for sandbox review under
  `sandbox/v2.1/safe/`.
- Bella semantic corrections have been applied for selected-lane purity, CO
  emergency dominance, alert-only visibility, unavailable-input honesty, and
  non-schema fixture wording.
- Status remains fixture-only, sandbox-only, sanitized, non-runtime, non-executable,
  and human-review material only.
- This does not grant diagnostics, generated-dashboard, entity, service,
  Home Assistant API, runtime-control, implementation, or promotion authority.
- Runtime implementation remains blocked.

Likely owners:

- Aetherbite: wording and UX experiment drafting.
- Aetherwing: generated-card implementation.
- Bella: coherence, release-boundary, and truth-surface review.

Change types:

- UX-only.
- Generated-card.
- Governance-only for proposal slicing.

Required validation:

- Direct runtime/card sanity harness.
- Generated-card placeholder and malformed-structure scan.
- Fixture coverage for normal idle, gated, pause/manual override, alert-only, AQ-only,
  humidifier-only, AQ plus humidifier, isolation, degraded data, and active alert
  states.
- Accessibility/readability review if visual treatment changes.

### Phase 2 - Telemetry Contracts And Integrity State

Scope:

- Define backend-owned telemetry contracts for v2.1 insights.
- Add a read-only Stability Score framework only after formula, inputs,
  per-component weighting, clamping, data coverage, missing-data behavior,
  attributes, and suppression reasons are specified.
- Add deterministic forecast/trajectory scaffolding only where slope, sample
  history, time window, confidence gates, and suppression behavior are sufficient.
- Add componentized System Integrity status for runtime inputs, lane resolution,
  dashboard mappings, configured outputs, optional dependencies, card export
  health, and diagnostics. It must not collapse unlike health signals into one
  vague pass/fail state.
- Define raw fallback fields for any humanised narrative.

Guardrails:

- New telemetry is read-only at first.
- Stability Score must not select lanes, override gates, change alert priority, or
  write outputs.
- Stability Score must expose its contributing components, weights or rules,
  clamps, data coverage, unavailable inputs, and suppression reason.
- Forecasts must be unavailable rather than guessed when slope, sample history,
  time window, or confidence data is weak, missing, stale, or ambiguous.
- System Integrity must preserve component-level truth. Optional frontend
  dependencies, including `not_inspectable` resource status, must not become
  backend runtime failures.
- Any new sensor/entity semantics must be documented before implementation.
- Diagnostics must explain why a score, forecast/prediction, or integrity state is
  unavailable.

Risk posture:

- Current allowed gate: governance-only contract, fixture-only expected outputs, then
  diagnostics-only truth surface.
- Blocked until: formula, weighting, clamping, unavailable-data behavior, JSON-safe
  attributes, recorder impact, forecast window/confidence rules, suppression
  behavior, componentized integrity semantics, and no-control guarantees are
  specified.
- Rollback path: remove or hide diagnostics/telemetry fields without changing stored
  user configuration, generated cards, lane selection, or output writes.

Likely owners:

- Aetherwing: telemetry/service/diagnostics implementation.
- Bella: semantic contract and release-readiness review.
- Aetherbite: wording for unavailable/degraded states after contracts exist.

Change types:

- Telemetry.
- Diagnostics-only.
- Runtime read-only.
- Docs/tests.

Required validation:

- Python compile/import sanity.
- Direct sanity coverage for formula boundaries, component breakdown, missing data,
  unknown/unavailable states, suppression behavior, JSON-safe attributes,
  componentized System Integrity, optional frontend non-blocking behavior, and no
  lane-control side effects.
- `self_check`, `dump_diagnostics`, and release-check output consistency.
- Home Assistant runtime validation for entity creation, restart persistence, recorder
  safety, and log cleanliness.

### Phase 3 - Dashboard Strategy And Orchestration Display UX

Scope:

- Explore native Home Assistant dashboard strategy support as optional UI delivery.
- Keep `dump_cards` as fallback/export mode until native dashboard delivery is proven
  stable and backwards-compatible.
- Build orchestration-display UX on top of Phase 1 display fixtures and Phase 2
  telemetry contracts. It may group or explain concurrent runtime states, but it
  must not become a control coordinator.
- Expand Harmonic Air Control only where primary safety truth remains visible and
  supporting raw operational truth remains visible or reachable.
- Add contextual read-only drill-downs only after an interaction contract exists.

Guardrails:

- Dashboard strategy support is optional first.
- Dashboard strategy and generated YAML must read the same mapping/diagnostics truth.
- No dashboard state may invent backend state.
- No tappable chip may create a hidden control path.
- Grouped UI language must preserve selected lane, active alert or CO state, gate
  state, degraded/missing telemetry, and unavailable-output visibility on the
  primary surface.
- Alert red, CO emergency dominance, disabled/gated states, unavailable states, and
  readable contrast must remain unmistakable.

Risk posture:

- Current allowed gate: opt-in generated-card/native-strategy display after Phase 1
  fixtures and Phase 2 telemetry contracts exist.
- Blocked until: generated YAML and native strategy read the same mapping/diagnostics
  truth, drill-downs have a read-only interaction contract, and `dump_cards` fallback
  parity is proven.
- Rollback path: disable native strategy/interaction support and keep `dump_cards` as
  the supported export path; runtime and entity semantics must remain unchanged.

Likely owners:

- Aetherwing: dashboard strategy, generated-card parity, service/mapping work.
- Aetherbite: orchestration-display UX experiment design.
- Bella: UI truth audit and release-boundary review.

Change types:

- Generated-card.
- UX-only.
- Diagnostics-only.
- Service/mapping changes if explicitly approved.

Required validation:

- Generated YAML export and native strategy output parity checks.
- Mobile/tablet/gallery rendering checks.
- Placeholder/pruning scan.
- Optional frontend dependency behavior check.
- Accessibility contrast review for visual state changes.
- Home Assistant validation for dashboard loading and frontend caching behavior.

### Phase 4 - Optional Future-Facing Intelligence Expansion

Scope:

- Longer-term environmental stability layers such as exposure windows, recovery
  quality, sleep suitability, comfort drift, room imbalance history, and
  property-protection framing.
- Future deterministic narrative patterns after raw telemetry contracts exist.
- Optional public docs for implemented environmental stability features.

Guardrails:

- No fake AI narration.
- No probabilistic advice without deterministic inputs, confidence rules, and
  suppressible output.
- No forecast or prediction text may appear when required inputs, sample history,
  confidence, or suppression contracts are incomplete.
- No hidden control path.
- No outcome-layer sensor may override lane priority, gates, alert hierarchy,
  humidifier independence, or output safety.
- Any user-facing "intelligence" claim must be traceable to runtime data,
  diagnostics, mappings, or documented confidence rules.

Risk posture:

- Current allowed gate: governance-only contract only, unless the work is decomposed
  into diagnostics-only or read-only telemetry slices.
- Blocked until: data-volume limits, recorder safety, history window, privacy posture,
  entity semantics, and suppression rules are defined.
- Rollback path: remove optional diagnostics/telemetry/UX surfaces and preserve the
  deterministic v2.0.6 baseline; no future-facing layer may become required for core
  humidity control.

Likely owners:

- Aetherbite: exploratory proposal drafting.
- Aetherwing: constrained implementation once contracts are approved.
- Bella: coherence, privacy, release semantics, and source-of-truth review.

Change types:

- Telemetry.
- Diagnostics.
- UX.
- Runtime read-only first.
- Runtime control only by separate approved proposal.

Required validation:

- Formal proposal promotion before implementation.
- Data-volume and recorder-safety review.
- Home Assistant restart and persistence validation.
- Regression coverage proving no lane-control side effects.
- Public/private documentation split review before publishing examples or screenshots.

## V2.1 Experimental UX Layer

The Harmonic Air Control draft belongs here, not in v2.0.6.

### Safe UI Evolution

Candidate slices:

- Idle and humidify wording cleanup.
- Multi-AQ display grouping using existing helpers.
- Reduced duplicate text in reason/display surfaces.
- Generated-card-only visual grouping where primary safety truth remains visible and
  raw ownership remains visible or reachable.

Allowed only when:

- It is display-only.
- It uses existing runtime truth.
- It ships with fixtures for active and degraded states.
- It preserves primary-surface visibility for selected lane, alert, CO emergency,
  gate, isolation, degraded telemetry, unavailable outputs, and missing-data
  conditions.

### Risky Semantic Abstraction

Candidate slices:

- Unified automation-family phrasing that remains display-only.
- Humanised "engine + trigger narrative".
- "Stabilising", "balancing", or "assist integrity" wording.
- AQ plus humidifier orchestration-display summaries.

Required first:

- Runtime-owned telemetry fields or an explicit display contract.
- Raw fallback text.
- Confidence/suppression rules where data is incomplete.
- Explicit source attribution for every intelligence-sounding phrase.
- Bella semantic continuity review.

### Future Orchestration Display Architecture

Candidate slices:

- Native dashboard strategy support.
- Contextual read-only drill-downs from primary chips.
- Composite harmonic visual language.
- Long-term environmental platform framing. Avoid public/runtime wording that makes
  HI sound like a separate autonomous operating system.

Required first:

- Interaction contract.
- Accessibility contrast review.
- Generated-card/native-strategy parity validation.
- Explicit release-boundary proposal.

## Long-Term Platform Direction

Humidity Intelligence should evolve from humidity automation toward explainable
environmental stability intelligence, but only through deterministic, inspectable,
and reversible layers.

Long-term direction:

- Stability, exposure, comfort drift, room imbalance, recovery behavior, and system
  integrity become interpretation layers above the deterministic engine.
- Dashboard delivery becomes less manual over time, but generated YAML remains the
  fallback until a native strategy is proven.
- Public docs may eventually describe environmental stability features, but only after
  contracts are implemented and validated.
- Optional frontend cards remain optional display dependencies, never backend control
  dependencies.
- Release cadence should prefer small coherent PRs over broad platform rewrites.

## Deferred / Watch Items

- Post-release Home Assistant compatibility checks remain useful before any v2.0.6
  patch, v2.0.7 maintenance claim, or v2.1 promotion claim.
- Normal pytest remains locally blocked unless Home Assistant test dependencies or
  collection isolation are added.
- Home Assistant 2026.5 dashboard strategy registration is a v2.1 input, not a
  v2.0.6 feature.
- GitHub/HACS release promotion for future versions must verify branch/version
  governance before any stable manifest version is used.
- Publish/auth path must be verified before promising a push.
- Manual sync is no longer part of normal work. If importing from a retired reference
  folder is unavoidable, copy path-preservingly into the canonical checkout or active
  worktree, verify ignored/local-only boundaries, and validate there before treating
  the result as release truth.
- Optional frontend dependency inspection must keep returning explicit non-blocking
  `not_inspectable` rather than false negatives when Lovelace internals are
  unavailable.
- Public docs, screenshots, examples, release notes, and test fixtures must not
  include private entity IDs, private device IDs, local paths, or user-specific
  telemetry.

## Architectural Risks

1. Semantic abstraction hiding runtime truth
   - Risk: humanised copy makes the system sound smarter while hiding lane, trigger,
     source, gate, alert, or missing-data truth.
   - Control: safety-critical truth must remain visible on the primary surface when
     active. Supporting raw operational detail may be reachable, and richer wording
     needs deterministic telemetry fields.

2. V2.1 ideas being backfilled into v2.0.6 history
   - Risk: post-release docs or polish make shipped v2.0.6 sound like it included
     future Environmental Stability Intelligence features.
   - Control: classify every future-facing candidate separately and reject anything
     that implies new telemetry, entity semantics, service output, or runtime behavior
     in v2.0.6.

3. Stability Score becoming hidden control input
   - Risk: a score intended for explanation starts influencing lane decisions.
   - Control: make Phase 2 score read-only first, componentized, suppressible, and
     covered by explicit no-control tests.

4. Dashboard strategy drift from generated YAML truth
   - Risk: native strategy and `dump_cards` tell different stories.
   - Control: share mapping/diagnostics truth and validate parity until strategy is
     proven.

5. Interaction chips creating hidden control paths
   - Risk: display chips become ambiguous controls.
   - Control: require an interaction contract; default drill-downs to read-only.

6. System Integrity becoming a vague health badge
   - Risk: unrelated runtime, mapping, dashboard, diagnostic, and optional frontend
     states collapse into one reassuring or alarming label.
   - Control: keep integrity componentized, expose unavailable/suppressed reasons,
     and preserve optional dependency status as non-blocking.

7. Optional frontend dependency status becoming a backend blocker
   - Risk: missing or uninspectable Lovelace resources look like runtime failures.
   - Control: preserve optional/non-blocking dependency semantics.

8. Local workspace state being mistaken for release truth
   - Risk: ignored planning docs, retired reference folders, or parent-folder Git state
     mislead release decisions.
   - Control: make release claims only from the canonical GitHub checkout or its
     worktrees after status, ignored-boundary, and public-safety checks.

## Open Questions

- What exact Stability Score formula should ship first, and how should each component
  be weighted, clamped, exposed, and suppressed?
- Should outcome-layer sensors be enabled by default, optional, or introduced behind
  an advanced setup/options toggle?
- Should humanised wording replace the current reason text, sit beside it, or appear
  as a concise secondary field with raw reason always available?
- Which raw runtime fields are required before richer trigger narratives can be
  generated safely?
- Should temperature comfort eventually become a separate setup step, or stay inside
  Global Gates for setup simplicity with post-config editing under Thresholds &
  Comfort?
- How should native dashboard strategy support coexist with `dump_cards`, exported
  YAML review, frontend resource loading, and HACS constraints?
- What fixture set is sufficient to approve the first Harmonic display experiment?
- Should public docs eventually include a trimmed roadmap, or should roadmap thinking
  remain local until v2.1 contracts are implemented?
- Should normal pytest be made runnable locally with Home Assistant test dependencies,
  or should the direct sanity harness remain the primary local fallback?

## Not Planned

- No integration rename.
- No hidden control paths outside the deterministic engine.
- No parallel output writers.
- No dashboard logic that invents state not backed by configured entities, HI runtime
  sensors, mappings, diagnostics, or explicit telemetry contracts.
- No fake AI narrative, probabilistic advice, or untraceable insight generation.
- No prediction or forecast wording when slope, sample history, time window,
  confidence data, or suppression contracts are weak, missing, stale, ambiguous, or
  unspecified.
- No private entity IDs in public docs, examples, generated cards, screenshots, or
  tests.
- No architecture rewrite as a v2.0.6 follow-up or documentation cleanup.

## Review Checklist Before Roadmap Or Proposal Promotion

Run this checklist before treating any roadmap item as implementation-ready:

- Coherence audit: confirms the slice fits `DESIGN_BRIEF.md`, `PROJECT_SUMMARY.md`,
  root `PROPOSALS.md`, and current implementation truth.
- Release-boundary audit: confirms whether the work belongs to post-v2.0.6
  maintenance, v2.1 staging, or long-term watch.
- Semantic continuity review: confirms runtime lane truth, humidifier independence,
  alert hierarchy, and entity semantics remain intact.
- Runtime/UI truth alignment review: confirms generated UI, diagnostics, services,
  and release checks are backed by the same source of truth.
- Validation plan review: confirms the exact local and Home Assistant checks required
  before the slice is called complete.
