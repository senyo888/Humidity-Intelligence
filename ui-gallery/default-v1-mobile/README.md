# Default V1 Mobile (Deprecated)

- Status: deprecated in v2.0.9; retained through the v2.0.9 line
- Replacement: V2 Mobile (`ui/cards/v2_mobile.yaml`)
- Style: legacy-compatible mobile layout with comfort band and humidity constellation
- Optimised for: phones and users keeping a V1-style dashboard presentation
- Author: @senyo888
- Source template: `ui/cards/v1_mobile.yaml`
- Required custom cards: `card-mod`, `button-card`, `mod-card`, `apexcharts-card`

[![Default V1 Mobile preview](preview.png)](preview.png)

## Notes

This example preserves the V1-style mobile presentation while using the V2
integration's canonical generated entities and semantics. It remains available for
existing users through v2.0.9, but new dashboards should use V2 Mobile. Its dynamic
room, target-profile, condensation, and mould text is escaped before HTML insertion.

The YAML is copied from the canonical generated card template and should be treated as
an example artifact. In a real installation, prefer the card YAML exported by
`humidity_intelligence.dump_cards` so placeholders match your generated entities.
Already-pasted V1 cards must be re-exported and re-copied to receive the v2.0.9
escaping fix. V1 removal remains a separate v2.1 migration proposal.

## Files

- [Preview](preview.png)
- [Card YAML](card.yaml)
