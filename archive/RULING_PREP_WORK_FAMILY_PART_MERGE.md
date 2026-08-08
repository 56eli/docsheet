# Ruling Prep — Work-Family Consolidation: per-part `work_id`s vs one-lecture-one-work

**Prepared:** 2026-08-08 (deeper data pass, follow-up to `FULL_STACK_AUDIT_2026-08-08.md`)
**Status:** awaiting owner ruling · **Branch:** `arena/019fe098-docsheet`
**Scope:** `data/work_families.csv` (27 rows), `data/filename_proposal_YYYYMM.csv`
(27 `work_id` cells), regenerated master + Pages outputs.

---

## 1. The finding

The README defines the edition model as *"DVD lecture parts each keep their
own row, **grouped under one work**"* — and that is how the D6a grouping works
for e.g. Causality (`w-causality-the-ego-s-foundation` holds parts 1–3).
**Eleven multi-part lecture groups (27 rows) violate that**: each part sits in
its **own** `work_id`, keyed to the *raw* titles' `(Part 1)`/`PART1` markers,
even though the master's cleaned public titles are identical across parts and
the filename proposal groups them as one `[1/3]…[3/3]` part-set.

| Part group | Rows | Today: separate `work_id` per part |
|---|---|---|
| Volume I: Power vs. Force Muscle Testing | 202, 203 | **202 is inside `w-power-vs-force` (the BOOK work, with 286)**; 203 is its own volume work |
| Volume II: Consciousness and Addiction | 204, 205 | `…-pa`, `…-pa-1` |
| Volume III: Advanced States of Consciousness | 206, 207 | `…n`, `…n-1` |
| Volume IV: Consciousness: How to Tell the Truth | 208, 209 | `…an`, `…an-1` |
| Volume V: Undoing the Barriers to Spiritual Progress | 210, 211, 212 | `…u`, `…u-1`, `…u-2` |
| Become That Which You Are | 215, 216, 217 | `…-part`, `…-part-1`, `…-part-2` |
| Love is a Way of Being | 218, 219, 220 | `…-part`, `…-part-1`, `…-part-2` |
| The Presence of Spiritual Awareness | 222, 223, 224 | `…-part`, `…-part-1`, `…-part-2` |
| Mind, Heart and Service | 226, 227 | `…-part1`, `…-part2` |
| Spiritual Will Inspiring Q & A | 228, 229 | `…-part1`, `…-part2` |
| Verification of Spiritual Realities | 230, 231, 232 | `…-part`, `…-part-1`, `…-part-2` |

Totals: **27 rows** (26 solo per-part works + row 202 inside the book work);
work count **208**, memberships **341** (unchanged by the fix), coverage
365/365.

**Why it happened:** the D6a bulk grouping (owner-approved 2026-08-03) keyed
works by **exact normalized raw title** — and the raw titles of these parts
embedded `(Part 1)`/`PART1` markers, so exact-match produced per-part works.
The 2026-08-07 title-cleanup pass then stripped those markers from the
**public** titles but never re-keyed the work families. The families'
`evidence_note` for these rows still says *"part rows of one lecture"* — the
notes themselves contradict the per-part work assignment.

**The 202 contamination (worst case):** master 202 (Volume I Part 1) is a
member of **`w-power-vs-force`**, the *book* work (master 286 = Power vs.
Force: The Hidden Determinants…). Its own evidence note flags this:
*"Volume I-Power vs Force (Part 1) lecture row; Veritas book 50411 +
audiobook 1542 are related_material on this row - REQUIRES RULING (see 286)."*
The 2026-08-07 rulings fixed the 50411/1542 primary matches (→ 286/331) but
never re-adjudicated 202's work membership — so a visitor grouping by **Work**
sees Volume I Part 1 under the *book's* work and Volume I Part 2 under its own
work. This is the same C1-class contamination the D6a/C1 ruling fixed for the
Enlightenment rows.

## 2. Proposed fix (single ruling)

Merge the 11 part groups into **11 works** (26 solo works + 202 → 11 works;
work count **208 → 193**; memberships stay 341; coverage stays 365/365):

| New `work_id` | Members | New `canonical_work_title` (cleaned, = master title) |
|---|---|---|
| `w-volume-i-power-vs-force-muscle-testing` | 202, 203 | Volume I: Power vs. Force Muscle Testing |
| `w-volume-ii-consciousness-and-addiction` | 204, 205 | Volume II: Consciousness and Addiction |
| `w-volume-iii-advanced-states-of-consciousness` | 206, 207 | Volume III: Advanced States of Consciousness |
| `w-volume-iv-consciousness-how-to-tell-the-truth` | 208, 209 | Volume IV: Consciousness: How to Tell the Truth About Anything |
| `w-volume-v-undoing-the-barriers-to-spiritual-progress` | 210, 211, 212 | Volume V: Undoing the Barriers to Spiritual Progress |
| `w-become-that-which-you-are-june-2004` | 215, 216, 217 | Become That Which You Are |
| `w-love-is-a-way-of-being-january-2004` | 218, 219, 220 | Love is a Way of Being |
| `w-the-presence-of-spiritual-awareness` | 222, 223, 224 | The Presence of Spiritual Awareness |
| `w-mind-heart-and-service` | 226, 227 | Mind, Heart and Service |
| `w-spiritual-will` | 228, 229 | Spiritual Will Inspiring Q & A |
| `w-verification-of-spiritual-realities` | 230, 231, 232 | Verification of Spiritual Realities |

Specifically:
1. **202 leaves `w-power-vs-force`** (which keeps 286; the related_material
   product links 50411/1542 on 202 stay in `data/product_relationships.csv`
   — the 2026-08-07 primary-match rulings are untouched).
2. All 27 `work_id` cells updated in **both** `data/work_families.csv` and the
   `work_id` column of `data/filename_proposal_YYYYMM.csv` (they must stay in
   sync; edition rows 320–343 are unaffected — their work_ids come from
   `edition_promotions.csv` and are not family members).
3. Canonical titles cleaned of `PART1`/`PART2`/`(Part N)` markers, aligned to
   the master's public titles (same convention as
   `w-causality-the-ego-s-foundation`).

## 3. Why the merge is safe

- The filename proposal's part-groups already use the **same group keys**
  (`clean_title`, year, month, format) and do not require a shared work_id
  (the Volume-Series fold guard spans works by design) — no filename changes
  needed, only the `work_id` column.
- No other artifact keys off these per-part work_ids: edition promotions,
  product relationships, taxonomy mappings, and inventory mirrors reference
  **master UUIDs**, not work_ids.
- The D6a precedent already groups part rows of one lecture into one work
  (Causality, Radical Subjectivity, …) — this ruling simply finishes that job
  for the 11 groups the raw-title markers missed.

## 4. Apply + verify checklist (after owner approval)

```bash
# edit data/work_families.csv (27 rows) + data/filename_proposal_YYYYMM.csv (27 work_id cells)
python build_research_master.py          # regenerates master work_id/legacy columns
python build_catalogue_pages.py
python reconcile_research_master.py
python -m unittest discover tests        # 114, must stay green
# all six --check modes + node checks
```

Expected master diff: the `work_id` column on the 27 rows (plus
`canonical_work_title` reflected only in the families input); the **Work**
grouping in the Everything tab now shows one work per lecture.
