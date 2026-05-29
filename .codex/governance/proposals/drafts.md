# Draft Proposals

New proposal material starts here unless Bella explicitly recommends immediate promotion to root `PROPOSALS.md`.

## Phase 1A Pruning Index

This file is the active draft index. Long-form drafts and reports are supporting
evidence only; they do not outrank this index, root `PROPOSALS.md`, `DESIGN_BRIEF.md`,
or approved runtime-protection contracts.

Expired drafts are stale by default. A stale draft must be reviewed, reclassified, or
archived before it can influence implementation, runtime validation, release wording,
generated UI, service/entity contracts, or HA Lab work.

| Draft | Pruning classification | State | Review / expiry date | Authority boundary |
| --- | --- | --- | --- | --- |
| Bella Draft - HA Lab Branch/Worktree Package Deploy Gate | keep | TESTED | 2026-06-28 | Stage A deploy-only copy completed and manual restart by Senyo plus read-only validation passed with log caveat; no release-candidate authority or stable access. |
| Bella Draft - Canonical Proposal URN and Lifecycle Tracking System | keep | REVIEW | 2026-06-28 | Governance metadata normalisation only; no runtime, registry, automation, root promotion, or release authority. |
| Bella Draft - HI Agent Memory Usage Auditor and Candidate Update Report | keep | TESTED | 2026-06-28 | Aetherwing local implementation, Bella review, approved memory mutation, and report-only automation activation completed; no root promotion or release authority. |
| Bella Amendment - HA Lab Phase 3D Follow-Up Hardening & Risk Closure | keep | TESTED | 2026-06-07 | Stopped after completed read-only readiness; current governance hardening gate only; no mutation authority. |
| AetherMite Draft - HI Lab Mock Telemetry & Boundary Exploration Layer | keep | TESTED | 2026-06-14 | Lab-only first-slice boundary and accepted-residue record; Phase 3A/3B/3C achieved; not release authority. |
| Aetherbite Draft - Harmonic Air Control Evolution | keep | IDEA | 2026-07-01 | Parked v2.1 exploratory UI wording direction; not a v2.0.x or runtime proposal. |
| AetherMite Draft - Home Assistant Lab Runtime Architecture | split | REVIEW | 2026-06-21 | Broad architecture reference, partially realized by governed HA Lab packets; not full architecture approval or release authority. |

## Canonical Metadata Fields

Active proposals must include the metadata block from
`.codex/governance/proposals/proposal_template.md` in their long-form artifact and in
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
| Bella Draft - HA Lab Branch/Worktree Package Deploy Gate | legacy-unassigned | legacy-unassigned | Bella Draft - HA Lab Branch/Worktree Package Deploy Gate | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | TESTED | Bella | high | ha-lab-filesystem-stage-a-plus-manual-stage-b-validation | proposal-governance; ha-lab-evidence; validation-tooling; lab-deploy-link; runtime-protection-contracts | true | 2026-06-28 | true | true | stage_b_post_restart_read_only | false | false | false | false | false |
| Bella Draft - Canonical Proposal URN and Lifecycle Tracking System | HI-PROP-20260529-001 | urn:hi:proposal:20260529:001:urn-lifecycle-tracking | Canonical Proposal URN and Lifecycle Tracking System | 2026-05-29 | governance | v2.1 | review-only | REVIEW | Senyo | low | governance-only | proposal-governance | false | 2026-06-28 | true | true | false | false | false | false | false | false |
| Bella Draft - HI Agent Memory Usage Auditor and Candidate Update Report | HI-PROP-20260529-002 | urn:hi:proposal:20260529:002:agent-memory-usage-auditor | HI Agent Memory Usage Auditor and Candidate Update Report | 2026-05-29 | governance | none | implemented | TESTED | Bella | medium | governance-only | proposal-governance; validation-tooling | true | 2026-06-28 | true | true | false | false | false | false | false | false |
| Bella Amendment - HA Lab Phase 3D Follow-Up Hardening & Risk Closure | legacy-unassigned | legacy-unassigned | Bella Amendment - HA Lab Phase 3D Follow-Up Hardening & Risk Closure | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | TESTED | Bella | high | governance-only | proposal-governance; ha-lab-evidence; diagnostics | true | 2026-06-07 | true | true | true | false | false | false | false | false |
| AetherMite Draft - HI Lab Mock Telemetry & Boundary Exploration Layer | legacy-unassigned | legacy-unassigned | AetherMite Draft - HI Lab Mock Telemetry & Boundary Exploration Layer | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | TESTED | Aetherbite | medium | governance-only | proposal-governance; ha-lab-evidence; diagnostics; generated-ui | false | 2026-06-14 | true | true | true | false | false | false | false | false |
| Aetherbite Draft - Harmonic Air Control Evolution | legacy-unassigned | legacy-unassigned | Aetherbite Draft - Harmonic Air Control Evolution | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | IDEA | Aetherbite | medium | governance-only | proposal-governance; generated-ui | false | 2026-07-01 | true | false | false | false | false | false | false | false |
| AetherMite Draft - Home Assistant Lab Runtime Architecture | legacy-unassigned | legacy-unassigned | AetherMite Draft - Home Assistant Lab Runtime Architecture | legacy-unassigned | legacy-unassigned | legacy-unassigned | legacy-unassigned | REVIEW | Aetherbite | high | governance-only | proposal-governance; ha-lab-evidence; runtime-protection-contracts; validation-tooling; generated-ui; lab-deploy-link | false | 2026-06-21 | true | false | false | false | false | false | false | false |

## Draft Detail Records

The Phase 1A table above is the active index. Detail records below preserve context,
but entries marked `supersede`, `archive`, or `reject` are historical unless promoted
again through review.

### Bella Draft - HI Agent Memory Usage Auditor and Candidate Update Report

Status: Draft / Aetherwing local implementation completed / Bella post-implementation
review passed / approved memory mutation and report-only automation activation applied
locally on 2026-05-29.

Owner label: Bella. Aetherwing implemented the bounded local reporting slice and the
autonomous maintainer completion-slice gate, addressed the in-scope caveat that
autonomous maintenance must be fail-closed, and returned the result for Bella
post-implementation review. Bella passed the local implementation slice. Jules then
approved memory mutation, automation activation, staging, commit, push, and final
checkout commitment. The approved memory update was applied through an exact manifest
and the report-only automation was activated. Root promotion, release authority, and
ungated memory mutation remain blocked.

Classification: local governance/reporting utility for agent memory usage review and
candidate memory-update triage, with an in-proposal autonomous maintainer completion
slice.

Runtime impact: None. This draft does not authorize runtime integration changes, Home
Assistant service calls, entity or service contract changes, generated UI changes,
diagnostics semantics changes, release metadata changes, root `PROPOSALS.md` promotion,
or ungated writes to `.codex/memories/`.

Summary: Defines a local, report-only auditor that checks whether recent HI agent work
consulted the expected memory and governance surfaces, identifies repeated successful
scripts/utilities/patterns that may deserve durable memory, and emits candidate memory
updates for human/Bella review. Candidate memory lines remain advisory until explicitly
approved. The auditor must treat current repository files and `DESIGN_BRIEF.md` as
higher authority than memory. The autonomous maintainer remains part of this proposal
until completion as a gated slice, not as a separate or hidden automation lane.

Boundary: Aetherwing may implement a small local script or equivalent local report
generator plus its generated audit report and autonomous maintainer completion-slice
file. The initial tool must be read-only against `.codex/memories/`, Home Assistant,
GitHub, and recurring automation configuration unless an exact approved candidate
manifest later authorizes an apply step. It may inspect local governance records, local
reports, proposal drafts, and approved automation run notes as evidence. It must not
scan unrestricted private session logs by default, must not infer memory usage from
stylistic similarity alone, and must redact or reject private paths, secrets, private
entity IDs, tokens, local credentials, telemetry, and machine-specific values from
candidate memory text.

Aetherwing loop outcome: Aetherwing implemented the approved bounded slice, recorded
the in-scope caveat and handling, validated the result, and returned the implemented
packet to Bella for review. Bella found no blocking findings. Jules approved the final
local commitment slice, including the exact memory manifest and report-only automation.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-29-hi-agent-memory-usage-auditor.md`.
Autonomous maintainer slice artifact: `.codex/governance/proposals/drafts/2026-05-29-hi-autonomous-memory-maintainer-slice.md`.
Aetherwing implementation report: `.codex/reports/handoffs/aetherwing_hi_memory_usage_auditor_implementation.md`.
Bella post-implementation review: `.codex/reports/audits/2026-05-29-hi-memory-usage-auditor-bella-review.md`.
Approved memory manifest: `.codex/reports/audits/hi_memory_usage_approved_manifest_2026-05-29.json`.
Approved apply report: `.codex/reports/audits/hi_memory_usage_apply_2026-05-29.json`.
Automation id: `hi-memory-usage-auditor`.

### Bella Draft - Canonical Proposal URN and Lifecycle Tracking System

Status: Draft / Bella-approved recommendations implemented locally by Aetherwing /
governance metadata normalisation only / review-only authority.

Owner label: Senyo. Bella supplied the approved review recommendations. Aetherwing
validated the local governance-record implementation.

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

Boundary: No separate `PROPOSAL_REGISTRY.md` is created in this phase. `drafts.md`
remains the active Phase 1B normalisation and index surface. Adoption is prospective
first; optional backfill is limited to active v2.1 proposals when they are next
touched.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-29-canonical-proposal-urn-and-lifecycle-tracking.md`.
Aetherwing handoff artifact: `.codex/reports/handoffs/aetherwing_canonical_proposal_urn_tracking_implementation.md`.

### Bella Draft - HA Lab Branch/Worktree Package Deploy Gate

Status: Draft / Bella coherence reviewed / Senyo approved Aetherwing implementation and
Stage A deploy on 2026-05-28 / Stage A deploy-only completed / Senyo manually
restarted HA Lab and approved read-only Stage B validation / no Codex restart or reload
authority / no release-candidate authority.

Owner label: Bella deployment-governance draft. Aetherwing is the required implementer
for the local Stage A deploy-gate tooling packet and the required reviewer before any
HA Lab package copy, restart/reload stage, or release-validation use.

Classification: HA Lab deploy gate / local branch-worktree source selection /
full-package SSH transport / two-stage activation boundary.

Runtime impact: Stage A changed files on the HA Lab filesystem only. The full
integration package was copied into the HA Lab after an exact Senyo-approved operation
packet, a local test/preflight gate, and a timestamped backup. Runtime activation
remains a separate Senyo-approved Stage B. Stable Home Assistant is out of scope.

Implementation outcome: `.codex/lab/tools/ha_lab_stage_a_package_deploy.py` and
`.codex/lab/tests/test_ha_lab_stage_a_package_deploy.py` were added as ignored local
lab tooling. One Stage A deploy-only full-package filesystem copy completed and is
recorded in `.codex/lab/reports/2026-05-28T12-33-04Z-stage-a-package-deploy.md`.
Senyo then restarted HA Lab manually and approved read-only Stage B validation, recorded
in `.codex/lab/reports/2026-05-28T12-47-31Z-stage-b-post-restart-validation.md`. The
source worktree was dirty, so both reports are lab-only evidence and not
release-candidate validation.

Summary: Keep branch selection and initial testing on the development machine. Do not
create a permanent `lab/test-ready` branch and do not put Git credentials or branch
pull authority inside Home Assistant. Use the existing HA Lab SSH link only as final
transport after the selected local branch/worktree records branch, commit, dirty
status, tests run, package source, exact destination, backup path, hashes, and rollback
evidence.

Boundary: Future deploy tooling must resolve the current lab target from
`.codex/private/ha_lab_ssh_config` and `.codex/private/ha_lab_runtime.env`. Historical
LAN addresses are evidence only and must not become deploy authority. Default deploy
unit is the full integration package to `/config/custom_components/humidity_intelligence/`
after a timestamped backup and clean replacement; changed-file deploys are blocked by
default and not authorized by this proposal. Failed pre-deploy checks hard-stop unless
Senyo explicitly records a lab-only override, but override is not available for target
mismatch, stable/prod/home target strings, generic production-looking env variables,
missing rollback, missing operation approval, changed-file deploy, partial-package
deploy, package overlay, missing backup, or missing hash-manifest comparison. Dirty
worktrees are allowed only for exploratory lab testing and must be marked
`release_candidate_validation: false`; release-candidate validation requires a clean
committed branch/worktree.

Aetherwing handoff: Prepare Stage A local tooling only. Required deliverables are an
implementation packet path, exact script or command name, package staging method,
private target-resolution checks, allowed SSH command list, remote backup format,
source/remote hash-manifest format, deployment report format, test coverage, stop
condition matrix, rollback dry-run or rehearsal evidence, and explicit confirmation
that Stage A deploy-only and Stage B runtime activation remain separate. Non-goals:
deploy execution without separate Senyo approval, Stage B activation, restart/reload,
Home Assistant service calls, helper/switch/output/scenario/dashboard mutation,
changed-file deploys, stable targets, Git authority inside Home Assistant, HACS
automation, release-candidate validation, and release promotion.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-28-ha-lab-branch-worktree-package-deploy-gate.md`.

### Aetherwing Handoff - V2.0.6 Seasonal Temperature Chip Colour Semantics

Status: Bella coherence reviewed / Aetherwing implementation handoff approved by
Senyo / implemented locally as v2.0.6-beta.1 / root `PROPOSALS.md` implemented
summary updated / stable release authority not granted.

Owner label: Bella proposal handoff. Aetherwing is the required runtime, diagnostics,
entity-semantics, generated-UI, and regression-safety validator before any
implementation slice.

Classification: V2.0.6 beta candidate / backend-truth-first generated-card colour
semantics / temperature comfort entity semantics review.

Runtime impact: Public entity names remain stable, but temperature comfort
classification semantics and diagnostics attributes changed for seasonal auto mode.
No service, lane-order, alert, humidifier, output-write, or migration change is
approved.

Summary: Refines the optional Current Air Control temperature chip row so colours use
explicit seasonal cold / comfort / warm / hot thresholds instead of the current generic
comfort-low / comfort-high / comfort-high + 1.0 rule. The proposal requires backend
truth first: add an explicit resolved warm/hot boundary, expose it through sensors and
diagnostics, then have generated mobile/tablet cards consume that truth.

Boundary: Do not implement as a YAML-only seasonal table. Do not add custom warm
threshold setup/options UI in this slice. Custom mode should keep the existing
`custom_high + 1.0` warm boundary until a separate custom warm-threshold proposal is
approved. Unknown, unavailable, incomplete, or non-numeric temperatures remain neutral.
Fahrenheit display may remain supported, but classification truth must stay
Celsius-normalized.

Implementation result: Added backend-owned `warm_high`, preserved custom mode as
custom high + 1.0°C, exposed the resolved boundary in sensors, diagnostics, and
diagnostics summaries, updated mobile/tablet card colour logic to consume backend
truth, and updated docs/tests in the same slice.

Validation result: `python3 -m py_compile helpers/seasonal.py sensors/core.py
diagnostics.py sensor.py`, `python3 "tests 2/test_runtime_card_sanity.py"`,
`python3 "tests 2/test_diagnostics.py"`, `python3 "tests 2/test_slope_sanity.py"`,
`python3 scripts/check_version_governance.py`, Ruby YAML parse sanity for both
generated card files, and `git diff --check` passed on 2026-05-28.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-28-v206-seasonal-temperature-chip-colour-semantics.md`.

### Bella Amendment - HA Lab Phase 3D Follow-Up Hardening & Risk Closure

Status: Draft / Senyo approved recommended next action / Aetherwing runtime-safety
reviewed / approved as governance hardening gate / Aetherwing drift-packet reviewed /
exact read-only drift observation completed / drift classified unexplained-contained /
read-only pre-mutation readiness completed / Senyo stop directive recorded /
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

Phase 3D.1 outcome: Senyo approved the hardening plan as governance-only. Aetherwing
reviewed the hardening plan, read-only drift checklist, and evidence template and
approved them as a prerequisite gate, not as runtime execution or runner implementation
approval. The local plan defines fail-closed credential rules, exact future allow-list
requirements, CO-clear gate criteria, read-only `air_control_enabled` drift
investigation scope, evidence reporting requirements, IAQ observational boundaries, and
fake-output blocks.

Drift investigation outcome: Aetherwing reviewed the Bella drift packet and required
scope amendments. The amendments were implemented, Senyo approval was recorded for the
exact read-only scope, and the read-only investigation was completed after reachability
returned. Local code review found no direct HI runtime write path that turns
`air_control_enabled` off during CO clear or return-to-normal. Exact live state capture
showed `air_control_enabled=on`, manual override `off`, CO emergency active `off`, mode
`normal`, diagnostics `ok`, and CO baseline. Latest classification:
`unexplained_contained`.

Read-only pre-mutation readiness outcome: Senyo approved the Phase 3D-class
pre-mutation action list for execution and completion. Codex executed this only as the
read-only operation `phase_3d_class_pre_mutation_readiness`: lab-only credential source,
redacted target/token fingerprints, `GET /api/`, `GET /api/config`, and exact targeted
`GET /api/states/<entity_id>` reads. The pass captured 23/23 required states, confirmed
6/6 blocked/deferred entities absent, and recorded no service calls, no helper mutation,
no availability toggle mutation, no switch restoration, no scenario rerun, no dashboard
mutation, no fake outputs, no output validation, no stable Home Assistant access, and
no release validation.

Current stop directive: Senyo requested "stop here" on 2026-05-27 after the proposal
status and implementation-trace review. The stop point is the completed read-only
pre-mutation readiness pass. No future HA Lab read, mutation, switch restoration,
output validation, HA-facing runner execution, or Phase 3D-class scenario rerun is
approved from this proposal. Reopening the lane requires a separate exact operation
packet with its own Aetherwing review and Senyo approval.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-24-bella-ha-lab-phase-3d-follow-up-hardening-amendment.md`.
Aetherwing review artifact: `.codex/reports/audits/2026-05-24-ha-lab-phase-3d-follow-up-hardening-aetherwing-runtime-safety-review.md`.
Phase 3D.1 plan artifact: `.codex/lab/implementation/phase-3d1-hardening-plan.md`.
Phase 3D.1 drift checklist: `.codex/lab/implementation/phase-3d1-air-control-enabled-drift-investigation-checklist.md`.
Phase 3D-class evidence template: `.codex/lab/templates/phase_3d_class_evidence_report.md`.
Aetherwing Phase 3D.1 plan review: `.codex/reports/audits/2026-05-24-ha-lab-phase-3d1-hardening-plan-aetherwing-review.md`.
Bella drift investigation packet: `.codex/reports/handoffs/bella_phase_3d1_air_control_enabled_drift_investigation_packet.md`.
Aetherwing drift packet review: `.codex/reports/audits/2026-05-24-ha-lab-phase-3d1-air-control-enabled-drift-packet-aetherwing-review.md`.
Latest drift investigation report: `.codex/lab/reports/2026-05-24T07-37-17Z-phase-3d1-air-control-enabled-drift-investigation.md`.
Latest reachability check: `.codex/lab/reports/2026-05-24T07-58-41Z-ha-lab-reachability-check.md`.
Latest completed drift state-capture report: `.codex/lab/reports/2026-05-24T08-03-56Z-phase-3d1-air-control-enabled-drift-investigation.md`.
Pre-mutation action list: `.codex/lab/implementation/phase-3d-class-pre-mutation-action-list.md`.
Aetherwing pre-mutation action-list review: `.codex/reports/audits/2026-05-24-ha-lab-phase-3d-class-pre-mutation-action-list-aetherwing-review.md`.
Phase 3D.2 runner creation packet: `.codex/lab/implementation/phase-3d2-runner-creation-packet.md`.
Aetherwing Phase 3D.2 runner creation review: `.codex/reports/audits/2026-05-24-ha-lab-phase-3d2-runner-creation-packet-aetherwing-review.md`.
Aetherwing Phase 3D.2 runner implementation review: `.codex/reports/audits/2026-05-24-ha-lab-phase-3d2-runner-implementation-aetherwing-review.md`.
Post-run runtime-safety validation: `.codex/reports/audits/2026-05-24-ha-lab-phase-3d2-post-run-runtime-safety-validation-aetherwing-review.md`.
Latest Phase 3D.2 report-only runner execution report: `.codex/lab/reports/2026-05-24T16-25-18Z-phase-3d2-runner-creation.md`.
Phase 3D-class pre-mutation readiness tool: `.codex/lab/tools/ha_lab_phase_3d_pre_mutation_readiness.py`.
Latest read-only pre-mutation readiness report: `.codex/lab/reports/2026-05-24T16-54-13Z-phase-3d-class-pre-mutation-readiness.md`.
Aetherwing read-only readiness completion review: `.codex/reports/audits/2026-05-24-ha-lab-phase-3d-class-pre-mutation-readiness-completion-aetherwing-review.md`.

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

Runtime impact: None from this draft alone. Later Senyo-authorized lab execution
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

Aetherwing/Senyo review outcome: constrained first-slice governance boundary approved
after three required corrections: AQI wording is corrected to current HI IAQ semantics,
VOC and PM2.5 are optional branch coverage, and fake outputs remain blocked.

Current decision: Senyo accepted the unknown optional/generated entities as expected
first-slice residue for HA Lab observation only. This does not approve fake outputs,
VOC/PM2.5 branch creation, generated-dashboard mutation, public docs, root proposal
promotion, or release-gate use.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-23-hi-lab-mock-telemetry-boundary-layer.md`.
Handoff artifact: `.codex/reports/handoffs/aetherwing_hi_lab_mock_telemetry_boundary_layer.md`.

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
`DESIGN_BRIEF.md`, and root `PROPOSALS.md` remain the source-of-truth hierarchy.

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
Aetherwing review and Senyo approval.

Recommended next action: Stop treating this broad draft as an executable plan. Use it
only as the architecture reference and route future work through the current HA Lab
README, baseline pointer, Phase 3D-class pre-mutation action list, and exact phase
packets. Any future HA-facing read, mutation, scenario rerun, deploy, dashboard change,
or release-gate claim requires a separate scoped packet.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-23-ha-lab-runtime-architecture.md`.

### Bella Draft - Local Version Preservation & Rollback Safeguard

Status: Approved for constrained v2.0.6 implementation investigation /
implemented as constrained v2.0.6-beta.1 local snapshot services / stable release
authority not granted.

Owner label: Bella for coherence and proposal governance. Aetherwing is the required
runtime-safety validator for the approved investigation pass.

Classification: Advanced maintenance capability / local HI-only snapshot support /
release-validation support / Phase 1 feasibility investigation.

Runtime impact: Service-contract and diagnostics/reporting surfaces changed in the
implemented beta slice. Deterministic control, lane ordering, outputs, entity semantics,
generated dashboards, restore behavior, and HACS update behavior remain unchanged.

Summary: Proposes optional advanced tooling for creating and listing local HI-only
snapshots of the currently installed `humidity_intelligence` custom integration folder
before explicit HI maintenance, beta validation, or experimental deployment work. The
draft rejects hidden HACS interception, implicit restore behavior, and
package-manager-like behavior.

Boundary: Any future implementation must be service-first, explicit, executor-backed for
disk I/O, diagnostics-visible, retention-limited, and restart-aware. Phase 1
investigation is strictly limited to `humidity_intelligence.create_local_backup`,
`humidity_intelligence.list_saved_versions`, deterministic retention, metadata
validation, compact diagnostics visibility, self_check visibility, warn/info-only
release_check visibility, executor-backed filesystem handling, persistent
notifications, scoped stale-partial cleanup, restart-aware semantics, and a global HI
maintenance lock. HI must not intercept HACS update mechanics, promise automatic
pre-update snapshots, behave like a package manager, modify Home Assistant core update
behavior, change deterministic lane ordering, alter entity semantics, change generated
dashboards, or affect runtime output control.

Implementation result: The constrained Phase 1 slice landed in v2.0.6-beta.1 as
`helpers/local_versions.py`, thin `services.py` handlers, `services.yaml`
documentation, compact diagnostics/self-check/release-check visibility, and direct
sanity coverage. This is local HI-only snapshot support, not Home Assistant backup,
restore, rollback, HACS interception, or package-manager behavior.

Bella verdict: Implemented beta maintenance slice after the earlier constrained
investigation approval. Stable release authority is still not granted. Direct restore,
live folder replacement, automatic rollback, automatic HACS interception, startup
snapshot creation, backup-platform integration, arbitrary delete services, runtime entity
additions, config-entry migration snapshotting, restore activation semantics, and
package-manager-like behavior remain deferred.

Recommended next action: validate the implemented beta slice through local direct tests
and HA Lab service smoke. Keep release-candidate validation false until a clean committed
branch/worktree, Home Assistant validation, Bella/AetherCore release gates, and maintainer
README approval exist.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-22-local-version-preservation-rollback-safeguard.md`.

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
direction, rejected for v2.0.5 implementation, not ready for root `PROPOSALS.md`
promotion.

Recommended next action: keep staged until the maintainer chooses a specific v2.1
experiment slice. Safest first slice is wording-only/generated-card-only copy for
idle, humidify, and multi-AQ display language with no runtime or entity semantics
change.

Long-form artifact: `.codex/governance/proposals/drafts/2026-05-17-harmonic-air-control-evolution.md`.

## Recently Closed Drafts

### Bella Draft - Local Version Preservation & Rollback Safeguard

Status: Implemented in v2.0.6-beta.1 as explicit local HI-only snapshot service support
after the constrained investigation approval. Stable release authority is not granted.

Implemented artifact: `.codex/governance/proposals/implemented/2026-05-22-local-version-preservation-rollback-safeguard.md`.
Original draft artifact: `.codex/governance/proposals/drafts/2026-05-22-local-version-preservation-rollback-safeguard.md`.

### Aetherwing Handoff - V2.0.6 Seasonal Temperature Chip Colour Semantics

Status: Implemented in v2.0.6-beta.1 as backend-owned seasonal temperature chip
colour semantics after Senyo approved the Aetherwing handoff on 2026-05-28.

Implemented artifact: `.codex/governance/proposals/implemented/2026-05-28-v206-seasonal-temperature-chip-colour-semantics.md`.
Original draft artifact: `.codex/governance/proposals/drafts/2026-05-28-v206-seasonal-temperature-chip-colour-semantics.md`.

### Aetherwing Draft - V2.0.6 Drift Statistics Helper Ownership

Status: Implemented as a v2.0.6-beta.1 drift dependency reporting, Repairs,
documentation, and validation-readiness slice. Moved to implemented governance
records after the 2026-05-27 drift ownership audit.

Implemented artifact: `.codex/governance/proposals/implemented/2026-05-23-v206-drift-statistics-helper-ownership.md`.
Original draft artifact: `.codex/governance/proposals/drafts/2026-05-23-v206-drift-statistics-helper-ownership.md`.

### Bella Draft - HA Lab Phase 3D Controlled Lane-Response Validation

Status: Archived on 2026-05-24 after being superseded by the Phase 3D follow-up
hardening amendment and the current HA Lab baseline pointer.

Archived artifact: `.codex/governance/proposals/archived/2026-05-23-bella-ha-lab-phase-3d-controlled-lane-response-validation.md`.

### Aetherwing Handoff - Issue #21 House Humidity Drift 7d Runtime Coherence

Status: Implemented in v2.0.5 and moved to implemented governance records.

Implemented artifact: `.codex/governance/proposals/implemented/2026-05-19-house-humidity-drift-7d-runtime-coherence.md`.

### Aetherwing Maintenance Follow-up - Local HA Helper Script Sanity

Status: Implemented as local-helper maintenance after v2.0.5 validation.

Implemented artifact: `.codex/governance/proposals/implemented/2026-05-19-local-ha-helper-maintenance.md`.

### Aetherwing Draft - Codex Versioning Boundary Cleanup

Status: Superseded and archived after the May 16, 2026 local workspace architecture
handoff resolved the broad source-boundary decision.

Archived artifact: `.codex/governance/proposals/archived/2026-05-15-codex-versioning-boundary-cleanup.md`.
