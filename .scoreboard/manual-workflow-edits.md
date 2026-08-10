# Manual Workflow Edits

GitHub Actions workflow/settings edits must be owner-applied or explicitly
approved. The end-user row-delivery postmortem found that legacy Pages deploys
are independent of CI and the current branch rules permit merge-before-check.

## Policy

Agents must not directly edit `.github/workflows/*` unless explicitly instructed
by the owner. Record exact reviewed changes here and mark affected scoreboard
aspects `blocked_manual_workflow_edit` until the owner applies them.

## Needed Manual Edits

### P0 — Require CI before merge

**Why:** PRs #48–#52 merged before checks completed; five red `main` commits
were published. Artifact deployment must not outrun validation.

In **Settings → Rules → Rulesets** (or classic **Settings → Branches**) for
`main`:

1. Require a pull request before merging.
2. Require status checks to pass before merging.
3. Require `Validate data pipeline and site` from workflow `CI`.
4. Require the branch to be up to date before merge.
5. Disable routine bot/agent bypass.
6. Keep the rule active after any job split by requiring a stable aggregate job.

Repository rulesets were empty during the incident. The classic protection API
was inaccessible to the GitHub integration, but observed merge timing proves
that the check was not enforced.

### P0 — Gate Pages on successful `main` CI and verify the deployed browser payload

**Why:** Pages currently uses legacy branch deployment (`main:/docs`) and starts
independently of CI. It verifies artifact upload, not the version consumed by a
browser. The frontend now publishes `docs/build-manifest.json`, content-versioned
`app.js` / `style.css` URLs, and a visible footer build ID; deployment must assert
that contract.

After owner review, add `.github/workflows/deploy_pages.yml`:

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
        uses: actions/checkout@v7
        with:
          ref: ${{ github.event.workflow_run.head_sha }}

      - name: Configure Pages
        uses: actions/configure-pages@v6

      - name: Upload validated docs directory
        uses: actions/upload-pages-artifact@v5
        with:
          path: docs

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v5

      - name: Verify deployed revision, assets, and curated payload
        env:
          PAGE_URL: ${{ steps.deployment.outputs.page_url }}
        shell: bash
        run: |
          set -euo pipefail
          expected_revision=$(jq -r .revision docs/build-manifest.json)
          for attempt in {1..12}; do
            if curl --fail --silent --show-error --location \
              "${PAGE_URL}build-manifest.json?attempt=${attempt}" \
              --output /tmp/live-manifest.json; then
              live_revision=$(jq -r .revision /tmp/live-manifest.json)
              if [ "$live_revision" = "$expected_revision" ]; then
                break
              fi
            fi
            if [ "$attempt" -eq 12 ]; then
              echo "Timed out waiting for deployed revision $expected_revision" >&2
              exit 1
            fi
            sleep 10
          done

          curl --fail --silent --show-error --location \
            "${PAGE_URL}master.json?revision=${expected_revision}" \
            --output /tmp/live-master.json
          expected_count=$(jq -r .master_items docs/catalogue-meta.json)
          actual_count=$(jq length /tmp/live-master.json)
          test "$actual_count" -eq "$expected_count" \
            || { echo "Row count mismatch: expected $expected_count, got $actual_count" >&2; exit 1; }

          for asset in app.js style.css; do
            expected=$(jq -r --arg asset "$asset" '.assets[$asset]' docs/build-manifest.json)
            curl --fail --silent --show-error --location \
              "${PAGE_URL}${asset}?sha=${expected}" --output "/tmp/${asset}"
            actual=$(sha256sum "/tmp/${asset}" | cut -d' ' -f1)
            test "$actual" = "$expected"
          done
```

Cutover procedure:

1. Confirm current Marketplace releases before applying. Audited 2026-08-09:
   `checkout@v7`, `configure-pages@v6`, `upload-pages-artifact@v5`, and
   `deploy-pages@v5` exist; pin full SHAs if the owner wants maximum supply-chain
   control.
2. Merge the reviewed workflow while legacy Pages remains enabled.
3. In **Settings → Pages**, change Source from **Deploy from a branch** to
   **GitHub Actions**.
4. Trigger one validated `main` CI run and confirm the environment SHA equals
   `${{ github.event.workflow_run.head_sha }}`.
5. Confirm the footer build ID and manifest hashes match the deployed files.
6. Do not leave both legacy branch and custom deployment paths active.

### P1 — Split monolithic CI, keep one required aggregate check

Current CI runs data/Python and browser validation serially. A late browser
failure makes the full run red after all data work has passed and obscures the
failure category.

Split into:

- `data-and-python`: recursive compile, all six `--check` modes, 149 offline
  tests, and coverage;
- `browser`: JS/spec syntax, `npm ci`, Chromium, and 25 Playwright specs;
- `required`: `if: always()` aggregate that fails unless both jobs pass.

The browser job must retain the computed-style row acceptance in
`tests/presentation-ux.spec.js`. Add a successful-run screenshot artifact for
fixed desktop light/dark viewports once the owner approves reference images.
Do not use a first-row/class-only check as visual acceptance.

### P1 — Add owner visual acceptance to the release procedure

No workflow can infer subjective acceptance. Before closing the row incident:

1. publish the versioned build;
2. record the visible build ID;
3. capture desktop light, desktop dark, and mobile screenshots;
4. verify at least lecture, discussion, and office block transitions after
   filtering and sorting;
5. obtain an explicit owner accept/reject response for that build ID.

## Workflows otherwise current

- `.github/workflows/update_spreadsheet.yml` — all three recorded runs succeeded;
  regenerates only `docs/data.json` when the raw source changes.
- `.github/workflows/map_veritas_catalogue.yml` — intentionally review-only; a
  candidate diff exits non-zero to demand review and is not a deployment error.
