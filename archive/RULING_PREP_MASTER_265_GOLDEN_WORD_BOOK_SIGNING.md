# Ruling Prep — Master 265 (Golden Word Book Signing – Audio)

**Prepared:** 2026-08-08 · **Status:** awaiting owner ruling · **Branch:** `arena/019fe098-docsheet`
**Audit reference:** `FULL_STACK_AUDIT_2026-08-08.md`, findings **C1** and **C2**.
**Rule of thumb applied:** edit reviewed inputs only (`migration_review_ledger.csv`,
`data/filename_proposal_YYYYMM.csv`, `data/research_master_source_overrides.csv`,
`build_research_master.py`), regenerate, then re-run every `--check` + tests.
Never hand-edit `data/research_master_draft.*` or `docs/*.json`.

---

## 1. What master 265 is today

| Field | Value |
|---|---|
| uuid | 265 |
| work_id | `w-golden-word-book-signing-audio` (single-member family, approved) |
| title | `Golden Word Book Signing – Audio` |
| item_type / series | lecture / Media Miscellaneous |
| year / month / year_source | 2007 / 01 / Ledger: recording date 2007 |
| **format / format_detail** | **`audiobook` / (empty)** ← candidate defect |
| **source_url_veritas** | **`https://veritaspub.com/product/https-veritaspub-com-product-golden-word-book-signing-january-13-2007/`** ← candidate defect |
| source_url_audible / amazon / reference_url_1 / notes | all empty |
| proposed_filename | `2007-01 - Golden Word Book Signing.m4b` (audiobook extension) |
| source (ledger raw) | row 297 (raw title `Audio 27. Golden Word Book Signing – Audio`, `raw_we_have ✅`) |
| inventory match | product 1552, `matched_by_primary_source` (URL-equal) |

## 2. Evidence (live-verified 2026-08-08 via veritaspub.com)

1. **WP-API product search** (`?search=golden word book`): exactly one product,
   id **1552**, whose stored `slug` and `link` are literally the mangled string
   `https-veritaspub-com-product-golden-word-book-signing-january-13-2007`.
   **No clean-slug duplicate exists.**
2. **Product 1552 page** resolves fine at the mangled URL and states:
   - **"Three Compact Disc Set"** · Running time **2 Hours 56 Minutes** ·
     Publisher Veritas Publishing · SKU `am_gwbs` · $29.95
   - The page itself links the **Amazon/Audible audiobook**
     (`amazon.com/.../B00KZ1QMX8`) as "Also available".
3. **No reviewed inventory row** exists for this title in
   `data/audible_official_products.csv`, `data/hayhouse_official_products.csv`,
   `data/edition_candidates.csv`, or `data/manual_master_candidates.csv` — so an
   audiobook edition cannot be minted from reviewed inventory today.

### Interpretation

- **C1 (URL):** the malformed URL is the **publisher's own canonical link** for
  product 1552, faithfully mirrored by the catalogue (an approved 2026-08-03
  override row preserved it). It is *not* a catalogue corruption, but it is the
  only malformed URL in the master and it is what visitors click.
- **C2 (format):** the official carrier of product 1552 is **CD (3-disc set)**;
  master 265's `format=audiobook` was produced by the format-inference rule
  (`"– audio" in official_title → audiobook`) because the ledger left
  `proposed_format` blank. The inference rule is too broad (latent defect).

### Evidence addendum — the Amazon/Audible angle (2026-08-08, after owner comment)

The Veritas page's "Available at amazon print, audio and kindle" button points
at the **Audible audiobook** of the same event (ASIN `B00KZ1QMX8`, "Audible
Audio Edition", release 2014-06-13, 2h56m — same running time as the CD set).
Follow-up verification:

- **Audible US (`audible.com/pd/.../B00KZ1QMX8`): "Sorry, it looks like this
  title is no longer available."** — the US audiobook listing is **de-listed**.
- Amazon.com still displays the ASIN as an Audible audiobook listing.
- **Audible India (`audible.in/pd/.../B07JGMY5W4`): active** (₹481, publisher
  Veritas Publishing, same 2h56m recording).

Consequence for Option B: minting a new audiobook master row now would point at
a US listing that is unavailable — recreating the "dead link in the catalogue"
problem this memo exists to fix. The audiobook lead belongs **outside the
master** (in `data/research_manual_leads.csv`) until a live, reviewed US
listing exists (repo rule: reviewed inventory rows only).

---

## 3. Recommended ruling — **Option A (minimal, apply now)**

Keep the publisher's URL as primary (it is the official, working link; a
"cleaner" URL is not canonical), correct the carrier to CD, document the
evidence. Detailed changes below — each is an input edit, no generated file is
touched by hand.

### A1 — `migration_review_ledger.csv`, row 297 (input change)

| Column | From | To |
|---|---|---|
| `proposed_format` | *(empty)* | `CD` |
| `proposed_format_detail` | *(empty)* | `three CD; 2h56m` |
| `review_reason` | `Item candidate indicated by ownership status and/or legacy tempid.` | append: ` Official Veritas product 1552 page: "Three Compact Disc Set", 2h56m (live-verified 2026-08-08); carrier corrected from audiobook.` |

(The builder copies `proposed_format`/`proposed_format_detail` into the master
row at line 1203–1204; format inference only fills blanks, so it will no longer
override.)

### A2 — `data/filename_proposal_YYYYMM.csv`, row 265 (input change)

| Column | From | To |
|---|---|---|
| `format` | `audiobook` | `CD` |
| `proposed_filename` | `2007-01 - Golden Word Book Signing.m4b` | `2007-01 - Golden Word Book Signing.mp3` |
| `proposed_filename_display` | `2007-01 - Golden Word Book Signing.m4b` | `2007-01 - Golden Word Book Signing.mp3` |

Convention check: every CD-carrier row uses `.mp3` (e.g. master 356
`2014-05 - Don't Set Sail Without A Compass – Audio.mp3`, masters 353/354/355);
every audiobook row uses `.m4b`. 265 stays globally unique either way (v4.1
guard unaffected).

### A3 — `data/research_master_source_overrides.csv`, row for raw 297 (input change)

| Column | From | To |
|---|---|---|
| `review_reason` | `Preserve current master association verified against the official inventory during reconciliation.` | `Preserve current master association verified against the official inventory during reconciliation. 2026-08-08: publisher-verbatim slug for product 1552 confirmed via live WP-API (no clean-slug equivalent exists); keep as-is, do not "fix".` |
| `evidence_source` | `data/veritas_official_products.csv` | `data/veritas_official_products.csv; live WP-API product search + product page, 2026-08-08` |

### A4 — `build_research_master.py` — tighten `infer_format_from_official_source` (code fix, latent defect)

Current (≈line 384–393 of the function):

```python
if any(k in slug for k in ("question-answer", "question-and-answer", "q&a")):
    return "streaming"
if "audio" in slug or "– audio" in ot or " audio" in ot:
    return "audiobook"
if "book" in slug or "(book)" in ot:
    return "book"
```

Proposed replacement:

```python
# Malformed/verbatim publisher slugs (e.g. product 1552's
# "https-veritaspub-com-product-..." link) carry no carrier signal — never
# guess from them; leave the format blank for manual review.
if "https-" in slug or "https" == slug[:5]:
    return ""

# CD markers in the slug or official title beat the generic "– Audio" title
# fallback (Veritas titles many 3-CD audio programs "… – Audio").
cd_tokens = {"cd", "cds", "cd-set", "cdset"}
if any(seg in cd_tokens for seg in slug.split("-")) or \
   re.search(r"\bcd set\b|\bcds\b|compact disc|disc set", ot):
    return "CD"

if "audio" in slug or "– audio" in ot or " audio" in ot:
    return "audiobook"
if "book" in slug or "(book)" in ot:
    return "book"
```

Behavior today: only master 265 would have been affected; with A1 it is no
longer blank so the rule is inert on the current master — the patch is purely
defensive for future promotions/backfills (e.g. product 1792/1544-style CD
titles that arrive without a hand-set format).

### A5 — Tests (add to `tests/test_pipeline.py`)

1. `test_format_inference_cd_markers_beat_audio_title` — product whose slug
   contains a `cd` token and whose title ends `– Audio` → `CD`.
2. `test_format_inference_malformed_slug_returns_blank` — product with the
   `https-veritaspub-com-...` slug shape → `""` (no guess).

### A6 — `data/research_manual_leads.csv` — track the audiobook lead (see §4)

Add one row per §4 so the de-listed audiobook is not forgotten and never
silently minted from an unavailable listing.

### A7 — Documentation

- `FULL_STACK_AUDIT_2026-08-08.md`: mark C1/C2 as **ruled** with a pointer to
  this memo (after approval + apply).
- `NEXT_AGENT_HANDOFF.md`: add a session line per the house-keeping rule.

---

## 4. Option B (full edition split — revised 2026-08-08, NOT recommended now)

Under the strict work×carrier edition model, the *model-correct* end state is
two rows: **265 = Veritas 3-CD edition** (`format=CD`, URL as-is) **plus a new
audiobook edition row** minted through `data/edition_candidates.csv` →
`data/edition_promotions.csv` (new master UUID, work-family row,
filename-proposal row, `format_detail="Audiobook"`).

**Revised assessment after the 2026-08-08 evidence:** do **not** mint the
audiobook row yet — the US Audible listing (`B00KZ1QMX8`) is de-listed on
audible.com, and the repo rule is that edition rows are minted only from
**reviewed inventory** evidence (an unavailable listing is precisely the
"dead link" class C1 belongs to). Track the lead instead:

- Add one row to `data/research_manual_leads.csv` (the standing "leads outside
  the master" lane):
  `Golden Word Book Signing – Audiobook (Audible)`, item_type lecture,
  proposed_format audiobook, lead_status `research_lead`, review_reason
  "US Audible ASIN B00KZ1QMX8 de-listed on audible.com 2026-08-08; Amazon.com
  listing still present; Audible.in B07JGMY5W4 active. Mint only after a
  reviewed, live US listing exists.", provenance_note citing this memo.

Re-open Option B whenever a live, reviewed US Audible/Amazon listing appears.

---

## 5. Apply + verify checklist (after owner approval)

```bash
# edit inputs per A1–A3 + A6, patch build_research_master.py per A4, add tests per A5
python build_research_master.py          # 265: format=CD, format_detail=three CD; 2h56m, filename *.mp3
python build_catalogue_pages.py          # regenerate docs/master.json etc.
python -m unittest discover tests        # 112 + 2 new = 114, all green
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
python process_data.py --check           # raw view untouched
python map_series_taxonomy.py --check
python sync_inventory_mirrors.py --check # mirrors unchanged (URL kept)
node --check docs/app.js
```

Expected master diff after A: exactly **one row** (265) — `format`,
`format_detail`, `proposed_filename`, `proposed_filename_display`; nothing else
(URL, work_id, codes, inventory mirrors all unchanged). Expected log lines:
`[filename] Applied 1 proposed filenames…`, `[format] Inferred 109 formats…`
(110 − 1; 265 now pre-set by the ledger). Expected non-master diffs: one
`manual_leads` row (+1; `docs/manual-leads.json` regenerates) and the two
doc/reason edits in A3.
