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

---

## 2026-08-08 — two workflow edits the App cannot push

The same `workflows`-permission restriction blocks two further edits prepared on
branch `arena/019fe01c-docsheet` (commit `3f8e6e1`). They are validated locally
(113 tests, all six `--check` modes green) but must be applied by the owner in the
GitHub web editor.

### 1. `ci.yml` — gate the inventory-mirror sync and fix the coverage label

Open
[`.github/workflows/ci.yml`](https://github.com/56eli/docsheet/edit/main/.github/workflows/ci.yml).
Immediately after:

```yaml
      - name: Verify series-taxonomy mapping matches its inputs
        run: python map_series_taxonomy.py --check
```

add:

```yaml
      - name: Verify Veritas inventory mirrors match the master
        run: python sync_inventory_mirrors.py --check
```

Then rename the coverage step from `Enforce the coverage floor (80%)` to
`Enforce the coverage floor (85%)` (`.coveragerc` has `fail_under = 85` since
2026-08-07; the label was stale). The header comment should also read "the six
generator --check modes (raw payload, master, Pages, reconciliation,
series-taxonomy, and inventory mirrors)" instead of "three".

### 2. `update_spreadsheet.yml` — drop the retired `docs/meta.json`

Open
[`.github/workflows/update_spreadsheet.yml`](https://github.com/56eli/docsheet/edit/main/.github/workflows/update_spreadsheet.yml)
and change the auto-commit `file_pattern` from:

```yaml
          file_pattern: docs/data.json docs/meta.json
```

to:

```yaml
          file_pattern: docs/data.json
```

`docs/meta.json` was retired on 2026-08-07 (never consumed); the file no longer
exists, so the pattern references a path that is never written.

---

## 2026-08-08 — Drop-in replacement guide (GitHub web editor)

The Arena GitHub App cannot push changes to `.github/workflows/`. Two workflow
edits are prepared on branch `arena/019fe01c-docsheet` (commit `3f8e6e1` and
follow-ups) and need to be applied by you, the repository owner. Both are
**text replacements** — you can paste them in the GitHub web editor without
touching anything else. The branch already contains the code/data/docs these
workflows validate; once applied, CI will exercise the new mirror check.

### File 1 of 2: `.github/workflows/ci.yml`

1. Open
   <https://github.com/56eli/docsheet/edit/main/.github/workflows/ci.yml>
   (or navigate to the file on `main` and click the pencil **Edit** icon).
2. Make these **three** small replacements:

**(a) Header comment** — find these three lines near the top:

```yaml
# Runs the deterministic checks that already exist in the repository:
#   - Python syntax compilation
#   - the three generator --check modes (master, Pages, reconciliation)
```

Replace them with:

```yaml
# Runs the deterministic checks that already exist in the repository:
#   - Python syntax compilation
#   - the six generator --check modes (raw payload, master, Pages,
#     reconciliation, series-taxonomy, and inventory mirrors)
```

**(b) Add the mirror check step** — find this block:

```yaml
      - name: Verify series-taxonomy mapping matches its inputs
        run: python map_series_taxonomy.py --check
      - name: Run deterministic pipeline test suite
        run: python -m unittest discover tests
```

Replace it with:

```yaml
      - name: Verify series-taxonomy mapping matches its inputs
        run: python map_series_taxonomy.py --check
      - name: Verify Veritas inventory mirrors match the master
        run: python sync_inventory_mirrors.py --check
      - name: Run deterministic pipeline test suite
        run: python -m unittest discover tests
```

**(c) Coverage-floor step label** — find:

```yaml
      - name: Enforce the coverage floor (80%)
```

Replace with:

```yaml
      - name: Enforce the coverage floor (85%)
```

(Only the label changes; `coverage report` still reads `fail_under = 85`
from `.coveragerc`, so enforcement was already correct — the step name was
the stale part.)

3. Scroll to **Commit changes**, leave "Commit directly to `main`" selected,
   and click **Commit changes**.

---

### File 2 of 2: `.github/workflows/update_spreadsheet.yml`

1. Open
   <https://github.com/56eli/docsheet/edit/main/.github/workflows/update_spreadsheet.yml>
2. Find the `file_pattern` line near the bottom:

```yaml
          file_pattern: docs/data.json docs/meta.json
```

Replace it with:

```yaml
          file_pattern: docs/data.json
```

`docs/meta.json` was retired on 2026-08-07 (the file no longer exists); the
auto-commit action warned but did not fail. Dropping it keeps the pattern
honest.

3. Commit directly to `main`.

---

### Verify

After both commits land on `main`, open the **Actions** tab and watch the next
**CI** run (the push itself will trigger it). It should pass with:

- six `--check` steps (including the new *Verify Veritas inventory mirrors
  match the master* step),
- the deterministic test suite reporting **113 tests**,
- coverage at **91%** against the 85% floor,
- the Playwright browser smoke tests.

If any step fails, the error message will name the script; the corresponding
fix is already on the `arena/019fe01c-docsheet` branch.
