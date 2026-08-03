# GitHub Pages Deployment Troubleshooting & Root Cause Analysis — 2026-08-03

**Date:** 2026-08-03  
**Repository:** `56eli/docsheet` (`main` branch, `/docs` folder)  
**Status:** Preventative fix applied (`docs/.nojekyll` added to bypass Jekyll processing); full diagnostic guide provided below.

---

## Executive Summary

If your GitHub Pages site (`https://56eli.github.io/docsheet`) stopped deploying from `main/docs` since the last merge, there are four potential root causes—ranging from **Jekyll build timeouts on large generated JSON files** (the most likely technical cause, which we have preventative-fixed in this branch) to **GitHub Actions token trigger restrictions** and **Settings misconfigurations**.

This report analyzes each possible root cause in order of likelihood, explains why it occurs after recent merges, and provides step-by-step instructions for diagnosis and remediation.

---

## Root Cause 1: Jekyll Build Timeout / Parser Failure on Large JSON Payloads (Most Likely Technical Cause — Preventatively Fixed)

### Why it happened since the last merge
When you configure GitHub Pages to deploy from `main` / `/docs`, GitHub Pages automatically runs **Jekyll** (`pages-build-deployment` / `github-pages` action) on the directory unless instructed otherwise. 

In recent merges (such as PR #17), several generated data sheets in `docs/` grew significantly in size and complexity:
- `docs/master.json`: ~341 KB (10,700+ lines)
- `docs/migration-review.json`: ~354 KB (10,100+ lines)
- `docs/product-relationships.json`: ~310 KB (6,500+ lines)
- `docs/data.json`: ~140 KB (5,600+ lines)

Jekyll attempts to scan, read, and parse every file in `/docs` during the build step. Large JSON payloads, special characters, or nested strings can cause Jekyll's default parser to time out, exhaust memory, or fail silently during the `pages-build-deployment` workflow run.

### Remediation & Preventative Fix
- **What we did in this branch:** We added an empty `.nojekyll` file inside the docs directory (`docs/.nojekyll`).
- **Why this fixes it:** The presence of `docs/.nojekyll` tells GitHub Pages to bypass Jekyll processing entirely and serve `/docs` directly as static HTML/CSS/JS/JSON files. This eliminates parser timeouts, speeds up deployment, and prevents large JSON files from breaking the build.
- **Action for you:** Once this branch is merged to `main`, GitHub Pages will serve static assets cleanly without Jekyll interference.

---

## Root Cause 2: `GITHUB_TOKEN` Workflow Trigger Restrictions (Automation Conflict)

### Why it happened since the last merge
GitHub has a built-in security restriction: **commits pushed by `GITHUB_TOKEN` inside a GitHub Action workflow do not trigger subsequent workflows.**

If the last commit on `main` was pushed automatically by an Actions workflow (such as `.github/workflows/update_spreadsheet.yml` using `git-auto-commit-action` with the default `GITHUB_TOKEN`), that commit is explicitly prevented by GitHub from triggering the built-in `pages-build-deployment` workflow. Consequently, the Pages site will not update automatically after that commit.

### How to diagnose
1. Go to your repository on GitHub and click the **Actions** tab.
2. Look in the left sidebar for **Pages build and deployment** (or `pages-build-deployment`).
3. Check if the workflow triggered after the last commit on `main`. If no run exists for the latest commit, it was suppressed by `GITHUB_TOKEN` restrictions.

### Remediation
1. **Immediate Fix:** In the **Actions** tab -> **Pages build and deployment**, click the three dots on the top right of the latest run and select **Re-run all jobs** (or push any commit from your user account).
2. **Permanent Fix for Automated Workflows:** If you want automated workflow commits to trigger Pages deployments, configure `update_spreadsheet.yml` to use a GitHub App token or a Personal Access Token (PAT) with `workflows` permission instead of the default `GITHUB_TOKEN`.

---

## Root Cause 3: Repository Pages Source Setting Drift (Settings Misconfiguration)

### Why it happened since the last merge
When `.github/workflows/` files are added or updated, GitHub UI prompts can sometimes toggle or default the repository's **Pages** build setting from **"Deploy from a branch"** to **"GitHub Actions"**.

Because `56eli/docsheet` does not contain an explicit custom Pages deployment workflow file (`.github/workflows/pages.yml`), setting the Pages source to "GitHub Actions" causes deployment to stop entirely.

### How to diagnose & fix
1. Go to your repository on GitHub and click **Settings**.
2. In the left sidebar under **Code and automation**, click **Pages**.
3. Under **Build and deployment -> Source**, check the dropdown:
   - Ensure it is set to **Deploy from a branch** (do **NOT** select "GitHub Actions").
4. Under **Branch**:
   - Ensure the first dropdown is set to **`main`**.
   - Ensure the folder dropdown is set to **`/docs`** (do **NOT** select `/ (root)`).
5. Click **Save**.

---

## Root Cause 4: Repository Visibility or Branch Protection / Concurrency Rules

### Why it happened since the last merge
- **Repository Visibility:** If repository visibility changed from **Public** to **Private** on a Free GitHub plan, GitHub Pages disables deployment automatically (GitHub Pages on Private repositories requires a GitHub Team or Enterprise plan).
- **Concurrency Locks:** If multiple commits were pushed in rapid succession, GitHub Pages cancels in-progress `pages-build-deployment` runs. If the last run was cancelled and didn't restart, the site will show an older build.

### How to diagnose & fix
1. Under **Settings -> General**, verify the repository visibility is **Public**.
2. In the **Actions** tab, check for any `pages-build-deployment` runs marked with a grey/cancelled icon or red/failed X. Click into the failed run to inspect the specific error message.

---

## Summary Table of Root Causes & Diagnostic Checklist

| Root Cause | Diagnostic Question | Resolution / Fix |
|---|---|---|
| **1. Jekyll Build Timeout** | Did `pages-build-deployment` fail with a Jekyll or build error in the Actions tab? | **Fixed in this branch:** `docs/.nojekyll` added to bypass Jekyll entirely. |
| **2. `GITHUB_TOKEN` Trigger Ban** | Was the latest commit on `main` pushed by a bot/workflow (`update_spreadsheet.yml`)? | Re-run the `pages-build-deployment` workflow manually in Actions tab. |
| **3. Pages Source Drift** | Is **Settings -> Pages -> Source** accidentally set to "GitHub Actions"? | Set Source to **Deploy from a branch**, Branch to **`main`**, Folder to **`/docs`**. |
| **4. Visibility / Concurrency** | Was the repository made Private, or was the deploy job cancelled? | Confirm repo is **Public** and check Actions logs for cancelled runs. |

---

## Optional: Migrating to an Explicit GitHub Actions Pages Deployment Workflow

If you prefer to deploy GitHub Pages via an explicit GitHub Actions workflow (allowing you to set **Source -> GitHub Actions** in Settings and gain full control over deployment logs), you can add the following file as `.github/workflows/deploy_pages.yml`:

```yaml
name: Deploy GitHub Pages
on:
  push:
    branches: [main]
    paths:
      - "docs/**"
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages-deploy-${{ github.ref }}
  cancel-in-progress: true

jobs:
  deploy:
    name: Deploy docs/ to GitHub Pages
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v5
      - name: Upload docs/ artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

Using this explicit workflow prevents Jekyll timeouts, avoids branch-deploy setting drift, and provides clear diagnostic logs directly in your Actions tab.
