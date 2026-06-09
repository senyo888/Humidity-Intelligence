# Stable And Lab Isolation Contract

Status: protected runtime-safety contract.

Purpose: keep stable Home Assistant, HA Lab, release-candidate validation, and local
governance evidence separated so lab work cannot quietly become production behavior or
release authority.

## Stable Home Assistant Boundary

Stable Home Assistant is protected production truth. Phase 1D does not authorize any
stable Home Assistant mutation.

Forbidden without a separate exact approval packet:

- service calls
- restarts or reloads
- helper mutation
- entity registry changes
- dashboard mutation
- output writes
- production telemetry mirroring
- shadow-mode comparison against stable
- installing or replacing Humidity Intelligence files

Read-only inspection may be used only when explicitly opened for a task and must be
reported as runtime evidence, not release approval.

## HA Lab Boundary

HA Lab is isolated evidence infrastructure. It may support future validation, but it
does not define runtime semantics by itself.

HA Lab is admitted as Operational Beta Validation Infrastructure for beta package
deploy evidence, runtime activation evidence, read-only soak/diagnostics checks, Stage
3 runtime-readiness checks, and generated-card/entity-map sanity evidence. This
admission is advisory only. It does not make HA Lab release authority, runtime
authority, stable Home Assistant authority, or permission for autonomous mutation.

HA Lab work must state:

- branch or worktree identity
- evidence date
- exact target
- whether mutation occurred
- rollback path
- whether the result is release-blocking or advisory

## Prohibited Lab Patterns

Phase 1D explicitly prohibits:

- fake outputs as release evidence
- shadow mode
- production telemetry mirroring
- reusable scenario runners without later exact approval
- lab evidence as release authority

Fake outputs, if ever proposed later, must be isolated to HA Lab, explicitly named,
non-production, rollback-defined, Aetherwing-reviewed, and unable to control real
devices. They still cannot prove release readiness by themselves.

## Release-Candidate Boundary

Release-candidate validation must run from a frozen branch or worktree. Lab evidence can
support release-candidate review only when tied to exact source identity, exact version,
and explicit validation scope.

Release-candidate evidence must not be mixed with active exploratory lab runs.

## Authority Rule

The authority chain is:

```text
DESIGN_BRIEF.md
-> source code in the relevant branch/worktree
-> approved governance contracts
-> Bella coherence review
-> Aetherwing runtime validation
-> release-candidate validation
-> Senyo approval
```

HA Lab reports and local tools are evidence. They are not authority.
