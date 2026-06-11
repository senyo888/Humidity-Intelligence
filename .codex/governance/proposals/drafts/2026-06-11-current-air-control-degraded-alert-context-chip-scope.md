# Current Air Control Degraded Alert Context Chip Scope

## Metadata

```yaml
proposal_id: HI-PROP-20260611-001
proposal_urn: urn:hi:proposal:20260611:001:current-air-control-degraded-alert-context-chip-scope
title: Current Air Control Degraded Alert Context Chip Scope
created: 2026-06-11
category: ui
target_version: v2.0.7
authority_status: implemented
state: TESTED
owner: Senyo
risk_level: medium
runtime_impact: ui-only
affected_surfaces:
  - proposal-governance
  - generated-ui
  - diagnostics
  - validation-tooling
rollback_defined: true
expiry_or_review_date: 2026-06-25
bella_approved: true
aetherwing_validated: true
ha_lab_validated: false
release_candidate_validated: false
entity_contract_changed: false
service_contract_changed: false
lane_order_risk: false
stable_runtime_risk: false
```

## Title

Current Air Control Degraded Alert Context Chip Scope

## Brief Diagnosis

The current v2.0.7 Current Air Control card templates can show a prominent
`DEGRADED ALERT CONTEXT` chip when `active_alert_context` telemetry contains a
degraded alert candidate, even when no alert lane is selected and another lane
such as AQ is the current deterministic runtime decision.

That presentation is truthful in the narrow sense that a degraded alert candidate
exists, but it spends chip-row attention on an unmapped alert output condition and
can make the chip row look like there is an active or selectable degraded control
lane. That is the wrong emphasis for Current Air Control.

The backend already records unmapped/degraded alert candidates in alert telemetry
and runtime reason text. The proposal is to keep that truth, but move it out of
the primary chip row and into plain reason-panel wording.

## Recommended Decision

Accept Senyo's recommendation with one refinement:

- Use degraded context as a fault/degradation window only when there is actual
  degraded backend truth, such as unavailable configured outputs, missing sensors,
  HI entity degradation, optional dependency failure, or skipped service support.
- Do not spend Current Air Control chip-row space on unmapped alert output lanes.
- Move unmapped-alert/no-automation explanation into the stage/reason field using
  humanised, grammatically correct text.
- Keep the selected runtime stage as the selected backend lane. For example, if AQ
  is the selected lane and an unmapped alert candidate exists, the stage remains
  `Stage: Air-quality assist running.` The unmapped alert becomes an `Alert:` or
  `Mapping:` line below it.

This should be a small generated-card/presentation proposal first. Backend wording
may be adjusted only if the existing runtime reason text cannot provide the clear
message without frontend invention.

## Non-Goals

- Do not add a new runtime lane.
- Do not add a new service path, helper, automation, or output writer.
- Do not change deterministic lane priority.
- Do not rename entities or alter entity semantics.
- Do not change config flow, options flow, HACS metadata, manifest metadata, or
  migrations.
- Do not mutate Home Assistant, HA Lab, dashboards, helpers, or runtime state as
  part of this proposal.
- Do not show last-known, last-good, or age values unless backend truth already
  provides them.

## Proposed UI Behavior

Current Air Control chip row:

- Keep the active mode/status chip.
- Keep AQ chips when AQ is active.
- Keep CO emergency chip when CO emergency is active.
- Keep active alert source/context chips only when the backend-selected runtime
  truth says an alert lane is active.
- Keep gate, humidifier, and isolation chips only when backed by existing runtime
  or mapped entity truth.
- Remove the standalone `DEGRADED ALERT CONTEXT` chip for unmapped alert output
  candidates.

Current Air Control reason panel:

- Keep the selected stage aligned with the actual runtime mode.
- Add unmapped alert context as a secondary explanation line when backend
  `alert_telemetry` or reason text reports an alert candidate that could not be
  safely mapped to a control output.
- Preserve the existing engine reason text unless a narrow backend wording change
  is approved.
- Avoid frontend-only risk logic. The card may format backend truth; it must not
  decide alert severity, zone mapping, output availability, or lane authority.

Fault/degradation window:

- Reserve degraded/fault language for actual degraded entities or dependencies:
  unavailable configured output, missing or unavailable configured sensor,
  unavailable mapped HI entity, optional frontend dependency failure, or service
  support/failure that backend diagnostics/runtime truth exposes.
- If the backend only reports an unmapped alert candidate, describe it as an
  unmapped alert/mapping issue rather than a general degraded control state.

## Proposed Wording Patterns

Runtime dashboard wording may include real configured room/output labels because
those are user-local runtime truth. Public tests, docs, examples, screenshots, and
proposal fixtures must use sanitized labels.

Unmapped alert candidate:

```text
Alert: Mould risk is active in the resolved room, but that room is not mapped to an output lane, so no alert automation was run for it.
```

Resolved room exists but no enabled zone maps it:

```text
Alert: Humidity danger is active in the resolved room, but no enabled zone maps that room, so HI skipped alert boost and continued to the next eligible lane.
```

Zone exists but has no outputs:

```text
Alert: Condensation risk is active in the resolved zone, but that zone has no configured fan outputs, so no alert boost was run.
```

Output/entity degradation:

```text
Output fault: the configured output is unavailable, so HI skipped that output and did not assume control succeeded.
```

Sensor degradation:

```text
Sensor fault: required humidity telemetry is unavailable, so automation is standing down until the configured source recovers.
```

Optional dependency degradation:

```text
Optional dependency degraded: the frontend dependency status is unavailable; backend control remains available.
```

Age/last-known wording:

```text
Last good update: use only when backend diagnostics or Home Assistant state metadata exposes a real timestamp or age.
```

## Data And Source-Of-Truth Requirements

- Active lane/status must come from backend runtime mode and mapped runtime
  entities.
- Active alert chip text must come from active alert context only when an alert
  lane is actually selected.
- Unmapped alert messaging must come from backend alert telemetry and runtime
  reason truth.
- Entity degradation must come from diagnostics/runtime data such as unavailable
  configured entities, mapped entity state, output state, frontend dependency
  status, or explicitly recorded service skip/failure truth.
- Last-known or last-good periods may not be invented in YAML/card JavaScript.
- Public-facing examples must not expose private entity IDs, device IDs, room
  names, telemetry values, helper names, or local paths.

## Files Likely Affected If Later Approved

- `[ui/cards/v2_mobile.yaml](../../../../ui/cards/v2_mobile.yaml)`
- `[ui/cards/v2_tablet.yaml](../../../../ui/cards/v2_tablet.yaml)`
- `[tests 2/test_runtime_card_sanity.py](../../../../tests%202/test_runtime_card_sanity.py)`
- `[automations/engine.py](../../../../automations/engine.py)`, only if backend-owned reason wording is approved
- `[diagnostics.py](../../../../diagnostics.py)` or `[services.py](../../../../services.py)`, only if a later real fault/degradation window
  needs more structured backend truth
- `[README.md](../../../../README.md)`, `[CHANGELOG.md](../../../../CHANGELOG.md)`, or `[docs/release-governance.md](../../../../docs/release-governance.md)`, only if the
  implemented change becomes release-facing user truth

## Runtime Impact

Preferred implementation impact is presentation-only:

- no lane-order change
- no control-loop change
- no output-write change
- no helper mutation
- no entity semantics change
- no service schema change
- no migration

If later implementation changes backend reason wording, runtime behavior still
must remain unchanged; only explanatory text changes.

## UI Impact

- Current Air Control chip row becomes less noisy and less likely to imply a
  selected degraded alert lane.
- Unmapped alerts remain visible in the reason panel.
- Selected lane truth stays dominant.
- Real degraded output/entity/dependency states remain eligible for clear fault
  presentation when backed by backend truth.

## Entity Semantics Impact

None proposed.

Any future structured fault window that adds new entity attributes, diagnostics
fields, or state semantics requires a separate review before implementation.

## Migration Impact

None.

If generated card templates are changed later, users must refresh/export generated
cards through the normal supported card update path before existing dashboards show
the new wording.

## Validation Plan

Proposal-only validation:

- Check proposal metadata against `[.codex/governance/proposals/proposal_template.md](../proposal_template.md)`.
- Check draft index row alignment in `[.codex/governance/proposals/drafts.md](../drafts.md)`.
- Run proposal link validation where available.
- Run `git diff --check`.

Implementation validation if later approved:

- `python3 'tests 2/test_runtime_card_sanity.py'`
- Targeted assertions that generated cards no longer contain
  `DEGRADED ALERT CONTEXT`.
- Targeted assertions that unmapped alert reason text remains visible.
- `python3 -m py_compile automations/engine.py diagnostics.py services.py sensors/core.py`
  if backend wording or diagnostics code changes.
- `python3 scripts/check_version_governance.py` if release/version surfaces change.
- HA Lab card export/render validation only after explicit HA Lab mutation approval.

## Risks And Rollback Safety

Risk: unmapped alerts become too quiet.

Mitigation: keep explicit reason-panel text with alert type, resolved source context,
mapping failure, and no-automation result.

Risk: card JavaScript starts parsing backend reason text too aggressively.

Mitigation: prefer structured `alert_telemetry` where available. If more structure is
needed, add backend-owned diagnostics in a separate approved slice instead of
inventing frontend truth.

Risk: real output/entity degradation is still not prominent enough.

Mitigation: treat real output/entity/dependency degradation as a separate
backend-truth enhancement, with diagnostics support and validation, not as a reused
unmapped-alert chip.

Rollback:

- Revert the generated-card template change and associated test update.
- Regenerate/export cards through the normal supported card update flow.
- No data migration rollback is required.

## House-Agent Verdicts

Bella:

Accept. This aligns with the design brief: Current Air Control chips must be
display-only truth surfaces, alert chips should stay concise, and backend
deterministic lane truth remains authoritative. The proposal should be card-template
first, with backend wording only if necessary.

Aetherwing:

Accept with validation guardrails. The risk is UI truth drift from a generic
`degraded === true` frontend check. Real degradation needs structured backend truth.
Unmapped alert candidates should stay visible, but not as a primary chip that looks
like a selected lane.

Aetherbite:

Accept. `DEGRADED ALERT CONTEXT` is too abstract for a live dashboard. Users need
plain language: what alert exists, what source/room/zone was resolved, what mapping
failed, and whether automation ran.

## Implementation Status

Senyo approved implementation on 2026-06-11 after the review-only proposal pass.
The approved implementation is limited to generated-card presentation, focused card
sanity coverage, and release-facing wording alignment. It does not change runtime
control, lane ordering, entity semantics, service contracts, config flow, migration,
HACS metadata, Home Assistant state, HA Lab state, release authority, PR state, or tag
state.

Validation evidence for the implementation commit must be read from the commit/session
that stages this implementation. The required validation set is:

- `python3 'tests 2/test_runtime_card_sanity.py'`
- `python3 -m py_compile automations/engine.py diagnostics.py services.py sensors/core.py`
- `python3 scripts/check_proposal_links.py`
- `python3 -m unittest 'tests 2/test_proposal_links.py'`
- `python3 scripts/check_version_governance.py`
- `git diff --check`
- `git diff --cached --check`

## Final Verdict

Accepted and implemented as a bounded UI-truth presentation change.

Use the reason panel for unmapped alert/no-automation context. Reserve primary chip
space for selected lane/status and resolved active source context. Reserve degraded
or fault wording for actual degraded entities, outputs, HI entities, or optional
dependencies backed by backend truth.

```text
FINAL VERDICT: ACCEPTED AND IMPLEMENTED
IMPLEMENTATION_ALLOWED: YES
SENYO_REVIEW_REQUIRED: YES
```
