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

**Repo-ready gate: FAIL — 7.8/10 effective (671 weighted points / 86).**

The data pipeline is healthy. Audited/deployed baseline `aa1f1b7` failed 25/25 browser specs after legacy Pages had already deployed it; this branch repairs the P0, removes dormant UI, and hardens shortcuts accessibility. PR CI run `31377436991` passes 149 offline, 2 Node, and 27 browser tests. The gate stays failed because legacy Pages still serves the broken baseline until merge/deploy, is not CI-gated, and the overall score remains below 8.

## Current priorities

| Priority | Aspect | Immediate action |
|---:|---|---|
| 8 | Deployment readiness | Merge/deploy the green repair, verify exact build, then owner gates Pages on CI |
| 5 | GitHub Pages presentation | Verify the exact public build and obtain owner acceptance |
| 4 | CI/CD | Require aggregate CI before merge/deploy; split data and browser jobs |
| 3 | Error handling / logging | Add a generic visible fatal-render state for async table failures |
| 3 | Performance | Measure Lighthouse/Web Vitals and eliminate duplicate module identities |
| — | Issue #18 | Ownership cross-check needs owner Drive access |

## Scoreboard table

| Aspect | Wt | Target | AI | User | Effective | Gap | Priority | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Project purpose / scope | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| README / onboarding | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Repo organization | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Code hygiene | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Architecture | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Maintainability | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Type safety / validation | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Error handling / logging | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work |
| Dependency hygiene | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Tests | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| CI/CD | 4 | 8 | 7 | — | 7 | 1 | 4 | blocked_manual_workflow_edit |
| Security / privacy | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Performance | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work |
| GitHub Pages presentation | 5 | 8 | 7 | — | 7 | 1 | 5 | needs_work |
| UX / usability | 4 | 8 | 8 | 8 | 8 | 0 | 0 | healthy |
| Accessibility | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Content quality | 3 | 8 | 9 | 7 | 7 | 1 | 3 | user_unhappy |
| Feature completeness | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Deployment readiness | 4 | 8 | 6 | — | 6 | 2 | 8 | blocked_manual_workflow_edit |
| Agent readiness | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Task hygiene | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Auditability | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Repo transparency | 3 | 8 | 7 | 7 | 7 | 1 | 3 | needs_work |
| **Overall effective** | **86** | **8** | — | — | **7.8** | — | — | **fail** |

## User-score notes

The canonical owner scores remain unchanged:

- UX / usability: **8/10**. Current AI score is also 8 after the browser-verified P0 repair.
- Content quality: **7/10**. AI data audit remains 9; status is `user_unhappy` until explicit owner input changes it.
- Repo transparency: **7/10**.

No other user score is inferred.

## Critical risk flags

1. **Broken public baseline:** the repair passes PR CI, but legacy Pages still serves `aa1f1b7` until merge/deploy.
2. **Ungated delivery:** Pages API reports legacy `main:/docs`; deployment can outrun CI.
3. **Incomplete module cache contract:** nested imports omit content versions and can load duplicate/stale module URLs.
4. **Owner acceptance pending:** the exact public build still needs hash/screenshot verification and explicit acceptance.
5. **Low-severity CSP debt:** `style-src 'unsafe-inline'`; script policy remains hash-pinned and Tabulator uses SRI.

## Quality gate details

- Overall 7.8 < required 8: **fail**.
- Security/privacy 8 ≥ 8: pass.
- Tests 9 ≥ 7: pass.
- README 8 ≥ 7: pass.
- CI/CD 7 ≥ 7: pass.
- Agent readiness 8 ≥ 8: pass.
- Remaining blockers are the overall score, legacy ungated deployment, exact live-build verification, and owner acceptance.

See the current audit for full evidence, verification limitations, independent data counts, and the remediation sequence.
