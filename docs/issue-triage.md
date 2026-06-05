# Report-Only Issue Triage

Humidity Intelligence includes a report-only Codex workspace helper for GitHub issue
triage.

The helper fetches open GitHub issues, identifies new, untriaged, or recently updated
items, and writes a structured Markdown report for Bella, Aetherwing, Aetherbite, or
the human maintainer to review.

It does not close, edit, label, assign, or comment on GitHub issues.
It also treats Community Ideas & Proposals issues as intake signals only: interest and
comments can inform visibility, but they do not grant implementation, runtime, release,
or Home Assistant authority.

## Manual Run

From the repository root:

```bash
GITHUB_REPOSITORY=senyo888/humidity-intelligence python3 scripts/issue_triage.py --dry-run
```

Default output:

```text
.codex/reports/issue_triage/daily_issue_triage.md
```

`.codex/` is local workspace output. Keep generated triage reports ignored/local unless
the maintainer explicitly asks to publish a sanitized summary.

Generated triage reports are timestamped support snapshots. They do not override the
current release state recorded in `CHANGELOG.md`, `ROADMAP.md`, or
`docs/release-governance.md`.

## Authentication

The script works without `GITHUB_TOKEN` for public, low-volume checks. Unauthenticated
GitHub API runs are rate limited, so scheduled workspace use should set a token through
the environment when available:

```bash
# With GITHUB_TOKEN already set in the environment:
GITHUB_REPOSITORY=senyo888/humidity-intelligence python3 scripts/issue_triage.py --dry-run
```

Never write tokens into docs, reports, shell history exports, cron logs, or issue text.

## Useful Options

```bash
# Include all fetched open issues instead of only new/recent/untriaged candidates.
python3 scripts/issue_triage.py --include-all-open

# Widen the recent-update window.
python3 scripts/issue_triage.py --lookback-days 7

# Write to a custom local report path.
python3 scripts/issue_triage.py --output .codex/reports/issue_triage/weekly_issue_triage.md

# Test report rendering from a saved GitHub issues JSON fixture.
python3 scripts/issue_triage.py --input-json /path/to/issues.json
```

## Safe Optional Scheduling

Use a read-only workspace schedule only if it matches maintainer capacity. For
community ideas, weekly or maintainer-capacity triage is safer than promising daily
attention. The scheduled command should run from the repository root and should only
write local `.codex/reports/` output.

Weekly cron-style example:

```cron
0 8 * * 1 cd <repo> && GITHUB_REPOSITORY=senyo888/humidity-intelligence python3 scripts/issue_triage.py --dry-run >> .codex/reports/issue_triage/issue_triage.log 2>&1
```

Codex workspace automation wording:

```text
Every Monday at 08:00, run from the Humidity Intelligence repository root:
GITHUB_REPOSITORY=senyo888/humidity-intelligence python3 scripts/issue_triage.py --dry-run

Keep the task read-only/report-only. Do not close, edit, label, assign, or comment on
GitHub issues.
```

## Triage Mapping

Suggested owner mapping:

- Bella: architecture, roadmap, governance, proposals, community ideas/proposals intake, coherence, documentation truth
- Aetherwing: runtime safety, regression protection, release validation, deterministic lane logic, issue fixes
- Aetherbite: UI ideas, visual polish, brainstorms, experimental UX proposals
- Human maintainer/Senyo: unclear reports, repo policy decisions, community-facing replies, release approval

Priority mapping:

- P0: safety, CO/emergency logic, data loss, broken install, HACS-breaking, release-blocking
- P1: runtime correctness, false UI state, broken config flow, broken services, major docs mismatch
- P2: normal bug, UX issue, dependency detection issue, confusing behaviour
- P3: enhancement, polish, wording, future idea
- Watch: unclear, needs reproduction, potentially duplicate, not enough detail

## Diagnostics Bundle Signal

Bug and configuration-help issues now ask users to attach the downloaded Home Assistant
diagnostics file for Humidity Intelligence:

```text
Settings -> Devices & services -> Humidity Intelligence -> Download diagnostics
```

The triage script detects issue bodies that mention or link the native Home Assistant
diagnostics download and suggests `has-diagnostics`. Bug, runtime, UI, or support
issues without an attached or mentioned native diagnostics file are suggested for
`needs-bundle`.

The existing `humidity_intelligence.dump_diagnostics` JSON export remains a local
maintainer/debug tool. It should not be counted as the safe GitHub issue attachment
path unless a maintainer explicitly asks for it.

These are manual label recommendations only. The script does not create labels, apply
labels, comment, close, assign, or upload anything.

Suggested maintainer flow:

1. Triage safety/release blockers first.
2. Prioritise `has-diagnostics` issues next because they are faster to inspect.
3. For `needs-bundle` issues, ask the reporter to attach the downloaded Home Assistant diagnostics file when practical.
4. Route `community-proposal` issues through maintainer/Bella review before any implementation planning. Convert a community idea into a formal HI proposal only if warranted.
5. Inspect diagnostics locally before deep investigation; the file should include versions, selected entities, runtime lane/reason, gates, outputs, frontend dependency status, generated UI summary, and redacted diagnostics.

## Implemented Issue Template Triage Fields

The GitHub issue templates include maintainer-friendly triage fields so the report has
better signals without needing a bot to edit public issues.

Bug reports, configuration help, and feature requests include a shared `Affected area`
dropdown:

- Runtime/control
- Config flow/options
- Generated UI/dashboard
- Services/diagnostics
- Documentation
- HACS/install
- Governance/release
- Unsure

Bug reports and configuration help include shared `Triage signals` checkboxes:

- Safety, CO, or emergency behaviour may be affected.
- This may block a release or HACS install.
- This looks like a regression from a previous HI version.
- This may be a duplicate of another issue.
- I think this needs maintainer/community reply rather than code.
- I think this needs proposal review before implementation.

Bug reports include a `Checks already tried` field for commands or services already
run, such as downloading diagnostics, `refresh_ui`, `self_check`,
`v205_release_check`, `dump_diagnostics`, or a Home Assistant restart.

Bug reports and configuration help include an optional diagnostics attachment field.
Version/setup fallback fields remain available for users who cannot download
diagnostics.

Feature requests include a required `Proposal scope` dropdown:

- Small bugfix-sized change
- UI polish
- Runtime semantics
- Release/governance
- v2.1 or later exploration
- Unsure

Community Ideas & Proposals issues include user-friendly intake fields:

- problem being solved
- requested improvement
- kind of idea
- affected area
- affected rooms, devices, integrations, or dashboards
- behavior HI should avoid
- practical benefit
- similar issues or proposals
- optional screenshots, examples, diagnostics, or workaround

Community idea labels are advisory workflow signals. They do not make the idea
accepted, scheduled, or implementation-ready. Submitting an idea does not guarantee
implementation, release scheduling, or acceptance.

Expected public lifecycle wording:

- Submitted
- Needs Info
- Triaged
- Accepted for Review
- Proposal Drafted
- Planned
- Not Accepted
- Archived

UI Gallery submissions include fields for:

- source layout
- frontend dependencies used
- whether the YAML was exported by HI, lightly edited from HI output, hand-written, or unsure

The script still treats all template-derived signals as advisory. Labels, assignments,
comments, duplicate links, closures, and proposal promotion remain manual maintainer
actions.

Recommended manual labels after review:

- `needs-triage`
- `community-proposal`
- `proposal-review`
- `support`
- `needs-bundle`
- `has-diagnostics`
