# Hawkins Archive Spreadsheet — Content & Data Quality Audit

**Audited file:** `hawkins archive clone - Sheet1.csv`  
**Audit date:** 2026-08-03  
**Method:** Static inspection of the CSV structure and values only. Links were checked for shape and host consistency; this audit does **not** assert that remote links resolve or that availability claims are accurate.

## Executive summary

The spreadsheet is an inventory/worklist for David R. Hawkins material, dominated by 2002–2011 lecture-series DVDs and supplemented with volume, office-visit, satsang, media, book, transcription, highlight, dissertation, and miscellaneous entries. It contains useful cataloguing progress and 225 product links, but it is not yet a clean relational catalogue: it mixes records, section headings, source URLs, notes, and 31 blank separator rows in the same table; it has an empty primary-ID column; and six of its thirteen exported columns have no usable structured content.

The public site currently exposes all **374 CSV data rows**, including blank rows and non-record headings, rather than a curated set of catalogue records.

## 1. File structure and inventory

| Measure | Result | Interpretation |
|---|---:|---|
| Physical CSV rows | 376 | Includes a title row, header row, and 374 rows read as data by the pipeline. |
| Columns | 13 | The real header is on CSV line 2; the pipeline correctly skips the title row. |
| Data rows published | 374 | Matches `docs/data.json`. |
| Entirely blank data rows | 31 | Visual separators that become empty table records. |
| Non-blank rows | 343 | Includes both actual items and hierarchy/section/note rows. |
| `uuid` values | 0 | The intended primary-key field is wholly unpopulated. |
| Titles present | 343 | Every non-blank row has a title-like value. |
| Unique non-empty titles | 342 | One title is duplicated. |

### Current exported schema

| CSV position | Current public JSON field | Populated rows | Assessment |
|---|---|---:|---|
| 1 | `uuid` | 0 | Empty primary-key column; should be removed or populated. |
| 2 | `tempid` | 245 | Main working identifier, but mixed formats and duplicates exist. |
| 3 | `title` | 343 | Semantically overloaded: item names, section headings, notes, and URLs. |
| 4 | `WE HAVE?` | 312 | Useful availability status, currently emoji-based. |
| 5 | `original source` | 311 | Source/provenance field, mostly `veritas`. |
| 6 | `Unnamed: 5` | 2 | Unnamed notes column; not a usable public field. |
| 7 | `format` | 1 | Structurally misused: the only value is a Discord URL, not a format. |
| 8 | `product link` | 225 | Most complete link field. |
| 9–11 | `Unnamed: 8`–`Unnamed: 10` | 0 | Entirely empty columns. |
| 12 | `Unnamed: 11` | 1 | A single Archive.org URL in an unnamed field. |
| 13 | `other links` | 0 | Entirely empty named column. |

**Schema conclusion:** `uuid`, `Unnamed: 8`, `Unnamed: 9`, `Unnamed: 10`, and `other links` are empty; `format` and the remaining unnamed columns need remediation before they can support meaningful filtering or presentation.

## 2. What the collection contains

The sheet has a clear source hierarchy but encodes it as regular rows rather than metadata.

### Primary lecture collection

- A landing-page URL introduces the **2002–2011 lecture series**.
- The lecture sequence has named annual sections:
  - 2002 — *The Way to God*
  - 2003 — *Devotional Nonduality*
  - 2004 — *Transcending the Mind*
  - 2005 — *Nonduality Intensive*
  - 2006 — *Transcending Levels of Consciousness*
  - 2007 — *Spiritual Reality & Modern Man*
  - 2008 — *Advanced Spiritual Awareness*
  - 2009 — *In the World but Not of It*
  - 2010 — *Practical Spirituality*
  - 2011 — *Love & Spiritual Seeker Qualities*
- Most lecture records use `LSYYYYMM_part` IDs. There are **198** such IDs.
- Within those IDs, the years represented are: 2002 (36), 2003 (18), 2004 (18), 2005 (30), 2006 (24), 2007 (27), 2008 (21), 2009 (12), 2010 (6), and 2011 (9). These counts are ID rows, not necessarily unique lectures; a lecture’s DVD parts commonly share one product link.

### Supplementary collection groups

The later sheet includes:

- **Volume series** — 13 `VOL` identifiers.
- **On The Road / talk series** — includes a prominent “most are missing” note and individual media titles.
- **Office series** — 18 `OFF` identifiers.
- **Satsang / question-and-answer material** — 3 `SAT` identifiers plus entries using a repeated informal identifier.
- **Media miscellaneous**, **discussion series**, **books**, **transcription-series books**, **Scott Jeffrey edited books**, **lecture highlights**, **dissertation**, **Dialogues on Consciousness and Spirituality**, and other miscellaneous/non-Veritas material.

This is valuable content coverage, but these groups should become a `collection` or `series` field rather than being inferred from adjacent display rows.

## 3. Availability and provenance

### Availability (`WE HAVE?`)

| Value | Rows | Share of all 374 rows | Share of marked rows |
|---|---:|---:|---:|
| ✅ | 283 | 75.7% | 90.7% |
| ❌ | 29 | 7.8% | 9.3% |
| Blank | 62 | 16.6% | — |

The 62 blank statuses comprise the 31 blank separator rows and unmarked headings/notes or catalogue entries. For an accurate public collection metric, blank and non-record rows must first be classified; the present “✅” count should not be presented as a verified holdings total without that qualification.

### Original source

| Value | Rows |
|---|---:|
| `veritas` | 298 |
| `veritas/only sold via audible` | 13 |
| Blank | 63 |

Availability and source mostly align: 282 rows are `veritas` + ✅, 16 are `veritas` + ❌, and all 13 “only sold via audible” records are ❌. One ✅ row has no source. The data should separate **publisher/source** (`Veritas`) from **commercial availability channel** (`Audible`, direct product page, etc.).

## 4. Identifiers and uniqueness

- `tempid` is populated for **245** rows but contains **233 distinct non-empty values**.
- The only duplicated identifier is the literal **`2cds each?`**, repeated across **13** rows (12 duplicate occurrences beyond the first). This is a note, not an identifier, and prevents reliable row-level joins or deduplication.
- Identifier families are: `LS` (198), `OFF` (18), `VOL` (13), `SAT` (3), and 13 informal/nonconforming values.
- `uuid` is empty throughout, so the site has no durable primary key.

**Risk:** Edits, imports, deduplication, and future API work cannot safely identify every record. A stable ID should be assigned to every true item, while human notes are moved to a note field.

## 5. Links audit

### Product links

- **225** product-link cells are populated.
- They reference **80 unique URLs**.
- All validly shaped product links use `veritaspub.com`.
- Repetition is largely expected: many lecture product pages are shared by 2–3 disc/part rows.
- **34 rows with a `tempid` have no product link**, representing a defined backfill queue.

### Detected malformed product links

Three rows share this malformed value:

```text
https://veritaspub.com/product/https://veritaspub.com/product/2002-08-advaita-the-way-to-god-through-mind/
```

It contains the product URL prefix twice and should be corrected before visitors use it.

### Links in the wrong fields

- Four title cells are standalone URLs rather than titles.
- Several title cells append a URL to a section title (for example, a collection heading followed by a Veritas URL).
- `format` contains one Discord URL, not a media-format value.
- `Unnamed: 11` contains one Archive.org URL.
- `other links` contains no data despite its intended purpose.

**Risk:** Link rendering is inconsistent. The current UI identifies a column as URL-heavy, so isolated URLs embedded in the title and unnamed fields are less discoverable than `product link` values.

## 6. Record-type contamination

The table presently combines multiple concepts:

1. **Catalogue items** — lectures, DVDs/parts, books, etc.
2. **Section headers** — e.g., annual series or material-category headings.
3. **Source/landing links** — e.g., collection pages.
4. **Editorial notes and gap markers** — e.g., “MOST ARE MISSING”, “Missing books?”, and research reminders.
5. **Blank separator rows** — 31 rows.

This explains why `title` has high completeness but is not a clean item-title field, why status is incomplete, and why ID coverage is only 65.5% of published rows. It also means a visitor cannot distinguish a material record from navigation/context without reading the text.

## 7. Priority data-quality issues

### Critical

1. **Automation defect outside the CSV:** `.github/workflows/update_spreadsheet.yml` still commits `public/data.json` and `public/meta.json`, while the live site and pipeline use `docs/`. Source changes therefore may not refresh the published data.
2. **No stable primary key:** `uuid` is entirely empty, and `tempid` has informal and duplicated values.
3. **Mixed record types in one table:** 31 blank rows plus headers/notes are published as records.

### High

4. **Broken product URL:** the August 2002 Advaita URL has a duplicated prefix in three rows.
5. **Weak schema:** six columns are empty or effectively unstructured; values are misplaced in unnamed columns and `format`.
6. **Unmodelled availability:** emoji status and “only sold via audible” source text conflate possession, product availability, source, and channel.

### Medium

7. **Missing product links:** 34 identified records have no product link.
8. **Links and titles are mixed:** collection pages and raw URLs are embedded in `title` instead of linked metadata.
9. **No collection/series metadata:** grouping relies on row order and headings, which cannot be reliably sorted or filtered.

## 8. Recommended target model

Retain the raw CSV unchanged as source evidence, but generate a clean public dataset with fields such as:

| Field | Purpose |
|---|---|
| `id` | Required immutable unique record ID. |
| `record_type` | `item`, `section`, `note`, or `source_link`; public item view should default to `item`. |
| `title` | Clean human-readable item title only. |
| `collection` / `series` | E.g., Lecture Series, Volume Series, Office Series, Books. |
| `year`, `month`, `part_number` | Parsed where possible from lecture IDs/titles. |
| `media_type` / `format` | DVD, audio, book, transcript, etc.; never a URL. |
| `held_status` | Controlled value such as `held`, `missing`, `unknown`. |
| `source` | Controlled publisher/provenance value. |
| `purchase_channel` | Veritas, Audible, etc., separate from source. |
| `product_url` | Validated canonical URL. |
| `alternate_urls` | Array for Archive.org, Discord, Goodreads, and other links. |
| `notes` | Editorial/research text, not an ID. |

## 9. Recommended delivery plan

1. **Fix the workflow output path** so rebuilt JSON is committed to `docs/`.
2. **Preserve the raw CSV** and add transformations rather than destructively editing historical source rows.
3. **Classify rows** into `item`, `section`, `note`, and blank; default the site to catalogue items and offer context separately.
4. **Remove or map empty/unnamed columns** and relocate the two notes plus the Archive.org/Discord URLs to named fields.
5. **Assign IDs** to all true items; replace `2cds each?` with a note and unique item IDs.
6. **Correct and validate URLs** (first the known duplicated-prefix link, then an optional network link checker).
7. **Normalize availability/source/channel** into controlled fields and calculate holdings statistics from true item records only.
8. **Backfill the 34 identified items missing product links**, prioritizing records marked as held or currently for sale.
9. **Enhance the UI after cleanup** with collection, availability, year, and media-type filters rather than displaying raw spreadsheet artifacts.

## Audit limitations

- This is a structural and content audit of the repository’s CSV as of the audit date.
- It does not verify ownership, copyright, remote link availability, duplicate intellectual works across differently named rows, or metadata correctness beyond clear structural anomalies.
- “We have” is treated as the sheet author’s label, not independently validated inventory evidence.
