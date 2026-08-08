# DocSheet — Live Spreadsheet

Renders the repository CSV as an interactive, searchable web table on
GitHub Pages (built with [Tabulator](https://tabulator.info/)).

- **Live site:** `https://56eli.github.io/docsheet` (once GitHub Pages is enabled)
- **Pipeline:** `process_data.py` reads the CSV with Pandas and publishes
  `docs/data.json` — data is currently passed through **unchanged**.
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
python -m unittest discover tests          # 121 tests, no browser/network needed
coverage run -m unittest discover tests && coverage report
```

The coverage gate (`fail_under = 85` in `.coveragerc`) passes at **91%** as of
2026-08-08; every pipeline module is ≥ 88%. `requirements-ci.txt` records the
exact Python dependency set prepared for CI/reproducible checks; apply the
workflow wiring in `WORKFLOW_WEB_EDITOR_GUIDE.md` to use it in GitHub Actions. Approved official links added after the ledger
pass live in `data/research_master_source_overrides.csv`; unresolved manual
edition/copy leads live in `data/research_manual_leads.csv` outside the master;
reviewed but unpromoted official candidates live in
`data/manual_master_candidates.csv`. Publisher-taxonomy-to-`series` proposals
live in `data/series_category_mapping.csv`, reviewed through
`data/series_taxonomy_review_queue.csv`, and become master data only after
owner approval — see `SERIES_TAXONOMY_MAPPING.md`.

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

Living documents sit at the repository root (`README`, `INSTRUCTIONS`,
`NEXT_AGENT_HANDOFF`, `archive/FULL_STACK_AUDIT_2026-08-04_FINAL_358_V2.md`, `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md`, policies, schemas,
proposals, and the generated `RECONCILIATION_REPORT.md`). Approved ruling
records live in
[`decisions/`](decisions/README.md); superseded status docs, research drafts,
and evidence notes live in [`archive/`](archive/README.md) and are not
normative.

## Curated records vs. official candidates

The **Everything** sheet intentionally shows curated master records next to
official product candidates so they can be compared. Every row therefore carries
an explicit `record_type`:

| `record_type` | Meaning |
|---|---|
| `master` | A curated master catalogue record (365) |
| `candidate_veritas` / `candidate_hayhouse` / `candidate_audible` | An official product listing shown for review; **not** a master record |
| `candidate_discovery` | An entry from the official discovery queue |
| `candidate_pending_promotion` | A reviewed manual candidate awaiting an owner promotion decision; **not** a master record |

Only `master` rows are catalogue records. Use the Record Type filter on that tab
to isolate curated data before exporting. Counts per class are published in
`docs/catalogue-meta.json` under `everything_record_types`.

The **Everything** view opens visitor-first: product facts (title, series,
type, edition, date, official store and streaming links, notes) are visible at
first sight, while technical metadata (Master ID, Work grouping, proposed file
names, provenance columns) stays hidden until the **Expert columns** toggle —
next to the Columns menu — is switched on; the choice persists per browser.
Clicking any row always shows every stored field, and the **View settings** menu can wrap long cells, switch row density, hide/show summary cards, or **Expand everything** (all columns + wrapped, roomy rows) for deep review. The layout adapts to phone screens (dense cells, full-width row details, horizontally scrolling tabs).

## Review workspace

The Pages spreadsheet exposes review inputs directly: **Review Overview**,
**Master Candidates**, **Manual Leads**, **Master Exclusions**, **Migration
Review**, **Source Overrides**, **Official Discovery**, **New Work Review**
(unmatched Veritas products awaiting a new-work ruling), **Series
Compilations**, **Veritas Decisions**, the official inventories (**Veritas
Products**, **Hay House Products**, **Audible Products**), and **Filename
Proposal** are separate sheets alongside the catalogue. Reviewers can search,
sort, export, and filter sheets with multiple review-status values without
opening repository folders. Two of these sheets (**Official Discovery** and **New Work Review**)
are intentionally empty right now: every queued item has been ruled, and the
sheets remain as standing **intake lanes** so any future Veritas catalogue
refresh lands its unmatched products there instead of in the curated views.

## Current reviewed catalogue state

The current curated master has **365** records (309 `lecture`, 40 `book`,
8 `discussion`, 7 `highlight`, 1 `other` — no untyped records remain since the
2026-08-07 rulings that record 246 was the audio edition already held as master
329 and that record 309 duplicated the Oxford talk already held as master 221),
**281** catalogue codes, **72** retained exclusions,
**131** approved source overrides (including the four Nightingale-Conant audio
editions, two Amazon Office Series links, the Audible/NC/Hay House program URLs,
and the official Veritas product link moved from retired duplicate 309 onto master 221; the three Advaita URL overlays were retired after the raw CSV was fixed),
**39** promoted and **0** unpromoted official candidates, **343** item-to-product relationships,
and **7** series-compilation relationships. The master exposes `legacy_title` alongside the cleaned public title
so the verbatim raw spreadsheet text is always exportable. Since 2026-08-04 the master also exposes `proposed_filename` between `title` and `item_type` using pattern `YYYY-MM - Name [1/3].mp4` (safe `[1-3]` on-disk, display `[1/3]`), no bracket for single part, audiobook label removed from name (`.m4b` indicates), Volume Series stripped of years (pre-2000 unknown) and standardized via `[1/2]` etc, Satsang month stripped. Since 2026-08-07 it also exposes `year_source` next to Year-Month (Ledger recording/first-pub, Veritas listing backfill, Manual candidate, Edition inherited, Blank intentional etc) and `source_url_amazon` as a curated direct Amazon product link where one has been approved (blank otherwise).

At the 2026-08-03 live-source checkpoint, every entry was verified field-by-field
against the Veritas Publishing API: 191/191 products reconciled exactly and all
195 verifiable lecture months matched the publisher's own dates. Subsequent
reviewed promotions and source corrections are covered by the current generated
inventory. See [FULL_STACK_AUDIT_2026-08-08_ARENA.md](FULL_STACK_AUDIT_2026-08-08_ARENA.md)
for the current full-stack audit and [NEXT_AGENT_HANDOFF.md](NEXT_AGENT_HANDOFF.md)
for open work; the archive reports preserve earlier checkpoints.

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
rows with an intentional blank/`198X` year (the 13 Volume Series and 16 Office
Series rows), and candidate/edition rows whose `proposed_year` was blank at
minting (e.g. the four CD/audio manual candidates 353/356/357/358 and the
edition rows 327–343, whose years were later backfilled from the official
listing), correctly carry no code. Codes are stable identifiers and are never
retroactively assigned or renumbered.

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
site renders it as a badge (`Owned` / `Not owned`) and leaves blank cells
empty; exports keep the raw `true`/`false`/empty values.

Two identifier conventions worth knowing: catalogue-code sequence numbers
(`LECTURE-2008-023`) follow **ledger/candidate minting order, not
chronology** (a candidate-promoted July talk can carry a higher sequence than
a raw-ledger September talk of the same year — codes are stable identifiers,
and codes are only minted when a year is known at promotion time, so some
lecture/discussion rows intentionally have none; see the field-semantics note
above and codes are never renumbered); and the master's `candidate_key`
stores the `candidate:` prefix (e.g. `candidate:manual-veritas-54219`) while
the promotion registries (`data/manual_candidate_promotions.csv`,
`data/edition_promotions.csv`) store the bare key.

### Edition model (work × carrier)

Since 2026-08-03 the master models **one row per edition** of a work: a work
that exists as book, audiobook, and video has separate rows (DVD lecture
parts each keep their own row, grouped under one work). `work_id` groups the
rows of a work and is assigned **only** from approved rows of the reviewed
`data/work_families.csv` input — never inferred from titles. Audio/CD/DVD
edition rows are minted from approved rows of `data/edition_promotions.csv`
(reviewed candidates in `data/edition_candidates.csv`); the audiobook URLs
moved off the book rows into their audiobook rows (D3). See
[EDITION_MODEL_PROPOSAL.md](EDITION_MODEL_PROPOSAL.md).

## License

This project is released under the [MIT License](LICENSE).
