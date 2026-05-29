# Aetherwing Handoff - Canonical Proposal URN Tracking Implementation

Date: 2026-05-29

Status: Local governance implementation applied, validated, and committed on
`senyo888-patch-1` as governance-only records.

Source proposal:

```text
.codex/governance/proposals/drafts/2026-05-29-canonical-proposal-urn-and-lifecycle-tracking.md
```

## Objective

Implement Bella's approved review recommendations for the Canonical Proposal URN and
Lifecycle Tracking System as local governance records only.

## Scope

Implemented:

- added canonical `proposal_id`, `proposal_urn`, `title`, `created`, `category`,
  `target_version`, and `authority_status` fields to the proposal metadata template
- preserved the existing canonical state progression:
  `IDEA -> SANDBOX -> REVIEW -> TESTED -> STAGED -> PROMOTABLE -> RELEASED`
- updated `drafts.md` as the active Phase 1B normalisation and index surface
- added the new proposal row, registry entry, and concise detail record
- created the long-form proposal artifact
- updated proposal-governance agent notes with ID/URN and authority rules
- updated draft-artifact README guidance for prospective ID/URN adoption
- mirrored the metadata fields in the v2.1 Phase 1 draft README

Not implemented:

- no runtime integration files
- no Home Assistant interaction
- no generated UI or dashboard YAML
- no public release docs
- no README, CHANGELOG, manifest, HACS metadata, services, entities, diagnostics, or
  tests
- no root `AGENTS.md` edit
- no root `PROPOSALS.md` promotion
- no separate `PROPOSAL_REGISTRY.md`
- no release authority or root-ledger promotion

## Files Changed

- `.codex/governance/proposals/proposal_template.md`
- `.codex/governance/proposals/drafts.md`
- `.codex/governance/proposals/drafts/2026-05-29-canonical-proposal-urn-and-lifecycle-tracking.md`
- `.codex/governance/proposals/AGENTS.md`
- `.codex/governance/proposals/drafts/README.md`
- `.codex/governance/proposals/drafts/v2.1/phase-1/README.md`
- `.codex/reports/handoffs/aetherwing_canonical_proposal_urn_tracking_implementation.md`

## Runtime Impact

None.

No lane ordering, output writes, alert behavior, telemetry processing, entity
semantics, service contracts, diagnostics behavior, generated dashboard behavior, or
Home Assistant runtime behavior changed.

## UI Impact

None.

No generated cards, Lovelace YAML, dashboard exports, frontend dependency behavior, or
UI truth surfaces changed.

## Migration Or Restart Impact

None.

No migration, Home Assistant restart, reload, dashboard refresh, service reload, or
HACS action is required.

## Validation Performed

Local governance validation:

```sh
git diff --check HEAD~1..HEAD -- .codex/governance/proposals .codex/reports/handoffs
rg -n "HI-PROP-20260529-001|urn:hi:proposal:20260529:001:urn-lifecycle-tracking" .codex/governance/proposals .codex/reports/handoffs
rg -n "proposal_id|proposal_urn|authority_status" .codex/governance/proposals/proposal_template.md .codex/governance/proposals/drafts.md .codex/governance/proposals/AGENTS.md .codex/governance/proposals/drafts/v2.1/phase-1/README.md
```

Home Assistant validation is not expected for this governance-only change.

## Rollback Path

Rollback is direct file reversion:

- remove the new long-form draft artifact
- remove this handoff report
- revert the metadata additions in `proposal_template.md`
- remove the new draft/index/detail records from `drafts.md`
- revert the proposal-governance agent note additions
- revert the draft-artifact README guidance additions
- revert the v2.1 phase README metadata additions

No Home Assistant cleanup, restart, migration, generated-dashboard cleanup, service
cleanup, entity cleanup, or release cleanup is required.
