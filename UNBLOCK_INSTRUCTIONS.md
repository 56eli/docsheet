# Unblock Instructions — CI Permission & Veritas Artifact

**Written:** 2026-08-03
**For:** repository owner (`56eli`), working in the GitHub web interface
**One task remaining (Task A, ~3 minutes).** Task B is complete — see below.
You do not need a terminal, git, or any local tooling.

---

# TASK A — Let the agent add the CI workflow

## Why

Every quality check in this project currently passes only because someone
remembers to run it by hand. The test files, the `--check` modes, and the npm
scripts are all already committed — the *only* missing piece is the workflow
file that runs them automatically on each push.

I cannot create that file myself. When I try to push it, GitHub replies:

> refusing to allow a GitHub App to create or update workflow
> `.github/workflows/ci.yml` without `workflows` permission

I re-confirmed this today with a test push. So **you** need to create the file.
Once it exists on `main`, I can edit it freely in future — the restriction only
blocks creating/updating workflow files, and it applies to me, not to you.

## Option A1 (recommended) — you create the file, once

### Step 1
Go to: **https://github.com/56eli/docsheet**

### Step 2
Make sure the branch selector (top-left, above the file list) says **`main`**.

### Step 3
Click the **`Add file`** button (top right of the file list) → **`Create new file`**.

### Step 4
In the filename box at the top, type exactly this — **including the slashes**:

```
.github/workflows/ci.yml
```

> GitHub will turn each `/` into a folder automatically as you type. When you're
> done, the breadcrumb above the box should read `docsheet / .github / workflows / ci.yml`.

### Step 5
Paste the **entire** block below into the large editor area. This is the
complete file — nothing to fill in, nothing to change.

```yaml
# ============================================================================
# CI — read-only validation for pull requests and main.
#
# Runs the deterministic checks that already exist in the repository:
#   - Python syntax compilation
#   - the three generator --check modes (master, Pages, reconciliation)
#   - JavaScript syntax checks
#   - Playwright browser smoke tests
#
# This workflow never writes to the repository and never contacts a live
# product API. Live Veritas refreshes stay manual in map_veritas_catalogue.yml.
# ============================================================================
name: CI

on:
  pull_request:
  push:
    branches: [main]
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
        run: pip install -r requirements.txt

      - name: Compile all Python scripts
        run: python -m py_compile *.py

      - name: Verify research master matches the review ledger
        run: python build_research_master.py --check

      - name: Verify Pages catalogue matches its inputs
        run: python build_catalogue_pages.py --check

      - name: Verify reconciliation report is current
        run: python reconcile_research_master.py --check

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm

      - name: Check JavaScript syntax
        run: |
          node --check docs/app.js
          node --check playwright.config.js
          node --check tests/csv-export.spec.js

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

### Step 6
Scroll to the bottom. In the **Commit new file** box:

- Commit message: `Add read-only CI workflow`
- Leave **"Commit directly to the `main` branch"** selected.

Click the green **`Commit new file`** button.

### Step 7 — verify it works
Click the **Actions** tab at the top of the repository. Within a few seconds a
run named **CI** should appear.

- ✅ **Green check** → done. This is also the first true browser-test execution
  this project has ever had; it certifies the CSV export and Everything-view
  tests that I can only syntax-check in my sandbox.
- ❌ **Red X** → click the run, click the failing step, and paste me the error.
  Most likely cause would be the Chromium install step, which I have no way to
  rehearse locally.

### Step 8 — tell me
Reply "CI added" and I'll take over maintaining it from there.

---

## Option A2 (alternative) — grant me the permission instead

If you'd rather I own the workflow file, expand the Arena GitHub App's scope:

1. Go to **https://github.com/settings/installations**
2. Find the **Arena** app in the list → click **`Configure`**.
3. Look for a **Permissions** section. If GitHub shows a pending permission
   request banner at the top, click **`Review request`** and **`Accept`**.
4. If there's no banner, the permission has to come from the app's own
   configuration — in that case use **Option A1** above, or reconnect GitHub
   from inside Arena and approve the expanded scope when prompted.
5. Reply "workflows granted" and I'll create `ci.yml` myself and verify the run.

> **Note:** Option A1 is more reliable. The `workflows` scope is one that many
> GitHub App installations simply cannot self-grant, which is why I'm
> recommending you create the single file directly.

---

# TASK B — Review the Veritas inventory artifact ✅ COMPLETE

**You already did this** — you supplied the diff on 2026-08-03 and it is now resolved.
No further action needed. Full write-up: [VERITAS_ARTIFACT_REVIEW.md](VERITAS_ARTIFACT_REVIEW.md).

**Result in one line:** the live Veritas catalogue had **not** changed — the diff
exposed a small defect in our own committed data, which is now fixed and guarded.

All 191 products were identical upstream. The six differing lines were all one
derived field (`normalized_title_match_count`) that claimed `0` while naming one
matched master record — an internal contradiction introduced when the approved
decision overlay recorded the matched IDs without carrying through the recomputed
count. I reproduced the correction offline from committed inputs, applied it, and
added a build guard so it cannot recur silently.

**Optional follow-up:** re-run **Map Veritas Catalogue** once from the Actions tab.
It should now **pass** instead of failing, which confirms the fix and means any
future failure is a genuine upstream change worth your attention.

---

# Quick reference

| Task | Who | Where | Time |
|---|---|---|---|
| **A** — Create `.github/workflows/ci.yml` | You | GitHub web editor, `main` branch | ~3 min |
| ~~**B** — Download & send the Veritas diff~~ | ✅ Done | Resolved 2026-08-03 | — |
| Everything after that | Me | — | — |

Only Task A remains. It doesn't block the data work I can continue on in the
meantime (title normalization, classifying the 87 untyped items, SRI/CSP hardening).
