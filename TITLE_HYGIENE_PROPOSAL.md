# Title Hygiene Proposal — 56 records with raw file artifacts

**Prepared:** 2026-08-03
**Status:** ✅ **Applied 2026-08-03.** The generated master now exposes a verbatim
`legacy_title` column and applies the owner-approved cleanup, with DVD/CD/PART
designators retained in the public title. The decision draft below is retained as
research history; its earlier proposal to move PART/A-series identifiers into
`format_detail` was **not** adopted.
**Scope (historical, 308-record draft):** master display titles carrying
filesystem artifacts. The two note-only placeholders discussed below were
separately excluded, leaving one untyped record. The cleanup now applies to
all **317** current master records; `legacy_title` preserves the verbatim raw
strings.

---

## What I need from you

1. Approve the **normalization rule** in §2 — you asked to discuss this first, so
   the specific questions are in §2a.
2. Confirm the **264/265 split-text fix** in §5 (you chose "handle 264 only").
3. Confirm the **record 203 correction** in §4 — investigated as you asked, and
   now conclusively resolved as a source typo.

**Investigation results since v1:** both flagged items turned out to be real,
provable source defects rather than judgement calls. Details in §4 and §5.

---

## 1. The problem

56 of 308 public catalogue titles are raw filenames, not titles:

| Artifact | Records | Example |
|---|---:|---|
| `.mp4` extension | 55 | `Devotion to Truth.mp4` |
| `PART1`/`PART2`/`(Part 1)` suffix | 27 | `Spiritual Will PART1.mp4` |
| `A-01`…`B-06` prefix | 16 | `A-01 Office Series-Stress.mp4` |
| Leading sequence number | 14 | `101 Volume I-Power vs Force…` |
| `-converted` transcode marker | 4 | `…of Consciousness-converted.mp4` |
| Trailing dash / whitespace | 1 | `26. "In the World But Not of It" – ` |

These are the *public* titles on a published catalogue. They also leak the
redundant string `Office Series-` into 16 titles that already have
`series = Office Series`.

## 2a. Open questions on the rule (you asked to discuss)

Before I apply anything, the three judgement calls embedded in the rule:

**Q1 — Should `A-01`…`B-06` leave the title?**
`A-01 Office Series-Stress.mp4` → title `Stress`, `format_detail` `A-01`.
Cleaner, and mirrors how `DVD01` was handled for lectures. But if you use those
codes to identify Office Series items at a glance, keeping them in the title is
defensible. *(16 records)*

**Q2 — Should the `Volume N-` prefix stay in Volume Series titles?**
I propose keeping it: `Volume I-Power vs Force`. It is part of the work's name,
not a filename artifact — the publisher titles them `Volume I: Power vs. Force…`
too. I only strip the numeric `101`/`102` disc prefix. *(13 records)*

**Q3 — Should `format_detail` hold `PART1` or `DVD01`-style values?**
Existing lecture records use `DVD01`. These records have no confirmed medium, so
I propose the neutral `PART1`, matching their own raw strings. Switching to
`DVD01` would assert a medium we have not evidenced. *(27 records)*

## 2. Proposed rule — follow the existing precedent exactly

The project already solved this for the 198 lecture records. `title_for()` in
`build_research_master.py` strips `(Mon YYYY) DVDnn` from LS-prefixed rows, keeping:

| Field | Holds | Example |
|---|---|---|
| `title` | clean display title | `Causality: The Ego's Foundation` |
| `title_source` | **verbatim raw string** | `Causality: The Ego's Foundation (Jan 2002) DVD01` |
| `format_detail` | the part designator | `DVD01` |

**Display titles are intentionally duplicated across parts** — three DVDs of one
lecture share one title and differ in `format_detail`. That is the established
model, and I propose extending it rather than inventing a new one.

### The normalization, in order

1. Strip trailing `.mp4`
2. Strip trailing `-converted` / `- converted`
3. Extract trailing `PART n` / `(Part n)` → `format_detail`
4. Extract leading `A-01`…`B-06` → `format_detail`
5. Strip leading sequence numbers (`101 `, `26. `)
6. Strip redundant leading `Office Series-`
7. Strip trailing dashes; collapse double spaces

**Nothing is discarded.** Every original string is preserved verbatim in
`title_source`, which is already exposed in the UI and in every CSV export.

### Result

- **56** display titles cleaned
- **43** gain a `format_detail` (27 `PARTn`, 16 `A-01`-style)
- **0** titles become empty
- **0** records lose information

Sample:

| ID | Before | After | `format_detail` |
|---:|---|---|---|
| 233 | `A-01 Office Series-Stress.mp4` | `Stress` | `A-01` |
| 228 | `Spiritual Will PART1.mp4` | `Spiritual Will` | `PART1` |
| 213 | `601 Volume VI-How to Raise Your Level of Consciousness-converted.mp4` | `Volume VI-How to Raise Your Level of Consciousness` | — |
| 285 | `What You are Changes the World.mp4` | `What You are Changes the World` | — |

## 3. What I am deliberately NOT doing

**Not adopting official product titles as display titles.** Our record 233 would
become `Stress`; the official product is also `Stress`. But elsewhere they diverge
(`Volume VI-How to Raise…` vs official `Volume VI: How to Raise…`). Replacing our
titles wholesale with publisher titles is a *different* decision about title
authority, and it would discard the archive's own naming. I'm only removing
filesystem noise.

**Not populating `format`.** Still no format evidence in the raw sheet. `format_detail`
here records a *part designator*, which is present in the raw string itself.

## 4. ✅ RESOLVED — record 203 is a confirmed source typo

You asked me to investigate rather than guess. I did, and the publisher's product
data settles it conclusively.

**Evidence from `volume-i-power-vs-force-muscle-testing-video`:**

| Field | Value | Significance |
|---|---|---|
| Title | Volume I: Power vs. Force Muscle Testing | |
| SKU | `vs_v1pvf_dvd` | **`v1`** = Volume 1 |
| Product details | **"Two DVD Set"**, 3h 4m | Exactly two discs — matches our two records |
| Description | "extensively demonstrates the technique of **kinesiology**" | Matches 203's "Applied Kinesiology" text |

**Evidence from the Volume Series index:** the real Volume II is
*"Consciousness and Addiction"* — an entirely different subject, which we already
hold separately as records **204** and **205**.

### Conclusion

| Record | Raw title | Actually is |
|---:|---|---|
| 202 | `101 Volume I-Power vs Force (Part 1)` | Volume I, disc 1 |
| 203 | `102 Volume II-David Hawkins -Applied Kinesiology-Power vs Force - Part 2` | **Volume I, disc 2** |

Three independent signals agree that 203 is Volume I disc 2: the `102` prefix
(Vol 1, disc 2), the official two-disc product it links to, and its own
"Applied Kinesiology-Power vs Force" subject matter. Only the string
"Volume II" disagrees — and Volume II is demonstrably a different work we hold
elsewhere.

**"Volume II" in record 203 is a confirmed transcription error for Volume I.**

### Recommendation

Correct the display title to `Volume I-David Hawkins -Applied
Kinesiology-Power vs Force`, with:

- the verbatim original preserved in `title_source` (nothing is lost),
- `format_detail` = `PART2`,
- a `notes` entry recording the correction and its evidence.

This is a **content correction**, distinct from the formatting rule in §2, so it
is recorded as its own decision even though both land in the same pass.

## 5. The 3 deferred records

Now the only untyped records in the master.

### 246 and 249 — deferred at your instruction

You chose "handle 264 only", so these two stay exactly as they are for now. The
analysis below is retained for when you want to revisit them.

### 246 — `where is B-02? might not exist.` and 249 — `where is B-05? might not exist.`

Not titles — unresolved research questions. No source URL, no official product.
The Office Series runs A-01…A-12, B-01, B-03, B-04, B-06 — B-02 and B-05 are
genuinely absent from the publisher's catalogue.

**Options:**

- **(a) Move to exclusions** *(my recommendation)* — they are provenance notes, not
  holdings. `research_master_exclusions.csv` exists precisely for raw rows that
  aren't master items. Master would become **306 records, 306 typed, 0 untyped**.
- **(b) Keep and retitle** as `Office Series B-02 (existence unverified)` with a note.
- **(c) Leave as-is.**

### 264 — ✅ SOLVED: a split-text defect spanning two raw rows

The truncation is not random. The raw rows read:

```
row 296:  '26. "In the World But Not of It" – '     ← ends with a dangling dash
row 297:  'Audio 27. Golden Word Book Signing – Audio'  ← STARTS with "Audio"
```

That leading `Audio` on row 297 is **the tail of item 26**, not part of item 27.
The official Media Miscellaneous catalogue contains exactly two matching products,
which confirms the reconstruction:

| Item | Correct title | Official product | SKU |
|---|---|---|---|
| 26 | `"In the World But Not of It" – Audio` | `in-the-world-but-not-of-it-cd` | `am_itwbnoi` |
| 27 | `Golden Word Book Signing – Audio` | `https-veritaspub-com-…-january-13-2007` | `am_gwbs` |

So a value split across two spreadsheet cells was migrated as two separate
fragments. Record **264** lost its `Audio` suffix; record **265** gained a spurious
`Audio ` prefix.

**Recommendation:**

- **264** → title `"In the World But Not of It" – Audio`; propose
  `in-the-world-but-not-of-it-cd` as a reviewed **source override** (not a silent
  attachment); then it types as `lecture` with the rest of Media Miscellaneous.
- **265** → strip the leading `Audio ` fragment → `Golden Word Book Signing – Audio`.

Both raw strings stay verbatim in `title_source`, so the defect remains visible.

> Note: the official page shows this is a **Nightingale-Conant** 6-CD set sold
> through Veritas. `source_url_nightingale_conant` is currently empty on all 308
> records — worth revisiting in a later provenance pass.

## 6. Verified side effects

| Measure | Effect |
|---|---|
| Master IDs | unchanged (keyed to raw row) |
| `catalog_code` | unchanged (derived from type+year, not title) |
| Relationships | unchanged (keyed by master ID) |
| Series compilations | **must re-verify** — `validate_series_compilations()` counts *distinct titles*, so collapsing part-titles could change counts. The 7 compilations target only LS lecture series, which are already canonicalized, so no impact is expected — but the build will prove it. |
| `title_source` | populated on 56 records (was 1) |

## 7. Implementation

Extend `title_for()` in `build_research_master.py` with the rule above, so
normalization is **generated and reproducible** rather than hand-edited into the
ledger — consistent with how the LS titles are handled.
