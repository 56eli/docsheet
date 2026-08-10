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

**Repo-ready gate: WARNING — 8.0/10 effective (687 weighted points / 86).**

The data pipeline is healthy. Baseline `aa1f1b7` failed after deployment, but PR #64 merged as `54b37f7`; main CI run `31379726756` passes 149 offline, 3 Node, and 28 browser tests, and Pages run `31379725585` deployed successfully. The live manifest exactly matches committed app/style/module/data hashes, live metadata reports 363 masters, and the fetched site renders the 363-row catalogue. The gate remains warning because legacy Pages is not CI-gated and explicit owner visual acceptance is pending.

## Current priorities

| Priority | Aspect | Immediate action |
|---:|---|---|
| 4 | Deployment readiness | Owner gates Pages on successful CI and enables required checks |
| 4 | CI/CD | Require aggregate CI before merge/deploy; split data and browser jobs |
| 3 | Error handling / logging | Add a generic visible fatal-render state for async table failures |
| 3 | Content quality | Resolve the owner-scored gap when new content direction is provided |
| — | Issue #18 | Ownership cross-check needs owner Drive access |

## Scoreboard table

| Aspect | Wt | Target | AI | User | Effective | Gap | Priority | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Project purpose / scope | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| README / onboarding | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Repo organization | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Code hygiene | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Architecture | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Maintainability | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Type safety / validation | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Error handling / logging | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work |
| Dependency hygiene | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Tests | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| CI/CD | 4 | 8 | 7 | — | 7 | 1 | 4 | blocked_manual_workflow_edit |
| Security / privacy | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Performance | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| GitHub Pages presentation | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| UX / usability | 4 | 8 | 8 | 8 | 8 | 0 | 0 | healthy |
| Accessibility | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Content quality | 3 | 8 | 9 | 7 | 7 | 1 | 3 | user_unhappy |
| Feature completeness | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Deployment readiness | 4 | 8 | 7 | — | 7 | 1 | 4 | blocked_manual_workflow_edit |
| Agent readiness | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Task hygiene | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Auditability | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Repo transparency | 3 | 8 | 7 | 7 | 7 | 1 | 3 | needs_work |
| **Overall effective** | **86** | **8** | — | — | **8.0** | — | — | **warning** |

## User-score notes

The canonical owner scores remain unchanged:

- UX / usability: **8/10**. Current AI score is also 8 after the browser-verified P0 repair.
- Content quality: **7/10**. AI data audit remains 9; status is `user_unhappy` until explicit owner input changes it.
- Repo transparency: **7/10**.

No other user score is inferred.

## Critical risk flags

1. **Ungated delivery:** Pages API reports legacy `main:/docs`; deployment can outrun CI.
2. **Owner acceptance pending:** the exact live revision and 363-row render are verified, but explicit visual acceptance is still required.
3. **Low-severity CSP debt:** `style-src 'unsafe-inline'`; script policy remains hash-pinned and Tabulator uses SRI.

## Quality gate details

- Overall 8.0 ≥ required 8: numeric pass.
- Security/privacy 8 ≥ 8: pass.
- Tests 9 ≥ 7: pass.
- README 8 ≥ 7: pass.
- CI/CD 7 ≥ 7: pass.
- Agent readiness 8 ≥ 8: pass.
- Gate remains **warning** because legacy Pages is ungated and explicit owner visual acceptance is pending.

See the current audit for full evidence, verification limitations, independent data counts, and the remediation sequence.
