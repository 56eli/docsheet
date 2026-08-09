# Scoreboard Rubric

The authoritative machine-readable data lives in `.scoreboard/scoreboard.yml`;
this rubric defines how scores, statuses, gates, and handoffs work.

## 1. Purpose

The scoreboard separates **AI audit judgment** (`ai_score`) from **user
satisfaction / override** (`user_score`). AI scores diagnose the repo with
recorded evidence. User scores decide planning priority. They are never
averaged, and user scores never erase AI findings, accepted debt, or risk
flags.

## 2. Score scale

0–10 integer scores only:

| Score | Meaning |
|---|---:|
| 10 | excellent |
| 9 | very strong |
| 8 | solid / ready |
| 7 | good enough with some issues |
| 6 | usable but needs improvement |
| 5 | mixed / incomplete |
| 4 | weak |
| 3 | poor |
| 2 | barely functional |
| 1 | almost absent |
| 0 | missing, broken, or unauditable |

Rules:

- Scores must be integers.
- `null` means unknown/missing.
- `null` is different from `0`.
- `0` means missing, broken, or unauditable.
- Do not use `0` to mean unknown.

## 3. Score types

- `ai_score`: evidence-based audit score produced by an agent after auditing.
- `user_score`: explicit owner/user score only. Never invented or inferred.
- `effective_score`: `user_score` if present, otherwise `ai_score`.

## 4. Effective score rule

```text
effective_score = user_score if present, otherwise ai_score
```

Never average AI and user scores.

User scores control planning priority, but they do not erase AI evidence,
accepted debt, or risk flags. PR approval, merge, or lack of user complaint
does **not** imply a new `user_score`.

## 5. Priority formula

```text
gap = max(target - effective_score, 0)
priority = gap * weight
```

Higher `priority` means future agents should address it sooner.

## 6. Status definitions

| Status | Meaning |
|---|---|
| `pending_audit` | No AI score exists yet. |
| `pending_user_review` | AI score exists, but user score is `null`, and no more urgent status applies. |
| `healthy` | Effective score >= target and no more specific status applies. |
| `needs_work` | Effective score < target and no more specific status applies. |
| `user_unhappy` | User score < target while AI score >= target. |
| `accepted_debt` | User score >= target while AI score < target. |
| `needs_audit` | AI score exists, but evidence is thin, confidence is low, or the score needs verification. |
| `stale` | Audit older than 45 days or predates a major rewrite. |
| `blocked_manual_workflow_edit` | Improvement requires a manual GitHub workflow edit. |
| `risk_accepted` | User explicitly accepts a documented risk; the risk flag remains visible. |
| `not_applicable` | Aspect does not apply to this repo. |

Clearly distinguish:

```text
pending_audit = no AI score exists yet
needs_audit   = AI score exists but evidence is thin, confidence is low, or verification is needed
```

If multiple statuses apply, prefer the most specific/actionable status.
Suggested precedence:

```text
not_applicable
pending_audit
blocked_manual_workflow_edit
user_unhappy
risk_accepted
accepted_debt
needs_audit
stale
needs_work
pending_user_review
healthy
```

Stale precedence: `stale` overrides `healthy`, `needs_work`, or
`pending_user_review`, unless a more urgent status (e.g.
`blocked_manual_workflow_edit`, `user_unhappy`, `risk_accepted`,
`accepted_debt`, `needs_audit`) applies.

## 7. User score protection

- Agents must not invent user scores.
- Agents must not infer user scores.
- Agents must not change user scores without explicit user instruction.
- The only valid user score source is explicit user instruction.

Valid examples:

```text
User: "Set GitHub Pages presentation to 4/10."
User: "Code hygiene is 10/10 for my purposes."
User: "README is now 8/10."
```

Invalid sources:

```text
PR was merged.
User did not complain.
Agent thinks the user will like it.
Agent assumes approval from silence.
```

## 8. AI score update rules

- AI scores may change only after an evidence-based audit.
- Evidence must mention commands run, files reviewed, or observed repo state.
- If confidence is low, say why and consider `status: needs_audit`.
- Record every change in `.scoreboard/history.md`.

## 9. Risk flag rules

- Risk flags remain visible even if the user accepts the risk.
- Security, privacy, data-loss, deployment, correctness, and compliance risks
  should be flagged.
- If the user explicitly accepts a risk, use `risk_accepted` — but the risk
  flag stays in `risk_flags` and in `SCOREBOARD.md`.

## 10. Quality gates

- Gates use `effective_score`.
- User overrides may satisfy numeric gates.
- Accepted debt and risk flags remain visible.
- If a gate passes only because of `user_score` while `ai_score` is low,
  record `accepted_debt` or `risk_accepted` for the affected aspect.
- Gate statuses: `pass`, `warning`, `fail`, or `unknown`.
- Gate results are stored in both `summary.repo_ready_gate_status` and
  `quality_gates.repo_ready.status`, and must stay consistent.
- `warning` means numeric thresholds pass but risk flags, accepted debt,
  low-confidence evidence, or stale scores exist.

## 11. Arena/sandbox handoff rule

- Agent sessions are sandboxed and may expire after PR merge.
- Each agent must update `.scoreboard/agent-handoff.md` before finishing.
- Future agents must not rely on chat memory — repo files are the durable
  memory (`meta.context_policy`).

## 12. Manual workflow edit policy

- Do not edit `.github/workflows/*` unless the user explicitly instructs it.
- Document needed edits in `.scoreboard/manual-workflow-edits.md`.
- If a workflow change blocks progress, use
  `status: blocked_manual_workflow_edit` for the affected aspect.

## 13. Safe audit behavior

- Do not install new dependencies just to audit unless necessary and safe.
- Do not run destructive commands.
- Prefer existing project scripts (`--check` modes, `unittest`) and read-only
  inspection.
- If checks cannot be run safely (e.g. Playwright CDN blocked in the
  sandbox), record the limitation in the evidence and the audit log.
