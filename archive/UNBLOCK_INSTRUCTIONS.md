# Repository-owner action — workflow update required

**Prepared:** 2026-08-03

GitHub Actions CI is already live and passing on `main`. The current Arena GitHub
App can read and run workflows but **cannot update** `.github/workflows/ci.yml`:
GitHub rejects the push because the app lacks the `workflows` permission.

## Add raw spreadsheet drift detection

In GitHub's web editor, open
[`main/.github/workflows/ci.yml`](https://github.com/56eli/docsheet/edit/main/.github/workflows/ci.yml).
Immediately after:

```yaml
      - name: Compile all Python scripts
        run: python -m py_compile *.py
```

add:

```yaml
      - name: Verify raw spreadsheet Pages payload matches its source
        run: python process_data.py --check
```

Commit directly to `main` with the message:

```
ci: verify raw spreadsheet Pages payload
```

This check is implemented and validated on the Arena branch, but it cannot be
included in that branch's pushed commit until the workflow permission is granted.
It compares the authoritative raw CSV to `docs/data.json` and validates stable
`docs/meta.json` fields while intentionally ignoring the build timestamp.

After committing, run **CI** from the Actions tab (or let the push trigger it)
and confirm the new step passes.

## Also add the series-taxonomy check (2026-08-03 addition)

`map_series_taxonomy.py` landed with the same `workflows` permission
limitation. In the same web-editor commit (or a follow-up), after the series
of `python … --check` steps, add:

```yaml
      - name: Verify series-taxonomy mapping matches its inputs
        run: python map_series_taxonomy.py --check
```

Verified locally on the Arena branch before push.

## Add the pipeline test suite + coverage gate (2026-08-03 addition)

`tests/test_pipeline.py` and the 80% coverage floor landed with the same
`workflows` permission limitation. In the same web-editor commit (or a
follow-up), immediately after the `map_series_taxonomy.py --check` step, add:

```yaml
      - name: Run deterministic pipeline test suite
        run: python -m unittest discover tests
      - name: Enforce the coverage floor (80%)
        run: |
          pip install -r requirements-dev.txt
          coverage run -m unittest discover tests
          coverage report
```

The suite needs no browser and no network; `requirements.txt` (pandas) is
already installed by the existing CI step, `requirements-dev.txt` adds
`coverage`. Passing locally on the Arena branch at 92% total, every pipeline
module ≥ 88%.

## Veritas refresh artifact

The latest **Map Veritas Catalogue** run fetched the live API successfully and
failed at its deliberate candidate-diff gate. Its artifact download endpoint
returns a TLS EOF in the Arena sandbox, so review the uploaded
`veritas-inventory-review-30813523859` artifact in GitHub before accepting any
inventory change. Do not replace `data/veritas_official_products.csv` without
that review.

## Bump the CI Node runtime 20 → 22 (2026-08-08 addition — ✅ APPLIED)

> **Applied by the owner as commit `406116f` on `main` (2026-08-08);
> `origin/main` ci.yml now pins `node-version: "22"`. The instructions below
> are kept for reference.**

Node 20 reached EOL on 2026-04-30; Node 22 is the active LTS line
(supported until 2027-04). In the web editor, open
[`main/.github/workflows/ci.yml`](https://github.com/56eli/docsheet/edit/main/.github/workflows/ci.yml)
and change the **Set up Node** step:

```yaml
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
```

i.e. replace `node-version: "20"` with `node-version: "22"` (one line; keep
`actions/setup-node@v4` and `cache: npm`).

Commit directly to `main` with the message:

```
ci: bump Node 20 -> 22 (Node 20 EOL 2026-04)
```

The repository code is already Node-22-compatible: local sandbox runs Node 22,
`node --check` passes on `docs/app.js`, `playwright.config.js` and both specs,
and the Playwright version (`@playwright/test` 1.62.1) supports Node 22.
After committing, re-run **CI** from the Actions tab and confirm the
"Set up Node" + "Run browser smoke tests" steps pass.

## Cover both Playwright specs in the JS-syntax step (2026-08-08 addition)

The "Check JavaScript syntax" step currently runs `node --check` against only
`tests/csv-export.spec.js`; `tests/column-layout.spec.js` is not syntax-checked
until the (Chromium-only, slower) browser-smoke step. In the web editor, open
[`main/.github/workflows/ci.yml`](https://github.com/56eli/docsheet/edit/main/.github/workflows/ci.yml)
and replace the three explicit `node --check` lines with a glob so every spec
is covered:

```yaml
      - name: Check JavaScript syntax
        run: |
          node --check docs/app.js
          node --check playwright.config.js
          for spec in tests/*.spec.js; do node --check "$spec"; done
```

Commit directly to `main` with the message:

```
ci: syntax-check every Playwright spec
```

This mirrors the local verification command already documented in
`NEXT_AGENT_HANDOFF.md` §2; a syntax error in `column-layout.spec.js` would
then fail fast instead of only at the browser step.
