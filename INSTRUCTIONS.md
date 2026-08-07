# 📊 INSTRUCTIONS — Live Spreadsheet Pipeline

This repository hosts a **Live Spreadsheet**: your CSV is rendered as an
interactive, searchable web table on GitHub Pages. The data flows through a
repeatable pipeline, so whenever the source file changes you can regenerate
the site in one click.

```
hawkins archive clone - Sheet1.csv        (source of truth — you edit this)
        │
        ▼  python process_data.py   (GitHub Actions: "Update Spreadsheet")
docs/data.json  +  docs/meta.json
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
displays your CSV exactly as-is. No enrichment logic has been added.

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
| Deploy source | Branch `main` → folder `/docs` |

---

## 4️⃣ Test locally

```bash
pip install -r requirements.txt   # installs pandas
python process_data.py            # regenerates docs/data.json + meta.json
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
```

After an approved review-input change, rebuild in this order and then repeat the
checks:

```bash
python build_research_master.py
python build_catalogue_pages.py
python reconcile_research_master.py
```

The generated Pages workspace includes the catalogue plus dedicated review
sheets for candidates, leads, exclusions, migration review, source overrides,
official discovery, Veritas decisions, item-product relationships, and series
compilations. See
`archive/PROJECT_STATE_AUDIT.md` and `archive/IMPLEMENTATION_PLAN.md` for current risk and
roadmap status.

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
python -m unittest discover tests      # 103 deterministic tests
coverage run -m unittest discover tests
coverage report                        # exits non-zero below the 80% floor (.coveragerc)
```

Current coverage: **92% total, every pipeline module ≥ 89%** (2026-08-03).
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
| `process_data.py` | Reads the CSV with Pandas, applies your rules (none yet), writes `docs/data.json` (array of objects) + `docs/meta.json` (row count, timestamp). Handles errors gracefully and exits non-zero on failure so CI shows the error. |
| `requirements.txt` | Python dependencies (pandas only, for now). |
| `docs/index.html` | Page shell: top bar (search + export + dark-mode toggle), table area, footer bar. |
| `docs/app.js` | Boots Tabulator with sorting, all rows in one scrollable view, inline editing, CSV export, column resizing, horizontal access to every column, and footer stats. |
| `docs/style.css` | Google Sheets–inspired styling, zebra rows, hover highlight, frozen header, dark mode. |
| `.github/workflows/update_spreadsheet.yml` | Rebuilds `docs/data.json` on demand (manual) or when the CSV changes on `main`. No schedule yet. |

### Notes & current behavior

- **Header row:** the CSV's first line is a stray Google Sheets title row
  (`archive clbs`); the real header (`uuid, tempid, title, ...`) is line 2, so
  `process_data.py` reads with `header=1`. Cell values are passed through
  **unchanged**.
- **Footer:** shows the active view's row count and its HTTP `Last-Modified`
  value. `docs/meta.json` remains a machine-readable build artifact for the raw
  spreadsheet pipeline and its `--check` validation.
- **Read-only published views:** catalogue and review sheets are generated from
  committed CSV inputs and cannot be edited in the browser. Make reviewed changes
  in their declared input file, regenerate the derived outputs, and run the
  checks before publishing.
- **Search:** the search box filters **all** columns live as you type.
- **Export CSV:** downloads the currently filtered/sorted view.
- **Dark mode:** toggle in the top-right; your choice is remembered
  (localStorage) and respects your OS preference the first time.

## ❓ Troubleshooting

- **Workflow fails** → open the run in **Actions**, read the log, and try
  `python process_data.py` locally. The script prints a clear error.
- **Site shows stale data** → re-run the workflow (or push a CSV change) and
  confirm the Pages deployment finished in **Actions → Pages** / **Environments**.
- **Table is empty / "Could not load data.json"** → you opened the file via
  `file://`. Serve over HTTP (see section 4) or use the deployed site.
- **CSV renamed** → pass the new name to the script:
  `python process_data.py "new name.csv"` (the workflow always uses the
  default filename; update `DEFAULT_CSV` in `process_data.py` if you rename it).
