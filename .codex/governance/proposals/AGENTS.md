# Proposal Governance Agent Notes

## Root Ledger Rule

When initiating a proposal, do not write directly into root `PROPOSALS.md` unless promotion is explicitly justified.

Start concise new proposal material in:

```text
.codex/governance/proposals/drafts.md
```

For long-form proposal bodies, create a dated file under:

```text
.codex/governance/proposals/drafts/
```

Then link it from `drafts.md`. The flat `.md` files remain the current ledgers for
stage summaries and migrated history; the stage folders are future artifact buckets,
not competing sources of truth.

Then classify it as one of:

- Draft
- Pending Analysis
- Needs Review
- Rejected
- Archived
- Watch
- Ready for Promotion

Only update root `PROPOSALS.md` when Bella explicitly recommends promotion and the proposal meets the governance update rules.

Root `PROPOSALS.md` remains the canonical proposal ledger. Governance proposal files are internal staging, review, history, and classification files.

## Canonical Proposal Metadata Rule

Every active proposal, v2.1 proposal, report handoff, or sandbox promotion request
must include a metadata block before it can move beyond draft review.

Use `.codex/governance/proposals/proposal_template.md` as the single canonical
template. Keep `drafts.md` and the long-form proposal artifact aligned.

```yaml
proposal_id: HI-PROP-YYYYMMDD-NNN
proposal_urn: urn:hi:proposal:YYYYMMDD:NNN:short-slug
title: Proposal Title
created: YYYY-MM-DD
category: governance
target_version: v2.x
authority_status: review-only
state: IDEA
owner: pending review
risk_level: low
runtime_impact: governance-only
affected_surfaces:
  - proposal-governance
rollback_defined: false
expiry_or_review_date: 2026-MM-DD
bella_approved: false
aetherwing_validated: false
ha_lab_validated: false
release_candidate_validated: false
entity_contract_changed: false
service_contract_changed: false
lane_order_risk: false
stable_runtime_risk: false
```

ID and authority rules:

- `proposal_id` is the human ledger key used in indexes, review packets, and
  handoffs. Do not encode category, target version, state, status, or authority in it.
- `proposal_urn` is the immutable lineage key. Assign it once and preserve it across
  title edits, file moves, state changes, reclassification, root promotion,
  implementation, or release movement.
- `category`, `target_version`, `state`, `status`, and `authority_status` are
  metadata. They must not be embedded in the URN.
- `authority_status` records whether a proposal is review-only, governance-only,
  implementation-authorized, implemented, release-candidate, or released. It is not a
  replacement for lifecycle `state`, and it does not override the root
  `PROPOSALS.md` promotion rules above.
- Existing drafts without ID/URN metadata are legacy records. Assign the new fields
  prospectively first, and backfill only active v2.1 proposals when they are next
  touched.

Valid state progression:

```text
IDEA -> SANDBOX -> REVIEW -> TESTED -> STAGED -> PROMOTABLE -> RELEASED
```

State meanings:

- `IDEA`: described but not built.
- `SANDBOX`: explored under `sandbox/v2.1/` with safe or hazardous classification.
- `REVIEW`: proposal or handoff exists and is ready for Bella/Aetherwing review.
- `TESTED`: direct checks, relevant fixtures, and runtime-protection snapshot evidence
  exist.
- `STAGED`: integrated into an approved staging branch with rollback defined.
- `PROMOTABLE`: frozen release-candidate evidence is complete and blockers are closed.
- `RELEASED`: merged, tagged, documented, validated, and approved by the maintainer.

Runtime-impact values should be one of:

```text
none
docs-only
governance-only
ui-only
diagnostics-only
read-only-telemetry
service-contract
entity-contract
runtime-control
```

Affected surfaces should be explicit and limited. Use values such as:

```text
proposal-governance
runtime-protection-contracts
ha-lab-evidence
diagnostics
generated-ui
services
entities
release-docs
public-docs
runtime-control
```

Every active draft must also be classified in `drafts.md` as one of:

- `keep`
- `split`
- `archive`
- `supersede`
- `reject`

Drafts without `expiry_or_review_date` are stale by default and must not be treated
as implementation authority. Expired drafts move to review before they can influence
implementation, runtime validation, release wording, generated UI, service/entity
contracts, or lab work.

Any `service-contract`, `entity-contract`, or `runtime-control` proposal must reference
the affected files under `.codex/runtime-protection/contracts/` and must not advance to
`PROMOTABLE` without Aetherwing drift-audit evidence and explicit maintainer approval.

## Bella Memory Rule

Bella governance memory is read from:

```text
.codex/memories/pets/Bella/memory.md
```

Do not store Bella memory under `.codex/pets_pointer/` or `.codex/pets/`. The current
local identity pointer path is `.codex/pets_pointer/`; `.codex/pets/` is historical or
possible app identity space only.
