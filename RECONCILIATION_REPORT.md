# Research Master Reconciliation Report

**Status:** Read-only comparison; no raw CSV, review ledger, master draft, or Pages JSON was changed to produce this report.

## Purpose

This report compares the committed `data/research_master_draft.csv` with the in-memory output of `build_research_master.py` using the current `migration_review_ledger.csv`. It also checks the paired master JSON and exclusions outputs, then shows the cascade to the Everything Pages dataset if the ledger projection were used. It is a review aid, not approval to overwrite either generated file.

## Summary

| Measure | Committed state | Current ledger projection |
|---|---:|---:|
| Research-master CSV records | 365 | 365 |
| Research-master JSON records | 365 | 365 |
| Research-master exclusion records | 72 | 72 |
| Draft-only CSV records without a matching ledger `item` | 63 | 0 |
| Ledger `item` records absent from CSV draft | 0 | 0 |
| Matched CSV records with one or more field differences | 0 | 0 |
| `docs/master.json` / ledger-projected Everything records | 365 | 365 |

The checked outputs are not yet fully reconciled. Review the differences below before rebuilding so reviewed additions are not lost.

The normal `python build_catalogue_pages.py --check` evaluates Pages files against the **committed** master CSV and may pass while this cascade differs. This report identifies the upstream master/ledger divergence that must be resolved first.

## Draft-only CSV records requiring a provenance decision

Each record below is present in the committed draft CSV and therefore included by the current Everything build, but is not an `item` in the current ledger projection. Retain it only by recording its approval and durable provenance in the ledger or a reviewed overrides input; otherwise it will disappear on a normal master rebuild.

| Raw row | Title | Type | Notes |
|---:|---|---|---|
| — | Book of Slides (The Complete Collection) | book | Promoted from official candidate manual-veritas-38608: Official page identifies a 655-page book compendium of lecture slides from 2002–2011. |
| — | Compassion (Audiobook) | lecture | Promoted edition audio of work w-compassion from candidate edition-audible-compassion: Audible audiobook edition of the lecture work; Audible inventory row matched_by_title. |
| — | Devotion to Truth Talk | lecture | Promoted from official candidate manual-veritas-55473: Official page identifies a 2003 On-the-Road talk; owner ruling 2026-08-08 records the streaming page as reference_url_1 for the product instead of storing streaming availability in format_detail. |
| — | Devotional Nonduality Intensive: Alignment (Audiobook) | lecture | Promoted edition audio of work w-alignment from candidate edition-audible-dni-alignment: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | Devotional Nonduality Intensive: Intention (Audiobook) | lecture | Promoted edition audio of work w-intention from candidate edition-audible-dni-intention: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | Dialogues on Consciousness and Spirituality | book | Promoted from official candidate manual-academic-dialogues-1998: Veritas Publishing 1998-01-01, 94 pages, spiral-bound, ISBN 0964326175; early transcript collection; evidence: Amazon, AbeBooks, Goodreads, Open Library; completeness audit. |
| — | Don’t Set Sail Without A Compass – Audio | lecture | Promoted from official candidate manual-veritas-1792: Official page identifies a one-CD 67-minute audio product. |
| — | Giving Up Illness through A Course in Miracles© – Audio | lecture | Promoted from official candidate manual-veritas-1544: Official page identifies a three-CD 3h45m audio presentation. |
| — | Healing and Recovery (Audiobook) | book | Promoted edition audio of work w-healing-and-recovery from candidate edition-audible-healing: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Healing: Achieving Total Wellness Through Higher Levels of Consciousness | lecture | Promoted edition audio of work w-healing-and-recovery from candidate edition-veritas-healing-audio: Veritas product 1695; audio edition of the work; inventory status unreviewed_official_product. |
| — | Highlights of the 2002 Lectures 1-6 | highlight | Promoted from official candidate manual-veritas-1800: Official Veritas product 1800 (title 'Highlights of the 2002 Lectures 1-6'); product page lists it as a streaming compilation of the 2002 lectures. Owner ruling 2026-08-07: promote to curated master, series Lecture Highlights, year 2002. |
| — | Highlights of the 2002 Lectures 7-12 | highlight | Promoted from official candidate manual-veritas-1808: Official Veritas product 1808 (title 'Highlights of the 2002 Lectures 7-12'); product page lists it as a streaming compilation of the 2002 lectures. Owner ruling 2026-08-07: promote to curated master, series Lecture Highlights, year 2002. |
| — | Highlights of the 2003 Lectures | highlight | Promoted from official candidate manual-veritas-1824: Official Veritas product 1824 (title 'Highlights of the 2003 Lectures'); product page lists it as a streaming compilation of the 2003 lectures. Owner ruling 2026-08-07: promote to curated master, series Lecture Highlights, year 2003. |
| — | Highlights of the 2004 Lectures | highlight | Promoted from official candidate manual-veritas-36857: Official Veritas product 36857 (title 'Highlights of the 2004 Lectures'); product page lists it as a streaming compilation of the 2004 lectures. Owner ruling 2026-08-07: promote to curated master, series Lecture Highlights, year 2004. |
| — | Highlights of the 2005 Lectures | highlight | Promoted from official candidate manual-veritas-39238: Official Veritas product 39238 (title 'Highlights of the 2005 Lectures'); product page lists it as a streaming compilation of the 2005 lectures. Owner ruling 2026-08-07: promote to curated master, series Lecture Highlights, year 2005. |
| — | Highlights of the 2006 Lectures | highlight | Promoted from official candidate manual-veritas-40747: Official Veritas product 40747 (title 'Highlights of the 2006 Lectures'); product page lists it as a streaming compilation of the 2006 lectures. Owner ruling 2026-08-07: promote to curated master, series Lecture Highlights, year 2006. |
| — | Highlights of the 2007 Lectures | highlight | Promoted from official candidate manual-veritas-44429: Official Veritas product 44429 (title 'Highlights of the 2007 Lectures'); product page lists it as a streaming compilation of the 2007 lectures. Owner ruling 2026-08-07: promote to curated master, series Lecture Highlights, year 2007. |
| — | How to Surrender to God | lecture | Promoted from official candidate manual-hayhouse-how-to-surrender: Official Hay House audiobook 'How to Surrender to God: The Path to Enlightenment Through Letting Go' by Sir David R. Hawkins, M.D. Ph.D. (7 tracks + supplemental, 3h06m, ISBN 9781401960506, published 2019-12-19; live Hay House product page verified 2026-08-07). No existing master matches; unique program promoted per owner ruling 2026-08-07. |
| — | In The World But Not Of It (Audiobook) | book | Promoted edition audio of work w-in-the-world-but-not-of-it from candidate edition-audible-itwbnoi: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Letting Go (Audiobook) | book | Promoted edition audio of work w-letting-go from candidate edition-audible-lettinggo: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Life with “Doc” My Husband & My Teacher, Dr. David R. Hawkins | book | Promoted from official candidate manual-veritas-53036: Official page identifies Susan Hawkins’s memoir and inside account. |
| — | Live Life As A Prayer (Audio) | lecture | Promoted edition audio of work w-live-prayer from candidate edition-hh-liveprayer: Hay House audio edition of the lecture work; Hay House inventory row unreviewed_official_product. |
| — | Mind, Heart and Service: The Pathway of Devotional Non-Duality | lecture | Promoted from official candidate manual-veritas-54219: Official page identifies a 2003 Science of Mind church lecture; owner ruling 2026-08-08 records the streaming page as reference_url_1 for the product instead of storing streaming availability in format_detail. |
| — | OM | other | Promoted from official candidate manual-audible-om: Audible listing of the mantra recording 'OM' by Dr. Hawkins with a 300-year-old Tibetan bell (59 min, meditation; publisher Veritas Publishing; (c)2017 Institute for Spiritual Research (P)2022; live Audible page verified 2026-08-07). No existing master matches; unique recording promoted per owner ruling 2026-08-07. |
| — | Orthomolecular Psychiatry: Treatment of Schizophrenia | book | Promoted from official candidate manual-academic-orthomolecular-1973: Co-authored with Linus Pauling (double Nobel laureate), W.H. Freeman 1973, 697 pages, ISBN 0716708981, early psychiatric academic work pre-dating spiritual corpus; listed in BookNotification, EverybodyWiki, Wellcome Collection; part of completeness audit for all Hawkins material ever produced. |
| — | Peace is the Natural State | lecture | Promoted from official candidate manual-veritas-1814: Official page identifies an On-the-Road audio product. |
| — | Permanent Inner Peace | discussion | Promoted from official candidate manual-veritas-50485: Official page identifies a 2012 discussion/interview product. |
| — | Power vs. Force (Audiobook) | book | Promoted edition audio of work w-power-vs-force from candidate edition-audible-pvf: Audible audiobook edition of the Power vs Force work; Audible inventory row matched_by_title. |
| — | Power vs. Force Audio Book | book | Promoted edition audio of work w-power-vs-force from candidate edition-veritas-pvf-audiobook: Veritas product 1542; audiobook edition of the Power vs Force work; currently related_material on lecture 202 - REQUIRES RULING on family placement. |
| — | Qualitative and Quantitative Analysis and Calibration of the Level of Human Consciousness | book | Promoted from official candidate manual-academic-qualitative-1998: Doctoral dissertation published by Veritas Publishing 1998-01-31, 200 pages, spiral-bound, ISBN 0964326183; defines Scale of Consciousness; evidence: Amazon, Open Library OL11707875M, BooksRun; completeness audit. |
| — | Satsang Series (Jan 2006) | lecture | Promoted from official candidate manual-veritas-satsang-1304: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Satsang Series (Jul 2006) | lecture | Promoted from official candidate manual-veritas-satsang-1310: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Satsang Series (Jul 2008) | lecture | Promoted from official candidate manual-veritas-satsang-1639: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Satsang Series (Jun 2010) | lecture | Promoted from official candidate manual-veritas-satsang-1697: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Satsang Series (Mar 2006) | lecture | Promoted from official candidate manual-veritas-satsang-1306: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Satsang Series (May 2006) | lecture | Promoted from official candidate manual-veritas-satsang-1308: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Satsang Series (Nov 2006) | lecture | Promoted from official candidate manual-veritas-satsang-1314: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Satsang Series (Sep 2006) | lecture | Promoted from official candidate manual-veritas-satsang-1312: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Satsang Series (Sep 2010) | lecture | Promoted from official candidate manual-veritas-satsang-1699: New-work candidate per SATSANG_MAPPING_DECISIONS.md Addendum (2026-08-03): missing collection month; no master overlap; ownership unknown. |
| — | Spiritual Reality and Modern Man: God vs. Science: Limits of the Mind (Audiobook) | lecture | Promoted edition audio of work w-god-vs-science from candidate edition-audible-srmm-godvs: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | The Discovery | lecture | Promoted from official candidate manual-audible-discovery: Official Nightingale-Conant program 'The Discovery: Revealing the Presence of God in Your Life' (7 sessions, 6h58m, by David Hawkins; live NC + Audible pages verified 2026-08-07). (c)2007 David Hawkins (P)2007 Nightingale Conant. No existing master matches; unique work promoted per owner ruling 2026-08-07. |
| — | The Ego is Not the Real You | book | Promoted from official candidate manual-veritas-47979: Official page identifies a paperback collection of selected Hawkins teachings and quotes. |
| — | The Essence of Letting Go: A Living Transmission of Truth | lecture | Promoted from official candidate manual-veritas-55576: Official page identifies an original 12-session audio program drawing on multiple earlier teachings. |
| — | The Eye of the I (Audiobook) | book | Promoted edition audio of work w-eye-of-the-i from candidate edition-audible-eye: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | The Highest Level of Enlightenment (Audiobook) | book | Promoted edition audio of work w-highest-level-of-enlightenment from candidate edition-audible-hle: Audible audiobook edition of the book; Audible inventory row matched_by_title. |
| — | The Highest Level of Enlightenment – Audio | lecture | Promoted edition audio of work w-highest-level-of-enlightenment from candidate edition-veritas-hle-audio: Veritas product 1742; audio edition (Veritas sells this work audio-only); inventory status unreviewed_official_product. |
| — | The Man Who Mapped Consciousness: Life and Legacy of Dr. David R. Hawkins | book | Promoted from official candidate manual-veritas-55425: Official page identifies a biography of Hawkins’s life and legacy. |
| — | The Power of Love: A Transformed Heart Changes the World | book | Promoted from official candidate manual-veritas-43146: Official page identifies Fran Grace’s book dedicated to Hawkins and Susan, with interview material. |
| — | The Ultimate David Hawkins Library | lecture | Promoted from official candidate manual-audible-ultimate-library: Official Nightingale-Conant 'The Ultimate David Hawkins Library' (10 volumes of classic segments from Hawkins' five NC programs plus bonus; 10h17m; live NC + Audible pages verified 2026-08-07). (c)2016 Dr. David Hawkins (P)2016 Nightingale-Conant. No existing master matches; unique compilation promoted per owner ruling 2026-08-07. |
| — | The Way to God: Advaita - The Way to God Through Mind (Audiobook) | lecture | Promoted edition audio of work w-advaita from candidate edition-audible-wtg-advaita: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | The Way to God: Realizing the Root of Consciousness (Audiobook) | lecture | Promoted edition audio of work w-realizing-root from candidate edition-audible-wtg-root: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | The Way to God: The Nature of Divinity vs. Religious Fallacy (Audiobook) | lecture | Promoted edition audio of work w-nature-of-divinity from candidate edition-audible-wtg-nature: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | The Wisdom of Dr. David R. Hawkins: Classic Teachings on Spiritual Truth and Enlightenment | book | Promoted from official candidate manual-veritas-53058: Official page identifies a book collecting ten core teachings and excerpts. |
| — | Transcending the Levels of Consciousness (Audiobook) | book | Promoted edition audio of work w-transcending-the-levels from candidate edition-audible-transcending: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Transcending the Levels of Consciousness Series: Perception vs. Essence (Audiobook) | lecture | Promoted edition audio of work w-tlc-perception from candidate edition-audible-tlc-perception: Audible audiobook edition; fuzzy title match to Perception vs Essence - VERIFY series part mapping.; candidate_title aligned to official Audible listing title (2026-08-07 distributor-naming audit) |
| — | Transcending the Mind Series: Emotions & Sensations (Audiobook) | lecture | Promoted edition audio of work w-emotions-sensations from candidate edition-audible-tms-emotions: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | Transcending the Mind Series: Identification & Illusion (Audiobook) | lecture | Promoted edition audio of work w-identification-illusion from candidate edition-audible-tms-id: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | Truth Vs Falsehood (Audiobook) | book | Promoted edition audio of work w-truth-vs-falsehood from candidate edition-audible-tvf: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Truth vs. Falsehood: The Art of Spiritual Discernment (CD & DVD set) | lecture | Promoted edition video of work w-truth-vs-falsehood from candidate edition-veritas-tvf-cddvd: Veritas product 1728; video/audio set edition of the work; inventory status unreviewed_official_product. |
| — | Unity Church of Sedona 2005 March (CD) | lecture | Promoted from official candidate manual-veritas-1546: Official page identifies a one-CD 67-minute March 2005 presentation. |
| — | Unity Church of Sedona 2006 June (CD) | lecture | Promoted from official candidate manual-veritas-1548: Official page identifies a one-CD 60-minute June 2006 presentation. |
| — | What is Real Success? | discussion | Promoted from official candidate manual-veritas-50488: Official page identifies a 2012 one-disc discussion/interview of approximately 60 minutes. |
| — | “In the World But Not of It” – Audio | lecture | Promoted edition audio of work w-in-the-world-but-not-of-it from candidate edition-veritas-itwbnoi-audio: Veritas product 1661; Nightingale-Conant 6-CD audio edition; inventory status matched_by_normalized_title. |

## Ledger items absent from the committed draft

| Raw row | Title | Type |
|---:|---|---|
| — | — |

## Field differences for matching provenance rows

Each entry is an exact current-draft value followed by the current ledger-derived value. Master IDs are included if they differ, because an identity change requires review.

No matching-record field differences were found.

## Downstream Pages impact

| `catalogue-meta.json` field | Committed Pages value | Ledger-projected value |
|---|---:|---:|
| `master_items` | 365 | 365 |
| `migrated_items` | 365 | 365 |
| `implemented_unreviewed` | 0 | 0 |

## Required resolution before rebuilding

1. Decide whether every draft-only record is an approved item, a documented manual candidate, or should remain outside the curated master.
2. Record approved changes to matching rows in the ledger or a versioned reviewed-overrides input; do not preserve them solely by editing generated draft CSV/JSON files.
3. Re-run this report until the reconciliation is understood and accepted.
4. Only then run `python build_research_master.py`, then `python build_catalogue_pages.py`, and verify both `--check` commands.

## Reproduce

```bash
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
python map_series_taxonomy.py --check
python sync_inventory_mirrors.py --check
```

`reconcile_research_master.py --check` verifies that this report still describes the current inputs. Omitting `--check` refreshes this Markdown report only; it does not change catalogue data.
