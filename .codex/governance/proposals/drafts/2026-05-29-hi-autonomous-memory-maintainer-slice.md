# Autonomous Memory Maintainer Completion Slice

Parent proposal: `HI-PROP-20260529-002`
Parent URN: `urn:hi:proposal:20260529:002:agent-memory-usage-auditor`

## Status

This is not a standalone proposal. It is a completion slice of the Bella Draft - HI
Agent Memory Usage Auditor and Candidate Update Report.

Authority status: implemented under the parent proposal, with Bella
post-implementation review and maintainer approval recorded before final checkout
commitment.

## Purpose

Keep the autonomous memory maintainer inside the same proposal until completion. The
maintainer exists to turn approved candidate memory updates into deterministic,
auditable memory maintenance without allowing hidden writes, stale authority, or private
data leakage.

## Operating Modes

### Report Only

Default mode. The maintainer inspects approved local evidence surfaces and writes a
report. It does not edit `.codex/memories/`.

### Candidate Manifest

The maintainer emits candidate memory entries with target file, exact candidate text,
evidence, privacy check, stale-authority check, and status.

Allowed statuses in generated output:

- `pending-review`
- `rejected`
- `parked`

The maintainer must not mark a candidate `accepted-by-maintainer` unless the exact text
and target file were already approved by Jules or by a separately approved Bella review.

### Apply Approved

Gated mode. This mode may exist as part of the completion design, but it must be
fail-closed.

Requirements:

- accepts only an explicit approved manifest;
- applies only exact approved candidate text to exact approved target files;
- rejects candidate text that changed after approval;
- rejects target files outside `.codex/memories/`;
- refuses secrets, private entity IDs, tokens, credentials, private telemetry,
  usernames, machine-specific paths, private MCP configuration, and unrestricted session
  excerpts;
- writes an application report showing every accepted, rejected, and skipped entry;
- remains disabled by default;
- is not wired to any recurring automation before Bella review and maintainer approval.

## Evidence Sources

Allowed by default:

- current repository source files;
- `DESIGN_BRIEF.md`, `AGENTS.md`, `AGENTS.local.md`, root `PROPOSALS.md`, and local
  proposal governance files;
- `.codex/memories/project/*.md` and `.codex/memories/pets/*/memory.md` for memory
  truth checks;
- local reports under `.codex/reports/`;
- approved automation run notes under `$CODEX_HOME/automations/*/memory.md`
  when the path is explicitly named in the parent proposal or current operation packet.

Blocked by default:

- unrestricted private session logs;
- Home Assistant API calls;
- GitHub mutation;
- recurring automation creation or update;
- raw secrets or local environment files;
- unreviewed runtime telemetry.

## Authority Rules

- `DESIGN_BRIEF.md` remains the implementation contract.
- Current repo files outrank memory.
- Root `PROPOSALS.md` outranks draft records for promoted proposal state.
- Draft records and local reports are evidence, not release authority.
- Memory supports continuity only and must not become shadow runtime, UI, release, or
  proposal authority.

## Aetherwing Implementation Requirements

Aetherwing may implement this slice as:

- a section in `scripts/local/hi_memory_usage_auditor.py`; or
- a separate local helper such as `scripts/local/hi_autonomous_memory_maintainer.py`;
  or
- a documented manual control file if Aetherwing determines code would create more risk
  than value in the first pass.

Whichever path is chosen, Aetherwing must record:

- operating modes implemented;
- unsupported modes;
- privacy rejection rules;
- stale-authority rejection rules;
- proof that `.codex/memories/` was not changed during dry-run validation;
- proof that root `PROPOSALS.md` was not changed;
- proof that no recurring automation was created or updated.

## Bella Review Requirements

Bella must review the implemented slice for:

- hidden write paths;
- vague approval semantics;
- memory authority drift;
- private data leakage;
- stale memory promotion risk;
- uncontrolled automation hooks;
- mismatch between generated candidate entries and accepted evidence.

If Bella rejects the implementation, the packet returns to Aetherwing for correction.
If Bella accepts the implementation, the work still pauses for Jules before staging,
commit, push, final checkout commitment, memory mutation, or recurring automation.

## Completion Criteria

This slice is complete only when:

- Aetherwing has implemented or explicitly justified the local maintainer shape;
- report-only mode works or has an exact documented substitute;
- candidate manifest output is deterministic and review-only by default;
- apply-approved mode is either safely implemented as disabled-by-default or explicitly
  parked with clear future requirements;
- Bella has completed post-implementation review;
- Jules has reviewed the final local state.

Completion of this slice does not by itself authorize memory mutation, automation
activation, root proposal promotion, release movement, runtime changes, or final
checkout commitment.
