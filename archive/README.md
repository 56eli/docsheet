# Archive

Superseded status documents, research drafts, and evidence notes that are no
longer normative. Files here are kept for provenance only — **do not treat
their counts, states, or instructions as current.** For current frontend,
Actions, Pages, and acceptance status use
[`docs/audits/2026-08-09-end-user-row-delivery-postmortem.md`](../docs/audits/2026-08-09-end-user-row-delivery-postmortem.md),
plus [README.md](../README.md),
[NEXT_AGENT_HANDOFF.md](../NEXT_AGENT_HANDOFF.md), and the generated
[RECONCILIATION_REPORT.md](../RECONCILIATION_REPORT.md). The older root audits
remain point-in-time data evidence only.

Root-level full-stack audits superseded by `FULL_STACK_AUDIT_2026-08-08_ARENA.md`
and moved here in the 2026-08-08 audit-noise cleanup:
- `FULL_STACK_AUDIT_2026-08-07_DEEP.md` — the 2026-08-07 end-of-day deep audit
  (was the root "current audit" until 2026-08-08; cross-referenced from
  historical session logs).
- `FULL_STACK_AUDIT_2026-08-08.md` — 2026-08-08 base audit (sections 1–14).
- `FULL_STACK_AUDIT_2026-08-08_DEEP_DIVE.md` — 2026-08-08 deep-dive companion.
- `FULL_STACK_AUDIT_2026-08-08_INDEPENDENT.md` — 2026-08-08 independent
  baseline audit (original 13KB archive copy; the expanded 31KB root version
  is archived as `FULL_STACK_AUDIT_2026-08-08_INDEPENDENT_ROOT.md`).
- `FULL_STACK_AUDIT_2026-08-08_INDEPENDENT_ROOT.md` — the expanded root-level
  version of the 2026-08-08 independent audit (31KB; supersedes the archive
  copy above); archived 2026-08-09 in the doc-cleanup pass.
- `FULL_STACK_AUDIT_2026-08-09_ARENA.md` — 2026-08-09 Arena audit
  (pre-PR #40); findings resolved at HEAD; archived 2026-08-09.
- `FULL_STACK_AUDIT_2026-08-09_ARENA_INDEPENDENT_FRESH.md` — 2026-08-09
  independent fresh-eyes audit; archived 2026-08-09 in the doc-cleanup pass.
- `UI_PRINCIPLES_AND_SUGGESTIONS.md` — UI design principles; archived 2026-08-09.
- `UX_REWORK_SUGGESTIONS.md` — prioritized UX backlog; archived 2026-08-09.
- `WORKFLOW_FIX_DROPINS_2026-08-09.md` — dated workflow fix snippets; archived 2026-08-09.
- `WORKFLOW_WEB_EDITOR_GUIDE.md` — web-editor workflow guide; archived 2026-08-09.

Root-level documents archived 2026-08-09 (repo-organization pass; the
declared-current audits are `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md`
+ `FULL_STACK_AUDIT_2026-08-09_ARENA_EXPERT.md` + `FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md`
at the repository root):

- `FULL_STACK_AUDIT_2026-08-08_ARENA.md` — 2026-08-08 checkpoint audit; the
  historical baseline pair with the next entry; superseded by the 08-09 audits.
- `FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md` — 2026-08-08 fresh-eyes
  independent audit; historical baseline pair; superseded by the 08-09 audits.
- `EXTERNAL_AUDIT.md` — 2026-08-08 external five-part audit of `bbe8b01`
  (pre-PR #40); carries a SUPERSEDED banner (opposite-direction owned-casing
  claim; references `check_docsheet.py`, which is not in the repo).
- `PRESENTATION_UX_PROPOSAL_2026-08-09.md` — Phases A–D fully implemented
  (catalogue overview hero, collection stats, series strip, Browse cards,
  Review-workspace toggle, Series tab, search hints, loading skeleton, a11y);
  re-verification tracked via scoreboard `github_pages_presentation` /
  `ux_usability`.

- `HANDOFF_HISTORY.md` — archived 2026-08-03 session chronicle + 2026-08-04
  final-audit notes, moved out of `NEXT_AGENT_HANDOFF.md` in the 2026-08-07
  hygiene checkpoint (kept for ruling rationale; not current state).
- `SCHEMA_REDUNDANCY_REVIEW.md` — two-pass column/sheet redundancy audit
  (2026-08-07); owner approved all three removals (title_source, meta.json,
  Original-view empty columns); includes the documented keep-list.
- `RULING_PREP_EMPTY_COLUMNS.md` — evidence + executed ruling (2026-08-07):
  the four always-empty master columns were dropped from the schema after
  showing no input could ever populate them.
- `TITLE_HYGIENE_PROPOSAL.md`, `ITEM_TYPE_CLASSIFICATION_PROPOSAL.md`,
  `VERITAS_ARTIFACT_REVIEW.md`, `VERITAS_PRODUCT_MAPPING.md`,
  `LECTURE_YEAR_INVESTIGATION.md`, `OFFICIAL_CATALOGUE_DISCOVERY.md`,
  `GITHUB_PAGES_DEPLOYMENT_ANALYSIS.md`, `RULING_PREP_PROGRESSIVE_LEVELS_309_221.md`,
  `FULL_STACK_AUDIT_2026-08-04_FINAL_358_V2.md` — completed/executed documents
  moved from the root in the 2026-08-07 hygiene triage (batch 1 of
  `TEMP_RESPONSE_HYGIENE_2026-08-07.md`); kept for provenance, their findings
  are implemented/closed.
- `CATALOGUE_READABILITY_ROADMAP.md`, `LECTURE_SERIES_REVIEW.md`,
  `REVIEW_MODEL_SLIM_ANALYSIS.md`, `SERIES_WORK_REGROUPING_PROPOSAL.md` —
  historical proposal snapshots (2026-08-03–04) moved from the root in the
  2026-08-09 hygiene pass (`arena/019fe620-docsheet`); they correctly describe
  early counts (356 rows etc.) and are superseded by the current generated
  schema + `FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md`.
- `TEMP_RESPONSE_HYGIENE_2026-08-07.md` — hygiene/ledger/complexity assessment (2026-08-07): ranked improvement proposals (root-doc triage, year-mirror retirement, derivable inventory mirrors, coverage-gate raise, handoff checkpointing), with an "already clean, do not fix" list.
- `TEMP_RESPONSE_TITLE_AUDIT_2026-08-07.md` — distributor title-alignment session (2026-08-07): 60 live-verified title corrections to official naming, the 50491 re-link 121→278, decision rules R1–R5, and the full change table.
- `TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR27.md` — post-PR #27 audit (2026-08-07); re-verified all catalogue counts, root-caused the red CI run on `main` to the stale Playwright candidate assertions (fixed data-driven), and corrected the 103-test/92%-coverage doc drift.
- `TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR26.md` — comprehensive post-PR #26 system audit and verification report (2026-08-07); validates 366 master items, 0 untyped, 0 format blank, and recent rulings. (Note: its "19 international queue rows" figure was stale — the queue holds 36 rows.)
- `TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR24.md`, `TEMP_RESPONSE_AUDIT_2026-08-07_SESSION.md` — earlier 2026-08-07 session logs and post-PR #24 check verifications.
- `HANDOFF.md`, `PROJECT_STATE_AUDIT.md` — superseded status stubs (kept so old
  external references resolve).
- `IMPLEMENTATION_PLAN.md` — earlier roadmap, absorbed into
  `NEXT_AGENT_HANDOFF.md`.
- `UNBLOCK_INSTRUCTIONS.md` — the CI-workflow web-editor instructions from
  before the App had `workflows` permission. The owner applied them: the full
  CI workflow (all `--check` modes, unittest suite, coverage gate, Playwright)
  landed on `main` as commit `6b28e66` and passed (run `30834666253`).
- `OFFICIAL_SOURCE_REGISTRY_DRAFT.md`, `RESEARCH_MASTER_DRAFT.md`,
  `RESEARCH_MASTER_SCHEMA_MIGRATION_DRAFT.md` — research drafts whose final
  versions are implemented.
- `TEMP_FORMAT_POPULATION_PROPOSAL.md`, `TEMP_INFERRED_FORMATS_REVIEW.md`,
  `TEMP_NIGHTINGALE_PROVENANCE.md` — evidence notes for open follow-up work
  (format second pass; Nightingale-Conant provenance).

## 2026-08-03 dated reports (consolidation round 2)

Point-in-time reports from the 2026-08-03 sessions, archived here when the
full-stack audit (`../FULL_STACK_AUDIT_2026-08-03.md`) superseded them at the
root. They overlap heavily with each other; conclusions that remain normative
were absorbed into the root policies, schemas, and handoff.

- `AUDIT_2026-08-03_FULL.md` — the day's full coherence audit; still the
  evidence base for § references like "AUDIT_2026-08-03_FULL.md §12.9" in
  root docs.
- `COMPREHENSIVE_AUDIT_2026-08-03.md`, `STATUS_QUO_AUDIT_2026-08-03.md`,
  `EVERYTHING_VERIFICATION_REPORT_2026-08-03.md` — parallel same-day audits
  whose findings were verified and merged into the full audit above.
- `TEMP_RESPONSE_AUDIT_2026-08-03.md` — the day's working temp log; §11
  remains the evidence base for the 8 remaining blank-format records
  (§11c/§11d) and deliberate exclusion classes (§11i).
- `BLANK_CELLS_BACKFILL_REPORT_2026-08-03.md`,
  `FORMAT_BACKFILL_REPORT_2026-08-03.md`,
  `YEAR_MONTH_BACKFILL_REPORT_2026-08-03.md`,
  `DEDUPLICATION_URL_FILL_REPORT_2026-08-03.md`,
  `SCHEMA_CLEANUP_REPORT_2026-08-03.md` — one-off backfill/cleanup reports
  whose results are all applied and check-verified.
- `SESSION_SUMMARY_2026-08-03.md` — day summary, superseded by
  `../NEXT_AGENT_HANDOFF.md` §4.
- `SPREADSHEET_AUDIT.md`, `SPREADSHEET_UX_REVIEW.md` — early raw-sheet and UX
  audits; the UX review's recommendations are implemented (compact columns,
  merged Year-Month, whole-sheet export).
- `UUID_264_REVIEW.md` — review of the record later renumbered to **246**;
  see `../NEXT_AGENT_HANDOFF.md` §6 for the still-open deferral.
- `RELATIONSHIP_EXPANSION_AUDIT.md` — relationship-coverage audit; its
  finding F1 was closed with the primary-relationship coverage hard-fail in
  `build_catalogue_pages.py`.
