# Filename Proposal v4 — `YYYY-MM - Name [1/3].mp4` (multi) / no bracket single, audiobook label removed, Volume Series blank pre-2000, Satsang month stripped, Part standardized via []

**Date:** 2026-08-07 (v4 updated, per owner feedback on v3 + blank-year ruling 2026-08-04)  
**Master baseline:** 358 records (307 lecture /40 book /10 discussion /1 untyped) after academic promotion and Path duplicate dedup (current)  
**Pattern v4:**  
- Single part: `YYYY-MM - Name.ext` — no bracket; if year blank, `Name.ext` (no prefix)
- Multi-part (same Year-Month, same cleaned title, same format, same product): `YYYY-MM - Name [1/3].mp4` safe on-disk `[1-3]`, display `[1/3]`; if Year-Month blank, `Name [1-3].mp4` safe / `Name [1/3].mp4` display
- Audiobook label removed from name (`.m4b` indicates), file type distinguishes
- Volume Series: year blank pre-2000 per owner ruling “do not name any if cannot name all” (2026-08-04), so filename has no year prefix, grouped by (clean_title, format) only → `Volume I Power vs Force [1-2].mp4` display `[1/2]`

## Owner feedback addressed

| Feedback | Fix in v4 |
|---|---|
| `2001 - The Eye of the I [1/2].pdf` and `2001 - The Eye of the I [2/2].m4b` don't need part numbers, they're different files, not part of a series. | Group by `(Year-Month, clean_title, format)` not just title. Book pdf and audiobook m4b now separate groups, each single, no bracket: `2001 - The Eye of the I.pdf` and `2001 - The Eye of the I.m4b` |
| `2012 - Letting Go [1/2].pdf` and `2012 - Letting Go [2/2].m4b` same | Same fix: book pdf vs audiobook m4b different format → separate groups, no bracket: `2012 - Letting Go.pdf` only (Letting Go audiobook is separate title? Actually Letting Go audiobook cleaned to Letting Go, same year 2012, format audiobook → single, no bracket: `2012 - Letting Go.m4b`) |
| `2007-03 - Volume I-David Hawkins -Applied Kinesiology-Power vs Force - Part 2.mp4` and `2007-03 - Volume I-Power vs Force (Part 1).mp4` can be standardized via [] | Clean Volume titles to canonical: `Volume I Power vs Force`, `Volume II Consciousness and Addiction`, `Volume III Advanced States of Consciousness`, `Volume IV How to Tell the Truth about Anything`, `Volume V Undoing the Barriers to Spiritual Progress`, `Volume VI How to Raise Your Level of Consciousness`, `Volume VII A Conversation with Knowingness`. Strip `Part X` from title, then group by canonical title + year-month + format → `[1/2]`, `[2/2]` |
| All Volume Series were produced before the year 2000 i'm pretty certain. Find the right years and fix it project-wide. | Ledger `migration_review_ledger.csv` raw rows 223-235 year blank → backfilled from Veritas listing date 2007-03 (incorrect). Initially fixed to 1995-1999 estimated pre-2000 (Vol II at Willis Harman conference pre-1997). Owner feedback 2026-08-04: “do not name any if cannot name all” → project-wide strip to blank pre-2000 per `CATEGORY_DOMINANCE_POLICY` year-investigation ruling. Reviewed reason in ledger: “Year under investigation, believed pre-2000 per owner (V1 1995,1996 known but others unclear), stripped from filename per owner request 2026-08-04 v4 feedback: do not name any if cannot name all.” Master rebuilt: Volume Series now blank year (no catalogue codes, filename no year prefix like `Volume I Power vs Force [1-2].mp4`), not 2007-03 nor 1995-1999 estimate. DVD 2002-2003 dates are later re-releases. |
| `2009-01 - Satsang Series (Jan 2009).mp3` and similar do not need (Jan 2009) anymore. | Clean title removes `(Jan 2009)` pattern: `Satsang Series (Jan 2009)` → `Satsang Series`. Filename becomes `2009-01 - Satsang Series.mp3` — year-month carries date, no redundancy. |
| Remove audio book from names, it can be recognized from file type. | Clean title strips `(Audiobook)` / `Audio Book` case-insensitive for format audiobook. Filename `1995 - Power vs. Force (Audiobook).m4b` → `1995 - Power vs. Force.m4b`? Actually after stripping, becomes `Power vs. Force` + extension `.m4b` indicates audiobook. |

## Current sample v4

```
1973 - Orthomolecular Psychiatry Treatment of Schizophrenia.pdf
1982 - A-01 Office Series-Stress.mp4
...
1995 - Power vs Force.pdf
1995 - Power vs. Force [1-2].m4b / 1995 - Power vs. Force [2-2].m4b (Decision: Two audiobook editions—Audible vs Veritas—sharing the exact same cleaned title, year, and format are disambiguated with [1-2]/[2-2] to prevent filename collision on disk).
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

Sample after blank-year fix (2026-08-07 verified from `data/filename_proposal_YYYYMM.csv`):
```
1973 - Orthomolecular Psychiatry Treatment of Schizophrenia.pdf
...
1995 - Power vs Force.pdf
1995 - Power vs. Force [1-2].m4b / [2-2].m4b (two audiobook editions 320 & 331 same title/year/format → [1-2][2-2])
1998 - Dialogues...
2001 - The Eye of the I.pdf (book, no bracket)
2001 - The Eye of the I.m4b (audiobook, no bracket — different format group)
2002-01 - Causality The Ego's Foundation [1-3].mp4 => display [1/3]
2009-01 - Satsang Series.mp3 (month stripped)
...
Volume I Power vs Force [1-2].mp4 (no year prefix, year blank pre-2000)
Volume I Power vs Force [2-2].mp4
Volume II Consciousness and Addiction [1-2].mp4
Volume V Undoing... [1-3].mp4 etc
```

Counts: 358 total, with bracket ~180 (multi-part), without ~178 (single). All 358 unique, 0 collisions (verified).

## Files

- `data/filename_proposal_YYYYMM.csv` — 358 rows, columns uuid, year, month, format, title, clean_title, part_index, part_total, proposed_filename safe [1-3], proposed_filename_display [1/3]
- `docs/filename-proposal.json` — same for frontend
- This doc v4 (updated 2026-08-07)

## Filesystem safety

- Safe on-disk uses hyphen `-` in `[1-3]` because slash `/` illegal. Display uses slash `[1/3]` for human.
- Illegal chars `<>:"/\\|?*` stripped, max 120 chars.

## Remaining open for Volume Series

- Exact recording years for Volume Series pre-2000 need verification via Veritas archives or VHS tape dates. Owner ruling 2026-08-04: “do not name any if cannot name all” → master year blank, no catalogue codes, filename no year prefix (`Volume I Power vs Force [1-2].mp4`). Better than incorrect 2007 listing date or partial 1995-1999 estimates.
- Future: if all Volume years become known, restore YYYY-MM prefix and catalogue codes.

*Updated 2026-08-07 from 358 master rows — Volume Series year blank pre-2000, not estimated.*
