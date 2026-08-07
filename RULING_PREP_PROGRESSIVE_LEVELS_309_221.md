# Ruling Prep — Product 53277 / Master 309 vs Master 221 ("Progressive Levels of Consciousness")

**Prepared:** 2026-08-07 (branch `arena/019fdd68-docsheet`)
**Status:** Evidence-only — no data changed. Awaiting owner ruling (question at the end).

---

## TL;DR

Veritas product **53277 ("Progressive Levels of Consciousness") is the Oxford, England talk** — its own description says so. That talk already exists in the catalogue as master **221** (*"Progressive Levels of Consciousness - A Special Talk Presented in Oxford (2003)"*). Master **309** (*"Progressive Levels of Consciousness"*) was minted on 2026-08-03 **from that same product listing** (candidate `manual-veritas-53277`), so **309 is a duplicate of 221** with a wrong year (2023 = storefront listing date, not the 2003 recording). Recommended ruling: **merge 309's links into 221 and exclude 309 as a duplicate.**

## Evidence

### 1 — The live product page (fetched 2026-08-07)

`https://veritaspub.com/product/progressive-levels-of-consciousness/` ($1.00, category *On the Road - Talk Series*, published 2023-09-17) — Description, verbatim:

> "Dr. Hawkins traveled to the UK to give this uplifting and informative talk. **Set in Oxford, England**, with his work being new and exciting, Dr. Hawkins presents his Map of Consciousness®, Levels of Consciousness, and explains the difference between Power and Force."

The store carries **exactly one** "Progressive Levels" product (full WP-API inventory, 191 products, re-fetched 2026-08-07 — no second listing); Audible carries none (checked committed Audible inventory).

### 2 — The two master rows

| Field | Master 221 | Master 309 |
|---|---|---|
| Title | `Progressive Levels of Consciousness - A Special Talk Presented in Oxford (2003)` | `Progressive Levels of Consciousness` |
| Origin | raw archive row (ledger) | minted 2026-08-03 from candidate `manual-veritas-53277` (created from product 53277 itself) |
| Year | **2003** (`Ledger: recording date 2003`) | **2023-09** (`Manual candidate blank → 2023` = the product's *storefront listing* date — violates the recording-year rule) |
| Format | `streaming` | `DVD` + `streaming video` |
| Veritas link | — | `…/product/progressive-levels-of-consciousness/` (primary, drives 1 derived relationship) |
| Reference URL | — | `…/progressive-levels-of-consciousness/` (streaming page, via approved streaming overlay) |
| Catalogue code | `LECTURE-2003-019` | — |
| Work | `w-progressive-levels-of-consciousness-a-sp` | `w-progressive-levels-of-consciousness` |
| Series | On The Road Talk Series | On The Road Talk Series |

### 3 — How the duplicate happened

1. The archive's raw row (221) names the talk by its full Oxford title — no verbatim title match to the short store listing.
2. On 2026-08-03 the store listing 53277 became a manual candidate with notes *"Official page identifies an On-the-Road UK talk available through streaming video"* and was promoted as master 309; the candidate flow assigns the product's storefront year (2023) when the candidate year is blank.
3. Nobody (including prior audits) had yet read the product *description* against 221; the title-only comparison (§1) keeps them looking like different talks. This was already on the suspect list — the 2026-08-04 post-2012 audit flagged 309's 2023 year as a release date, pending its recording year.

## Impact of the recommended ruling (merge into 221, exclude 309)

- Master **366 → 365** (310 lecture → 309); duplicate-exclusion precedent follows 246/281/284.
- 221 gains: Veritas primary link (53277), its streaming reference URL, and the derived primary relationship (relationships stay **343**: derived moves 309 → 221).
- 309's format/year anomaly disappears; the last "year > 2012 release-date" flag in the On-the-Road family resolves (recording year = 2003).
- Candidate layer: `manual-veritas-53277` becomes *promoted-as-duplicate* (un-mint UUID 309); work families collapse to one work (member 221); taxonomy row 53277 → 221 (series unchanged — both On The Road Talk Series).
- Tests/docs counts update (master 365, promoted candidates 40 → 39, work families 342 → 341 members).

## Alternative readings (checked and refuted)

- *"309 is a different Progressive Levels talk."* — No: exactly one store listing exists, its description names Oxford explicitly, and 309's entire identity is that listing.
- *"Keep 309, exclude 221."* — Loses the raw-derived identity, the correct 2003 recording year, and the catalogue code; the duplicate-exclusion precedent (246/281/284) kept the better-provenanced record.

## Ruling needed from the owner

Execute **Option A** (merge into 221, exclude 309 as duplicate) or **Option B** (keep both unchanged). If A, I will implement it the same day with full regeneration, tests, and doc sync.
