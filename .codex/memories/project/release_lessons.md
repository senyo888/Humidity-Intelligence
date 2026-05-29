# Release Lessons

This file records durable release lessons already supported by current repository context.
Keep it light. Do not add imagined incidents or speculative rules.

## Known Lessons

- Treat v2.0.5 as the completed adoption-friendly configuration UX and support-readiness release with stable runtime semantics.
- Keep v2.1 Environmental Stability Intelligence as planned future direction until implemented and validated.
- Normal `pytest` may be blocked in local environments without Home Assistant installed; use the direct sanity harness as a local fallback and report the pytest blocker plainly.
- Optional frontend dependency detection must be non-blocking and shared across setup/options, diagnostics, `self_check`, and `v205_release_check`.
- `dump_cards` remains canonical: unscoped calls export all cached/generated layouts, scoped `layout` calls export only the requested layout.
- Root-content HACS packaging needs release validation that accounts for `content_in_root: true` and staged Hassfest checks.
- Local planning and governance files must stay public-safe and ignored unless explicitly approved for publication.
- Future release readiness still depends on Home Assistant-capable validation,
  generated-card rendering checks, HACS metadata checks, and GitHub workflow results.
- Future version release/tagging is blocked until full Bella verification, full
  AetherCore governance verification, release sanity validation, and README approval by
  Senyo are complete.
- Native Home Assistant diagnostics are the preferred GitHub issue attachment; the
  fuller `dump_diagnostics` export remains a local maintainer/debug path.
- For scheduled issue-triage work, preserve report-only dry runs and manual GitHub mutation boundaries unless a maintainer explicitly approves a wider operation packet.
