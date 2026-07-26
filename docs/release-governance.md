# Release Governance

Humidity Intelligence uses semantic versioning with explicit prerelease markers for
testing and validation branches.

## Canonical Version Model

- `2.0.9-beta.1`: testing build.
- `2.0.9-rc.1`: release-candidate build.
- `2.0.9`: stable version label. On `senyo888-patch-1`, `develop`, or `main`,
  stable metadata may be staged or promoted through the governed release path.
  Published release status comes from release tags, GitHub release publication, and
  maintainer approval.

The integration version in `manifest.json` is the release-state source of truth for
Home Assistant and HACS metadata checks.

v2.0.8 is the latest published stable release line. Tag and GitHub Release `v2.0.8`
were published from `main` on 2026-07-06.

The working metadata on `senyo888-patch-1` is `2.0.9-rc.1` for local
release-candidate validation. That branch state is not a tag, GitHub Release, HACS
publication, `develop` promotion, or `main` promotion. The maintainer has confirmed
stable-instance beta testing for the v2.0.9 line; the supplied private validation
packet remains a separate evidence lane and reports `PASS_WITH_NOTES` because two
configured visual-alert outputs currently exist but are unavailable. No generated
card reference is missing, and the warning remains visible until those household
outputs recover or their retained mappings are deliberately updated.

The former v2.0.8 candidate moved through `senyo888-patch-1`, `develop`, and `main`
before publication. Stable metadata on a staging or review branch was not release
authority; the published tag and GitHub Release now provide the public release fact.
Senyo has maintainer-confirmed stable-instance testing for v2.0.8; that evidence is
recorded as maintainer confirmation unless independently verified in the same
validation packet. Stable-instance access or mutation requires explicit approval for
this lane.

For future promotion candidates, release readiness needs more than Stage A HA Lab
package deploy evidence. Each release-readiness record must separately state whether
restart/reload approval, post-restart read-only checks, generated-card evidence, Bella
review, Aetherwing runtime/security review, AetherCore governance review, Aetherbite
release-language/visual review, maintainer stable-instance confirmation, and
maintainer promotion approval are complete.

## v2.0.8 Release Path Record

The v2.0.8 develop-review merge made `develop` the release-review source only. The
later `main` promotion, tag, and GitHub Release completed the publication path on
2026-07-06. The `develop` merge by itself did not publish or authorize the release.

The recorded develop-to-main promotion checklist was:

1. Confirm the develop-review PR merged to `develop` and GitHub CI is green.
2. Confirm CodeRabbit or human review comments have either been fixed or explicitly
   marked not applicable with a short reason.
3. Record sanitized HA Lab evidence in the PR body or a PR comment. Stage A package
   deploy evidence may prove full-package transport, backup creation, and source/remote
   hash agreement. Read-only Stage B evidence may prove current HA Lab reachability,
   runtime readiness, diagnostics/card counts, and scenario baseline. Without a
   separately approved Home Assistant restart or reload, Stage B does not prove that
   the just-copied package has been activated by Home Assistant.
4. Keep the generated-dashboard checkbox honest: if `refresh_ui`, dashboard paste,
   or browser refresh was not performed, leave that item unchecked and explain that
   users should re-export or refresh generated cards after install.
5. Preserve the hard release gates below as separate `main`, tag, and GitHub Release
   approval requirements.

For future releases, a `develop` merge must not be treated as tag, GitHub Release, or
`main` authority. Final promotion still requires maintainer approval, Bella coherence
review, Aetherwing runtime/release validation, AetherCore governance consistency
review, README/release approval, and the normal release sanity checks for the exact
branch being promoted.

For v2.0.9 owned-artifact namespace validation, the release packet must separately
record:

- exact diagnostics, self-check, release-check, generated-card, and registered
  dashboard paths;
- admin rejection before work for external `self_check`, `dump_cards`, and
  `view_cards`, continuity of trusted setup/options/release-test exports, and truthful
  cache-only startup refresh;
- single-entry and entry-qualified multi-entry filenames, exact purge preview/removal
  ownership, and retention of custom and legacy root artifacts;
- descriptor-relative no-follow atomic writer tests, including concurrent writes,
  directory creation/permissions, symlink, non-regular target, and directory
  substitution rejection;
- consumer migration and rollback evidence that does not treat stale root JSON/YAML
  as current output;
- a full Home Assistant restart after package installation before HA Lab runtime
  evidence. A config-entry reload may validate already-loaded options/regeneration
  behavior, but does not prove that newly installed Python or service schemas loaded.

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
  current stable manifest version from their base branch. Treat them as maintenance
  lanes only; release approval, tagging, and publication stay with the normal release
  gates.
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
  proposal/release-process consistency, and local/public boundary safety. AetherCore's
  role here is governance verification; runtime authority and release approval stay
  with the established maintainers and gates.
- Release sanity validation has passed for the change scope, including version
  governance, HACS/package metadata checks, and the relevant Home Assistant runtime,
  direct sanity, service, or generated-card checks.
- HA Lab beta-validation status is recorded when a beta package has been deployed,
  activated, soaked, or checked in HA Lab. This is operational evidence only: it can
  inform Bella, Aetherwing, AetherCore, maintainer, PR, and release-readiness review,
  while release approval, runtime semantics, stable Home Assistant validation, and
  mutation approval stay with their normal gates.
- The `humidity-intelligence-maintenance` companion has been updated with advisory
  release-gate evidence, blocker notes, or an explicit no-op maintenance status for
  the staging promotion. This records maintenance evidence; promotion approval and
  canonical HI truth stay in the canonical repo.
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

This guard protects the release boundary. Runtime logic, entity semantics, generated
dashboards, and Home Assistant services stay governed by the integration source.

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
