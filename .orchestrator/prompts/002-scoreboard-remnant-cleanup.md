Remove dead .scoreboard/ references from the PR template

0. FETCH AND VERIFY

use `git fetch --depth 1 origin +arena/01a0cb00-docsheet:refs/remotes/origin/_orch && git show refs/remotes/origin/_orch:.orchestrator/prompts/002-scoreboard-remnant-cleanup.md > /tmp/task.md`

Read this file from /tmp/task.md. Do NOT use `origin/arena/01a0cb00-docsheet` (single-branch clones do not create it). Do NOT use `FETCH_HEAD` (the next fetch of main overwrites it). Do NOT `git checkout` or `git show` orchestrator paths into your worktree. Write outside the repository; never commit this file; never push to the orchestrator branch `arena/01a0cb00-docsheet`.
Halt conditions: if /tmp/task.md is empty, or if `head -1 /tmp/task.md` does not equal the Expected title below, stop and report — do not improvise. If this stub and the fetched file disagree, the fetched file wins.
If GitHub auth fails mid-session with HTTP 401/403 "Bad credentials", that is a known sandbox issue: checkpoint locally first, then ask the operator via `ask_user` with the option "I reconnected GitHub — retry now" (plus one neutral alternative, custom answer enabled). Ask at most once per expiry event. Never improvise credentials, remotes, or git config.

1. TASK TITLE AND SCOPE

Finish the scoreboard dismantling (owner: "it definitely has to go") by removing the two dead `.scoreboard/manual-workflow-edits.md` references from `.github/pull_request_template.md`, replacing them with the settled owner policy now recorded in the canonical tracker, and advance the tracker's Immediate Next Task line to the next queued maintenance item.
Complete this in ONE pull request.

2. REQUIRED READING ORDER

1. `docs/PROJECT_STATE.md` — canonical tracker (merged via PR #74). §2 carries the workflow-edit policy; §4 carries the Immediate Next Task line you will advance.
2. `.github/pull_request_template.md` — the only file with dead scoreboard references in current scope; read it in full before editing.
3. `orchestrator/INIT-RECORD.md` — owner-order provenance for the dismantling (read-only context; do not edit).
Not required: the CORE prompt file (rules inlined below); `archive/`, `docs/audits/`, `review/`, and the root `0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch` (all historical — see §4).

3. PROJECT CONTEXT AND OWNER VISION

DocSheet is a governed catalogue + Pages spreadsheet whose governance now runs on Orchestrator CORE v4.9.1 with a fresh canonical tracker (`docs/PROJECT_STATE.md`, PR #74). The scoreboard system was dismantled on 2026-09-22 but the PR template still mandates its defunct path, so every PR form invites contributors to write to a file that does not exist.
Owner Vision Context: this is the second step of the owner-approved maintenance sequence (bootstrap → scoreboard remnants → behavior gate → handoff hygiene → product/research work); closing it clears the last live reference to the dismantled system so the maintenance queue can move to the behavior gate.

4. CONFIRMED FACTS, ARCHITECTURAL INVARIANTS, AND SCOPE BOUNDARIES

Confirmed facts (verify, do not re-derive):
- `.scoreboard/` does not exist on `main`. Confirm: `git ls-tree -r --name-only origin/main -- .scoreboard | wc -l` → `0` (after your sync fetch of main in §8).
- `.github/pull_request_template.md` contains EXACTLY two occurrences of `.scoreboard/manual-workflow-edits.md` (lines 4 and 21). Confirm with `grep -n ".scoreboard/manual-workflow-edits.md" .github/pull_request_template.md` — exactly two hits expected; on any other count, HALT AND REPORT.
- The tracker records the settled policy you will mirror, in §2: "The former `.scoreboard/manual-workflow-edits.md` tracking path is defunct with the scoreboard; any pending manual workflow edit must be raised with the owner before dispatch." Confirm anchor: `grep -n "defunct with the scoreboard" docs/PROJECT_STATE.md` — one hit, else HALT.
- The tracker's §4 Immediate Next Task currently reads (anchor `grep -n "Immediate Next Task" docs/PROJECT_STATE.md`, exactly one line, must start `- **Immediate Next Task:** Scoreboard remnant cleanup`):
  `- **Immediate Next Task:** Scoreboard remnant cleanup — remove or replace the dead \`.scoreboard/manual-workflow-edits.md\` references in \`.github/pull_request_template.md\` (current files only; \`archive/\` and \`docs/audits/\` stay historical), then continue the maintenance queue above.`
  If the line does not match this text, HALT AND REPORT — `main` may have moved past what this prompt was authored against.
- Historical files that legitimately still mention `.scoreboard/` and are OUT OF SCOPE (do not "fix"): `archive/**`, `docs/audits/**`, `review/APPLY_CI_LINT_PATCH_2026-08-10.md`, `review/LINKS_VIMEO_OWNED_FINDINGS.md`, root `0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch`, `docs/PROJECT_STATE.md` (its intentional dismantling records), `orchestrator/INIT-RECORD.md` (owner-order quote).

Architectural invariants this task must respect and preserve:
- Scoreboard dismantled; no new `.scoreboard/` paths may appear anywhere (tracker §1).
- `.github/workflows/*` change only on explicit owner instruction — this PR does not touch workflows.
- Research byte-freeze: `data/`, schemas, research docs/outputs untouched.
- Generated artifacts never hand-edited; delivery contract untouched (no frontend files).
- Agents never push to the orchestrator branch; the orchestrator never opens PRs absent express per-PR authorization.

Scope boundaries (this PR must NOT):
- Must NOT touch any file other than `.github/pull_request_template.md` and the single tracker line in `docs/PROJECT_STATE.md`.
- Must NOT edit `archive/`, `docs/audits/`, `review/`, the root init patch file, `AGENTS.md`, `NEXT_AGENT_HANDOFF.md`, `orchestrator/**`, workflows, code, data, tests, or frontend assets.
- Must NOT delete or rewrite the tracker's historical/decision bullets — only the Immediate Next Task line changes.
- Must NOT create tags, releases, or a second tracker.

5. CORE OBJECTIVE

A single PR where `.github/pull_request_template.md` contains zero `.scoreboard/` references (both dead mentions replaced with the tracker-aligned owner policy) and `docs/PROJECT_STATE.md` §4's Immediate Next Task now names the behavior-gate task as next.
Done criteria: PR open against `main`; `grep -n ".scoreboard" .github/pull_request_template.md` returns nothing; both edits match §6 byte-for-byte; full quality battery green; PR description per §15.

6. EXACT DELIVERABLES

Modify: `.github/pull_request_template.md` — exactly two replacements.

Replacement A — OLD (line 4; confirm with the grep in §4 first):

```
- [ ] Workflow edits documented in `.scoreboard/manual-workflow-edits.md`
```

Replacement A — NEW:

```
- [ ] Workflow edits raised with the owner (deferred items tracked in `docs/PROJECT_STATE.md`)
```

Replacement B — OLD (lines 20–21, two-line wrapped block):

```
- `.github/workflows/*` — agents must not edit workflows unless the owner
  explicitly instructs it; pending edits belong in `.scoreboard/manual-workflow-edits.md`.
```

Replacement B — NEW:

```
- `.github/workflows/*` — agents must not edit workflows unless the owner
  explicitly instructs it; pending edits are raised with the owner and tracked in `docs/PROJECT_STATE.md`.
```

Every other byte of the template stays identical (headings, checkboxes, prose).

Modify: `docs/PROJECT_STATE.md` — one line replaced.

OLD (exactly one line; confirm via `grep -n "Immediate Next Task" docs/PROJECT_STATE.md`, else HALT):

```
- **Immediate Next Task:** Scoreboard remnant cleanup — remove or replace the dead `.scoreboard/manual-workflow-edits.md` references in `.github/pull_request_template.md` (current files only; `archive/` and `docs/audits` stay historical), then continue the maintenance queue above.
```

NOTE on the OLD line: re-read the matched line from your grep output and use that exact text as the old side — the authoritative bytes are whatever `grep`/`sed -n '<n>p'` shows on `main`, including the exact rendering of the parenthetical. If your grep output differs from the text above in any character, prefer the grep output and say so in the PR description.

NEW:

```
- **Immediate Next Task:** Orchestrator behavior gate — repo-adaptive mechanical check covering the five CORE duties (dispatch-stub first line, guarded publish/verify form, CORE anchor sha256 match, trigger-phrase run-log entry, no merges to the orchestrator branch), with an explicit boundary statement that judgment duties stay with review lanes; then handoff-pointer hygiene (`AGENTS.md`, `NEXT_AGENT_HANDOFF.md`, `orchestrator/prompts/README.md`, `.gitignore` recovery-dir line).
```

Do NOT touch any other line of the tracker (its dated decisions, scope boundaries, and invariants — including the §3 bullet that still describes the queue as of 2026-09-22 — stay as written).

7. SUB-TASK BREAKDOWN AND CHECKPOINTS

1. Sync per §8, then run every §4 confirmation grep/ls-tree — on any mismatch HALT AND REPORT (no push required).       → no push yet
2. Apply Replacement A + B to `.github/pull_request_template.md` → commit + push
3. Apply the Immediate Next Task line replacement in `docs/PROJECT_STATE.md` → commit + push
4. Run §14 quality checks (incl. the zero-`scoreboard` grep) → commit + push (no-op if clean)
5. Open ONE pull request against `main` with the §15 description.       → done

8. BRANCH AND TARGET

Base branch: `main` — never the orchestrator branch.
Target branch: `fix/scoreboard-remnant-cleanup`
Orchestrator branch: `arena/01a0cb00-docsheet` — fetch source only; never a base or target; never push to it.
Dependencies: none. PR #74 (tracker bootstrap) is MERGED; you are building on current `main`.
Resuming: fresh branch from main.
Before the first checkpoint, align HEAD to a remote tip — being on a branch named `fix/scoreboard-remnant-cleanup` is not evidence it is the remote:

use `git fetch --depth 50 origin +fix/scoreboard-remnant-cleanup:refs/remotes/origin/_resume && git checkout -B fix/scoreboard-remnant-cleanup refs/remotes/origin/_resume`

If that fetch cannot find the remote ref, the branch is new:

use `git fetch --depth 1 origin +main:refs/remotes/origin/main && git checkout -B fix/scoreboard-remnant-cleanup origin/main`

Do not skip the fetch because you appear to be on the target. Do not commit on `main`. "couldn't find remote ref" here is not an environment failure.

9. WORK PERSISTENCE AND PUSH CADENCE

Checkpoint after each sub-task in section 7, before any long or risky operation, and at the end. Your session can expire without warning; unpushed work is lost. Section 7 is your push schedule; there is no time-based rule.
A checkpoint is ONE command — first push, later pushes, and the nothing-to-push no-op are the same form. Do not run status/diff inspections around it:

```
git add -A && (git diff --cached --quiet || git commit -qm "chore: wip <sub-task>") && git push -qu origin fix/scoreboard-remnant-cleanup
```

Match the project's commit convention for the subject (`git log` shows plain descriptive subjects; `chore: wip <sub-task>` is a valid fallback). Open ONE pull request at the end, when quality checks pass. Do not open a draft PR first. Checkpoint commits may be broken — that is expected. Never commit secrets. Never push to the orchestrator branch.
Sync rule: rebase onto `origin/main` ONLY before your first push. After the first push, integrate with `git fetch --depth 50 origin +main:refs/remotes/origin/main && git merge --no-edit origin/main` then `git push origin HEAD`. Never force-push unless explicitly instructed, and then only with `--force-with-lease`. On merge conflict: halt and report the conflicting files. Same for "refusing to merge unrelated histories" — never pass `--allow-unrelated-histories`.
If a push or fetch fails with an authentication or network error, report it plainly and keep working locally; retry the push at the next checkpoint. Never claim work is pushed while a push has failed; never modify credentials, remotes, or git config to work around it. If a push is rejected non-fast-forward, halt and report the raw rejection — do not `git pull`, do not force-push.

10. TECHNICAL REQUIREMENTS

- Documentation-only PR: two precise Markdown edits (byte-exact old→new as specified in §6).
- Preserve file encodings, trailing newlines, and line endings; do not reflow unrelated lines.
- TEST_COMMAND: `python -m unittest discover tests` — expect 158 tests, all pass in a dependency-complete environment (CI runs it; if your sandbox lacks pandas, subprocess tests fail with `No module named 'pandas'` — that is environmental: record it and rely on CI, do not "fix" the suite).
- INTEGRATION_TEST_COMMAND: not applicable — no component, persistence, API, queue, configuration, or deployment boundary is crossed; two Markdown files change.
- FULL_SUITE_COMMAND: `python -m unittest discover tests && npm run lint` — risk-based equivalent; Playwright e2e skipped locally (zero JS/HTML/CSS/data changes; CI runs it on the PR). Record the skip and reason.
- COVERAGE_COMMAND: `coverage run -m unittest discover tests && coverage report` — threshold 85% (`.coveragerc`), currently 92%; expect pass where dependencies exist; CI enforces it regardless.
- MUTATION_TEST_COMMAND: not warranted — no production logic paths change.
- LINT_COMMAND: `npm run lint` — zero errors.
- BUILD_COMMAND: not applicable — no build step; do not re-run generators.

11. SAFETY AND COMPATIBILITY RULES

- Must NOT break: any `--check` gate, the delivery contract, tests, CI on `main`, or the PR template's remaining structure (checkbox semantics stay usable on GitHub).
- Must NOT change: `data/`, schemas, research outputs, generated `docs/*.json`, frontend assets, workflows, tests, requirements, `package.json`.
- The template replacements must align with the tracker's §2 policy — do not invent a different workflow-edit process.
- No migrations apply; nothing user-facing on the live site changes.

12. CLEANUP RULES

By the final push: no commented-out code, temporary logs, ad-hoc scripts, TODO markers; no unrelated modifications; no reformatting outside the two edits. Do not commit the fetched prompt file or anything in /tmp. Intermediate checkpoint commits are exempt — clean up once before opening the PR.

13. STRICT BOUNDARIES / OUT OF SCOPE

- Do not push to the orchestrator branch `arena/01a0cb00-docsheet`.
- Do not open more than one PR; do not create tags or GitHub releases.
- Do not "clean" historical mentions of the scoreboard in `archive/`, `docs/audits/`, `review/`, the root init patch file, `AGENTS.md`, `NEXT_AGENT_HANDOFF.md`, `README.md`, `INSTRUCTIONS.md`, or `orchestrator/prompts/README.md` — later queued tasks own those pointers; this PR's file set is exactly the two deliverables.
- Do not add the behavior-gate checker, CI jobs, or scripts in this PR (that is the NEXT task).
- Do not edit `.github/workflows/*`.
- Do not rewrite tracker decisions/invariants beyond the one specified line.
- Artifacts: none produced; if anything artifact-like appears, do not commit it — path + sha256 into the PR description and stop.

14. QUALITY CHECKS

Run and record (expected outcome in parentheses):
- `grep -n ".scoreboard" .github/pull_request_template.md` (no output — zero hits)
- `grep -c "docs/PROJECT_STATE.md" .github/pull_request_template.md` (2 — both replacements landed)
- `grep -n "Immediate Next Task" docs/PROJECT_STATE.md` (exactly one line, now naming "Orchestrator behavior gate")
- `git diff main --stat` (touches ONLY `.github/pull_request_template.md` and `docs/PROJECT_STATE.md`)
- `python -m unittest discover tests` (158 pass; or documented environmental pandas failure + CI reliance)
- `coverage run -m unittest discover tests && coverage report` (pass, ≥85%, same caveat)
- `npm run lint` (zero errors)
- `git diff main -- .github/workflows/ data/ docs/app.js docs/index.html` (empty)
- Confirm: all work is pushed; `git status` clean.

15. PR DESCRIPTION REQUIREMENTS

Title: same as the work order title (first line above).
Body must contain:
- **Summary** — what and why (last live scoreboard references removed; tracker queue advanced).
- **Design rationale** — why replacement wording mirrors tracker §2 (raise-with-owner + tracker as the deferred ledger); why only the PR template is in scope while historical files keep their mentions (dated records, non-normative); why only the Immediate Next Task line updates (minor-fix tracker policy — avoid hot-file churn). Describe only this PR's changes.
- **Test results** — outcomes of every §14 command, including skip reasons and any environmental limitation.
- **Breaking changes / migration notes** — none expected; state so. Note the template checkbox wording change is intentional and GitHub-render-safe.
- Claim-scope check: every file named appears in the changed-file list.
- `#### Session Irregularities` per §16.

16. HARDENING REPORT — Session Irregularities

Under heading `#### Session Irregularities` in the PR description: if no significant irregularity (threshold: interfered with the prompt AND cost >~10 min / blocked progress / required workaround AND reveals a recurring invariant or blind spot), write `None significant`. Otherwise one row: `Category | Symptom | Impact | Workaround | Hardening candidate` (3–6 lines). Do not pad with trivial retries or expected platform behavior (refresh triggers, non-fast-forward halt, rewind alignment are expected). This report does not affect review verdicts unless it reveals a missing deliverable.
