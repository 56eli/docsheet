# Independent Full-Stack Audit — 2026-08-09 (Fresh Eyes)

**Auditor:** Arena.ai Agent Mode (independent, fresh eyes)
**Date:** 2026-08-09
**Branch:** `arena/019fe63c-docsheet` (from `main` at `150f080`)

## Executive Summary

The DocSheet project is a well-architected, defensively-coded data pipeline that
curates a David Hawkins lecture/book catalogue from a raw Google Sheets CSV
export into an interactive GitHub Pages site. The project is in **good health**:
all 126 tests pass, all 6 `--check` modes pass, coverage is 91% (floor 85%),
and the README counts match the generated data exactly. This audit found
**zero critical/data-loss issues**, **4 low-severity inconsistencies**, and
**3 medium-severity structural observations**.

---

## 1. Automated Verification Results

| Check | Result |
|---|---|
| `python process_data.py --check` | ✅ PASS |
| `python build_research_master.py --check` | ✅ PASS |
| `python build_catalogue_pages.py --check` | ✅ PASS |
| `python reconcile_research_master.py --check` | ✅ PASS |
| `python map_series_taxonomy.py --check` | ✅ PASS |
| `python sync_inventory_mirrors.py --check` | ✅ PASS |
| `python -m unittest discover tests` | ✅ 126/126 PASS |
| `coverage report` | ✅ 91% total, all modules ≥ 88% |
| `node --check docs/app.js` | ✅ PASS |
| `node --check playwright.config.js` | ✅ PASS |
| All docs/*.json valid JSON | ✅ PASS |
| CSP integrity hashes present | ✅ PASS |

---

## 2. Catalogue Data Verification

### README Claims vs Actual Data

| Metric | README Claim | Actual | Match? |
|---|---|---|---|
| Master records | 362 | 362 | ✅ |
| Item types (lecture/book/discussion/highlight/other) | 306/40/8/7/1 | 306/40/8/7/1 | ✅ |
| Catalogue codes | 278 | 278 | ✅ |
| Retained exclusions | 75 | 75 | ✅ |
| Approved source overrides | 134 | 134 | ✅ |
| Promoted candidates | 39 | 39 | ✅ |
| Unpromoted candidates | 0 | 0 | ✅ |
| Product relationships (total) | 340 | 340 | ✅ |
| Series compilations | 7 | 7 | ✅ |
| Veritas official products | 191 | 191 | ✅ |
| Retired UUID gaps | {225,226,227,246,249,264,281,284,302,309} | Same | ✅ |
| Work family memberships | 338 | 338 | ✅ |

### Structural Integrity

- **Zero empty titles** in master — every record has a display title.
- **Zero empty item_types** — the controlled-vocabulary validator rejects blanks.
- **Zero empty formats** — every record has a carrier.
- **Zero empty work_ids** — every master record belongs to a work family.
- **Zero books with catalogue codes** — correctly limited to lecture/discussion.
- **Zero duplicate catalogue codes** — sequence numbers are globally unique.
- **Zero orphaned work-family UUIDs** — every family member exists in the master.
- **Zero master Veritas URLs missing from inventory** — full URL coverage.
- **Zero unreviewed Hay House/Audible products** — all processed.
- **Duplicate titles (75 groups)** — all are legitimate DVD multi-part lectures
  (DVD01/DVD02/DVD03 sharing the same cleaned title, grouped under one work).

---

## 3. Findings

### 3.1 — Documentation Bloat (Medium, Structural)

**23 root-level `.md` files** and **78 archive/ documents** create significant
noise for newcomers. The project has accumulated 7+ independent audit files at
the root (`FULL_STACK_AUDIT_2026-08-03_*` through `*_2026-08-09_*`), plus
multiple proposals, handoff documents, and schema files.

The README justifies this by distinguishing "normative" root docs from
"historical" archive docs, and notes that 64 cross-references would break if
moved. Nevertheless, a `docs/` or `proposals/` subdirectory for non-normative
root docs (e.g. `UX_REWORK_SUGGESTIONS.md`, `UI_PRINCIPLES_AND_SUGGESTIONS.md`,
`WORKFLOW_WEB_EDITOR_GUIDE.md`) would reduce cognitive load.

**Risk:** Medium. No functional impact, but contributes to onboarding friction
and makes it easy to miss a normative doc among the noise.

### 3.2 — NEXT_AGENT_HANDOFF.md Branch Reference Drift (Low, Doc)

The handoff document references `arena/019fe620-docsheet` (the previous session
branch) as "current" but the actual current branch is `arena/019fe63c-docsheet`.
This is expected behavior — the handoff is written by the previous agent and
the new agent is always on a fresh branch — but the document's header reads as
if it's the definitive current-state reference.

**Risk:** Low. The handoff is a working document; each new agent session
naturally creates a new branch.

### 3.3 — Generator Scripts Lack `--check` Mode (Low, Consistency)

`generate_migration_ledger.py` and `generate_lecture_review.py` are the only
pipeline scripts without a `--check` verification mode. They're bootstrapping
generators (run once to create the review CSV), so this is acceptable — but
it means the test suite can only verify byte-for-byte determinism via the
`test_csv_generators_are_deterministic` test, not an idempotent `--check` round
trip like every other pipeline module.

**Risk:** Low. Both scripts are covered by the deterministic test and by the
integration write-then-check test in the sandbox. The lack of `--check` is
consistent with their one-shot bootstrap purpose.

### 3.4 — CSP `unsafe-inline` for Styles (Low, Security)

`docs/index.html`'s Content-Security-Policy allows `style-src 'self' 'unsafe-inline'`
for styles. This is required for the dark-mode toggle and Tabulator's inline
styling, so it's a deliberate trade-off rather than an oversight. Script
execution is properly restricted with a `sha256-` hash allowlist.

**Risk:** Low. `unsafe-inline` for styles only (not scripts) is a standard
CSP pattern for sites using CSS-in-JS or dynamic theme toggling.

### 3.5 — Large Monolithic Python Files (Medium, Maintainability)

`build_research_master.py` (1,660 lines, 77KB) and `build_catalogue_pages.py`
(1,078 lines, 50KB) are substantial single-file modules. The code is well-
organized with clear function separation, docstrings, and dataclass boundaries,
but the sheer size makes navigation and targeted testing harder.

`build_research_master.py` in particular handles: ledger parsing, title
cleaning, month extraction, format inference, source overrides, work families,
edition promotions, filename proposals, series taxonomy, year provenance, and
8+ validator functions — all in one file.

**Risk:** Medium. No functional impact, but refactoring into focused modules
(e.g. `master_validators.py`, `format_inference.py`, `year_provenance.py`)
would improve testability and code review.

### 3.6 — Root-Level Data CSVs with Spaces in Names (Low, Hygiene)

Three root-level CSV files have spaces in their names:
- `hawkins archive clone - Sheet1.csv` (source of truth)
- `migration_review_ledger.csv`
- `lecture_series_review.csv`

The space-containing filename is inherited from the Google Sheets export and
referenced by `process_data.py`'s `DEFAULT_CSV` constant. It works, but
spaces in filenames cause friction in shell scripts and CI.

**Risk:** Low. The `find_source_csv()` fallback mechanism handles renamed files
gracefully, and the CI workflow uses the exact name.

### 3.7 — EXTERNAL_AUDIT Has No File Extension (Low, Consistency)

`EXTERNAL_AUDIT` is a plain-text file at the repository root with no `.md`
or `.txt` extension. Every other text document in the repo has an extension.

**Risk:** Purely cosmetic. GitHub renders it as plain text regardless.

---

## 4. Architecture Observations

### 4.1 — Pipeline Design is Exemplary

The pipeline architecture is one of the best I've seen for a data curation project:

- **Layered inputs → generated outputs** with explicit `--check` modes on every
  generator, preventing silent data drift.
- **Reconciliation report** (`reconcile_research_master.py`) that projects the
  downstream impact of ledger changes before any generated file is overwritten.
- **Inventory mirror sync** (`sync_inventory_mirrors.py`) that re-derives
  computed columns and refuses to write when reviewed inputs contradict URL
  evidence.
- **Series taxonomy mapping** with a review overlay that preserves hand-reviewed
  dispositions across regeneration.
- **Product relationship derivation** that auto-generates primary relationships
  from master URLs and only requires hand-curation for non-primary links.

### 4.2 — Test Coverage is Strong

126 deterministic tests cover:
- End-to-end write/check/tamper cycles for all 5 core generators
- CSV generation determinism
- CLI entrypoint smoke tests
- Rule matrices (taxonomy dominance, format inference, title matching)
- Validator failure paths (malformed inputs, missing columns, vocabulary
  violations)
- Edge cases (UUID stability, source override idempotency, filename uniqueness
  guards, year/month backfill logic)
- Cross-module consistency (README counts, handoff counts, migration ledger
  counts)

The 91% coverage with 88%+ per module is strong for a project of this nature.
The uncovered lines are primarily `if __name__ == "__main__"` guards and rare
dependency-error branches.

### 4.3 — Defensive Coding Throughout

Notable defensive patterns:
- `process_data.py`: rejects CSVs that don't have the expected raw-spreadsheet
  headers, preventing silent selection of a migration ledger as a source.
- `build_research_master.py`: validates `proposed_owned` casing (rejects "True"),
  item_type vocabulary (rejects deprecated "audio"/"video"), work_id format
  (must start with "w-"), and edition format vocabulary.
- `fetch_veritas_catalogue.py`: retries transient API failures, preserves
  the committed inventory on error, and separates candidate generation from
  review acceptance.
- `build_catalogue_pages.py`: validates that every master record has a work_id,
  that inventory mirrors match, and that mapping decisions don't contradict
  primary URL evidence.

### 4.4 — Frontend Architecture

The frontend is a single-page application using Tabulator 6.5.2 (pinned with
SRI hashes) with:
- 19 tabbed views, each loading its own JSON file
- Faceted filtering (Series/Year/Type/Format/Owned) with per-view persistence
- Mobile browse mode with work-card stacks and discovery rails
- Expert columns toggle for technical metadata
- Dark mode with localStorage persistence and OS preference detection
- CSV export from the active view
- Content Security Policy with script hash allowlisting

---

## 5. Recommendations (Prioritized)

| # | Priority | Recommendation | Effort |
|---|---|---|---|
| 1 | P2 | Archive historical audit/proposal docs to `archive/`, keep only normative schemas at root | Low |
| 2 | P3 | Add `.md` extension to `EXTERNAL_AUDIT` | Trivial |
| 3 | P3 | Consider `pyproject.toml` for modern Python project metadata | Low |
| 4 | P2 | Consider splitting `build_research_master.py` into focused modules | Medium |
| 5 | P3 | Consider a `requirements-optional.txt` or optional dep for Playwright | Low |
| 6 | P3 | Update `NEXT_AGENT_HANDOFF.md` branch references for new sessions | Low |

---

## 6. Conclusion

**The DocSheet project is in excellent shape.** The data pipeline is defensively
coded, well-tested, and the catalogue data is consistent across all validation
layers. The README accurately describes the current state. The frontend is
functional with strong CSP protections.

No blocking issues. The findings above are improvement suggestions for an
already-solid codebase.
