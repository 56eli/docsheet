# 📊 DocSheet — Repo Scoreboard

Persistent quality scoreboard for agents and the owner. Durable context lives in repository files because sandbox sessions can expire.

- **Canonical source:** [`.scoreboard/scoreboard.yml`](.scoreboard/scoreboard.yml)
- **Rubric:** [`.scoreboard/rubric.md`](.scoreboard/rubric.md)
- **History:** [`.scoreboard/history.md`](.scoreboard/history.md)
- **Current handoff:** [`.scoreboard/agent-handoff.md`](.scoreboard/agent-handoff.md)
- **Owner workflow actions:** [`.scoreboard/manual-workflow-edits.md`](.scoreboard/manual-workflow-edits.md)
- **Current audit:** [`docs/audits/2026-08-10-arena-019febd6-full-audit.md`](docs/audits/2026-08-10-arena-019febd6-full-audit.md)

## Scoring policy

- `ai_score` is an evidence-based audit score from 0–10.
- `user_score` is explicit owner input only; agents never infer it from merges, silence, or approval.
- `effective_score` is the user score when present, otherwise the AI score; scores are never averaged.
- `priority = max(target − effective_score, 0) × weight`.
- User scores control numeric priority but never erase AI findings or risk flags.

## Current verdict

**Repo-ready gate: CONDITIONAL PASS — 8.1/10 effective (694 weighted points / 86).**

The data pipeline is healthy. **The previously release-blocking frontend defect is fixed, merged to `main`, and verified live** (session 019feb3e): PR #64 (`54b37f7`) is deployed (Pages built @10:34Z), main CI run `31379726756` is green, and the public `build-manifest.json` + deployed `columns.js` are byte-verified to carry the P0 fix. The broken-baseline blocker is closed. The gate is *conditional* only on the owner-applied CI-gated (Actions) Pages switch and explicit owner visual acceptance — until Pages is gated, a future broken commit can still deploy before CI fails.

## Current priorities

| Priority | Aspect | Immediate action |
|---:|---|---|
| 8 | CI/CD | Owner: gate Pages on CI; agent-safe: add `node --check docs/js/*.js` + ESLint `no-undef` to ci.yml |
| 5 | GitHub Pages presentation | Owner: give explicit visual acceptance of the now-live, byte-verified build |
| 4 | Deployment readiness | Owner: switch Pages from legacy to Actions `workflow` build type (deploy depends on green CI) |
| 3 | Content quality | Resolve the owner-scored gap when new content direction is provided |
| — | Issue #18 | Ownership cross-check needs owner Drive access (open mismatch: ~12 owned=true with no matching file) |

Recent work: session 019febb6 added dependency-free XLSX, JSON, and TSV exports beside CSV/ODS, with contract/browser tests, and fixed the ODS Lecture Series color mapping (`lectures-2002-2011`, 201 rows). Earlier work completed the full audit, dead-code/mobile cleanup, Original Spreadsheet retirement, and audiobook ownership correction (289 true / 25 false / 49 blank overall).

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
| Error handling / logging | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Dependency hygiene | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Tests | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| CI/CD | 4 | 8 | 7 | — | 7 | 1 | 4 | blocked_manual_workflow_edit |
| Security / privacy | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Performance | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| GitHub Pages presentation | 5 | 8 | 8 | — | 8 | 0 | 0 | needs_owner_acceptance |
| UX / usability | 4 | 8 | 8 | 8 | 8 | 0 | 0 | healthy |
| Accessibility | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Content quality | 3 | 8 | 9 | 7 | 7 | 1 | 3 | user_unhappy |
| Feature completeness | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Deployment readiness | 4 | 8 | 8 | — | 8 | 0 | 0 | needs_owner_action |
| Agent readiness | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Task hygiene | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Auditability | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Repo transparency | 3 | 8 | 7 | 7 | 7 | 1 | 3 | needs_work |
| **Overall effective** | **86** | **8** | — | — | **8.1** | — | — | **conditional_pass** |

## User-score notes

The canonical owner scores remain unchanged:

- UX / usability: **8/10**. Current AI score is also 8 after the browser-verified P0 repair.
- Content quality: **7/10**. AI data audit remains 9; status is `user_unhappy` until explicit owner input changes it.
- Repo transparency: **7/10**.

No other user score is inferred.

## Critical risk flags

1. **RESOLVED (2026-08-10):** the broken public baseline is fixed, merged, deployed, and byte-verified live; this flag is retired.
2. **Ungated delivery (owner action):** Pages API still reports legacy `main:/docs`; deployment can outrun CI until the owner switches to Actions-based gated Pages.
3. **Owner acceptance pending:** the live build is hash-verified, but explicit owner visual acceptance is still required (`acceptance: owner_visual_review_required`).
4. **Low-severity CSP debt:** `style-src 'unsafe-inline'`; script policy remains hash-pinned and Tabulator uses SRI.
5. **Static-quality gap (agent-safe):** CI does not syntax-check `docs/js/*.js` and has no `no-undef` lint — both would catch the next P0-class defect pre-browser.

## Quality gate details

- Overall 8.1 ≥ required 8: **pass** (conditional on owner Pages-gating + acceptance).
- Security/privacy 8 ≥ 8: pass.
- Tests 9 ≥ 7: pass.
- README 8 ≥ 7: pass.
- CI/CD 7 ≥ 7: pass.
- Agent readiness 8 ≥ 8: pass.
- Remaining items are the owner-applied CI-gated Pages switch, owner visual acceptance, and the agent-safe quick wins (module syntax check, ESLint, dead-code removal).

See the current audit for full evidence, verification limitations, independent data counts, and the recommended sequence.
