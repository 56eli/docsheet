# GitHub Web-Editor Workflow Guide — Drop-in Snippets

**Prepared:** 2026-08-08 · branch `arena/019fe11d-docsheet`

The Arena GitHub App **cannot push changes to `.github/workflows/*`** (GitHub
rejects the push — workflows need the `workflows` permission). Apply workflow
edits yourself in the GitHub web editor. Each item below is self-contained:
open the file, find the "Replace this" block, paste the "With this" block over
it, and commit directly to `main`.

Item 1 and Item 2 are now applied on `main` by the owner (the full-file
blocks below are retained as a copy/paste record). The Node 20→22 project-runtime
bump was already applied (commit `406116f`); Item 2 upgraded the action runtimes
to current Node-24-compatible majors. **Important ordering:** the workflow
changes reference `requirements-ci.txt`, which was merged through PR #34; the subsequent main CI run passed. The
PR remains the change record for that configuration.

---

## Item 1 — Cover every Playwright spec in the JS-syntax check — ✅ APPLIED 2026-08-08

**Why:** `.github/workflows/ci.yml` syntax-checks only
`tests/csv-export.spec.js`. A syntax error in
`tests/column-layout.spec.js` would slip past the fast JS step and only surface
later in the slower Chromium browser-smoke step. Looping over `tests/*.spec.js`
matches the local verification command in `NEXT_AGENT_HANDOFF.md` §2 and
catches every spec early.

**File:** `.github/workflows/ci.yml`
(on `main`: https://github.com/56eli/docsheet/edit/main/.github/workflows/ci.yml)

### Step by step

1. Open the link above (or **`main` → `.github/workflows/ci.yml` → ✏️ Edit**).
2. Find the **"Check JavaScript syntax"** step (around line 65).
3. Select the whole block shown under **Replace this** below and overwrite it
   with the **With this** block.
4. Scroll up to **Commit changes…**, set:
   - Commit message: `ci: syntax-check every Playwright spec`
   - Choose **"Commit directly to the `main` branch"**.
5. Click **Commit changes**.
6. Go to the **Actions** tab, open the run that this push started, and confirm
   **"Check JavaScript syntax"** is green (the browser tests still run after
   it and should stay green too).

### Replace this

```yaml
      - name: Check JavaScript syntax
        run: |
          node --check docs/app.js
          node --check playwright.config.js
          node --check tests/csv-export.spec.js
```

### With this

```yaml
      - name: Check JavaScript syntax
        run: |
          node --check docs/app.js
          node --check playwright.config.js
          for spec in tests/*.spec.js; do node --check "$spec"; done
```

### How to verify it worked

After CI runs, the **"Check JavaScript syntax"** step log should show no output
and exit 0. To confirm the glob actually covers every spec, you can temporarily
introduce a typo in `tests/column-layout.spec.js` locally and run:

```bash
for spec in tests/*.spec.js; do node --check "$spec" || echo "FAILED: $spec"; done
```

It should print `FAILED: tests/column-layout.spec.js` — i.e. the loop checks
that file (revert the typo afterwards).

---

## Item 2 — Remove raw-output/CI race and upgrade action runtimes — ✅ APPLIED ON MAIN

**Why:** a raw-only push to `main` currently starts CI and the raw-data updater
at the same time. CI can inspect stale `docs/data.json` before the updater's
bot commit lands. The same raw-output contract must remain explicit for pull
requests. GitHub's current runner also warns that the old action majors target
Node 20 internally; the current majors target the supported Node 24 runtime.

The code-side hardening is in this branch: `process_data.py` validates raw
headers/fallbacks and `requirements-ci.txt` pins the tested Python set. The
owner applied the workflow edits on `main`; use the full blocks below as the
canonical replacement record. Verify CI after any future workflow change that alters the
constraint file.

### `.github/workflows/ci.yml`

1. Upgrade action majors:

```yaml
uses: actions/checkout@v7
uses: actions/setup-python@v7
uses: actions/setup-node@v7
uses: actions/upload-artifact@v7
```

Keep each action's existing `with:` / `env:` / `if:` blocks.

2. Replace the `push` trigger:

```yaml
  push:
    branches: [main]
    paths-ignore:
      - "hawkins archive clone - Sheet1.csv"
```

The raw-only `main` push is handled by `Update Spreadsheet`; code/data-only
pushes still run CI. Pull-request CI remains active and requires the generated
`docs/data.json` to be included when a PR changes the raw CSV.

3. Use the tested Python constraints in both install steps:

```yaml
run: pip install -r requirements.txt -c requirements-ci.txt
```

and:

```yaml
pip install -r requirements-dev.txt -c requirements-ci.txt
```

### `.github/workflows/update_spreadsheet.yml`

Upgrade `actions/checkout@v7`, `actions/setup-python@v7`,
and `stefanzweifel/git-auto-commit-action@v7`; change its install step to:

```yaml
run: pip install -r requirements.txt -c requirements-ci.txt
```

### `.github/workflows/map_veritas_catalogue.yml`

Upgrade `actions/checkout@v7`, `actions/setup-python@v7`, and
`actions/upload-artifact@v7`. This workflow has no third-party Python install;
the fetcher uses the standard library.

**Verification:** run `python -m unittest discover tests`, all six `--check`
commands, and inspect the next CI run. The exact local constraint command is:

```bash
pip install -r requirements-dev.txt -c requirements-ci.txt
```

---

## Full-file replacement blocks — copy/paste option

If you prefer not to edit individual snippets, replace each workflow file in
full. The blocks below are the complete intended files for the current branch.
They contain no secrets or repository-specific tokens.

### Full `.github/workflows/ci.yml`

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
        uses: actions/checkout@v7
      - name: Set up Python
        uses: actions/setup-python@v7
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
        uses: actions/setup-node@v7
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
        uses: actions/upload-artifact@v7
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
          if-no-files-found: ignore
```

### Full `.github/workflows/update_spreadsheet.yml`

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
        uses: actions/checkout@v7
      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"
          cache: pip
      - name: Install dependencies
        run: pip install -r requirements.txt -c requirements-ci.txt
      - name: Run the pipeline
        run: python process_data.py
      - name: Commit updated data
        uses: stefanzweifel/git-auto-commit-action@v7
        with:
          commit_message: "Update docs data via Live Spreadsheet pipeline"
          file_pattern: docs/data.json
          commit_user_name: github-actions[bot]
          commit_user_email: github-actions[bot]@users.noreply.github.com
```

### Full `.github/workflows/map_veritas_catalogue.yml`

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
        uses: actions/checkout@v7
        with:
          ref: ${{ github.ref }}
      - name: Set up Python
        uses: actions/setup-python@v7
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
        uses: actions/upload-artifact@v7
        with:
          name: veritas-inventory-review-${{ github.run_id }}
          path: |
            data/veritas_official_products_candidate.csv
            data/veritas_inventory_diff.patch
          if-no-files-found: warn
```

### Web-editor apply checklist

1. Open each workflow on `main` in GitHub and select **Edit this file**.
2. Replace the entire file with the matching block above.
3. Commit directly to `main` (workflow files need the owner/workflows permission).
4. Confirm the next CI run is green and its action-runtime warning is gone.
5. For a raw CSV change, run `python process_data.py` locally in the PR so
   `docs/data.json` is included before merging; after merge, the updater owns
   the raw-only `main` regeneration path.

---

## Already applied (no action needed)

### Node 20 → 22 — ✅ applied as commit `406116f`

The CI workflow pins `node-version: "22"` in the **Set up Node** step. Node 20
reached EOL on 2026-04-30; Node 22 is active LTS. Nothing to do — if you want
to confirm, open `.github/workflows/ci.yml` and check the step reads:

```yaml
      - name: Set up Node
        uses: actions/setup-node@v7
        with:
          node-version: "22"
          cache: npm
```

---

## Notes

- **Commit directly to `main`** for these workflow-only edits; they are
  validated locally (`node --check` passes on every spec) and do not change
  catalogue data.
- If you would rather go through a branch/PR, choose **"Create a new branch"**
  in the commit dialog instead — but then merge it before the change takes
  effect on `main`.
- Historical note: the stale-50491 and related documentation fixes from
  `arena/019fe11d-docsheet` have since merged to `main`; no owner workflow
  edit or follow-up PR is required for that completed batch.
