# Research Master Draft — Clean Migration

**Status:** Generated clean draft; not yet wired into the public spreadsheet UI.
**Build command:** `python build_research_master.py`
**Outputs:**

- `data/research_master_draft.csv` — reviewable spreadsheet export
- `data/research_master_draft.json` — machine-readable equivalent
- `data/research_master_exclusions.csv` — every raw row not included as a clean item

## Migration result

| Measure | Result |
|---|---:|
| Raw spreadsheet data rows preserved in the ledger | 374 |
| Clean migrated item records | 308 |
| Excluded provenance/context rows | 66 |
| UUIDs | 308 unique UUIDv7 values |
| Readable catalogue codes assigned | 198 |
| Lecture records with `LECTURE-YEAR-SEQUENCE` codes | 198 |
| Records with blank catalogue code pending verified type/year | 110 |
| Proposed `lecture` items | 198 |
| Proposed `book` items | 23 |
| Items with type still blank | 87 |
| Valid migrated Veritas source URLs | 222 |
| Public reference URLs migrated | 1 |

## What was migrated cleanly

- Each of the 308 candidate material rows now has a stable UUIDv7.
- The 198 `LS` lecture-part rows have a distinct readable catalogue code, canonical title without only the trailing date/DVD label, series, year/month, DVD detail, ownership status, and valid Veritas URL where present.
- Existing `tempid` values are retained as `legacy_tempid`; they are not treated as primary keys.
- The approved source URL columns and public location fields exist in the draft schema, even where current values are blank.
- Raw non-Veritas source wording and the two populated unnamed-note cells are preserved in `notes`.
- The one URL found in an incorrectly used raw `format` cell is preserved as a public reference URL, not misclassified as a format.

## What intentionally did not make the clean item dataset

`data/research_master_exclusions.csv` preserves all 66 excluded raw rows:

| Raw disposition | Count | Reason |
|---|---:|---|
| Blank separator | 31 | Visual layout only; no catalogue content. |
| Series/category context | 21 | Used to propose tags but not itself a flat item. |
| Research note | 8 | Missing-material reminders or ambiguous editorial notes. |
| Source context | 5 | Landing/reference URLs embedded as title rows. |
| Needs review | 1 | Ambiguous title requiring a direct decision. |

No raw data is deleted. The raw CSV, full migration ledger, and exclusions CSV remain the provenance trail.

## Important unresolved work

1. **87 records have no approved item type** and **110 have no readable catalogue code** because type and/or year are not verified. This follows the approved UUID-only fallback rule.
2. The three malformed August 2002 *Advaita* URLs remain excluded from the Veritas URL field pending correction; the three February 2007 *Relativism vs Reality* parts still have no product URL.
3. The draft has not replaced `docs/data.json`, so the current public site remains unchanged until the clean dataset and UI transition are explicitly approved.
4. Internet-discovered material must enter through a separate research-import queue; it should not be mixed into the raw spreadsheet or silently added to the draft.

## Next phase: external material discovery

The requested next phase is to discover Hawkins-related material beyond this spreadsheet. Each candidate should first enter a review queue with:

- canonical/source title
- item type, series, year, and format where evidenced
- approved official-source URL(s)
- source URL(s) supporting the discovery
- proposed ownership/location fields left blank unless known
- confidence/review notes

Only after review should an external candidate receive a UUID and be added to the research-master draft.
