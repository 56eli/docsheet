# Archive

Superseded status documents, research drafts, and evidence notes that are no
longer normative. Files here are kept for provenance only — **do not treat
their counts, states, or instructions as current.** For the current state use
the repository root: [README.md](../README.md),
[NEXT_AGENT_HANDOFF.md](../NEXT_AGENT_HANDOFF.md),
[FULL_STACK_AUDIT_2026-08-03.md](../FULL_STACK_AUDIT_2026-08-03.md), and the
generated [RECONCILIATION_REPORT.md](../RECONCILIATION_REPORT.md).

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
