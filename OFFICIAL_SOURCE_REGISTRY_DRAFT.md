# Official Source Registry — Research Draft

**Status:** Draft for approval; do not use as a final source-of-truth registry yet.  
**Research date:** 2026-08-03  
**Requested registry fields:** source name and official catalogue URL.

## Scope and inclusion rule used for this draft

This is a global open-web discovery pass for publisher, rights-holder, creator-affiliated, or platform-controlled David R. Hawkins catalogues. It intentionally excludes marketplace resellers such as eBay and does not treat community, review, archive, or social references as an official distributor merely because they mention a work.

A global web search cannot establish mathematical completeness. It can establish a reviewable candidate registry, which should be approved before it is used to create source columns or automate item matching.

## Proposed registry

| Source name | Official catalogue URL | Proposed role | Evidence for inclusion | Recommendation |
|---|---|---|---|---|
| Veritas Publishing | https://veritaspub.com/hawkins-products/ | Primary creator-affiliated publisher / catalogue | Veritas identifies itself as producing and publishing Hawkins’s works; its product hub lists books, lecture series, office series, volume series, media, and satsang material. [Veritas home](https://veritaspub.com/), [product hub](https://veritaspub.com/hawkins-products/) | **Approve as primary source.** This is the most complete official source for the current sheet’s lecture/media content. |
| Hay House | https://www.hayhouse.com/authorbio/david-r-hawkins-m-d-ph-d | Publisher catalogue | Hay House has an official Hawkins author page and product pages; Veritas also identifies Hay House as a source for Hawkins books. [Hay House author page](https://www.hayhouse.com/authorbio/david-r-hawkins-m-d-ph-d), [Veritas biography](https://veritaspub.com/dr-hawkins/) | **Approve as official book-publisher source.** |
| Nightingale-Conant | https://www.nightingale.com/pages/david-hawkins | Audio-program publisher / catalogue | Nightingale-Conant maintains an official Hawkins author page and product pages; Veritas product pages identify Nightingale-Conant as publisher for relevant audio releases. [Nightingale author page](https://www.nightingale.com/pages/david-hawkins), [example Veritas product metadata](https://veritaspub.com/product/in-the-world-but-not-of-it-cd/) | **Approve as official audio-program source.** |
| Audible | https://www.audible.com/author/David-R-Hawkins/B001H6MLOO | Platform catalogue, not a publisher | Audible has an official Hawkins author catalogue. Nightingale-Conant explicitly directs users to Audible for its programs. [Audible author page](https://www.audible.com/author/David-R-Hawkins/B001H6MLOO), [Nightingale product page](https://www.nightingale.com/products/in-the-world-but-not-of-it) | **Approve only as an official platform/source column**, not as a publisher or rights-holder. |
| Veritas Publishing YouTube | https://www.youtube.com/@VeritasPublishing | Official video channel / discovery catalogue | The channel identifies itself as Veritas Publishing and directs viewers to Veritas streaming information. [Channel](https://www.youtube.com/@VeritasPublishing), [Veritas FAQ](https://veritaspub.com/faqs/) | **Optional.** Include only if public video/channel links should be source columns rather than related links. |
| Penguin Random House | https://www.penguinrandomhouse.com/authors/2331680/david-r-hawkins-mdphd/ | Distribution/catalogue presence for Hay House titles | PRH’s Hawkins author page says the listed books are published by Hay House and exposes product/ISBN metadata. [PRH author page](https://www.penguinrandomhouse.com/authors/2331680/david-r-hawkins-mdphd/), [example product record](https://www.penguinrandomhouse.com/books/691568/the-wisdom-of-dr-david-r-hawkins-by-david-r-hawkins-md-phd/) | **Hold for decision.** It is useful bibliographic/distribution evidence, but the current evidence does not make it a separate original publisher for Hawkins works. |

## Sources deliberately not registered as official distributors

| Source/category | Reason |
|---|---|
| Amazon | Retail marketplace; not added under the requested no-reseller rule. It may appear as a link from a rights-holder but is not itself a publisher/creator-controlled catalogue in this model. |
| Goodreads | Bibliographic/community reference, not an official distributor. |
| Archive.org | Archive/reference source, not treated as an official distributor in this draft. |
| Discord | Personal/community reference location, not an official distributor. |
| eBay, AbeBooks, used-book sellers | Resellers/secondary market; excluded. |
| Fan, study-group, critical, or biography websites | Potential research evidence only; not official distribution sources. |

## Registry observations relevant to the spreadsheet

1. **Veritas is the key canonical catalogue for the existing CSV.** Its product hub mirrors the spreadsheet’s high-level groups: annual lecture series, books, office series, volume series, media miscellaneous, and satsang series.
2. **Hay House and Nightingale-Conant are not interchangeable with Veritas.** The data model should preserve separate source URLs instead of overwriting one source with another.
3. **Audible is a platform field, not a publisher field.** Its presence can document an official listening option, but publisher attribution should remain Veritas, Nightingale-Conant, Hay House, or another evidenced publisher.
4. **Publisher/source is different from item ownership and private-reference location.** The approved public model can retain all of these fields, but they should not be collapsed into one `original source` column.
5. **No source columns are created in the production CSV or site by this draft.** That requires your approval of the registry and a separate schema/migration proposal.

## Approval decisions needed

Please confirm each proposed source as one of:

- `approved — dedicated source column`
- `approved — repeatable/related source only`
- `exclude`
- `research further`

The minimum decision set is:

1. Veritas Publishing
2. Hay House
3. Nightingale-Conant
4. Audible
5. Veritas Publishing YouTube
6. Penguin Random House

After approval, the next deliverable should be a **schema and migration map** showing how every current CSV field and row type will move into the research-master dataset without discarding raw source data.
