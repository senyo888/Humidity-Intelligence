# Stable Runtime Boundary

Status: boundary document only. This is not a target profile, not a selectable configuration, and not a command input.

## Rule

The HA Lab Runtime protects the stable household Home Assistant runtime by staying isolated, explicit, and fail-closed. Stable Home Assistant must never be reachable through lab defaults, lab credentials, lab reports, scenario manifests, or future lab tooling.

## Stable Is Not A Lab Target

- Do not create a stable target profile.
- Do not create a production target profile.
- Do not create default, home, live, main, or generic target profiles.
- Do not place this boundary under a machine-readable `profiles/` folder.
- Do not store stable credentials in lab credential files.
- Do not allow a future lab command to fall back to stable Home Assistant.
- Do not mirror production telemetry in this first slice.
- Do not implement shadow mode in this first slice.

## Lab-Only Credential Rule

The approved first lab credential location is:

```text
.codex/private/ha_lab_runtime.env
```

Allowed names for the HA Lab Runtime:

```bash
HI_LAB_HA_BASE_URL=
HI_LAB_HA_TOKEN=
HI_LAB_INSTANCE_LABEL=humidity-intelligence-lab
```

Forbidden names for the HA Lab Runtime:

```bash
HA_URL
HA_TOKEN
HOME_ASSISTANT_TOKEN
PROD_HA_TOKEN
STABLE_HA_TOKEN
```

## Fail-Closed Requirements

Any future HA-targeting command must stop before execution if it cannot prove:

- instance label
- HA base URL
- token fingerprint only
- source branch
- source commit
- manifest version
- intended operation
- read-only or mutating classification

No target identity means no execution.

## Manual Copy Rule

Manual copies into Home Assistant `custom_components` are contaminated as source evidence unless reconciled to the repository or a named worktree. A lab observation from an unreconciled manual copy can identify a problem, but it cannot define source truth or release readiness.

## Mutation Rule

No mutating action belongs in this first slice. That includes Home Assistant write services, helper mutation, MQTT publishing, dashboard creation, restart, reload, deployment automation, install automation, scenario execution, real-device integration, production telemetry mirroring, and release-gate enforcement.

## Release Truth Rule

Lab evidence can support review. It cannot promote a proposal, redefine runtime semantics, replace Bella/Aetherwing/AetherCore review, replace repository validation, or approve a release.

Operational Beta Validation Infrastructure does not change this rule. HA Lab beta
deploy, activation, soak, Stage 3, generated-card, or entity-map evidence remains
advisory and isolated from stable Home Assistant unless a separate exact stable-runtime
inspection packet is approved.
