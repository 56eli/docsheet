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
| 15 | GitHub Pages presentation | Modern Linear/Stripe design applied; owner to re-score |
| 12 | UX / usability | Clean horizontal dividers & comfortable row padding applied; owner to re-score |
| 8 | Maintainability | Monolith generators modularized into pipeline/ package |
| 3 | Content quality | Owner scored 7/10 (user_unhappy); AI 9 — clarify expectations |
| 3 | Repo organization | Root .md noise reduced 2026-08-09 (4 superseded/implemented docs archived); re-audit pending |
| — | Issue #18 | Owned-flags cross-check vs. lak.nz Drive (needs owner Drive access) |

## Scoreboard table

| Aspect | Weight | Target | AI | User | Effective | Gap | Priority | Status | Confidence | Next Action |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Project purpose / scope | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| README / onboarding | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Repo organization | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work | high | Re-audit after 2026-08-09 consolidation |
| Code hygiene | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Architecture | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Maintainability | 4 | 8 | 9 | 6 | 6 | 2 | 8 | needs_work | high | — |
| Type safety / validation | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | — |
| Error handling / logging | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | — |
| Dependency hygiene | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Tests | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | Keep CI running 26 browser specs |
| CI/CD | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Security / privacy | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | See risk flags below |
| Performance | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | medium | Optional Lighthouse pass |
| GitHub Pages presentation | 5 | 8 | 9 | 5 | 5 | 3 | 15 | user_unhappy | medium | Ask owner what falls short |
| UX / usability | 4 | 8 | 9 | 5 | 5 | 3 | 12 | user_unhappy | high | Ask owner what falls short |
| Accessibility | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | medium | Optional axe-core scan |
| Content quality | 3 | 8 | 9 | 7 | 7 | 1 | 3 | user_unhappy | high | Clarify owner expectations |
| Feature completeness | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | Triage issue #18 |
| Deployment readiness | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Agent readiness | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| Task hygiene | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy | high | Triage issue #18 |
| Auditability | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy | high | — |
| **Overall effective** | **83** | **8** | — | — | **7.9** | — | — | **fail** | — | — |

## AI / user disagreement notes

Owner user scores were provided on 2026-08-09. AI scores and evidence are
unchanged; the user scores below drive priority:

| Aspect | AI | User | Reading |
|---|---:|---:|---|
| GitHub Pages presentation | 9 | 5 | `user_unhappy` — owner finds the site presentation lacking despite a strong AI assessment; agents should ask what falls short |
| UX / usability | 9 | 5 | `user_unhappy` — same; concrete feedback needed |
| Content quality | 9 | 7 | `user_unhappy` — mild; clarify expectations |
| Maintainability | 7 | 6 | `needs_work` — both sides agree below target; modularize generators |

Disagreements are preserved — user scores never erase AI findings.

## Critical risk flags

- **CSP `style-src 'unsafe-inline'` (low severity)** — required for the
  dark-mode/theme toggles; `script-src` stays hash-pinned and Tabulator is
  SRI-pinned. Recorded 2026-08-09; remains visible until explicitly accepted
  by the owner (`risk_accepted`) or mitigated.

## Aspects needing user review

18 aspects still have `user_score: null` (all are `pending_user_review`-
eligible). The owner may provide scores at any time — e.g. "set Tests to
9/10" — which will drive priority without changing AI findings.

## Quality gate status

**`repo_ready` = `fail`** (evaluated 2026-08-09).

- Overall effective score **7.9** < minimum 8 ❌ (moved from 8.4 by the
  owner's user scores for GitHub Pages presentation 5, UX 5, content 7,
  maintainability 6)
- Required aspects still pass individually: security/privacy 8 ≥ 8 ✅,
  tests 9 ≥ 7 ✅, README 9 ≥ 7 ✅, CI/CD 9 ≥ 7 ✅, agent readiness 9 ≥ 8 ✅
- `fail` because the overall minimum is not met. User scores drive priority;
  AI evidence is unchanged. See `.scoreboard/scoreboard.yml` → `quality_gates`.
