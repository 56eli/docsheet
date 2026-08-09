# Agent Handoff

Last updated: 2026-08-09

## Current repo state

DocSheet: a GitHub Pages live spreadsheet + curated research catalogue for
David Hawkins material. The 2026-08-09 expert full-stack audit
(`FULL_STACK_AUDIT_2026-08-09_ARENA_EXPERT.md`, root) plus
`FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` and its extension
`FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md` are the declared-current audits.
The scoreboard was created as part of the persistent-memory protocol:
`SCOREBOARD.md`, `.scoreboard/scoreboard.yml` (canonical), `.scoreboard/rubric.md`,
`.scoreboard/history.md`, `.scoreboard/agent-handoff.md`,
`.scoreboard/manual-workflow-edits.md`, `AGENTS.md`,
`docs/audits/2026-08-09-baseline.md`, `.github/pull_request_template.md`.

## 2026-08-09 fresh audit + fixes + repo-organization pass (this branch)

- **Fresh full-stack audit** (`docs/audits/2026-08-09-arena-full-audit.md`,
  uncommitted on `arena/019fe6c1-docsheet`): all six `--check` modes, 126/126
  tests, 91% coverage, ~30 independent probes — catalogue data clean, every
  documented count reproduced. New findings (all low):
  - F-01 `market='Spanish'` on two international-queue Audible rows → fixed
    to `United States` (`data/international_discovery_queue.csv` +
    regenerated `docs/international-products.json`).
  - F-02 `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md` stale "365" → 362.
  - F-03 `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` "8 view columns" → 7.
  - F-04 `.scoreboard/history.md` + `.scoreboard/manual-workflow-edits.md` +
    `docs/audits/2026-08-09-baseline.md` "19 browser specs" → 26.
- **Repo-organization pass (owner-approved):** archived 4 root docs with
  banners — `FULL_STACK_AUDIT_2026-08-08_ARENA.md`,
  `FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`, `EXTERNAL_AUDIT.md`,
  `PRESENTATION_UX_PROPOSAL_2026-08-09.md` (implemented). README
  "Documentation layout", INSTRUCTIONS (was still pointing at the 08-08
  audit as current!), NEXT_AGENT_HANDOFF, archive/README.md, and the
  declared-current audits updated accordingly. Root now has 18 .md files.
- **Presentation/UX feedback:** owner deferred (no concrete feedback yet);
  priorities 15/12 remain open.
- Nothing committed yet on this branch — review `git status`/`git diff`.

## Top priorities for next agent

1. `github_pages_presentation` (priority 15, `user_unhappy`): owner scored
   5/10 while AI is 9 — **ask the owner what specifically falls short**
   (layout, branding, content presentation, speed?) before making changes.
2. `ux_usability` (priority 12, `user_unhappy`): owner scored 5/10 while AI
   is 9 — same: get concrete feedback first.
3. `maintainability` (priority 8): owner scored 6/10; split the two large
   generators (`build_research_master.py` ~1660 lines,
   `build_catalogue_pages.py` ~1078 lines) into focused modules; the
   126-test suite is the safety net.
4. `code_hygiene` (priority 4): same refactor workstream.
5. `content_quality` (priority 3, `user_unhappy`): owner scored 7/10; clarify
   expectations (e.g. raw placeholder rows still visible in the original
   sheet?).
6. `repo_organization` (priority 3): consolidation executed 2026-08-09
   (4 superseded/implemented root docs archived); re-audit the aspect on the
   next pass — score kept at 7.
7. Triage GitHub issue #18 (owned-flags cross-check vs. the lak.nz Drive) —
   requires owner Drive access or a CSV export.

## User scores currently known

Explicit owner scores (2026-08-09, via Arena chat):

| Aspect | User score |
|---|---:|
| github_pages_presentation | 5 |
| ux_usability | 5 |
| content_quality | 7 |
| maintainability | 6 |

All other aspects have `user_score: null` — do not invent scores from PR
merges, silence, or assumed satisfaction. AI scores are unchanged by these
user scores (see `.scoreboard/scoreboard.yml`).

## Important risks

- CSP `style-src 'unsafe-inline'` (low severity; required for dark-mode
  toggles; scripts are hash-pinned, Tabulator SRI-pinned). Visible in
  `SCOREBOARD.md` and `scoreboard.yml` until the owner accepts or mitigates it.
- Browser e2e suite (26 specs) cannot run in the Arena sandbox (Playwright
  CDN blocked); CI is the verification point — always check CI status after
  pushes.
- Live site `https://56eli.github.io/docsheet` is unreachable from the
  sandbox network; use `gh run list` Pages status instead.

## Presentation/UX implementation (2026-08-09, owner approved the full plan)

Phases A–D of `archive/PRESENTATION_UX_PROPOSAL_2026-08-09.md` (archived
2026-08-09 after implementation) are implemented on
`arena/019fe659-docsheet`: catalogue overview hero + collection stats +
series strip, desktop Browse cards toggle, Review-workspace nav toggle,
Series browser tab, search hints, loading skeleton, a11y labels; browser
suite 19 → 26 tests. **Scoreboard AI scores are unchanged pending a re-audit
and the owner's re-score** — the owner's user scores (presentation 5, UX 5)
still make those the top priorities (15/12). Next agent: verify the new
specs in CI, then ask the owner to re-score or give concrete feedback.

## Manual workflow edits pending

None. See `.scoreboard/manual-workflow-edits.md`.

## Quality gate status

`repo_ready` = **fail** (overall_effective_score **7.9** < 8 minimum, after
the owner's user scores: presentation 5, UX 5, content 7, maintainability 6).
All five required aspect thresholds still pass individually. The gate will
recover when the owner raises scores, the flagged aspects are improved, or a
re-audit changes effective scores. Re-evaluate after the next audit.

## Checks last run

- `python process_data.py --check` ✅
- `python build_research_master.py --check` ✅ (362 items; 75 excluded; 134 overrides)
- `python build_catalogue_pages.py --check` ✅
- `python reconcile_research_master.py --check` ✅
- `python map_series_taxonomy.py --check` ✅ (186 mappings; 0 queued)
- `python sync_inventory_mirrors.py --check` ✅
- `python -m unittest discover tests` ✅ Ran 126, OK
- `coverage run -m unittest discover tests && coverage report` ✅ 91%
- `node --check docs/app.js` + all `tests/*.spec.js` (26 browser specs) ✅
- `npm ci` ✅; Playwright browser install ❌ (CDN blocked in sandbox — CI only;
  the 26 specs run in CI)
- Static serve of `docs/` ✅ (all assets 200)

## Files intentionally not changed

- `.github/workflows/*` — policy: never edit workflows without explicit user
  instruction; none needed currently.
- No data/master CSV changes for the scoreboard (read-only audit scoring).

## Notes for next sandboxed session

1. Start by reading `SCOREBOARD.md`, `.scoreboard/scoreboard.yml`,
   `.scoreboard/agent-handoff.md`, and `AGENTS.md` (Scoreboard Protocol).
2. `NEXT_AGENT_HANDOFF.md` is still the deep project handoff; the scoreboard
   is the lightweight durable layer on top.
3. All audit findings are resolved; the only open data item is issue #18.
4. If you change scores: update `scoreboard.yml`, `history.md`, `SCOREBOARD.md`,
   this file, and the PR template section — and record evidence.
5. Branch for this session: `arena/019fe659-docsheet` (commits `f2d05c8`,
   `83b5c37`, `1886b84`). No PR has been opened yet; the owner may merge or
   open one later.
