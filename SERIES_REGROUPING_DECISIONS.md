# Series Regrouping Decisions

**Updated:** 2026-08-03
**Input changed:** `migration_review_ledger.csv` (`proposed_series` only)
**Scope:** correcting master records filed under the wrong `series` value.

This document records reviewed series reassignments. A series value is a
catalogue-structure claim, so it must be backed by the publisher's own grouping
or by explicit raw-source structure — never by title resemblance alone.

---

## Decision SR-1 — 12 records: `Media Miscellaneous` → `On The Road Talk Series`

**Decided:** 2026-08-03
**Status:** approved
**Records:** master IDs 266–277 (raw rows 300–311)

### Affected records

| Master ID | Raw row | Title | Official product slug |
|---:|---:|---|---|
| 266 | 300 | All is Divinity | `all-is-divinity` |
| 267 | 301 | Compassion: The Pathway of the Heart | `compassion-the-pathway-of-the-heart` |
| 268 | 302 | God is Hidden Within the Beauty of the Music | `god-is-hidden-within-the-beauty-of-the-music` |
| 269 | 303 | God is The Infinite Field | `god-is-the-infinite-field` |
| 270 | 304 | Spiritual Reality | `spiritual-reality-3-cd-set` |
| 271 | 305 | The Ever-Present Joy | `the-ever-present-joy` |
| 272 | 306 | The Power of Devotion | `the-power-of-devotion` |
| 273 | 307 | The Prevailing Silence | `prevailing-silence-3-cd-set` |
| 274 | 308 | Transcending the Ego | `transcending-the-ego` |
| 275 | 309 | Truth Shines Forth | `truth-shines-forth-3-cd-set` |
| 276 | 310 | Virtues: The Spiritual Foundation | `virtues-the-spiritual-foundation` |
| 277 | 311 | You Are the Light of Consciousness | `you-are-light-consciousness` |

### Evidence

**1. Publisher taxonomy (primary).** The official Veritas product category
`https://veritaspub.com/product-category/on-the-road-talk-series/` reports
*"Showing all 21 results"*, and **all 12 products above appear in it**. Individual
product pages state the category explicitly:

- *All is Divinity* — `Category: On the Road - Talk Series`, `SKU: cd_aid`
- *The Ever-Present Joy* — `Category: On the Road - Talk Series`, `SKU: cd_otr_ej`
  (the `otr` infix is the publisher's own On-The-Road abbreviation)

Before this change, that single official category was split across two of our
series values: 14 records under `On The Road Talk Series` and these 12 under
`Media Miscellaneous`.

**2. Raw-source structure (corroborating).** In the source spreadsheet these rows
sit under an explicit `Missing OTR` note:

```
row 294  series_context : "Media Miscellaneous: https://veritaspub.com/media-miscellaneous-2/"
row 295  research_note  : "❌❌ MOST ARE MISSING ❌❌ NOT YET IN THE SPREADSHEET ❌❌"
row 296  item           : 26. "In the World But Not of It" –          ← stays Media Misc
row 297  item           : Audio 27. Golden Word Book Signing – Audio  ← stays Media Misc
row 298  blank_separator
row 299  research_note  : "Missing OTR"                               ← section boundary
rows 300–311  items     : All is Divinity … You Are the Light of Consciousness
```

**3. Product family coherence (corroborating).** All 12 published 2014-01-01 →
2014-01-27 (one 2022 reissue), all `owned=false`, consistent with "missing".

### Root cause

The migration classified the `Missing OTR` marker at raw row 299 as a
`research_note` rather than a `series_context` heading. Series assignment carries
forward from the last `series_context` row, so these 12 records inherited
`Media Miscellaneous` from row 294 instead of opening a new section.

**The raw spreadsheet was correct.** This is a migration defect, not a source
error.

### Records deliberately NOT moved

| Master ID | Title | Why it stays |
|---:|---|---|
| 264 | `26. "In the World But Not of It" –` | Above the `Missing OTR` boundary; no product link; truncated title pending the hygiene pass |
| 265 | Golden Word Book Signing – Audio | Official page states `Category: Media Miscellaneous`, `SKU: am_gwbs` |

### Effect

| Series | Before | After |
|---|---:|---:|
| Media Miscellaneous | 14 | 2 |
| On The Road Talk Series | 18 | 30 |

No master IDs, catalogue codes, source URLs, relationships, or ownership values
change. `series` is not an input to compact-ID assignment or code generation.

### Not changed by this decision

`item_type` for these records remains empty; it is handled separately in
`ITEM_TYPE_CLASSIFICATION_PROPOSAL.md` (decision D7 → `audio`). Series membership
and content type are independent claims and are recorded as independent decisions.

---

## Decision IT-1 — classify the 87 untyped records by content class

**Decided:** 2026-08-03
**Status:** applied
**Input changed:** `migration_review_ledger.csv` (`proposed_item_type` on 84 rows)
**Full analysis:** `ITEM_TYPE_CLASSIFICATION_PROPOSAL.md` (v3)

### Governing rule (now enforced in code)

> **`item_type` records what a record *is* (content class).
> `format` records the carrier it arrives on.**

Established by existing precedent: 198 DVD lecture recordings are
`item_type='lecture'` with `format='DVD'` — they are *not* typed `video`.

### Assignments

| Series | Records | `item_type` |
|---|---:|---|
| Love & Spiritual Seeker Qualities | 3 | `lecture` |
| Volume Series | 13 | `lecture` |
| On The Road Talk Series | 30 | `lecture` |
| Office Series | 16 | `lecture` |
| Satsang Series | 13 | `lecture` |
| Media Miscellaneous (265) | 1 | `lecture` |
| Discussion Series | 8 | **`discussion`** |
| Deferred (246, 249, 264) | 3 | *(none)* |

`format` was deliberately left blank: the raw spreadsheet holds no format data for
any of these records, and SKU/slug hints are partial and inconsistent.

### Vocabulary change

Added **`discussion`** to the controlled vocabulary. The Discussion Series is a
two-party dialogue — the official page for *What is Meant by Spiritual (2012)*
states *"Dr. Hawkins **and his wife Susan** explore…"* and the raw sheet names it
*"Discussion Series with Dr. David Hawkins & Wife Susan"*. `interview` was rejected
as misleading (Susan is a co-participant, not an interviewer) and `lecture` as
inaccurate for a dialogue.

The vocabulary is now split explicitly in `build_research_master.py`:

- `CONTENT_ITEM_TYPES` — the supported content classes, including `discussion`.
- `DEPRECATED_MEDIUM_ITEM_TYPES` — `audio` and `video`, retained only for backward
  compatibility. They describe a medium, not a content class, and must not be used
  for new classifications.

### New guard

`proposed_item_type` in the ledger was previously **unvalidated** — a typo would
have silently produced a stray catalogue-code prefix. The builder now fails with
the offending raw row and the list of allowed values.

### Effect

| Measure | Before | After |
|---|---:|---:|
| Records with `item_type` | 221 | **305** |
| `lecture` / `book` / `discussion` | 198 / 23 / 0 | **274 / 23 / 8** |
| Catalogue codes | 198 | **221** |
| Existing codes changed | — | **0** |

The 23 new codes are all `LECTURE-YYYY-NNN`, appending to existing year sequences.
No master IDs, relationships, source URLs, or ownership values changed.
