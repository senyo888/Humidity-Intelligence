# Bella Draft - Canonical Proposal URN and Lifecycle Tracking System

Date: 2026-05-29

## Metadata

```yaml
proposal_id: HI-PROP-20260529-001
proposal_urn: urn:hi:proposal:20260529:001:urn-lifecycle-tracking
title: Canonical Proposal URN and Lifecycle Tracking System
created: 2026-05-29
category: governance
target_version: v2.1
authority_status: review-only
state: REVIEW
owner: Senyo
risk_level: low
runtime_impact: governance-only
affected_surfaces:
  - proposal-governance
rollback_defined: false
expiry_or_review_date: 2026-06-28
bella_approved: true
aetherwing_validated: true
ha_lab_validated: false
release_candidate_validated: false
entity_contract_changed: false
service_contract_changed: false
lane_order_risk: false
stable_runtime_risk: false
```

Pruning classification: keep as governance metadata normalisation draft.

Status: Bella-approved review recommendations implemented locally by Aetherwing /
review-only / governance-only / not promoted to root `PROPOSALS.md`.

Owner: Senyo

Proposal steward: Bella

Target governance window: v2.1

Root ledger state: Not promoted to root `PROPOSALS.md`.

Aetherwing handoff:
`.codex/reports/handoffs/aetherwing_canonical_proposal_urn_tracking_implementation.md`.

## 1. Objective

Introduce a canonical proposal identifier and immutable proposal URN model for Humidity
Intelligence governance records so proposal lineage remains stable when titles,
classifications, files, owners, target versions, or lifecycle states change.

This proposal is a local governance-record normalisation only. It does not create
runtime behavior, Home Assistant interaction, generated dashboard behavior, public
release documentation, automation, registry services, or release authority.

## 2. Governance Position

Proposal records need two stable references:

- `proposal_id`: a human ledger key for indexes, review packets, handoffs, and
  maintainer discussion.
- `proposal_urn`: an immutable lineage key that survives title edits,
  reclassification, file movement, state transitions, implementation, and release
  movement.

The new fields are metadata. They do not change the proposal lifecycle model, root
promotion rules, release gates, runtime authority, or implementation authority.

Existing canonical state progression remains authoritative:

```text
IDEA -> SANDBOX -> REVIEW -> TESTED -> STAGED -> PROMOTABLE -> RELEASED
```

This proposal does not replace that progression with `idea`, `draft`, `approved`,
`implemented`, or any parallel lifecycle vocabulary.

## 3. Canonical Fields

New proposal artifacts should carry these fields before the existing metadata block:

```yaml
proposal_id: HI-PROP-YYYYMMDD-NNN
proposal_urn: urn:hi:proposal:YYYYMMDD:NNN:short-slug
title: Proposal Title
created: YYYY-MM-DD
category: governance
target_version: v2.x
authority_status: review-only
```

Field rules:

- `proposal_id` is the human ledger key. It must not encode category, target version,
  state, status, or authority.
- `proposal_urn` is the immutable lineage key. Assign it once, then preserve it
  across title edits, file moves, reclassification, state changes, implementation, and
  release movement.
- `title` is mutable display text. Clarifying the title must not change the URN.
- `created` is the original creation date, not the latest review or implementation
  date.
- `category` is metadata only.
- `target_version` is metadata only.
- `authority_status` records governance, implementation, and release authority
  separately from lifecycle `state`.

Category, target version, lifecycle state, status, and authority status must not be
embedded in the URN.

## 4. Authority Status

`authority_status` answers a different question from `state`.

`state` records lifecycle position. `authority_status` records what authority the
record currently carries.

Recommended values:

- `review-only`
- `governance-only`
- `implementation-authorized`
- `implemented`
- `release-candidate`
- `released`

These values do not override the root `PROPOSALS.md` promotion rules. A proposal can
be coherent, reviewed, or locally implemented as governance metadata and still carry
no runtime, Home Assistant, release, or root-promotion authority.

## 5. Phase 1B Boundary

Permitted in this implementation:

- update `.codex/governance/proposals/proposal_template.md`
- update `.codex/governance/proposals/drafts.md`
- create this long-form draft artifact
- update `.codex/governance/proposals/AGENTS.md`
- update `.codex/governance/proposals/drafts/README.md`
- update `.codex/governance/proposals/drafts/v2.1/phase-1/README.md`
- create an Aetherwing local handoff report

Blocked:

- no runtime integration files
- no Home Assistant interaction
- no generated UI or dashboard YAML
- no services, entities, diagnostics, manifests, README, CHANGELOG, tests, or release
  docs
- no root `PROPOSALS.md` promotion
- no root `AGENTS.md` edit
- no separate registry file
- no commit before Jules review

## 6. Registry Decision

No separate `PROPOSAL_REGISTRY.md` is created now.

`drafts.md` remains the active Phase 1B normalisation and index surface. The current
registry table in `drafts.md` carries the new fields for this proposal and explicitly
marks legacy rows as not backfilled.

If a future governance pass needs a dedicated registry, it should be proposed and
reviewed separately, with migration rules and root-ledger interaction defined before
implementation.

## 7. Adoption Policy

Adoption is prospective first.

New proposal artifacts should use `proposal_id`, `proposal_urn`, `title`, `created`,
`category`, `target_version`, and `authority_status` from creation.

Existing proposal records should not be batch-backfilled by this Phase 1B pass.
Optional backfill is allowed only for active v2.1 proposals when they are next touched
for real review, reconciliation, implementation planning, or promotion.

Historical, archived, rejected, superseded, or implemented records should not receive
new IDs just to make tables look complete.

## 8. Runtime And UI Truth

Runtime impact: none.

Generated UI impact: none.

Entity semantics: unchanged.

Service contracts: unchanged.

Lane ordering: unchanged.

Home Assistant validation: not required for this governance-only metadata pass.

Release impact: none. This draft creates no release authority and no public release
documentation.

## 9. Rollback

Rollback is direct file reversion:

- remove this long-form draft artifact
- remove the new draft-index row and registry row from `drafts.md`
- revert metadata-field additions in `proposal_template.md`
- revert proposal governance notes in `.codex/governance/proposals/AGENTS.md`
- revert draft-artifact README guidance additions
- revert v2.1 phase README metadata additions
- remove the Aetherwing handoff report

No Home Assistant cleanup, migration, restart, entity cleanup, service cleanup,
dashboard cleanup, or release cleanup is required.

## 10. Validation

Minimum validation for this local governance-only implementation:

```sh
git diff --check -- .codex/governance/proposals .codex/reports/handoffs
rg -n "HI-PROP-20260529-001|urn:hi:proposal:20260529:001:urn-lifecycle-tracking" .codex/governance/proposals .codex/reports/handoffs
rg -n "proposal_id|proposal_urn|authority_status" .codex/governance/proposals/proposal_template.md .codex/governance/proposals/drafts.md .codex/governance/proposals/AGENTS.md .codex/governance/proposals/drafts/v2.1/phase-1/README.md
```

Do not claim runtime, Home Assistant, generated-dashboard, release-candidate, or public
documentation validation for this proposal.
