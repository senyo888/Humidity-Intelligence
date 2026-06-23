# V2.0.7 Degraded Alert UI Truth Separation

## Metadata

```yaml
proposal_id: HI-PROP-20260608-001
proposal_urn: urn:hi:proposal:20260608:001:v207-degraded-alert-ui-truth-separation
title: V2.0.7 Degraded Alert UI Truth Separation
created: 2026-06-08
category: ui
target_version: v2.0.7
authority_status: implemented
state: IMPLEMENTED
owner: Aetherwing
risk_level: medium
runtime_impact: ui-only
affected_surfaces:
  - proposal-governance
  - generated-ui
  - public-docs
rollback_defined: true
expiry_or_review_date: 2026-06-22
bella_approved: true
aetherwing_validated: true
ha_lab_validated: advisory_read_only
release_candidate_validated: warning_only
entity_contract_changed: false
service_contract_changed: false
lane_order_risk: false
stable_runtime_risk: false
implemented_in: v2.0.7
release_candidate_validation_note: stable-instance availability warnings remain non-blocking advisories
ha_lab_validation_note: 2026-06-23 HA Lab identity, HI presence, scenario-matrix read-only baseline, and Stage 3 runtime readiness passed for commit 55dc2b9; rendered UI was not validated
closed: 2026-06-23
```

## Closure Status

This proposal is now a historical governance record. The v2.0.7 implementation moved
red control-row styling to selected alert/CO runtime truth, kept degraded or unmapped
alert candidates in reason text, and preserved backend lane ordering and entity
semantics. HA Lab validation remains separate advisory evidence and is not claimed by
this proposal record as rendered-UI approval. The 2026-06-23 HA Lab run confirmed the
lab target identity, HI install/diagnostics presence, read-only baseline, and Stage 3
runtime readiness for commit `55dc2b9`.

## Scope

Draft a review-gated v2.0.7 proposal for correcting a stable dashboard truth issue
where the control row below Current Air Control can stay red after the selected
runtime lane clears. The observed stable case is caused by raw environmental danger
binary sensors remaining active for a degraded or unmapped alert candidate while the
backend correctly reports a non-alert runtime mode.

This proposal is documentation and governance only. It does not authorize card edits,
runtime edits, entity changes, service changes, dashboard regeneration, release
promotion, Home Assistant mutation, or HACS packaging changes.

## Stable-Instance Evidence

Sanitized evidence from local stable diagnostics shows:

- The installed line is v2.0.6 stable.
- `HI Air Control Mode` is `normal` with display `NORMAL`.
- `HI Air Control Reason` reports the system is armed, no lane needs to run, and
  skipped alert candidates continue to the next eligible priority instead of blind
  boost.
- The raw humidity danger binary sensor is `on` because one unmapped room is above
  the active Summer high-risk threshold.
- `HI Active Alert Context` contains degraded alert telemetry for that unmapped room:
  humidity danger and mould risk candidates are degraded, have no resolved zone, and
  have no outputs.
- Configured zones include a Zone 1 room and a Zone 2 room, but not the degraded
  alert candidate room.
- CO emergency is off, AQ active switches are off, and the relevant configured alert
  switch is off.
- Release-check unresolved optional alert placeholders are present for optional alert
  slots while self-check reports no unresolved placeholders by card. Treat that as a
  separate validation/reporting noise candidate unless future source review proves it
  participates in the red-row symptom.

The public proposal intentionally does not include private room names, private entity
IDs, raw telemetry dumps, or machine-specific paths.

## Root Cause

The backend behavior is correct: degraded or unmapped alert candidates must remain
visible in reason text and diagnostics, but must not blindly select an output lane.

The UI issue is narrower. [ui/cards/v2_mobile.yaml](../../ui/cards/v2_mobile.yaml)
and [ui/cards/v2_tablet.yaml](../../ui/cards/v2_tablet.yaml) already use backend
runtime mode and active alert switch/context logic for the main Current Air Control
panel border, status chip, and alert-context chip. The separate `Ready / Zone 1 /
Zone 2 / AQ` row still derives red styling from raw danger binary sensors:

- `binary_sensor.humidity_danger`
- `binary_sensor.condensation_danger`
- `binary_sensor.mould_danger`
- `input_boolean.air_co_emergency_active`

[ui/register.py](../../ui/register.py) maps those canonical placeholders to generated
HI binary sensors. That means environmental risk truth can make output-control lane
buttons look like an active alert command even when `sensor.air_control_mode` is
`normal`, `air_quality`, or another non-alert mode and the alert candidate was
intentionally skipped as degraded or unmapped.

## Desired UI Behavior

Separate three meanings cleanly:

1. Actionable selected lane: red control-row styling only when backend runtime truth
   says an alert or CO emergency lane is selected, or backend-owned alert activity
   state says an actionable alert lane is currently selected.
2. Degraded or unmapped alert candidate: visible reason-panel context when
   `sensor.active_alert_context` attributes contain degraded alert telemetry and no
   actionable alert lane is selected. The later
   local Current Air Control degraded-context proposal narrows this surface so
   unmapped alert candidates do not occupy primary chip-row space.
3. Environmental risk readings: humidity, mould, condensation, AQ, and temperature
   chips may still show risk colors based on telemetry, but those colors must not make
   output-control lane buttons imply a command state.

The Current Air Control mode remains backend truth: `NORMAL`, `AQ`, `GLOBAL GATE`,
`ALERT`, `CO EMERGENCY`, or the current backend-owned display value.

## Non-Goals

- Do not change lane priority, alert hierarchy, CO emergency behavior, humidifier
  behavior, AQ ownership, global-gate behavior, output writes, or alert resolution.
- Do not suppress degraded/unmapped alert candidates from reason text, diagnostics, or
  active-alert telemetry.
- Do not introduce observed-room-specific, room-specific, entity-specific, or
  installation-specific logic into public cards, tests, screenshots, docs, or
  examples.
- Do not add hidden automations, extra output writers, synthetic entities, or
  card-only mode inference.
- Do not treat optional alert placeholder release-check noise as the red-row cause
  without separate evidence.

## Recommended Implementation Approach

Preferred future implementation: update the generated v2 mobile and tablet card
templates so the `Ready / Zone 1 / Zone 2 / AQ` row colors by selected runtime lane
instead of raw danger binary sensors.

The future card change should:

- Use `sensor.air_control_mode` as the primary lane truth.
- Treat red as active only for `co_emergency`, backend alert modes, or backend-owned
  actionable alert activity switches that match the existing active alert detection
  logic used by Current Air Control.
- Keep Zone 1, Zone 2, AQ, gate, paused, manual override, disabled, and normal styling
  aligned with current mode semantics.
- Derive degraded/unmapped reason context from
  `sensor.active_alert_context.attributes.alert_telemetry[*].degraded === true` only
  when no actionable alert lane is selected.
- Surface unmapped alert context in the Current Air Control reason area, not as a
  primary chip or red output-control row state.
- Keep environmental risk chips red/yellow when telemetry truth warrants it.

This is the smallest release-safe correction because the backend already exposes the
right distinction: selected runtime lane versus degraded alert candidate telemetry.

## Alternative Approaches Rejected Or Deferred

### Keep Raw Binary Red Row

Rejected. It preserves environmental risk visibility but causes a false command-state
signal. The row visually reads like an alert lane is commanding outputs when the
backend intentionally skipped the candidate.

### Add A Backend-Owned UI Severity Helper

Deferred. A helper such as a card severity sensor could make template logic simpler,
but it adds a new semantic surface, entity contract, diagnostics expectations, docs,
and migration/restart considerations. That may be justified later if card logic grows,
but it is not required for this narrow stable truth correction.

### Suppress Raw Danger Binary Sensors For Unmapped Rooms

Rejected. The environmental risk remains real and should stay visible. Suppressing raw
danger sensors would weaken diagnostics and risk truth to solve a presentation problem.

## Files Likely Affected In A Future Implementation

- [ui/cards/v2_mobile.yaml](../../ui/cards/v2_mobile.yaml)
- [ui/cards/v2_tablet.yaml](../../ui/cards/v2_tablet.yaml)
- [tests 2/test_runtime_card_sanity.py](<../../tests 2/test_runtime_card_sanity.py>)
- [README.md](../../README.md), if user-facing generated-card refresh guidance or UI
  truth wording needs a release note
- [ARCHITECTURE.md](../../ARCHITECTURE.md), only if the UI truth contract needs
  explicit control-row wording
- [ui/register.py](../../ui/register.py), only if future review chooses a
  backend-owned helper or mapping change; not expected for the preferred card-only
  approach
- [services.py](../../services.py), only if generated-card validation or release-check
  reporting for optional placeholders is separately corrected; not expected for the
  red-row fix

## Runtime Impact

No Home Assistant runtime impact for this proposal-only artifact.

For the recommended future implementation, runtime behavior should remain unchanged:
no lane-order change, no output-write change, no alert-resolution change, no CO change,
no AQ change, no humidifier change, no config-flow change, and no service-contract
change.

## Entity Semantics Impact

None for this proposal. The preferred future implementation should not change public
entity semantics.

## Generated Dashboard / UI Impact

None for this proposal until implementation is separately approved.

If implemented later, generated v2 mobile/tablet cards would change visually:

- The control row would stop turning red solely because raw danger binary sensors are
  `on`.
- Degraded/unmapped alert candidates would remain visible in reason text when no
  alert lane is selected, without occupying primary chip-row space.
- Existing environmental telemetry chips could still show red/yellow risk colors.

Users with Manual dashboard cards would need to rerun `humidity_intelligence.dump_cards`
and paste refreshed YAML after the implemented card-template change.

## Migration / Restart Impact

No migration required. No restart required for this proposal-only work.

For the preferred future implementation, no migration should be required. A Home
Assistant restart or integration reload may be needed only to load updated integration
files, and generated Manual cards would need refresh/export/re-paste to show the UI
change.

## Deterministic Lane-Order Risk

Low if the preferred card-only approach is followed. The change would render existing
backend truth differently but would not influence lane selection, priority resolution,
output writes, timers, gates, or alert handling.

Any backend helper alternative would need a separate Aetherwing contract review because
it would add a new semantic surface, even if lane order remained unchanged.

## UI Truth Consistency Risk

Medium before implementation because the stable UI can currently imply an alert output
lane when the backend selected `normal` or another non-alert mode.

Low after the preferred implementation if the row keys off backend-selected runtime
lane and degraded candidates remain in reason text rather than primary chip or red
command-state surfaces.

## Validation Plan

Minimum validation for a later implementation:

- Run targeted card sanity tests covering v2 mobile/tablet templates.
- Add or update a regression assertion that raw danger binary sensors alone cannot make
  the control row red when `sensor.air_control_mode` is `normal` and active alert
  activity is absent.
- Add or update a regression assertion that degraded alert telemetry can produce amber
  degraded context without red actionable alert-row styling.
- Verify mapped/generated cards do not ship private entities, unresolved placeholders,
  malformed structures, empty conditional containers, or stale fallback IDs.
- Run:
  - `python3 scripts/check_proposal_links.py`
  - `python3 -m unittest 'tests 2/test_proposal_links.py'`
  - targeted runtime/card sanity tests from `tests 2/test_runtime_card_sanity.py`
  - `git diff --check`
  - `git status --short`
  - `git ls-files -ci --exclude-standard`

Stable diagnostics re-check after implementation should confirm:

- runtime mode remains backend-owned;
- degraded alert candidates remain visible in reason/diagnostics;
- the control row no longer shows a red actionable-lane state for skipped degraded
  candidates;
- optional alert placeholder release-check noise is either unchanged and documented as
  separate, or fixed by a separately approved validation/reporting change.

## HA Lab Read-Only Check

Performed on 2026-06-08 against the approved HA Lab target with targeted GET-only
checks. No services were called, no bulk state scan was performed, no dashboard export
was requested, and no restart/reload or helper mutation occurred.

Observed HA Lab evidence:

- Identity preflight passed against Home Assistant `2026.5.4`.
- Scenario-matrix read-only baseline passed: current first-slice state is normal,
  numeric, and no lane currently needs to run.
- Backend mode/reason source capture passed; rendered UI was not validated.
- Targeted UI-truth reads observed:
  - `sensor.humidity_intelligence_hi_air_control_mode`: `normal`, display `NORMAL`.
  - `sensor.humidity_intelligence_hi_air_control_reason`: system armed, current house
    humidity `47.5%`, no lane currently needs to run.
  - `sensor.humidity_intelligence_hi_active_alert_context`: `None`, with zero
    `alert_telemetry` entries and zero degraded entries.
  - `binary_sensor.humidity_intelligence_hi_humidity_danger`: `off`, threshold `68.0`.

Interpretation: HA Lab was healthy and not currently reproducing the degraded-alert
red-row condition. That is acceptable for this proposal stage because the proposal is
grounded in stable diagnostics and source inspection, while the HA Lab check confirms
the live lab baseline is safe before any future implementation work.

## Rollback Safety

Proposal rollback is simple: remove this artifact and any matching local proposal
ledger entry.

Future implementation rollback should be safe if limited to v2 card templates and
tests: revert the card-template diff, regenerate/export cards, and re-run the same
card sanity checks. No entity migration or data repair should be required for the
preferred approach.

## House-Agent Review Log

### Aetherbite Findings

Options considered:

1. Keep the row red for any raw danger signal.
   - Strong risk visibility, but poor trust because it conflates environmental risk
     with selected output command state.
2. Change the control row to selected-lane colors and add amber degraded context.
   - Best scanability and least surprise: red means actionable selected alert/CO lane,
     amber means degraded attention needed, risk chips still show environmental truth.
3. Add a backend-owned severity helper for all card color states.
   - Potentially clean long-term, but too much semantic surface for this narrow issue.

Recommendation: option 2. It preserves trust by making the command row mean command
state, while still showing degraded risk context without making users think HI is
boosting a zone.

### Bella Findings

The recommendation matches [ARCHITECTURE.md](../../ARCHITECTURE.md) and README truth
principles:

- backend runtime remains authoritative;
- degraded/unmapped alerts remain visible and safely skipped;
- UI does not invent lane logic;
- raw risk truth is not suppressed;
- generated dashboards remain backend/config/diagnostics truth surfaces;
- no hidden behavior drift is introduced.

Docs to revisit if implementation proceeds:

- [ARCHITECTURE.md](../../ARCHITECTURE.md) only if the control-row distinction needs to
  become explicit in the UI truth contract;
- [README.md](../../README.md) or release notes if users need dashboard refresh
  guidance for the card visual correction.

### Aetherwing Findings

Exact future implementation surfaces are the v2 mobile/tablet card templates and
targeted card sanity tests. [ui/register.py](../../ui/register.py) already maps
canonical placeholders to HI entities; that mapping explains the symptom but does not
need to change for the preferred approach.

Backend runtime tests already cover degraded/unmapped alert candidates continuing to
the next eligible lane without blind boost. The missing coverage is presentation-level:
the control row should not style itself as a red alert lane from raw danger binary
sensors alone.

Deterministic lane-order risk is low for card-only work. UI truth consistency risk is
the actual issue and should be reduced by moving red control-row styling to selected
runtime lane truth.

### Conflict Resolution

All lanes converge on a card-template-first proposal. Backend helper work remains
deferred until there is evidence that card-only logic cannot stay maintainable or
truthful.

## Senyo Approval Gate (Historical)

FINAL VERDICT: IMPLEMENTED IN V2.0.7.

IMPLEMENTATION ALLOWED: CLOSED; no further implementation is authorized by this proposal.

SENYO RELEASE REVIEW REQUIRED: YES.

This proposal remains in the repository as the public governance record for the
implemented UI truth correction. Future changes require a new proposal, issue, or
release patch with its own validation evidence. This proposal closure does not
approve tagging, publishing, or GitHub release creation.
