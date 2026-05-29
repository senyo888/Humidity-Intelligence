# Bella Draft - HI Agent Memory Usage Auditor and Candidate Update Report

## Metadata

```yaml
proposal_id: HI-PROP-20260529-002
proposal_urn: urn:hi:proposal:20260529:002:agent-memory-usage-auditor
title: HI Agent Memory Usage Auditor and Candidate Update Report
created: 2026-05-29
category: governance
target_version: none
authority_status: implementation-authorized
state: TESTED
owner: Bella
risk_level: medium
runtime_impact: governance-only
affected_surfaces:
  - proposal-governance
  - validation-tooling
rollback_defined: true
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

## Classification

- Pruning classification: keep
- Root ledger state: not promoted
- Implementation status: Aetherwing local implementation complete; Bella
  post-implementation review passed
- Release authority: none
- Final checkout commitment: blocked until Bella post-implementation review and
  maintainer review

## Objective

Create a small local governance auditor that reports whether recent Humidity
Intelligence agent work used the expected memory surfaces, then proposes concise
candidate memory updates for review. Keep the autonomous memory maintainer as a
completion slice inside this proposal so the full memory-governance path is designed,
implemented, reviewed by Bella, and then paused for maintainer approval.

The Aetherwing implementation must be fail-closed. Candidate memory lines are advisory
until Jules or a separately approved Bella review explicitly accepts the exact text and
target file. Any autonomous apply mode must require an exact approved manifest and must
not silently mutate memory.

Implementation outcome: Aetherwing implemented the local auditor in
`scripts/local/hi_memory_usage_auditor.py`, added regression coverage in
`tests 2/test_hi_memory_usage_auditor.py`, generated the first audit report, and
recorded a handoff. Bella post-implementation review passed with the caveat that any
future memory apply remains exact approved-manifest-only.

Approved completion outcome: Jules approved memory mutation, automation activation,
staging, commit, push, and final checkout commitment after review. The accepted
candidate was applied to `.codex/memories/project/release_lessons.md` through
`.codex/reports/audits/hi_memory_usage_approved_manifest_2026-05-29.json`, producing
`.codex/reports/audits/hi_memory_usage_apply_2026-05-29.json`. The report-only
automation was activated as `hi-memory-usage-auditor`.

## Reason

Humidity Intelligence now has repository-local memory under `.codex/memories/`, but
that only helps if agents consistently consult it and keep it lean. The current risk is
two-sided:

- useful project lessons may be rediscovered repeatedly instead of reused;
- stale, private, or speculative notes could become shadow authority if memory updates
  are written automatically.

The correct implementation path is phased: first a memory-usage auditor and candidate
update report, then a controlled autonomous maintainer slice that can prepare and, only
under explicit gates, apply approved memory updates.

## Boundary

Allowed in the first implementation:

- add a local, read-only auditor or equivalent report generator;
- add an autonomous memory maintainer completion-slice file under this proposal;
- generate or refresh a local report under `.codex/reports/audits/`;
- inspect current repo governance files, proposal records, local reports, and approved
  automation run notes;
- identify candidate memory updates with evidence, target file, privacy check, stale
  authority check, and reviewer status;
- document Aetherwing caveats and Bella review outcomes inside the local report or
  handoff packet.

Blocked:

- no runtime code changes;
- no Home Assistant service calls, reloads, entity mutations, or API writes;
- no generated UI, dashboard, diagnostics-semantics, service, entity, manifest, HACS,
  release-note, or changelog changes;
- no ungated edits to `.codex/memories/`;
- no automatic memory writer that can apply unapproved text;
- no recurring automation creation or update before Bella review and maintainer
  approval;
- no root `PROPOSALS.md` promotion;
- no unrestricted scan of private session logs by default;
- no staging, committing, pushing, or final checkout commitment before Jules reviews the
  implemented local slice.

Included completion slice:

- autonomous memory maintainer operating rules;
- approved-manifest-only memory update path;
- dry-run/report-only default mode;
- explicit privacy and stale-authority rejection rules;
- Bella post-implementation review before the slice is considered complete.

Still blocked until later explicit approval:

- recurring automation activation;
- ungated direct memory mutation;
- public documentation about local/private memory behaviour.

## Source Hierarchy

The auditor must enforce this authority order:

1. `DESIGN_BRIEF.md`
2. current repository files and runtime truth
3. root `PROPOSALS.md` for promoted proposal state
4. `.codex/governance/proposals/drafts.md` and long-form local proposal records
5. `.codex/memories/` as continuity support only
6. automation memories and local reports as evidence, not authority

If memory and current repo truth disagree, the report must flag the conflict and refuse
to recommend copying the stale memory forward.

## Safe Evidence That Memory Was Used

Acceptable evidence:

- a session/report explicitly lists the memory files read;
- a final review or handoff cites a memory-derived rule and then verifies it against
  current repo files;
- a local report names the exact memory surfaces consulted and the decision they
  influenced;
- an approved automation run note records a continuity rule that was followed.

Weak or insufficient evidence:

- output merely matches existing memory wording;
- an agent follows the right rule but provides no evidence that memory was consulted;
- a session mentions memory generally without naming the relevant file or rule;
- a report relies on private, unredacted, or unrestricted logs.

## Safe Evidence That Memory Should Be Updated

A candidate update may be proposed only when all of these are true:

- the lesson is durable and likely to recur;
- the same pattern, script, command, caveat, or routing rule was useful in more than one
  relevant project context, or one high-risk context exposed a clear future hazard;
- current source files or accepted local reports support the claim;
- the proposed text is concise and belongs in memory rather than roadmap, proposal,
  release notes, docs, or a script comment;
- the candidate does not include private entity IDs, secrets, tokens, credentials,
  addresses, usernames, private telemetry, machine-specific paths, or local MCP details;
- the candidate cannot override `DESIGN_BRIEF.md`, runtime truth, release status,
  privacy rules, or proposal promotion rules.

## Candidate Update Format

Each candidate memory update must use this structure in the audit report:

```text
target_file:
candidate_text:
why_it_matters:
evidence:
current_repo_truth_check:
privacy_check:
stale_authority_check:
recommended_reviewer:
status: pending-review
```

`status` may be `pending-review`, `accepted-by-maintainer`, `rejected`, or `parked`.
The first implementation must emit only `pending-review`, `rejected`, or `parked`.
It must not mark anything accepted unless Jules has already approved the exact text.

The autonomous maintainer may only apply entries marked `accepted-by-maintainer` in an
approved manifest. It must refuse free-form generated writes, partial approvals, and
candidate text that has changed after approval.

## Aetherwing Review And Implementation Packet

Aetherwing should execute this sequence:

1. Review this proposal against `DESIGN_BRIEF.md`, `AGENTS.md`, `AGENTS.local.md`,
   `.codex/memories/project/canon.md`, `.codex/memories/project/architecture.md`,
   and the current proposal-governance rules.
2. Identify caveats before implementation and address in-scope caveats inside the
   implementation packet.
3. Implement a minimal local report generator, preferably under `scripts/local/`, using
   only the Python standard library or existing local shell patterns.
4. Implement or update the autonomous memory maintainer completion-slice file listed
   below.
5. Generate the first local report under `.codex/reports/audits/`.
6. Validate that `.codex/memories/`, root `PROPOSALS.md`, runtime files, generated UI,
   Home Assistant state, automations, and release metadata were not changed.
7. Return the implemented packet to Bella for post-implementation review.
8. Stop and leave the working tree for Jules to review before staging, committing,
   pushing, or syncing as final checkout state.

Suggested implementation file:

- `scripts/local/hi_memory_usage_auditor.py`

Suggested report path:

- `.codex/reports/audits/hi_memory_usage_audit.md`

Autonomous maintainer completion-slice artifact:

- `.codex/governance/proposals/drafts/2026-05-29-hi-autonomous-memory-maintainer-slice.md`

Suggested future maintainer implementation file, if Aetherwing decides a separate script
is cleaner than extending the auditor:

- `scripts/local/hi_autonomous_memory_maintainer.py`

Optional handoff path if caveats are found:

- `.codex/reports/handoffs/aetherwing_hi_memory_usage_auditor_caveats.md`

## Caveat Handling

In-scope caveats include:

- narrowing the evidence allow-list;
- making the report format stricter;
- adding a stronger privacy rejection rule;
- changing the script name or report path to fit existing local patterns;
- adding validation that proves memory files were not edited.
- splitting the autonomous maintainer into a dry-run/default mode and a gated
  apply-approved mode.

Out-of-scope caveats include:

- ungated automatic writes to `.codex/memories/`;
- adding or updating recurring automations before Bella review and maintainer approval;
- scanning unrestricted private session history;
- changing runtime behaviour;
- changing generated dashboard output;
- altering entity, service, diagnostics, manifest, HACS, or release contracts;
- promoting this draft to root `PROPOSALS.md`;
- treating memory as authority over current repo truth.

Out-of-scope caveats must be documented for Bella review and must not be implemented as
active behaviour.

## Runtime And UI Truth

No runtime, UI, diagnostics, entity, service, lane ordering, generated dashboard, Home
Assistant, HACS, or release behaviour is changed by this proposal.

The auditor is a local governance and validation helper only. It must never be imported
by the integration, called by Home Assistant, exposed as a Home Assistant service, or
used as a generated-dashboard data source.

## Privacy Rules

The auditor must reject candidate memory text containing:

- secrets, tokens, credentials, bearer headers, API keys, or local environment values;
- private entity IDs, device IDs, addresses, usernames, or private telemetry values;
- machine-specific absolute paths;
- private MCP configuration;
- unrestricted session excerpts;
- unreviewed Home Assistant runtime data.

Evidence may reference sanitized local file categories, but candidate memory text must
be portable and public-safe unless Jules separately approves a private local memory
exception.

## Acceptance Criteria

- Aetherwing implementation records the review/caveat handling performed before and
  during implementation.
- A local report generator exists or an explicitly documented reason explains why a
  script was rejected in favour of a manual report.
- The autonomous memory maintainer completion-slice file exists and remains tied to
  this proposal.
- The first report is generated under `.codex/reports/audits/`.
- The report contains memory-used evidence, candidate memory updates, rejected/parked
  candidates, privacy checks, stale-authority checks, and next-review recommendations.
- Candidate memory lines remain review-only unless an approved manifest explicitly
  authorizes exact application.
- Any autonomous maintainer apply path is dry-run by default and approved-manifest-only.
- Root `PROPOSALS.md` is unchanged.
- No recurring automation is created or updated before Bella review and maintainer
  approval.
- No runtime, generated UI, entity, service, diagnostics, manifest, HACS, release, or
  Home Assistant state changes occur.
- Validation proves memory files were not mutated.
- Bella post-implementation review is required after Aetherwing implementation.
- Aetherwing/Bella stop after implementation, validation, and Bella review, leaving the
  result for Jules' review before final checkout commitment.

## Validation

Minimum validation for the first implementation:

```bash
python3 -m py_compile scripts/local/hi_memory_usage_auditor.py
python3 scripts/local/hi_memory_usage_auditor.py --dry-run --output .codex/reports/audits/hi_memory_usage_audit.md
test -f .codex/governance/proposals/drafts/2026-05-29-hi-autonomous-memory-maintainer-slice.md
git diff --check
git diff -- .codex/memories/
git diff -- PROPOSALS.md
```

If no Python script is implemented, Aetherwing must replace the first two checks with
the exact manual report-generation command or checklist used.

Runtime tests are not required for the first implementation because this is
governance-only local tooling. If any runtime, service, entity, generated UI,
diagnostics, release, or Home Assistant surface changes unexpectedly, the implementation
must stop and return to Bella.

## Rollback

Rollback is local and direct:

- remove the new local auditor script and any autonomous maintainer script;
- remove the generated audit report and any caveat handoff;
- remove the autonomous memory maintainer completion-slice file;
- remove this draft's rows from `.codex/governance/proposals/drafts.md`;
- remove this long-form draft;
- verify `.codex/memories/`, root `PROPOSALS.md`, runtime files, generated UI files,
  release metadata, automations, and Home Assistant state were not changed.

If any memory file was changed during implementation, Aetherwing must stop, report the
exact diff, and request maintainer approval before attempting cleanup.

## Stop State

After Aetherwing implementation and Bella post-implementation review, the work must
pause. The intended final state before Jules' review is:

- local files changed;
- validation run and reported;
- autonomous memory maintainer slice included in this proposal;
- no memory files mutated;
- no automations created or updated;
- no root proposal promotion;
- no staging;
- no commit;
- no push;
- no final checkout commitment.
