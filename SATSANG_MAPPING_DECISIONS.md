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
