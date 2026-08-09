# Agent Handoff

Last updated: 2026-08-09

## Current repo state

DocSheet is a GitHub Pages live spreadsheet plus a curated David Hawkins
research catalogue. The declared-current audit is
`docs/audits/2026-08-09-deployment-forensics-full-audit.md`.

This handoff is for branch `arena/019fe7b6-docsheet`, based on `main` commit
`ea4e30d`.

## Deployment-forensics result

The recent red Actions were **CI failures, not Pages deployment failures**.
Commit `255d937` removed stats/overview controls from `docs/index.html` while
`tests/ux-enhancements.spec.js` still waited for `#show-stats-toggle`.

- 11 CI runs failed from PR #48 through the latest `main` push (plus one cancelled superseded run).
- Every failure had the same single browser-test cause; 24 other specs passed.
- Every corresponding GitHub Pages deployment succeeded.
- Latest Pages build/deployment API reports `ea4e30d` built and deployed.
- PR #46 / `a981641` (REVISION1 rows) had green CI and green Pages.

The row corrections are in the curated `docs/master.json` consumed by
**Everything**. They intentionally are not copied into raw `docs/data.json`
consumed by **Original Spreadsheet**. Several corrected promoted UUIDs do not
exist in the raw CSV.

## Fixes on this branch

- Replaced the stale stats-chip E2E path with navigation through the surviving
  `#view-jump` menu.
- Added an offline regression test that reads the actual Pages payload and
  locks REVISION1 UUIDs 312, 315, 356, 357, and 358.
- Offline suite: **140 tests**, all passing; total coverage **90%**.
- Browser suite: **25 specs** (1 blank-row, 4 column-layout, 5 CSV/export,
  6 presentation, 9 UX), all green in PR #53 run `31328879360`.
- Corrected current docs that falsely claimed 26 browser specs and every
  pipeline module ≥88%; individual coverage is currently 78–100%.
- Added full deployment forensics and updated the scoreboard.

## Verification

Passed locally:

- `python process_data.py --check`
- `python build_research_master.py --check`
- `python build_catalogue_pages.py --check`
- `python reconcile_research_master.py --check`
- `python map_series_taxonomy.py --check`
- `python sync_inventory_mirrors.py --check`
- `python -m py_compile *.py pipeline/*.py tests/*.py`
- `python -m unittest discover tests` — 140 passed
- `coverage run -m unittest discover tests && coverage report` — 90% total
- `ruff check .`
- `node --check` for app/config/all specs
- `npm ci`; `npm audit --audit-level=moderate` — 0 vulnerabilities
- `git diff --check`; `git fsck`

Environment limitations:

- Chromium download fails locally with CDN TLS resets; PR #53 CI supplied the
  browser verification (all 25 passed in run `31328879360`).
- Direct GitHub Pages fetch fails with TLS EOF from this sandbox; Pages API,
  deployment status, and GitHub Contents API hashes were used instead.
- Classic branch-protection API is forbidden to this integration; repository
  rulesets are empty, and observed merges prove checks were not required.

## Current data state

- Raw/ledger rows: 374; ledger items 299; exclusions 75.
- Curated master / Everything: 362.
- Owned values: 295 true / 25 false / 42 unstated.
- Master types: 306 lecture / 40 book / 8 discussion / 7 highlight / 1 other.
- URLs: 461 populated, all HTTPS/parseable; zero orphan primary Veritas URLs.
- Zero duplicate UUIDs, relationship IDs, Veritas IDs, or filenames.
- Zero blank master UUID/title/type/work ID/proposed filename/year source.
- 19 intentional blank years; 16 Office `198X`; zero malformed years/months.
- Display order exactly matches the approved 362-row overlay.

## Top priorities

1. `github_pages_presentation` — priority 15, owner score 5/10.
2. `ux_usability` — priority 12, owner score 5/10.
3. `maintainability` — priority 8, owner score 6/10.
4. `code_hygiene` — priority 4: remove dead overview/stats JS and CSS.
5. `ci_cd` — priority 4: require CI and gate Pages; owner/workflow settings.
6. `content_quality`, `repo_organization`, and `task_hygiene` — priority 3.
7. Issue #18 — needs owner Drive export/access and an “owned” definition.

## Owner decisions needed

Exact options are documented in `.scoreboard/manual-workflow-edits.md`:

1. Require the CI check before merging to `main`.
2. Replace legacy branch Pages deployment with a CI-gated Pages workflow.
3. Add a visible build/data revision and a post-deploy row assertion.
4. Rename/describe views to make curated versus raw data explicit.
5. Approve a behavior-preserving dead frontend cleanup.

Do not edit `.github/workflows/*` without explicit owner instruction.

## Scoreboard

- Overall effective score: **7.6**; `repo_ready` = **fail** (< 8).
- Required aspect floors still pass, but CI/CD and agent readiness are exactly
  at their thresholds and deployment gating remains an active risk.
- User scores are preserved unchanged: presentation 5, UX 5, content 7,
  maintainability 6.

## Files intentionally not changed

- `.github/workflows/*` — workflow/settings proposals only; owner approval is
  required by repository policy.
- Curated/raw data inputs and generated JSON — audit verified them current and
  did not change data.
