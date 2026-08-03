# Item Type Classification Proposal — the 87 Untyped Master Items

**Prepared:** 2026-08-03
**Status:** ✅ **Implemented 2026-08-03** — the v3 classification was applied to
the review ledger (`item_type` + ledger type validation, `discussion` added;
see `TEMP_RESPONSE_AUDIT_2026-08-03.md`). The current master is 316/317 typed
(277 lecture / 29 book / 10 discussion / 1 untyped — record **264**, deferred).
The proposal below is retained as the decision record; scope figures refer to
the 308-record draft as it stood when it was written.
**Scope (historical):** the 87 master records (of 308) with an empty `item_type`.

---

## ⚠️ v3 — I was wrong, and you were right to challenge it

You asked whether `video` means *medium* or *content class*. Checking the existing
precedent shows **my v1/v2 proposal was internally inconsistent and would have
corrupted the field's meaning.**

**The precedent is unambiguous:**

| Existing records | `item_type` | `format` |
|---:|---|---|
| 198 | `lecture` | `DVD` |
| 23 | `book` | *(blank)* |

Those 198 records are **DVDs — a video medium — typed as `lecture`**. So the
established contract is:

> **`item_type` = what the thing *is* (content class). `format` = what it's *on* (medium).**

My earlier proposal typed Volume/Office/Discussion as `video` and
Satsang/On-The-Road-12 as `audio` — i.e. **by medium**. That would have created two
mutually contradictory conventions in one column: a DVD lecture typed `lecture`,
but a CD talk typed `audio`. Sorting or filtering by `item_type` would then return
incoherent results, and the field would silently stop meaning one thing.

The root cause is that the controlled vocabulary itself **mixes two axes**:

- **content class:** `lecture, book, interview, transcript, dissertation, article, highlight`
- **medium:** `audio, video` ← the trap
- **escape hatch:** `other`

The presence of `audio`/`video` in that list invited exactly the mistake I made.

### What this also means

The elaborate D3a/D3b split I derived in v2 — 18 `lecture` vs 12 `audio`, justified
by SKU prefixes and streaming availability — **was solving the wrong problem.** All
30 are recorded public talks. The DVD/CD difference is real, but it is a `format`
fact, not an `item_type` fact. Under a content-class reading the split disappears.

---

## Revised proposal (v3) — classify by content class

| # | Series | Records | `item_type` | `format` | Rationale |
|---|---|---:|---|---|---|
| D1 | Love & Spiritual Seeker Qualities | 3 | `lecture` | *(blank)* | Q&A sessions within a lecture series; siblings already `lecture` |
| D2 | Volume Series | 13 | `lecture` | *(blank)* | Numbered studio teaching presentations (Volume I–VII) |
| D3 | On The Road Talk Series | 30 | `lecture` | *(blank)* | Recorded public talks — one official series; DVD/CD is a `format` distinction |
| D4 | Office Series | 16 | `lecture` | *(blank)* | Single-topic clinical talks A-01…B-06 |
| D5 | Satsang Series | 13 | `lecture` | *(blank)* | Dated satsang teaching sessions |
| D6 | Discussion Series | 8 | **`interview`** | *(blank)* | **Two-party dialogues** — see below |
| D7 | Media Miscellaneous (265) | 1 | `lecture` | *(blank)* | Golden Word book-signing Q&A event |
| — | Deferred placeholders (246, 249, 264) | 3 | *(none)* | — | Identity in doubt — see §4 |

**Total typed: 84 of 87.** Final distribution across all 308 master records:
**274 `lecture`, 23 `book`, 8 `interview`, 3 untyped.**

### Why D6 is `interview` and not `lecture`

This is the one genuine content-class difference in the set, and it's confirmed by
the publisher. The official product page for *What is Meant by Spiritual (2012)*
states:

> "Dr. Hawkins **and his wife Susan** explore the different facets of spirituality."

The series is titled *"Discussion Series with Dr. David Hawkins & Wife Susan"* in
the raw sheet, and Veritas files it under its own `Discussion Series` category
(SKU `ds2014_01_dvd`). A two-party dialogue is structurally different from a
solo talk, and `interview` is the vocabulary's closest content-class value.

> If you consider `interview` misleading (Susan is a co-participant, not an
> interviewer), the alternatives are `lecture` for consistency, or adding a
> `discussion` value to the vocabulary. Say which you prefer.

### Why `format` stays blank

The raw spreadsheet has **no format data for any of these 87 records**. Slug and
SKU hints exist but are inconsistent and partial. Populating `format` from them
would be inference presented as evidence. The medium facts I gathered (SKU
prefixes, disc-set descriptions, streaming availability) are recorded in the
decision document so a later, deliberate `format` pass can use them.

## Side effects — re-verified for v3

| Measure | Result |
|---|---:|
| Existing catalogue codes broken | **0** |
| New catalogue codes created | 23 |
| `item_type` coverage | 221/308 → **305/308** |
| Master IDs affected | none |

All 23 new codes are `LECTURE-YYYY-NNN`, appending cleanly to existing year
sequences (e.g. `LECTURE-2007-028…032` for the 2007 Satsang records). Because
everything resolves to `lecture`, no new code prefix is introduced — a further
sign this reading is the consistent one.

---

## What I need from you

Approve or amend the **seven series-level decisions** in §3. One reply covers all
87 records — they fall into seven complete, homogeneous series, so this is seven
decisions, not eighty-seven.

**Update (after you asked to discuss):** I dug into the raw spreadsheet and both
previously-ambiguous decisions are now **resolved by primary evidence**:

- **D5 Satsang → `audio`** (was: unsure). The source heading literally reads
  *"Missing satsang **audios**"* and every row's `tempid` is `2cds each?`. My
  earlier "month-dated therefore lecture" reasoning was inference; this is evidence.
- **D7 Media Miscellaneous → `audio`** (was: unsure). All 14 are audio products.

That research also surfaced **one new issue**, which I then **confirmed against the
live publisher taxonomy**: 12 of the 14 "Media Miscellaneous" records are listed by
Veritas itself under the official *On the Road – Talk Series* product category. The
raw spreadsheet's *"Missing OTR"* note was right; the migration mis-read it. See D7.
I recommend applying the *type* now and handling the *series reassignment* as its
own reviewed change.

---

## 1. Why these 87 are untyped

Not neglect — the migration ledger has `proposed_item_type` **empty for all 87**.
Every one of the 221 typed records got its type from the raw spreadsheet's
lecture-series structure (`LS200201_1`-style IDs). These seven series sat outside
that structure, so the conservative migration left them blank rather than guessing.

The gap is therefore a genuine open decision, exactly as intended.

## 2. Evidence used

| Source | What it gives |
|---|---|
| Official Veritas product page linked from each record | Authoritative title, and sometimes a format hint in the URL slug |
| The raw spreadsheet's `original source` / `WE HAVE?` columns | Provenance and ownership |
| Existing typed records in the same series | Internal precedent |
| The controlled vocabulary in `build_research_master.py` | `lecture, book, audio, video, transcript, interview, highlight, dissertation, article, other` |

**Coverage:** 74 of 87 records link to a confirmed official Veritas product; 13
have no source URL (listed in §4).

**Live publisher verification (added after your "dig further" request):** I fetched
`veritaspub.com` category and product pages directly. Product pages expose an
explicit `Category:` and `SKU:` for each item, which is the strongest evidence
available short of the publisher's own database — and it resolved D7 outright.

**Important limit:** the raw spreadsheet's `format` column is **empty for all 87**
records, and slug hints are inconsistent (7 of 13 Volume slugs say `video`, 7 of 13
Satsang slugs say `cd`). **I therefore propose `item_type` only and deliberately
leave `format` blank.** Inventing a format from a URL slug would be exactly the
kind of inference this project's rules forbid.

## 3. Proposed decisions

### D1 — Love & Spiritual Seeker Qualities (3 records: 199–201) → `lecture`
**Confidence: High.** These are the Jan/Mar/Jul 2011 Q&A sessions sitting inside a
series whose other 6 records (193–198) are already `lecture` / `DVD`. Official
titles confirm "Question/Answer Session (Jan 2011)". Same series, same year, same
official catalogue treatment.

### D2 — Volume Series (13 records: 202–214) → `video`
**Confidence: High.** Seven of the 13 official product slugs explicitly end in
`-video` (`volume-i-power-vs-force-muscle-testing-video`,
`volume-iv-...-video`, `volume-v-...-video`). The remainder are the same numbered
Volume I–VII product family. These are studio productions, distinct from the
recorded-lecture series, so `video` fits better than `lecture`.

> Note: records 202 and 203 both point at the *same* official product
> (Volume I). That's correct — they are Part 1 and Part 2 of one product.

### D3 — On The Road Talk Series (30 records) → **split by product medium**
**Confidence: High. ⚠️ Revised after the SR-1 regrouping.**

The regrouping merged two groups into one 30-record series, and that exposed a
problem with my original series-wide rule: **the merged series spans two distinct
product media**, so one `item_type` for all 30 would be wrong for half of them.

| Sub-group | Records | Owned | Raw titles | Publisher evidence | Proposed |
|---|---:|---|---|---|---|
| Original OTR | 18 (215–232) | all `true` | all `.mp4` | *Become That Which You Are*: streaming video; *Verification of Spiritual Realities*: **SKU `vsr_dvd`**, Vimeo trailer | `lecture` |
| Moved by SR-1 | 12 (266–277) | all `false` | none `.mp4` | *All is Divinity*: **SKU `cd_aid`**; *Ever-Present Joy*: **SKU `cd_otr_ej`**; both state *"Streaming Video is **not** available for this topic"* | `audio` |

The split is clean and independently corroborated three ways: SKU prefix
(`_dvd` vs `cd_`), streaming-video availability, and our own ownership/filename
evidence (we hold `.mp4` video copies of the first 18 and nothing of the latter 12).

**This is a good argument for keeping `series` and `item_type` as independent
fields** — the publisher groups by *topic and occasion*, not by medium.

> The two `Spiritual Will` records (228–229) map to "Spiritual Will Inspiring
> Q & A". They stay `lecture` with the other owned video items; flag it if you'd
> prefer `interview` for Q&A material.

### D4 — Office Series (18 records: 233–250) → `video`
**Confidence: High.** A structured A-01…A-12 / B-01…B-06 series of single-topic
clinical talks (Stress, Health, Depression, Cancer, Death and Dying). Each maps to
its own official Veritas product. Consistent with D2's treatment of studio
productions.

> Includes the two placeholder rows 246 and 249 — see §4, I recommend handling
> those separately.

### D5 — Satsang Series (13 records: 251–263) → `audio`
**Confidence: High — resolved by new evidence, no longer ambiguous.**

I went back to the raw spreadsheet and found the decisive evidence I'd missed:

| Raw evidence | Value |
|---|---|
| Section heading (raw row 279) | **"Missing satsang _audios_"** |
| `tempid` column, all 13 rows | **`2cds each?`** |
| `original source` | `veritas/only sold via audible` |
| `WE HAVE?` | `❌` (all 13) |
| Official slugs | 7 of 13 end in `-cd` |

The compiler of the spreadsheet explicitly called these **audios** and recorded
them as **2 CDs each**. Every independent signal agrees. This overrides my earlier
"month-dated therefore lecture" reasoning, which was inference from structure
rather than evidence.

**Revised recommendation: `audio`.** No vocabulary change needed — `satsang` is
already captured by the `series` field, which is the right place for it.

> Corollary: `format` for these 13 is genuinely evidenced as CD (`2cds each?`).
> I still propose leaving `format` blank in this pass, because the trailing `?`
> signals the compiler's own uncertainty about the disc count. Worth a separate
> decision if you want it populated.

### D6 — Discussion Series (8 records: 278–285) → `video`
**Confidence: Medium-High.** 2012–2014 single-topic discussion products
("Improving Your Relationships", "What is Meant by Spiritual", "The Importance of
Family"). Five of eight map to official `(2012)`/`(2014)` products. Same
studio-production character as D2/D4.

### D7 — Media Miscellaneous → `audio` ✅ **regrouping APPLIED (SR-1)**

> **Status update:** the 12-record regrouping described below was approved and
> applied on 2026-08-03 (commit `973519d`, see `decisions/SERIES_REGROUPING_DECISIONS.md`).
> Those 12 records now live in `On The Road Talk Series` and are typed under **D3**
> as `audio`. Media Miscellaneous now holds **2** records: 264 (deferred, §4) and
> 265 Golden Word Book Signing → **`audio`** (page states *"Three Compact Disc
> Set"*, SKU `am_gwbs`).
>
> The original analysis is retained below as the decision record.

### D7 (original analysis) — Media Miscellaneous (14 records: 264–277) → `audio`, **and 12 are mis-grouped**
**Confidence: High for both — confirmed against the live publisher taxonomy.**

I fetched the official Veritas pages directly (the site is reachable via the web
tool even though the raw API isn't). The publisher's own product taxonomy settles
this definitively.

**Finding 1 — the grouping is wrong.** `veritaspub.com/product-category/on-the-road-talk-series/`
returns *"Showing all 21 results"*, and **12 of our 14 "Media Miscellaneous"
records are in that official category**:

| Our record | Official category (from the product page) |
|---|---|
| 266 All is Divinity | `On the Road - Talk Series`, SKU `cd_aid` |
| 271 The Ever-Present Joy | `On the Road - Talk Series`, SKU `cd_otr_ej` |
| 267, 268, 269, 270, 272, 273, 274, 275, 276, 277 | all listed on the same official OTR category page |

The official OTR category spans **both** of our groupings — 14 records we already
file as On The Road, plus these 12. That's 26 of the 21 official products (some
products cover multiple DVD parts), so the two groups are one series upstream.

**Finding 2 — the two survivors are genuinely Media Miscellaneous.** Record 265
("Golden Word Book Signing") states `Category: Media Miscellaneous`, SKU `am_gwbs`.
Record 264 has no product link. So exactly 2 of 14 stay put — matching the raw
sheet's structure precisely.

**Finding 3 — the type is `audio`.** SKUs are prefixed `cd_`, the product pages say
*"Streaming Video is **not** available for this topic"*, product details read
*"Three Compact Disc Set"*, and each links to an Audible/Amazon audiobook edition.

**This vindicates the raw spreadsheet.** Its `"Missing OTR"` note at row 299 was
accurate all along; the migration mis-classified that note as a `research_note`
instead of a `series_context` heading, so the 12 records were absorbed into the
preceding section.

**Recommendation:** apply `audio` to all 14 now. Handle the 12-record series
reassignment as its own reviewed change (see §6) — it is now evidence-backed
rather than speculative, but it changes series counts and deserves its own diff.

## 4. Records I recommend excluding from this pass

| ID | Title | Issue | Recommendation |
|---:|---|---|---|
| 246 | `where is B-02? might not exist.` | Not a title — an unresolved research question. No source URL. | Don't type. Resolve separately (audit item P2-9) |
| 249 | `where is B-05? might not exist.` | Same | Same |
| 264 | `26. "In the World But Not of It" –` | Truncated title, trailing whitespace defect, no source URL | Don't type. Fix in the title-hygiene pass |

Typing these would lend false legitimacy to records whose existence or identity is
explicitly in doubt.

## 5. Side effects — verified, and smaller than they look

`catalog_code` is auto-generated as `{TYPE}-{YEAR}-{NNN}` **only when both
`item_type` and `year` are present**. I simulated every scenario above:

| Scenario | Existing codes broken | New codes created |
|---|---:|---:|
| D1 + D5 as `lecture` | **0** | 16 |
| D1 `lecture`, D5 `satsang` | **0** | 16 |
| All seven series typed | **0** | 23 |
| **Final proposal (D1–D7 as revised)** | **0** | **23** |

Under the final proposal, `item_type` coverage goes from **221/308 → 305/308**,
leaving only the 3 deferred placeholders. The 23 new codes are:

- `LECTURE-2011-007…009` — the three 2011 Q&A sessions (D1)
- `LECTURE-2003-019`, `LECTURE-2004-019…024` — seven dated On The Road talks (D3)
- `AUDIO-2007-001…005`, `AUDIO-2008-001…002`, `AUDIO-2009-001…004`,
  `AUDIO-2010-001…002` — the thirteen Satsang records (D5)

The Satsang records open a clean new `AUDIO-` sequence rather than interleaving
with the `LECTURE-` numbering — a further argument for D5 being `audio`.

✅ **No existing catalogue code changes under any scenario.** New codes only append
to the end of each year's sequence, because the code counter follows ledger row
order and these records all sort after the typed lecture rows.

Only 23 of the 87 would gain a code at all — the other 64 have no `year`, so they
correctly stay code-less.

**Master IDs (1–308) are unaffected** — they're keyed to raw row number, not type.

## 6. How I'd implement it

Types belong in the **migration ledger** (`proposed_item_type`), the declared input,
**not** hand-edited into the generated master. So:

1. Set `proposed_item_type` for the approved rows in `migration_review_ledger.csv`.
2. Re-run `build_research_master.py` → regenerates the master with types + codes.
3. Re-run `build_catalogue_pages.py` → regenerates Pages JSON.
4. Verify all three `--check` modes + a clean-clone rebuild.
5. Record the rationale in a decision document, consistent with existing practice.

## 7. Summary — what I need approved

**See the v3 table at the top of this document.** In one line:

> Type all 84 by **content class**: 83 `lecture` + 8 `interview` (Discussion
> Series), `format` left blank, 3 placeholders deferred.

The sections below (§1–§6) are the original evidence gathering and remain valid;
only the *interpretation* of `item_type` changed in v3.

**Open question:** whether D6 should be `interview`, `lecture`, or a new
`discussion` vocabulary value.
