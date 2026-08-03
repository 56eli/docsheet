# Unblock Instructions — CI Permission & Veritas Artifact

**Written:** 2026-08-03
**For:** repository owner (`56eli`), working in the GitHub web interface
**Two independent tasks.** Task A takes ~3 minutes. Task B takes ~5 minutes.
You do not need a terminal, git, or any local tooling for either.

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

# TASK B — Review the Veritas inventory artifact

## Why

The **Map Veritas Catalogue** workflow ran on `main` and **failed on purpose**.
That is the safeguard working correctly, not a bug: it fetched the live Veritas
product catalogue, compared it to the reviewed inventory committed in this
repository, found a difference, and refused to auto-update anything. It uploaded
the difference as an artifact for a human to inspect.

Nobody has inspected it yet. I can't — the artifact download redirects to Azure
blob storage, which my sandbox cannot reach (I verified the artifact itself is
intact and unexpired: **16,922 bytes**, created 2026-08-03 10:03 UTC).

**This is time-sensitive.** GitHub deletes artifacts after 90 days by default,
which means it disappears around **1 November 2026**. After that the only way to
see the difference is to re-run the workflow.

## Step 1 — download the artifact

Go directly to:

**https://github.com/56eli/docsheet/actions/runs/30803991007**

Scroll to the bottom of that page to the **Artifacts** section. You'll see:

```
veritas-inventory-review-30803991007     16.5 KB
```

Click it. Your browser downloads `veritas-inventory-review-30803991007.zip`.

> Ignore the big red "This run failed" banner — as explained above, that failure
> is the intended review signal.

## Step 2 — unzip it

Double-click the downloaded `.zip`. Inside are exactly two files:

| File | What it is |
|---|---|
| `veritas_official_products_candidate.csv` | What the live Veritas site says **right now** |
| `veritas_inventory_diff.patch` | The differences vs. our reviewed copy |

## Step 3 — look at the diff

Open **`veritas_inventory_diff.patch`** in any text editor (TextEdit, Notepad,
VS Code — anything).

You're reading a standard diff. Only two line types matter:

- Lines starting with **`-`** → a product in our reviewed inventory that the
  live site **no longer has** (delisted, renamed, or re-IDed).
- Lines starting with **`+`** → a product the live site has that our reviewed
  inventory **does not** (new release, or a changed title/date/category).

Lines starting with `@@`, `---`, or `+++` are just position markers — skip them.

## Step 4 — send it to me

**Easiest option:** attach both files to your next message here, or paste the
contents of `veritas_inventory_diff.patch` directly into the chat.

If the patch is very long, paste just the `-` and `+` lines.

## Step 5 — what I'll do with it

I will **not** blindly overwrite the reviewed inventory. For each change I'll
classify it and bring you a decision list:

| Change type | My proposal |
|---|---|
| Genuinely new official product | Add to inventory; propose as a candidate — **not** auto-promoted to a master record |
| Product removed from the live site | Keep in inventory with a "delisted" note; never silently drop reviewed evidence |
| Title/date/category edited upstream | Update the inventory field; re-apply our mapping decision overlay so the 35 reviewed dispositions survive |
| Changed product ID | Flag for your explicit decision — this can break relationship references |

You approve the classification, then I apply it as a normal reviewed change with
the `--check` modes verifying nothing else moved.

---

# Quick reference

| Task | Who | Where | Time |
|---|---|---|---|
| **A** — Create `.github/workflows/ci.yml` | You | GitHub web editor, `main` branch | ~3 min |
| **B** — Download & send the Veritas diff | You | Actions run 30803991007 | ~5 min |
| Everything after that | Me | — | — |

Neither task blocks the other, and neither blocks the data work I can already
continue on (title normalization, classifying the 87 untyped items, SRI/CSP
hardening).
