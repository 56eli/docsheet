# DocSheet Implementation Roadmap

**Updated:** 2026-08-03
**Scope:** Preserve raw evidence while operating a reproducible, reviewable Hawkins research catalogue.
**Current audit:** [PROJECT_STATE_AUDIT.md](PROJECT_STATE_AUDIT.md)

## Objective

Maintain clear boundaries between raw spreadsheet evidence, curated master records, official product inventories, review decisions, and generated Pages data. A live-source refresh or UI change must not silently overwrite reviewed research decisions.

## Current baseline

| Area | Current state |
|---|---:|
| Raw spreadsheet rows | 374 |
| Curated master records | 308 |
| Excluded raw rows | 66 |
| Approved source overrides | 80 |
| Reviewed/unpromoted manual candidates | 17 |
| Manual research leads | 1 |
| Veritas official products | 191 |
| Item-to-product relationships | 301 |
| Series-compilation relationships | 7 |
| Everything Pages records | 344 |

### Completed milestones

- Raw evidence, migration ledger, source overrides, manual leads, and unpromoted candidates are separate review inputs.
- Master and Pages builders have read-only `--check` modes and reproduce committed derivative data.
- Exact source URL, date-aware Satsang/repeated-title, primary-source, related-material, and annual Highlights series-compilation relationships are validated and published.
- Pages exposes a review workspace with dedicated searchable/exportable sheets and review-status filters.
- The main Update Spreadsheet workflow writes `docs/` outputs and the branch is synchronized with that correction.

## Guiding rules

1. **Never alter the raw spreadsheet through a generator.**
2. **Do not equate a commercial listing or title match with master identity.**
3. **Store reviewed decisions in explicit inputs, not generated JSON/CSV edits.**
4. **Require a durable provenance key for every manual candidate or promotion.**
5. **Keep product relationships at the evidence level actually supported:** item-level when a specific item is proven, series-level when only the lecture scope is proven.
6. **Generated Pages files are derivatives, not review sources.**

## Priority roadmap

### P0 — Make Veritas refresh review-safe

**Problem:** The Map Veritas workflow can regenerate `data/veritas_official_products.csv` from live matching and overwrite manually reviewed statuses or relationship decisions.

**Deliverables**

1. Add `data/veritas_mapping_decisions.csv` keyed by official product ID, with reviewed status, rationale, relationship/promotion references, and review date.
2. Update `fetch_veritas_catalogue.py` to fetch a raw inventory, then apply these decisions deterministically.
3. Change the workflow to produce a diff/review artifact or fail on unreviewed mapping changes; do not auto-commit destructive status replacement.
4. Add a `--check` mode for the fetch/mapping pipeline.

**Done when:** a live refresh cannot remove a reviewed product disposition without an explicit reviewed decision change.

### P1 — Enforce checks in CI

**Deliverables**

1. Add a pull-request workflow for Python compilation, `node --check`, master/pages/reconciliation checks, and review-input validation.
2. Add static HTTP smoke checks for every declared Pages sheet/tab and generated JSON file.
3. Keep live source fetch manual; CI must not call remote inventories.

**Done when:** a stale derivative, missing review sheet, malformed input, or syntax error blocks merge.

### P1 — Implement selective candidate promotion

**Current state:** 17 candidates are reviewed and intentionally `not_promoted`.

**Deliverables**

1. Define a promotion-decision input keyed by `candidate_key`.
2. Require approved final item type, year, format, ownership, source product, and promotion rationale.
3. Extend the master builder to generate stable UUIDs/codes for promoted candidates while retaining manual provenance.
4. Keep non-promoted candidates visible in the review workspace.

**Done when:** a selected candidate can enter the master reproducibly without direct generated-file edits.

### P1 — Resolve inventory-only decisions

1. Review the nine unmatched Satsang products individually for candidate, exclusion, or inventory-only disposition.
2. Revisit the seven annual Highlights only if evidence later identifies individual DVD-part inclusion.
3. Review excluded spin-off/promotional products only if catalogue scope changes.

### P2 — Formalize schemas and build provenance

**Deliverables**

1. Publish versioned machine-readable contracts for master, candidates, source overrides, inventory decisions, item relationships, and series compilations.
2. Validate controlled vocabularies, URL/source consistency, unique keys, UUIDs, years/months, and promotion state.
3. Emit a compact build manifest with input hashes, row counts, schema version, generator commit, and build time.
4. Add a raw `process_data.py --check` mode that handles the dynamic metadata timestamp safely.

### P3 — Harden review and public UX

1. Add browser tests for tab loading, global search + status filter composition, export, keyboard navigation, and dark mode.
2. Consider self-hosting or a documented fallback for CDN dependencies.
3. Keep session-only edit behavior explicit; consider disabling editing in review sheets if reviewers mistake it for persistence.
4. Add view-level explanatory copy/counts distinguishing master records, broad candidates, inventory-only products, and relationships.

## Execution order

| Order | Milestone | Why it comes next |
|---:|---|---|
| 1 | P0 Veritas mapping decisions | Protects the reviewed work before the next live refresh. |
| 2 | P1 CI | Makes the protected state enforceable for collaborators. |
| 3 | P1 candidate promotion | Converts approved research into master data safely. |
| 4 | P1 inventory-only decisions | Extends content coverage after promotion mechanics exist. |
| 5 | P2 schemas/manifest | Makes governance and release provenance machine-verifiable. |
| 6 | P3 UX/browser hardening | Builds on stable data and review workflows. |

## Definition of healthy project state

- All generated artifacts pass their `--check` command in a clean checkout.
- A source refresh preserves reviewed decisions or explicitly reports a decision diff.
- Every promoted master record has traceable raw or manual provenance.
- Every public review sheet has a generated source, declared tab, and successful static smoke check.
- Pages deployment reflects reviewed `docs/` data only after merge to `main`.
