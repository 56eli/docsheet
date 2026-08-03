# TEMP — Suggestions: Pending Items into Everything + Pages Readability (2026-08-03)

**One-sentence task summary:** Created actionable suggestions for promoting pending candidates into the Everything view and improving spreadsheet readability across all pages.

## 1. Moving "everything pending" into the Everything sheet

Current state (Everything = 353 rows):
- 317 curated masters
- 36 official candidates (discovery + veritas + hayhouse + audible)

**Pending items that could be surfaced more deliberately:**

A. **17 manual candidates** (currently only in "Master Candidates" tab, not promoted)
   - Suggestion: Add a new `promotion_status` filter in the Everything generator or expose a "Promotable Candidates" sub-view. Or add a one-click "Promote all reviewed" path once owner decisions are recorded.

B. **6 unpromoted reviewed candidates** + **1 manual lead**
   - Suggestion: Create a lightweight `pending_promotions.csv` input that the generator can optionally merge into Everything as `candidate_pending_promotion` rows (with clear provenance).

C. **~86 remaining blank-format rows** (after the 27 we just inferred)
   - Suggestion: Run a second pass using `format_detail` + product page text (e.g., "Two DVD Set", "streaming video is not available") to backfill more.

D. **International discovery queue** (currently separate tab)
   - Suggestion: Optionally merge Spanish/Intl items into Everything as `candidate_international` so the main view becomes truly "everything available".

E. **Nightingale-Conant provenance** (we just added the first override)
   - Suggestion: Extend the same pattern to the 5 other known NC products (Healing, etc.) once evidence URLs are confirmed.

**Recommended next engineering step:** Add an optional `--include-pending` flag to `build_catalogue_pages.py` that surfaces the 17+6 pending items as distinct record_types for owner review without polluting the master.

## 2. Pages / sheet readability improvements

Current UI (Tabulator) is already strong, but these would raise polish:

1. **Column width & freezing** — Already good, but add a "Compact view" preset that hides low-priority columns (uuid, raw_*, matched_*) by default on Everything.
2. **Status badges** — Record_type badges are excellent; extend the same visual treatment to `format` (color-code DVD/CD/streaming/audio/book).
3. **Row density toggle** — Add a "Dense / Comfortable" switch (localStorage) for users who want more rows visible.
4. **Relationship drawer** — When clicking a master row, show a collapsible "Related Products" section (pull from product-relationships.json) instead of forcing users to switch tabs.
5. **Search scope hint** — Show "Searching across 17 sheets" or "Current view only" under the global search box.
6. **Empty-state messaging** — For tabs with 0 rows, show helpful "This review sheet is empty because..." text.
7. **Mobile / narrow-screen** — Add responsive column hiding (already responsiveLayout=false; consider a mobile preset).
8. **Export with provenance** — Include `record_type` column by default in all CSV exports so downstream users always know curated vs candidate.
9. **Dark-mode polish** — The current dark theme is good; add a subtle zebra-row contrast improvement.

**Quick win:** Add a "Readability" section in the footer that links to a short help modal explaining record_type, format vs item_type, and why candidates appear alongside masters.

These suggestions keep the existing architecture intact while making the live spreadsheet more usable for both reviewers and end users.

**File is temporary — delete after review.**