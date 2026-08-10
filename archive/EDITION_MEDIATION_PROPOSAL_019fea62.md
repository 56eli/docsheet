# Edition Column Mediation — Carrier vs Edition-Note

**Session:** `arena/019fea62-docsheet` · 2026-08-10  
**Status:** Proposal + minimal implementation (see `data/edition_notes.csv`, `pipeline/enrichments.apply_edition_notes`, `edition_note` column)  
**Related:** `EDITION_MODEL_PROPOSAL.md`, `data/work_families.csv`, `data/edition_candidates.csv`, `data/research_manual_leads.csv`

---

## 1. Problem — two valid meanings of "Edition"

| Meaning | Who wanted it | How it is used today (362 masters) |
|---|---|---|
| **A — Carrier** = the physical/digital carrier of a work (book, audiobook, DVD, CD, streaming). The work × carrier model (`work_id` + one master row per carrier) was implemented 2026-08-03 and is stable: 24 minted edition rows (320–343), `format` + `format_detail` → virtual `edition` column (`format · format_detail`) with color dots and carrier filters. | Later implementation, now downstream of `pipeline/*`, `docs/app.js` (carrier dots, `displayMobileEdition`), `tests/test_pipeline` validators, and the Pages filters. | `edition` is **derived** in `docs/app.js` `loadData` → `row.edition = fmt ? (detail …) : detail`. Stored fields are `format` / `format_detail`. |
| **B — Edition note** = free-text note distinguishing multiple entries of the **same work** that happen to share a carrier. Example: *Power vs Force* special edition (non-B&W cover, pre-1995 Veritas hardcover) vs the current Hay House paperback (B&W cover, 2014). Both are `format=book` but are not the same physical edition. | Original intent for the "Edition" column per owner note: "provide notes on multiple entries of the same work but different editions of them. Like the special Power vs Force edition." | **Nowhere.** The only free-text that could hold it (`notes`) is reserved for the single `FRAN GRACE` owner marker; `research` holds provenance. The old-cover Power vs Force therefore lives only as a manual lead `manual-power-vs-force-old-edition` in `data/research_manual_leads.csv` (lead_status=`manual_edition_lead`). It is invisible in the Everything view except via that lead sheet. |

Both meanings are legitimate and the pipeline should support both without reusing the same column name for two different semantics.

## 2. Why naively reusing `edition` would break

- 147 tests assert `format` ∈ `EDITION_FORMATS` and `edition` derived from `format`. Changing `edition` to free-text would invalidate `FormatInferenceTests`, `EditionCandidateTests`, `FrontendDeliveryContractTests`, and the carrier-dot UI.
- The 24 promoted edition rows depend on `format`/`edition_role` validation; free-text would bypass the controlled vocabulary and re-introduce the title-matching bug (C2) that the `work_id` model fixed.
- Existing Sheets exports and the `catalogue_display_order` + `build-manifest` would drift on the next `--check`.

**Conclusion:** keep `edition` as carrier; introduce a new field for the descriptive note.

## 3. Mediation — keep carrier, add Edition Note, add a row where the note justifies a distinct physical edition

### 3.1 Principle
- **Carrier stays carrier.** The column labelled "Edition" in the UI keeps showing `format · format_detail` with the colored dot. For clarity its tooltip/label is changed to "Edition — Carrier" but the field name `edition` is unchanged.
- **Descriptive nuance gets its own field.** New stored column `edition_note` (nullable free-text, per-master-row, reviewed via `data/edition_notes.csv`) holds the original intent: e.g. "Original 1995 Veritas hardcover, non-B&W cover, dust jacket" vs "Current Hay House paperback, B&W cover, 2014 printing".
- **A truly distinct physical edition gets its own row.** When the note describes a carrier-identical but physically distinct printing that has a verifiable source URL or ISBN, it should be minted as a **new master row** via the existing edition-promotion path (`data/edition_candidates.csv` → `data/edition_promotions.csv`) with that `edition_note` attached, not just a note on the existing row. The manual lead `manual-power-vs-force-old-edition` is the first candidate for this.

### 3.2 New row idea — "Work-edition comparison row" (presentation, not a new table)

Instead of adding a 363rd horizontal spreadsheet column that clutters the grid, the new data is presented as a **work-first comparison row**:

- **In the grid:** the existing columns stay: `Work` (hidden under Expert), `Edition` (carrier), and a new **hidden-by-default** `Edition Note` column (`minWidth 180`) that appears when `Expert columns` is on or when a facet filter is applied. Cells render the note as italic muted text (`color: var(--text-muted); font-style: italic`), truncated with `title` tooltip for the full note.

- **In the row-details drawer:** a new `Edition` section entry: "Edition note" (between `Edition` and `Ownership`). Always visible when non-empty, even when the grid column is hidden.

- **In Mobile Browse / Desktop Browse:** each work card's edition stack already shows `displayMobileEdition` (`audiobook · Audiobook`) and the file `proposed_filename`. The mediation adds the `edition_note` as a second line under the filename: `edition_note · year` when present, so a user scanning a work with two `book` editions (B&W vs non-B&W) can distinguish them without opening the drawer.

- **In the review workspace:** a new sheet **"Edition Notes"** (`docs/edition-notes.json`, view key `editionNotes`) lists every `edition_note` row with `work_id`, `member_master_uuid`, `canonical_work_title` context — this is the review lane for authoring notes, mirroring `work_families.csv` and `master_year_overrides.csv` provenance. Its `record_count` is published in `catalogue-meta.json`.

This is the "another row idea": a **horizontal comparison row** (the work's edition stack) plus a **vertical review row** (the Edition Notes sheet), both derived from the same `edition_note` field, rather than overloading the `edition` string.

### 3.3 Schema

New input file `data/edition_notes.csv` (reviewed overlay, same review columns as `master_year_overrides.csv` / `master_notes_overrides.csv`):

```csv
uuid,edition_note,review_status,reviewed_on,reason
286,Current Hay House paperback, B&W cover — original 1995 Veritas hardcover had non-B&W dust jacket (see lead manual-power-vs-force-old-edition; distinct printing unpromoted until ISBN verification),approved,2026-08-10,Example mediation: distinguish current vs original Power vs Force printing
```

Master CSV gains one column `edition_note` after `format_detail` (position 15). `build_research_master.py:FIELDS` includes `edition_note`; `build_catalogue_pages.py:EVERYTHING_FIELDS` includes `edition_note`; `pipeline/enrichments.apply_edition_notes()` reads approved rows and writes `item["edition_note"] = row["edition_note"]`.

Validators: `pipeline/validators.validate_master_items_integrity` allows `edition_note` free-text (no controlled vocab). `validate_edition_notes()` checks `uuid` exists, `review_status` ∈ `{approved,proposed}`, ISO date.

Frontend: `docs/js/config.js` adds `edition_note: "Edition Note"` to `COLUMN_LABELS`, adds to `master.priority` after `edition`, and to `DETAIL_SECTIONS` Content. `docs/app.js` treats it as a searchable text field and renders it with the muted-italic style.

### 3.4 Worked example — Power vs Force

*Work* `w-power-vs-force` has today 2 master rows:
- 286 `Power vs Force` (book, Hay House paperback, 1995 first-pub, `source_url_amazon` Hay House)
- 320 `Power vs Force (Audiobook)` (audiobook edition, Audible, `w-power-vs-force`, minted via `edition-audible-pvf` → master 320)

The special non-B&W cover is **not a carrier difference** — both are `book` — so the work × carrier model cannot distinguish them. The manual lead describes a third row that is book-carrier but edition-distinct.

Mediation steps:

1. Keep 286's `edition` = `book` (carrier). Add `edition_note` on 286: "Current Hay House paperback, B&W cover (2014 printing)".
2. Promote the lead as a **new edition row** (or as a new book-edition member of the same work) when an Amazon/Veritas URL with a distinct ISBN is verified: `edition-audible-pvf-old-cover` → master 373 (example), `format=book`, `format_detail=Hardcover`, `edition_note="Original 1995 Veritas hardcover, non-B&W dust jacket, verified via [scan]"`. Its `work_id` is `w-power-vs-force` so the UI groups three cards under one work: two `book` cards distinguished only by `edition_note`, plus one `audiobook` card distinguished by `edition` carrier.
3. The Edition Note sheet shows the two `book` rows side-by-side, making the distinction reviewable without opening the Amazon pages.

This preserves the carrier UI (dots, filters, exports) and satisfies the original Edition-note intent.

### 3.5 Alternatives considered

| Alt | Why rejected |
|---|---|
| Rename `edition` to carrier and repurpose free-text to `edition` | Breaks 147 tests, carrier-dot UI, and export contracts; title-matching regression risk. |
| Put the note into `notes` | `notes` is reserved for the single `FRAN GRACE` marker; mixing would hide provenance again. |
| Put the note into `research` | `research` is auto-migrated provenance, not user-visible by default in the grid. |
| Add a second virtual column `edition2` derived from a different field | Adds confusion; a stored `edition_note` with explicit review columns is auditable. |

### 3.6 Implementation phasing (owner approval required for data, not for code)

- **Phase 0 (this branch):** code ships the new column as nullable `""` (no data drift). Tests pass, `build --check` green, `edition_notes.csv` is empty except a commented example. This is the mediation contract.
- **Phase 1 (owner review):** Populate `data/edition_notes.csv` with approved rows (first batch: w-power-vs-force 286). Run `build_research_master.py` → `build_catalogue_pages.py` → `--check`. The new `Edition Note` sheet appears in the review workspace for audit.
- **Phase 2 (if the old cover warrants a distinct row):** Add a new row to `data/edition_candidates.csv` for the non-B&W hardcover, promote via `data/edition_promotions.csv`. The work's `work_families.csv` already groups Power vs Force, so no family change.

### 3.7 What stays unchanged

- Raw CSV, ledger, `process_data.py` raw lane, `work_families.csv` approval flow, `edition_candidates` / `promotion` validators, carrier dot rendering, display order, and block map — all unchanged.
- The new `edition_note` sheet is **opt-in**; when empty, `catalogue-meta.json:edition_notes` is 0 and the UI hides the tab via the existing `hidden` logic (same as the empty Official Discovery lane).

---

**Owner decision needed:**

1. Accept the mediation (carrier stays, note is new column + new row where justified)?
2. Approve the first `edition_notes.csv` example row (286) with the suggested wording, or supply preferred wording?
3. Promote the old-cover Power vs Force lead to a distinct master row, or keep it as a note-only distinction?

*— arena 019fea62 · 2026-08-10 · proposal only; code on this branch already supports the column (null-safe) and the row idea is the work-stack comparison view.*
