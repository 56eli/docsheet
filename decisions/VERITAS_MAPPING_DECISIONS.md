# Veritas Mapping Decisions

**Status:** Persistent reviewed overlay, seeded 2026-08-03  
**Input:** `data/veritas_mapping_decisions.csv`  
**Review sheet:** **Veritas Decisions** in Pages

## Purpose

The Veritas WordPress API supplies a live commercial inventory, not a durable record of research decisions. `fetch_veritas_catalogue.py` first derives deterministic primary-source, date-aware, and normalized-title results from the live product data, then reapplies this product-ID keyed decision overlay.

This prevents a live refresh from resetting reviewed non-primary dispositions such as `unique_item`, `compilation_or_new_edition`, `excluded_related_material`, and evidence-backed non-primary title matches.

## Required fields

| Field | Rule |
|---|---|
| `veritas_product_id` | Must identify one current official product and appear only once. |
| `mapping_status` | One reviewed non-primary status: `unique_item`, `compilation_or_new_edition`, `excluded_related_material`, `matched_by_title`, or `matched_by_normalized_title`. |
| `matched_master_uuids` / `matched_master_titles` | Required only for match statuses; titles must exactly match the current referenced compact master IDs. The column name is retained for compatibility. |
| `review_notes` | Preserved inventory note. |
| `review_status` / `reviewed_on` | Must be `approved` and an ISO date. |
| `decision_reason` | Non-empty human rationale for retaining the decision. |

## Refresh behavior

1. Run `python fetch_veritas_catalogue.py --check` to compare the live, decision-applied inventory with the committed reviewed inventory.
2. A difference is a **review event**, not an automatic data update.
3. The Map Veritas workflow writes a candidate CSV and diff patch artifact, then fails when a diff exists. It never auto-commits a refreshed inventory.
4. Review source changes, update this decision input where needed, regenerate the reviewed inventory deliberately, rebuild Pages data, and run all checks before committing.

## Current seed

The current overlay contains **18** approved decisions: 7 annual-Highlights
compilation products, 4 excluded related products, and 7 non-primary master
associations. Exact primary-source and date-aware results remain
deterministic and do not need overlay rows.

**2026-08-04 reduction (35 → 18):** the 17 decisions that preserved
pre-promotion `unique_item`/`compilation_or_new_edition` dispositions for
products whose works were promoted to the curated master on 2026-08-03
(masters 309–319, 353–358) were removed. Their master rows carry the exact
Veritas primary URLs, so the deterministic primary-source matcher now links
them — the suppression rows had become stale duplicates of curated records.
See `../VERITAS_ARTIFACT_REVIEW.md` Addendum 3 and
`../NEXT_AGENT_HANDOFF.md` §4 item 15.
