# Official Catalogue Discovery — Initial Comparison

**Status:** Discovery comparison recorded 2026-08-03; the draft it refers to
has since grown to the current 317-record research master. The four
Nightingale-Conant candidates listed below entered the review queue; separate
official candidates were subsequently promoted through the reviewed
`data/manual_master_candidates.csv` + `data/manual_candidate_promotions.csv`
path (11 promoted, 6 pending). This document is retained as the initial
source-comparison record.
**Discovery date:** 2026-08-03
**Approved sources examined:** Veritas Publishing, Hay House, Nightingale-Conant, Audible.

## Result summary

| Source | Official evidence | Discovery result | Action |
|---|---|---|---|
| Veritas Publishing | [Hawkins Products](https://veritaspub.com/hawkins-products/) | The live official product hub reports **190 results** and exposes 13 collection categories: books, 2002–2011 lectures, office visits, discussion series, media miscellaneous, On the Road, volume series, new products, card decks, highlights, satsang, transcription series, and Map of Consciousness. | Use as the primary cataloguing comparison source; its products must be mapped to the per-part model, not blindly imported one-for-one. |
| Hay House | [Hawkins author catalogue](https://www.hayhouse.com/authorbio/david-r-hawkins-m-d-ph-d/) | Official author page exposes books and book editions, including *Discovery of the Presence of God*, *Healing and Recovery*, *I: Reality and Subjectivity*, *Letting Go*, and *The Eye of the I*. | Cross-reference item-specific URLs when book records are reviewed; do not duplicate an existing work just because another official source lists it. |
| Nightingale-Conant | [Hawkins author catalogue](https://www.nightingale.com/pages/david-hawkins) | Official page lists seven programs: *The Ultimate David Hawkins Library*, *The Discovery*, *Healing*, *The Highest Level of Enlightenment*, *In The World But Not Of It*, *Truth Vs Falsehood*, and *Naked*. | Four entries require review against the current draft and are in the queue. |
| Audible | [Hawkins author page](https://www.audible.com/author/David-R-Hawkins/B001H6MLOO) | Official platform author catalogue. Nightingale-Conant provides direct Audible links for its listed programs. | Store platform URLs alongside Nightingale-Conant records; do not treat Audible as a publisher. |

## Veritas catalogue scope observed

The Veritas hub’s category counts are catalog-navigation counts, not a deduplicated record total; products can be represented across categories/variants. The public page lists the following categories and displayed counts:

| Category | Displayed count |
|---|---:|
| Archival Office Visit Series | 17 |
| Books Published by Dr. Hawkins | 27 |
| Discussion Series | 8 |
| Lectures Series | 77 |
| Map of Consciousness | 1 |
| Media Miscellaneous | 12 |
| On the Road – Talk Series | 21 |
| Volume Series | 7 |
| New Products | 13 |
| Card Decks | 2 |
| Highlights | 7 |
| Satsang | 25 |
| The Six Book 2002 Transcription Series | 7 |

This confirms that the current spreadsheet is not yet a complete representation of the official catalogue. It also confirms why a direct product-list import would be wrong: one official product can correspond to multiple owned discs/parts in the research master, and an official product can be a compilation, book edition, card deck, or related work.

## New official-source review queue

`data/official_discovery_queue.csv` contains four Nightingale-Conant candidates that did not have an exact current-draft match or have an ambiguous relationship:

1. *The Ultimate David Hawkins Library*
2. *The Discovery*
3. *Healing*
4. *Naked* (a multi-contributor item)

The queue deliberately contains **no ID, no catalogue code, and no ownership claim**. Each row needs approval and relationship research before import, consistent with the approved AI-drafts/human-approval workflow.

## Important comparison rule

The 317 migrated master records are chiefly **individual material parts**, whereas official catalogues expose **commercial products/editions**. Therefore:

- an official listing that matches an existing title may add a source URL, not a new item;
- a compilation or new edition must be examined for changed content before it becomes a separate record;
- an official listing with no draft match enters the review queue rather than being automatically imported;
- no claim of a complete worldwide Hawkins corpus is made at this stage.

## Next discovery pass

1. Build a detailed Veritas product-to-draft match table, collection by collection.
2. Review the four Nightingale-Conant candidates and import approved distinct works.
3. Extract Hay House edition metadata and connect it to existing book records.
4. Continue internationally with the known-not-approved publisher list only after the official core-source comparison has been reviewed.
