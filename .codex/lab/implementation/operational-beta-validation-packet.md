# HA Lab Operational Beta Validation Packet

Status: retained continuity packet. The current active runbook is
`.codex/lab/implementation/operational-beta-validation-runbook.md`.

Purpose: admit HA Lab into the normal Humidity Intelligence beta-validation workflow as
Operational Beta Validation Infrastructure while keeping it non-binding, local-only,
and isolated from stable Home Assistant.

This packet is a checklist and evidence contract. It does not authorize runtime source
changes, UI/card YAML changes, entity semantics changes, helper/dashboard/output
mutation, new scenario mutation runners, stable Home Assistant access, restart/reload
calls, push, tag, release, or PR creation.

## Authority Boundary

HA Lab evidence is useful, expected, and part of beta-validation review. It remains
advisory evidence only.

HA Lab evidence is not:

- release authority;
- runtime authority;
- stable Home Assistant authority;
- a substitute for Bella, Aetherwing, AetherCore, or Senyo gates;
- permission for autonomous mutation;
- proof that generated dashboards have been refreshed unless card evidence is captured;
- proof that stable Home Assistant is safe.

## Current Green Baseline

- Branch/worktree identity: `senyo888-patch-1`
- Source commit: `03d18d1`
- Commit subject: `Fix PM25 aggregate runtime truth`
- Manifest version: `2.0.7-beta.1`
- Stage A deploy report:
  `.codex/lab/reports/2026-06-09T18-23-00Z-stage-a-package-deploy.md`
- Stage 3 PASS report:
  `.codex/lab/reports/2026-06-09T18-29-19Z-stage-3-six-sensor-runtime-readiness.md`
- Canonical current baseline:
  `.codex/lab/baselines/current-first-slice-runtime-baseline.md`
- Current baseline pointer:
  `.codex/labs/ha-lab/current-baseline.md`
- Current runbook:
  `.codex/lab/implementation/operational-beta-validation-runbook.md`

Current beta evidence:

- Stage A full-package deploy: pass
- Source/remote package comparison: pass
- Rollback backup evidence: present
- Stage 3 verdict: `PASS`
- Six-sensor helper/wrapper surface: `108/108`
- `sensor.humidity_intelligence_hi_house_pm25_average`: `5.0`
- `sensor.humidity_intelligence_hi_level1_pm25_average`: `5.0`
- `sensor.humidity_intelligence_hi_level2_pm25_average`: `5.0`
- legacy dotted-slug entity `sensor.humidity_intelligence_hi_house_pm2_5_average`:
  HTTP `404`

## Aetherbite Workflow Shape

After a beta deploy, the maintainer should do this in order:

1. Confirm source identity from the canonical checkout or active worktree.
2. Run Stage A as a full-package deploy only, with package comparison and rollback
   evidence.
3. Treat runtime activation as a separate approval moment. A Stage A deploy does not
   grant restart or reload authority.
4. After activation, collect read-only runtime evidence: HA identity, HI service
   presence, diagnostics, key runtime entities, and log/startup evidence where
   available.
5. Run Stage 3 when aggregate telemetry or air-quality truth is in scope.
6. Capture generated-card/entity-map sanity only when UI truth or release readiness
   needs that evidence.
7. Summarize HA Lab status in the PR or release-readiness review as advisory evidence,
   with blockers or caveats stated plainly.

Keep the workflow light: if a change is docs-only or unrelated to HA runtime/card truth,
mark HA Lab as `not applicable` rather than inventing a lab ritual.

## Checklist

### 1. Package Deploy Identity Checks

- [ ] Canonical checkout or active worktree confirmed.
- [ ] Branch/worktree identity recorded.
- [ ] Source commit recorded.
- [ ] Manifest version recorded.
- [ ] Source dirty/clean state recorded.
- [ ] Target classification recorded as HA Lab only.
- [ ] Private target details omitted from public docs, PRs, and release notes.
- [ ] No stable-looking target, generic HA env var, or fallback target is selectable.

### 2. Stage A Full-Package Deploy

- [ ] Full integration package staged.
- [ ] Changed-file or partial-package deploy rejected.
- [ ] Source hash manifest created.
- [ ] Remote backup created before replacement.
- [ ] Remote hash manifest created.
- [ ] Source/remote hash manifests match.
- [ ] Stage A report written.
- [ ] Stage A report states advisory authority classification.
- [ ] Stage A report states restart/reload authority is separate.

### 3. Runtime Activation Or Restart Approval

- [ ] Runtime activation approval source recorded.
- [ ] Activation method recorded as manual maintainer action or separately approved
      HA Lab action.
- [ ] No standing restart/reload authority inferred from Stage A.
- [ ] Stable Home Assistant not touched.
- [ ] If activation is blocked or not run, record `not activated` and stop before
      runtime-readiness claims.

### 4. Read-Only Soak And Diagnostics Checks

- [ ] HA API identity check passed or blocker recorded.
- [ ] Home Assistant version recorded.
- [ ] HI service/domain presence recorded.
- [ ] Diagnostics entity state recorded.
- [ ] Startup/log evidence recorded, or unavailable log access recorded as blocked.
- [ ] Air-control mode/reason and relevant aggregate entities recorded.
- [ ] No Home Assistant service call, helper mutation, dashboard mutation, output
      write, scenario replay, restart, or reload performed during read-only checks.

### 5. Stage 3 Six-Sensor Runtime Readiness

- [ ] Stage 3 is relevant to the beta scope, or marked `not applicable`.
- [ ] Approved helper/wrapper surface exactness recorded.
- [ ] `36/36` sensor wrappers confirmed when Stage 3 applies.
- [ ] `36/36` value helpers confirmed when Stage 3 applies.
- [ ] `36/36` availability controls confirmed when Stage 3 applies.
- [ ] Runtime aggregate truth checked for relevant families.
- [ ] Fake output entities remain absent or explicitly blocked.
- [ ] Stage 3 verdict recorded as `PASS`, `CONFIGURATION_NOT_READY`, `BLOCKED`, or
      `not applicable`.

### 6. Generated-Card And Entity-Map Truth Sanity

- [ ] Card/entity-map sanity is relevant to the beta scope, or marked
      `not applicable`.
- [ ] Export source identity recorded for any generated-card evidence.
- [ ] Stale mapping and unresolved placeholder checks recorded.
- [ ] Public examples contain no private entity IDs, room names, device IDs, URLs, or
      telemetry values.
- [ ] Generated cards consume backend runtime truth only.
- [ ] Optional frontend-card dependency status recorded as present, blocked, or not
      applicable.
- [ ] UI truth consistency risk stated explicitly.

### 7. Rollback Evidence And Boundaries

- [ ] Rollback backup path exists in the local report or is marked not required for
      read-only work.
- [ ] Rollback action is HA Lab only.
- [ ] Restart/reload after rollback requires separate approval.
- [ ] Rollback is not described as HACS rollback, production rollback, stable Home
      Assistant rollback, or release rollback.
- [ ] No cleanup or restore action is run without a separate exact packet.

### 8. PR And Release-Readiness Feed

- [ ] PR records HA Lab advisory status as `pass`, `fail`, `blocked`, `not run`, or
      `not applicable`.
- [ ] Release-readiness review treats HA Lab evidence as input, not authority.
- [ ] Bella review confirms source-of-truth and local/public boundary coherence.
- [ ] Aetherwing review confirms runtime/risk, rollback, lane-order, and UI-truth risk.
- [ ] AetherCore review remains dormant advisory governance consistency only.
- [ ] Senyo approval remains required for release promotion.

## House-Agent Review Contract

Use these roles as structured review lanes only:

- Aetherbite: workflow/product shape and maintainer ergonomics.
- Bella: coherence, source-of-truth, public/private boundary, and governance review.
- Aetherwing: runtime, deployment/restart, rollback, lane-order, and UI-truth risk.
- AetherCore: dormant advisory governance consistency check only.

AetherCore must not become a scheduler, standing reviewer, release authority,
autonomous approver, or runtime actor.

Required verdict fields:

```text
AETHERBITE_VERDICT:
BELLA_VERDICT:
AETHERWING_VERDICT:
AETHERCORE_VERDICT:
FINAL_VERDICT:
```

## Impact Defaults For Documentation-Only Updates

When this packet is updated without runtime source, UI template, entity, service, or
manifest changes, report:

- runtime impact: none;
- UI impact: none;
- entity semantics changed: no;
- migration required: no;
- restart required: no.
