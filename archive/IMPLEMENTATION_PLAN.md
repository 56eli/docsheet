# DocSheet Implementation Roadmap

**Updated:** 2026-08-03 (post entry-by-entry official-source audit)
**Scope:** Preserve raw evidence while operating a reproducible, reviewable Hawkins research catalogue with a user-friendly spreadsheet interface.
**Current audit:** [AUDIT_2026-08-03_FULL.md](../AUDIT_2026-08-03_FULL.md)
**Transition guide:** [NEXT_AGENT_HANDOFF.md](../NEXT_AGENT_HANDOFF.md)

## Objective

Maintain clear boundaries between raw spreadsheet evidence, curated master records, official product inventories, review decisions, generated Pages data, and browser-only spreadsheet interaction. A live-source refresh, ID migration, or UI change must not silently overwrite reviewed research decisions.

## Current baseline

| Area | Current state |
|---|---:|
| Raw spreadsheet rows | 374 |
| Curated master records | 308 (274 lecture, 23 book, 8 discussion, 3 untyped) |
| Compact master ID range | 1–308, capped at 10000 |
| Excluded raw rows | 66 |
| Approved source overrides | 80 |
| Reviewed/unpromoted manual candidates | 17 |
| Manual research leads | 1 |
| Veritas official products | 191 |
| Item-to-product relationships | 301 |
| Series-compilation relationships | 7 |
| Everything Pages records | 344 (308 master + 36 candidates, tagged by `record_type`) |
| Catalogue codes | 221 |
| Months verified against official product dates | 195 / 195 |

## Completed milestones

- Raw evidence, migration ledger, source overrides, manual leads, and unpromoted candidates are separate review inputs.
- Master and Pages builders have read-only `--check` modes and reproduce committed derivative data.
- Master identity values were migrated from long UUID-style identifiers to compact numeric IDs in the approved 1–10000 range; all current references were updated.
- Exact source URL, date-aware Satsang/repeated-title, primary-source, related-material, and annual Highlights series-compilation relationships are validated and published.
- Pages exposes a review workspace with dedicated searchable/exportable sheets and review-status filters.
- Spreadsheet UX now includes per-view descriptions/counts, readable URL labels, column presets, a column chooser, row details, active filter chips, and CSV export smoke-test files.
- The main Update Spreadsheet workflow writes `docs/` outputs and the branch is synchronized with that correction.

## Guiding rules

1. **Never alter the raw spreadsheet through a generator.**
2. **Do not equate a commercial listing or title match with master identity.**
3. **Store reviewed decisions in explicit inputs, not generated JSON/CSV edits.**
4. **Require durable raw or manual provenance for every promoted record.**
5. **Keep compact master IDs stable once issued.**
6. **Keep product relationships at the evidence level actually supported:** item-level when a specific item is proven, series-level when only the lecture scope is proven.
7. **Generated Pages files are derivatives, not review sources.**
8. **Browser edits are session-only unless a persistence path is explicitly added.**

## Priority roadmap

### P0 — Merge the current branch

This branch contains a coordinated compact-ID data migration, generated artifact rebuild, frontend UX improvements, browser test scaffolding, and documentation refresh. Merge it as a single unit so `main` and GitHub Pages are internally consistent.

**Done when:** PR from `arena/019fc714-docsheet` is merged and Pages redeploys successfully.

### P1 — Add CI workflow once workflow permissions are available

**Delivered on this branch**

1. `package.json`, `package-lock.json`, `playwright.config.js`, and `tests/csv-export.spec.js` add Playwright browser smoke tests for active-view CSV export and selected-view export filenames.
2. README and instructions document how to install and run browser tests.
3. Live source fetch remains manual; CI should not call remote inventories.

**Blocked:** pushing `.github/workflows/ci.yml` failed because the configured GitHub App lacks `workflows` permission for workflow-file updates.

**Remaining:** reconnect/update GitHub permissions for workflow edits, add the read-only CI workflow, confirm Chromium installs and tests run in Actions, then expand smoke coverage to every declared Pages sheet/tab and generated JSON file.

### P1 — Review the current Veritas refresh artifact

The review-only Map Veritas workflow is active. Manual `main` run `30803991007` reached candidate generation and failed intentionally during comparison, proving the artifact review path works.

**Remaining:** download and inspect `veritas-inventory-review-30803991007` before accepting any live inventory or mapping-decision changes.

### P1 — Disable or clarify session-only editing

The UI still allows double-click cell edits that are not persisted. Either disable editing on generated/review sheets or add an explicit unsaved-edits state and reset path.

### P1 — Implement selective candidate promotion

**Current state:** 17 candidates are reviewed and intentionally `not_promoted`.

**Deliverables**

1. Define a promotion-decision input keyed by `candidate_key`.
2. Require approved final item type, year, format, ownership, source product, and promotion rationale.
3. Extend the master builder to generate stable compact IDs/codes for promoted candidates while retaining manual provenance.
4. Keep non-promoted candidates visible in the review workspace.

### P1 — Resolve inventory-only decisions

1. Review the nine unmatched Satsang products individually for candidate, exclusion, or inventory-only disposition.
2. Revisit the seven annual Highlights only if evidence later identifies individual DVD-part inclusion.
3. Review excluded spin-off/promotional products only if catalogue scope changes.

### P2 — Formalize schemas and build provenance

**Deliverables**

1. Publish versioned machine-readable contracts for master, candidates, source overrides, inventory decisions, item relationships, and series compilations.
2. Validate controlled vocabularies, URL/source consistency, unique keys, compact master IDs, years/months, and promotion state.
3. Emit a compact build manifest with input hashes, row counts, schema version, generator commit, and build time.
4. Add a raw `process_data.py --check` mode that handles the dynamic metadata timestamp safely.

### P3 — Harden review and public UX

1. Add explicit export modes (`filtered`, `all visible`, later `selected`).
2. Add copy-to-clipboard controls for compact IDs and source URLs.
3. Add browser tests for every tab, global search + status filter composition, column chooser, row details, export, keyboard navigation, and dark mode.
4. Consider self-hosting or a documented fallback for CDN dependencies.
5. Add mobile/card view refinements if review usage shifts to small screens.

## Execution order

| Order | Milestone | Why it comes next |
|---:|---|---|
| 1 | PR/merge this branch | Keeps compact-ID data, generated Pages, frontend UX, and docs synchronized. |
| 2 | Verify Pages deployment | Confirms public site serves the compact-ID/UX update. |
| 3 | Add CI after workflow permissions | Makes the protected state enforceable for collaborators. |
| 4 | Review Veritas artifact | Resolves the known live inventory divergence deliberately. |
| 5 | Disable/clarify editing | Removes a remaining UX/data-governance hazard. |
| 6 | Candidate promotion | Converts approved research into master data safely. |
| 7 | Schemas/manifest | Makes governance and release provenance machine-verifiable. |

## Definition of healthy project state

- All generated artifacts pass their `--check` command in a clean checkout.
- Master IDs are compact, unique, stable, and referenced consistently.
- A source refresh preserves reviewed decisions or explicitly reports a decision diff.
- Every promoted master record has traceable raw or manual provenance.
- Every public review sheet has a generated source, declared tab, and successful static/browser smoke coverage.
- Pages deployment reflects reviewed `docs/` data only after merge to `main`.
