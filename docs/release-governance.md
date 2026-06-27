# Release Governance

Humidity Intelligence uses semantic versioning with explicit prerelease markers for
testing and validation branches.

## Canonical Version Model

- `2.0.7-beta.1`, `2.0.7-beta.2`: testing builds.
- `2.0.7-rc.1`: release-candidate builds.
- `2.0.7`: stable version label.

The integration version in `manifest.json` is the release-state source of truth for
Home Assistant and HACS metadata checks.

v2.0.7 is the current stable release line. Stable `2.0.7` metadata is present on
`main`, while `senyo888-patch-1` may still carry final release-validation fixes
ahead of `main` until those fixes are promoted. Tagging and GitHub release
publication remain gated until final validation, promotion, and maintainer
approval are complete. HA Lab advisory validation for commit `55dc2b9` passed on
2026-06-23 after lab-only deploy and manual restart; it remains evidence input,
not release authority. The rules below remain the active promotion model for future
versions and for any maintenance patch.

For a `2.0.8-beta.1` candidate, Stage A HA Lab package deploy evidence is not enough
to claim beta runtime validation. The release-readiness record must separately state
whether restart/reload approval, post-restart read-only checks, generated-card evidence,
Bella review, Aetherwing review, and maintainer staging approval are complete.

## Branch Responsibilities

- `senyo888-patch-1`: staging lane for all manifest labels. It may carry beta, rc,
  or stable version metadata while work is being prepared and reviewed.
- `develop`: release-candidate or stable version metadata only. Beta labels stay on
  `senyo888-patch-1`.
- `main`: stable production version metadata only. No prerelease suffix is allowed.
- `vMAJOR.MINOR.PATCH`: release-verification branch for the exact matching stable
  manifest version only. For example, `v2.0.7` may carry `2.0.7`, but not
  `2.0.7-rc.1` or `2.0.8`.
- `dependabot/*`: automated dependency-maintenance branches may inherit the
  current stable manifest version from their base branch. They are not release
  lanes and do not approve, tag, or publish a release.
- Short-lived development branches, including `Bella/*`, `codex/*`, `feature/*`,
  `fix/*`, `patch/*`, and `test/*`, must not carry stable manifest versions.

## Promotion Rules

1. Beta, rc, and stable labels may be staged on `senyo888-patch-1`.
2. Promotion to `develop` uses `MAJOR.MINOR.PATCH-rc.N` or stable
   `MAJOR.MINOR.PATCH` version metadata only.
3. Promotion to `main` uses stable `MAJOR.MINOR.PATCH` version metadata only.
4. Exact `vMAJOR.MINOR.PATCH` branches may be used for stable release-verification CI,
   but they do not replace the `main` release/tag gate.
5. A GitHub release is created only from a stable version on `main`.

## Hard Release Gates

No Humidity Intelligence version release, GitHub release, or release tag may be created
until all of these gates are satisfied:

- Bella verification has confirmed source-of-truth alignment, UI truth consistency,
  deterministic release boundaries, and README/release-note coherence.
- AetherCore verification has confirmed governance coherence, role-boundary integrity,
  proposal/release-process consistency, and local/public boundary safety. This is a
  governance verification gate; it does not make AetherCore a runtime authority or
  release approver.
- Release sanity validation has passed for the change scope, including version
  governance, HACS/package metadata checks, and the relevant Home Assistant runtime,
  direct sanity, service, or generated-card checks.
- HA Lab beta-validation status is recorded when a beta package has been deployed,
  activated, soaked, or checked in HA Lab. This is operational evidence only: it can
  inform Bella, Aetherwing, AetherCore, maintainer, PR, and release-readiness review,
  but it cannot approve a release, redefine runtime semantics, replace stable Home
  Assistant validation, or authorize autonomous mutation.
- The `humidity-intelligence-maintenance` companion has been updated with advisory
  release-gate evidence, blocker notes, or an explicit no-op maintenance status for
  the staging promotion. This records maintenance evidence only; it does not approve
  promotion or change canonical HI truth.
- Wiki update status is recorded as `updated`, `no-op`, or `blocked` for any release
  that changes support flow, diagnostics, generated dashboards, HACS/update guidance,
  configuration behavior, services, entity semantics, or release documentation. The
  Wiki remains a public support manual; runtime and release truth stay in the
  repository source and release documentation.
- The README has maintainer approval before release tagging.

If any gate is missing for the version being prepared, the release state is `not ready`,
even when the manifest version already carries a stable number on `senyo888-patch-1`,
`develop`, or `main`.

## Enforcement

`scripts/check_version_governance.py` validates the branch/version contract locally and
in CI. It rejects:

- prerelease versions on `main`
- beta versions on `develop`
- stable versions on short-lived testing branches
- prerelease or mismatched stable versions on `vMAJOR.MINOR.PATCH` branches
- stable versions on unapproved branches outside `senyo888-patch-1`, `develop`, and
  `main`, exact matching `vMAJOR.MINOR.PATCH` release-verification branches, and
  automated `dependabot/*` dependency-maintenance branches

This is a release-boundary guard only. It does not alter runtime logic, entity
semantics, generated dashboards, or Home Assistant services.

## HACS Integration Preflight

HACS Integration Preflight is an optional but recommended local/VS Code release-perimeter
check before promotion. Run it from the release-source checkout or a worktree after
implementation sanity and before the final release readiness review.

Use it for:

- HACS/install metadata validation
- release packaging sanity
- `manifest.json`, `hacs.json`, branding, workflow, and repository hygiene support

Do not treat it as a replacement for pytest, direct runtime/card sanity, Home Assistant
runtime validation, Bella coherence review, Aetherwing validation, or version governance.
Preflight findings are packaging/readiness findings only; they must not imply runtime
behavior, service, diagnostics, UI generation, or configuration-flow changes unless a
separate implementation patch is explicitly approved.

## HA Lab Operational Beta Validation

HA Lab is admitted into the normal beta-validation workflow as Operational Beta
Validation Infrastructure. Use it after beta deploys to collect practical runtime
evidence from an isolated Home Assistant lab instance while preserving repository and
review authority.

Expected HA Lab evidence for beta-readiness review:

- package deploy identity: source branch/worktree, commit, manifest version, target
  classification, and clean/dirty source state;
- Stage A full-package deploy result, including source/remote comparison and rollback
  backup evidence;
- runtime activation or restart approval evidence, clearly separated from Stage A
  deploy authority;
- read-only soak, diagnostics, service-domain, startup/log, and runtime entity checks;
- Stage 3 six-sensor runtime-readiness status where the beta touches air-quality or
  aggregate telemetry truth;
- generated-card and entity-map sanity findings when UI truth or card exports are in
  scope;
- rollback boundary and whether any HA Lab mutation occurred.

HA Lab evidence remains non-binding. It is not release authority, runtime authority,
stable Home Assistant authority, or a substitute for Bella coherence review,
Aetherwing runtime/risk validation, AetherCore governance consistency review,
release-candidate validation, or Senyo approval.
