# Current HA Lab Baseline Pointer

Status: Operational Beta Validation Infrastructure pointer.

Current baseline document:

```text
.codex/lab/baselines/current-first-slice-runtime-baseline.md
```

Current source evidence reports:

```text
.codex/lab/reports/2026-06-09T18-23-00Z-stage-a-package-deploy.md
.codex/lab/reports/2026-06-09T18-29-19Z-stage-3-six-sensor-runtime-readiness.md
```

Superseded first-slice source evidence:

```text
.codex/lab/reports/2026-05-23T16-24-39Z-hi-configuration-result-check.md
```

## Current Baseline Summary

- Branch/worktree identity: `senyo888-patch-1`
- Source commit: `03d18d1`
- Manifest version: `2.0.7-beta.1`
- Stage A full-package deploy: pass
- Source/remote package comparison: pass
- Rollback backup evidence: present
- Stage 3 six-sensor runtime readiness: `PASS`
- Six-sensor helper/wrapper surface: `108/108`
- Canonical PM25 aggregate runtime truth: present and numeric
- Stable Home Assistant touched: no
- Authority classification: advisory operational beta evidence only

## Authority Boundary

The current baseline is local HA Lab evidence only. It is advisory; it is not release
authority. It does not override `DESIGN_BRIEF.md`, source code, root `PROPOSALS.md`,
runtime-protection contracts, Bella review, Aetherwing validation, AetherCore
governance consistency review, release-candidate validation, stable Home Assistant
evidence, or Senyo approval.

HA Lab reports must not become release authority, runtime authority, stable Home
Assistant authority, or permission for autonomous mutation.

## Supersession Rule

All timestamped reports under `.codex/lab/reports/` are historical/advisory unless
explicitly referenced by the current baseline document above. Even referenced source
reports remain evidence inputs; the current baseline document is the live comparison
point.

Older reports must not be treated as competing runtime truth, release readiness,
implementation approval, or generated UI truth.

## Required Fields For Future Baselines

Every future HA Lab baseline update must include:

- branch or worktree identity
- evidence date
- exact target
- whether mutation occurred
- rollback path
- release-blocking or advisory classification
- source evidence report
- superseded baseline or report references
- explicit runtime/UI/entity/migration/restart impact statement
