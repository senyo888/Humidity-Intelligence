# Humidity Intelligence HA Lab Runtime

Status: local-only HA Lab governance and evidence scaffold with bounded completed
phase packets.

This folder documents the governed HA Lab slices for Humidity Intelligence. It contains
report templates, checklist material, lab-only link notes, phase packets, read-only
tools, tests, evidence reports, and stable/lab boundary rules. It is not a runtime
subsystem, not production deployment tooling, and not a release gate.

## Approved Lab Target

- HA lab instance name: private HA Lab instance
- HA lab base URL: resolved from `.codex/private/ha_lab_runtime.env`
- HA lab SSH target: resolved from `.codex/private/ha_lab_ssh_config`
- HA lab user: resolved from `.codex/private/ha_lab_ssh_config`
- Target boundary: private HA Lab instance only
- Lab instance label for future tooling: `humidity-intelligence-lab`

Historical LAN addresses in reports or older phase notes are evidence only. Current
deploy authority comes from the private runtime env plus private SSH config, and future
deploy tooling must hard-stop if those sources disagree.

The lab is evidence infrastructure only. Repository source, release worktrees,
approved governance documents, and `DESIGN_BRIEF.md` remain the source of runtime
truth. HA Lab is now admitted as Operational Beta Validation Infrastructure for
advisory beta deploy, runtime-readiness, diagnostics, and card/entity-map sanity
evidence; it is not release authority, runtime authority, stable Home Assistant
authority, or permission for autonomous mutation.

Current operational beta runbook:

```text
.codex/lab/implementation/operational-beta-validation-packet.md
```

## Initial Scaffold Scope

Allowed by the initial scaffold:

- local-only governance notes
- deployment report template
- validation report template
- scenario manifest template
- read-only checklist
- lab/stable boundary rules
- credential storage instructions

Additional tools, tests, reports, baseline files, and link plans are allowed only where
documented by the explicit phase sections below.

Forbidden in the initial scaffold slice:

- Home Assistant API calls
- scripts that call Home Assistant
- token loaders
- deployment automation
- install automation
- runtime code changes
- Home Assistant services
- write-service calls
- scenario runner
- MQTT publishing
- helper mutation
- dashboard creation
- restart or reload automation
- stable runtime integration
- real-device integration
- release-gate enforcement
- public docs updates
- root `PROPOSALS.md` promotion

## Phase 2A Scope

Phase 2A adds a read-only identity/connectivity preflight. It proves that lab
target identity, lab credential isolation, source branch, source commit, manifest
version, and basic Home Assistant API reachability can be confirmed before later
lab validation work.

Approved Phase 2A tool:

```bash
python3 .codex/lab/tools/ha_lab_identity_preflight.py
```

Allowed Phase 2A Home Assistant calls:

```text
GET /api/
GET /api/config
```

Still forbidden in Phase 2A:

- Home Assistant service calls
- `/api/states`
- `/api/services`
- diagnostics calls
- dashboard export
- helper mutation
- MQTT publishing
- restart or reload
- deployment or install automation
- scenario runner
- production telemetry mirroring
- shadow mode
- release-gate enforcement

Phase 2A reports are written under `.codex/lab/reports/` and must remain
local-only, redacted, and evidence-only.

## Phase 2B Scope

Phase 2B adds a read-only HI presence inventory. It answers only whether
Humidity Intelligence is visible in the HA Lab instance through minimal read-only
evidence.

Approved Phase 2B tool:

```bash
python3 .codex/lab/tools/ha_lab_hi_presence_inventory.py
```

Allowed Phase 2B Home Assistant calls:

```text
GET /api/
GET /api/config
GET /api/services
GET /api/states/sensor.hi_diagnostics
GET /api/states/sensor.humidity_intelligence_hi_diagnostics
```

The diagnostics fallback entity is checked only when the primary diagnostics
entity is not found.

Still forbidden in Phase 2B:

- bulk `GET /api/states`
- Home Assistant service calls
- `/api/events`
- `/api/template`
- diagnostics export
- dashboard export
- helper mutation
- MQTT publishing
- restart or reload
- deployment or install automation
- scenario runner
- production telemetry mirroring
- shadow mode
- release-gate enforcement

Phase 2B reports must summarize HI presence only. They must not include full
service dumps, full state payloads, unrelated entity lists, token values, bearer
headers, or release-readiness claims.

## Phase 3A Scope

Phase 3A implements the approved safest mock telemetry first slice as local-only
contract tooling. It records the corrected entity boundary before any HA Lab helper
or wrapper is created.

Approved Phase 3A tool:

```bash
python3 .codex/lab/tools/ha_lab_mock_telemetry_contract.py
```

Approved minimum first-slice sensors:

- `sensor.hi_lab_humidity_room_01`
- `sensor.hi_lab_temperature_room_01`
- `sensor.hi_lab_iaq_01`
- `sensor.hi_lab_co_01`

Deferred optional branch coverage:

- `sensor.hi_lab_voc_01`
- `sensor.hi_lab_pm25_01`

Blocked fake outputs:

- `fan.hi_lab_fake_fan_zone_1`
- `fan.hi_lab_fake_fan_zone_2`
- `fan.hi_lab_fake_fan_aq`

Phase 3A makes no Home Assistant calls and creates no helpers. It writes only a
local contract report under `.codex/lab/reports/`.

Still forbidden in Phase 3A:

- Home Assistant API calls
- Home Assistant service calls
- helper creation or mutation
- YAML generation
- dashboard creation or export
- fake `fan.*` creation
- output-write validation
- MQTT publishing
- restart or reload
- deployment or install automation
- production telemetry mirroring
- shadow mode
- release-gate enforcement

## Phase 3A Addendum: Six-Sensor Family Expansion

Phase 3A now has a Stage 1 addendum preparing a bounded expansion from the completed
four-sensor first slice to six sensors per telemetry family, for 36 HA Lab telemetry
sensor wrappers total.

Active addendum packet:

```text
.codex/lab/implementation/phase-3a-six-sensor-family-expansion-addendum.md
```

Stage 1 evidence report:

```text
.codex/lab/reports/2026-06-01T16-22-04Z-phase-3a-six-sensor-expansion-stage-1.md
```

Stage 2 local contract evidence:

```text
.codex/lab/reports/2026-06-01T16-51-15Z-mock-telemetry-contract.md
.codex/lab/reports/2026-06-01T16-53-29Z-six-sensor-expansion-stage-2.md
```

Stage 2 status: local contract/tool/test implementation is complete. Stage 2B HA Lab
helper creation executed through the approved dry-run-first transport packet.

Stage 2B automated helper-creation packet:

```text
.codex/lab/implementation/stage-2b-automated-helper-creation-packet.md
```

Stage 2B status: executed. Final no-mutation dry-run readback confirmed
`exists_exact=108` for the approved helper/wrapper surface. A fresh read-only
revalidation on 2026-06-06 again confirmed `exists_exact=108` and performed no Home
Assistant mutation.

Stage 2B evidence:

```text
.codex/lab/reports/2026-06-01T17-19-27Z-stage-2b-helper-creator-dry-run.md
.codex/lab/reports/2026-06-01T17-20-13Z-stage-2b-automated-creation-due-process.md
.codex/lab/reports/2026-06-01T17-39-22Z-stage-2b-helper-creator-execution.md
.codex/lab/reports/2026-06-01T17-40-03Z-stage-2b-helper-creator-execution.md
.codex/lab/reports/2026-06-01T17-41-38Z-stage-2b-helper-creator-execution.md
.codex/lab/reports/2026-06-01T17-41-51Z-stage-2b-helper-creator-dry-run.md
.codex/lab/reports/2026-06-01T17-41-56Z-mock-telemetry-contract.md
.codex/lab/reports/2026-06-01T17-45-29Z-stage-2b-pm25-unit-readback-note.md
.codex/lab/reports/2026-06-06T13-57-31Z-stage-2b-helper-creator-dry-run.md
```

Stage 3 runtime-readiness packet:

```text
.codex/lab/implementation/stage-3-six-sensor-runtime-readiness-packet.md
```

Stage 3 status: read-only execution passed on 2026-06-09 after the v2.0.7 PM2.5
aggregate fix was committed to `senyo888-patch-1`, pushed, deployed to HA Lab, and
activated by Home Assistant restart. The approved six-sensor helper/wrapper surface
remains exact at `108/108`, with all six families showing `6/6` wrappers, `6/6`
value helpers, and `6/6` availability controls. Runtime readiness is `PASS`; the HA
Lab runtime truth surface now exposes
`sensor.humidity_intelligence_hi_house_pm25_average`.

Stage 3 evidence:

```text
.codex/lab/reports/2026-06-09T18-29-19Z-stage-3-six-sensor-runtime-readiness.md
.codex/lab/reports/2026-06-09T18-26-56Z-stage-3-six-sensor-runtime-readiness.md
.codex/lab/reports/2026-06-06T14-39-27Z-stage-3-six-sensor-runtime-readiness.md
```

Operational beta validation packet:

```text
.codex/lab/implementation/operational-beta-validation-packet.md
```

Review evidence:

```text
.codex/reports/audits/2026-06-01-ha-lab-six-sensor-expansion-bella-review.md
.codex/reports/audits/2026-06-01-ha-lab-six-sensor-expansion-aetherwing-review.md
```

Stage 1 is documentation and proposal alignment only. It performs no Home Assistant
calls, creates no helpers, mutates no dashboards, changes no runtime code, and does not
promote root `PROPOSALS.md`.

Stage 2 approval was received with:

```text
APPROVED: Stage 2 HA Lab sensor expansion
```

The local mock telemetry contract/tooling/tests were updated. The first Stage 2 report
stopped before helper creation, then the separate approved Stage 2B packet executed the
helper-backed entity expansion and final exact readback confirmed the expected 108
helper/wrapper entities. Any future HA Lab creation must preserve existing first-slice
`*_01` entities, record created vs already-existing entities, avoid fake outputs, and
leave production runtime/dashboard semantics unchanged.

## Phase 3B Scope

Phase 3B is the approved manual wrapper-creation checklist. It does not authorize Codex
automation or Home Assistant mutation from tools. It gives Senyo the manual HA Lab UI
steps for creating the four approved mock telemetry wrappers.

Checklist:

```text
.codex/lab/implementation/phase-3b-manual-mock-telemetry-wrapper-checklist.md
```

Approved Phase 3B manual entities:

- `sensor.hi_lab_humidity_room_01`
- `sensor.hi_lab_temperature_room_01`
- `sensor.hi_lab_iaq_01`
- `sensor.hi_lab_co_01`

Phase 3B still blocks:

- `sensor.hi_lab_aqi_01`
- `sensor.hi_lab_voc_01`
- `sensor.hi_lab_pm25_01`
- fake `fan.*` entities
- output-write validation
- Home Assistant API mutation tooling
- Home Assistant service calls from Codex
- YAML generation
- dashboard mutation
- release-gate use

## Current Operational Beta Baseline

The current HA Lab baseline is the accepted Operational Beta Validation Infrastructure
baseline from 2026-06-09. It supersedes the older Phase 2C first-slice runtime
observation as the live comparison point while preserving that older report as
historical evidence.

Current baseline:

```text
.codex/labs/ha-lab/current-baseline.md
```

Detailed baseline:

```text
.codex/lab/baselines/current-first-slice-runtime-baseline.md
```

Operational beta validation packet:

```text
.codex/lab/implementation/operational-beta-validation-packet.md
```

Baseline source:

```text
.codex/lab/reports/2026-06-09T18-23-00Z-stage-a-package-deploy.md
.codex/lab/reports/2026-06-09T18-29-19Z-stage-3-six-sensor-runtime-readiness.md
```

Superseded first-slice source:

```text
.codex/lab/reports/2026-05-23T16-24-39Z-hi-configuration-result-check.md
```

Current operational beta baseline means:

- the source identity is `senyo888-patch-1` at `03d18d1`;
- manifest version is `2.0.7-beta.1`;
- Stage A full-package deploy identity and source/remote comparison passed;
- rollback backup evidence exists for the HA Lab package replacement;
- Stage 3 six-sensor runtime readiness is `PASS`;
- the approved helper/wrapper surface is exact at `108/108`;
- canonical PM25 aggregate runtime truth is present and numeric;
- the legacy dotted PM2.5 aggregate entity is absent as expected;
- generated-card/entity-map release proof is not captured by this baseline;
- stable Home Assistant was not touched;
- this is advisory beta evidence only, not a release gate.

This supersedes the earlier Phase 2B report that showed HI as `not installed`, and the
Phase 2C first-slice baseline that accepted the original four-sensor runtime
observation.

All timestamped reports under `.codex/lab/reports/` are historical/advisory unless
explicitly referenced by the current baseline. A referenced report is source evidence,
not the live baseline itself.

Future HA Lab reports must include branch or worktree identity, evidence date, exact
target, whether mutation occurred, rollback path, and authority classification. The
authority classification must state whether the report is release-blocking or advisory.

The superseded Phase 2C first-slice baseline meant:

- HI is installed and visible in the HA Lab.
- `sensor.hi_diagnostics` is present and `ok`.
- first-slice telemetry mapping is accepted.
- runtime posture is acceptable for read-only lab observation.
- optional/generated residue is accepted only for this constrained first slice.
- generated dashboard truthfulness is not release-clean.
- output validation remains blocked.
- this is not a release gate.

The current operational beta baseline adds no Home Assistant calls, service calls,
credential loading, runtime code, deployment automation, helper mutation, dashboard
mutation, restart, or reload by itself. Any future HA Lab operation still needs its
own allowed packet or checklist scope.

## Phase 3D.2 Runner Creation Scope

Phase 3D.2 creates a report-only Phase 3D-class runner skeleton. It is local tooling
only and does not execute scenarios against HA Lab.

Approved Phase 3D.2 tool:

```bash
python3 .codex/lab/tools/ha_lab_phase_3d_runner.py
```

Phase 3D.2 may validate runner-creation boundaries and write a local runner-creation
report. It makes no Home Assistant calls and cannot execute Home Assistant service
calls or mutations.

Latest report-only execution report:

```text
.codex/lab/reports/2026-05-24T16-25-18Z-phase-3d2-runner-creation.md
```

Post-run runtime-safety validation:

```text
.codex/reports/audits/2026-05-24-ha-lab-phase-3d2-post-run-runtime-safety-validation-aetherwing-review.md
```

Phase 3D.2 records these approvals:

- Aetherwing validated the pre-mutation action list as a governance gate.
- Senyo approved runner creation only.
- Aetherwing validated the exact runner creation packet.
- Aetherwing validated the completed report-only run as a stop state.

Still forbidden in Phase 3D.2:

- runner execution against HA Lab
- Home Assistant API calls
- Home Assistant service calls
- helper value mutation
- availability toggle mutation
- switch restoration
- Phase 3D-class rerun
- dashboard mutation
- YAML generation
- fake `fan.*` entity creation
- output-write validation
- stable Home Assistant access
- release-gate enforcement

## Phase 3D-Class Pre-Mutation Readiness Scope

The pre-mutation action list has now been executed only as a read-only readiness pass.
This is not a Phase 3D-class scenario rerun and not mutation authority.

Approved read-only readiness tool:

```bash
python3 .codex/lab/tools/ha_lab_phase_3d_pre_mutation_readiness.py
```

Latest read-only readiness report:

```text
.codex/lab/reports/2026-05-24T16-54-13Z-phase-3d-class-pre-mutation-readiness.md
```

Aetherwing completion review:

```text
.codex/reports/audits/2026-05-24-ha-lab-phase-3d-class-pre-mutation-readiness-completion-aetherwing-review.md
```

This pass performed only:

- `GET /api/`
- `GET /api/config`
- exact targeted `GET /api/states/<entity_id>` reads listed in the report

It confirmed HA Lab identity, HA version, diagnostics, approved wrapper/helper/toggle
state capture, control-state capture, and blocked fake-output/deferred entity absence.

Still forbidden after this readiness pass:

- Home Assistant service calls
- helper value mutation
- availability toggle mutation
- `switch.*` restoration or mutation
- Phase 3D-class scenario rerun
- dashboard mutation
- YAML generation
- fake `fan.*` entity creation
- output-write validation
- stable Home Assistant access
- release-gate enforcement

## Phase 3E Scenario Matrix Read-Only Validation Scope

Phase 3E adds the approved HA Lab scenario-matrix read-only validation slice. It
checks only the current first-slice baseline plus backend mode/reason truth capture
and does not run scenario replay or mutate Home Assistant.

Packet:

```text
.codex/lab/implementation/phase-3e-scenario-matrix-read-only-validation.md
```

Scenario matrix:

```text
.codex/lab/implementation/ha-lab-scenario-matrix.md
```

Approved Phase 3E tool:

```bash
python3 .codex/lab/tools/ha_lab_scenario_matrix_readiness.py
```

Current final read-only baseline report:

```text
.codex/lab/reports/2026-05-31T16-42-20Z-scenario-matrix-read-only-validation.md
```

Phase 3E may validate only:

- current first-slice baseline truth for `HA-LAB-SM-001`
- backend mode/reason source capture for `HA-LAB-SM-011`
- deferred status for mutation-required scenarios

Still forbidden in Phase 3E:

- Home Assistant service calls
- helper value mutation
- availability toggle mutation
- `switch.*` restoration or mutation
- scenario replay
- CO pressure
- dashboard mutation or export
- YAML generation
- fake `fan.*` entity creation
- output-write validation
- stable Home Assistant access
- release-gate enforcement

## Phase 3F Scenario Matrix Safe Mutation Scope

Phase 3F records the bounded HA Lab safe-mutation validation slice for the approved
scenario matrix. It remains HA Lab evidence only, with rollback defined and CO
pressure opt-in rather than default.

Packet:

```text
.codex/lab/implementation/phase-3f-scenario-matrix-safe-mutation-validation.md
```

Approved Phase 3F tool:

```bash
python3 .codex/lab/tools/ha_lab_scenario_matrix_mutation_runner.py
```

Key continuity reports:

```text
.codex/lab/reports/2026-05-31T16-34-46Z-scenario-matrix-safe-mutation-validation.md
.codex/lab/reports/2026-05-31T16-39-59Z-scenario-matrix-safe-mutation-validation.md
.codex/lab/reports/2026-05-31T16-42-33Z-phase-3f-fault-fix-and-mutation-summary.md
.codex/lab/reports/2026-05-31T15-58-55Z-helper-baseline-restore-after-failed-run.md
.codex/lab/reports/2026-05-31T15-43-27Z-co-emergency-latch-repair.md
```

Phase 3F continuity result: the final recorded blocker was HA Lab transport/VM
instability under repeated mutation pressure after runtime defects were isolated and
documented, not an unresolved helper baseline leak in the canonical local continuity
record.

## Phase 4A Scope

Phase 4A classifies HA Lab generated-UI gaps from existing local evidence before
adding sensors or mutating dashboards.

Approved Phase 4A tool:

```bash
python3 .codex/lab/tools/ha_lab_ui_gap_classifier.py
```

Phase 4A reads only an existing diagnostics/config-entry JSON export and local lab
baseline/report files. It makes no Home Assistant calls.

Phase 4A answers:

- whether more first-slice sensors are required before UI work
- whether missing frontend resources are blocking rendered UI
- which unresolved placeholders are output/control residue
- which unresolved placeholders are optional telemetry residue
- which unresolved placeholders are stale/default room or unconfigured-level residue
- whether a separately approved full generated-card export is needed

Still forbidden in Phase 4A:

- Home Assistant API calls
- Home Assistant service calls
- `dump_cards`
- dashboard creation or mutation
- helper creation or mutation
- YAML generation
- MQTT publishing
- restart or reload
- deployment or install automation
- fake `fan.*` entity creation
- output-write validation
- production telemetry mirroring
- release-gate enforcement
- runtime code changes

## Phase 4B Scope

Phase 4B is the approved HA Lab frontend-resource readiness slice. It addresses the
Phase 4A finding that rendered UI is blocked by missing frontend resources, not by
missing first-slice sensors.

Checklist:

```text
.codex/lab/implementation/phase-4b-ha-lab-frontend-resource-readiness-plan.md
```

Report template:

```text
.codex/lab/templates/ui_render_readiness_report.md
```

Phase 4B originally expected missing resources to restore manually in HA Lab:

- `button-card`
- `mod-card`

Live Phase 4B investigation found that current `lovelace-card-mod` serves
`card-mod.js`, and that file provides `custom:mod-card`. Do not add a separate
`/hacsfiles/lovelace-card-mod/mod-card.js` resource when the asset returns `404`.

Phase 4B does not authorize Codex to call Home Assistant, install resources through
the API, create helpers, add sensors, paste dashboard YAML, run `dump_cards`, restart,
reload, or touch stable Home Assistant. Senyo performs any HACS/Lovelace resource
changes manually in the HA Lab UI.

After Senyo saves a fresh local diagnostics export, Codex may classify that local JSON
with:

```bash
python3 .codex/lab/tools/ha_lab_ui_gap_classifier.py --diagnostics-file /path/to/fresh/config_entry-humidity_intelligence.json
```

## Phase 4C Scope

Phase 4C creates a durable lab-only SSH deploy link so future HA Lab file deploys do
not depend on browser-terminal paste.

Plan:

```text
.codex/lab/implementation/phase-4c-lab-ssh-deploy-link-plan.md
```

Approved local SSH alias:

```bash
ssh -F .codex/private/ha_lab_ssh_config <ha-lab-ssh-alias>
```

Current SSH endpoint authority:

```text
.codex/private/ha_lab_ssh_config
```

Historical endpoint values in reports remain evidence only and must not be hardcoded
into future deploy commands.

Verified public key fingerprint: recorded in local private operator notes, not in
committed lab governance docs.

Phase 4C must remain HA Lab only. It does not authorize stable/prod/home SSH targets,
password-based deployment, restart/reload automation, dashboard mutation, helper
mutation, sensor expansion, fake outputs, HACS release/update automation, or hidden
deploys from unreviewed source files.

Future package deploys over this link must follow the branch/worktree package deploy
gate in `.codex/governance/proposals/drafts/2026-05-28-ha-lab-branch-worktree-package-deploy-gate.md`.
That proposal keeps branch selection and initial testing on the development machine,
uses SSH only as the final lab transport, deploys the full integration package by
default, and keeps runtime activation as a separate approval stage.

## Phase 4D Scope

Phase 4D implements the governed Stage A full-package package-deploy gate and executes
one HA Lab deploy-only filesystem copy after Senyo approval.

Operation packet:

```text
.codex/lab/implementation/phase-4d-stage-a-package-deploy-operation-packet.md
```

Approved Stage A tool:

```bash
python3 .codex/lab/tools/ha_lab_stage_a_package_deploy.py --dry-run --operation-packet .codex/lab/implementation/phase-4d-stage-a-package-deploy-operation-packet.md --approval-reference "Senyo approved Stage A HA Lab package deploy in current Codex thread on 2026-05-28"
```

Latest Stage A deploy-only report:

```text
.codex/lab/reports/2026-06-09T18-23-00Z-stage-a-package-deploy.md
```

Result: full integration package copied into the HA Lab
`/config/custom_components/humidity_intelligence/` through the Phase 4C SSH alias
after a timestamped remote backup. Source and remote hash manifests matched.

Runtime impact: files changed on the HA Lab filesystem only during Stage A. Runtime
activation/restart is a separate approval and evidence step, never standing authority
from Stage A. The 2026-06-09 Stage 3 PASS report is the current post-activation
read-only runtime evidence for the deployed `2.0.7-beta.1` package. No helper,
dashboard, output, stable Home Assistant, or generated UI mutation is authorized by
the operational beta baseline. The deploy report records release-candidate validation
as true for the clean `senyo888-patch-1` source identity, but HA Lab evidence remains
advisory rather than release authority.

Latest Stage B post-restart validation report:

```text
.codex/lab/reports/2026-05-28T12-47-31Z-stage-b-post-restart-validation.md
```

Stage B validation result: HA API identity checks passed, Home Assistant reported
`2026.5.4`, the `humidity_intelligence` service domain was present, diagnostics entity
`sensor.hi_diagnostics` was present with state `ok`, and the inventory verdict was
`installed`. Log review was blocked because `/api/error_log` returned `404` and no
`/config/home-assistant.log*` files were present.

Phase 4D does not authorize changed-file deploys, package overlays, stable/prod/home
targets, Git authority inside Home Assistant, HACS automation, restart/reload,
dashboard mutation, helper mutation, Stage B activation, release-candidate validation,
or release promotion.

## Credential Storage

Senyo stores the long-lived token locally after this scaffold exists. Do not paste it into chat, reports, commits, screenshots, release notes, pull requests, or public docs.

Create the private folder locally:

```bash
mkdir -p .codex/private
chmod 700 .codex/private
```

Create this ignored local file:

```text
.codex/private/ha_lab_runtime.env
```

Use only these variable names:

```bash
HI_LAB_HA_BASE_URL=
HI_LAB_HA_TOKEN=
HI_LAB_INSTANCE_LABEL=humidity-intelligence-lab
```

Set `HI_LAB_HA_BASE_URL` to the current HA Lab URL in the ignored private env file.
Do not hardcode that URL in reusable deploy commands or proposal gates.

Do not use these names for the HA Lab Runtime:

```bash
HA_URL
HA_TOKEN
HOME_ASSISTANT_TOKEN
PROD_HA_TOKEN
STABLE_HA_TOKEN
```

## Future Command Identity Banner

Any future command that can target Home Assistant must display the following before it can run:

- instance label
- HA base URL
- token fingerprint only, never token value
- source branch
- source commit
- manifest version
- intended operation
- whether the operation is read-only or mutating

First-slice status: documented only. No command implements this yet.

## Fail-Closed Rule

Future lab tooling must fail closed when target identity, lab-only credentials, branch, commit, manifest version, or operation mode cannot be confirmed. Failure to identify the target is a stop condition, not a prompt to guess.

## Manual Copy Contamination Rule

Any manual copy into Home Assistant `custom_components` is contaminated as source evidence until reconciled back to the repository or a named worktree. Lab findings must be reproduced in source before they can affect release truth.

## Deletion Safety

This folder is local governance/report scaffolding only. Deleting `.codex/lab/` must not affect Humidity Intelligence runtime behavior, Home Assistant state, release metadata, services, entities, dashboards, or tests.
