# Canonical Proposal Template

Use this template for new Humidity Intelligence proposals, handoffs, amendments, and
sandbox promotion requests. Keep the metadata block complete. Unknown fields should
be set explicitly to `false`, `none`, or `pending review`; do not leave blank authority
gaps.

This file is the single canonical proposal metadata template. `drafts.md` is the
active index; individual proposal artifacts must keep their metadata block aligned with
the index before review, staging, implementation, lab execution, or release promotion.

## Metadata

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

## Field Rules

- `proposal_id`: human ledger key for index tables, review packets, and handoffs.
  It must not encode category, target version, state, status, or authority.
- `proposal_urn`: immutable lineage key. Assign once, then preserve across title
  edits, file moves, state changes, reclassification, promotion, implementation, or
  release movement. Format: `urn:hi:proposal:YYYYMMDD:NNN:short-slug`.
- `title`: current human-readable proposal title. The title may be clarified without
  changing `proposal_urn`.
- `created`: original proposal creation date in ISO format.
- `category`: metadata only, such as `governance`, `runtime`, `ui`, `diagnostics`,
  `release`, `docs`, `ha-lab`, or `support`. It must not be embedded in the URN.
- `target_version`: intended planning or release track, such as `v2.1`, `v2.0.6`, or
  `none`. It is metadata only and must not be embedded in the URN.
- `authority_status`: records governance, implementation, and release authority
  separately from lifecycle state. Use explicit values such as `review-only`,
  `governance-only`, `implementation-authorized`, `implemented`,
  `release-candidate`, or `released`. It must not replace `state`.
- `category`, `target_version`, `state`, `status`, and `authority_status` remain
  metadata. They must not be embedded in `proposal_urn`.
- `state`: one of `IDEA`, `SANDBOX`, `REVIEW`, `TESTED`, `STAGED`,
  `PROMOTABLE`, or `RELEASED`.
- `owner`: proposal steward only. It does not grant approval authority. Valid owners
  include `Senyo`, `Bella`, `Aetherwing`, `Aetherbite`, `AetherCore`, or
  `pending review`.
- `risk_level`: `low`, `medium`, or `high`.
- `runtime_impact`: one of `none`, `docs-only`, `governance-only`, `ui-only`,
  `diagnostics-only`, `read-only-telemetry`, `service-contract`,
  `entity-contract`, or `runtime-control`.
- `affected_surfaces`: use explicit, limited values such as `proposal-governance`,
  `runtime-protection-contracts`, `ha-lab-evidence`, `diagnostics`,
  `generated-ui`, `services`, `entities`, `release-docs`, `public-docs`, or
  `runtime-control`.
- `rollback_defined`: `true` only when a concrete revert, cleanup, or containment
  path is documented. Anything moving to `STAGED`, `PROMOTABLE`, or `RELEASED`
  must define rollback.
- `expiry_or_review_date`: required ISO date. Expired drafts are stale by default.
- Approval and validation booleans mean evidence exists for that lane. Lab evidence
  remains evidence only; it is not release authority.
- Contract/risk booleans must be truthful. Any `true` value for
  `entity_contract_changed`, `service_contract_changed`, `lane_order_risk`, or
  `stable_runtime_risk` requires explicit runtime-protection review before
  promotion.

## Classification

- Pruning classification: keep | split | archive | supersede | reject
- Root ledger state: not promoted
- Implementation authorization: none
- Release authority: none

## Objective

State the smallest useful objective. Proposal text must not imply implementation,
runtime mutation, generated dashboard changes, release promotion, or Home Assistant
service calls unless those are explicitly approved.

## Boundary

List what is allowed, what is blocked, and what remains deferred. Include stable/lab
isolation when Home Assistant validation is involved.

## Runtime And UI Truth

State whether lane ordering, entity semantics, service contracts, diagnostics,
generated UI, release docs, or runtime control are affected. If any answer is yes,
link the relevant `.codex/runtime-protection/contracts/` file.

## Rollback

Define the rollback path before implementation, Home Assistant mutation, staging,
promotion, or release movement. If rollback is not defined, the proposal cannot move to
`STAGED`, `PROMOTABLE`, or `RELEASED`, and it cannot authorize runtime, service,
entity, generated-dashboard, or lab mutation. Evidence-only `REVIEW` or `TESTED`
records may keep `rollback_defined: false` only when they carry no mutation or release
authority.

## Validation

List the minimum validation required for the proposed scope. Lab reports are evidence
only; they are not release authority.
