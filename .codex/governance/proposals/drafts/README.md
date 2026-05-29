# Draft Proposal Artifacts

Use this folder for long-form draft proposal bodies that are too large for
`.codex/governance/proposals/drafts.md`.

Filename format:

```text
YYYY-MM-DD-short-title.md
```

Link every file from `drafts.md`. Drafts are not implementation truth until promoted
through the root `PROPOSALS.md` ledger.

Every active draft must carry the canonical metadata block from:

```text
.codex/governance/proposals/proposal_template.md
```

New draft artifacts should receive `proposal_id` and `proposal_urn` metadata when
they are created. Existing legacy artifacts are not batch-backfilled here; assign
ID/URN metadata to active v2.1 proposals only when they are next touched for real
review, reconciliation, implementation planning, or promotion.

`drafts.md` is the active index. It owns the proposal ID/URN registry fields,
pruning classification, current state, review/expiry date, and authority boundary for
each active draft.
