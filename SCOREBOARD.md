# 📊 DocSheet — Repo Scoreboard

Persistent quality scoreboard for agents and the owner. Durable context lives in repository files because sandbox sessions can expire.

- **Canonical source:** [`.scoreboard/scoreboard.yml`](.scoreboard/scoreboard.yml)
- **Rubric:** [`.scoreboard/rubric.md`](.scoreboard/rubric.md)
- **History:** [`.scoreboard/history.md`](.scoreboard/history.md)
- **Current handoff:** [`.scoreboard/agent-handoff.md`](.scoreboard/agent-handoff.md)
- **Owner workflow actions:** [`.scoreboard/manual-workflow-edits.md`](.scoreboard/manual-workflow-edits.md)
- **Current audit:** [`docs/audits/2026-08-10-arena-019feaf6-full-audit.md`](docs/audits/2026-08-10-arena-019feaf6-full-audit.md)

## Scoring policy

- `ai_score` is an evidence-based audit score from 0–10.
- `user_score` is explicit owner input only; agents never infer it from merges, silence, or approval.
- `effective_score` is the user score when present, otherwise the AI score; scores are never averaged.
- `priority = max(target − effective_score, 0) × weight`.
- User scores control numeric priority but never erase AI findings or risk flags.

## Current verdict

**Repo-ready gate: FAIL — 7.1/10 effective (614 weighted points / 86).**

The data pipeline is healthy, but audited/deployed baseline `aa1f1b7` has a confirmed frontend runtime defect: `docs/js/columns.js` calls `isExtraEditionRow()` without importing it. Main CI failed 25/25 browser specs after legacy Pages had already deployed it. This branch carries the import repair plus executable Node/browser regression coverage; the gate stays failed until GitHub browser CI and the exact deployed revision are verified.

## Current priorities

| Priority | Aspect | Immediate action |
|---:|---|---|
| 16 | Deployment readiness | Repair frontend P0, then owner gates Pages on successful CI |
| 15 | GitHub Pages presentation | Import missing helper, execute formatters in tests, verify deployed build |
| 8 | CI/CD | Require aggregate CI before merge/deploy; split data and browser jobs |
| 8 | Feature completeness | Restore primary grid; restore or remove dormant overview/stats UI |
| 6 | Error handling / logging | Cover async formatter failure and visible fatal-render state |
| 5 | Agent readiness | Keep one current handoff/audit and synchronized scoreboards |
| 4 | Code hygiene | Add no-undef/import lint; remove redundant/dead module code |
| 4 | Maintainability | Correct module graph/cache strategy before more extraction |
| — | Issue #18 | Ownership cross-check needs owner Drive access |

## Scoreboard table

| Aspect | Wt | Target | AI | User | Effective | Gap | Priority | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Project purpose / scope | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| README / onboarding | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Repo organization | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Code hygiene | 4 | 8 | 7 | — | 7 | 1 | 4 | needs_work |
| Architecture | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Maintainability | 4 | 8 | 7 | — | 7 | 1 | 4 | needs_work |
| Type safety / validation | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Error handling / logging | 3 | 8 | 6 | — | 6 | 2 | 6 | needs_work |
| Dependency hygiene | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Tests | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| CI/CD | 4 | 8 | 6 | — | 6 | 2 | 8 | blocked_manual_workflow_edit |
| Security / privacy | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Performance | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work |
| GitHub Pages presentation | 5 | 8 | 5 | — | 5 | 3 | 15 | needs_work |
| UX / usability | 4 | 8 | 6 | 8 | 8 | 0 | 0 | accepted_debt |
| Accessibility | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work |
| Content quality | 3 | 8 | 9 | 7 | 7 | 1 | 3 | user_unhappy |
| Feature completeness | 4 | 8 | 6 | — | 6 | 2 | 8 | needs_work |
| Deployment readiness | 4 | 8 | 4 | — | 4 | 4 | 16 | blocked_manual_workflow_edit |
| Agent readiness | 5 | 8 | 7 | — | 7 | 1 | 5 | needs_work |
| Task hygiene | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work |
| Auditability | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Repo transparency | 3 | 8 | 7 | 7 | 7 | 1 | 3 | needs_work |
| **Overall effective** | **86** | **8** | — | — | **7.1** | — | — | **fail** |

## User-score notes

The canonical owner scores remain unchanged:

- UX / usability: **8/10**. Current AI score is 6 because the owner score predates the audited frontend regression; status is `accepted_debt`, and the P0 risk remains visible.
- Content quality: **7/10**. AI data audit remains 9; status is `user_unhappy` until explicit owner input changes it.
- Repo transparency: **7/10**.

No other user score is inferred.

## Critical risk flags

1. **Production JavaScript defect:** missing `isExtraEditionRow` import in `columns.js`.
2. **Ungated delivery:** Pages API reports legacy `main:/docs`; deployment can outrun CI.
3. **Incomplete module cache contract:** nested imports omit content versions and can load duplicate/stale module URLs.
4. **Browser acceptance pending:** byte/hash consistency does not prove application execution or owner visual acceptance.
5. **Low-severity CSP debt:** `style-src 'unsafe-inline'`; script policy remains hash-pinned and Tabulator uses SRI.

## Quality gate details

- Overall 7.1 < required 8: **fail**.
- Security/privacy 8 ≥ 8: pass.
- Tests 8 ≥ 7: pass.
- README 8 ≥ 7: pass.
- CI/CD 6 < 7: fail.
- Agent readiness 7 < 8: fail.

See the current audit for full evidence, verification limitations, independent data counts, and the remediation sequence.
