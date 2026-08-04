# TEMP — Nightingale-Conant Provenance Gap Fill (2026-08-03)

> **RESOLVED 2026-08-04 — kept for the audit trail.**
> Option 1 was adopted (schema extended to include `source_url_nightingale_conant`
> in `SOURCE_OVERRIDE_FIELDS`). The official NC author page
> (https://www.nightingale.com/pages/david-hawkins, fetched live 2026-08-04)
> lists exactly 7 Hawkins programs. The 4 that are master audio editions were
> filled via **candidate-keyed** approved overrides (masters **327–330**:
> Truth Vs Falsehood, Healing, In The World But Not Of It, The Highest Level
> Of Enlightenment — the edition rows minted from `edition_candidates.csv`;
> they have no `raw_row_number`, so overrides key on their `candidate_key`).
> The other 3 NC products (The Ultimate David Hawkins Library, The Discovery,
> Naked) are unmapped compilations/programs that remain in
> `data/official_discovery_queue.csv` pending owner ruling — deliberately NOT
> force-mapped onto masters. `source_url_nightingale_conant` is now 4/356
> populated (was 0/317 when this note was written).
>
> Note: the record-300/1661 analysis below refers to the pre-edition-model
> master (record 300 then carried the audio-edition association directly);
> under the 2026-08-03 edition model the NC 6-CD edition became master 329.

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