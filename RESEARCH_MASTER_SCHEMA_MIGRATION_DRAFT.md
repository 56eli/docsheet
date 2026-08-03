# Research Master Schema & Migration Map — Draft

**Status:** Proposal only; no source rows, public JSON, or UI behavior are changed by this document.  
**Basis:** Approved catalogue vision and the CSV audit dated 2026-08-03.  
**Source preservation rule:** `hawkins archive clone - Sheet1.csv` remains immutable raw evidence. A new curated dataset is generated from it only after this proposal is approved.

## 1. Approved design decisions captured here

- Scope: all Hawkins-related material, including authorized derivatives, edited/transcribed/compiled and posthumous material.
- Catalogue shape: flat public records; every disc, file, or part is a separate top-level item.
- Identity: each item receives an compact numeric master ID plus a readable `TYPE-YEAR-SEQUENCE` catalogue code; current `tempid` stays as a legacy reference only.
- Metadata: canonical title; core tags for type, series, year, and format; per-part ownership; item-to-series grouping only.
- Editions: make a separate item only where content changes.
- Sources: retain separate official-source URL columns; approved starting sources are Veritas, Hay House, Nightingale-Conant, and Audible.
- Locations and links: all current personal-reference locations and URLs are public under the current policy.
- Missing confirmed works remain catalogue records. Unresolved metadata is blank rather than replaced by an `Unknown` label.
- Governance: AI may prepare research/change drafts, but a human approves changes. Source rechecking is manual.

## 2. Curated item schema (v1)

This is a flat **item** table. It contains true catalogue items only; hierarchy labels, editorial notes, landing-page links, and blank rows stay in the raw source or a migration review ledger rather than becoming public items.

| Field | Required | Format / controlled values | Purpose and migration rule |
|---|---|---|---|
| `uuid` | Yes | Compact numeric master ID, 1..10000 | Permanent technical ID, created once for each approved item. The field name is retained for compatibility. |
| `catalog_code` | Yes | `TYPE-YEAR-SEQUENCE` | Readable unique item ID, for example `LECTURE-2002-001` or `BOOK-2011-001`. Sequence is per item; because discs/files are top-level items, each gets its own code. |
| `legacy_tempid` | No | Raw text | Preserves current `tempid`; it is not unique enough to become the primary key. |
| `title` | Yes | Canonical human-readable title | Normalized canonical title. Do not place collection URLs or editorial notes here. |
| `title_source` | No | Raw text | Optional original title text when canonicalization materially changes wording. |
| `item_type` | Yes | Controlled: `lecture`, `book`, `audio`, `video`, `transcript`, `interview`, `highlight`, `dissertation`, `article`, `other` | Flat discovery type. The initial controlled vocabulary can expand only by approval. |
| `series` | No | Canonical text | Flat group tag, e.g. `The Way to God`, `Volume Series`, `Office Series`; no parent/child data model. |
| `year` | No | Four-digit year | Release, recording, or lecture year, documented by the item’s evidence. |
| `month` | No | `01`–`12` | Retained only where a date is reliably known. |
| `format` | No | Controlled: `DVD`, `CD`, `audio`, `book` | Initial approved format vocabulary. Preserve finer wording in `format_detail` rather than inventing a value. |
| `format_detail` | No | Text | Examples: `DVD01`, `MP3`, `paperback`, or `6 CD set`. |
| `owned` | No | `true`, `false`, blank | Per-item/part ownership. Current ✅ maps to `true`, ❌ to `false`, and blank remains blank. |
| `location_physical` | No | Public text/URL | Exact shelf/container or physical reference, if supplied. |
| `location_digital` | No | Public text/URL | Exact local/cloud file reference, if supplied. |
| `location_streaming` | No | Public text/URL | Streaming/account/reference location, if supplied. |
| `source_url_veritas` | No | HTTPS URL | Official Veritas item page. |
| `source_url_hay_house` | No | HTTPS URL | Official Hay House item page. |
| `source_url_nightingale_conant` | No | HTTPS URL | Official Nightingale-Conant item page. |
| `source_url_audible` | No | HTTPS URL | Audible item page or author catalogue entry. Audible is a platform, not a publisher. |
| `reference_url_1` | No | URL | Public non-core reference such as an archive, bibliographic, or research page. |
| `reference_url_2` | No | URL | A second public reference when needed. More repeatable references require a later schema decision. |
| `notes` | No | Text | Human research note; never an identifier or title. |

### Deliberate exclusions from v1

- No `record_type` column in the curated table: non-item rows are excluded rather than published with a type label.
- No artificial `unknown` values: unresolved fields stay blank.
- No separate work/edition/copy hierarchy: every disc/file/part is its own flat record, as approved.
- No dedicated columns yet for known-but-not-approved publishers. When approved, each source can gain a named `source_url_<publisher>` column through a versioned schema change.

## 3. Raw CSV → curated schema map

| Current raw field / row form | Current condition | Proposed curated destination | Rule / approval need |
|---|---|---|---|
| `uuid` | Empty in all 374 rows | `uuid` | Generate compact numeric IDs only for approved true-item rows. |
| `tempid` | 245 populated; 233 distinct; `2cds each?` repeated 13 times | `legacy_tempid` | Preserve raw value. Do not use placeholder/note values as IDs. |
| `title` | Mixes item titles, section headings, notes, and URLs | `title`, `series`, `notes`, or migration ledger | Manual/approved classification required before output. Canonical item titles go to `title`; headings yield a `series` tag for associated items; notes/URLs do not become item titles. |
| `WE HAVE?` | ✅, ❌, blank | `owned` | ✅ → `true`; ❌ → `false`; blank → blank. Apply only to true items. |
| `original source` | Mostly `veritas`; 13 `veritas/only sold via audible` | Source URL columns and `notes` | Do not map source labels directly to a single URL. Resolve item pages using the approved source registry. Preserve channel wording in `notes` until normalized. |
| `Unnamed: 5` | Two notes | `notes` | Move note text to `notes` after item association is approved. |
| `format` | 373 blank; one Discord URL | `format` / `reference_url_*` | Do not treat the Discord URL as format. Leave format blank until known; place the URL in a public reference field only after row association is reviewed. |
| `product link` | 225 Veritas URLs; 80 unique; one malformed URL repeated three times | `source_url_veritas` | Map valid Veritas URLs. Quarantine the duplicated-prefix URL for correction/research; never silently repair it. |
| `Unnamed: 8`–`Unnamed: 10` | Entirely blank | None | Exclude from curated output; keep in raw source. |
| `Unnamed: 11` | One Archive.org URL | `reference_url_1` | Move only after it is associated with a specific item or collection. |
| `other links` | Entirely blank | None | Exclude from curated output until populated. |
| 31 blank rows | Display separators | None | Exclude from curated output; retain raw row number in the migration ledger. |
| Annual-series / category headings | Context rows | `series` tag | Use only as context to propose tags; require review of each assignment. |
| “missing” or editorial note rows | Research context | `notes` or future confirmed-missing item | Convert to an item only when title/identity is confirmed. |
| Standalone title URLs | Landing pages | `reference_url_*` or source registry | Do not expose as title records. |

## 4. Row classification before migration

Every raw data row must receive exactly one proposed migration disposition in a reviewable ledger:

| Disposition | Meaning | Expected treatment |
|---|---|---|
| `item` | A cataloguable individual disc, file, book, or other material item | Becomes one curated record after approval. |
| `missing_item_candidate` | A known work/part appears to be absent but identity is sufficiently clear | Becomes a curated record with `owned = false` after approval. |
| `series_context` | Heading or collection label used to derive a `series` tag | Does not become an item. |
| `source_context` | Landing page or source URL | Becomes a source/reference association, not an item. |
| `research_note` | Editorial reminder, uncertainty, or gap note | Moves to notes/ledger; not a catalogue item until confirmed. |
| `blank_separator` | Empty visual separator | Remains only in raw evidence. |
| `needs_review` | Ambiguous row | No public curated record until human decision. |

This classification is critical because the current 374 published rows are not 374 catalogue items.

## 5. ID assignment rules

1. Generate `uuid` as a compact numeric ID after an item is approved. It is never reissued or changed.
2. Generate `catalog_code` after canonical `item_type` and `year` are approved.
3. `SEQUENCE` is a zero-padded running number among items sharing the same `TYPE-YEAR` prefix. Example: three distinct 2002 lecture-disc records could become `LECTURE-2002-001`, `LECTURE-2002-002`, and `LECTURE-2002-003`.
4. Preserve any legacy identifier in `legacy_tempid`, even if malformed or duplicated. Never overwrite raw evidence.
5. If year is unknown, leave `year` blank and defer code issuance rather than manufacturing an inaccurate year. A future approved fallback rule can address such records.

## 6. Example migration (illustrative only)

The first identifiable 2002 DVD row currently has `tempid = LS200201_1`, title `Causality: The Ego's Foundation (Jan 2002) DVD01`, ✅, source `veritas`, and a Veritas product link. A proposed output, pending review, would look like:

```json
{
  "uuid": "<generated compact numeric ID after approval>",
  "catalog_code": "LECTURE-2002-001",
  "legacy_tempid": "LS200201_1",
  "title": "Causality: The Ego's Foundation",
  "item_type": "lecture",
  "series": "The Way to God",
  "year": "2002",
  "month": "01",
  "format": "DVD",
  "format_detail": "DVD01",
  "owned": true,
  "source_url_veritas": "https://veritaspub.com/product/2002-01-causality-the-egos-foundation-jan-2002/"
}
```

The sample illustrates the model only. It does **not** establish the final canonical title, series assignment, item type, or catalogue code without approval.

## 7. Proposed implementation sequence

1. Approve or amend this schema and controlled vocabulary.
2. Produce a **migration review ledger** for all 374 raw rows: original row number, raw values, proposed disposition, and proposed field values. No source data changes.
3. Review/approve the ledger in batches (for example, lecture series first, then books/media).
4. Generate the curated dataset and a machine-readable schema file from approved rows only.
5. Update the site to use the curated item view with search and filters for type, series, year, format, ownership, and approved source columns.
6. Retain the raw spreadsheet and review ledger as public provenance artifacts.

## 8. Decisions still needed before implementation

1. Confirm the exact `item_type` vocabulary; `audio`, `video`, and `lecture` may overlap in current records.
2. Confirm whether `location_physical`, `location_digital`, and `location_streaming` are the desired separate public location columns.
3. Confirm the year rule: recording year, original release year, publication year, or a documented priority order when they differ.
4. Confirm how a known missing work with no reliable year receives a readable catalogue code.
5. Approve a controlled syntax for `format_detail` (e.g. `DVD01` vs `DVD 1`).
6. Decide when additional approved publishers receive dedicated URL columns versus a future repeatable source structure.
