# Research Master Reconciliation Report

**Status:** Read-only comparison; no raw CSV, review ledger, master draft, or Pages JSON was changed to produce this report.

## Purpose

This report compares the committed `data/research_master_draft.csv` with the in-memory output of `build_research_master.py` using the current `migration_review_ledger.csv`. It also checks the paired master JSON and exclusions outputs, then shows the cascade to the Everything Pages dataset if the ledger projection were used. It is a review aid, not approval to overwrite either generated file.

## Summary

| Measure | Committed state | Current ledger projection |
|---|---:|---:|
| Research-master CSV records | 356 | 356 |
| Research-master JSON records | 356 | 356 |
| Research-master exclusion records | 68 | 68 |
| Draft-only CSV records without a matching ledger `item` | 50 | 0 |
| Ledger `item` records absent from CSV draft | 0 | 0 |
| Matched CSV records with one or more field differences | 0 | 0 |
| `docs/master.json` / ledger-projected Everything records | 376 | 376 |

The checked outputs are not yet fully reconciled. Review the differences below before rebuilding so reviewed additions are not lost.

The normal `python build_catalogue_pages.py --check` evaluates Pages files against the **committed** master CSV and may pass while this cascade differs. This report identifies the upstream master/ledger divergence that must be resolved first.

## Draft-only CSV records requiring a provenance decision

Each record below is present in the committed draft CSV and therefore included by the current Everything build, but is not an `item` in the current ledger projection. Retain it only by recording its approval and durable provenance in the ledger or a reviewed overrides input; otherwise it will disappear on a normal master rebuild.

| Raw row | Title | Type | Notes |
|---:|---|---|---|
| — | Book of Slides (The Complete Collection) | book | Promoted from official candidate manual-veritas-38608: Official page identifies a 655-page book compendium of lecture slides from 2002–2011. |
| — | Compassion (Audiobook) | lecture | Promoted edition audio of work w-compassion from candidate edition-audible-compassion: Audible audiobook edition of the lecture work; Audible inventory row matched_by_title. |
| — | Devotion to Truth Talk | lecture | Promoted from official candidate manual-veritas-55473: Official page identifies a 2003 On-the-Road talk and makes the full lecture available through streaming video. |
| — | Devotional Nonduality Intensive: Alignment (Audiobook) | lecture | Promoted edition audio of work w-alignment from candidate edition-audible-dni-alignment: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | Devotional Nonduality Intensive: Intention (Audiobook) | lecture | Promoted edition audio of work w-intention from candidate edition-audible-dni-intention: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | Don’t Set Sail Without A Compass – Audio | lecture | Promoted from official candidate manual-veritas-1792: Official page identifies a one-CD 67-minute audio product. |
| — | Giving Up Illness through A Course in Miracles© – Audio | lecture | Promoted from official candidate manual-veritas-1544: Official page identifies a three-CD 3h45m audio presentation. |
| — | Healing and Recovery (Audiobook) | book | Promoted edition audio of work w-healing-and-recovery from candidate edition-audible-healing: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Healing: Achieving Total Wellness Through Higher Levels of Consciousness | lecture | Promoted edition audio of work w-healing-and-recovery from candidate edition-veritas-healing-audio: Veritas product 1695; audio edition of the work; inventory status unreviewed_official_product. |
| — | In The World But Not Of It (Audiobook) | book | Promoted edition audio of work w-in-the-world-but-not-of-it from candidate edition-audible-itwbnoi: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Letting Go (Audiobook) | book | Promoted edition audio of work w-letting-go from candidate edition-audible-lettinggo: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Life with “Doc” My Husband & My Teacher, Dr. David R. Hawkins | book | Promoted from official candidate manual-veritas-53036: Official page identifies Susan Hawkins’s memoir and inside account. |
| — | Live Life As A Prayer (Audio) | lecture | Promoted edition audio of work w-live-prayer from candidate edition-hh-liveprayer: Hay House audio edition of the lecture work; Hay House inventory row unreviewed_official_product. |
| — | Mind, Heart and Service: The Pathway of Devotional Non-Duality | lecture | Promoted from official candidate manual-veritas-54219: Official page identifies a 2003 Science of Mind church lecture available through streaming video. |
| — | Peace is the Natural State | lecture | Promoted from official candidate manual-veritas-1814: Official page identifies an On-the-Road audio product. |
| — | Permanent Inner Peace (2012) | discussion | Promoted from official candidate manual-veritas-50485: Official page identifies a 2012 discussion/interview product. |
| — | Power vs. Force (Audiobook) | book | Promoted edition audio of work w-power-vs-force from candidate edition-audible-pvf: Audible audiobook edition of the Power vs Force work; Audible inventory row matched_by_title. |
| — | Power vs. Force Audio Book | book | Promoted edition audio of work w-power-vs-force from candidate edition-veritas-pvf-audiobook: Veritas product 1542; audiobook edition of the Power vs Force work; currently related_material on lecture 202 - REQUIRES RULING on family placement. |
| — | Progressive Levels of Consciousness | lecture | Promoted from official candidate manual-veritas-53277: Official page identifies an On-the-Road UK talk available through streaming video. |
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
| — | The Ego is Not the Real You | book | Promoted from official candidate manual-veritas-47979: Official page identifies a paperback collection of selected Hawkins teachings and quotes. |
| — | The Essence of Letting Go: A Living Transmission of Truth | lecture | Promoted from official candidate manual-veritas-55576: Official page identifies an original 12-session audio program drawing on multiple earlier teachings. |
| — | The Eye of the I (Audiobook) | book | Promoted edition audio of work w-eye-of-the-i from candidate edition-audible-eye: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | The Highest Level of Enlightenment (Audiobook) | book | Promoted edition audio of work w-highest-level-of-enlightenment from candidate edition-audible-hle: Audible audiobook edition of the book; Audible inventory row matched_by_title. |
| — | The Highest Level of Enlightenment – Audio | lecture | Promoted edition audio of work w-highest-level-of-enlightenment from candidate edition-veritas-hle-audio: Veritas product 1742; audio edition (Veritas sells this work audio-only); inventory status unreviewed_official_product. |
| — | The Man Who Mapped Consciousness: Life and Legacy of Dr. David R. Hawkins | book | Promoted from official candidate manual-veritas-55425: Official page identifies a biography of Hawkins’s life and legacy. |
| — | The Power of Love: A Transformed Heart Changes the World | book | Promoted from official candidate manual-veritas-43146: Official page identifies Fran Grace’s book dedicated to Hawkins and Susan, with interview material. |
| — | The Way to God: Advaita - The Way to God Through Mind (Audiobook) | lecture | Promoted edition audio of work w-advaita from candidate edition-audible-wtg-advaita: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | The Way to God: Realizing the Root of Consciousness (Audiobook) | lecture | Promoted edition audio of work w-realizing-root from candidate edition-audible-wtg-root: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | The Way to God: The Nature of Divinity vs. Religious Fallacy (Audiobook) | lecture | Promoted edition audio of work w-nature-of-divinity from candidate edition-audible-wtg-nature: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | The Wisdom of Dr. David R. Hawkins: Classic Teachings on Spiritual Truth and Enlightenment | book | Promoted from official candidate manual-veritas-53058: Official page identifies a book collecting ten core teachings and excerpts. |
| — | Transcending the Levels of Consciousness (Audiobook) | book | Promoted edition audio of work w-transcending-the-levels from candidate edition-audible-transcending: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Transcending the Levels of Consciousness Series: Perception (Audiobook) | lecture | Promoted edition audio of work w-tlc-perception from candidate edition-audible-tlc-perception: Audible audiobook edition; fuzzy title match to Perception vs Essence - VERIFY series part mapping. |
| — | Transcending the Mind Series: Emotions & Sensations (Audiobook) | lecture | Promoted edition audio of work w-emotions-sensations from candidate edition-audible-tms-emotions: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | Transcending the Mind Series: Identification & Illusion (Audiobook) | lecture | Promoted edition audio of work w-identification-illusion from candidate edition-audible-tms-id: Audible audiobook edition of the lecture part; Audible inventory row matched_by_title. |
| — | Truth Vs Falsehood (Audiobook) | book | Promoted edition audio of work w-truth-vs-falsehood from candidate edition-audible-tvf: Audible audiobook edition; Audible inventory row matched_by_title. |
| — | Truth vs. Falsehood: The Art of Spiritual Discernment (CD & DVD set) | lecture | Promoted edition video of work w-truth-vs-falsehood from candidate edition-veritas-tvf-cddvd: Veritas product 1728; video/audio set edition of the work; inventory status unreviewed_official_product. |
| — | Unity Church of Sedona 2005 March (CD) | lecture | Promoted from official candidate manual-veritas-1546: Official page identifies a one-CD 67-minute March 2005 presentation. |
| — | Unity Church of Sedona 2006 June (CD) | lecture | Promoted from official candidate manual-veritas-1548: Official page identifies a one-CD 60-minute June 2006 presentation. |
| — | What is Real Success? (2012) | discussion | Promoted from official candidate manual-veritas-50488: Official page identifies a 2012 one-disc discussion/interview of approximately 60 minutes. |
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
| `master_items` | 376 | 376 |
| `migrated_items` | 356 | 356 |
| `implemented_unreviewed` | 22 | 22 |

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
```

`reconcile_research_master.py --check` verifies that this report still describes the current inputs. Omitting `--check` refreshes this Markdown report only; it does not change catalogue data.
