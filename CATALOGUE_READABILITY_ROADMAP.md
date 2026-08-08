# Catalogue Readability & Consistency — Roadmap

**Date:** 2026-08-04
**Status:** Proposal for owner review — **no code/data changed yet**.
**Goal:** make the sheet an easy-to-scan overview of all Hawkins material, where
every field means one clear thing and the same thing everywhere.

---

## 1. What is inconsistent today (catalogued from the data)

### 1.1 `book` means three different things
- `item_type="book"` is a content class (38 records) — fine.
- `series="Books"` is a grouping (35 records) — collides with the content class.
- Audiobook **edition rows** are `item_type="book"` + `format="audio"` +
  `series="Books"` (e.g. *Power vs. Force (Audiobook)*, *The Eye of the I
  (Audiobook)*). So "an audiobook is typed as a book" — project-consistent by
  the edition model, but reads as "books" on screen.

### 1.2 `format` mixes carriers, media and content
Current values: `DVD` (254), `CD` (31), `book` (29), `audio` (24),
`streaming` (10), blank (8).
- `book` is used as a **carrier** for book records (odd — a book's carrier is
  paperback/hardcover/ebook).
- `audio` is a **medium**, not a carrier (an audiobook's carrier is an
  audiobook/audio-download).
So `format` is not a consistent vocabulary.

### 1.3 `series` is used inconsistently
- 37 records: `series="On The Road Talk Series"` (umbrella).
- 208 records: `series` = the **yearly** name (`The Way to God` 39,
  `Devotional Nonduality` 18, `Transcending the Mind` 20, `Nonduality
  Intensive` 32, `Transcending Levels of Consciousness` 26, `Spiritual Reality
  & Modern Man` 28, `Advanced Spiritual Awareness` 21, `In the World but Not
  of It` 12, `Practical Spirituality` 6, `Love & Spiritual Seeker Qualities`
  6).
- So the same umbrella series is split across an umbrella label *and* ten
  yearly labels — a reader can't tell if a talk's series is "On The Road" or
  "The Way to God".

### 1.4 Part numbering lives in three places
- In the **title**: `PART1` / `PART2` (e.g. *Become That Which You Are (June
  2004) PART1*), and `(Part 1)` / `(Part 2)` (e.g. *Volume I-Power vs Force
  (Part 1)*).
- In **`format_detail`**: `DVD01` / `DVD02` / `CD02` (239 records, e.g.
  *Causality: The Ego's Foundation* has `format_detail=DVD01`).
- In the **Edition column** (format · format_detail → `DVD · DVD01`).
So "Part" and "DVD" appear in some titles, not others; the same info also
lives in format_detail and the Edition column.

### 1.5 Title format noise
Titles carry `Volume I-`, `PART1`, `(Part 1)`, `-converted`, `.mp4`, etc. — a
lot of that is transcription/carrier noise that belongs in other fields.

---

## 2. Target model (the field semantics we want)

Four orthogonal concepts, each meaning one thing:

| Concept | Field | Rule |
|---|---|---|
| **What it is** | `item_type` | content class: `lecture`, `book`, `discussion`, `interview`, … |
| **Carrier / medium** | `format` | clean vocabulary: `DVD`, `CD`, `streaming`, `audiobook`, `paperback`, `hardcover`, `ebook` (drop `audio`, `book`) |
| **Edition of a work** | `work_id` + `format_detail` | which edition, and the disc/part (`DVD01`, `CD02`) |
| **Grouping** | `series` | the thematic/yearly series (one value per record; resolve umbrella) |

**Series decision (needs owner ruling):** make `series` the **yearly** series
name (what the reader actually searches), and stop using `On The Road Talk
Series` as a series value. If we want the umbrella visible, add it as a
**display-only** parent column rather than a series value.

**Books:** drop `series="Books"`. Books are grouped by `work_id` (already
present) and filtered via `item_type="book"`. Optionally introduce a
`publication_type` (hardcover/paperback/ebook/audiobook) instead of overloading
`format`.

---

## 3. Roadmap phases

### Phase 0 — Decide the target (owner, ~30 min)
1. Confirm the `format` vocabulary: `audio` → `audiobook`; `book` → the actual
   carrier (`paperback`/`hardcover`/`ebook`). Or keep a small set the UI maps.
2. Confirm `series` = yearly name, umbrella becomes display-only (or keep
   umbrella and add year as a column).
3. Confirm titles carry **no** part/disc/volume noise (all part info → `format_detail`).
4. Confirm audiobook rows stay `item_type="book"` but with `format="audiobook"`
   (clearer than `audio`).

### Phase 1 — Data model cleanup (code + reviewed inputs, ~medium)
- Update the controlled `format` vocabulary in `build_research_master.py` and
  the validators; migrate the data (`audio`→`audiobook`, `book`→carrier).
- Remove `series="Books"`; regroup books by `work_id` (data + docs).
- Normalize `series` to yearly names; move the On-the-Road umbrella to a
  display-only parent (add a mapping, not per-row edits).
- **Regression risk:** medium — touches `item_type`/`format`/`series`
  validators and counts; keep `--check` + doc-currency tests green.

### Phase 2 — Title hygiene (~medium)
- Strip `PART1`/`(Part 1)`/`DVD`/`CD`/`Volume I-`/`-converted`/`.mp4` from
  public titles; put the part in `format_detail`.
- Preserve verbatim raw text in `legacy_title` (already exists) so nothing is
  lost.
- Canonicalize volume-series titles (e.g. *Power vs Force (Part 1)* → *Power
  vs Force* with `series=Volume Series`, `format_detail=DVD01`).
- **Regression risk:** low–medium (display text only; `legacy_title` keeps the
  source).

### Phase 3 — Spreadsheet UI (`docs/app.js`) (~medium)
- One consistent **Edition** column: `format` · `format_detail` (e.g.
  `DVD · DVD01`, `Audiobook · Power vs. Force`). Never show `DVD` vs
  `DVD · DVD01` inconsistently.
- Make **series → work → part** the default grouping/sort (the "Series
  priority" change the owner suggested) so the sheet reads top-down: a series,
  then each work, then each disc.
- Add a **Medium/Carrier filter** (DVD / CD / Audiobook / Streaming /
  Paperback) built from the cleaned `format`.
- Add a **record-type badge** (Lecture / Book / Discussion) so content class is
  obvious without relying on the word "book".

### Phase 4 — Docs, tests, guards (~low)
- Update README / INSTRUCTIONS / schema docs and the doc-currency tests for
  the new vocabularies and counts.
- Add regression guards: `format` vocab is closed; no title carries part/disc
  noise; `series` uses the yearly names; audiobook rows use `format="audiobook"`.

---

## 4. Ordering and effort

| Phase | Effort | Risk | Depends on |
|---|---|---|---|
| 0. Decisions | — | — | — |
| 1. Data model | medium | medium | 0 |
| 2. Title hygiene | medium | low–medium | 0 |
| 3. UI | medium | low | 1, 2 |
| 4. Docs/tests | low | low | 1, 2 |

Do **Phase 0 first** — every later phase depends on the field-semantics rulings
(format vocabulary, series semantics, title rule, audiobook typing). Phase 1
and 2 can proceed in parallel after 0; Phase 3 (UI) should wait for the data
to be clean so the columns and filters match the new model.

## 5. Decisions I need from you
1. **`format` vocabulary** — OK to move `audio`→`audiobook` and `book`→
   `paperback`/`hardcover`/`ebook`?
2. **`series` semantics** — yearly name as the value, umbrella display-only?
3. **Titles** — OK to strip all `PART`/`(Part)`/`DVD`/`Volume`/transcoding
   noise from public titles (raw kept in `legacy_title`)?
4. **Audiobooks** — stay `item_type="book"` + `format="audiobook"` (clearer
   than `audio`)?
5. **Books grouping** — drop `series="Books"` and rely on `work_id` + a
   `item_type=book` filter?

> **Owner decisions (2026-08-04):**
> 1. **Format — minimal:** keep a small closed vocabulary; do NOT expand to
>    paperback/hardcover/ebook. Net set: `DVD`, `CD`, `streaming`, `book`,
>    `audiobook` (i.e. migrate the 24 `audio` → `audiobook`; keep `book`).
>    **✅ IMPLEMENTED 2026-08-04** (commit `2bc45c9`).
> 2. **Series — keep the umbrella:** `series` stays `On The Road Talk Series`
>    (and other umbrella values); the year lives in the existing `year` field.
>    Convert the 208 yearly-name records (`The Way to God`, `Devotional
>    Nonduality`, …) back to the umbrella series instead of the yearly names.
>    **⏳ DEFERRED** — pending a later session (collapsing drops the yearly
>    theme names; 10 edition rows have no year).
> 3. **Titles — strip noise only where it matches the official distributor
>    title** (e.g. the Veritas listing). Clean `PART`/`(Part)`/`DVD`/`Volume`/
>    transcoding noise from a public title **only when the cleaned form equals
>    the official listing title**; otherwise keep the current title.
>    **✅ IMPLEMENTED 2026-08-04** (commit `0fdce41`): 13 lecture titles
>    cleaned, raw kept in `legacy_title`, 5 inventory `matched_master_titles`
>    rows synced.
> 4. **Audiobooks:** keep `item_type="book"`, set `format="audiobook"`.
>    **✅ IMPLEMENTED 2026-08-04** (part of commit `2bc45c9`).
> 5. **Books grouping:** keep `series="Books"` (do not drop it).
>    **✅ DECIDED** (no change needed).

The pipeline is green (113 tests, 91% coverage, six curated `--check` modes; this snapshot is dated — see `AUDIT_2026-08-08.md` for current state).
