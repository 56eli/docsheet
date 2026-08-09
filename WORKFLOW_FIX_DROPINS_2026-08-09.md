# Workflow Pin Fix — Drop-in Replacements (2026-08-09)

**Reason:** GitHub App cannot push `.github/workflows/*` without `workflows` permission. Apply these 3 corrected files via GitHub’s **web editor** (pencil icon) — same flow as prior `node-version 20→22` bump.

**PR:** `arena/019fe5d4-docsheet` → `main` (#40) is already pushed **without** these 3 files. After you paste the drop-ins, the branch and `main` will both have the correct pins (`v7` does not exist; correct pins are `v4`/`v5`).

---

## 1. `.github/workflows/ci.yml` — replace entire file with:

```yaml
# ============================================================================
# CI — read-only validation for pull requests and main.
# ============================================================================
name: CI
on:
  pull_request:
  push:
    branches: [main]
    # The raw-source updater owns docs/data.json regeneration after a raw-only
    # main push. Do not race it with a second CI check against stale output.
    paths-ignore:
      - "hawkins archive clone - Sheet1.csv"
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
jobs:
  validate:
    name: Validate data pipeline and site
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Install Python dependencies
        run: pip install -r requirements.txt -c requirements-ci.txt
      - name: Compile all Python scripts
        run: python -m py_compile *.py
      - name: Verify raw spreadsheet Pages payload matches its source
        run: python process_data.py --check
      - name: Verify research master matches the review ledger
        run: python build_research_master.py --check
      - name: Verify Pages catalogue matches its inputs
        run: python build_catalogue_pages.py --check
      - name: Verify reconciliation report is current
        run: python reconcile_research_master.py --check
      - name: Verify series-taxonomy mapping matches its inputs
        run: python map_series_taxonomy.py --check
      - name: Verify Veritas inventory mirrors match the master
        run: python sync_inventory_mirrors.py --check
      - name: Run deterministic pipeline test suite
        run: python -m unittest discover tests
      - name: Enforce the coverage floor (85%)
        run: |
          pip install -r requirements-dev.txt -c requirements-ci.txt
          coverage run -m unittest discover tests
          coverage report
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
      - name: Check JavaScript syntax
        run: |
          node --check docs/app.js
          node --check playwright.config.js
          for spec in tests/*.spec.js; do node --check "$spec"; done
      - name: Install Node dependencies
        run: npm ci
      - name: Install Chromium for browser tests
        run: npx playwright install --with-deps chromium
      - name: Run browser smoke tests
        run: npm run test:e2e
        env:
          CI: "true"
      - name: Upload Playwright report on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
          if-no-files-found: ignore
```

---

## 2. `.github/workflows/map_veritas_catalogue.yml` — replace entire file with:

```yaml
name: Map Veritas Catalogue

on:
  workflow_dispatch:

# A refresh is intentionally review-only. The workflow writes a candidate
# inventory and diff artifact; a reviewer applies approved mapping decisions
# and commits the reviewed inventory through a normal branch change.
permissions:
  contents: read

concurrency:
  group: map-veritas-catalogue-${{ github.ref }}
  cancel-in-progress: false

jobs:
  map-catalogue:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout selected branch
        uses: actions/checkout@v4
        with:
          ref: ${{ github.ref }}
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Fetch reviewed inventory candidate
        run: >
          python fetch_veritas_catalogue.py
          --output data/veritas_official_products_candidate.csv
      - name: Compare candidate with reviewed inventory
        id: inventory-diff
        shell: bash
        run: |
          set +e
          git diff --no-index -- \
            data/veritas_official_products.csv \
            data/veritas_official_products_candidate.csv \
            > data/veritas_inventory_diff.patch
          status=$?
          if [ "$status" -gt 1 ]; then
            exit "$status"
          fi
          if [ "$status" -eq 1 ]; then
            echo "A reviewed inventory update is required; inspect the artifact diff." >&2
            exit 1
          fi
          echo "Candidate matches the reviewed inventory."
      - name: Upload candidate and diff for review
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: veritas-inventory-review-${{ github.run_id }}
          path: |
            data/veritas_official_products_candidate.csv
            data/veritas_inventory_diff.patch
          if-no-files-found: warn
```

---

## 3. `.github/workflows/update_spreadsheet.yml` — replace entire file with:

```yaml
# ============================================================================
# Update Spreadsheet — regenerates docs/data.json from the source CSV.
# ============================================================================
name: Update Spreadsheet
on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - "hawkins archive clone - Sheet1.csv"
permissions:
  contents: write
concurrency:
  group: update-spreadsheet
  cancel-in-progress: true
jobs:
  update-data:
    name: Regenerate docs/data.json
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Install dependencies
        run: pip install -r requirements.txt -c requirements-ci.txt
      - name: Run the pipeline
        run: python process_data.py
      - name: Commit updated data
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Update docs data via Live Spreadsheet pipeline"
          file_pattern: docs/data.json
          commit_user_name: github-actions[bot]
          commit_user_email: github-actions[bot]@users.noreply.github.com
```

---

## How to apply via web editor

1. Open `https://github.com/56eli/docsheet` → switch branch to `arena/019fe5d4-docsheet` **or** `main` (either; the fix is identical).
2. Click the file path above (e.g. `.github/workflows/ci.yml`) → click the **pencil** (Edit this file).
3. Select all (`Ctrl+A`), paste the **entire** replacement block for that file (including the first `---` line if shown? No — paste only the YAML content between the triple backticks, not the markdown fences).
4. At the bottom, choose **Commit directly to the `...` branch**, add message e.g. `fix: pin GitHub Actions to v4/v5 (v7 does not exist)` → **Commit changes**.
5. Repeat for the other 2 files.

After committing, `python -m py_compile *.py` and all 6 `--check` modes + `125/125 tests` still pass (the workflows are not part of local checks, but CI will now resolve the correct action versions).

See also `archive/UNBLOCK_INSTRUCTIONS.md` for the prior pattern and `FULL_STACK_AUDIT_2026-08-09_ARENA.md §14` for the audit note on this permission gap.
