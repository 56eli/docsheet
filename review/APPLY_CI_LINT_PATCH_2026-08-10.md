# Apply the CI lint patch — GitHub web editor, step by step

**Prepared:** 2026-08-10 (Arena 019febe9) — for the owner's web editor.
**Why:** the GitHub App token used by the sandbox lacks `workflows` permission,
so the branch cannot push `.github/workflows/ci.yml` itself. The exact change is
also committed as `.scoreboard/ci-lint-workflow-edit-2026-08-10.patch`
(`git apply` equivalent), but this file gives you a drop-in copy/paste for the
web editor.

> ⚠️ **Order matters:** the new `npm run lint` step needs the lint
> infrastructure (`eslint.config.mjs`, the `lint` script, the `eslint`
> devDependency) which lives on the `arena/019febe9-docsheet` branch — **not on
> `main` yet**. Do one of:
> - **(A)** merge the `arena/019febe9-docsheet` PR to `main` first, then apply
>   only the ci.yml change below; or
> - **(B)** include `eslint.config.mjs` and the updated `package.json` /
>   `package-lock.json` in the same web-editor commit as the ci.yml change.

---

## 1. Open the file in the web editor

1. Go to <https://github.com/56eli/docsheet/blob/main/.github/workflows/ci.yml>
2. Click the **pencil icon** ("Edit this file") in the top-right.

## 2. Replace the whole file with this content

Select everything (Ctrl/Cmd+A), delete, and paste:

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
          for module in docs/js/*.js; do node --check "$module"; done
          node --check playwright.config.js
          for spec in tests/*.spec.js; do node --check "$spec"; done
      - name: Install Node dependencies
        run: npm ci
      - name: Lint shipped frontend for undefined references
        run: npm run lint
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

If you prefer **two minimal edits** instead of replacing the whole file:

- **Edit 1** — inside the `Check JavaScript syntax` step, add one line:
  `          for module in docs/js/*.js; do node --check "$module"; done`
  directly after `node --check docs/app.js`.
- **Edit 2** — immediately after the `Install Node dependencies` step (`run: npm ci`), add:
  `      - name: Lint shipped frontend for undefined references`
  `        run: npm run lint`

## 3. Commit

1. Scroll to **"Commit changes"**.
2. Title: `ci(lint): check all docs/js modules and lint no-undef on shipped frontend`
3. Under the commit title, choose:
   - **"Create a new branch for this commit and start a pull request"** —
     recommended (CI will run before merge), or
   - **"Commit directly to the `main` branch"** if you are sure.
4. Click **Commit changes**.

## 4. Verify

1. Open **Actions** on GitHub.
2. The `CI` run (on the commit/PR) should show a green
   **"Lint shipped frontend for undefined references"** step.
3. If it ever fails, it means the shipped `docs/app.js` / `docs/js/*.js` code
   references an undefined variable — exactly the P0-class bug that broke the
   live site on 2026-08-10 — and it is now caught before any browser test or
   deploy.

## Reference

- Same change as a git patch: `.scoreboard/ci-lint-workflow-edit-2026-08-10.patch`
  (`git apply .scoreboard/ci-lint-workflow-edit-2026-08-10.patch`).
- Lint config: `eslint.config.mjs` (flat config; `no-undef`; browser globals).
- Script: `npm run lint` → `eslint docs/app.js docs/js/*.js`.
- Recorded in `.scoreboard/manual-workflow-edits.md`.
