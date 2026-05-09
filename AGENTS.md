# Humidity Intelligence Agent Guide

This is the public, repository-safe operating guide for AI agents working on Humidity Intelligence. It is intentionally concise and does not replace the design brief.

## Project Identity

Humidity Intelligence is a deterministic Home Assistant environmental control engine packaged as a HACS custom integration. It performs runtime-driven environmental orchestration, resolves one control decision per cycle, and generates truth-based dashboards from backend telemetry, mappings, and diagnostics.

## Source of Truth

- `DESIGN_BRIEF.md` is the implementation contract.
- `PROJECT_SUMMARY.md` may exist in maintainer workspaces as a local planning and release-preparation summary.
- Runtime behavior must follow `DESIGN_BRIEF.md`.
- If architecture, runtime behavior, security posture, release flow, contributor expectations, or documentation expectations materially change, update `DESIGN_BRIEF.md` in the same work.
- Maintainers may keep local-only instructions in `AGENTS.local.md`. That file is intentionally ignored and must not be required for public contributors or public repo correctness.

## Non-Negotiable Architecture Rules

- Preserve the integration name, domain, HACS identity, and public package positioning unless explicitly instructed otherwise.
- Keep deterministic control authoritative: one selected ventilation lane per evaluation cycle.
- Keep humidity targets season-aware and profile-relative.
- Keep generated dashboards and reason panels aligned with backend truth only.
- Do not add hidden automations, hidden service paths, or parallel output writers.
- Optional frontend cards and UI dependencies must never block backend functionality.
- Unknown, unavailable, incomplete, or unmapped inputs must degrade safely and explainably.

## Deterministic Runtime Rules

- Preserve lane priority: CO emergency, humidity danger, mould danger, mould risk, condensation danger, condensation risk, zone 1, zone 2, AQ, normal.
- CO emergency is always the highest-priority runtime lane.
- Humidity, mould, and condensation alerts must resolve source, room, and zone before applying zone-bound control.
- Humidity danger thresholds are derived from the active target profile, not legacy static alert values.
- Humidifier lanes remain independent from ventilation lane resolution.
- Global gates must be respected and surfaced truthfully in runtime telemetry and UI.
- Missing outputs or failed optional service calls must be logged, skipped, and exposed without crashing the control loop.

## UI/Card Generation Rules

- Do not invent placeholder entities.
- Do not use private entity IDs, device IDs, room names, telemetry values, or user-specific helpers in published cards, tests, docs, screenshots, or examples.
- Do not ship malformed Lovelace structures, empty card containers, invalid conditionals, or unresolved self-mapped placeholders.
- Dashboard chips must map to backend telemetry, entity mapping, diagnostics, or runtime truth.
- Current Air Control chips are display surfaces only. They must not create or alter lane decisions.
- Alert chipsets should stay concise: active lane/status plus resolved source context.
- Optional chip rows and optional frontend dependencies must hide or degrade cleanly when unavailable.
- After UI template, mapping, chip, or card-generation changes, validate exported/generated cards before completion.

## Home Assistant and HACS Compatibility Rules

- Keep config flow, options flow, entity registry behavior, services, translations, diagnostics, and generated files compatible with supported Home Assistant versions.
- Avoid blocking filesystem, network, or slow I/O work in async Home Assistant paths.
- Keep service schemas explicit and error messages actionable.
- Keep `hacs.json` limited to HACS-supported keys.
- Keep integration metadata in `manifest.json`.
- Keep branding assets, README expectations, HACS metadata, and release notes aligned with the actual package layout.
- Do not add hard dependencies on optional frontend cards.

## Validation Expectations

- Run validation appropriate to the changed scope.
- For runtime changes, include Python compile/import sanity and targeted regression tests where available.
- For card/UI changes, validate generated Lovelace output and check for stale mappings, private entities, malformed structures, and frontend dependency assumptions.
- For docs-only changes, perform a documentation sanity pass: check filenames, source-of-truth references, public-safety, and consistency with current repository structure.
- Review for stale imports, stale mappings, stale docs, outdated service names, and drift from `DESIGN_BRIEF.md`.
- Do not claim validation was completed if it was not run.

## Documentation and Release Expectations

- Keep `README.md`, `manifest.json`, `hacs.json`, docs, release notes, UI examples, and runtime behavior aligned.
- Update related docs when implementation behavior changes.
- Preserve backwards compatibility where practical. If compatibility breaks, call it out explicitly and document the migration path.
- Keep release notes factual, version-aligned, and free of private local details.
- Report changed files and validation results at the end of the work.

## Safety and Privacy Rules

- Never expose secrets, tokens, credentials, addresses, private telemetry, private entity IDs, device IDs, usernames, machine names, or local absolute paths.
- Do not run destructive actions unless explicitly requested.
- Do not delete user files, generated outputs, dashboards, helpers, or repository metadata without clear authorization.
- Public examples must use canonical HI entities or sanitized placeholders only.
- Do not publish local-only planning notes unless explicitly approved.

## What Agents Must NOT Do

- Do not rename the integration.
- Do not bypass deterministic architecture.
- Do not invent entities, services, sensors, helpers, features, workflows, or commands.
- Do not weaken runtime truth principles.
- Do not silently remove backward compatibility.
- Do not introduce private entities into public docs, cards, screenshots, examples, release notes, or tests.
- Do not mark work complete without appropriate validation.
- Do not duplicate the design brief here or let this file become bloated documentation.
