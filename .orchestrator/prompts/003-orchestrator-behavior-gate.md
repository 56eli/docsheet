Add orchestrator behavior gate as a deterministic test stage

0. FETCH AND VERIFY

use `git fetch --depth 1 origin +arena/01a0cb00-docsheet:refs/remotes/origin/_orch && git show refs/remotes/origin/_orch:.orchestrator/prompts/003-orchestrator-behavior-gate.md > /tmp/task.md`

Read this file from /tmp/task.md. Do NOT use `origin/arena/01a0cb00-docsheet` (single-branch clones do not create it). Do NOT use `FETCH_HEAD` (the next fetch of main overwrites it). Do NOT `git checkout` or `git show` orchestrator paths into your worktree. Write outside the repository; never commit this file; never push to the orchestrator branch `arena/01a0cb00-docsheet`.
Halt conditions: if /tmp/task.md is empty, or if `head -1 /tmp/task.md` does not equal the Expected title below, stop and report — do not improvise. If this stub and the fetched file disagree, the fetched file wins.
If GitHub auth fails mid-session with HTTP 401/403 "Bad credentials", that is a known sandbox issue: checkpoint locally first, then ask the operator via `ask_user` with the option "I reconnected GitHub — retry now" (plus one neutral alternative, custom answer enabled). Ask at most once per expiry event. Never improvise credentials, remotes, or git config.

1. TASK TITLE AND SCOPE

Add the repo-adaptive mechanical orchestrator compliance gate as a new deterministic unittest stage (`tests/test_orchestrator_gate.py`) covering all five CORE duties with the mandated boundary statement, plus the tracker declarations the gate verifies and the test-count house-rule updates.
Complete this in ONE pull request.

2. REQUIRED READING ORDER

1. `docs/PROJECT_STATE.md` — canonical tracker; §2 is where the new declaration bullets land; §4 carries the Immediate Next Task line you advance. Also your source for the CORE anchor row (§2 first bullet).
2. `orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md` — read ONLY the section anchored by `grep -n "Orchestrator behavior gating" "orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md"` (the five duties + boundary) and the section anchored by `grep -n "dispatch stub standard" "orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md"` (duty-1 wording). Do not read the whole 122 KB file; the applicable text is also inlined below.
3. `tests/test_pipeline.py` — one representative test class only (style/reference for how this repo writes unittest: `unittest.TestCase`, clear subTests, CLI-subprocess patterns NOT needed here).
4. `.coveragerc` — confirms `tests/*` is omitted from the coverage denominator (your new file does not move the coverage number).
5. `README.md` and `INSTRUCTIONS.md` — the test-count lines you must update under the house rule (they say `158` today; confirm by grep, do not trust this sentence).
Not required: `archive/`, `docs/audits/`, frontend, generators, `data/`.

3. PROJECT CONTEXT AND OWNER Vision Context

DocSheet runs a deterministic CI gate set (six `--check` generators, 158-test suite at 92% coverage, lint, e2e) and now, after tasks 001–002, has a canonical tracker holding the CORE v4.9.1 sha256 anchor and the maintenance queue. The behavior gate is the third of four owner-approved maintenance tasks: it turns the orchestrator's five checkable duties into a fail-closed test so compliance is enforced by CI instead of memory.
Owner Vision Context: the owner wants orchestrator 4.9 functionality "in there as soon as possible" and chose this gate as priority 3 of the maintenance sequence; a green gate means every later dispatch can trust that anchor drift, unguarded publishes, missing run-log declarations, stub-format drift, or merges onto the orchestrator branch fail the build.

4. CONFIRMED FACTS, ARCHITECTURAL INVARIANTS, AND SCOPE BOUNDARIES

Confirmed facts (verify with the confirming command; do not copy from memory):
- The five duties, quoted from the CORE (confirm anchor `grep -n "Every dispatch stub" "orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md"`):
  1. Every dispatch stub's first line is `<repo> agent. Fetch your work order from the orchestrator branch:` (the dispatch stub standard, v4.9.0; supersedes the v4.5 agent-addressing form).
  2. Publish / verify state commits use the guarded publish / verify form shipped in this prompt (no unguarded push-and-assume).
  3. The materialized prompt file's sha256 matches the tracker anchor (the Initialization spec record law, mechanically verified).
  4. Every trigger-phrase fire has a run-log entry (where the repo keeps a run log; repos without one declare in the project state under a declared line instead of silently dropping entries).
  5. The orchestrator branch receives no merges — distribution only.
- The boundary statement, quoted from the CORE (confirm anchor `grep -n "covers ONLY this checkable subset"`): "this mechanical check covers ONLY this checkable subset; a failing check blocks the release/boot that invoked it, exit non-zero. Judgment duties — plan quality, advice honesty, verdict soundness — are NOT machine-checkable and stay with review lanes and adversarial audits. A checker that pretends to verify everything is worse than one that honestly verifies the mechanical half."
- The governing file is `orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md`, sha256 `37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52` — anchored in `docs/PROJECT_STATE.md` §2 bullet 1. Confirm: `sha256sum` on the file AND `grep -n "37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52" docs/PROJECT_STATE.md` — both hit, else HALT AND REPORT.
- The orchestrator branch is `arena/01a0cb00-docsheet` (distribution only; never merges; carries only `.orchestrator/prompts/*` and `.orchestrator/local/ORCHESTRATOR_STATE.md`).
- Arena coding sessions are BRANCH-LOCKED to their provisioned `arena/*` branch (field-reported via PR #75's Session Irregularities): you are on your session branch; do not create or attempt to push any other feature branch. The fallback branch name in §8 applies only if your environment is provably not branch-locked.
- The tracker's tracker §2 workflows invariant forbids any `.github/workflows/*` change — this task must NOT need one (see §6: the gate enters CI through the existing `python -m unittest discover tests` step).
- `tests/*` and `tests/test_style_contrast.py` are omitted from the coverage denominator (`.coveragerc`) — adding a test file does not change the reported coverage percentage's denominator.
- Current suite count is `158` (confirm: `python -m unittest discover tests 2>&1 | tail -3` shows `Ran 158 tests` in a dependency-complete environment; if your sandbox lacks pandas, count via `grep -c "def test_" tests/*.py` for the pre-existing total and re-derive after adding yours, then let CI confirm — and record the limitation in the PR).

Architectural invariants this task must respect:
- Research byte-freeze; scoreboard stays dismantled; generated artifacts never hand-edited; delivery contract untouched (no frontend files).
- `.github/workflows/*` change only on explicit owner instruction — NOT instructed here; zero workflow edits.
- The gate must be deterministic and repo-idiomatic: plain `unittest`, no new dependencies, no browser, no test-framework changes.
- Agents never push to the orchestrator branch; the orchestrator never opens PRs absent express per-PR authorization.

Scope boundaries (this PR must NOT):
- Must NOT touch `.github/**`, `docs/app.js`, `docs/js/**`, `docs/index.html`, `docs/style.css`, any `docs/*.json`, `data/**`, generators, `pipeline/**`, `requirements*`, `package.json`, `orchestrator/**`, `archive/**`, `docs/audits/**`, or the retired stubs `AGENTS.md` / `NEXT_AGENT_HANDOFF.md` (task 004 owns those).
- Must NOT create tags, releases, or any branch other than your session branch.
- Must NOT weaken or skip duties to make them pass: no `skipTest` without a documented, environment-specific reason; duty 3 must genuinely recompute sha256.

5. CORE OBJECTIVE

A single PR that (a) adds `tests/test_orchestrator_gate.py` — discovered by the existing suite — mechanically covering all five duties fail-closed, with the boundary statement in the module header; (b) adds the two tracker declaration bullets in §6 that duties 1 and 4 check against; (c) advances the tracker's Immediate Next Task to task 004; (d) updates the test-count house-rule lines in `README.md` and `INSTRUCTIONS.md`.
Done criteria: `python -m unittest discover tests` includes the gate tests and passes in CI; every duty maps to at least one executed assertion (mapping table in the module docstring); mutating any guarded fact (anchor sha, declaration line, CORE file byte) makes the gate fail — verify this with a temporary local mutation and REVERT it (record the mutation evidence in the PR description); PR open with §15 description.

6. EXACT DELIVERABLES

Create: `tests/test_orchestrator_gate.py` with:
- A module docstring that contains, verbatim, (i) the boundary statement quoted in §4, and (ii) a duty→check mapping table covering duties 1–5. Example shape (adapt names, keep completeness):
  ```
  Duty 1 (stub first line) -> asserts the golden first-line string is declared in docs/PROJECT_STATE.md §2 and appears in the CORE's dispatch-stub standard section
  Duty 2 (guarded publish) -> asserts the CORE file contains the guarded-publish form markers (ls-remote --exit-code probe, staged-path allowlist guard, both merge-base --is-ancestor directions) AND that docs/PROJECT_STATE.md §2 declares the guarded publish/verify form invariant
  Duty 3 (anchor sha256)   -> recomputes sha256 of the CORE file and compares it to the anchor parsed from docs/PROJECT_STATE.md §2
  Duty 4 (run-log entry)   -> asserts the run-log declared line exists in docs/PROJECT_STATE.md §2 (repos without an in-tree run log declare it here; entries themselves live in .orchestrator/local/ORCHESTRATOR_STATE.md ## Run Log on the orchestrator branch)
  Duty 5 (no orch merges)  -> fetches arena/01a0cb00-docsheet at bounded depth and asserts zero merge commits (rev-list --min-parents=2); network-unreachable → loud skip ONLY via the documented ORCH_GATE_OFFLINE=1 escape hatch, otherwise fail
  ```
  (Your table may rephrase but must name duty, file anchor, and assertion for all five.)
- Test methods: at minimum one TestCase per duty (5+), each with a failure message that names the duty and the remediation (e.g., "Duty 3: CORE sha256 mismatch — re-materialize from the owner channel and re-record the tracker anchor").
- Duty-3 parsing: extract the 64-hex anchor from the tracker §2 CORE-anchor bullet (regex), assert exactly one candidate, `hashlib.sha256` the CORE file bytes, exact match.
- Duty-5 mechanics: run git through `subprocess` with a short timeout; fetch into a throwaway ref (e.g., `refs/remotes/origin/_orch_gate_check` — never move `HEAD`, never touch the working tree); default = perform the check (CI has network); `ORCH_GATE_OFFLINE=1` = `unittest.skip` with an explicit reason naming the env var; any other git/network error = FAIL (fail-closed), not skip.
- No new dependencies (stdlib only: `hashlib`, `re`, `subprocess`, `pathlib`, `unittest`, `os`).

Modify: `docs/PROJECT_STATE.md` — three edits, byte-exact.

Edit 1 — insert TWO new bullets IMMEDIATELY AFTER this literal line (confirm with `grep -n "defunct with the scoreboard" docs/PROJECT_STATE.md` — exactly one hit — and take the line's bytes from that grep output as the old side; the line must remain, unchanged, as the anchor):

```
- `.github/workflows/*` change only on explicit owner instruction. The former `.scoreboard/manual-workflow-edits.md` tracking path is defunct with the scoreboard; any pending manual workflow edit must be raised with the owner before dispatch.
```

Insert after it (old side = the literal line above; new side = that line followed by these two bullets):

```
- `.github/workflows/*` change only on explicit owner instruction. The former `.scoreboard/manual-workflow-edits.md` tracking path is defunct with the scoreboard; any pending manual workflow edit must be raised with the owner before dispatch.
- **Run-log declaration (CORE duty 4):** trigger-phrase fires ("handoff", "timeout", "new orchestrator", plus milestone re-grounding runs) append a dated entry to `## Run Log` in `.orchestrator/local/ORCHESTRATOR_STATE.md` on the orchestrator branch — entries are never silently dropped; this declared line is what `tests/test_orchestrator_gate.py` verifies on `main`.
- **Dispatch-stub first line (CORE duty 1):** every dispatch stub's first line is exactly `<repo> agent. Fetch your work order from the orchestrator branch:` where `<repo>` is the name part of `git remote get-url origin` (here: `docsheet`).
```

Edit 2 — replace this literal line (anchor `grep -n "Immediate Next Task" docs/PROJECT_STATE.md`, exactly one hit; take the line's bytes from the grep output as the old side — do not trust this rendering over the grep):

```
- **Immediate Next Task:** Orchestrator behavior gate — repo-adaptive mechanical check covering the five CORE duties (dispatch-stub first line, guarded publish/verify form, CORE anchor sha256 match, trigger-phrase run-log entry, no merges to the orchestrator branch), with an explicit boundary statement that judgment duties stay with review lanes; then handoff-pointer hygiene (`AGENTS.md`, `NEXT_AGENT_HANDOFF.md`, `orchestrator/prompts/README.md`, `.gitignore` recovery-dir line).
```

with:

```
- **Immediate Next Task:** Handoff-pointer hygiene — reconcile the retired `AGENTS.md` / `NEXT_AGENT_HANDOFF.md` stubs, the superseded `orchestrator/prompts/README.md` claims-on-main text, and add `.orchestrator/local/recovery/` to `.gitignore`; surface the root `0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch` placement question to the owner at that hand-back.
```

Edit 3 — none; all other tracker lines (vision, invariants other than the two inserts, settled decisions, milestone, current state) stay byte-identical.

Modify: `README.md` — test-count house rule: update the quick-start comment line (`python -m unittest discover tests  # 158 tests, no browser/network needs` — confirm current text with `grep -n "158" README.md`, use grep bytes) and any other `158` count in `README.md` to the NEW total (count = number of tests in your final suite run; if environment-blocked, count `grep -rc "def test_" tests/` style methods and adjust for subTests honestly, and say in the PR how you derived it). Note: the new gate test may require network — where the README/INSTRUCTIONS promise "no browser/network needed", amend that phrase minimally to keep the claim true (e.g., note the orchestrator gate's bounded fetch and its `ORCH_GATE_OFFLINE=1` escape hatch). Confirm current phrase first: `grep -n "no browser/network" README.md INSTRUCTIONS.md`.

Modify: `INSTRUCTIONS.md` — same house rule: update every `158` suite count and the same no-browser/network phrase per the grep above (the house-rule drift line in INSTRUCTIONS lists historical counts — append the new total the same way the pattern shows, if that is how the line is maintained; mirror whatever structure grep reveals, and describe any judgment call in the PR).

Do NOT touch anything else.

7. SUB-TASK BREAKDOWN AND CHECKPOINTS

1. Sync per §8; run every §4/§6 confirmation grep + `sha256sum` — any mismatch HALT AND REPORT (no push yet).
2. Create `tests/test_orchestrator_gate.py` with docstring, mapping table, five duty tests → commit + push
3. Apply the two tracker inserts + Immediate Next Task replacement → commit + push
4. Recount the suite; update `README.md` + `INSTRUCTIONS.md` count/network lines → commit + push
5. Run §14 battery including the mutation drill (mutate → see gate fail → revert → gate green) → commit + push
6. Open ONE pull request against `main` with the §15 description.

8. BRANCH AND TARGET

Base branch: `main` — never the orchestrator branch.
Target branch: **your provisioned session branch** (you are already on it — Arena sessions are branch-locked to `arena/<id>-docsheet`; do NOT create or switch to any other branch).
Orchestrator branch: `arena/01a0cb00-docsheet` — fetch source only (note: different session id from yours); never a base or target; never push to it.
Dependencies: none. Tasks 001 (#74) and 002 (#75) are MERGED; you build on current `main`.
Before the first checkpoint, align HEAD to the remote tip of YOUR session branch (being on a branch named X is not evidence it is the remote X):

use `git fetch --depth 50 origin +<your-session-branch>:refs/remotes/origin/_resume && git checkout -B <your-session-branch> refs/remotes/origin/_resume`

If that fetch cannot find the remote ref — you are in a non-Arena, not-branch-locked environment — the fallback branch is `docs/orchestrator-behavior-gate`, created from main:

use `git fetch --depth 1 origin +main:refs/remotes/origin/main && git checkout -B docs/orchestrator-behavior-gate origin/main`

Do not commit on `main`. "couldn't find remote ref" here is not an environment failure.

9. WORK PERSISTENCE AND PUSH CADENCE

Checkpoint after each sub-task in section 7, before any long or risky operation, and at the end. Your session can expire without warning; unpushed work is lost. Section 7 is your push schedule; there is no time-based rule.
A checkpoint is ONE command — first push, later pushes, and the nothing-to-push no-op are the same form (replace `<your-session-branch>` with your actual branch):

```
git add -A && (git diff --cached --quiet || git commit -qm "chore: wip <sub-task>") && git push -qu origin <your-session-branch>
```

Match the project's commit convention for the subject (`chore: wip <sub-task>` is a valid fallback). Open ONE pull request at the end, when quality checks pass. Do not open a draft PR first. Checkpoint commits may be broken. Never commit secrets. Never push to the orchestrator branch.
Sync rule: rebase onto `origin/main` ONLY before your first push. After the first push, integrate with `git fetch --depth 50 origin +main:refs/remotes/origin/main && git merge --no-edit origin/main` then `git push origin HEAD`. Never force-push unless explicitly instructed, and then only with `--force-with-lease`. On merge conflict: halt and report the conflicting files. Same for "refusing to merge unrelated histories" — never pass `--allow-unrelated-histories`.
If a push or fetch fails with an authentication or network error, report it plainly and keep working locally; retry at the next checkpoint. Never claim work is pushed while a push has failed; never modify credentials, remotes, or git config. A non-fast-forward rejection is a halt: report it raw; do not `git pull`; do not force-push.

10. TECHNICAL REQUIREMENTS

- Plain Python `unittest`, stdlib only; mirror the style of `tests/test_pipeline.py` (class-based `TestCase`, assertion messages that teach).
- Tests discover under the existing `python -m unittest discover tests` command (file name starts with `test_`).
- No new dependencies, no pytest, no workflow edits, no Makefile.
- The gate must pass on current `main` content as-is (it does: anchor correct, declarations about to be added by this same PR — order your commits so the final state is green; intermediate checkpoint commits may be red).
- TEST_COMMAND: `python -m unittest discover tests` — all tests pass (158 + your new count), including every gate duty test.
- INTEGRATION_TEST_COMMAND: not applicable — no component/persistence/API/queue/config/deployment boundary beyond the bounded git fetch inside duty 5 (which is part of the focused tests themselves).
- FULL_SUITE_COMMAND: `python -m unittest discover tests && npm run lint` — risk-based: full Python suite + lint; Playwright e2e skipped locally (zero JS/HTML/CSS/data changes; CI runs it) — record reason.
- COVERAGE_COMMAND: `coverage run -m unittest discover tests && coverage report` — floor 85%, expect ~unchanged (tests omitted from denominator).
- MUTATION_TEST_COMMAND: the §5 mutation drill IS the required mutation evidence (anchor/declaration/CORE-byte perturbation must fail the gate; revert afterwards). Full mutation frameworks not warranted.
- LINT_COMMAND: `npm run lint` — zero errors (unchanged frontend).
- BUILD_COMMAND: not applicable — no build step.

11. SAFETY AND COMPATIBILITY RULES

- Must NOT break: the existing 158 tests, any `--check` gate, the delivery contract, CI on `main`.
- Must NOT change: workflows, code, data, generated JSON, frontend, requirements, package manifests.
- Duty-5 git operations: read-only fetch to a namespaced throwaway ref; never `push`, never `reset`, never move `HEAD`, never write tracked files; clean up the throwaway ref afterwards (best effort).
- The escape hatch env var defaults UNSET (gate runs); only explicit `ORCH_GATE_OFFLINE=1` skips duty 5, loudly.
- Offline/local promise in docs must stay truthful after your edit (amend the phrase, don't delete the suite's determinism claim for the other tests).
- No migrations; nothing user-facing on the live site changes.

12. CLEANUP RULES

By the final push: no commented-out code, temporary debug logs, ad-hoc scripts, leftover mutation artifacts (the drill must be fully reverted — `git diff main` shows only the §6 deliverables), no TODO markers. Do not commit the fetched prompt file or anything in /tmp. Checkpoint commits exempt — clean once before the PR.

13. STRICT BOUNDARIES / OUT OF SCOPE

- Do not push to the orchestrator branch `arena/01a0cb00-docsheet`; do not create tags or releases; one PR only.
- Do not edit `.github/**` (workflows OR the PR template), `AGENTS.md`, `NEXT_AGENT_HANDOFF.md`, `orchestrator/prompts/README.md`, `README` sections beyond the count/network lines, or anything outside §6.
- Do not implement duties partially "for later": all five land now, fail-closed, with the boundary statement.
- Do not add network calls anywhere except duty 5's bounded fetch.
- Do not weaken existing tests or lower any threshold (`.coveragerc` floor stays 85).
- Artifacts: none; if one appears, path + sha256 into the PR description and stop.

14. QUALITY CHECKS

Run and record (expected outcome in parentheses):
- `sha256sum "orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md"` (equals the tracker anchor)
- `grep -c "defunct with the scoreboard" docs/PROJECT_STATE.md` (1 after your edit — anchor line preserved)
- `grep -n "Run-log declaration (CORE duty 4)" docs/PROJECT_STATE.md` (1 hit)
- `grep -n "Dispatch-stub first line (CORE duty 1)" docs/PROJECT_STATE.md` (1 hit)
- `grep -n "Immediate Next Task" docs/PROJECT_STATE.md` (1 line, naming Handoff-pointer hygiene)
- `python -m unittest discover tests` (all pass; includes `test_orchestrator_gate`; record final count)
- Mutation drill: (a) append one byte to a copy of the CORE file / point the test at a tampered path — duty 3 fails with the Duty-3 message; (b) delete the run-log declared line temporarily — duty 4 fails; (c) revert both — suite green. Record transcripts' short outputs in the PR. Never leave the tamper in the committed tree.
- `coverage run -m unittest discover tests && coverage report` (pass, ≥85%)
- `npm run lint` (zero errors)
- `git diff main --stat` (exactly: `tests/test_orchestrator_gate.py`, `docs/PROJECT_STATE.md`, `README.md`, `INSTRUCTIONS.md`)
- Confirm: work pushed, `git status` clean.

15. PR DESCRIPTION REQUIREMENTS

Title: same as the work order's first line.
Body must contain:
- **Summary** — what and why (mechanical five-duty gate; declarations; count housekeeping).
- **Design rationale** — why a unittest stage instead of a workflow (workflows need explicit owner instruction, none given; the existing suite already runs in CI → gate inherits CI for free); why duty 5 is the only network check and how fail-closed vs `ORCH_GATE_OFFLINE=1` semantics work; why duties 1–4 are tree/declaration checks; where the boundary statement lives.
- **Duty coverage table** — duty → test method → assertion (mirrors the docstring).
- **Test results** — every §14 command + mutation-drill evidence; final suite count; skips and reasons (must be none except documented offline hatch used or not).
- **Breaking changes / migration notes** — none; note the docs phrase amendment for network truthfulness.
- Claim-scope: every file named appears in the changed-file list.
- `#### Session Irregularities` per §16.

16. HARDENING REPORT — Session Irregularities

Under heading `#### Session Irregularities`: if none significant (threshold: interfered with the prompt AND cost >~10 min / blocked progress / required workaround AND reveals a recurring invariant or blind spot), write `None significant`. Otherwise one row per item: `Category | Symptom | Impact | Workaround | Hardening candidate` (3–6 lines). Branch-lock friction should NOT be reported again if you simply used your session branch as §8 now instructs — that fix is already folded in; report only what still bites. No padding with trivial retries or expected platform behavior.
