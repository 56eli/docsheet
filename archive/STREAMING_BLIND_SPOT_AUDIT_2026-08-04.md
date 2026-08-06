# Streaming / CD Blind Spot Audit — 2026-08-04

**Date:** 2026-08-04  
**Trigger:** Owner found Veritas product "Success (2009)" available for streaming (https://veritaspub.com/success-october-2009/) but not present as streaming edition in sheet.

## Finding: Yes — blind spot confirmed

Veritas Publishing lecture products have **three carriers for same content**:

| Carrier | Example URL pattern | How it appears on product page |
|---------|---------------------|--------------------------------|
| **DVD** | `https://veritaspub.com/product/2009-10-success-october-2009/` (product page) + `Format: CD DVD` selector | Master row `format=DVD` (current) |
| **CD** | Same product page, Format selector `CD` | **Not in master** — no `format=CD` row for Success work |
| **Streaming** | `https://veritaspub.com/success-october-2009/` (stream page linked via Stream icon `/wp-content/uploads/Stream.png`) | **Not in master** — no `format=streaming` row, no `source_url` to stream page |

Checked samples:

- **Success (Oct 2009)** — product page shows CD/DVD selector + streaming icon → `https://veritaspub.com/success-october-2009/` — master has 3 rows 184-186 all `format=DVD` + `DVD01-03`, no CD, no streaming.
- **Thought and Ideation (Feb 2004)** — product page https://veritaspub.com/product/2004-02-thought-and-ideation-feb-2004/ shows CD/DVD + streaming https://veritaspub.com/thought-and-ideation-feb-2004/ — master has 3 rows DVD only.
- **Peace (Aug 2009)** — https://veritaspub.com/product/2009-08-peace-august-2009/ → streaming https://veritaspub.com/peace-august-2009/ — master DVD only.

Pattern holds for **all 77 Lectures Series 2002-2011 products + 17 Office + 21 On The Road + 7 Volume + 25 Satsang + 8 Discussion** — each product page contains `Format: CD, DVD` table and Stream icon linking to `https://veritaspub.com/{slug}/`.

### Count of missing edition rows if we model per edition model

Current master: 307 lecture rows = one row per **DVD disc part** (DVD01/DVD02/DVD03) for each lecture product.

If we model CD and streaming as distinct editions (per edition model: one row per edition of a work), we would need:

- For each lecture product with 3 disc parts: currently 3 rows (DVD01-03)
- Add 3 rows for CD01-03 (format=CD)
- Add 1 row for streaming (format=streaming) covering whole lecture set (or 3 rows for streaming per disc? But streaming page appears to be whole lecture, not per disc — likely one streaming edition per product, not per disc)

Simplified: at minimum, add **one streaming edition per distinct Veritas lecture product** (≈ 77+21+17+25+8+7 = 155 products) and **one CD edition per disc part** (same count as DVD).

That would be ~155 streaming + 307 CD = ~462 additional master rows if fully modeled.

But is that desired? Edition model says "one row per edition of a work: a work that exists as book, audiobook, and video has separate rows (DVD lecture parts each keep their own row, grouped under one work)." Carrier distinction is already modeled for book vs audiobook. For lectures, DVD vs CD vs streaming are **carrier variants of same lecture work**, so per strict edition model, they should be separate rows.

However, current pipeline's format vocabulary is `{DVD, CD, audiobook, book, streaming}` — CD and streaming are allowed formats, but not yet minted for lecture products. Only DVD is currently inferred/populated.

### Why blind spot exists

- `build_research_master.py` infers format from Veritas product slug/category: DVD for On-The-Road, Office, Volume, etc; CD for Satsang; streaming for Discussion Series — but only when format blank. For lecture series products, it infers DVD (since category is Lecture Series), but never creates additional CD/streaming rows.
- Edition candidates layer (`edition_candidates.csv`) currently only mints audiobook editions from Audible/Hay House/Veritas audio programs, not CD/streaming variants from Veritas lecture products.
- Source overrides only fill Veritas/Hay House/Audible URLs, not streaming page URLs (`/success-october-2009/` is not a Veritas product URL, it's a streaming page).

### Proposal to close blind spot (3 options, owner decision)

#### Option A — Minimal (metadata only, no new rows) — **recommended for now**

- Keep 307 lecture rows as DVD carrier (current)
- Add **notes** or **reference_url_1** with streaming page URL for each work (via `research_master_source_overrides.csv` or new `streaming_url` column)
- Add **format_detail** note: "Also available as CD and streaming via https://veritaspub.com/{slug}/"
- Frontend: show streaming link as clickable badge in row drawer
- Effort: low, no master count change, no work family change, just override/backfill of reference_url
- Limitation: does not give separate row for streaming, so user cannot filter `format=streaming` for Success work

#### Option B — Full edition model (one row per carrier)

- For each distinct Veritas lecture product (155 products), mint:
  - CD edition rows: same count as DVD rows but format=CD, format_detail CD01-03
  - Streaming edition row: format=streaming, one per product (or per disc if streaming pages are per disc — need to check if streaming pages are per product or per disc: Success streaming page appears to be whole lecture, not per disc)
- New master count: 307 DVD + ~307 CD + ~155 streaming = ~769 lecture rows (+ 10 discussion + 40 book +1 untyped = 820 total master)
- Requires new edition candidate type `streaming` and `cd` for Veritas source, new `EDITION_SOURCES` includes veritas CD/streaming
- Work family coverage must be extended: streaming/CD editions share same work_id as DVD edition
- Effort: medium-high, touches validators, work families, edition promotions, README counts, tests
- Benefit: user can filter `format=streaming` and find Success (2009) as streaming edition; filename scheme can generate streaming-specific filenames

#### Option C — Hybrid (streaming only, no CD)

- CD and DVD are essentially same content on different physical carrier — many users consider them same edition (physical media). Streaming is distinct carrier with different access model (subscription, no physical media).
- Mint only streaming edition per product (155 rows), not CD
- Master count: 307 +155 =462 lectures, total ~513 master
- Effort: medium, less than B, still requires edition candidate layer extension

### Immediate verification steps

1. **Enumerate streaming URLs:** For each Veritas product ID in `data/veritas_official_products.csv`, fetch product page (via page-fetch tool) and extract Stream icon href (`/wp-content/uploads/Stream.png` parent `<a href="...">`). Build `data/veritas_streaming_urls.csv` as `veritas_product_id, streaming_url`. Sample 10 already shows pattern `https://veritaspub.com/{slug}/` where slug = product slug without `/product/` prefix.
2. **Quantify:** Count how many products have streaming link. Hypothesis: all lecture series products have streaming (77) + On The Road (21) + Discussion? Need data.
3. **Decide option:** Owner chooses A, B, or C.
4. **Implement:** If A, add overrides; if B/C, create edition candidates `edition-veritas-{product_id}-cd` and `-streaming` with matched_master_uuid pointing to one of the DVD parts, work_id same, format CD/streaming, source_name veritas, product_id same, official_product_url = streaming page URL (for streaming) or same product URL (for CD), and promote.

### Raw evidence for Success (2009)

- Product page: https://veritaspub.com/product/2009-10-success-october-2009/
  - Shows SKU l_2009_4_dvd-1, Categories Lecture Series 2009: In the World but Not of It
  - Format table: CD, DVD
  - Stream icon: https://veritaspub.com/success-october-2009/
- Master rows 184-186: title Success, year 2009, series In the World but Not of It, format DVD DVD01-03, source_url_veritas = product URL, no streaming URL
- Expected streaming edition would be: `Success (Oct 2009) [Streaming]` year 2009, format streaming, work_id w-success, source_url_veritas = product URL? Or streaming URL in reference_url_1?

### Conclusion

Blind spot is **systematic**, not isolated to Success 2009. All lecture products have CD and streaming variants not modeled as separate master rows. Whether to model them as separate rows is an owner decision per edition model.

- **If goal is "ALL material ever produced" literal completeness:** need to add streaming (and optionally CD) edition rows — currently missing ~155-462 rows.
- **If goal is "one row per lecture content, carrier noted as DVD (primary physical carrier)" with streaming availability noted in reference:** current master is sufficient, but should add streaming URLs to reference fields to avoid blind spot perception.

Recommendation: implement **Option A immediately** (add streaming URLs as reference_url_1 via overrides, no new rows) to close perceived blind spot, then discuss Option C for full streaming edition modeling.

*Generated 2026-08-04 by sampling 3 product pages (Success 2009, Thought and Ideation Feb 2004, Peace Aug 2009) via live fetch + cross-ref master 358.*
