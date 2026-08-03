# Research Master Reconciliation Report

**Status:** Read-only comparison; no raw CSV, review ledger, master draft, or Pages JSON was changed to produce this report.

## Purpose

This report compares the committed `data/research_master_draft.csv` with the in-memory output of `build_research_master.py` using the current `migration_review_ledger.csv`. It also checks the paired master JSON and exclusions outputs, then shows the cascade to the Everything Pages dataset if the ledger projection were used. It is a review aid, not approval to overwrite either generated file.

## Summary

| Measure | Committed state | Current ledger projection |
|---|---:|---:|
| Research-master CSV records | 314 | 308 |
| Research-master JSON records | 308 | 308 |
| Research-master exclusion records | 59 | 66 |
| Draft-only CSV records without a matching ledger `item` | 6 | 0 |
| Ledger `item` records absent from CSV draft | 0 | 0 |
| Matched CSV records with one or more field differences | 36 | 0 |
| `docs/master.json` / ledger-projected Everything records | 354 | 348 |

The committed master **JSON already matches the current 308-record ledger projection**, while the committed master CSV has 314 rows and the exclusions CSV has 59 rows instead of the current 66-row projection. The CSV and JSON are therefore internally inconsistent before any new build is run.

The normal `python build_catalogue_pages.py --check` evaluates Pages files against the **committed** master CSV and may pass while this cascade differs. That is expected: this report is specifically identifying the upstream master/ledger divergence that must be resolved first.

## Draft-only CSV records requiring a provenance decision

Each record below is present in the committed draft CSV and therefore included by the current Everything build, but is not an `item` in the current ledger projection. Retain it only by recording its approval and durable provenance in the ledger or a reviewed overrides input; otherwise it will disappear on a normal master rebuild.

| Raw row | Title | Type | Notes |
|---:|---|---|---|
| 368 | Qualitative and Quantitative Analysis and Calibration of the Level of Human Consciousness | book | Original raw text: DISSERTATION ❌❌❌ |
| 371 | Dialogues on Consciousness and Spirituality | book | Original raw text: Dialogues on Consciousness and Spirituality: WHAT IS THIS ⚠️⚠️⚠️. Discord note: SETH HAS IT. |
| 375 | The Scorpion Book | book | Original raw text: scorpion book |
| 376 | Orthomolecular Psychiatry | book | Original raw text: orthomolecular book. Owned: ✅ |
| 376 | Orthomolecular Psychiatry | book | Original raw text: orthomolecular book. Owned: ✅ |
| — | Power vs Force (Original old edition, non B&W cover) | book | Extracted from explicit research request: original/old edition of Power vs Force without the black and white cover. |

## Ledger items absent from the committed draft

| Raw row | Title | Type |
|---:|---|---|
| — | — |

## Field differences for matching provenance rows

Each entry is an exact current-draft value followed by the current ledger-derived value. UUIDs are included if they differ, because an identity change requires review.

### Raw row 134 — Live Your Life Like a Prayer

- `source_url_veritas`: `https://veritaspub.com/product/how-to-live-your-life-like-a-prayer-2/` → `https://veritaspub.com/product/2006-11-live-your-life-like-a-prayer-nov-2006/`

### Raw row 260 — A-01 Office Series-Stress.mp4

- `source_url_veritas`: `https://veritaspub.com/product/stress/` → `∅`

### Raw row 261 — A-02 Office Series-Health.mp4

- `source_url_veritas`: `https://veritaspub.com/product/health/` → `∅`

### Raw row 262 — A-03 Office Series-Spiritual First Aid.mp4

- `source_url_veritas`: `https://veritaspub.com/product/spiritual-first-aid-2/` → `∅`

### Raw row 263 — A-04 Office Series-Sexuality.mp4

- `source_url_veritas`: `https://veritaspub.com/product/sexuality-2/` → `∅`

### Raw row 264 — A-05 Office Series-The Aging Process.mp4

- `source_url_veritas`: `https://veritaspub.com/product/the-aging-process/` → `∅`

### Raw row 265 — A-06 Office Series-Handling Major Crises.mp4

- `source_url_veritas`: `https://veritaspub.com/product/handling-major-crises-2/` → `∅`

### Raw row 266 — A-07 Office Series-Worry Fear and Anxiety.mp4

- `source_url_veritas`: `https://veritaspub.com/product/worry-fear-and-anxiety-2/` → `∅`

### Raw row 267 — A-08 Office Series-Pain and Suffering.mp4

- `source_url_veritas`: `https://veritaspub.com/product/pain-and-suffering/` → `∅`

### Raw row 268 — A-09 Office Series-Losing Weight.mp4

- `source_url_veritas`: `https://veritaspub.com/product/losing-weight/` → `∅`

### Raw row 269 — A-10 Office Series-Depression.mp4

- `source_url_veritas`: `https://veritaspub.com/product/depression/` → `∅`

### Raw row 270 — A-11 Office Series-Illness and Self-Healing.mp4

- `source_url_veritas`: `https://veritaspub.com/product/illness-and-self-healing/` → `∅`

### Raw row 271 — A-12 Office Series-Alcoholism.mp4

- `source_url_veritas`: `https://veritaspub.com/product/alcoholism/` → `∅`

### Raw row 272 — B-01 Office Series-Drug Addiction and Alcoholism....mp4

- `source_url_veritas`: `https://veritaspub.com/product/drug-addiction-and-alcoholism/` → `∅`

### Raw row 274 — B-03 Office Series-A Map Of Consciousness.mp4

- `source_url_veritas`: `https://veritaspub.com/product/map-of-consciousness-dr-david-hawkins/` → `∅`

### Raw row 275 — B-04 Office Series-Cancer.mp4

- `source_url_veritas`: `https://veritaspub.com/product/cancer/` → `∅`

### Raw row 277 — B-06 Office Series-Death and Dying.mp4

- `source_url_veritas`: `https://veritaspub.com/product/death-and-dying/` → `∅`

### Raw row 297 — Audio 27. Golden Word Book Signing – Audio

- `source_url_veritas`: `https://veritaspub.com/product/https-veritaspub-com-product-golden-word-book-signing-january-13-2007/` → `∅`

### Raw row 316 — How to See the Reality of Life.mp4

- `source_url_veritas`: `https://veritaspub.com/product/how-to-see-the-reality-of-life/` → `∅`

### Raw row 317 — Improving Your Relationships.mp4

- `source_url_veritas`: `https://veritaspub.com/product/improving-your-relationships-2012/` → `∅`

### Raw row 319 — The Importance of Family.mp4

- `source_url_veritas`: `https://veritaspub.com/product/the-importance-of-family-2014/` → `∅`

### Raw row 320 — What is Meant by Spiritual.mp4

- `source_url_veritas`: `https://veritaspub.com/product/what-is-meant-by-spiritual-2012/` → `∅`

### Raw row 322 — What You are Changes the World.mp4

- `source_url_veritas`: `https://veritaspub.com/product/what-you-are-changes-the-world-2/` → `∅`

### Raw row 325 — Power vs Force

- `source_url_audible`: `https://www.audible.com/pd/Power-vs-Force-Audiobook/B002V5GOH0` → `∅`

### Raw row 326 — The Eye of the I

- `source_url_audible`: `https://www.audible.com/pd/The-Eye-of-the-I-Audiobook/1401962459` → `∅`

### Raw row 328 — Truth vs Falsehood

- `source_url_veritas`: `https://veritaspub.com/product/truth-vs-falsehood-the-art-of-spiritual-discernment/` → `∅`
- `source_url_audible`: `https://www.audible.com/pd/Truths-vs-Falsehood-Audiobook/B00NWS4SQO` → `∅`

### Raw row 329 — Letting Go

- `source_url_veritas`: `https://veritaspub.com/product/letting-go-the-pathway-of-surrender-book/` → `∅`
- `source_url_audible`: `https://www.audible.com/pd/Letting-Go-Audiobook/B00ZJFQN9I` → `∅`

### Raw row 330 — Healing and Recovery

- `source_url_veritas`: `https://veritaspub.com/product/healing-achieving-total-wellness-through-higher-levels-of-consciousness-by-david-r-hawkins-m-d-ph-d/` → `∅`
- `source_url_audible`: `https://www.audible.com/pd/Healing-and-Recovery-Audiobook/1401962440` → `∅`

### Raw row 331 — Discovery of the Presence of God

- `source_url_veritas`: `https://veritaspub.com/product/discovery-of-the-presence-of-god-devotional-nonduality-sc/` → `∅`

### Raw row 333 — Transcending the Levels of Consciousness

- `source_url_audible`: `https://www.audible.com/pd/Transcending-the-Levels-of-Consciousness-Audiobook/1401961878` → `∅`

### Raw row 334 — The Map of Consciousness Explained

- `source_url_veritas`: `https://veritaspub.com/product/the-map-of-consciousness-explained/` → `∅`

### Raw row 335 — Success Is for You

- `source_url_veritas`: `https://veritaspub.com/product/success-is-for-you-using-heart-centered-power-principles-for-lasting-abundance-and-fulfillment/` → `∅`

### Raw row 337 — Daily Reflections

- `source_url_veritas`: `https://veritaspub.com/product/daily-reflections-from-dr-david-r-hawkins-365-contemplations-on-surrender-healing-and-consciousness/` → `∅`

### Raw row 341 — In the World, But Not of It

- `source_url_veritas`: `https://veritaspub.com/product/in-the-world-but-not-of-it-cd/` → `∅`
- `source_url_audible`: `https://www.audible.com/pd/In-the-World-but-Not-of-It-Audiobook/B00NMUQ8DS` → `∅`

### Raw row 342 — The Highest Level of Enlightenment

- `source_url_veritas`: `https://veritaspub.com/product/the-highest-level-of-enlightenment/` → `∅`
- `source_url_audible`: `https://www.audible.com/pd/The-Highest-Level-of-Enlightenment-Audiobook/B00O3I950G` → `∅`

### Raw row 349 — Beyond Illusion: Exploring Perception, Ego, and Meditation on the Path to Truth

- `source_url_veritas`: `https://veritaspub.com/product/beyond-illusion-exploring-perception-ego-and-meditation-on-the-path-to-truth/` → `∅`

## Downstream Pages impact

| `catalogue-meta.json` field | Committed Pages value | Ledger-projected value |
|---|---:|---:|
| `master_items` | 354 | 348 |
| `migrated_items` | 314 | 308 |
| `implemented_unreviewed` | 42 | 42 |

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
