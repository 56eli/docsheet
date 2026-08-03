# Edition Model Proposal — one row per work × carrier (book / audio / video)

**Prepared:** 2026-08-03
**Status:** ⏳ Design proposal — no data changed. Owner direction: the project
must clearly distinguish carrier editions (book, audio, video) of the same
work and reflect that logic through the whole project.
**Related:** `ITEM_TYPE_CLASSIFICATION_PROPOSAL.md` (content class vs carrier),
`PRODUCT_RELATIONSHIP_SCHEMA.md`, `VERITAS_PRODUCT_MAPPING.md`,
`NEXT_AGENT_HANDOFF.md` §5 (binding data rules).

---

## 1. The oversight, stated precisely

Today the master records **one row per physical item part**, not per edition.
For most lectures that is fine (a DVD part *is* the carrier unit), but for
works that exist in **several carriers**, the extra editions are *collapsed
into the row or hidden in relationships* instead of being their own records:

| Edition of the work | Where it lives today | Where it should live |
|---|---|---|
| Book (Veritas / Hay House) | Master row (`item_type=book`, `format=book`) | Master row |
| Audiobook (Audible / Veritas audio product) | `source_url_audible` cell on the book row, or a `related_material` row, or an inventory row | **its own master row** (`format=audio`) |
| Video / DVD set (Veritas) | `related_material` row, or DVD part rows | its own master row (`format=DVD`) or part rows under one work |

### Worked example — Truth vs Falsehood (master 289, as the owner flagged)

- Master row **289**: `item_type=book`, `format=book`, Veritas URL → product
  **50398** `Truth vs. Falsehood: How to Tell the Difference (Book)`,
  `source_url_audible` → the **audiobook** listing.
- Related product **1728** `Truth vs. Falsehood: The Art of Spiritual
  Discernment (CD & DVD set)` is a `related_material` relationship — the
  **video/audio set edition** is not a row.
- So one work appears as book **and** audiobook **and** CD&DVD set — i.e. the
  user's "three times" — while only one row exists. The other two editions
  are visible only as a URL cell and a relationship row.

### Quantified scope (committed data, 2026-08-03)

| Evidence of collapsed editions | Count | Where |
|---|---:|---|
| Book rows with an Audible audiobook URL | 7 | 286, 287, 289, 290, 291, 294, 300 |
| `related_material` rows that are other editions of the same work (audio/CD/DVD/book) | 6 | 289→1728, 291→1695, 300→1661, 301→1742, 202→1542, 202→50411 |
| Audible inventory rows (audiobook editions) | 26 | `data/audible_official_products.csv` (17 `matched_by_title`, 6 `unreviewed`, 3 `possible_related_match`) |
| Hay House rows (paperback/eBook/audio/guided journal/card deck) | 24 | `data/hayhouse_official_products.csv` |
| Veritas non-primary products (audio/CD/DVD editions, unique items) | 28 | `unreviewed` 4, `unique_item` 9, `compilation_or_new_edition` 15 |
| Works with the same title as another carrier row (e.g. book 286 *Power vs Force* vs lecture 202) | several | e.g. 202↔286, 289, 291, 300, 301 |

Lecture DVD parts (65 title groups × ~3 parts, e.g. rows 1–3 "Causality…")
are **not** duplicates: they are parts of one video edition and must keep
their per-part identity (ownership, codes, relationships).

---

## 2. Target model

```
work  (one conceptual work, e.g. "Truth vs Falsehood")
 └── editions  (one master row per work × carrier)
      ├── book edition      item_type=book      format=book    (Veritas 50398 / Hay House)
      ├── audiobook edition item_type=book      format=audio   (Audible / Veritas 1542-style)
      └── video edition     item_type=lecture   format=DVD     (Veritas 1728; N part rows)
```

Mechanically:

1. **`work_id`** — a stable identity column on every master row. Rows of the
   same work share it. Minted by a **reviewed input** (`data/work_families.csv`:
   `work_id`, canonical work title, member master rows / product IDs, evidence),
   *not* by title matching alone (C2 rule: title matching caused four
   wrong-edition links). Proposal generation can be deterministic
   (`generate_work_families.py` style) with an approval queue, mirroring the
   series-taxonomy pattern.
2. **Edition rows** — new master rows created from **reviewed edition
   candidates** (`data/edition_candidates.csv` + promotion registry, reusing
   the candidate/promotion pattern). Each edition row carries its own
   `source_url_*`, `owned`, `catalog_code` (when typed+year), `format`, and
   relationships. Provenance for non-raw rows already has precedent
   (`raw_row_number = candidate:manual-veritas-XXXXX`).
3. **Field semantics unchanged** — `item_type` = content class
   (`lecture`/`book`/`discussion`), `format` = carrier (`book`/`audio`/`DVD`/
   `CD`/`streaming`). This is exactly the rule already documented in README
   and enforced since 2026-08-03; the edition model *uses* it instead of
   letting carriers hide in URL cells.
4. **Relationships** — primary product = the edition's own product; same-work
   cross-carrier links become `same_material_edition` (an existing controlled
   value, currently unused) between edition rows, or stay `related_material`
   where evidence is weaker.
5. **Views/counts/docs** — Everything view gains the `work_id`/edition label;
   README/handoff counts and the documentation-currency tests follow the
   generated data.

### Open decisions (need owner ruling before implementation)

| # | Decision | Options |
|---|---|---|
| D1 | **Lecture part granularity** | (a) keep per-part rows under one `work_id` + one video edition (recommended: preserves IDs/codes/ownership/relationships); (b) collapse parts into one row per video edition, part info into `format_detail`/notes |
| D2 | **Source of edition rows** | (a) reviewed `edition_candidates.csv` + promotion registry (recommended, same boundary as candidates); (b) auto-mint rows from Audible/HH/Veritas inventories with a review queue |
| D3 | **Existing collapsed URLs** | The 7 `source_url_audible` cells: (a) become the audiobook edition row's source and are cleared from the book row (recommended); (b) stay as convenience links on the book row |
| D4 | **`work_id` minting** | (a) reviewed `work_families.csv` input with generated proposals (recommended); (b) purely manual ledger column |
| D5 | **First batch scope** | e.g. the 7 Audible-linked books (small, well-evidenced) before the 26-row Audible / 24-row Hay House inventories |

### Suggested phasing

1. **Phase 1 — model plumbing:** `work_id` + `work_families.csv` proposal
   generator + review queue + master/Pagestests, no data change until the
   first families are approved.
2. **Phase 2 — first edition batch:** audiobook rows for the 7 Audible-linked
   books (and the 6 related-material audio/CD/DVD editions) via
   `edition_candidates.csv`, owner approval per row.
3. **Phase 3 — inventory coverage:** Audible (26), Hay House (24), and the
   remaining Veritas audio editions, each as reviewed batches.
4. **Phase 4 — docs/UI:** edition labels in the spreadsheet, README/handoff
   counts, schema docs, tests.

Nothing in this proposal changes raw evidence, the ledger's part rows, or the
review boundary: every new row is approved before it becomes master data.
