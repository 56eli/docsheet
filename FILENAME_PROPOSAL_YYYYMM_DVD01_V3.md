# Filename Proposal v3 — `YYYY-MM - Name [1/3].mp4` / no bracket for single, audiobook label removed from name

**Date:** 2026-08-04 (v3, per owner request: remove audio book from names, file type indicates)  
**Status:** Proposal — derived mapping only  
**Master baseline:** 358 records  
**Pattern v3:**  
- Multi-part: `YYYY-MM - Name [1/3].mp4` safe on-disk `[1-3]`, display `[1/3]`
- Single part: `YYYY-MM - Name.ext` — no bracket, as requested "remove part number where there is only one part"
- Audiobook label removed from name: file type `.m4b` indicates audiobook, so `(Audiobook)` / `Audio Book` stripped from title before filename generation.

## Changes from v2 → v3

| Aspect | v2 | v3 (this) |
|---|---|---|
| Audiobook text in name | Kept `(Audiobook)` in title, plus `[Audiobook]` bracket | **Removed** `(Audiobook)`, `Audio Book` from title; file type `.m4b` indicates audiobook; only `[1/3]` part notation remains if multiple audiobook editions of same work |
| Single part bracket | No bracket for single (same) | Same: no bracket for single |
| Multi-part | `[1-3]` safe / `[1/3]` display | Same |
| Example Power vs Force | `1995 - Power vs. Force (Audiobook).m4b` or `1995 - Power vs. Force (Audiobook) [Audiobook].m4b` | `1995 - Power vs Force.pdf` (book, no bracket), `1995 - Power vs. Force [1-2].m4b`, `1995 - Power vs. Force [2-2].m4b` — two audiobook editions distinguished by [1-2]/[2-2], no "Audiobook" text, only extension |
| Office single | `1982 - A-01 Office Series-Stress.mp4` no bracket | Same |

## Why remove audiobook label?

- Extension `.m4b` / `.mp3` already indicates audio
- Keeps filename shorter, avoids redundant `Power vs Force (Audiobook) [Audiobook].m4b`
- User request: "remove audio book from names, it can be recognized from file type"

Implementation: `clean_title_for_filename()` strips regex `\s*\(?\s*Audio\s*Book\s*\)?` and `\s*\(?\s*Audiobook\s*\)?` case-insensitive, collapses spaces.

## Sample v3 (first 40)

```
1973 - Orthomolecular Psychiatry Treatment of Schizophrenia.pdf
1982 - A-01 Office Series-Stress.mp4
1982 - A-02 Office Series-Health.mp4
...
1995 - Power vs Force.pdf
1995 - Power vs. Force [1-2].m4b
1995 - Power vs. Force [2-2].m4b
1998 - Dialogues on Consciousness and Spirituality.pdf
1998 - Qualitative and Quantitative Analysis and Calibration of the Level of Human C.pdf
2001 - The Eye of the I.pdf
2001 - The Eye of the I.m4b
2002-01 - Causality The Ego's Foundation [1-3].mp4 => display [1/3]
2002-01 - Causality The Ego's Foundation [2-3].mp4 => display [2/3]
2002-01 - Causality The Ego's Foundation [3-3].mp4 => display [3/3]
...
2004-02 - Thought and Ideation [1-3].mp4 => display [1/3]
```

- Single-part lecture: `2004 - A-01 Office Series-Stress.mp4` — no bracket
- Multi-part lecture (3 discs): `2002-01 - Causality ... [1-3].mp4`, `[2-3]`, `[3-3]`
- Book single: `1995 - Power vs Force.pdf` — no bracket
- Audiobook single edition (if only one audio edition per work): would be `1995 - Power vs Force.m4b` — no bracket, extension distinguishes, but currently Power vs Force has 2 audio editions, so they get [1-2], [2-2] to disambiguate.

Counts: 358 total, with bracket 223, without 135. All unique, 0 collisions.

## Files

- `data/filename_proposal_YYYYMM.csv` — 358 rows, columns `uuid, work_id, item_type, series, year, month, format, format_detail, catalog_code, title, clean_title, part_index, part_total, proposed_filename (safe [1-3]), proposed_filename_display ([1/3])`
- `docs/filename-proposal.json` — same for frontend
- This doc

## Filesystem safety

- Slash `/` in `[1/3]` is illegal on all OSes (path separator). Safe on-disk uses hyphen `[1-3]`, display uses slash `[1/3]`. Both provided in CSV.

## Open question

- For Office Series, keep `A-01` prefix or strip to `Stress`? Currently keeps prefix.
- For books, keep year prefix `1995 - Power vs Force.pdf` or just `Power vs Force.pdf`? Currently keeps year for sortability.

*Generated 2026-08-04 from 358 master rows, deterministic, no network.*
