# Filename Proposal — `YYYY-MM - Name [DVD01].mp4` for all files

**Date:** 2026-08-04  
**Status:** Proposal — no master data changed, only derived filename mapping  
**Master baseline:** 358 records (307 lecture / 40 book / 10 discussion / 1 untyped) after academic promotion and Path duplicate dedup  
**Requested pattern:** `YYYY-02 - Name [DVD01].mp4` — year first, month optional, short human name, edition detail in brackets, extension from format.

## Design Decisions

### 1. Pattern

```
{Year-Month} - {ShortTitle} [{EditionDetail}].{ext}
```

- **Year-Month:** `YYYY-MM` if month known, else `YYYY` if year only, else `0000` for deferred untyped 246 (no year). This sorts chronologically in Finder/Explorer.
- **ShortTitle:** cleaned public title truncated to 80 chars, illegal chars `<>:"/\|?*` stripped, whitespace collapsed. Keeps hook words so user recognizes "Oh yeah that Feb 2004 talk".
- **EditionDetail:** only short controlled values:
  - If `format_detail` present and ≤20 chars and no `;` (e.g., `DVD01`, `CD01`, `Audiobook`, `Streaming`): use it
  - Else if multiple files share same Year-Month + ShortTitle (e.g., Volume II has 2 disc parts same title same month, Presence of Spiritual Awareness has 3 disc parts): generate `DVD01`, `DVD02`, `DVD03` (or `CD01`, `Part1`) based on order within group
  - Else for single files:
    - `format=audiobook` → `[Audiobook]`
    - `format=CD` → `[CD]`
    - `format=streaming` → `[Streaming]`
    - `format=DVD` → `[DVD01]` (even for single, to match your example `YYYY-02 - Name [DVD01].mp4`)
    - `format=book` → no bracket (e.g., `1995 - Power vs Force.pdf` — easy)
- **Extension:**
  - DVD → mp4
  - CD → mp3
  - audiobook → m4b
  - book → pdf
  - streaming → mp4
  - blank → mp4 (lecture default) or pdf (book default)

### 2. Why this solves the unsatisfying problem

- **Old:** `The Levels of Consciousness: Subjective & Social Consequences (Mar 2002) DVD01` — redundant date twice, colon illegal on Windows, long.
- **New:** `2002-03 - The Levels of Consciousness Subjective & Social Consequences [DVD01].mp4` — year-month first, scannable, short, safe, still has disc detail in brackets for multi-part.

For books: `Power vs Force.pdf` stays easy, audiobook variant `1995 - Power vs. Force (Audiobook) [Audiobook].m4b` groups next to it alphabetically.

For Office Visit 1982: `1982 - A-01 Office Series-Stress [DVD01].mp4` — year first, then office series label, still recognizable.

### 3. Uniqueness

- Grouped by `(Year-Month, ShortTitle)` — if multiple rows share same key (e.g., Volume II Consciousness and Addiction has 2 disc parts same title same month, Presence of Spiritual Awareness has 3 parts), disambiguate with `[DVD01]`, `[DVD02]`, `[DVD03]`.
- Result: **358 unique filenames, 0 collisions** (verified).

### 4. Folder hierarchy suggestion (optional, not part of filename itself)

Pair this filename scheme with **Year folders** for the "that 2004 one" browsing:

```
Hawkins Archive/
  1973/
    1973 - Orthomolecular Psychiatry Treatment of Schizophrenia.pdf
  1982/
    1982 - A-01 Office Series-Stress [DVD01].mp4
    ...
  1995/
    1995 - Power vs Force.pdf
    1995 - Power vs. Force (Audiobook) [Audiobook].m4b
  2002-01/
    2002-01 - Causality The Ego's Foundation [DVD01].mp4
    2002-01 - Causality The Ego's Foundation [DVD02].mp4
    ...
  2004-02/
    2004-02 - Thought and Ideation [DVD01].mp4
```

Alternatively **Series folders** if you prefer thematic browsing, but Year folders directly solve "oh yeah lets watch that one lecture from 2004".

## Sample (first 60)

```
1973 - Orthomolecular Psychiatry Treatment of Schizophrenia.pdf
1982 - A-01 Office Series-Stress [DVD01].mp4
1982 - A-02 Office Series-Health [DVD01].mp4
1982 - A-03 Office Series-Spiritual First Aid [DVD01].mp4
1982 - A-04 Office Series-Sexuality [DVD01].mp4
1982 - A-05 Office Series-The Aging Process [DVD01].mp4
1982 - A-06 Office Series-Handling Major Crises [DVD01].mp4
1982 - A-07 Office Series-Worry Fear and Anxiety [DVD01].mp4
1982 - A-08 Office Series-Pain and Suffering [DVD01].mp4
1982 - A-09 Office Series-Losing Weight [DVD01].mp4
1982 - A-10 Office Series-Depression [DVD01].mp4
1982 - A-11 Office Series-Illness and Self-Healing [DVD01].mp4
1982 - A-12 Office Series-Alcoholism [DVD01].mp4
1982 - B-01 Office Series-Drug Addiction and Alcoholism [DVD01].mp4
1982 - B-03 Office Series-A Map Of Consciousness [DVD01].mp4
1982 - B-04 Office Series-Cancer [DVD01].mp4
1982 - B-06 Office Series-Death and Dying [DVD01].mp4
1995 - Power vs Force.pdf
1995 - Power vs. Force (Audiobook) [Audiobook].m4b
1995 - Power vs. Force Audio Book [Audiobook].m4b
1998 - Dialogues on Consciousness and Spirituality.pdf
1998 - Qualitative and Quantitative Analysis and Calibration of the Level of Human C.pdf
2001 - The Eye of the I.pdf
2001 - The Eye of the I (Audiobook) [Audiobook].m4b
2002-01 - Causality The Ego's Foundation [DVD01].mp4
2002-01 - Causality The Ego's Foundation [DVD02].mp4
2002-01 - Causality The Ego's Foundation [DVD03].mp4
2002-02 - Radical Subjectivity The 'I' of Self [DVD01].mp4
2002-02 - Radical Subjectivity The 'I' of Self [DVD02].mp4
2002-02 - Radical Subjectivity The 'I' of Self [DVD03].mp4
2002-03 - The Levels of Consciousness Subjective & Social Consequences [DVD01].mp4
2002-03 - The Levels of Consciousness Subjective & Social Consequences [DVD02].mp4
2002-03 - The Levels of Consciousness Subjective & Social Consequences [DVD03].mp4
2002-04 - Positionality and Duality Transcending the Opposites [DVD01].mp4
...
```

Full list: `data/filename_proposal_YYYYMM.csv` (358 rows) and `docs/filename-proposal.json` (same, JSON for frontend).

CSV columns: `uuid, work_id, item_type, series, year, month, format, format_detail, catalog_code, title, proposed_filename`

## Examples per your request

- Original cumbersome: `The Levels of Consciousness: Subjective & Social Consequences (Mar 2002) DVD01`
  → Proposed: `2002-03 - The Levels of Consciousness Subjective & Social Consequences [DVD01].mp4`

- Original easy: `Power vs Force.pdf`
  → Proposed: `1995 - Power vs Force.pdf` (year added for sortability, still easy)

- Lecture 2004: `Thought and Ideation (Feb 2004) DVD01`
  → Proposed: `2004-02 - Thought and Ideation [DVD01].mp4` — exactly `YYYY-02 - Name [DVD01].mp4` pattern you asked.

- Audiobook edition: `Power vs. Force (Audiobook)`
  → Proposed: `1995 - Power vs. Force (Audiobook) [Audiobook].m4b` — groups next to book edition.

- Discussion 2012: `What is Real Success? (2012)`
  → Proposed: `2012 - What is Real Success [DVD01].mp4`

- Office Visit 1982: `A-01 Office Series-Stress`
  → Proposed: `1982 - A-01 Office Series-Stress [DVD01].mp4` (keeps A-01 office prefix from raw title; could be cleaned further to `1982 - Stress [DVD01].mp4` if desired)

## Handling edge cases

- **No year (deferred untyped 246):** `0000 - In the World But Not of It - Audio [CD].mp3` — `0000` sorts first, clearly flagged as missing year.
- **Multi-part same title same month (Volume series, Presence, Verification):** `2007-03 - Volume II-Consciousness and Addiction [DVD01].mp4` vs `[DVD02].mp4` — disambiguated via generated DVD01/02/03 based on UUID order.
- **Long titles (academic):** truncated to 80 chars + `...` to keep filename ≤120 chars.
- **Illegal chars:** `:` `"` `?` etc stripped.

## Implementation steps (if approved)

1. Approve this CSV as reviewed input (`data/filename_proposal_YYYYMM.csv` is already generated, deterministic, 358 unique).
2. Add new generator `build_filename_pages.py` (similar to other generators) that validates uniqueness, illegal chars, max length, and writes `docs/filename-proposal.json` + `docs/filename-proposal-meta.json` + updates `build_catalogue_pages.py` to include new **Filenames** tab in frontend (shows proposed filename + copy button + sidecar JSON).
3. Add tests: uniqueness, no illegal chars, max length ≤120, extension matches format, all 358 master rows have filename.
4. Optional local organizer script `organize_files.py --profile YYYYMM --source ~/Downloads/Hawkins --dest ~/Hawkins --link hardlink` that reads CSV and creates hardlinks with proposed names + sidecar JSON.

## Comparison with prior proposal (which you marked trash)

| Prior proposal | This proposal |
|----------------|---------------|
| 3 profiles (canonical/human/plex), series abbr table, complex | Single profile only: `YYYY-MM - Name [DVD01].mp4` — exactly what you asked |
| Year-first OR series-first options, folder hierarchy options | Year-first only, simple |
| Short title with 5-7 words, 48 char cap, abbr mapping | Short title truncated to 80 chars, no abbr table, keeps original words |
| Edition detail logic complex (DVD01 only when multi-part) | Always includes [DVD01] for DVD even for single, matches your example |

## Open questions

- Do you want Office Series A-01 prefix stripped? Currently `1982 - A-01 Office Series-Stress [DVD01].mp4` keeps it. Alternative `1982 - Stress [DVD01].mp4` cleaner but loses office series context.
- For books, do you want year prefix? Current `1995 - Power vs Force.pdf` includes year for sortability, but you said `Power vs Force.pdf` is easy. Option: books without year prefix `Power vs Force.pdf` vs with year `1995 - Power vs Force.pdf`. Which do you prefer?
- For audiobooks, do you want `[Audiobook]` bracket or just extension `.m4b` distinguishes? Current includes bracket as you requested pattern.
- Max length 120 — OK or shorter 80?

## Files

- `data/filename_proposal_YYYYMM.csv` — 358 rows, reviewed, deterministic
- `docs/filename-proposal.json` — same for frontend
- This doc

*Generated 2026-08-04 by deterministic Python script from `data/research_master_draft.csv` 358 rows, no network.*
