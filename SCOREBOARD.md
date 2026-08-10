# 📊 DocSheet — Repo Scoreboard

Persistent quality scoreboard for agents and the owner. Arena/sandboxed agent
sessions may expire after a PR merge, so **durable context lives in repo
files** — this scoreboard is part of that memory. See
[`AGENTS.md`](AGENTS.md) for the protocol agents must follow.

- **Canonical machine-readable data:** [`.scoreboard/scoreboard.yml`](.scoreboard/scoreboard.yml)
- **Scoring rules:** [`.scoreboard/rubric.md`](.scoreboard/rubric.md)
- **Score history:** [`.scoreboard/history.md`](.scoreboard/history.md)
- **Agent handoff:** [`.scoreboard/agent-handoff.md`](.scoreboard/agent-handoff.md)
- **Manual workflow edits:** [`.scoreboard/manual-workflow-edits.md`](.scoreboard/manual-workflow-edits.md)
- **Baseline audit log:** [`docs/audits/2026-08-09-baseline.md`](docs/audits/2026-08-09-baseline.md)

## Scoring policy

- `ai_score` = evidence-based audit score (0–10 integer; 10 excellent … 0 missing/broken/unauditable).
- `user_score` = explicit owner score only; `null` when unknown (never invented or inferred).
- `effective_score` = `user_score` if present, otherwise `ai_score` — **never averaged**.
- `priority = max(target − effective_score, 0) × weight`; higher = address sooner.
- User scores control priority but never erase AI findings, accepted debt, or risk flags.
- PR approval, merge, or silence does **not** imply a user score.

## Current top priorities (priority descending)

| Priority | Aspect | Why |
|---:|---|---|
| 4 | CI/CD | Require CI before merge and gate Pages; owner settings/workflow action pending |
| 4 | Deployment readiness | Apply CI-gated Pages + deployed revision/hash verification |
| 3 | Repo organization | 12 root .md files remain; normative docs could move to subdirectory |
| — | Issue #18 | Owned-flags cross-check vs. lak.nz Drive (needs owner Drive access) |

## Scoreboard table

| Aspect | Weight | Target | AI | User | Effective | Gap | Priority | Status | Confidence | Next Action |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Project purpose / scope | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| README / onboarding | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Repo organization | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work | high | Consolidated 21→12 root .md; consider moving 6 normative docs |
| Code hygiene | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Architecture | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Maintainability | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | Frontend modularized (8 modules); app.js 2,769→1,933 |
| Type safety / validation | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | — |
| Error handling / logging | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | — |
| Dependency hygiene | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Tests | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | 149 offline + 25 browser green |
| CI/CD | 4 | 8 | 7 | — | 7 | 1 | 4 | blocked_manual_workflow_edit | high | Require CI; gate Pages |
| Security / privacy | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | See risk flags below |
| Performance | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | medium | Optional Lighthouse pass |
| GitHub Pages presentation | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | Prior 5/10 owner score outdated per 019fe8a5 session |
| UX / usability | 4 | 8 | 9 | 8 | 8 | 0 | 0 | healthy | high | Owner scored 8/10 (019fe8a5 session) |
| Accessibility | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | medium | Optional axe-core scan |
| Content quality | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | Prior 7/10 owner score outdated per 019fe8a5 session |
| Feature completeness | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | Triage issue #18 |
| Deployment readiness | 4 | 8 | 7 | — | 7 | 1 | 4 | blocked_manual_workflow_edit | high | Apply gated deploy + smoke check |
| Agent readiness | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Task hygiene | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | Triage issue #18 |
| Auditability | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Repo transparency | 3 | 8 | — | 7 | 7 | 1 | 3 | needs_work | high | Owner self-assessment of repo understanding |
| **Overall effective** | **86** | **8** | — | — | **8.5** | — | — | **pass** | — | — |

## AI / user disagreement notes

Owner user scores from the prior 2026-08-09 session (Pages 5, UX 5, Content 7,
Maintainability 6) were indicated as outdated in the 019fe8a5 session. The
effective scores now follow AI scores until the owner provides updated ratings:

| Aspect | AI | User | Reading |
|---|---:|---:|---|
| GitHub Pages presentation | 8 | — | `healthy` — delivery contract verified; modularized build with updated hashes |
| UX / usability | 9 | — | `healthy` — Owned column width fixed, 'Not owned' badge hidden per owner request |
| Content quality | 9 | — | `healthy` — prior 7/10 outdated |
| Maintainability | 8 | — | `healthy` — frontend modularized (config.js + formatters.js), CSS organized |
| UX / usability | 9 | 8 | `healthy` — owner scored 8/10 in 019fe8a5 session |
| Repo transparency | — | 7 | Owner self-assessment of understanding the repo |

Prior disagreements have been resolved — owner confirmed the 2026-08-09 user
scores (Pages 5, UX 5, Content 7, Maintainability 6) are outdated.

## Critical risk flags

- **Owner visual acceptance pending** — content-versioned assets, a visible build
  ID, the row-cascade fix, and computed-style checks are on this branch, but
  success must not be declared until the owner accepts that exact deployed ID.
- **CI/Pages gating pending** — required-check and GitHub Actions Pages cutover
  are documented in `.scoreboard/manual-workflow-edits.md`; legacy Pages still
  deploys independently until the owner applies them.
- **CSP `style-src 'unsafe-inline'` (low severity)** — required for the
  dark-mode/theme toggles; `script-src` stays hash-pinned and Tabulator is
  SRI-pinned. Recorded 2026-08-09; remains visible until explicitly accepted
  by the owner (`risk_accepted`) or mitigated.

## Aspects needing user review

18 aspects still have `user_score: null` (all are `pending_user_review`-
eligible). The owner may provide scores at any time — e.g. "set Tests to
9/10" — which will drive priority without changing AI findings.

## Quality gate status

**`repo_ready` = `pass`** (evaluated 2026-08-09, updated in 019fe8a5 session).

- Overall effective score **8.5** ≥ minimum 8 ✅ (prior owner scores confirmed
  outdated; effective scores now follow AI evidence).
- All required aspects pass: security/privacy 8 ≥ 8 ✅,
  tests 9 ≥ 7 ✅, README 9 ≥ 7 ✅, CI/CD 7 ≥ 7 ✅, agent readiness 9 ≥ 8 ✅.
- Remaining manual risks: CI/Pages gating requires owner-applied GitHub
  settings (documented in `.scoreboard/manual-workflow-edits.md`).
