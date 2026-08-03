# Unique-Item Candidate Decisions

**Approved:** 2026-08-03  
**Scope:** Preserve evidence for the official Veritas `unique_item` products without prematurely promoting them into the 308-record research master.

## Decision

Nine `unique_item` products reviewed in `UNIQUE_ITEM_REVIEW_PACKET.md` are recorded in `data/manual_master_candidates.csv` as `reviewed_candidate` rows with:

- a stable `manual-veritas-<product-id>` provenance key;
- official Veritas product ID, URL, title, and product-page evidence;
- proposed controlled type/year/format metadata where the evidence supports it;
- blank year where the product page did not establish a recording/release year;
- `promotion_status = not_promoted`.

They remain visible in **Everything** as official broad candidates but do not receive a master ID, catalogue code, ownership assertion, or master-source relationship until a separate promotion decision is recorded. *Spiritual Will Inspiring Q & A* is not retained as a candidate because its official URL already maps directly to two existing master parts; see `COMPILATION_CANDIDATE_DECISIONS.md`.

## Validation boundary

`build_research_master.py` validates the candidate key, controlled fields, review/promotion status, official product URL/title, and Veritas inventory reference on every build or `--check`. The validator does not emit these rows into the master CSV/JSON.

## Future promotion

A promotion must explicitly select candidate(s), confirm the final item type/year/format, decide ownership, and create a durable master identity. It must be modeled as a reviewed source input—not a manual edit to generated master files.
