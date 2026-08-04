# 2014-batch Lectures — Recording-Date Investigation

**Date:** 2026-08-04
**Scope:** The 35 lectures whose `year` currently shows **2014** — the
Veritas **storefront-listing date** (a batch of lecture products added
2014-01–2014-05), not their recording date.

---

## 1. Finding

Per the owner's Year-Month rule, a lecture's `year`/`month` should be the
**recording date** (secondarily its **first release date**), never the day the
product was listed on the website. These 35 lectures are all showing the
product-listing year **2014** because `backfill_months_from_official_source()`
fills a blank lecture year from the Veritas product `published_date`, and all
35 products were added to the storefront in the **2014-01 → 2014-05 batch**
(not when they were recorded).

Unlike the book batch (which I fixed to first-publication years), these are
**lectures**, so the correct value is the **recording** date. The trouble: the
exact recording date is **not encoded in the committed data** (these rows have
no `LSyyyy` tempid, and their URL slugs carry no date), and it is **not
reliably recoverable from public sources** for all 35 — the Veritas store
shows only the 2014 listing date, and Audible/Amazon show later audiobook
release dates (2022), not the original recording.

## 2. The 35 records and what is established

| uuid | Series | Title | Product ID |
|---|---|---|---|
| 222–224 | On The Road Talk Series | The Presence of Spiritual Awareness (3 parts) | 42624 |
| 230–232 | On The Road Talk Series | Verification of Spiritual Realities (3 parts) | 1830 |
| 266–277 | On The Road Talk Series | All is Divinity; Compassion: The Pathway of the Heart; God is Hidden Within the Beauty of the Music; God is The Infinite Field; Spiritual Reality; The Ever-Present Joy; The Power of Devotion; The Prevailing Silence; Truth Shines Forth; Virtues: The Spiritual Foundation; You Are the Light of Consciousness | 1826/39375/1810/1802/46042/1828/1804/37761/40035/36441/37223 |
| 357 | On The Road Talk Series | Peace is the Natural State | 1814 |
| 233–250 | Office Series | A-01…B-06 (Stress, Health, Sexuality, Cancer, …) | 50435–50482 |
| 356 | Media Miscellaneous | Don't Set Sail Without A Compass – Audio | 1792 |

**Established from Veritas's own series page** ([Lecture Series 2002-2011](https://veritaspub.com/lecture-series-2002-2011/)): the On-the-Road lecture series ran **2002–2011** by year theme —
2002 *The Way to God*, 2003 *Devotional Nonduality*, 2004 *Transcending the Mind*,
2005 *Nonduality Intensive*, 2006 *Transcending Levels of Consciousness*,
2007 *Spiritual Reality & Modern Man*, 2008 *Advanced Spiritual Awareness*,
2009 *In the World but Not of It*, 2010 *Practical Spirituality*,
2011 *Love & Spiritual Seeker Qualities*.

So these talks were recorded **somewhere in 2002–2011** (not 2014), and the
**Office Series** records were private office visits from the early 2000s.
But the **specific year (and month) for each of the 35 cannot be sourced
reliably** from the committed data or public pages without per-title
confirmation.

## 3. Recommendation

Setting guessed recording dates into the review-gated master is **riskier than
leaving the listing date**, because a wrong year on a curated record is a
real data defect and hard to unwind. I therefore recommend **one of**:

1. **Leave the 35 as-is for now** and treat them as a documented open item
   (they are *consistent* — the 2014 date is at least a real release-listing
   date, not invented). Document the limitation so a future pass with
   authoritative sources can fill them.
2. **Owner supplies the authoritative recording dates** for the 35 (or at
   least the year groups), and I apply them through the ledger `proposed_year`
   / `proposed_month` (the same reviewed path as the book fix).
3. **Targeted partial fix:** correct only the subset where the recording year
   is well-attested (e.g. any talk verifiably part of the 2002 *The Way to
   God* series) and leave the rest flagged.

**I have not changed the curated master** for these 35 records. The pipeline
remains green (101 tests, 92% coverage, all 5 checks). The 2014 values are
unchanged pending the owner's ruling on how to source the true recording dates.
