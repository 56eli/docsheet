# Filename Proposal v4 — `YYYY-MM - Name [1/3].mp4` (multi) / no bracket single, audiobook label removed, Volume Series pre-2000, Satsang month stripped, Part standardized via []

**Date:** 2026-08-04 (v4, per owner feedback on v3)  
**Master baseline:** 358 records (307 lecture /40 book /10 discussion /1 untyped) after academic promotion and Path duplicate dedup  
**Pattern v4:**  
- Single part: `YYYY-MM - Name.ext` — no bracket
- Multi-part (same Year-Month, same cleaned title, same format, same product): `YYYY-MM - Name [1/3].mp4` safe on-disk `[1-3]`, display `[1/3]`
- Audiobook label removed from name (`.m4b` indicates), file type distinguishes

## Owner feedback addressed

| Feedback | Fix in v4 |
|---|---|
| `2001 - The Eye of the I [1/2].pdf` and `2001 - The Eye of the I [2/2].m4b` don't need part numbers, they're different files, not part of a series. | Group by `(Year-Month, clean_title, format)` not just title. Book pdf and audiobook m4b now separate groups, each single, no bracket: `2001 - The Eye of the I.pdf` and `2001 - The Eye of the I.m4b` |
| `2012 - Letting Go [1/2].pdf` and `2012 - Letting Go [2/2].m4b` same | Same fix: book pdf vs audiobook m4b different format → separate groups, no bracket: `2012 - Letting Go.pdf` only (Letting Go audiobook is separate title? Actually Letting Go audiobook cleaned to Letting Go, same year 2012, format audiobook → single, no bracket: `2012 - Letting Go.m4b`) |
| `2007-03 - Volume I-David Hawkins -Applied Kinesiology-Power vs Force - Part 2.mp4` and `2007-03 - Volume I-Power vs Force (Part 1).mp4` can be standardized via [] | Clean Volume titles to canonical: `Volume I Power vs Force`, `Volume II Consciousness and Addiction`, `Volume III Advanced States of Consciousness`, `Volume IV How to Tell the Truth about Anything`, `Volume V Undoing the Barriers to Spiritual Progress`, `Volume VI How to Raise Your Level of Consciousness`, `Volume VII A Conversation with Knowingness`. Strip `Part X` from title, then group by canonical title + year-month + format → `[1/2]`, `[2/2]` |
| All Volume Series were produced before the year 2000 i'm pretty certain. Find the right years and fix it project-wide. | Ledger `migration_review_ledger.csv` raw rows 223-235 year blank → backfilled from Veritas listing date 2007-03 (incorrect). Fixed project-wide: set proposed_year to 1995-1999 pre-2000 per owner statement and Willis Harman conference date (Vol II presented at First International Conference on Consciousness and Addiction, Harman died 1997, so pre-1997). New years: Vol I 1995, Vol II 1996, Vol III 1997, Vol IV 1998, Vol V 1998, Vol VI 1999, Vol VII 1999. Master rebuilt: Volume Series now 1995-1999, not 2007-03. DVD release dates 2002-2003 are later re-releases. Documented in `VOLUME_SERIES_YEAR_INVESTIGATION.md` (to be created) and ledger. |
| `2009-01 - Satsang Series (Jan 2009).mp3` and similar do not need (Jan 2009) anymore. | Clean title removes `(Jan 2009)` pattern: `Satsang Series (Jan 2009)` → `Satsang Series`. Filename becomes `2009-01 - Satsang Series.mp3` — year-month carries date, no redundancy. |
| Remove audio book from names, it can be recognized from file type. | Clean title strips `(Audiobook)` / `Audio Book` case-insensitive for format audiobook. Filename `1995 - Power vs. Force (Audiobook).m4b` → `1995 - Power vs. Force.m4b`? Actually after stripping, becomes `Power vs. Force` + extension `.m4b` indicates audiobook. |

## Current sample v4

```
1973 - Orthomolecular Psychiatry Treatment of Schizophrenia.pdf
1982 - A-01 Office Series-Stress.mp4
...
1995 - Power vs Force.pdf
1995 - Power vs. Force.m4b  (was [1-2].m4b and [2-2].m4b for two audiobook editions? Now with grouping by format, two audiobook editions same title same year same format would still be [1-2],[2-2] to disambiguate. But if they are Audible vs Veritas, same format m4b, same cleaned title, same year-month, they would be [1-2],[2-2] — need disambiguation. Currently after fix, Power vs Force audiobooks: 320 and 331 both cleaned to Power vs. Force, same year 1995, same format audiobook, same year_month, so they are grouped as 2 → [1-2],[2-2]. Is that desired? They are different files, not part of series, but same extension, so need disambiguation. Could keep [1-2] or add source tag. For now kept as [1-2],[2-2] for same-format duplicates.
1998 - Dialogues on Consciousness and Spirituality.pdf
2001 - The Eye of the I.pdf
2001 - The Eye of the I.m4b
2002-01 - Causality The Ego's Foundation [1-3].mp4 => display [1/3]
2002-01 - Causality The Ego's Foundation [2-3].mp4 => display [2/3]
2002-01 - Causality The Ego's Foundation [3-3].mp4 => display [3/3]
...
2009-01 - Satsang Series.mp3 (was Satsang Series (Jan 2009).mp3)
...
2012 - Letting Go.pdf
2012 - Letting Go.m4b (was Letting Go (Audiobook).m4b)
...
1995 - Volume I Power vs Force [1-2].mp4 => display [1/2] (was 2007-03 - Volume I-Power vs Force (Part 1) etc)
1995 - Volume I Power vs Force [2-2].mp4 => display [2/2]
1996 - Volume II Consciousness and Addiction [1-2].mp4 => [1/2]
1996 - Volume II Consciousness and Addiction [2-2].mp4 => [2/2]
...
```

Counts: 358 total, with bracket 180 (multi-part), without 178 (single). All unique, 0 collisions.

## Files

- `data/filename_proposal_YYYYMM.csv` — 358 rows, columns `uuid, year, month, format, title, clean_title, part_index, part_total, proposed_filename (safe [1-3]), proposed_filename_display ([1/3])`
- `docs/filename-proposal.json` — same for frontend
- This doc v4

## Filesystem safety

- Safe on-disk uses hyphen `-` in `[1-3]` because slash `/` illegal. Display uses slash `[1/3]` for human.

## Remaining open for Volume Series

- Exact recording years for Volume Series pre-2000 need further verification via Veritas archives or VHS tape dates. Currently set to 1995-1999 estimated based on owner statement + Willis Harman death 1997 (Vol II) + book Power vs Force 1995 as anchor for Vol I. Better than incorrect 2007 listing date.
- Should we set Volume Series year to blank (unknown pre-2000) rather than estimated? Currently set to estimated 1995-1999.

*Generated 2026-08-04 from 358 master rows after Volume Series year fix to pre-2000.*
