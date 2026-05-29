# V2.1 Phase 1 Draft Proposals

Use this folder for v2.1 Phase 1 draft proposals before promotion.

Template metadata for new artifacts only. This README is not an active draft record:

```yaml
proposal_id: HI-PROP-YYYYMMDD-NNN
proposal_urn: urn:hi:proposal:YYYYMMDD:NNN:short-slug
title: Proposal Title
created: YYYY-MM-DD
category: governance
target_version: v2.1
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

Valid state progression:

```text
IDEA -> SANDBOX -> REVIEW -> TESTED -> STAGED -> PROMOTABLE -> RELEASED
```

Drafts must not imply implementation approval, runtime authorization, or release
commitment.

`proposal_id` is the human ledger key. `proposal_urn` is the immutable lineage key.
Category, target version, state, status, and `authority_status` remain metadata and
must not be embedded in the URN. Existing canonical state progression remains
authoritative; `authority_status` records governance, implementation, and release
authority separately from state.

Each active draft must also be classified in `.codex/governance/proposals/drafts.md`
as `keep`, `split`, `archive`, `supersede`, or `reject`. Expired drafts are stale by
default and require review before they can influence implementation, runtime
validation, release wording, generated UI, service/entity contracts, or lab work.
