# Satsang Date-Mapping Decisions

**Approved:** 2026-08-03  
**Scope:** Correct the date-loss collision in the Veritas Satsang title matcher without creating unsupported master items.

## Approved exact mappings

Thirteen official Satsang products now match a single master record by the same Month/Year and are approved as primary Veritas sources:

- January, March, May, July, and September 2007
- May and September 2008
- January, May, September, and November 2009
- February and November 2010

Their official URLs are retained through `data/research_master_source_overrides.csv`; the build publishes direct `primary_product_for_item_part` relationships for all thirteen records.

## Inventory-only dates

Nine official Satsang products have no matching master date and remain `unmatched_official_product` inventory rows:

- January, March, May, July, September, and November 2006
- July 2008
- June and September 2010

They are not attached to a different Satsang recording, are not added to the master, and are not placed in Everything. A later review can create a candidate only after item identity, type, year, ownership, and relationship are approved.

## Matcher safeguard

`fetch_veritas_catalogue.py` now treats Satsang Month/Year as identity-bearing metadata. A Satsang product maps only when the official product title and master title share the exact `YYYY-MM`; otherwise it is emitted as `unmatched_official_product`. This replaces the former behavior that stripped the date and produced 286 false candidate pairs.

## Addendum — new-work ruling evidence for the nine inventory-only dates (2026-08-03)

The nine `unmatched_official_product` Satsang monthlies (Jan/Mar/May/Jul/Sep/
Nov 2006, Jul 2008, Jun 2010, Sep 2010) were re-examined after the edition
model and the New Work Review lane landed. Verdict: **all nine are new-work
candidates, none is an edition or duplicate of an existing master record.**

Evidence chain:

- Each product's `matched_master_uuids` is empty and its URL appears nowhere
  in the master or in `data/product_relationships.csv` — no overlap with any
  of the 13 approved Satsang records (2007 ×5, 2008 ×2, 2009 ×4, 2010
  Feb/Nov) or the three 2011 Q&A records.
- The master collection skips exactly these months (e.g. it holds Feb and
  Nov 2010 but not Jun/Sep 2010), so the nine are **missing collection
  months**, not reissues.
- The raw spreadsheet has no rows for them (no `tempid`, no `product link`,
  no ownership marker), so `owned` must stay unknown (the
  "ownership intentionally unknown" precedent used for promoted candidates).

Proposed candidate shape (if the owner approves creating them through the
manual-candidate path):

| Field | Value |
|---|---|
| candidate_title | `Satsang Series (MM YYYY)` — same naming as the 13 approved records |
| proposed_item_type | `lecture` |
| series | `Satsang Series` |
| proposed_year | the product's year; month only in the title (matches the 13 existing records, whose `month` is empty) |
| proposed_format | `CD` (Veritas Satsang monthly CD products) |
| proposed_owned | blank (unknown) |
| source | Veritas product ID + URL from `data/veritas_official_products.csv` |
| review_status | `reviewed_candidate` only after owner approval; until then the rows stay in `data/new_work_review_queue.csv` |

Until a ruling, the nine rows remain in the New Work Review queue with
`match_status = not_found_in_current_draft` (they are genuinely absent from
the master), and nothing is added to the master or to Everything.
