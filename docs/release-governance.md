# Release Governance

Humidity Intelligence uses semantic versioning with explicit prerelease markers for
testing and validation branches.

## Canonical Version Model

- `2.0.5-beta.1`, `2.0.5-beta.2`: testing builds.
- `2.0.5-rc.1`: release-candidate builds on `develop` when the branch is ready for
  final validation.
- `2.0.5`: stable production release on `main` or `release/*` only.

The integration version in `manifest.json` is the release-state source of truth for
Home Assistant and HACS metadata checks.

## Branch Responsibilities

- `senyo888-patch-1`: beta/testing state only. Local Home Assistant validation should
  clearly show a `-beta.N` manifest version.
- `develop`: beta or release-candidate state. Use `-beta.N` while fixes are still
  moving, then `-rc.N` for final release validation.
- `main`: stable production state only. No prerelease suffix is allowed.
- `release/*`: stable production state only. No prerelease suffix is allowed.
- Short-lived development branches, including `Bella/*`, `codex/*`, `feature/*`,
  `fix/*`, `patch/*`, and `test/*`, must not carry stable manifest versions.

## Promotion Rules

1. Beta work starts on `senyo888-patch-1` as `MAJOR.MINOR.PATCH-beta.N`.
2. Each local Home Assistant validation build increments the beta number when the
   manifest changes.
3. Promotion to `develop` keeps a prerelease version: either the current beta or an
   `rc.N` once the release candidate is frozen.
4. Promotion to `main` or `release/*` removes the prerelease suffix and updates release
   notes to the stable version.
5. A GitHub release is created only from a stable version on `main` or `release/*`.

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
- The README has maintainer approval before release tagging.

If any gate is missing, the release state is `not ready`, even when the manifest version
already carries a stable number on `main` or `release/*`.

## Enforcement

`scripts/check_version_governance.py` validates the branch/version contract locally and
in CI. It rejects:

- stable versions on testing branches
- beta or release-candidate versions on `main` or `release/*`
- non-beta versions on `senyo888-patch-1`
- non-beta/non-rc versions on `develop`

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
