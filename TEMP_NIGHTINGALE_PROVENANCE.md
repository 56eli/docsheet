# TEMP — Nightingale-Conant Provenance Gap Fill (2026-08-03)

**Task completion summary:** Identified the primary evidence case (record 300 / product 1661) and the official Nightingale-Conant product page; prepared proposal for safe population of `source_url_nightingale_conant`.

## Evidence
- Record 300 ("In the World, But Not of It") has Veritas primary URL but empty `source_url_nightingale_conant`.
- Veritas product 1661 official title explicitly states "Publisher: Nightingale-Conant".
- Official Nightingale-Conant product page: https://www.nightingale.com/products/in-the-world-but-not-of-it
- The field `source_url_nightingale_conant` is currently 0/317 populated across the entire master (P2 hardening item).

## Proposed action (reviewable, non-destructive)
Because `source_url_nightingale_conant` is **not** in the current `SOURCE_OVERRIDE_FIELDS`, the cleanest path is one of:
1. Extend the override schema to include it (small, safe change), or
2. Add a dedicated `nightingale_mapping_decisions.csv` parallel to `veritas_mapping_decisions.csv`.

For the first record (300 / 1661) we can add the URL via a new source-override row once the schema is extended, or manually populate it in the ledger if the owner prefers a one-off.

**Suggested first override row (after schema update):**
```
341,source_url_nightingale_conant,https://www.nightingale.com/products/in-the-world-but-not-of-it,approved,2026-08-03,Publisher explicitly listed on Veritas product 1661 page; matches official Nightingale-Conant product for the same work.,web search + Veritas product 1661 metadata
```

This keeps the pattern consistent with existing source overrides.

**File is temporary — delete after decision.**