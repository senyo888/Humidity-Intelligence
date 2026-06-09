# Current HA Lab Operational Beta Baseline

Status: accepted Operational Beta Validation Infrastructure baseline.

This baseline summarizes local HA Lab evidence only. It is not release authority, not
runtime authority, not stable Home Assistant authority, not deployment approval, and not
permission for autonomous mutation.

Canonical pointer:

```text
.codex/labs/ha-lab/current-baseline.md
```

Detailed baseline path:

```text
.codex/lab/baselines/current-first-slice-runtime-baseline.md
```

Operational runbook:

```text
.codex/lab/implementation/operational-beta-validation-packet.md
```

## Baseline Identity

- Branch/worktree identity: `senyo888-patch-1` at commit `03d18d1`
- Commit subject: `Fix PM25 aggregate runtime truth`
- Manifest version: `2.0.7-beta.1`
- Evidence date: `2026-06-09`
- Exact target: HA Lab instance `humidity-intelligence-lab`
- Stable Home Assistant touched: no
- Authority classification: advisory HA Lab operational beta baseline; not
  release-blocking and not release authority

## Source Evidence

- Stage A deploy report:
  `.codex/lab/reports/2026-06-09T18-23-00Z-stage-a-package-deploy.md`
- Stage 3 PASS report:
  `.codex/lab/reports/2026-06-09T18-29-19Z-stage-3-six-sensor-runtime-readiness.md`
- Superseded first-slice baseline source:
  `.codex/lab/reports/2026-05-23T16-24-39Z-hi-configuration-result-check.md`

Referenced reports remain evidence inputs. This baseline document is the current local
comparison point for beta-validation review.

## Stage A Deploy Baseline

- Operation: full-package HA Lab Stage A deploy
- Source branch: `senyo888-patch-1`
- Source commit: `03d18d1`
- Manifest version: `2.0.7-beta.1`
- Source worktree clean before copy: yes
- Full package deploy: yes
- Changed-file or partial-package deploy attempted: no
- Source/remote hash-manifest comparison: pass
- Rollback evidence: timestamped HA Lab backup captured before replacement
- Restart/reload authority from Stage A: not granted by Stage A itself

Stage A validates package transport identity and rollback evidence. It does not by
itself prove runtime activation, generated dashboard truth, release readiness, or stable
Home Assistant safety.

## Stage 3 Runtime-Readiness Baseline

- Operation: read-only Stage 3 six-sensor runtime-readiness check
- Home Assistant service calls: none
- Mutating actions: none
- Helper mutation: none
- Availability toggle mutation: none
- Scenario execution: none
- Dashboard mutation: none
- Fake outputs: blocked/absent
- Stable Home Assistant access: none
- Sensor wrappers: `36/36`
- Value helpers: `36/36`
- Availability controls: `36/36`
- Expected helper/wrapper entities: `108/108`
- Stage 3 verdict: `PASS`

Runtime truth captured by the current PASS report:

- `sensor.humidity_intelligence_hi_house_pm25_average`: `5.0`
- `sensor.humidity_intelligence_hi_level1_pm25_average`: `5.0`
- `sensor.humidity_intelligence_hi_level2_pm25_average`: `5.0`
- legacy dotted-slug entity `sensor.humidity_intelligence_hi_house_pm2_5_average`:
  HTTP `404`

The PM2.5 aggregate beta fix is therefore admitted as current HA Lab operational beta
evidence. That admission remains advisory and does not close release gates by itself.

## Generated-Card And Entity-Map Sanity Boundary

The current baseline proves that the runtime-facing PM25 aggregate entities and the
six-sensor helper/wrapper surface are present and readable in HA Lab. It does not prove
that generated mobile/tablet cards were exported, pasted, browser-refreshed, or visually
reviewed after the beta deploy.

Before a release-readiness decision where card truth is in scope, collect separate
generated-card/entity-map evidence covering:

- `dump_cards` or exported card source identity;
- stale mapping and unresolved placeholder checks;
- PM25 card/entity-map references use backend runtime truth only;
- no private entity IDs, room names, device IDs, URLs, or helper values leak into
  public docs or examples;
- optional frontend-card dependency assumptions are recorded as present, blocked, or
  not applicable.

## Rollback Boundary

Rollback evidence exists at the Stage A report level. Any restore from that backup is
HA Lab only and requires separate approval before runtime activation, restart, or reload.
It is not production rollback, HACS rollback, stable Home Assistant rollback, or release
rollback.

## Authority Boundary

HA Lab evidence now feeds normal beta-validation review as advisory operational
evidence. It does not replace:

- `DESIGN_BRIEF.md`
- source code in the relevant branch/worktree
- Bella coherence review
- Aetherwing runtime/risk validation
- AetherCore governance consistency review
- release-candidate validation
- stable Home Assistant evidence when explicitly required
- Senyo approval

## Superseded Evidence

This baseline supersedes the Phase 1E first-slice baseline as the current comparison
point:

```text
.codex/lab/reports/2026-05-23T16-24-39Z-hi-configuration-result-check.md
```

That older report remains valid historical evidence for the original first-slice lab
observation. It no longer represents the current beta validation baseline.

All other timestamped reports under `.codex/lab/reports/` are historical/advisory unless
a future current baseline explicitly references them. They must not compete with this
baseline as runtime truth, release readiness, implementation approval, generated UI
truth, or release authority.

## Baseline Verdict

- Package deploy identity: passed
- Full-package deploy comparison: passed
- Rollback evidence: present for HA Lab package restore
- Runtime activation evidence: present only through later approved/manual activation
  context, not through standing Stage A authority
- Six-sensor helper/wrapper readiness: passed
- PM25 runtime aggregate truth: passed for canonical `pm25` entity IDs
- Legacy dotted PM2.5 aggregate entity: absent as expected
- Generated-card/entity-map release proof: not captured by this baseline
- Stable Home Assistant status: untouched
- Release-gate status: not a release gate

## Next Safe Use

Use this baseline for the next beta-readiness review and for comparison before future
HA Lab reads. The next recommended HA Lab action is an advisory generated-card/entity-map
sanity pass if the beta is being prepared for release-readiness review.
