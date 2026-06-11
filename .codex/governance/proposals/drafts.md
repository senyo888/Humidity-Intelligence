# Draft Proposals

New proposal material starts here unless Bella explicitly recommends immediate promotion to root `[PROPOSALS.md](../../../PROPOSALS.md)`.

## Phase 1A Pruning Index

This file is the active draft index. Long-form drafts and reports are supporting
evidence only; they do not outrank this index, root `[PROPOSALS.md](../../../PROPOSALS.md)`, `[DESIGN_BRIEF.md](../../../DESIGN_BRIEF.md)`,
or approved runtime-protection contracts.

Expired drafts are stale by default. A stale draft must be reviewed, reclassified, or
archived before it can influence implementation, runtime validation, release wording,
generated UI, service/entity contracts, or HA Lab work.

| Draft | Pruning classification | State | Review / expiry date | Authority boundary |
| --- | --- | --- | --- | --- |
| Bella Amendment - HA Lab Phase 3D Follow-Up Hardening & Risk Closure | keep | TESTED | 2026-06-07 | Stopped after completed read-only readiness; current governance hardening gate only; no mutation authority. |
| AetherMite Draft - HI Lab Mock Telemetry & Boundary Exploration Layer | keep | TESTED | 2026-06-14 | Lab-only first-slice boundary and accepted-residue record; Phase 3A/3B/3C achieved; not release authority. |
| Bella Draft - Local Version Preservation & Rollback Safeguard | keep | TESTED | 2026-06-14 | Constrained stable v2.0.6 Phase 1 implemented in canonical checkout; no restore, HACS interception, runtime-control, generated-dashboard, or standalone release authority. |
| Bella Draft - Community Ideas & Proposals | keep | TESTED | 2026-06-28 | Implemented in canonical checkout commit `e91ae37`; no automated GitHub mutation, runtime, or release authority. |
| Bella Draft - Canonical Proposal URN and Lifecycle Tracking System | keep | TESTED | 2026-06-28 | Jules-approved governance metadata normalisation model; no runtime, registry, automation, root promotion, or release authority. |
| Bella Draft - Secret-Leak Prevention Hardening Layer | keep | TESTED | 2026-06-28 | Full-history baseline passed and required Gitleaks workflow job committed locally in canonical checkout commit `1285d28`; no push, GitHub settings mutation, or runtime authority. |
| Bella Draft - Codex Identity Registration Layer | keep | STAGED | 2026-06-29 | Jules approved staging; local TOML registry implementation applied and Aetherwing-validated; root promotion, publication, release, and runtime authority remain blocked. |
| Aetherwing Draft - V2.0.6 Runtime Telemetry And CO Clear Fixes | keep | TESTED | 2026-06-14 | Canonical v2.0.6 runtime/UI truth fixes implemented, reviewed, and included in stable v2.0.6; future maintenance still requires maintainer release sanity and approval. |
| Bella Addendum - HA Lab Mock Telemetry Six-Sensor Family Expansion | keep | TESTED | 2026-06-15 | HA Lab six-sensor helper/wrapper surface exact-readback validated; validation-tooling only; no runtime, UI, release, or root-promotion authority. |
| V2.0.7 PM2.5 House Aggregate Runtime Truth Fix | keep | REVIEW | 2026-06-21 | Required v2.0.7 runtime/entity-contract fix from Stage 3; no implementation or release authority until Bella/Aetherwing review and Senyo approval. |
| Config Flow Staged Refactor And Validation Proposal | keep | TESTED | 2026-06-23 | Official local proposal; Phases 1-5 implemented with validation evidence and Phase 6 HA Lab advisory acceptance passed; no runtime, dashboard, entity, release, stable HA, or migration authority. |
| Current Air Control Degraded Alert Context Chip Scope | keep | TESTED | 2026-06-25 | Senyo-approved UI truth implementation applied in the canonical checkout; unmapped-alert degradation no longer occupies primary chip-row space and no-automation context remains in reason text. |
| HI Two-Repo Governance Bridge | keep | TESTED | 2026-07-06 | Private maintenance companion bridge implemented as governance docs only; no runtime, UI, public docs, HACS, release, or root-promotion authority. |
| Aetherbite Draft - Harmonic Air Control Evolution | keep | IDEA | 2026-07-01 | Parked v2.1 exploratory UI wording direction; not a v2.0.x or runtime proposal. |
| AetherMite Draft - Home Assistant Lab Runtime Architecture | split | REVIEW | 2026-06-21 | Broad architecture reference, partially realized by governed HA Lab packets; not full architecture approval or release authority. |

## Canonical Metadata Fields

Active proposals must include the metadata block from
`[.codex/governance/proposals/proposal_template.md](proposal_template.md)` in their long-form artifact and in
the registry below before they can move beyond draft review.

```yaml
proposal_id:
proposal_urn:
title:
created:
category:
target_version:
authority_status:
state:
owner:
risk_level:
runtime_impact:
affected_surfaces:
rollback_defined:
expiry_or_review_date:
bella_approved:
aetherwing_validated:
ha_lab_validated:
release_candidate_validated:
entity_contract_changed:
service_contract_changed:
lane_order_risk:
stable_runtime_risk:
```

The registry is the Phase 1B normalisation surface. If a long-form artifact and this
index disagree, the proposal is stale until reconciled. The index remains the active
draft authority; long-form artifacts preserve supporting evidence.

Legacy rows marked `legacy-unassigned` are intentionally not backfilled by this
Phase 1B pass. Assign ID/URN metadata prospectively first, and backfill only active
v2.1 proposals when they are next touched.

| Draft | proposal_id | proposal_urn | title | created | category | target_version | authority_status | state | owner | risk_level | runtime_impact | affected_surfaces | rollback_defined | expiry_or_review_date | bella_approved | aetherwing_validated | ha_lab_validated | release_candidate_validated | entity_contract_changed | service_contract_changed | lane_order_risk | stable_runtime_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bella Amendment - HA Lab Phase 3D Follow-Up Hardening & Risk Closure | legacy-unassigned | legacy-unassigned | Bella Amendment - HA Lab Phase 3D Follow-Up Hardening & Risk Closure | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | TESTED | Bella | high | governance-only | proposal-governance; ha-lab-evidence; diagnostics | true | 2026-06-07 | true | true | true | false | false | false | false | false |
| AetherMite Draft - HI Lab Mock Telemetry & Boundary Exploration Layer | legacy-unassigned | legacy-unassigned | AetherMite Draft - HI Lab Mock Telemetry & Boundary Exploration Layer | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | TESTED | Aetherbite | medium | governance-only | proposal-governance; ha-lab-evidence; diagnostics; generated-ui | false | 2026-06-14 | true | true | true | false | false | false | false | false |
| Bella Draft - Local Version Preservation & Rollback Safeguard | legacy-unassigned | legacy-unassigned | Bella Draft - Local Version Preservation & Rollback Safeguard | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | TESTED | Bella | medium | service-contract | proposal-governance; services; diagnostics; release-docs; public-docs | true | 2026-06-14 | true | true | false | false | false | true | false | false |
| Bella Draft - Community Ideas & Proposals | legacy-unassigned | legacy-unassigned | Bella Draft - Community Ideas & Proposals | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | TESTED | Bella | low | governance-only | proposal-governance; public-docs | true | 2026-06-28 | true | true | false | false | false | false | false | false |
| Bella Draft - GitHub Wiki Public Support Manual Pilot | HI-PROP-20260607-001 | urn:hi:proposal:20260607:001:github-wiki-support-manual-pilot | GitHub Wiki Public Support Manual Pilot | 2026-06-07 | docs | none | implemented | TESTED | Bella | medium | docs-only | proposal-governance; public-docs; release-docs | true | 2026-06-21 | true | true | false | false | false | false | false | false |
| Bella Draft - Canonical Proposal URN and Lifecycle Tracking System | HI-PROP-20260529-001 | urn:hi:proposal:20260529:001:urn-lifecycle-tracking | Canonical Proposal URN and Lifecycle Tracking System | 2026-05-29 | governance | v2.0.6-beta.1 | governance-only | TESTED | Senyo | low | governance-only | proposal-governance | true | 2026-06-28 | true | true | false | false | false | false | false | false |
| Bella Draft - Secret-Leak Prevention Hardening Layer | HI-PROP-20260529-002 | urn:hi:proposal:20260529:002:secret-leak-prevention-hardening | Secret-Leak Prevention Hardening Layer | 2026-05-29 | security | none | implementation-authorized | TESTED | Bella | low | none | proposal-governance; public-docs; repository-security | true | 2026-06-28 | true | true | false | false | false | false | false | false |
| Bella Draft - Codex Identity Registration Layer | HI-PROP-20260530-001 | urn:hi:proposal:20260530:001:codex-identity-registration-layer | Codex Identity Registration Layer | 2026-05-30 | governance | none | implemented | STAGED | Bella | low | governance-only | proposal-governance; local-codex-governance | true | 2026-06-29 | true | true | false | false | false | false | false | false |
| Aetherwing Draft - V2.0.6 Runtime Telemetry And CO Clear Fixes | HI-PROP-20260531-001 | urn:hi:proposal:20260531:001:v206-runtime-telemetry-co-clear | V2.0.6 Runtime Telemetry And CO Clear Fixes | 2026-05-31 | runtime | v2.0.6 | implemented | TESTED | Aetherwing | high | runtime-control | proposal-governance; runtime-control; entities; generated-ui; release-docs; public-docs; ha-lab-evidence | true | 2026-06-14 | true | true | true | false | true | false | false | true |
| Bella Addendum - HA Lab Mock Telemetry Six-Sensor Family Expansion | HI-PROP-20260601-001 | urn:hi:proposal:20260601:001:ha-lab-telemetry-six-sensor-expansion | HA Lab Mock Telemetry Six-Sensor Family Expansion | 2026-06-01 | ha-lab | none | implementation-authorized | TESTED | Bella | medium | validation-tooling | proposal-governance; ha-lab-evidence; validation-tooling | true | 2026-06-15 | true | true | true | false | false | false | false | false |
| V2.0.7 PM2.5 House Aggregate Runtime Truth Fix | HI-PROP-20260606-001 | urn:hi:proposal:20260606:001:v207-pm25-house-aggregate-runtime-truth | V2.0.7 PM2.5 House Aggregate Runtime Truth Fix | 2026-06-06 | runtime | v2.0.7 | review-only | REVIEW | Aetherwing | medium | entity-contract | proposal-governance; runtime-control; entities; diagnostics; generated-ui; release-docs; public-docs; ha-lab-evidence | true | 2026-06-21 | false | false | false | false | true | false | false | true |
| Config Flow Staged Refactor And Validation Proposal | HI-PROP-20260609-001 | urn:hi:proposal:20260609:001:config-flow-staged-refactor-validation | Config Flow Staged Refactor And Validation Proposal | 2026-06-09 | governance | v2.0.7 | implemented | TESTED | Senyo | medium | config-options-flow-ux-only | proposal-governance; config-flow; validation-tooling; ha-lab-evidence | true | 2026-06-23 | true | true | true | false | false | false | false | false |
| Current Air Control Degraded Alert Context Chip Scope | HI-PROP-20260611-001 | urn:hi:proposal:20260611:001:current-air-control-degraded-alert-context-chip-scope | Current Air Control Degraded Alert Context Chip Scope | 2026-06-11 | ui | v2.0.7 | implemented | TESTED | Senyo | medium | ui-only | proposal-governance; generated-ui; diagnostics; validation-tooling | true | 2026-06-25 | true | true | false | false | false | false | false | false |
| HI Two-Repo Governance Bridge | HI-PROP-20260606-002 | urn:hi:proposal:20260606:002:two-repo-governance-bridge | HI Two-Repo Governance Bridge | 2026-06-06 | governance | none | implemented | TESTED | Senyo | low | governance-only | proposal-governance; maintenance-companion-governance; local-continuity-anchors | true | 2026-07-06 | true | true | false | false | false | false | false | false |
| Aetherbite Draft - Harmonic Air Control Evolution | legacy-unassigned | legacy-unassigned | Aetherbite Draft - Harmonic Air Control Evolution | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | IDEA | Aetherbite | medium | governance-only | proposal-governance; generated-ui | false | 2026-07-01 | true | false | false | false | false | false | false | false |
| AetherMite Draft - Home Assistant Lab Runtime Architecture | legacy-unassigned | legacy-unassigned | AetherMite Draft - Home Assistant Lab Runtime Architecture | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | REVIEW | Aetherbite | high | governance-only | proposal-governance; ha-lab-evidence; runtime-protection-contracts; validation-tooling; generated-ui; lab-deploy-link | false | 2026-06-21 | true | false | false | false | false | false | false | false |

## Draft Detail Records

The Phase 1A table above is the active index. Detail records below preserve context,
but entries marked `supersede`, `archive`, or `reject` are historical unless promoted
again through review.

### Current Air Control Degraded Alert Context Chip Scope

Status: Senyo-approved UI truth proposal implemented in the canonical checkout.

Classification: generated-card presentation / Current Air Control chip-row truth /
unmapped alert reason wording.

Runtime impact: UI-only. No lane ordering, runtime control, entity semantics,
service contract, config flow, migration, HACS metadata, Home Assistant mutation, or
release authority is included in this proposal.

Summary: The implemented proposal accepts the house-agent recommendation to remove
unmapped-alert degradation from primary chip-row prominence. Current Air Control keeps
selected lane/status and resolved active source context in the chip row, while
unmapped alert/no-automation details move into humanised reason text. Real
degraded/fault language remains reserved for backend-truth degradation such as
unavailable outputs, missing sensors, HI entity degradation, optional dependency
failure, or recorded service support/failure.

Boundary: This proposal authorizes only the committed generated-card presentation
slice and aligned tests/docs. It does not authorize dashboard export, Home Assistant
reload/restart, service calls, HA Lab mutation, release promotion, PR creation, push,
or tag creation. Public-facing examples must use sanitized labels and must not expose
private entity IDs, room names, telemetry values, helper names, or local paths.

Long-form artifact:
`[.codex/governance/proposals/drafts/2026-06-11-current-air-control-degraded-alert-context-chip-scope.md](drafts/2026-06-11-current-air-control-degraded-alert-context-chip-scope.md)`.

### Config Flow Staged Refactor And Validation Proposal

Status: Official local proposal / Phases 1-5 implemented / Phase 6 HA Lab advisory
acceptance passed / local governance ledger active.

Owner label: Senyo. Aetherbite, Bella, Aetherwing, and dormant AetherCore roles are
recorded in the long-form artifact as review lenses only; they do not grant runtime,
release, HA Lab, or autonomous implementation authority.

Classification: config-flow maintainability / contract-first staged refactor planning
/ validation-governance gate.

Runtime impact: Config/options-flow UX only. The staged implementation lane has not
changed deterministic lane ordering, entity semantics, service contracts, generated
dashboards/UI, manifest metadata, HACS metadata, migrations, translations, runtime
control code, stable Home Assistant state, or release authority.

Summary: Created the review gate for a staged config-flow refactor after the Phase 0
audit. Senyo later authorized bounded implementation and Phase 6 HA Lab advisory
acceptance. The long-form artifact now records Phase 1 guard tests, Phase 2/3
schema-helper extraction, Phase 4 alert save-helper extraction, Phase 5 alert form
payload dedupe, and Phase 6 HA Lab options alert-add validation with the
commands/results available for each phase.

Boundary: Only the completed Senyo-approved phase-scoped `config_flow.py` refactor
slices are authorized. Further runtime implementation, Home Assistant service calls,
reload/restart by Codex, helper mutation, dashboard mutation, entity semantic change,
generated dashboard logic change, release/tag/PR creation, and stable Home Assistant
access remain unauthorized. Root `[PROPOSALS.md](../../../PROPOSALS.md)` promotion is
now official local proposal status only; it is not release authority.

Long-form artifact:
`[.codex/governance/proposals/drafts/2026-06-09-config-flow-staged-refactor-and-validation.md](drafts/2026-06-09-config-flow-staged-refactor-and-validation.md)`.

### Bella Addendum - HA Lab Mock Telemetry Six-Sensor Family Expansion

Status: Draft addendum / implementation-authorized / Stage 2 local contract implemented
and tested / Stage 2B helper-backed HA Lab entity surface exact-readback validated /
validation-tooling only / no release authority.

Owner label: Bella. Aetherwing validated the safety boundary for the expansion and the
approved dry-run-first Stage 2B helper-creation packet. Senyo manually confirmed sensor
entities were added to HA Lab and service checks were run; raw service output is not
captured in this registry.

Classification: HA Lab mock telemetry six-sensor family expansion / helper-backed
telemetry input evidence / proposal-governance and lab-evidence sync.

Runtime impact: None to production Humidity Intelligence runtime. The packet changes
local HA Lab validation tooling/evidence only. It does not change production entity
semantics, service contracts, generated dashboards/UI, manifest metadata, HACS
metadata, release state, or deterministic lane ordering.

Summary: Expands the HA Lab mock telemetry surface from the four-sensor Phase 3A first
slice to six sensors per family across humidity, temperature, IAQ, CO, VOC, and PM2.5.
Stage 2B evidence confirms the approved helper/wrapper surface has 36 value helpers,
36 availability controls, and 36 sensor wrappers. Fresh read-only revalidation on
2026-06-06 reported `exists_exact=108` and performed no Home Assistant mutation. Stage
3 read-only runtime readiness also confirmed the 108 helper/wrapper surface, but
returned `CONFIGURATION_NOT_READY` because
`sensor.humidity_intelligence_hi_house_pm25_average` is missing from the current HA
Lab runtime truth surface.

Boundary: Further mutation, rollback/delete automation, dashboard mutation, fake
outputs, output/control entities, MQTT, production telemetry mirroring, release
promotion, and root `[PROPOSALS.md](../../../PROPOSALS.md)` promotion remain blocked
unless a new exact operation packet is approved.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-06-01-ha-lab-mock-telemetry-six-sensor-family-expansion.md](drafts/2026-06-01-ha-lab-mock-telemetry-six-sensor-family-expansion.md)`.
HA Lab addendum: `[.codex/lab/implementation/phase-3a-six-sensor-family-expansion-addendum.md](../../lab/implementation/phase-3a-six-sensor-family-expansion-addendum.md)`.
Latest exact readback evidence: `[.codex/lab/reports/2026-06-06T13-57-31Z-stage-2b-helper-creator-dry-run.md](../../lab/reports/2026-06-06T13-57-31Z-stage-2b-helper-creator-dry-run.md)`.
Latest Stage 3 runtime-readiness evidence: `[.codex/lab/reports/2026-06-06T14-39-27Z-stage-3-six-sensor-runtime-readiness.md](../../lab/reports/2026-06-06T14-39-27Z-stage-3-six-sensor-runtime-readiness.md)`.

### V2.0.7 PM2.5 House Aggregate Runtime Truth Fix

Status: Draft / review-only / required v2.0.7 fix / no implementation authority yet.

Owner label: Aetherwing. Bella review is required for source-of-truth and release
wording before promotion; Aetherwing review is required for runtime/entity-contract
risk before implementation.

Classification: PM2.5 aggregate runtime truth / entity-contract fix / HA Lab Stage 3
follow-up.

Runtime impact: Entity-contract impact. The proposal requires configured PM2.5
telemetry to expose `sensor.humidity_intelligence_hi_house_pm25_average` when usable
PM2.5 telemetry exists, and to degrade explicitly when PM2.5 telemetry is missing,
unknown, unavailable, or intentionally unconfigured. It must not change lane priority,
output writers, service contracts, or AQ lane ownership without separate approval.

Summary: HA Lab Stage 3 confirmed all 108 six-sensor helper/wrapper entities, but
returned `CONFIGURATION_NOT_READY` because
`sensor.humidity_intelligence_hi_house_pm25_average` returned `404`. VOC aggregate was
present and numeric. This is now a required v2.0.7 fix, not a helper-creation task.

Revisit gate: rerun Stage 3 only after the PM2.5 aggregate fix is committed and tested
in `senyo888-patch-1`, the tested package is pushed/deployed to HA Lab, and Senyo has
reduced the VOC aggregate before the next run.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-06-06-v207-pm25-house-aggregate-runtime-truth.md](drafts/2026-06-06-v207-pm25-house-aggregate-runtime-truth.md)`.
Stage 3 evidence: `[.codex/lab/reports/2026-06-06T14-39-27Z-stage-3-six-sensor-runtime-readiness.md](../../lab/reports/2026-06-06T14-39-27Z-stage-3-six-sensor-runtime-readiness.md)`.

### HI Two-Repo Governance Bridge

Status: Implemented / governance-only / private maintenance companion bridge / no
runtime, UI, HACS, release, or public-doc authority.

Owner label: Senyo. The proposal was approved for official proposal-process handling
through implementation on 2026-06-06. Bella, Aetherwing, and Aetherbite subsequently
returned `PASS` for docs-only maintenance repo commit/push and local ignored
governance continuity.

Classification: two-repo governance bridge / maintenance companion push points /
source-proof and redaction validation matrix.

Runtime impact: None. This proposal does not change deterministic lane ordering,
output writers, Home Assistant services, entity semantics, config flow behavior,
diagnostics logic inside HI, generated dashboards, release state, HACS metadata, or
public documentation truth.

Summary: Implements the approved bridge by adding `PUSH_POINTS.md` and
`VALIDATION_MATRIX.md` to the private `humidity-intelligence-maintenance` repo and
cross-linking them from the existing maintenance contract, safeguards, intake policy,
support playbook, release gates, and README. The bridge defines named handoff points
between canonical HI and the private maintenance companion while keeping canonical HI
authoritative for runtime, UI, entity, diagnostics, HACS, version, README, CHANGELOG,
and promoted proposal truth.

Boundary: No root `[PROPOSALS.md](../../../PROPOSALS.md)` promotion. No public docs
change. No scripts, workflows, sync jobs, issue automation, PR automation, release
automation, Home Assistant calls, dashboard generation, HACS metadata mutation, or
canonical runtime mutation. House-agent review narrowed commit/push to the maintenance
repo tracked docs only; ignored canonical governance, lab, sandbox, and memory anchors
remain local continuity evidence.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-06-06-two-repo-governance-bridge.md](drafts/2026-06-06-two-repo-governance-bridge.md)`.
Maintenance implementation files: `PUSH_POINTS.md` and `VALIDATION_MATRIX.md` in
the private `humidity-intelligence-maintenance` repo.

### Aetherwing Draft - V2.0.6 Runtime Telemetry And CO Clear Fixes

Status: Draft / implementation-authorized by Jules for Phase 3F fault remediation /
canonical v2.0.6 runtime fixes implemented and included in stable v2.0.6 / HA Lab
isolated probes passed / global-gate stale-alert regression validated / no
standalone release authority.

Owner label: Aetherwing runtime-fix procedure. Bella review remains required before
root promotion or release-candidate promotion because the packet changes entity
semantics and stable runtime behavior.

Classification: v2.0.6 runtime integrity fix / CO clear timing / missing telemetry
stand-down / entity truth update.

Runtime impact: Runtime-control and entity-contract impact. `sensor.humidity_intelligence_hi_air_control_mode`
may now report `telemetry_unavailable` when required humidity, or configured
temperature telemetry, is unavailable. CO emergency clear timing becomes bounded by an
engine-scheduled recheck at the two-minute clear-hold deadline. Service contracts and
generated card templates are unchanged.

Summary: Defines the correct path for moving the HA Lab-discovered runtime fixes from
the old HI Work folder into the canonical v2.0.6 branch. The procedure requires narrow
source transplant, regression tests, release-truth docs, HA Lab backup/SHA/restart
discipline, read-only baseline checks, isolated missing-telemetry probes, and explicit
release notes for the entity semantics change. Subsequent continuity commits also
covered global-gate humidity-danger alert preemption, tracked public contract wording,
and the time-gate `outside_action: pause` regression.

Boundary: This packet does not authorize wholesale old-folder sync, public inclusion
of local `.codex/lab` runner hardening, generated-dashboard mutation, release tagging,
root `[PROPOSALS.md](../../../PROPOSALS.md)` promotion, or CO pressure execution by default. The remaining full
matrix blocker is HA Lab transport or VM networking instability under repeated API
pressure and must not be misreported as a clean full-matrix pass.

Continuity update: canonical commits `9c634c1`, `354b2a6`, and `a2ebcef`
completed the global-gate humidity-danger stale-alert fix, docs/governance release
contract clarification, and time-gate pause regression test. Bella and Aetherwing
reviewed the runtime/UI behavior as safe; release promotion remains separate from
this local proposal evidence.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-31-v206-runtime-telemetry-and-co-clear-fixes.md](drafts/2026-05-31-v206-runtime-telemetry-and-co-clear-fixes.md)`.
HA Lab evidence artifact: `[.codex/lab/reports/2026-05-31T16-42-33Z-phase-3f-fault-fix-and-mutation-summary.md](../../lab/reports/2026-05-31T16-42-33Z-phase-3f-fault-fix-and-mutation-summary.md)`.

### Bella Draft - Canonical Proposal URN and Lifecycle Tracking System

Status: Draft / Bella-approved recommendations implemented locally by Aetherwing /
Jules-approved governance model as of 2026-05-30 / governance metadata normalisation
only / governance-only authority.

Owner label: Senyo. Bella supplied the approved review recommendations. Aetherwing
validated the local governance-record implementation. Jules approved the model with
Bella's recommendations on 2026-05-30.

Classification: proposal identifier and lifecycle metadata normalisation / Phase 1B
draft-index hardening / governance-only.

Runtime impact: None. This draft does not authorize runtime integration changes, Home
Assistant interaction, registry automation, generated UI changes, service/entity
contract changes, root proposal promotion, release documentation, release authority, or
implementation authority outside the local governance records.

Summary: Adds canonical `proposal_id`, immutable `proposal_urn`, title, created date,
category, target version, and `authority_status` metadata to the proposal template,
draft index, proposal-agent notes, and v2.1 Phase 1 artifact guidance. Existing
canonical state progression remains authoritative.

Boundary: No separate `PROPOSAL_REGISTRY.md` is created in this phase. `[drafts.md](drafts.md)`
remains the active Phase 1B normalisation and index surface. Adoption is prospective
first; optional backfill is limited to active v2.1 proposals when they are next
touched.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-29-canonical-proposal-urn-and-lifecycle-tracking.md](drafts/2026-05-29-canonical-proposal-urn-and-lifecycle-tracking.md)`.
Aetherwing handoff artifact: `[.codex/reports/handoffs/aetherwing_canonical_proposal_urn_tracking_implementation.md](../../reports/handoffs/aetherwing_canonical_proposal_urn_tracking_implementation.md)`.

### Bella Draft - Secret-Leak Prevention Hardening Layer

Status: Draft / Bella-approved proposal / Aetherwing reviewed as safe for constrained
implementation / full-history baseline clean / required Gitleaks workflow job committed
locally in canonical checkout commit `1285d28` / not pushed / no GitHub settings
changes / repository security hygiene only / no runtime authority.

Owner label: Bella. Aetherwing is requested to review the implementation packet for
release-safety, deterministic-runtime non-impact, CI disruption risk, redaction
requirements, and rollback clarity before any repository-hygiene patch is treated as
ready for Jules review.

Classification: repository secret-leak prevention / GitHub security setting
verification / Gitleaks scanner adoption / local maintainer scan path.

Runtime impact: None. This draft does not authorize Home Assistant runtime changes,
entity semantics, service contracts, diagnostics behavior, generated UI, dashboard
generation, lane ordering, control semantics, Home Assistant calls, release tagging, or
root proposal promotion.

Summary: Adds a layered secret-protection plan: verify GitHub native secret scanning
and push protection, add Gitleaks as the primary repository scanner, preserve the
existing custom secret-pattern scan as a secondary HI-specific guard, provide a local
maintainer scan command, use a narrow `.gitleaks.toml` that extends default rules only,
and require a full-history baseline before any required branch-check enforcement.

Boundary: No broad allowlists for `.codex/`, docs, reports, YAML, examples, fixtures,
or tests. Findings must be redacted. Real secrets require credential rotation before
any history-cleanup claim. GitHub settings remain manual verification unless Jules
separately approves direct settings mutation in the live repository.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-29-secret-leak-prevention-hardening.md](drafts/2026-05-29-secret-leak-prevention-hardening.md)`.
Aetherwing handoff artifact: `[.codex/reports/handoffs/aetherwing_secret_leak_prevention_hardening.md](../../reports/handoffs/aetherwing_secret_leak_prevention_hardening.md)`.
Aetherwing review artifact: `[.codex/reports/audits/2026-05-29-secret-leak-prevention-aetherwing-review.md](../../reports/audits/2026-05-29-secret-leak-prevention-aetherwing-review.md)`.

### Bella Draft - Codex Identity Registration Layer

Status: Draft / AetherCore guardrails applied / Jules approved staging / Aetherwing
local registry implementation applied and validated / local Codex governance only / no
runtime authority.

Owner label: Bella. Aetherwing is requested to validate only the constrained local TOML
identity registry packet and then return evidence for Jules review before any root
promotion, publication, or release movement.

Classification: local Codex identity registration / operational contract / routing
metadata / governance-only.

Runtime impact: None. This draft does not authorize Home Assistant runtime changes,
entity semantics, service contracts, diagnostics behavior, generated UI, dashboard
generation, lane ordering, control semantics, Home Assistant calls, release tagging,
or public documentation changes.

Summary: Defines and stages `.codex/agents/*.toml` as a compact machine-readable
identity registration layer for Bella, Aetherwing, Aetherbite, and AetherCore. The
registry indexes existing markdown authority and memory sources; it does not duplicate
canon, create executable agents, create schedulers, create recurring review, or grant
approval authority.

Boundary: TOML metadata may route and constrain Codex identity loading, but it cannot
override Senyo, `[DESIGN_BRIEF.md](../../../DESIGN_BRIEF.md)`, root `[PROPOSALS.md](../../../PROPOSALS.md)`,
`[.codex/governance/AGENT_BOUNDARIES.md](../AGENT_BOUNDARIES.md)`, AetherCore boundaries, or existing memory
sources. If TOML conflicts with controlling markdown, the TOML is stale.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-30-codex-identity-registration-layer.md](drafts/2026-05-30-codex-identity-registration-layer.md)`.
Aetherwing handoff artifact: `[.codex/reports/handoffs/aetherwing_codex_identity_registration_layer_implementation.md](../../reports/handoffs/aetherwing_codex_identity_registration_layer_implementation.md)`.
Aetherwing validation artifact: `[.codex/reports/audits/2026-05-30-codex-identity-registration-layer-aetherwing-validation.md](../../reports/audits/2026-05-30-codex-identity-registration-layer-aetherwing-validation.md)`.

### Bella Amendment - HA Lab Phase 3D Follow-Up Hardening & Risk Closure

Status: Draft / Jules approved recommended next action / Aetherwing runtime-safety
reviewed / approved as governance hardening gate / Aetherwing drift-packet reviewed /
exact read-only drift observation completed / drift classified unexplained-contained /
read-only pre-mutation readiness completed / Jules stop directive recorded /
no runtime mutation authorized by this amendment.

Owner label: Bella post-run governance amendment. Aetherwing remains the required
runtime-safety validator before any further HA Lab mutation or reusable execution
tooling is approved.

Classification: HA Lab post-run risk closure / credential-boundary hardening /
CO-clear gating / IAQ observational boundary / fake-output block preservation.

Runtime impact: None from this amendment. It does not authorize Home Assistant service
calls, helper mutation, control-switch mutation, dashboard mutation, YAML, fake
outputs, scenario-runner implementation, release promotion, stable Home Assistant
access, or public documentation changes.

Summary: Converts the Phase 3D partial-pass caveats into hard requirements before any
future HA Lab mutation. The amendment requires lab-only credential loading,
generic-environment rejection, exact mutation allow-lists, a mandatory CO-clear gate,
control-switch drift investigation, IAQ observational status, and continued fake-output
blocking.

Boundary: Phase 3D is accepted only as first-slice evidence for wrapper propagation,
true unavailable behavior, humidity alert/risk surfaces, CO dominance, reset-only
rollback, and restored lab baseline. It is not accepted as AQ lane validation,
mould/condensation lane validation, output-write validation, generated-dashboard truth,
release readiness, stable HA safety, or reusable runner approval.

Phase 3D.1 outcome: Jules approved the hardening plan as governance-only. Aetherwing
reviewed the hardening plan, read-only drift checklist, and evidence template and
approved them as a prerequisite gate, not as runtime execution or runner implementation
approval. The local plan defines fail-closed credential rules, exact future allow-list
requirements, CO-clear gate criteria, read-only `air_control_enabled` drift
investigation scope, evidence reporting requirements, IAQ observational boundaries, and
fake-output blocks.

Drift investigation outcome: Aetherwing reviewed the Bella drift packet and required
scope amendments. The amendments were implemented, Jules approval was recorded for the
exact read-only scope, and the read-only investigation was completed after reachability
returned. Local code review found no direct HI runtime write path that turns
`air_control_enabled` off during CO clear or return-to-normal. Exact live state capture
showed `air_control_enabled=on`, manual override `off`, CO emergency active `off`, mode
`normal`, diagnostics `ok`, and CO baseline. Latest classification:
`unexplained_contained`.

Read-only pre-mutation readiness outcome: Jules approved the Phase 3D-class
pre-mutation action list for execution and completion. Codex executed this only as the
read-only operation `phase_3d_class_pre_mutation_readiness`: lab-only credential source,
redacted target/token fingerprints, `GET /api/`, `GET /api/config`, and exact targeted
`GET /api/states/<entity_id>` reads. The pass captured 23/23 required states, confirmed
6/6 blocked/deferred entities absent, and recorded no service calls, no helper mutation,
no availability toggle mutation, no switch restoration, no scenario rerun, no dashboard
mutation, no fake outputs, no output validation, no stable Home Assistant access, and
no release validation.

Current stop directive: Jules requested "stop here" on 2026-05-27 after the proposal
status and implementation-trace review. The stop point is the completed read-only
pre-mutation readiness pass. No future HA Lab read, mutation, switch restoration,
output validation, HA-facing runner execution, or Phase 3D-class scenario rerun is
approved from this proposal. Reopening the lane requires a separate exact operation
packet with its own Aetherwing review and Jules approval.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-24-bella-ha-lab-phase-3d-follow-up-hardening-amendment.md](drafts/2026-05-24-bella-ha-lab-phase-3d-follow-up-hardening-amendment.md)`.
Aetherwing review artifact: `[.codex/reports/audits/2026-05-24-ha-lab-phase-3d-follow-up-hardening-aetherwing-runtime-safety-review.md](../../reports/audits/2026-05-24-ha-lab-phase-3d-follow-up-hardening-aetherwing-runtime-safety-review.md)`.
Phase 3D.1 plan artifact: `[.codex/lab/implementation/phase-3d1-hardening-plan.md](../../lab/implementation/phase-3d1-hardening-plan.md)`.
Phase 3D.1 drift checklist: `[.codex/lab/implementation/phase-3d1-air-control-enabled-drift-investigation-checklist.md](../../lab/implementation/phase-3d1-air-control-enabled-drift-investigation-checklist.md)`.
Phase 3D-class evidence template: `[.codex/lab/templates/phase_3d_class_evidence_report.md](../../lab/templates/phase_3d_class_evidence_report.md)`.
Aetherwing Phase 3D.1 plan review: `[.codex/reports/audits/2026-05-24-ha-lab-phase-3d1-hardening-plan-aetherwing-review.md](../../reports/audits/2026-05-24-ha-lab-phase-3d1-hardening-plan-aetherwing-review.md)`.
Bella drift investigation packet: `[.codex/reports/handoffs/bella_phase_3d1_air_control_enabled_drift_investigation_packet.md](../../reports/handoffs/bella_phase_3d1_air_control_enabled_drift_investigation_packet.md)`.
Aetherwing drift packet review: `[.codex/reports/audits/2026-05-24-ha-lab-phase-3d1-air-control-enabled-drift-packet-aetherwing-review.md](../../reports/audits/2026-05-24-ha-lab-phase-3d1-air-control-enabled-drift-packet-aetherwing-review.md)`.
Latest drift investigation report: `[.codex/lab/reports/2026-05-24T07-37-17Z-phase-3d1-air-control-enabled-drift-investigation.md](../../lab/reports/2026-05-24T07-37-17Z-phase-3d1-air-control-enabled-drift-investigation.md)`.
Latest reachability check: `[.codex/lab/reports/2026-05-24T07-58-41Z-ha-lab-reachability-check.md](../../lab/reports/2026-05-24T07-58-41Z-ha-lab-reachability-check.md)`.
Latest completed drift state-capture report: `[.codex/lab/reports/2026-05-24T08-03-56Z-phase-3d1-air-control-enabled-drift-investigation.md](../../lab/reports/2026-05-24T08-03-56Z-phase-3d1-air-control-enabled-drift-investigation.md)`.
Pre-mutation action list: `[.codex/lab/implementation/phase-3d-class-pre-mutation-action-list.md](../../lab/implementation/phase-3d-class-pre-mutation-action-list.md)`.
Aetherwing pre-mutation action-list review: `[.codex/reports/audits/2026-05-24-ha-lab-phase-3d-class-pre-mutation-action-list-aetherwing-review.md](../../reports/audits/2026-05-24-ha-lab-phase-3d-class-pre-mutation-action-list-aetherwing-review.md)`.
Phase 3D.2 runner creation packet: `[.codex/lab/implementation/phase-3d2-runner-creation-packet.md](../../lab/implementation/phase-3d2-runner-creation-packet.md)`.
Aetherwing Phase 3D.2 runner creation review: `[.codex/reports/audits/2026-05-24-ha-lab-phase-3d2-runner-creation-packet-aetherwing-review.md](../../reports/audits/2026-05-24-ha-lab-phase-3d2-runner-creation-packet-aetherwing-review.md)`.
Aetherwing Phase 3D.2 runner implementation review: `[.codex/reports/audits/2026-05-24-ha-lab-phase-3d2-runner-implementation-aetherwing-review.md](../../reports/audits/2026-05-24-ha-lab-phase-3d2-runner-implementation-aetherwing-review.md)`.
Post-run runtime-safety validation: `[.codex/reports/audits/2026-05-24-ha-lab-phase-3d2-post-run-runtime-safety-validation-aetherwing-review.md](../../reports/audits/2026-05-24-ha-lab-phase-3d2-post-run-runtime-safety-validation-aetherwing-review.md)`.
Latest Phase 3D.2 report-only runner execution report: `[.codex/lab/reports/2026-05-24T16-25-18Z-phase-3d2-runner-creation.md](../../lab/reports/2026-05-24T16-25-18Z-phase-3d2-runner-creation.md)`.
Phase 3D-class pre-mutation readiness tool: `[.codex/lab/tools/ha_lab_phase_3d_pre_mutation_readiness.py](../../lab/tools/ha_lab_phase_3d_pre_mutation_readiness.py)`.
Latest read-only pre-mutation readiness report: `[.codex/lab/reports/2026-05-24T16-54-13Z-phase-3d-class-pre-mutation-readiness.md](../../lab/reports/2026-05-24T16-54-13Z-phase-3d-class-pre-mutation-readiness.md)`.
Aetherwing read-only readiness completion review: `[.codex/reports/audits/2026-05-24-ha-lab-phase-3d-class-pre-mutation-readiness-completion-aetherwing-review.md](../../reports/audits/2026-05-24-ha-lab-phase-3d-class-pre-mutation-readiness-completion-aetherwing-review.md)`.

### AetherMite Draft - HI Lab Mock Telemetry & Boundary Exploration Layer

Status: Draft / Bella coherence reviewed / Aetherwing constrained first-slice reviewed /
Phase 3A local contract tooling implemented / Phase 3B manual checklist approved /
Phase 3C HA Lab first-slice observed / governance-only / lab-only.

Owner label: Aetherbite exploratory governance, using the AetherMite title supplied
for this task. Aetherwing is the required runtime-safety validator before any helper,
wrapper, unavailable-state, fake-output, YAML, API, or lab configuration work. Bella is
the required coherence reviewer before promotion.

Classification: HA Lab mock telemetry contract / helper-backed sensor exploration /
manual boundary validation / deterministic runtime evidence preparation.

Runtime impact: None from this draft alone. Later Jules-authorized lab execution
created and corrected HA Lab-only wrapper fixtures, configured HI against the four
approved wrappers, and produced first-slice runtime evidence. No fake fans, dashboard
generation changes, release metadata, deployment behavior, or stable Home Assistant
behavior are approved by this draft record.

Summary: Defines a lab-only helper-backed telemetry contract for deterministic HI
boundary exploration before real integrations are introduced. The draft favors
sanitized manual helpers and sensor wrappers for humidity, temperature,
HI-compatible IAQ, and CO as the first-slice minimum, while moving VOC and PM2.5 to
optional branch coverage and keeping HI backend truth authoritative. Fake outputs,
MQTT, scenario runners, API tooling, and real integrations remain delayed.

Boundary: The full entity catalogue is only a naming reservation. The approved first
slice used the reduced minimal telemetry subset: humidity, temperature,
HI-compatible IAQ, and CO. Numeric helpers alone were not sufficient for
unavailable-state validation; the governed wrapper/toggle mechanism supplied the
first-slice unavailable-state evidence. VOC and PM2.5 remain optional branch coverage
only. Fake fans and output-write validation remain blocked.

Aetherwing/Jules review outcome: constrained first-slice governance boundary approved
after three required corrections: AQI wording is corrected to current HI IAQ semantics,
VOC and PM2.5 are optional branch coverage, and fake outputs remain blocked.

Current decision: Jules accepted the unknown optional/generated entities as expected
first-slice residue for HA Lab observation only. This does not approve fake outputs,
VOC/PM2.5 branch creation, generated-dashboard mutation, public docs, root proposal
promotion, or release-gate use.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-23-hi-lab-mock-telemetry-boundary-layer.md](drafts/2026-05-23-hi-lab-mock-telemetry-boundary-layer.md)`.
Handoff artifact: `[.codex/reports/handoffs/aetherwing_hi_lab_mock_telemetry_boundary_layer.md](../../reports/handoffs/aetherwing_hi_lab_mock_telemetry_boundary_layer.md)`.

### AetherMite Draft - Home Assistant Lab Runtime Architecture

Status: Broad architecture reference / Bella coherence reviewed / split / partially
realized by governed HA Lab packets / governance-only / not full architecture approval.

Owner label: Aetherbite exploratory governance, using the AetherMite title supplied
for this task. Aetherwing is the required runtime and regression-safety validator
before any implementation slice. Bella is the required coherence reviewer before
promotion.

Classification: Long-term development ecosystem / Home Assistant lab runtime /
deployment validation / regression staging / scenario replay / release-candidate
runtime.

Runtime impact: None from this architecture record. Later governed HA Lab packets
created local-only scaffolding, read-only identity/presence tools, a baseline pointer,
mock telemetry contract tooling, report-only runner tooling, read-only readiness
checks, UI gap classification, and a lab-only SSH deploy link. Those packets do not
authorize runtime source changes, entity semantic changes, dashboard mutation authority,
release metadata changes, release-gate use, or stable deployment behavior.

Summary: Proposes a dedicated isolated Home Assistant laboratory runtime as the
canonical validation environment for future Humidity Intelligence development. The
lab would act as sandbox, staging runtime, regression lab, deployment validation
environment, integration proving ground, scenario replay host, runtime truth
verifier, and safe bridge between Codex engineering and stable Home Assistant
deployment. The lab provides validation evidence only; repository source,
`[DESIGN_BRIEF.md](../../../DESIGN_BRIEF.md)`, and root `[PROPOSALS.md](../../../PROPOSALS.md)` remain the source-of-truth hierarchy.

Boundary: The lab must remain isolated from stable Home Assistant, use separate
tokens and credentials, default to mock/helper/synthetic telemetry, forbid direct
control of production devices, and preserve deterministic HI principles. It must not
create hidden automations, hidden output paths, autonomous production mutation,
frontend-inferred runtime truth, or release promotion without explicit validation
evidence.

Current governed state: The original architecture direction has been split into
specific HA Lab packets. Completed or accepted slices include local scaffold,
Phase 2A identity preflight, Phase 2B HI presence inventory, Phase 2C baseline lock,
Phase 3A mock telemetry contract tooling, Phase 3B manual wrapper checklist, Phase 3C
first-slice observation, Phase 3D partial controlled lane-response evidence,
Phase 3D.2 report-only runner stop state, Phase 3D-class read-only pre-mutation
readiness, Phase 4A UI gap classification, Phase 4B frontend-resource readiness
classification, and Phase 4C lab-only SSH deploy linkage. All remain local HA Lab
evidence only.

Blocked expansion: Fake outputs, output-write validation, AQ lane validation,
mould/condensation runtime validation, dashboard mutation authority, release-gate
authority, stable-runtime deployment authority, production telemetry mirroring, and
autonomous runtime execution remain blocked unless a future exact packet receives
Aetherwing review and Jules approval.

Recommended next action: Stop treating this broad draft as an executable plan. Use it
only as the architecture reference and route future work through the current HA Lab
README, baseline pointer, Phase 3D-class pre-mutation action list, and exact phase
packets. Any future HA-facing read, mutation, scenario rerun, deploy, dashboard change,
or release-gate claim requires a separate scoped packet.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-23-ha-lab-runtime-architecture.md](drafts/2026-05-23-ha-lab-runtime-architecture.md)`.

### Bella Draft - Local Version Preservation & Rollback Safeguard

Status: Implemented as constrained stable v2.0.6 Phase 1 /
draft-governed / canonical checkout committed and validated / runtime-control-neutral.

Owner label: Bella for coherence and proposal governance. Aetherwing is the required
runtime-safety validator for the approved investigation pass.

Classification: Advanced maintenance capability / local HI-only snapshot support /
release-validation support / Phase 1 constrained implementation.

Runtime impact: Manual maintenance service contract and compact diagnostics/reporting
surfaces only. No deterministic runtime-control behavior changed.

Summary: Proposes optional advanced tooling for creating and listing local HI-only
snapshots of the currently installed `humidity_intelligence` custom integration folder
before explicit HI maintenance, beta validation, or experimental deployment work. The
draft rejects hidden HACS interception, implicit restore behavior, and
package-manager-like behavior.

Boundary: The implemented Phase 1 is service-first, explicit, executor-backed for disk
I/O, diagnostics-visible, retention-limited, and restart-aware. It is limited to
`humidity_intelligence.create_local_backup`, `humidity_intelligence.list_saved_versions`,
deterministic retention, metadata validation, compact diagnostics visibility,
self_check visibility, warn/info-only release_check visibility, executor-backed
filesystem handling, persistent notifications, scoped stale-partial cleanup,
restart-aware semantics, and a global HI maintenance lock. HI must not intercept HACS
update mechanics, promise automatic pre-update snapshots, behave like a package manager,
modify Home Assistant core update behavior, change deterministic lane ordering, alter
entity semantics, change generated dashboards, or affect runtime output control.

Implementation outcome: The constrained Phase 1 landed in the canonical GitHub checkout
as `0a2e354` (`v2.0.6-beta.1: add local HI snapshot services`) and was later preserved
through release-surface repair commit `c674f73` plus docs-truth sync `ea52a41`. Direct
restore, live folder replacement, automatic rollback, automatic HACS interception,
startup snapshot creation, backup-platform integration, arbitrary delete services,
runtime entity additions, config-entry migration snapshotting, restore activation
semantics, and package-manager-like behavior remain deferred.

Recommended next action: Treat the implemented create/list snapshot slice as tested
beta maintenance support only. Any future restore path, HACS/update interception,
startup snapshotting, runtime entity addition, generated-dashboard change, release
promotion, or root proposal promotion requires a separate scoped proposal, Aetherwing
runtime-safety review where applicable, and Jules approval.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-22-local-version-preservation-rollback-safeguard.md](drafts/2026-05-22-local-version-preservation-rollback-safeguard.md)`.

### Bella Draft - Community Ideas & Proposals

Status: Implemented in canonical GitHub checkout commit `e91ae37` / constrained
Aetherwing implementation recommendations actioned / governance-only /
runtime-neutral.

Owner label: Bella proposal governance draft. The proposal owner is senyo888.

Classification: Community ideas/proposals intake / GitHub issue-template planning /
proposal lifecycle governance / maintainer-led triage.

Runtime impact: None. This draft and the implemented first slice do not
authorize Home Assistant behavior changes, HI runtime behavior changes, lane ordering
changes, threshold changes, entity semantic changes, service changes,
telemetry-processing changes, generated-dashboard changes, frontend-card changes,
release promotion, or environmental control behavior changes.

Summary: Proposes a lightweight Community Ideas & Proposals intake path for collecting feature
ideas, dashboard suggestions, documentation improvements, integration compatibility
feedback, diagnostics/support-flow ideas, and automation/control suggestions through a
structured GitHub intake path. The program is an intake and governance feeder only:
community submissions, comments, and reactions may inform visibility and prioritisation
but must not become implementation authority, release authority, runtime authority, or
automatic approval.

Boundary: Future implementation planning may consider one dedicated public Community
Proposal issue template, a small label set, a short authority-boundary note, and manual
triage workflow guidance. It must not create autonomous decision making, automatic
proposal approval, automatic implementation promotion, mandatory voting, public issue
mutation by automation, runtime behavior changes, Home Assistant service changes,
entity-contract changes, dashboard-generation changes, or root proposal promotion
without separate approval.

Final outcome: constrained Aetherwing first slice implemented and committed as
`e91ae37` on `senyo888-patch-1`. The public issue form is named Community Ideas &
Proposals, uses friendly user-facing questions, and states that submission does not
guarantee implementation, release scheduling, or acceptance. Report-only triage routes
`community-proposal` issues to manual Bella/Jules review and preserves the rule that
popularity is visibility evidence only.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-28-community-proposal-program.md](drafts/2026-05-28-community-proposal-program.md)`.
Aetherwing handoff artifact: `[.codex/reports/handoffs/aetherwing_community_proposal_program_implementation.md](../../reports/handoffs/aetherwing_community_proposal_program_implementation.md)`.

### Bella Draft - GitHub Wiki Public Support Manual Pilot

Status: Implemented as a docs-only public support-manual pilot /
proposal-governed / review-backed / runtime-authority-neutral.

Owner label: Bella for proposal governance and support-surface coherence.

Classification: Public support manual pilot / README deflation /
repo-and-Wiki authority-boundary preservation.

Runtime impact: None. No deterministic runtime-control behavior, entity contract,
service contract, dashboard generation behavior, HACS metadata, or release version
state changed through this draft itself.

Summary: Defines the GitHub Wiki as a support-manual layer for Humidity Intelligence
so the README can remain the public front door while longer configuration, support,
diagnostics, generated-dashboard, HACS/update, AQ/CO safety, troubleshooting, and
release-validation guidance move into a calmer public manual. The draft keeps runtime
truth in tracked repository sources and blocks the Wiki from becoming backend, entity,
service, generated-dashboard, release, or HACS authority.

Boundary: [`README.md`](../../../README.md) remains the public front door, `docs/` remains the
version-controlled support/release layer, and [`DESIGN_BRIEF.md`](../../../DESIGN_BRIEF.md) remains the
implementation contract. Future expansion, deeper runtime/configuration explanatory
pages, and any further release-process changes remain blocked until maintainer
approval.

Recommended next action: Maintainer reviews the slimmed README, live Wiki routing, and
pushed repo docs branch, then decides whether any future manual expansion is
warranted.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-06-07-github-wiki-support-manual-pilot.md](drafts/2026-06-07-github-wiki-support-manual-pilot.md)`.

### Aetherbite Draft - Harmonic Air Control Evolution

Status: Brainstorm draft / Bella coherence reviewed / held for v2.1 design.

Owner label: Aetherbite. AetherMite was supplied in the originating proposal and is
treated as an alternate title/reference for Aetherbite only.

Classification: UX harmonisation, interaction evolution, humanisation layer.

Runtime impact: None at draft stage. Not approved for implementation.

Summary: Explores a future "Harmonic State Interface" for Current Air Control,
including unified automation-family phrasing, reduced reason-field repetition,
calmer idle-state language, composite visual states, and possible contextual chip
drill-down behavior.

Boundary: This draft must not weaken deterministic lane ownership, alert hierarchy,
CO emergency dominance, humidifier independence, raw operational truth, or generated
dashboard alignment. Any implementation must keep v2.0.5 release scope separate from
v2.1 Environmental Stability Intelligence planning.

Bella follow-up: Completed May 17, 2026. Verdict: coherent as v2.1 exploratory
direction, rejected for v2.0.5 implementation, not ready for root `[PROPOSALS.md](../../../PROPOSALS.md)`
promotion.

Recommended next action: keep staged until the maintainer chooses a specific v2.1
experiment slice. Safest first slice is wording-only/generated-card-only copy for
idle, humidify, and multi-AQ display language with no runtime or entity semantics
change.

Long-form artifact: `[.codex/governance/proposals/drafts/2026-05-17-harmonic-air-control-evolution.md](drafts/2026-05-17-harmonic-air-control-evolution.md)`.

## Recently Closed Drafts

### Aetherwing Draft - V2.0.6 Drift Statistics Helper Ownership

Status: Implemented as a stable v2.0.6 drift dependency reporting, Repairs,
documentation, and validation-readiness slice. Moved to implemented governance
records after the 2026-05-27 drift ownership audit.

Implemented artifact: `[.codex/governance/proposals/implemented/2026-05-23-v206-drift-statistics-helper-ownership.md](implemented/2026-05-23-v206-drift-statistics-helper-ownership.md)`.
Original draft artifact: `[.codex/governance/proposals/drafts/2026-05-23-v206-drift-statistics-helper-ownership.md](drafts/2026-05-23-v206-drift-statistics-helper-ownership.md)`.

### Bella Draft - HA Lab Phase 3D Controlled Lane-Response Validation

Status: Archived on 2026-05-24 after being superseded by the Phase 3D follow-up
hardening amendment and the current HA Lab baseline pointer.

Archived artifact: `[.codex/governance/proposals/archived/2026-05-23-bella-ha-lab-phase-3d-controlled-lane-response-validation.md](archived/2026-05-23-bella-ha-lab-phase-3d-controlled-lane-response-validation.md)`.

### Aetherwing Handoff - Issue #21 House Humidity Drift 7d Runtime Coherence

Status: Implemented in v2.0.5 and moved to implemented governance records.

Implemented artifact: `[.codex/governance/proposals/implemented/2026-05-19-house-humidity-drift-7d-runtime-coherence.md](implemented/2026-05-19-house-humidity-drift-7d-runtime-coherence.md)`.

### Aetherwing Maintenance Follow-up - Local HA Helper Script Sanity

Status: Implemented as local-helper maintenance after v2.0.5 validation.

Implemented artifact: `[.codex/governance/proposals/implemented/2026-05-19-local-ha-helper-maintenance.md](implemented/2026-05-19-local-ha-helper-maintenance.md)`.

### Aetherwing Draft - Codex Versioning Boundary Cleanup

Status: Superseded and archived after the May 16, 2026 local workspace architecture
handoff resolved the broad source-boundary decision.

Archived artifact: `[.codex/governance/proposals/archived/2026-05-15-codex-versioning-boundary-cleanup.md](archived/2026-05-15-codex-versioning-boundary-cleanup.md)`.
