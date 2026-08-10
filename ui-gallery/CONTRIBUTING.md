![Humidity Intelligence UI Gallery contributing banner](../assets/header.png)

# Contributing UI Gallery Examples

Thank you for helping improve the Humidity Intelligence UI Gallery.

This guide covers Lovelace cards, dashboards, previews, and layout documentation only. Backend logic, sensors, entity semantics, automation behavior, and generated helper contracts are out of scope for gallery submissions.

The browseable Gallery page lives in the GitHub Wiki, but canonical submissions still happen here through repository pull requests. Do not submit Wiki-only dashboard YAML as the source of truth.

## Scope

The integration provides:

- Stable generated entities
- Canonical risk semantics
- Runtime reason telemetry
- Generated card templates
- Safe service-driven card export

UI Gallery examples show how that intelligence can be presented.

Visual creativity is welcome. Canonical behavior, privacy safety, and copy/paste clarity are mandatory.

## What You Can Contribute

You may submit:

- Full dashboard examples
- Individual card examples
- Variants of the default V2 layouts
- Mobile, tablet, and wall-panel layouts
- Experimental designs, when clearly marked as experimental

## Required Folder Format

Create your gallery folder locally:

```text
ui-gallery/<card-id>/
```

Example:

```text
ui-gallery/default-v2-mobile-aq/
```

Each example must include:

```text
README.md
preview.png
card.yaml
```

Use `dashboard.yaml` instead of `card.yaml` only when the submission is a full dashboard view.

## README Entry Format

Every example folder must include a short `README.md` using this shape:

```md
# Example Name

- Style: concise visual description
- Optimised for: Mobile / Tablet / Wall panel
- Author: @handle
- Source template: custom_components/humidity_intelligence/ui/cards/example.yaml
- Required custom cards: card-mod, button-card, mod-card, apexcharts-card

[![Preview](preview.png)](preview.png)

## Notes

Short setup or behavior notes.

## Files

- [Preview](preview.png)
- [Card YAML](card.yaml)
```

The top-level [README.md](README.md) must also get a matching entry.

Maintainers may mirror accepted examples into the Wiki after review. The Wiki entry should link back to the repository YAML and preview files rather than becoming an independent dashboard source.

## Canonical Compatibility Rules

Submissions must:

- Preserve Humidity Intelligence backend semantics: `OK`, `Watch`, `Risk`, `Danger`, lane order, and runtime reason meaning
- Use generated/canonical Humidity Intelligence entities and placeholders where possible
- Document required custom cards
- Avoid private entity IDs, addresses, people names, device IDs, tokens, internal URLs, or other personal data
- Avoid modifying backend logic or sensor meanings
- Remain understandable when copied into a clean Home Assistant instance
- Keep Current Air Control chips tied to backend status truth. Layout and colour may
  clarify state but must not merge ventilation selection, humidifier demand,
  reconciliation, or physical-output meaning.
- Use fresh runtime captures for claims about a candidate UI. Mockups and captures
  from an earlier package must be labelled as references, never current playback
  evidence.

Examples may use generic demo rooms such as Bathroom, Bedroom, Kitchen, Zone 1, or Zone 2.

## Pull Request Checklist

Before opening a pull request, confirm:

- [ ] Folder path is `ui-gallery/<card-id>/`
- [ ] Folder was created locally and committed with all files
- [ ] `README.md`, `preview.png`, and YAML are included
- [ ] YAML contains no private entity IDs or secrets
- [ ] Screenshots contain no private data
- [ ] Canonical entities and semantics are preserved
- [ ] Required custom cards are documented
- [ ] Top-level `ui-gallery/README.md` is updated
- [ ] Wiki mirror/update need is noted in the PR
- [ ] PR targets `develop`
- [ ] PR title follows `UI Gallery: <short description>`

## Design Intent

A good Humidity Intelligence UI should help answer:

- Where is the risk?
- How serious is it?
- What is the runtime doing now?
- What should the user inspect next?

Clarity matters more than decoration. A beautiful dashboard that changes semantics or hides risk is not a good gallery example.
