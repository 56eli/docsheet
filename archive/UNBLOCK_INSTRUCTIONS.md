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
