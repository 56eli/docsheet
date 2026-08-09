# Scoreboard History

| Date | Aspect | AI Before | AI After | User Before | User After | Changed By | Evidence / Notes |
|---|---|---:|---:|---:|---:|---|---|
| 2026-08-09 | project_purpose_scope | — | 9 | — | null | Arena agent | Baseline audit; README/INSTRUCTIONS purpose reproduced; full-stack audit §1–§2. |
| 2026-08-09 | readme_onboarding | — | 9 | — | null | Arena agent | Baseline audit; README counts verified exactly against CSVs; 6/6 --check green. |
| 2026-08-09 | repo_organization | — | 7 | — | null | Arena agent | Baseline audit; 18 root .md files remain noisy (was 24 pre-PR #43); needs_work. |
| 2026-08-09 | code_hygiene | — | 7 | — | null | Arena agent | Baseline audit; py_compile clean, but generators remain large monoliths; needs_work. |
| 2026-08-09 | architecture | — | 9 | — | null | Arena agent | Baseline audit; ledger-driven pipeline with --check idempotence verified end-to-end. |
| 2026-08-09 | maintainability | — | 7 | — | null | Arena agent | Baseline audit; monoliths (build_research_master 1660 lines); refactor in progress; needs_work. |
| 2026-08-09 | maintainability | 7 | 7 | null | 6 | Owner (via Arena chat) | Explicit user score 'maintainability 6/10'; effective 6, priority 8, status needs_work. |
| 2026-08-09 | type_safety_validation | — | 8 | — | null | Arena agent | Baseline audit; typed row contracts, controlled vocabularies, rule matrices verified. |
| 2026-08-09 | error_handling_logging | — | 8 | — | null | Arena agent | Baseline audit; non-zero exits, load-error UI, abort-safe fetches. |
| 2026-08-09 | dependency_hygiene | — | 9 | — | null | Arena agent | Baseline audit; pinned requirements-ci.txt, npm ci clean, audit 0 vulns (prior). |
| 2026-08-09 | tests | — | 9 | — | null | Arena agent | Baseline audit; 126/126 unit tests, 91% coverage ≥ 85 floor; 26 browser specs via CI. |
| 2026-08-09 | ci_cd | — | 9 | — | null | Arena agent | Baseline audit; CI + Pages green on main (gh run list); concurrency guards reviewed. |
| 2026-08-09 | security_privacy | — | 8 | — | null | Arena agent | Baseline audit; CSP/SRI/no secrets; low-severity style-src 'unsafe-inline' flag recorded. |
| 2026-08-09 | performance | — | 8 | — | null | Arena agent | Baseline audit; static JSON payloads; no browser benchmark (Playwright unavailable); medium confidence. |
| 2026-08-09 | github_pages_presentation | — | 9 | — | null | Arena agent | Baseline audit; 19-tab site, mobile browse; Pages deploy green; medium confidence (CI-verified). |
| 2026-08-09 | github_pages_presentation | 9 | 9 | null | 5 | Owner (via Arena chat) | Explicit user score 'github_pages_presentation 5/10'; effective 5, priority 15, status user_unhappy. |
| 2026-08-09 | ux_usability | — | 9 | — | null | Arena agent | Baseline audit; facets, chips, persistence, shortcuts, settings menu reviewed. |
| 2026-08-09 | ux_usability | 9 | 9 | null | 5 | Owner (via Arena chat) | Explicit user score 'ux_usability 5/10'; effective 5, priority 12, status user_unhappy. |
| 2026-08-09 | accessibility | — | 8 | — | null | Arena agent | Baseline audit; ARIA/focus-trap/roving tabindex; no automated scan run; medium confidence. |
| 2026-08-09 | content_quality | — | 9 | — | null | Arena agent | Baseline audit; ~20 independent probes, no data defects; ledger row 371 reclassified. |
| 2026-08-09 | content_quality | 9 | 9 | null | 7 | Owner (via Arena chat) | Explicit user score 'content_quality 7/10'; effective 7, priority 3, status user_unhappy. |
| 2026-08-09 | feature_completeness | — | 8 | — | null | Arena agent | Baseline audit; 19/19 views present; issue #18 open (owned flags vs Drive). |
| 2026-08-09 | deployment_readiness | — | 9 | — | null | Arena agent | Baseline audit; Pages automation green; docs/ self-contained with .nojekyll. |
| 2026-08-09 | agent_readiness | — | 9 | — | null | Arena agent | Baseline audit; handoff/INSTRUCTIONS/--check modes + new scoreboard files. |
| 2026-08-09 | task_hygiene | — | 8 | — | null | Arena agent | Baseline audit; 1 open issue (#18); no TODO markers in notes. |
| 2026-08-09 | auditability | — | 9 | — | null | Arena agent | Baseline audit; provenance columns, ledger dispositions, generated reconciliation. |
| 2026-08-09 | overall_effective_score | — | 8.4 | — | null | Arena agent | Weighted average of 22 aspects (701/83); gate warning (risk flag + medium-confidence items). |
| 2026-08-09 | overall_effective_score | 8.4 | 7.9 | null | (4 aspects) | Owner (via Arena chat) | User scores applied (presentation 5, UX 5, content 7, maintainability 6); weighted average 655/83 = 7.9; gate fail (below 8 minimum). |
| 2026-08-09 | tests | 9 | 9 | null | null | Arena agent | REVISION1 ODS pass: suite 126 → 132 (OwnerOverrideAndDisplayOrderTests: overrides + display order); coverage 91% → 90% (floor 85, generators still 88%); six --check green. No score change. |
| 2026-08-09 | content_quality | 9 | 9 | null | null | Arena agent | Owner REVISION1 ODS applied (58 filenames, year/notes overrides, block order); all 362 rows matched cell-by-cell before applying. No score change. |
| 2026-08-09 | github_pages_presentation | 9 | 9 | 5 | 5 | Arena agent | Desktop table modernized: sleek Linear/Stripe style with subtle left-border accents, refined row padding and typography, and REVISION1 ODS grouping color-coding (11 distinct block groups); doc sweep aligned test count 126 -> 132 and coverage to 90% across secondary docs. |
| 2026-08-09 | auditability | 9 | 9 | — | null | Arena agent | Deep full-stack and catalogue audit completed; documented in docs/audits/2026-08-09-expert-full-stack-audit.md; all 6 --check modes green, 132 tests green, 0 data defects. |
| 2026-08-09 | code_hygiene | 7 | 9 | — | null | Arena agent | Ran ruff linter sweep across all python modules and tests: resolved all 61 linter notices down to 0 warnings, added missing shebangs, removed unused imports/variables, and updated exception handling. |
| 2026-08-09 | maintainability | 7 | 9 | 6 | 6 | Arena agent | Monolith generator scripts build_research_master.py (1,747 lines) and build_catalogue_pages.py (1,169 lines) refactored into modular pipeline/ package (helpers, enrichments, validators, relationships); 132/132 tests green, coverage 90%, all 6 --check modes green. |
