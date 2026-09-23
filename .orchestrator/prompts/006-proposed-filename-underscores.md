Adopt underscore convention for proposed_filename columns

docsheet agent. Fetch your work order from the orchestrator branch:

```
git fetch --depth 1 origin +arena/01a0cb00-docsheet:refs/remotes/origin/_orch && git show refs/remotes/origin/_orch:.orchestrator/prompts/006-proposed-filename-underscores.md > /tmp/task.md
```

Work from the task text in `/tmp/task.md` (do not rely on `/tmp` long-term — copy it into your working notes if needed). Expected PR title = line 1 of this file, verbatim. Done = PR open against `main` from your provisioned session branch.

## 1. Owner directive (verbatim, 2026-09-23)

> For the "Proposed File Name" column i need spaces to become underscores according to the following standard "2002-03_The_Levels_of_Consciousness_Subjective_&_Social_Consequences_[1-3].mp4"

Dash ruling (owner answer to the clarifying question, 2026-09-23): **collapse** — every ` - ` segment separator becomes one `_`, then every remaining space becomes `_`. Example confirmed by owner: `2004-06 - OTR - Become That Which You Are [1-3].mp4` → `2004-06_OTR_Become_That_Which_You_Are_[1-3].mp4`. Not the literal space-only swap (that would leave `_-_` at the date boundary, contradicting the owner's standard).

This directive is an **explicit, scoped owner instruction**: it authorizes writes to `data/filename_proposal_YYYYMM.csv` (the two filename columns only) and to that sheet's generator outputs. Every other research byte-freeze surface stays frozen (§7).

## 2. Current state (live `main`, verify before editing)

`data/filename_proposal_YYYYMM.csv` is the source of truth — there is no Python generator for it; the pipeline only consumes it:

- 363 data rows + header; CRLF line endings; no BOM; QUOTE_MINIMAL quoting (20 filename values contain commas and are quoted).
- Two columns transform: `proposed_filename` (on-disk, `[1-3]`) and `proposed_filename_display` (display, `[1/3]`). All other columns (`uuid, work_id, item_type, series, year, month, format, title, clean_title, part_index, part_total`) must parse byte-identical before vs after.
- Variants present: 237 rows start `YYYY-MM - `; 126 rows have no month prefix (e.g. `Volume I Power vs. Force…`, year-only `2003 - OTR - …`); 112 rows contain internal ` - ` beyond the date prefix; extensions `.mp4` 272 / `.mp3` 32 / `.pdf` 32 / `.m4b` 27; 15 values contain `'`; 13 contain `&`; **0 values contain `_` today** (the transform is safe to reason about); 0 double spaces.

Live sample (row uuid 1): `2002-01 - Causality The Ego's Foundation [1-3].mp4` → target `2002-01_Causality_The_Ego's_Foundation_[1-3].mp4` (display keeps `[1/3]`).

Consumers (verify with grep; quote-by-copy if you cite them):

- `pipeline/enrichments.py` — `apply_filename_proposal()` copies `proposed_filename` onto master items after `validate_filename_proposal_groups()`.
- `pipeline/validators.py` — `validate_filename_proposal_groups()` enforces non-empty + **global uniqueness** across both columns + part-group coherence. It has NO format-pattern check → no validator code change expected; the uniqueness gate is fail-closed and must stay green.
- `build_research_master.py:400` — `apply_filename_proposal(items)`.
- `build_catalogue_pages.py:668-679` — maps `proposed_filename_display` into Everything rows / `docs/filename-proposal.json`.
- `crosscheck_final_registry.py` — `proposed_stem()` is a T1x match key (see §4 step 1).

## 3. Deliverables

1. Transformed `data/filename_proposal_YYYYMM.csv` (both filename columns; rule = `.replace(" - ", "_").replace(" ", "_")` applied to each value; every other field untouched; CRLF + quoting preserved).
2. All generator outputs regenerated through the repo's own build commands (expect at least `docs/master.json`, `docs/filename-proposal.json`; discover the rest via `git status` after builds — e.g. `data/research_master_draft.csv` only if it carries `proposed_filename`). Generated artifacts are never hand-edited: inputs → generators → `--check` gates green.
3. Crosscheck integration green (§4 step 1–2): `python crosscheck_final_registry.py --check` exit 0 after the transform, with bucket counts unchanged (A=234, B=11, C=14, D=15, E=41; A+B+C=259).
4. Tests updated to the new convention (§5 known touchpoints), full suite green.
5. Pattern prose refreshed: `README.md:191` currently reads (copy-quoted from live main):

   > Since 2026-08-04 the master also exposes `proposed_filename` between `title` and `item_type` using pattern `YYYY-MM - Name [1/3].mp4` (safe `[1-3]` on-disk, display `[1/3]`)

   Replace the pattern fragment with the underscore standard, e.g. pattern `YYYY-MM_Name_[1/3].mp4` (safe `[1-3]`, display `[1/3]`), and adjust the sentence so it stays truthful (separator is `_`, spaces are `_`, dashes collapsed). Do NOT edit `docs/audits/*` or `archive/*` (historical, never rewritten).
6. House-rule counts: if the test count changes, update `README.md` (lines 66, 71) and `INSTRUCTIONS.md` (lines 188, 196) — append `→ <new>` to the drift chain in INSTRUCTIONS (live chain ends `… 158 → 166 → 213`), keep every count consistent across both files; if the count stays 213, leave the lines and say so in the PR body.
7. Delivery contract (architectural invariant): payload changes to `docs/master.json` / `docs/filename-proposal.json` require refreshed version IDs in `docs/index.html` (`?v=` query hashes on `style.css`/`app.js`, footer `app-…/css-…` revision) and `docs/build-manifest.json` hashes in the same PR. The delivery-contract tests enforce this — run the suite and follow the failure messages.

## 4. Required sequence (crosscheck safety)

`proposed_stem()` currently strips the date prefix with `^\d{4}-\d{2}\s*-\s*` and the part suffix with `\s*\[\d+-\d+\]$`; after the transform the date is followed by `_` and the bracket is preceded by `_`, so the old regexes would miss and T1x keys would shift. Therefore:

1. **Before touching the CSV**: harden `proposed_stem()` (and only where needed the fold into `normalize`) so it treats `_` like whitespace at those boundaries — date-prefix strip accepts `_` separators, part-suffix strip accepts a preceding `_`, and `_` folds to space before key comparison. Prove no-op: `python crosscheck_final_registry.py --check` must exit 0 on unmodified inputs (old values contain zero underscores → outputs byte-identical). If you cannot get exit 0 without changing committed outputs at this step, STOP and disclose in the PR body instead of rewriting 005's outputs silently.
2. Baseline record: capture `--check` output and the bucket tallies from `review/final_registry_crosscheck.csv` before the transform.
3. Apply the CSV transform with a one-shot throwaway script (not committed): field-aware via `csv` module, `lineterminator="\r\n"`, `QUOTE_MINIMAL`. Assert after: (a) zero spaces and zero ` - ` remain in the two filename columns; (b) every untouched column parses identical to the original for all 363 rows; (c) row count 363; (d) reverse-spot-check 5 rows including uuid 1, 221 (`2003 - OTR - Progressive Levels…`), 202 (no date prefix), and one comma-bearing filename row; (e) `validate_filename_proposal_groups` uniqueness still passes (it runs inside the next build).
4. Regenerate all outputs via the repo's documented build commands; run their `--check` modes; commit only files whose bytes legitimately change.
5. Re-run `python crosscheck_final_registry.py --check` → must exit 0 with identical bucket counts. Any bucket movement = STOP, investigate normalization, disclose; never silently regenerate the merged 005 report/CSV to hide a key-shift (only if step 1's no-op proof already passed and a real content delta remains, regenerate via the script and disclose the exact deltas + reconciliation A+B+C=259 in the PR body).
6. Full suite + coverage as usual; then prose/count/delivery-contract fixes; final `--check` sweep of every gate the repo defines.

## 5. Known test touchpoints (copy-quoted from live main; re-grep yourself before editing)

- `tests/test_pipeline.py:2028` — `            "2003 - OTR - Devotion to Truth Talk.mp4",` (uuid 311 exact-value assert → becomes `2003_OTR_Devotion_to_Truth_Talk.mp4`)
- `tests/test_pipeline.py:2032` — `            "2003 - OTR - Mind, Heart and Service The Pathway of Devotional Non-Duality.mp4",` (uuid 310 → `2003_OTR_Mind,_Heart_and_Service_The_Pathway_of_Devotional_Non-Duality.mp4`)
- `tests/test_pipeline.py:2043-2044` — `"1995 - Power vs. Force (Audible).m4b"` / `"1995 - Power vs. Force (Veritas).m4b"` → `1995_Power_vs._Force_(Audible).m4b` / `(Veritas)`
- `tests/test_pipeline.py:2069-2070` — uniqueness-seed `text.replace(...)` literals use the two old OTR strings above; update BOTH the source and seeded replacement consistently (the test must still seed a duplicate AFTER the transform, i.e. replace new-form with new-form).
- `tests/test_final_registry_crosscheck.py:95` — `        stem = cfr.proposed_stem("2002-01 - Causality The Ego's Foundation [1-3].mp4")` — old-format fixture: KEEP it (normalization must stay backward-compatible per §4.1) and ADD an underscored twin assert so both forms are pinned; if you add a test, apply §3.6 count updates.
- JS specs (`tests/column-layout.spec.js`, `csv-export.spec.js`, `ux-enhancements.spec.js`) assert column position/visibility, not values — expect no change; run them anyway.

## 6. Scope boundaries (frozen — do not touch)

- Raw lane: `hawkins archive clone - Sheet1.csv`, `docs/data.json` (workflow-owned), raw-spreadsheet pipeline behavior.
- All other `data/*.csv` inputs (candidates, promotions, families, overrides, streaming URLs, `final_registry.csv`, …), schemas, research docs/outputs, `docs/audits/*`, `archive/*`.
- `.github/workflows/*` (owner-only), `orchestrator/**`, `.orchestrator/**` (orchestrator branch), `docs/PROJECT_STATE.md` §2 duty lines, `.scoreboard/**` (dismantled — must not reappear).
- No `owned`-flag edits, no master-row content edits, no schema changes. The ONLY hand-authorized input edit is the two filename columns of `data/filename_proposal_YYYYMM.csv`.

## 7. PR mechanics

- Branch: your provisioned session branch (`arena/…-docsheet`), pushed only to that branch. Never push `main`; never touch the orchestrator branch; never open PRs other than this one; never merge.
- Title: line 1 of this file, verbatim.
- Body must include: transform rule + owner quote; row/column invariants proven (363 rows, untouched columns identical); every regenerated file listed; `--check` results for each gate (paste command + exit codes); crosscheck bucket table before/after (must be identical: 234/11/14, D=15, E=41, Σ=259); test count before/after (213 → N) and which count lines you touched; delivery-contract refresh confirmation; Session Irregularities section (any sandbox restore, token expiry, platform rewind, blocked push — report facts, do not route around auth or git failures).
- Local limitation you may hit: sandbox lacks `pandas` → 8 pipeline tests fail locally; CI is authoritative (known environmental gap — note it, don't "fix" it).
- Done = PR open + CI green. The orchestrator reviews (three-stage) and advises MERGE/REVISE; merging is the operator's call, never yours.
