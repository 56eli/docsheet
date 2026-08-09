# 📊 INSTRUCTIONS — Live Spreadsheet Pipeline

This repository hosts a **Live Spreadsheet**: your CSV is rendered as an
interactive, searchable web table on GitHub Pages. The data flows through a
repeatable pipeline, so whenever the source file changes you can regenerate
the site in one click.

```
hawkins archive clone - Sheet1.csv        (source of truth — you edit this)
        │
        ▼  python process_data.py   (GitHub Actions: "Update Spreadsheet")
docs/data.json
        │
        ▼  GitHub Pages serves /docs
https://<username>.github.io/<repo-name>   (the live site)
```

---

## 1️⃣ Set up GitHub Pages (one-time)

1. Open your repository on GitHub.
2. Go to **Settings → Pages** (left sidebar, under "Code and automation").
3. Under **Build and deployment → Source**, select **"Deploy from a branch"**.
4. Set **Branch** to `main` and **Folder** to **`/docs`**, then click **Save**.
5. Wait ~1 minute for the first deployment. Your site is now live at:

   **`https://<username>.github.io/<repo-name>`**

   For this repository: **`https://56eli.github.io/docsheet`**

---

## 2️⃣ Add data transformation rules (when you're ready)

The raw-spreadsheet pipeline above is intentionally **pass-through** — it
displays your CSV with every cell value untouched (the published view trims
the six always-empty raw columns listed under "How the pieces fit together"
below; the source CSV keeps them). No enrichment logic has been added.

> ⚠️ This repository also hosts a separate **curated-catalogue pipeline**:
> the raw CSV flows through the hand-maintained `migration_review_ledger.csv`
> and review overlays (`data/*.csv`) into `data/research_master_draft.*` and
> the `docs/*.json` catalogue sheets, all gated by `--check` modes and the
> test suite. See the README's "Catalogue-data safeguard" section — do not
> confuse the pass-through view with the curated catalogue.

When you're ready to transform the data:

1. Open **`process_data.py`** and find the section marked:

   ```
   === DATA TRANSFORMATION RULES ===
   ```

   (It's the `apply_transformations()` function near the top of the file —
   the DataFrame is already loaded for you as **`df`**.)

2. Add your Pandas code below the marker line, e.g.:

   ```python
   df['New Column'] = df['Existing Column'].apply(some_function)
   ```

   ⚠️ Only edit that section. Everything else in the script is infrastructure.

3. Commit and push your change.
4. In GitHub, go to **Actions → "Update Spreadsheet" → Run workflow** (or just
   push a change to the CSV — the workflow also auto-triggers on that).
5. The workflow regenerates `docs/data.json` and commits it automatically.
   GitHub Pages picks up the new file within a minute or two.

---

## 3️⃣ Live site URL format

| Item | Value |
|---|---|
| Format | `https://[username].github.io/[repo-name]` |
| This repo | `https://56eli.github.io/docsheet` |
| Deploy source | Branch `main` → folder `/docs` (CI-gated Actions cutover pending) |

The footer shows the exact content versions of `app.js` and `style.css` and
links `build-manifest.json`, which also records raw/curated payload hashes. When
investigating a stale or incorrect page, record that visible build ID; do not
use a green Pages badge as a substitute for the browser revision or owner
acceptance. Required-check and CI-gated Pages cutover steps are maintained in
`.scoreboard/manual-workflow-edits.md`.

---

## 4️⃣ Test locally

```bash
pip install -r requirements.txt   # installs pandas
python process_data.py            # regenerates docs/data.json (view trims 6 always-empty raw columns)
python process_data.py --check    # verifies generated outputs match the source
```

Then serve the site over HTTP (the page uses `fetch()`, which doesn't work
when opening the file directly from disk):

```bash
python -m http.server 8000
# open http://localhost:8000/docs/
```

To verify browser behavior, including CSV export from the active spreadsheet view:

```bash
npm ci
npm run test:e2e:install
npm run test:e2e
```

### Edition model inputs (work × carrier)

Since 2026-08-03 the curated master holds **one row per edition** of a work
(book / audio / video). The Work column shows the `work_id` that groups a
work's edition rows; the Edition column merges `format` + `format_detail`
(e.g. "audiobook · Audiobook"). Two reviewed inputs drive this:

- `data/work_families.csv` — `work_id` per master row (approved rows only;
  never title-inferred).
- `data/edition_candidates.csv` + `data/edition_promotions.csv` — reviewed
  edition rows (audiobooks, CD/DVD sets, audio programs) minted into the
  master after owner approval.

See `EDITION_MODEL_PROPOSAL.md` for the model, rulings, and status.

### Curated catalogue and review workspace

The raw spreadsheet pipeline is separate from the reviewed research catalogue.
Before writing curated derivatives, validate the current inputs:

```bash
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
python map_series_taxonomy.py --check
python sync_inventory_mirrors.py --check   # derived inventory mirrors (see below)
```

The Veritas inventory's mirror columns (`normalized_title_match_count`,
`matched_master_titles`, and — for `matched_by_primary_source` rows —
`matched_master_uuids`) are derived from the curated master, never edited by
hand. After changing master titles or Veritas URLs, run
`python sync_inventory_mirrors.py` to re-derive them (then rebuild below and
re-run the checks). The tool refuses to write when a reviewed non-primary
association contradicts URL evidence — that needs an owner ruling, not a sync.

After an approved review-input change, rebuild in this order and then repeat the
checks:

```bash
python build_research_master.py
python map_series_taxonomy.py        # taxonomy mirrors follow the master + inventory
python build_research_master.py      # re-apply if mapped_series values changed
python build_catalogue_pages.py
python reconcile_research_master.py
```

The generated Pages workspace includes the catalogue plus dedicated review
sheets for candidates, leads, exclusions, migration review, source overrides,
official discovery, Veritas decisions, item-product relationships, and series
compilations. Three additional reviewed inputs shape the master without
hand-editing generated files: `data/master_year_overrides.csv` (owner
year/month/year_source corrections), `data/master_notes_overrides.csv`
(verbatim notes replacements), and `data/catalogue_display_order.csv` (the
owner-approved block order of the Everything view and its CSV export; the
change record is the colour-coded `review/hawkins-everything-REVISION1.ods`).
See `docs/audits/2026-08-09-full-audit-019fe830-multidisciplinary.md` (declared-current multidisciplinary audit at `9e4ee4d`) alongside
`archive/FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` (with its
extension `archive/FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md`) for full-stack evidence and `NEXT_AGENT_HANDOFF.md` §6 for current risk and roadmap
status (`archive/` material is historical and not normative).

### Pipeline test suite and coverage gate

`tests/test_pipeline.py` exercises the whole pipeline without a browser or
network: every generator runs end-to-end in sandboxed copies of the inputs
(write, `--check`, tamper detection, CLI entrypoint smoke), the CSV generators
are held to run-twice determinism, the Veritas fetcher is replayed offline
against a synthetic API rebuilt from the committed inventory (including its
retry ladder), and the rule matrices (taxonomy dominance, matching, format
inference, validators) are unit-tested directly.

```bash
pip install -r requirements-dev.txt    # runtime deps + coverage
python -m unittest discover tests      # 146 deterministic tests
coverage run -m unittest discover tests
coverage report                        # exits non-zero below the 85% floor (.coveragerc)
```

> House rule: when the suite grows or shrinks, update the test count here and
> in the README's quick-start line in the same change — it has drifted three
> times (103 → 107 → 110 → 112 → 115 → 117 → 121 → 123 → 125 → 126 → 132 → 139 → 141 → 145 → 146).

Current coverage: **90% total; individual modules 78–100%** (2026-08-09;
style tests are excluded from the coverage denominator).
For exact CI reproduction, install with `pip install -r requirements-dev.txt -c requirements-ci.txt`.
The remaining misses are `if __name__ == "__main__"` guards and rare
dependency-error branches. Browser behavior stays with Playwright
(`npm run test:e2e`), which needs Chromium and runs in CI.

### Veritas refresh review

Do not overwrite the reviewed Veritas inventory directly from the live API.
The product-ID decisions in `data/veritas_mapping_decisions.csv` are reapplied
after deterministic matching:

```bash
python fetch_veritas_catalogue.py --check
# or write a review candidate without replacing the committed inventory:
python fetch_veritas_catalogue.py --output data/veritas_official_products_candidate.csv
```

Review any candidate diff, update decisions deliberately, rebuild the catalogue,
and run the curated checks. The Map Veritas workflow follows this review-only
pattern and uploads its candidate/diff artifact instead of auto-committing.
Merge the branch code/data first, then run it manually in GitHub Actions and
inspect the artifact before accepting any live-source update.

---

## 🔧 How the pieces fit together

| File | Purpose |
|---|---|
| `hawkins archive clone - Sheet1.csv` | Your source data — never modified by the pipeline. |
| `process_data.py` | Reads the CSV with Pandas, applies your rules (none yet), writes `docs/data.json` (array of objects; 6 always-empty raw columns are trimmed from the view per owner ruling 2026-08-07 — the source CSV keeps them). Handles errors gracefully and exits non-zero on failure so CI shows the error. |
| `requirements.txt` | Flexible Python runtime dependencies (pandas only, for now). |
| `requirements-ci.txt` | Exact tested Python constraints used by CI and the raw-data updater. |
| `docs/index.html` | Page shell: top bar (search + export + dark-mode toggle), table area, footer bar. |
| `docs/app.js` | Boots the read-only catalogue UI: Tabulator sorting/columns/exports and review filters on desktop; on phones, the Everything view defaults to work-card Browse mode with Source/Stream actions, Series and Timeline discovery rails, and a persistent Spreadsheet escape hatch. It also owns row details, footer stats, and View settings (wrap cells, compact rows, summary cards, Expand everything). |
| `docs/style.css` | Google Sheets–inspired styling, zebra rows, hover highlight, frozen header, dark mode. |
| `.github/workflows/update_spreadsheet.yml` | Rebuilds `docs/data.json` on demand (manual) or when the CSV changes on `main`. No schedule yet. |

### Notes & current behavior

- **Header row:** the CSV's first line is a stray Google Sheets title row
  (`archive clbs`); the real header (`uuid, tempid, title, ...`) is line 2, so
  `process_data.py` reads with `header=1`. Cell values are passed through
  **unchanged** (only the six always-empty raw columns — `uuid`,
  `Unnamed: 8–11`, `other links` — are trimmed from the published view).
- **Footer:** shows the active view's row count and its HTTP `Last-Modified`
  value. (The legacy `docs/meta.json` descriptor was dropped by owner ruling
  2026-08-07: nothing but `process_data.py`'s own self-check ever read it,
  and its `generated_at` timestamp only churned diffs.)
- **Read-only published views:** catalogue and review sheets are generated from
  committed CSV inputs and cannot be edited in the browser. Make reviewed changes
  in their declared input file, regenerate the derived outputs, and run the
  checks before publishing.
- **Search:** the search box filters **all** columns live as you type.
- **Export CSV:** downloads all rows of the active sheet (filters/search affect the on-screen view, not the exported dataset).
- **Dark mode:** toggle in the top-right; your choice is remembered
  (localStorage) and respects your OS preference the first time.

## ❓ Troubleshooting

- **Workflow fails** → open the run in **Actions**, read the log, and try
  `python process_data.py` locally. The script prints a clear error.
- **Raw CSV workflow contract (owner-applied, PR merge prerequisite):** CI on
  `main` now ignores a raw-only push so it cannot race `Update Spreadsheet`,
  which regenerates `docs/data.json`. The workflow also uses the pinned
  `requirements-ci.txt`; PR #34 merged this configuration to `main` and the
  subsequent main CI run passed. A pull request that changes the raw CSV must
  include regenerated `docs/data.json` (run `python process_data.py`).
- **Site shows stale data** → re-run the workflow (or push a CSV change) and
  confirm the Pages deployment finished in **Actions → Pages** / **Environments**.
- **Table is empty / "Could not load data.json"** → you opened the file via
  `file://`. Serve over HTTP (see section 4) or use the deployed site.
- **CSV renamed** → pass the new name to the script:
  `python process_data.py "new name.csv"` (the workflow always uses the
  default filename; update `DEFAULT_CSV` in `process_data.py` if you rename it).
