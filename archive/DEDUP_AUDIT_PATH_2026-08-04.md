# Dedup Audit — Path to Spiritual Advancement duplicate removal — 2026-08-04

**Date:** 2026-08-04 (second pass after academic promotion)  
**Task:** Owner requested dedup of duplicate Path to Spiritual Advancement rows 302/303.

## Before

- `migration_review_ledger.csv` raw rows 343 and 347 both marked `item`:
  - 343: `The Path to Spiritual Advancement` (truncated title, series Books, no Veritas URL)
  - 347: `The Path to Spiritual Advancement: How to Transcend the Ego and Experience the Presence of God` (full title, series Transcription Series Books, Veritas URL)
- Both promoted as master records:
  - UUID 302: `w-the-path-to-spiritual-advancement` — truncated title, Hay House URL only, no Veritas URL
  - UUID 303: `w-the-path-to-spiritual-advancement-how-to` — full title, Veritas URL + Hay House URL
- Work families 335 rows, master 359 rows (307 lecture / 41 book / 10 discussion /1 untyped) including 3 academic

## After dedup

- Ledger row 343 disposition changed `item` → `duplicate`, review_reason: "Duplicate of raw row 347 — same work, full title variant kept as master 303; truncated title variant previously created duplicate work_id."
- `data/research_master_source_overrides.csv` line for raw row 343 removed (duplicate override) — overrides 110 → 109
- `data/work_families.csv` entry for member 302 (w-the-path-to-spiritual-advancement) removed — families 335 → 334, works 202 → 201
- Master rebuilds: 359 → **358** items (307 lecture / **40 book** /10 discussion /1 untyped) — book count 41→40 (removed one duplicate Path book)
- Everything view 379 → **378** (358 master + 8 veritas +4 discovery +4 hayhouse +4 audible)
- Exclusions 68 → **69** (duplicate adds one excluded row)
- `MIGRATION_REVIEW_LEDGER.md` updated: item 306→305, adds `duplicate` 1 row, total 374
- `README.md` and `NEXT_AGENT_HANDOFF.md` updated to 358 baseline: 307 lecture /40 book /10 discussion /1 untyped, 271 codes, 69 exclusions, 109 overrides, 29 promoted
- Tests: 103/103 pass, coverage 92%

## Six Book Transcription Series final

After dedup:

- Path to Spiritual Advancement now single master row 303 (full title)
- Six Book Transcription Series 6 works:
  1. Path Jan-Feb (303)
  2. Evolution Mar-Apr (304)
  3. Beyond Illusion May-Jun (305)
  4. Spiritual Power Jul-Aug (306)
  5. Karma and Devotion Sep-Oct (307)
  6. Final Doorway Nov-Dec (308)

Previously 7 rows due to duplicate Path variant; now **6 rows, 6 works** — 100% complete, no duplicate.

## Verdict

Dedup successful: Path duplicate removed, master 358, no data integrity loss, all checks green.

*Generated 2026-08-04.*
