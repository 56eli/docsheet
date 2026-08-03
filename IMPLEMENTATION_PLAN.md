# DocSheet Implementation Plan

**Status:** Proposed roadmap — no raw source or catalogue-record decision is made by this document.  
**Prepared:** 2026-08-03  
**Scope:** Make the public static catalogue reproducible, reviewable, and safe to evolve without overwriting raw evidence.

## Objective

Move from the current useful research/discovery interface to a dependable catalogue workflow in which raw evidence, reviewed master records, official-product inventories, and generated GitHub Pages files have clear ownership and can be rebuilt and verified safely.

## Initial baseline recorded for planning (before reconciliation)

| Area | Current state | Planning implication |
|---|---|---|
| Raw evidence | The source CSV has 374 data rows and remains preserved. | Never edit it as part of normal catalogue generation. |
| Review surface | `migration_review_ledger.csv` has 374 rows: 308 `item`, 31 blank separators, 21 series contexts, 8 research notes, 5 source contexts, and 1 needs-review row. | Ledger approval must be explicit before it becomes the sole master-data source. |
| Curated draft | The committed CSV has 314 rows, but its paired JSON has 308; a clean isolated rebuild from the present ledger produces 308 master rows and 66 exclusions (the committed exclusions CSV has 59). | Reconcile the six draft-only CSV records and 36 shared-record metadata differences before accepting a regenerated draft. Do **not** overwrite the committed output merely to make it match. |
| Public catalogue | `docs/master.json` has 354 records; an isolated rebuild using the current ledger-derived draft produces 348. | Generated website data and `docs/catalogue-meta.json` need the same reconciliation before a deployment refresh. |
| Official inventory | Veritas has 191 product records; Hay House has 24; Audible has 26; the international queue has 36. | Commercial products and intellectual-material records must remain separate until an approved relationship is recorded. |
| Deployment | GitHub Pages is publicly built from `main` → `/docs`. | Generated website files must always be written and committed under `docs/`. |
| Workflow | `update_spreadsheet.yml` runs `process_data.py`, which writes to `docs/`, but its comments and auto-commit paths still point to `public/`. | A raw-CSV update can succeed without committing the files the site uses; correct this first. |

The rebuild comparison above was performed in a temporary isolated directory; it made no repository changes.

**P0 reconciliation outcome (2026-08-03):** the reviewed rebuild now has 308 master records and 66 exclusions in both CSV/JSON derivatives, 62 approved source associations are preserved in `data/research_master_source_overrides.csv`, and the unresolved manual *Power vs Force* edition lead is retained outside the master in `data/research_manual_leads.csv`. `RECONCILIATION_REPORT.md` verifies the resulting build is consistent.

**P2 relationship outcome (2026-08-03):** `data/product_relationships.csv` now provides a validated, repeatable relationship layer with 276 exact primary Veritas item/product associations and four separately reviewed related-material products. Title-only matches remain unpromoted pending evidence. See `PRODUCT_RELATIONSHIP_SCHEMA.md`, `RELATIONSHIP_EXPANSION_AUDIT.md`, `BOOK_RELATIONSHIP_DECISIONS.md`, and `SATSANG_MAPPING_DECISIONS.md`.

## Guiding rules

1. **Preserve provenance.** `hawkins archive clone - Sheet1.csv` is immutable raw evidence. Keep raw rows, their row numbers, and any non-item context available through the ledger.
2. **Do not infer approval from a match.** A title match or official listing can propose a relationship, but cannot independently create an approved master identity, ownership claim, year, or item type.
3. **Keep data layers separate.** Raw CSV, migration ledger, curated research master, official-source inventories, and Pages JSON have different purposes and must not overwrite one another.
4. **Generate deterministically.** A clean checkout must either recreate committed generated files exactly or fail a documented validation check explaining why not.
5. **Make review decisions explicit.** Store approvals, corrections, rationale, and supporting URLs in reviewable source files—not as manual edits to generated JSON.

## Priority roadmap

### P0 — Establish a safe, reproducible build boundary

**Why first:** At present the raw-data workflow targets obsolete `public/` paths and catalogue generators do not recreate all committed output from their current declared inputs. Refreshing data before reconciliation risks silently dropping curated additions or publishing stale files.

1. Correct `.github/workflows/update_spreadsheet.yml` to describe, commit, and validate `docs/data.json` and `docs/meta.json`.
2. Identify every draft-only record and metadata difference between `migration_review_ledger.csv` and `data/research_master_draft.csv`.
   - The present draft-only raw rows are 368, 371, 375, and 376, plus an explicit manually added *Power vs Force* old-edition record with no raw row number; two draft records share an empty raw-row key.
   - Decide, per record, whether it belongs in the ledger as an approved item, a documented manual candidate with its own durable provenance key, or outside the master draft.
3. Reconcile the 36 differing shared master-record values through the ledger or an explicit reviewed-overrides input; never rely on hand-edits to `data/research_master_draft.csv`.
4. Define a documented build order and implement a non-writing verification command (for example, `python build_research_master.py --check` and `python build_catalogue_pages.py --check`) that reports stale outputs with a non-zero exit code.
5. Add a CI workflow that runs syntax checks and both verification commands on pull requests and on the protected/default branch.
6. Regenerate committed derivative files only after steps 2–5 are approved and the check passes.

**Acceptance criteria**

- The spreadsheet workflow commits only `docs/` outputs and has no `public/` references.
- An intentional one-file input change makes the verification command fail; a rebuild then makes it pass.
- A clean checkout reproduces the reviewed master and Pages derivatives byte-for-byte, except for an intentionally documented timestamp field.
- No raw CSV value is changed by the build or workflow.

### P1 — Complete the migration-ledger approval pass

**Why now:** Stable generation needs an authoritative review input, not a mixture of generated rows and later manual edits.

1. Review the 198 lecture-part proposals as a bounded first batch.
   - Confirm ten series labels, date extraction, title cleanup, item type, DVD detail, and per-part ownership.
   - Resolve the three quarantined August 2002 *Advaita* URLs (raw rows 28–30).
   - Source or deliberately leave blank the three February 2007 *Relativism vs Reality* URLs (raw rows 144–146).
2. Review the remaining candidate items by collection (Volume, Office, Satsang, media, books, transcripts, highlights, dissertation, and miscellaneous), preserving a review note for every correction.
3. Resolve the ledger’s one `needs_review` row and determine whether each research note is context only, a confirmed missing item, or an excluded lead.
4. Add an explicit review/approval convention to the ledger or a companion overrides file: reviewer, decision date, decision status, evidence URL, and rationale.
5. Give manually introduced candidates a durable source/provenance key rather than an empty `raw_row_number`; do not generate identity from title text.

**Acceptance criteria**

- Every public curated record has a review status and a traceable raw-row or documented manual-candidate provenance key.
- Every true item has a unique UUID; a readable catalogue code is assigned only after the approved type/year rule is satisfied.
- Raw row 28–30 link handling and raw rows 144–146 missing-link handling have recorded decisions.

### P2 — Model official-source relationships without duplication

**Why now:** The official inventory is valuable evidence but a commercial product can be a format, edition, compilation, or unrelated product rather than a new material record.

1. Preserve the full 191-row Veritas inventory and its current statuses: 110 normalized-title matches, 49 title matches, 10 unique items, 18 compilations/new editions, and 4 excluded related-material products.
2. Convert approved match decisions into explicit master-to-product relationships rather than duplicate master records. Record relationship type such as `same_material_format`, `compilation`, `new_edition`, `related_material`, or `unresolved`.
3. Review the four Hay House unreviewed products: *How to Surrender to God*, *Live Life As A Prayer*, *The Letting Go Guided Journal*, and *The Letting Go Deck*.
4. Review Audible/Nightingale-Conant candidates and possible relationships, including *The Ultimate David Hawkins Library*, *The Discovery*, *Healing*, *Naked*, *OM*, and the three flagged possible relationships.
5. Keep the 36-entry international queue separate until a source is approved and the product’s language, market, and relationship are verified.
6. Keep source inventories immutable per fetch date or add a retrieval timestamp/source snapshot so changes at publishers can be audited.

**Acceptance criteria**

- Each approved source association has a stable master identifier, official product URL, source/platform, relationship type, review status, and evidence note.
- “Everything” has a documented inclusion rule that distinguishes approved master items from review candidates and compilations.
- A source refresh cannot erase a prior reviewed mapping without an explicit diff and review.

### P3 — Formalize the curated data contract

**Why now:** The draft schema is sound as a proposal, but the software needs a machine-enforced contract to prevent regressions.

1. Publish a versioned schema (JSON Schema, CSV contract, or equivalent) for research-master records and validate all generated records against it.
2. Enforce controlled fields for `item_type`, `format`, `owned`, year/month shape, URLs, UUIDv7, catalogue-code uniqueness, and provenance keys.
3. Clarify the policy for unknown year/type: no catalogue code until approved, but a UUID/provenance key may still be assigned after identity approval.
4. Define the relationship/inventory schema in P2 rather than overloading the flat master record with repeated source columns beyond the currently approved core sources.
5. Emit a compact, machine-readable build manifest with source file hashes, row counts, schema version, build time, and generator version/commit.

**Acceptance criteria**

- Invalid controlled values, duplicate identifiers, malformed URLs, or an untraceable record fail validation before Pages JSON is written.
- Schema changes are versioned and include a migration note.
- Build metadata identifies exactly which reviewed inputs produced a deployed data set.

### P4 — Improve the public catalogue experience after data stabilization

**Why fourth:** UI filters and statistics should reflect approved structured metadata, not the raw spreadsheet’s mixed headings, notes, and separators.

1. Make the default landing view clearly distinguish approved master items, review candidates, official products, and the immutable original spreadsheet.
2. Add structured filters for item type, series, year, format, ownership, source/platform, language, and review state only where the values are approved and complete enough to be useful.
3. Show source relationships and product/edition context rather than making title matches look like duplicate catalogue works.
4. Label all session-only editing unambiguously and consider disabling it in data views if it misleads users into expecting persistence.
5. Add accessible empty, loading, error, and no-results states; test keyboard navigation, focus behavior, responsive layout, and link safety.
6. Add lightweight browser smoke tests for tab loading, search, CSV export, and source-link rendering.

**Acceptance criteria**

- The default public count is an explained count of approved master items, not raw rows or mixed commercial candidates.
- Every catalogue tab loads from an available generated file; tabs have understandable labels and accessible keyboard behavior.
- Search/export operates on the selected view and never mutates source data.

### P5 — Operate and document the pipeline

1. Document the exact local commands for validate, rebuild, preview, and source refresh.
2. Update `README.md`, `INSTRUCTIONS.md`, and `HANDOFF.md` when the workflow/data contract changes; remove stale claims such as the current assertion that the `public/` path issue is already fixed.
3. Add a release/checklist for a data refresh: fetch inventory, inspect source diff, run validation, review relationship changes, rebuild derivatives, preview Pages, and verify deployment.
4. Configure workflow permissions narrowly and retain manual dispatch for remote-source retrieval unless a reviewed schedule is deliberately introduced.
5. Record known source limitations and last-reviewed dates so users can distinguish a current official inventory from research leads.

## Recommended execution order

| Milestone | Deliverable | Depends on |
|---|---|---|
| 1 | Corrected raw-spreadsheet workflow and automated check foundation | None |
| 2 | Reconciliation report and reviewed ledger/overrides design | Milestone 1 |
| 3 | Reproducible research-master and Pages rebuild | Milestone 2 |
| 4 | Lecture-series approval batch and remaining ledger review | Milestone 2 |
| 5 | Official product relationship model plus reviewed mappings | Milestones 3–4 |
| 6 | Schema validation and build manifest | Milestone 5 |
| 7 | Structured UI filters, public-count clarity, and browser tests | Milestone 6 |

## Next implementation recommendation

Start the next P2 batch with the 27 remaining non-Satsang title-only candidates documented in `RELATIONSHIP_EXPANSION_AUDIT.md`. Review a bounded group by evidence rather than promoting normalized-title matches wholesale; books/audiobooks that share a lecture title, compilations, and related interviews require distinct relationship decisions.
