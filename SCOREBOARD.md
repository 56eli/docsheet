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
| 4 | Code hygiene | Generators remain large monoliths; split into focused modules |
| 4 | Maintainability | Same root cause; refactor in progress (PR #43 started it) |
| 3 | Repo organization | 18 root-level .md files; consolidate/archive superseded audits |
| — | Issue #18 | Owned-flags cross-check vs. lak.nz Drive (needs owner Drive access) |

## Scoreboard table

| Aspect | Weight | Target | AI | User | Effective | Gap | Priority | Status | Confidence | Next Action |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Project purpose / scope | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| README / onboarding | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Repo organization | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work | high | Archive superseded root audits |
| Code hygiene | 4 | 8 | 7 | — | 7 | 1 | 4 | needs_work | high | Split generator monoliths |
| Architecture | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Maintainability | 4 | 8 | 7 | — | 7 | 1 | 4 | needs_work | high | Modularize generators |
| Type safety / validation | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | — |
| Error handling / logging | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | — |
| Dependency hygiene | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Tests | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | Keep CI running 19 browser specs |
| CI/CD | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Security / privacy | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | See risk flags below |
| Performance | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | medium | Optional Lighthouse pass |
| GitHub Pages presentation | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy | medium | — |
| UX / usability | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Accessibility | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | medium | Optional axe-core scan |
| Content quality | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Feature completeness | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | Triage issue #18 |
| Deployment readiness | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Agent readiness | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Task hygiene | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | Triage issue #18 |
| Auditability | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| **Overall effective** | **83** | **8** | — | — | **8.4** | — | — | **warning** | — | — |

## AI / user disagreement notes

None yet — the user has not provided any scores (`user_score` is `null`
everywhere). If the owner supplies scores, disagreements are preserved here
and never averaged away.

## Critical risk flags

- **CSP `style-src 'unsafe-inline'` (low severity)** — required for the
  dark-mode/theme toggles; `script-src` stays hash-pinned and Tabulator is
  SRI-pinned. Recorded 2026-08-09; remains visible until explicitly accepted
  by the owner (`risk_accepted`) or mitigated.

## Aspects needing user review

All 22 aspects are `pending_user_review`-eligible (AI score exists, user
score `null`). The owner may provide scores at any time — e.g. "set UX to
7/10" — which will drive priority without changing AI findings.

## Quality gate status

**`repo_ready` = `warning`** (evaluated 2026-08-09).

- Overall effective score **8.4** ≥ minimum 8 ✅
- Required aspects: security/privacy 8 ≥ 8 ✅, tests 9 ≥ 7 ✅, README 9 ≥ 7 ✅,
  CI/CD 9 ≥ 7 ✅, agent readiness 9 ≥ 8 ✅
- `warning` because an active (low-severity) risk flag exists and several
  scores are medium-confidence (browser suite CI-verified only; no automated
  a11y scan). See `.scoreboard/scoreboard.yml` → `quality_gates`.
