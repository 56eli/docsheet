# Manual Workflow Edits

GitHub Actions workflow edits may need to be performed manually in the GitHub
web editor.

## Policy

Agents must not edit `.github/workflows/*` unless explicitly instructed by the
user. If workflow changes are needed, document them here and mark the affected
scoreboard aspects `blocked_manual_workflow_edit`.

## Needed Manual Edits

### P1 — Require CI before merge (recommended first)

**Why:** PRs #48–#52 were merged before their checks completed or despite a
known failing head; five red `main` commits then deployed to Pages. The stale
test did not block the row corrections, but the same design could deploy a real
data defect.

In **Settings → Branches** (or **Settings → Rules → Rulesets**) for `main`:

1. Require a pull request before merging.
2. Require status checks to pass before merging.
3. Require the current check `Validate data pipeline and site` (workflow `CI`).
4. Require branches to be up to date before merging.
5. Do not permit routine bypass for agents/bots.

If the CI job is later split, replace the required check with a stable aggregate
check (for example, `CI / Required checks`) so settings do not churn.

### P1 — Gate GitHub Pages on successful `main` CI

**Why:** Pages currently uses legacy branch deployment (`main:/docs`) and starts
independently of CI. Every recent red CI commit still deployed successfully.

Preferred migration after the owner reviews it:

1. Add `.github/workflows/deploy_pages.yml` through a reviewed PR:

   ```yaml
   name: Deploy Pages

   on:
     workflow_run:
       workflows: [CI]
       types: [completed]
       branches: [main]

   permissions:
     contents: read
     pages: write
     id-token: write

   concurrency:
     group: pages
     cancel-in-progress: true

   jobs:
     deploy:
       if: ${{ github.event.workflow_run.conclusion == 'success' }}
       runs-on: ubuntu-latest
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - name: Checkout the validated commit
           uses: actions/checkout@v4
           with:
             ref: ${{ github.event.workflow_run.head_sha }}
         - name: Configure Pages
           uses: actions/configure-pages@v5
         - name: Upload validated docs directory
           uses: actions/upload-pages-artifact@v3
           with:
             path: docs
         - name: Deploy to GitHub Pages
           id: deployment
           uses: actions/deploy-pages@v4
   ```

2. Confirm the action majors against the GitHub Marketplace at implementation
   time; current `checkout@v4` and other JavaScript actions emit Node 20
   deprecation warnings on the 2026 runner.
3. In **Settings → Pages**, change Source from **Deploy from a branch** to
   **GitHub Actions** only after the new workflow has passed on a test PR/main
   run.
4. Verify the deployed environment SHA equals
   `${{ github.event.workflow_run.head_sha }}`.
5. Add a post-deploy smoke step with retries that fetches the deployed
   `master.json`, asserts 362 rows, and checks a generated revision manifest.

Do not leave both legacy branch deployment and custom deployment enabled during
the final cutover.

### P2 — Split monolithic CI and update action runtimes deliberately

Current `ci.yml` runs data/Python and browser work serially in one job. Split it
into:

- `data-and-python`: compile recursively, six `--check` modes, 140 tests,
  coverage;
- `browser`: JS syntax, `npm ci`, Chromium, 25 Playwright specs;
- `required`: a tiny `if: always()` aggregate job that fails unless both pass.

Use only action major versions confirmed to exist. A previous blind “latest”
edit set several actions to `@v7` and added `-c requirements-ci.txt` before the
constraint file existed, causing three dependency-stage failures. Preserve the
raw updater/CI path filters and existing least-privilege permissions.

## Workflows otherwise current

- `.github/workflows/update_spreadsheet.yml` — all three recorded runs succeeded;
  regenerates only `docs/data.json` when the raw CSV changes.
- `.github/workflows/map_veritas_catalogue.yml` — intentionally review-only; a
  candidate diff exits non-zero to demand review and is not a deployment error.
