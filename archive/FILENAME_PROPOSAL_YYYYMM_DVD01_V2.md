# Filename Proposal v2 — `YYYY-MM - Name [1/3].mp4` (multi-part) / no bracket for single

**Date:** 2026-08-04 (v2, per owner request)  
**Status:** Proposal — no master data changed, only derived filename mapping  
**Master baseline:** 358 records (307 lecture / 40 book / 10 discussion / 1 untyped)  
**Requested pattern v2:** Change all Part 1 and DVD 1 to `[1/X]` where X is max part number. Remove part number where there is only one part.

## Pattern v2

```
Single part (most books, single-disc Office Visit):
  {Year-Month} - {ShortTitle}.{ext}
  Example: 1995 - Power vs Force.pdf
  Example: 1982 - A-01 Office Series-Stress.mp4

Multi-part (same lecture, same Year-Month, same ShortTitle, e.g., 3 DVD parts):
  {Year-Month} - {ShortTitle} [1/3].{ext}
  {Year-Month} - {ShortTitle} [2/3].{ext}
  {Year-Month} - {ShortTitle} [3/3].{ext}

Filesystem-safe variant:
  Slash `/` is illegal in filenames on all OSes (it's a path separator). The safe on-disk name uses hyphen `-` instead: `[1-3]` but displays as `[1/3]` in documentation/UI.
  CSV provides both:
  - `proposed_filename` — safe on-disk: `2002-01 - Causality The Ego's Foundation [1-3].mp4` (hyphen)
  - `proposed_filename_display` — human display: `2002-01 - Causality The Ego's Foundation [1/3].mp4` (slash)

## Why [1/X]?

- Old: `[DVD01]`, `[DVD02]` — tells you disc label but not how many total discs.
- New: `[1/3]`, `[2/3]`, `[3/3]` — immediately tells you this is part 1 of 3 total, intuitive for "oh yeah that 2004 one, part 2".
- No bracket for single part: `1995 - Power vs Force.pdf` is clean, no redundant `[1/1]`.

## Examples per your request

- **Causality Jan 2002 has 3 DVD parts:**
  - Before: `2002-01 - Causality The Ego's Foundation [DVD01].mp4`, `[DVD02]`, `[DVD03]`
  - **Now v2:** `2002-01 - Causality The Ego's Foundation [1/3].mp4`, `[2/3]`, `[3/3]`
  - Safe on-disk: `[1-3]`, `[2-3]`, `[3-3]`

- **Thought and Ideation Feb 2004 (3 parts):**
  - `2004-02 - Thought and Ideation [1/3].mp4`, `[2/3]`, `[3/3]`

- **Power vs Force book (single):**
  - Before: `1995 - Power vs Force.pdf` (same) or `1995 - Power vs Force [Book].pdf`
  - **Now v2:** `1995 - Power vs Force.pdf` — no bracket, as requested (only one part)

- **Power vs Force Audiobook (single audiobook edition, separate from book):**
  - Before: `1995 - Power vs. Force (Audiobook) [Audiobook].m4b`
  - **Now v2:** `1995 - Power vs. Force (Audiobook).m4b` — no bracket because single part (extension `.m4b` already distinguishes audiobook)

- **Office Visit 1982 single disc:**
  - Before: `1982 - A-01 Office Series-Stress [DVD01].mp4`
  - **Now v2:** `1982 - A-01 Office Series-Stress.mp4` — no bracket (only one part)

- **Volume II Consciousness and Addiction has 2 DVD parts same title same month:**
  - `2007-03 - Volume II-Consciousness and Addiction [1/2].mp4`, `[2/2].mp4`

- **Presence of Spiritual Awareness has 3 parts same title 2004 (no month):**
  - `2004 - The Presence of Spiritual Awareness [1/3].mp4`, `[2/3]`, `[3/3]`

## Implementation

- Group rows by `(Year-Month, ShortTitle)` — short title truncated to 80 chars, illegal chars stripped.
- Within each group, sort by UUID (stable), assign index 1..N where N = group size.
- If N>1: filename = `{Year-Month} - {ShortTitle} [{index}-{N}].{ext}` safe, display `[{index}/{N}]`
- If N==1: filename = `{Year-Month} - {ShortTitle}.{ext}` — no bracket

Result: **358 unique filenames, 0 collisions** (verified).

## Full list

- **CSV:** `data/filename_proposal_YYYYMM.csv` — 358 rows, columns `uuid, work_id, item_type, series, year, month, format, format_detail, catalog_code, title, part_index, part_total, proposed_filename, proposed_filename_display`
- **JSON:** `docs/filename-proposal.json` — same for frontend
- Sample first 60:

```
1973 - Orthomolecular Psychiatry Treatment of Schizophrenia.pdf
1982 - A-01 Office Series-Stress.mp4
1982 - A-02 Office Series-Health.mp4
...
1995 - Power vs Force.pdf
1995 - Power vs. Force (Audiobook).m4b
...
2002-01 - Causality The Ego's Foundation [1-3].mp4 => display [1/3]
2002-01 - Causality The Ego's Foundation [2-3].mp4 => display [2/3]
2002-01 - Causality The Ego's Foundation [3-3].mp4 => display [3/3]
...
2004-02 - Thought and Ideation [1-3].mp4 => display [1/3]
...
```

## Changes from v1

| v1 | v2 (this) |
|---|---|
| `[DVD01]`, `[DVD02]` even for single | `[1/3]`, `[2/3]` for multi-part, no bracket for single |
| `1995 - Power vs Force [Book].pdf` or `[DVD01].mp4` for single | `1995 - Power vs Force.pdf`, `1982 - A-01 Office Series-Stress.mp4` — clean, no redundant bracket |
| Edition detail from `format_detail` used when present | Edition detail ignored; part counting is based on grouping, not format_detail string |
| 358 unique, but single DVDs had [DVD01] bracket | 358 unique, singletons have no bracket |

## Open questions for final approval

- For books that have both book and audiobook editions same year same base title (Power vs Force book pdf + audiobook m4b), they currently have same Year-Month + ShortTitle? Actually short titles differ: "Power vs Force" vs "Power vs. Force (Audiobook)" — different groups, each single, no bracket. Do you want them grouped as 2 parts of same work with [1/2] [2/2] across formats, or keep separate as now (extension distinguishes)?
- For Office Series, title includes "A-01 Office Series-Stress" — keep prefix or strip to "Stress"? Currently keeps prefix.
- Max length 120 — okay?

## Next steps if approved

1. Keep CSV as reviewed input
2. Add generator `build_filename_pages.py` that validates uniqueness, illegal chars, max length, and writes `docs/filename-proposal.json` + meta
3. Add new **Filenames** tab in frontend showing proposed filename + display version + copy button
4. Optional organizer script uses CSV to hardlink local files

*Generated 2026-08-04 by deterministic Python from 358 master rows, no network.*
