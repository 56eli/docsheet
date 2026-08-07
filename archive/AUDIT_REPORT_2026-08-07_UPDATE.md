# Incremental Audit Update — 2026-08-07

**Auditor:** Senior Dev & Data Analyst
**Scope:** Recent changes in `arena/019fdcbc-docsheet` vs PR #24 merge

## Summary of Recent Changes

A thorough review of the git history and project state reveals the following significant additions to the project since the previous deep audit:

1. **Amazon Links (18 direct links)**:
   - Added direct Amazon product links for Books (Power vs Force, Eye of I, Truth vs Falsehood, Letting Go, Healing and Recovery, Transcending Levels, Map Explained, I Reality, Discovery, Reality Spirituality Modern Man, Success Is for You).
   - Added direct Amazon product links for the Office Series (Stress 1987, Death and Dying 1983, Sexuality, Illness Self-Healing, Worry Fear Anxiety, Pain Suffering, Handling Major Crises).
   - *Result*: The `source_url_amazon` column is now fully populated for 18 specific items, bringing total **source overrides to 127**.

2. **Year Source Provenance Column**:
   - A `year_source` column was introduced next to Year-Month.
   - It captures the provenance of the year assigned (e.g., "Ledger", "Veritas listing backfill", "Manual candidate", "Edition inherited", "Blank intentional").

3. **Year Fixes & Catalogue Codes**:
   - Specific years were fixed/assigned for outliers (e.g., Office Series 1987/1983, Devotion 2003, Mind Heart 2003, Spiritual Will 2004, Discussion 2012).
   - *Result*: Because catalogue codes are generated based on year presence, the total **catalogue codes increased from 271 to 280**.

4. **Relationships Output**:
   - The relationships total slightly increased from **333 to 336** derived relationships, thanks to URL backfills for those specific years and editions.

5. **Filename Proposal Updates**:
   - Generated filename proposals were synced to account for the year fixes (358 unique filenames maintained).

## Project Health & Pipeline Status

- **Pipeline integrity**: Fully deterministic. `build_research_master.py`, `build_catalogue_pages.py`, `reconcile_research_master.py` all generate exact expected state.
- **Test Suite**: Run re-verified in venv. **103/103 tests passing**.
- **Coverage**: 92% minimum, with modules >= 89%.
- **Curated Master**: Remains at **358 records**, 378 in the Everything View.

## Next Recommendations

- The `FULL_STACK_AUDIT_2026-08-07_DEEP.md` and `NEXT_AGENT_HANDOFF.md` are somewhat stale concerning counts (e.g., they still say "271 catalogue codes", "109 overrides"). I will update `NEXT_AGENT_HANDOFF.md` to reflect the 280 codes, 127 overrides, and 336 relationships.
