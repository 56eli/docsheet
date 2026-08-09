# AGENTS.md — Instructions for Arena/sandboxed agents

This repository is worked on by Arena/sandboxed agents. Agent sessions may
expire after a PR merge, so **all durable project context must live in repo
files** — never rely on chat history or future agent memory.

Before any work, read (in order):

1. `SCOREBOARD.md` — human-readable scoreboard + top priorities.
2. `.scoreboard/scoreboard.yml` — canonical machine-readable scores.
3. `.scoreboard/agent-handoff.md` — what the previous agent left for you.
4. `.scoreboard/manual-workflow-edits.md` — any pending GitHub workflow edits.
5. `NEXT_AGENT_HANDOFF.md` — the deep project handoff (pipeline, data rules,
   open work).
6. `INSTRUCTIONS.md` — local setup and verification commands.

## Scoreboard Protocol

This repo uses a persistent scoreboard because Arena/sandboxed agent sessions
may expire after PR merge. Durable context must live in repo files.

### Before work

1. Read `SCOREBOARD.md`.
2. Read `.scoreboard/scoreboard.yml`.
3. Read `.scoreboard/agent-handoff.md`.
4. Read `.scoreboard/manual-workflow-edits.md`.
5. Identify affected scoreboard aspects.
6. Prioritize high-priority, low-effective-score, high-weight, risk-flagged,
   or user-unhappy aspects.

### During work

1. Preserve user scores.
2. Do not invent user satisfaction.
3. Do not treat PR approval, merge, or silence as a new user score.
4. Do not chase perfect AI scores if the user has accepted the area.
5. If AI score is high but user score is low, follow user notes and desired
   direction.
6. If AI score is low but user score is high, treat it as accepted debt
   unless risk flags exist or the task touches that area.
7. Do not directly edit `.github/workflows/*` unless explicitly instructed by
   the user.
8. Document needed workflow edits in `.scoreboard/manual-workflow-edits.md`.

### After work

1. Run relevant checks where possible (all six `--check` modes,
   `python -m unittest discover tests`).
2. Update only audited AI scores.
3. Recalculate effective score, gap, priority, and status.
4. Recalculate summary fields and quality gate status.
5. Add evidence for score changes.
6. Update `.scoreboard/history.md`.
7. Update `.scoreboard/agent-handoff.md` for the next sandboxed agent.
8. Summarize remaining manual workflow edits.

## Repository conventions (brief)

- Generators are standalone scripts with `--check` modes; run
  `python <script>.py --check` before and after data changes.
- The curated master is **generated** from `migration_review_ledger.csv` and
  the review overlays in `data/*.csv` — never hand-edit
  `data/research_master_draft.csv` or the `docs/*.json` outputs.
- Owner revisions go through the reviewed overlays
  `data/master_year_overrides.csv` and `data/master_notes_overrides.csv`
  (consumed by `build_research_master.py`); the Everything view/export order
  is `data/catalogue_display_order.csv` (consumed by
  `build_catalogue_pages.py`); the change record behind them is
  `review/hawkins-everything-REVISION1.ods`.
- All six `--check` modes must pass; the 139-test suite must stay green
  (coverage floor 85%).
- Do not edit `.github/workflows/*` (see `.scoreboard/manual-workflow-edits.md`).
