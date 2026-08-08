# GitHub Web-Editor Workflow Guide — Drop-in Snippets

**Prepared:** 2026-08-08 · branch `arena/019fe11d-docsheet`

The Arena GitHub App **cannot push changes to `.github/workflows/*`** (GitHub
rejects the push — workflows need the `workflows` permission). Apply workflow
edits yourself in the GitHub web editor. Each item below is self-contained:
open the file, find the "Replace this" block, paste the "With this" block over
it, and commit directly to `main`.

Only **one** item is currently open. The Node 20→22 bump is already applied
(commit `406116f`); it is kept at the bottom for reference.

---

## Item 1 — Cover both Playwright specs in the JS-syntax check

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
and exit 0. To confirm the glob actually covers both specs, you can temporarily
introduce a typo in `tests/column-layout.spec.js` locally and run:

```bash
for spec in tests/*.spec.js; do node --check "$spec" || echo "FAILED: $spec"; done
```

It should print `FAILED: tests/column-layout.spec.js` — i.e. the loop checks
that file (revert the typo afterwards).

---

## Already applied (no action needed)

### Node 20 → 22 — ✅ applied as commit `406116f`

The CI workflow pins `node-version: "22"` in the **Set up Node** step. Node 20
reached EOL on 2026-04-30; Node 22 is active LTS. Nothing to do — if you want
to confirm, open `.github/workflows/ci.yml` and check the step reads:

```yaml
      - name: Set up Node
        uses: actions/setup-node@v4
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
- The data fixes from this session (the stale 50491 Veritas decision row and
  the doc cleanups) are already committed on `arena/019fe11d-docsheet`; push
  and open a PR for that branch separately to ship them — they do **not**
  require any workflow edit.
