# DocSheet — Live Spreadsheet

[![CI](https://github.com/56eli/docsheet/actions/workflows/ci.yml/badge.svg)](https://github.com/56eli/docsheet/actions/workflows/ci.yml)

Renders the repository CSV as an interactive, searchable web table on
GitHub Pages (built with [Tabulator](https://tabulator.info/)).

- **Live site:** `https://56eli.github.io/docsheet` (once GitHub Pages is enabled)
- **Pipeline:** `process_data.py` reads the CSV with Pandas and publishes
  `docs/data.json` — data is currently passed through **unchanged** (cell
  values are never modified; the published view trims the six always-empty
  raw columns, see INSTRUCTIONS).
- **Automation:** the "Update Spreadsheet" GitHub Actions workflow regenerates
  the data on demand or whenever the CSV changes on `main`.

📖 Full setup and usage guide: **[INSTRUCTIONS.md](INSTRUCTIONS.md)**

## Quick start

```bash
pip install -r requirements.txt
python process_data.py
python process_data.py --check  # verify committed raw-Pages outputs are current
python -m http.server 8000   # then open http://localhost:8000/docs/
```

Browser smoke tests, including CSV export, are available with Playwright:

```bash
npm ci
npm run test:e2e:install
npm run test:e2e
```

Local frontend assets are content-versioned in `docs/index.html`. The public
footer exposes the matching app/style build ID and links
`docs/build-manifest.json`, which records full asset and raw/curated payload
hashes. `FrontendDeliveryContractTests` fails if a file changes without its URL,
visible ID, and manifest being refreshed. This identifies browser-delivery
revisions; explicit owner visual acceptance is still required before a row
presentation issue is considered resolved.

## Catalogue-data safeguard

The raw spreadsheet pipeline above is independent from the curated research
catalogue. Before rebuilding curated master or catalogue Pages files, inspect
and acknowledge any ledger/draft divergence first:

```bash
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
python map_series_taxonomy.py --check
python sync_inventory_mirrors.py --check
```

`RECONCILIATION_REPORT.md` is the read-only review artifact. A master-check
failure indicates a ledger/draft mismatch; do not run the writing build commands
until that review is resolved.

`tests/test_pipeline.py` runs all of the above generators plus tamper
detection and the rule matrices in one command:

```bash
pip install -r requirements-dev.txt
python -m unittest discover tests          # 149 tests, no browser/network needed
coverage run -m unittest discover tests && coverage report
```

The coverage gate (`fail_under = 85` in `.coveragerc`) passes at **90%** as of
2026-08-10 (with 149 deterministic pipeline, style, and delivery-contract tests;
individual module coverage is 78–100%). `requirements-ci.txt` records the
exact Python dependency set used by the owner-applied workflows. PR #34 merged
the constraint file to `main`, and the subsequent main CI run passed. The full
replacement record is in `archive/WORKFLOW_WEB_EDITOR_GUIDE.md`. Approved official links added after the ledger
pass live in `data/research_master_source_overrides.csv`; unresolved manual
edition/copy leads live in `data/research_manual_leads.csv` outside the master;
reviewed but unpromoted official candidates live in
`data/manual_master_candidates.csv`. Publisher-taxonomy-to-`series` proposals
live in `data/series_category_mapping.csv`, reviewed through
`data/series_taxonomy_review_queue.csv`, and become master data only after
owner approval — see `SERIES_TAXONOMY_MAPPING.md`.

Owner revisions that no automated step could derive go through reviewed
overlays, never hand-edits of the generated master: `data/master_year_overrides.csv`
(year/month/year_source corrections, e.g. the REVISION1 ODS year changes for
masters 356–358) and `data/master_notes_overrides.csv` (verbatim notes
replacements, e.g. the `FRAN GRACE` author marker on master 315). The
**curated presentation order** of the Everything view and its CSV export is
`data/catalogue_display_order.csv` — the owner-approved REVISION1 colour-group
order (2002–2011 lectures first, then discussion / satsang / on-the-road /
volume / office / books / transcription / media-misc blocks, undecided rows,
Fran Grace last); `build_catalogue_pages.py` fails the build if the order file
is not a dense 1..n approved covering of all 363 masters. The change record
behind all three inputs is the colour-coded
`review/hawkins-everything-REVISION1.ods` (committed for provenance; the CSVs
are the pipeline inputs, the ODS is the human review artifact).

Approved master-to-product assertions render in the **Product Relationships**
site tab: the primary item→product links are **derived automatically** from
each master's `source_url_veritas`, and only the distinct non-primary
relationships (`related_material`) are hand-maintained in
`data/product_relationships.csv`; evidence-backed annual compilation
relationships live in `data/series_compilation_relationships.csv` and render
in **Series Compilations**. See `PRODUCT_RELATIONSHIP_SCHEMA.md` and
`SERIES_COMPILATION_SCHEMA.md` before adding either relationship type. Live
Veritas inventory refreshes use the approved product-ID overlay in
`data/veritas_mapping_decisions.csv`; see `decisions/VERITAS_MAPPING_DECISIONS.md`. The
inventory's `normalized_title_match_count` is derived and must always equal the
number of IDs in `matched_master_uuids`; `build_catalogue_pages.py` fails the
build otherwise. The latest refresh review is in `archive/VERITAS_ARTIFACT_REVIEW.md`.

## Documentation layout

| Location | Contents |
|---|---|
| Root (essential) | `README`, `INSTRUCTIONS`, `AGENTS`, [`SCOREBOARD.md`](SCOREBOARD.md) + [`.scoreboard/`](.scoreboard/scoreboard.yml), `NEXT_AGENT_HANDOFF`, `RECONCILIATION_REPORT` (generated) |
| Root (normative) | `EDITION_MODEL_PROPOSAL`, `SERIES_TAXONOMY_MAPPING`, `PRODUCT_RELATIONSHIP_SCHEMA`, `SERIES_COMPILATION_SCHEMA`, `CATEGORY_DOMINANCE_POLICY`, `MIGRATION_REVIEW_LEDGER` |
| [`docs/audits/`](docs/audits/) | **Declared-current** multidisciplinary audit, corrective postmortem, prior audits |
| [`decisions/`](decisions/README.md) | Approved ruling records, filename proposals, provenance docs, source registry |
| [`archive/`](archive/README.md) | Superseded audits, historical proposals, suggestion docs, workflow guides |

## Curated records vs. official candidates

The **Everything** sheet shows curated master records, and — whenever the
intake lanes are populated — official product candidates next to them for
comparison. Every row therefore carries
an explicit `record_type`:

| `record_type` | Meaning |
|---|---|
| `master` | A curated master catalogue record (363) |
| `candidate_veritas` / `candidate_hayhouse` / `candidate_audible` | An official product listing shown for review; **not** a master record |
| `candidate_discovery` | An entry from the official discovery queue |
| `candidate_pending_promotion` | A reviewed manual candidate awaiting an owner promotion decision; **not** a master record |

Only `master` rows are catalogue records. Use the Record Type filter on that tab
to isolate curated data before exporting (the filter appears when more than one
record type is present; today every row is `master`, so the toolbar stays
hidden until a candidate lands). Counts per class are published in
`docs/catalogue-meta.json` under `everything_record_types`.

The **Everything** view opens in the owner-approved REVISION1 presentation
order (lecture series first, then the colour-group blocks, Fran Grace last)
and visitor-first: product facts (title, series,
type, edition, date, official store and streaming links, notes) are visible at
first sight, while technical metadata (Master ID, Work grouping, proposed file
names, provenance columns) stays hidden until the **Expert columns** toggle —
next to the Columns menu — is switched on; the choice persists per browser.
A **Series** tab (Catalogue group) lists every series as a card (records, owned,
year span) and opens the Everything view pre-filtered.
Clicking any row always shows every stored field in the clean details drawer, and the **View settings** menu can wrap long cells, switch row density, hide/show summary cards, or **Expand everything** (all columns + wrapped, roomy rows) for deep review. The Everything view opens in **Browse mode** on phone screens — compact work stacks that expand into editions/parts with quick Source and Streaming actions, plus tap-friendly **Series** and **Timeline** rails that reuse the normal facet filters — and the same work-card browser is available on desktop via the **Browse cards** toolbar toggle; **Spreadsheet** restores the full Tabulator grid for expert comparison. All 19 catalogue and review workspace sheets are accessed directly via the clean **Jump to** dropdown selector in the top bar. Full-width row details and responsive table scrolling remain available in all views.

## Review workspace

The Pages spreadsheet exposes review inputs directly: **Review Overview**,
**Master Candidates**, **Manual Leads**, **Master Exclusions**, **Migration
Review**, **Source Overrides**, **Official Discovery**, **New Work Review**
(unmatched Veritas products awaiting a new-work ruling), **Series
Compilations**, **Veritas Decisions**, **International Editions** (official
non-English publishers queued for catalogue extraction), the official
inventories (**Veritas Products**, **Hay House Products**, **Audible
Products**), the approved-source **Publishers** registry, and **Filename
Proposal** are separate sheets alongside the catalogue. Reviewers can search,
sort, export, and filter sheets with multiple review-status values without
opening repository folders. Two of these sheets (**Official Discovery** and **New Work Review**)
are intentionally empty right now: every queued item has been ruled, and the
sheets remain as standing **intake lanes** so any future Veritas catalogue
refresh lands its unmatched products there instead of in the curated views.

## Current reviewed catalogue state

The current curated master has **363** records (306 `lecture`, 41 `book`,
8 `discussion`, 7 `highlight`, 1 `other` — no untyped records remain since the
2026-08-07 rulings that record 246 was the audio edition already held as master
329 and that record 309 duplicated the Oxford talk already held as master 221;
the 2026-08-08 D-01 collapse retired duplicate streaming masters 225/226/227,
which shared their primary Veritas URL with the promoted DVD masters 311/310
per the owner's "one DVD/CD master with streaming in `reference_url_1`" ruling),
**278** catalogue codes, **75** retained exclusions,
**134** approved source overrides (including the four Nightingale-Conant audio
editions, two Amazon Office Series links, the Audible/NC/Hay House program URLs,
the three academic-book Amazon links moved onto the curated column on 2026-08-08,
and the official Veritas product link moved from retired duplicate 309 onto master 221; the three Advaita URL overlays were retired after the raw CSV was fixed),
**40** promoted and **0** unpromoted official candidates, **340** item-to-product relationships,
and **7** series-compilation relationships. The master exposes `legacy_title` alongside the cleaned public title
so the verbatim raw spreadsheet text is always exportable. Since 2026-08-04 the master also exposes `proposed_filename` between `title` and `item_type` using pattern `YYYY-MM - Name [1/3].mp4` (safe `[1-3]` on-disk, display `[1/3]`), no bracket for single part, audiobook label removed from name (`.m4b` indicates) except an explicit publisher suffix when two same-work audiobook editions would otherwise collide, Volume Series stripped of years (pre-2000 unknown) and standardized via `[1/2]` etc, Satsang month stripped. Since 2026-08-07 it also exposes `year_source` next to Year-Month (Ledger recording/first-pub, Veritas listing backfill, Manual candidate, Edition inherited, Blank intentional etc) and `source_url_amazon` as a curated direct Amazon product link where one has been approved (blank otherwise).

At the 2026-08-03 live-source checkpoint (historical snapshot), every entry was
verified field-by-field against the Veritas Publishing API: 191/191 products
reconciled exactly and all 195 verifiable lecture months matched the publisher's
own dates. Subsequent reviewed promotions, source corrections, and new-work
additions are reflected in the current generated inventory (363 master records,
191 Veritas products, 340 relationships). See the declared-current
[`docs/audits/2026-08-10-arena-019feaf6-full-audit.md`](docs/audits/2026-08-10-arena-019feaf6-full-audit.md)
for the latest full-stack evidence and [NEXT_AGENT_HANDOFF.md](NEXT_AGENT_HANDOFF.md)
for open work; older audit reports preserve their historical checkpoints.

### Field semantics

`item_type` records **what a record is** (its content class: `lecture`, `book`,
`discussion`, …). `format` records **the carrier it arrives on** (`DVD`, `CD`, …).
DVD lecture recordings are therefore `item_type=lecture` with `format=DVD`, never
`item_type=video`. Per the 2026-08-08 owner ruling, products represented only by
a streaming source/reference may stand as `format=streaming`, while streaming
availability for an item that has a DVD/CD carrier is stored as `reference_url_1`
on that item, not as a competing `format_detail`. The deprecated medium values `audio`/`video` were **retired
from the controlled vocabulary on 2026-08-03**: every pipeline validator now
rejects them — use the content class and record the carrier in `format`.

`month` is derived from the official Veritas product slug, which is the
publisher's authoritative date. It is **not** taken from the legacy `LSyyyynn_p`
identifier, whose `nn` segment is an ordinal position within the annual series
(this distinction caused a 156-record defect that was fixed on 2026-08-03).
For lectures/discussions the `year`/`month` reflect the recording date where
known and otherwise fall back to the publisher's product date.

For `book` rows, `year` is the work's **first-publication year**, never the day
the listing appeared on the storefront (Veritas added a whole batch of books
with a `published_date` of 2014-03-30 — e.g. *Power vs. Force* was first
published in **1995**, *The Eye of the I* in **2001**, *The Ego is Not the Real
You* in **2021**). Book years come only from the reviewed ledger / candidate
inputs, so they are never overwritten from an official inventory listing date,
and books never receive a catalogue code.

Catalogue codes are assigned to **`lecture`/`discussion` rows whose year was
already verified at minting time** (a readable `LECTURE-YYYY-###` /
`DISCUSSION-YYYY-###` is issued only when both the content type and a year are
proposed in the reviewed ledger or promotion registry). They are therefore
*lecture/discussion-only*, but not *every* lecture/discussion has one: pre-2000
rows with an intentional **blank** year (the 13 Volume Series rows), and
candidate/edition rows whose `proposed_year` was blank at minting (e.g. the
four CD/audio manual candidates 353/356/357/358 and the edition rows 327–343,
whose years were later backfilled from the official listing), correctly carry
no code. The 16 Office Series rows, whose ledger-proposed year is the decade
placeholder `198X`, **were** minted with codes (`LECTURE-198X-001 … -016`) —
`198X` counted as a proposed year at minting time. Codes are stable
identifiers and are never retroactively assigned or renumbered.

Pre-2000 lectures whose exact recording date is unconfirmed but whose decade
is established carry the placeholder year `198X` (the 16 Office Series rows;
ledger evidence — most believed 1982 — is in `year_source`, and the site
displays `c. 1980s` while exports keep the raw value). Rows whose decade is
also unknown carry a **blank** `year` with a labelled `year_source` instead
(e.g. `Blank: intentional pre-2000 (Volume Series)`, `Blank: under
investigation`).

`owned` records collection status with three values: `true` (owned), `false`
(explicitly not owned), and **blank** (not stated — e.g. minted edition rows
and NC/Hay House programs that have no raw spreadsheet ownership marker). The
site renders it as a badge (`Owned`) and leaves blank cells
empty; exports keep the raw `true`/`false`/empty values.

`notes` is reserved for **owner-applied markers only** (e.g. the FRAN GRACE
marker on master 315). All provenance, audit-trail, and research notes
(title corrections, publisher source evidence, promotion records) live in the
`research` column at the end of the master — hidden under Expert columns in
the spreadsheet, visible in the row-details drawer.

Two identifier conventions worth knowing: catalogue-code sequence numbers
(`LECTURE-2008-023`) follow **ledger/candidate minting order, not
chronology** (a candidate-promoted July talk can carry a higher sequence than
a raw-ledger September talk of the same year — codes are stable identifiers,
and codes are only minted when a year is known at promotion time, so some
lecture/discussion rows intentionally have none; see the field-semantics note
above and codes are never renumbered); and the master's `candidate_key`
stores the `candidate:` prefix (e.g. `candidate:manual-veritas-54219`) while
the promotion registries (`data/manual_candidate_promotions.csv`,
`data/edition_promotions.csv`) store the bare key. A third convention: despite
its name, the master `uuid` is a **stable compact integer id**, not a UUID —
values run 1–372 with gaps where duplicate records were retired (225, 226,
227, 246, 249, 264, 281, 284, 302, 309); ids are never reissued or
renumbered.

### Edition model (work × carrier)

Since 2026-08-03 the master models **one row per edition** of a work: a work
that exists as book, audiobook, and video has separate rows (DVD lecture
parts each keep their own row, grouped under one work). `work_id` groups the
rows of a work and is assigned from approved rows of the reviewed
`data/work_families.csv` input — for minted edition rows (masters 320–343),
from the approved `work_id` column of `data/edition_promotions.csv` — never
inferred from titles. Audio/CD/DVD
edition rows are minted from approved rows of `data/edition_promotions.csv`
(reviewed candidates in `data/edition_candidates.csv`); the audiobook URLs
moved off the book rows into their audiobook rows (D3). See
[EDITION_MODEL_PROPOSAL.md](EDITION_MODEL_PROPOSAL.md).

## License

This project is released under the [MIT License](LICENSE).
