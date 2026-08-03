# Title Hygiene Proposal — 56 records with raw file artifacts

**Prepared:** 2026-08-03
**Status:** ⏳ **Awaiting approval — no data changed.**
**Scope:** master display titles carrying filesystem artifacts, plus the 3 records
still untyped after IT-1.

---

## What I need from you

1. Approve the **normalization rule** in §2 (one rule, applied to 56 records).
2. Decide the **3 deferred records** in §5.
3. Rule on **one source discrepancy** in §4 that I will not auto-correct.

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

## 4. ⚠️ One source discrepancy — needs your ruling

Records **202** and **203** both point at the same official product,
`Volume I: Power vs. Force Muscle Testing`:

| ID | Raw title | Prefix says | Title text says |
|---:|---|---|---|
| 202 | `101 Volume I-Power vs Force (Part 1).mp4` | Vol **I**, part 01 | Volume **I** ✅ |
| 203 | `102 Volume II-David Hawkins -Applied Kinesiology-Power vs Force - Part 2.mp4` | Vol **I**, part 02 | Volume **II** ❌ |

The `102` prefix and the official product both say **Volume I**; only the title
text says Volume II. This looks like a source typo — but correcting a factual
claim is not title hygiene.

**My recommendation:** normalize 203's formatting only (leaving `Volume II` in the
text) and record the discrepancy as a note for a separate content decision.

## 5. The 3 deferred records

Now the only untyped records in the master.

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

### 264 — `26. "In the World But Not of It" –`

Truncated, trailing dash, no source URL. The official Media Miscellaneous page
lists **`"In the World But Not of It" – Audio`** (`in-the-world-but-not-of-it-cd`),
which is very likely this record.

**My recommendation:** normalize the title to `"In the World But Not of It"`, and
propose the official product URL as a **source override** (the existing reviewed
mechanism) rather than silently attaching it. Then it can be typed `lecture` with
the rest of Media Miscellaneous.

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
