Complete handoff-pointer hygiene and archive the init patch

0. FETCH AND VERIFY

use `git fetch --depth 1 origin +arena/01a0cb00-docsheet:refs/remotes/origin/_orch && git show refs/remotes/origin/_orch:.orchestrator/prompts/004-handoff-pointer-hygiene.md > /tmp/task.md`

Read this file from /tmp/task.md. Do NOT use `origin/arena/01a0cb00-docsheet` (single-branch clones do not create it). Do NOT use `FETCH_HEAD` (the next fetch of main overwrites it). Do NOT `git checkout` or `git show` orchestrator paths into your worktree. Write outside the repository; never commit this file; never push to the orchestrator branch `arena/01a0cb00-docsheet`.
Halt conditions: if /tmp/task.md is empty, or if `head -1 /tmp/task.md` does not equal the Expected title below, stop and report — do not improvise. If this stub and the fetched file disagree, the fetched file wins.
If GitHub auth fails mid-session with HTTP 401/403 "Bad credentials", that is a known sandbox issue: checkpoint locally first, then ask the operator via `ask_user` with the option "I reconnected GitHub — retry now" (plus one neutral alternative, custom answer enabled). Ask at most once per expiry event. Never improvise credentials, remotes, or git config.

1. TASK TITLE AND SCOPE

Finish the maintenance queue: turn the retired `AGENTS.md` / `NEXT_AGENT_HANDOFF.md` stubs and the superseded `orchestrator/prompts/README.md` into honest redirects, fix the stale handoff pointers in `README.md` / `INSTRUCTIONS.md`, add the orchestrator recovery dir to `.gitignore`, advance the canonical tracker (milestone, 158→166 count, next task), and move the root init patch into `archive/` (owner ruling 2026-09-22).
Complete this in ONE pull request.

2. REQUIRED READING ORDER

1. `docs/PROJECT_STATE.md` — canonical tracker; §2 is OFF LIMITS (the behavior gate pins bytes there — see §4); §4 holds the three lines you edit.
2. `AGENTS.md`, `NEXT_AGENT_HANDOFF.md` — the two retired stubs you re-point (note: both wrongly say `CORE v4.9.0`; the governing version is v4.9.1).
3. `orchestrator/prompts/README.md` — superseded claims-on-main text you correct.
4. `README.md` lines anchored by `grep -n "NEXT_AGENT_HANDOFF" README.md` (two hits at last refresh: docs-layout row ~118, open-work pointer ~199) and `INSTRUCTIONS.md` line anchored by `grep -n "NEXT_AGENT_HANDOFF" INSTRUCTIONS.md` (one hit ~173).
5. `.gitignore` — insertion point for the recovery-dir line.
Not required: CORE prompt file beyond what §4 inlines; `archive/`; `docs/audits/`; `tests/`; frontend; generators.

3. PROJECT CONTEXT AND OWNER VISION

Tasks 001–003 (PRs #74, #75, #76) landed the canonical tracker + CORE v4.9.1 anchor, finished scoreboard dismantling, and put the five-duty behavior gate into CI. This is the fourth and final maintenance task of the owner-approved sequence; afterwards the queue opens to owner-directed product/research work (owner: "We'll do research after we cleaned up the maintenance stuff.").
Owner Vision Context: pointer hygiene is what makes the next agent — human or sandboxed — find current state on `main` instead of retired stubs; the init-patch move keeps the root clean per the owner's explicit placement ruling.

4. CONFIRMED FACTS, ARCHITECTURAL INVARIANTS, AND SCOPE BOUNDARIES

Confirmed facts (verify; do not copy from memory — every old-side block below was captured from `main` @ `923ba55` this session, re-grep before editing and prefer the grep output's bytes):
- `grep -c "Run-log declaration (CORE duty 4)\|Dispatch-stub first line (CORE duty 1)" docs/PROJECT_STATE.md` → `2`. **§2 of the tracker MUST remain byte-identical** — `tests/test_orchestrator_gate.py` duties 1–4 pin those bytes; any §2 edit fails CI (fail-closed). This PR touches only §4 of the tracker.
- Both stubs currently claim `CORE v4.9.0`; governing version is v4.9.1 (`sha256sum` of the CORE file must equal the §2 anchor — run it, HALT on mismatch).
- `orchestrator/prompts/README.md` currently reads exactly (confirm `git show origin/main:orchestrator/prompts/README.md`): `Task prompts for the docsheet orchestrator live here; dispatch stubs fetch from this path (v4.9.0 canon standard).` — superseded by the owner's 2026-09-22 structured ruling: distribution = `.orchestrator/prompts/` on orchestrator branch `arena/01a0cb00-docsheet`.
- `.gitignore` has no `.orchestrator/` entry (recovery overlay currently untracked-by-design but undeclared).
- Owner ruling, verbatim: the root init patch moves to `archive/` (structured answer 2026-09-22: "Move to archive/").
- Arena sessions are branch-locked to their provisioned `arena/*` branch; §8 tells you to stay on it.
- Suite count on `main` is 166 (confirm `grep -rn "166 deterministic\|166 tests" README.md INSTRUCTIONS.md` — PR #76 applied the house rule; the tracker's §4 line still wrongly says 158 — that is one of your edits).

Architectural invariants this task must respect:
- **Do not modify `docs/PROJECT_STATE.md` §2, §1, §3 at all** — only the three §4 lines in §6 (the gate's duty 1/2/4 assertions read §2; duty 3 reads the CORE anchor bullet).
- Research byte-freeze; scoreboard stays dismantled; no new `.scoreboard/` paths; no `.github/**` changes (workflows forbidden — and the PR template is already clean).
- Delivery contract untouched; no frontend/data/generated-JSON/code/test changes.
- The behavior gate must stay green: after your edits, `python -m unittest tests.test_orchestrator_gate` passes (8 tests).
- Agents never push to the orchestrator branch; the orchestrator never opens PRs absent express per-PR authorization.

Scope boundaries (this PR must NOT):
- Must NOT touch: `.github/**`, `tests/**`, `docs/app.js`, `docs/js/**`, `docs/index.html`, `docs/style.css`, `docs/*.json`, `data/**`, generators, `pipeline/**`, requirements, `package.json`, `orchestrator/INIT-RECORD.md`, `orchestrator/ORCHESTRATOR CORE*`, `archive/` contents (except RECEIVING the moved patch), `docs/audits/**`, `review/**`, `decisions/**`.
- Must NOT delete `AGENTS.md` or `NEXT_AGENT_HANDOFF.md` (README and external links land on them — they become redirects, not corpses).
- Must NOT remove the HTML comment block inside `NEXT_AGENT_HANDOFF.md`.
- Must NOT touch tracker §2 (see above) or invent new sections.
- Must NOT create tags, releases, or any branch other than your session branch.

5. CORE OBJECTIVE

A single PR where: every current-file pointer to retired handoff state resolves to `docs/PROJECT_STATE.md`; the two stubs and the prompts README tell the truth (v4.9.1, owner-confirmed distribution shape); `.gitignore` declares the recovery overlay; the tracker §4 reflects post-004 reality (maintenance complete, 166 tests, next = owner-directed work); the init patch lives in `archive/`.
Done criteria: `grep -rn "NEXT_AGENT_HANDOFF" README.md INSTRUCTIONS.md` shows only tracker-resolving pointers (or zero stale promises of "open work / risk / roadmap" from the stub); the gate's 8 tests pass; PR open with §15 description.

6. EXACT DELIVERABLES

Replace `AGENTS.md` ENTIRELY with (old side = current 3-line file, confirm bytes first):

```
# AGENTS.md

Agent governance for this repository has moved to `orchestrator/` (CORE v4.9.1); this file is a retired redirect (was: instructions and protocol for sandboxed agents). Current state, owner vision, scope boundaries, and the task queue live in [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md).
```

Replace `NEXT_AGENT_HANDOFF.md` ENTIRELY with the following — keeping the existing HTML comment block verbatim BELOW it (old side = current file; new side = header lines + unchanged comment):

```
# NEXT_AGENT_HANDOFF.md

Agent governance for this repository has moved to `orchestrator/` (CORE v4.9.1); this file is a retired redirect (was: deep pipeline, data rules, and risk handoff for subsequent agents). Current state, open work, risk, and the immediate next task live in [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md).

<!--
...existing comment block stays byte-identical...
-->
```

(The comment block: copy the file's current `<!-- ... -->` section unchanged — do not edit its contents.)

Replace `orchestrator/prompts/README.md` ENTIRELY with (old side = the single line quoted in §4):

```
Task prompts for the docsheet orchestrator live on the orchestrator branch at `.orchestrator/prompts/` (owner-confirmed distribution shape 2026-09-22, CORE v4.9.1 branch model; dispatch stubs fetch `arena/01a0cb00-docsheet` into `refs/remotes/origin/_orch`). This directory is retained as init-era lineage from the superseded "Governing Shape" note in `orchestrator/INIT-RECORD.md`; no new prompts are published here.
```

Modify `.gitignore` — insert this block between the `data/veritas_inventory_diff.patch` line and the `# OS / editor` line (old side, literal from `main`):

```
data/veritas_inventory_diff.patch

# OS / editor
```

new side:

```
data/veritas_inventory_diff.patch

# Orchestrator local recovery overlay (guarded-publish recovery aid; never staged)
.orchestrator/local/recovery/

# OS / editor
```

Modify `docs/PROJECT_STATE.md` §4 ONLY — three line replacements. Old sides, literal from `main` (re-grep; prefer grep bytes if any character differs from this rendering):

Line A (Active Milestone) — old:

```
- **Active Milestone:** Maintenance & governance hardening — tracker/anchor bootstrap, scoreboard remnants, orchestrator behavior gate, handoff-pointer hygiene — before any research or feature work.
```

new:

```
- **Active Milestone:** Maintenance & governance hardening — COMPLETE with this PR (001 tracker+anchor #74, 002 scoreboard remnants #75, 003 behavior gate #76, 004 pointer hygiene); next phase is owner-directed product/research work.
```

Line B (Current State) — old:

```
- **Current State:** 363-record curated catalogue; six generator `--check` gates green in CI; 158 Python tests at 92% coverage (floor 85 in `.coveragerc`); 9 Node unit tests; ESLint + Playwright e2e in CI; declared-current audit `docs/audits/2026-08-10-arena-019febe9-full-audit.md` (healthy / conditional pass, 8.1/10). Orchestrator initialized at CORE v4.9.1; this tracker is the first governance artifact on `main`.
```

new:

```
- **Current State:** 363-record curated catalogue; six generator `--check` gates green in CI; 166 Python tests at 92% coverage (floor 85 in `.coveragerc`, suite includes the five-duty orchestrator behavior gate `tests/test_orchestrator_gate.py`); 9 Node unit tests; ESLint + Playwright e2e in CI; declared-current audit `docs/audits/2026-08-10-arena-019febe9-full-audit.md` (healthy / conditional pass, 8.1/10). Orchestrator initialized at CORE v4.9.1; this tracker is the canonical project state on `main`.
```

Line C (Immediate Next Task) — old:

```
- **Immediate Next Task:** Handoff-pointer hygiene — reconcile the retired `AGENTS.md` / `NEXT_AGENT_HANDOFF.md` stubs, the superseded `orchestrator/prompts/README.md` claims-on-main text, and add `.orchestrator/local/recovery/` to `.gitignore`; surface the root `0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch` placement question to the owner at that hand-back.
```

new:

```
- **Immediate Next Task:** Open the owner-directed phase — the maintenance queue is complete (001–004); the owner picks the first product/research work order (owner ruling 2026-09-22: research follows maintenance).
```

Modify `README.md` — two pointer edits (old sides from `grep -n` / `sed -n '<n>p'` on `main`; prefer grep bytes):
1. After the docs-layout row `| Root (essential) | \`README\`, \`INSTRUCTIONS\`, \`AGENTS\`, \`NEXT_AGENT_HANDOFF\`, \`RECONCILIATION_REPORT\` (generated) |` insert a new row immediately below:
   `| Canonical tracker | \`docs/PROJECT_STATE.md\` — owner vision, invariants, settled decisions, active milestone & queue |`
2. On the line containing `[NEXT_AGENT_HANDOFF.md](NEXT_AGENT_HANDOFF.md)` (anchor `grep -n "NEXT_AGENT_HANDOFF" README.md`), take the full line via `sed -n '<n>p'` and replace the link+purpose so it reads (keeping the rest of the line byte-identical):
   `[docs/PROJECT_STATE.md](docs/PROJECT_STATE.md) for the current queue and open work`
   i.e., the stale handoff link becomes the tracker link with the same "for open work" role.

Modify `INSTRUCTIONS.md` — one pointer edit: on the line containing `` `NEXT_AGENT_HANDOFF.md` §6 `` (anchor `grep -n "NEXT_AGENT_HANDOFF" INSTRUCTIONS.md`), take the full line and replace `` `NEXT_AGENT_HANDOFF.md` §6 `` with `` `docs/PROJECT_STATE.md` `` so the sentence promises current risk/roadmap from the tracker (keep the rest of the line byte-identical).

Move (owner ruling 2026-09-22: "Move to archive/"):

```
git mv 0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch archive/0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch
```

then `grep -rn "0001-Init-v4.9.0" --exclude-dir=.git .` — any CURRENT-file hit outside `archive/` must be updated to the new path (the tracker's old Line C mention disappears via the replacement above; `archive/` files that mention it historically stay untouched). If `archive/README.md` carries a file inventory section (check first), add one line naming the moved patch; otherwise skip that file and say so in the PR.

7. SUB-TASK BREAKDOWN AND CHECKPOINTS

1. Sync per §8; run every §4/§6 confirmation grep + `sha256sum` — mismatch ⇒ HALT (no push yet).
2. Rewrite `AGENTS.md` + `NEXT_AGENT_HANDOFF.md` redirects → commit + push
3. Rewrite `orchestrator/prompts/README.md` + `.gitignore` insert → commit + push
4. Apply the three tracker §4 line replacements (nothing else in the file) → commit + push
5. Apply README + INSTRUCTIONS pointer edits; `git mv` the init patch + reference sweep → commit + push
6. Run §14 battery (gate must be 8/8) → commit + push
7. Open ONE pull request against `main` with the §15 description.

8. BRANCH AND TARGET

Base branch: `main` — never the orchestrator branch.
Target branch: **your provisioned session branch** (Arena sessions are branch-locked to `arena/<id>-docsheet`; do NOT create or switch branches).
Orchestrator branch: `arena/01a0cb00-docsheet` — fetch source only (different session id from yours); never a base or target; never push to it.
Dependencies: none. PRs #74/#75/#76 are MERGED; build on current `main` (`923ba55` at authoring — refresh first).
Before the first checkpoint, align HEAD:

use `git fetch --depth 50 origin +<your-session-branch>:refs/remotes/origin/_resume && git checkout -B <your-session-branch> refs/remotes/origin/_resume`

If that fetch cannot find the remote ref — non-Arena, not branch-locked — fallback branch `docs/handoff-pointer-hygiene` from main:

use `git fetch --depth 1 origin +main:refs/remotes/origin/main && git checkout -B docs/handoff-pointer-hygiene origin/main`

Do not commit on `main`. "couldn't find remote ref" here is not an environment failure.

9. WORK PERSISTENCE AND PUSH CADENCE

Checkpoint after each sub-task in section 7, before any long or risky operation, and at the end. Your session can expire without warning; unpushed work is lost. Section 7 is your push schedule; there is no time-based rule.
A checkpoint is ONE command (replace `<your-session-branch>` with your actual branch):

```
git add -A && (git diff --cached --quiet || git commit -qm "chore: wip <sub-task>") && git push -qu origin <your-session-branch>
```

Match the project's commit convention for the subject (`chore: wip <sub-task>` is a valid fallback). Open ONE pull request at the end, when quality checks pass. Do not open a draft PR first. Checkpoint commits may be broken. Never commit secrets. Never push to the orchestrator branch.
Sync rule: rebase onto `origin/main` ONLY before your first push. After the first push, integrate with `git fetch --depth 50 origin +main:refs/remotes/origin/main && git merge --no-edit origin/main` then `git push origin HEAD`. Never force-push unless explicitly instructed, and then only with `--force-with-lease`. On merge conflict: halt and report the conflicting files. Same for "refusing to merge unrelated histories" — never pass `--allow-unrelated-histories`.
If a push or fetch fails with an authentication or network error, report it plainly and keep working locally; retry at the next checkpoint. Never claim work is pushed while a push has failed; never modify credentials, remotes, or git config. A non-fast-forward rejection is a halt: report it raw; do not `git pull`; do not force-push.

10. TECHNICAL REQUIREMENTS

- Documentation/config-only: Markdown redirects/pointers, one `.gitignore` block, one `git mv`. No code, no YAML, no JSON.
- Byte-fidelity: tracker §4 replacements exactly as specified (after grep re-confirmation); HTML comment in the handoff stub preserved; §2 untouched.
- TEST_COMMAND: `python -m unittest tests.test_orchestrator_gate -v` — 8 tests, all pass (your edits must not disturb §2/CORE).
- INTEGRATION_TEST_COMMAND: `python -m unittest discover tests` — full suite passes (166; same environmental caveat as before: sandbox may lack pandas — record and rely on CI if so).
- FULL_SUITE_COMMAND: `python -m unittest discover tests && npm run lint` — risk-based; Playwright e2e skipped locally (zero JS/HTML/CSS/data changes; CI runs it) — record reason.
- COVERAGE_COMMAND: `coverage run -m unittest discover tests && coverage report` — floor 85%, expect 92%.
- MUTATION_TEST_COMMAND: not warranted — no production logic paths change.
- LINT_COMMAND: `npm run lint` — zero errors.
- BUILD_COMMAND: not applicable — no build step; generators not re-run.

11. SAFETY AND COMPATIBILITY RULES

- Must NOT break: the behavior gate (8/8), any `--check` gate, the delivery contract, existing 166 tests, CI on `main`, or inbound links that land on `AGENTS.md` / `NEXT_AGENT_HANDOFF.md` (they must resolve to working redirects, not 404s or empty files).
- Must NOT change: workflows, PR template, code, data, generated JSON, frontend, requirements, manifests, tracker §1–§3, INIT-RECORD, the CORE file.
- The patch move must be a pure rename (same blob — `git diff -M --stat` shows rename, content unchanged).
- No migrations; nothing user-facing on the live site changes (the moved patch is a repo file, not a Pages asset — `archive/` is outside `docs/`).

12. CLEANUP RULES

By the final push: no commented-out code, temporary logs, ad-hoc scripts, TODO markers; `grep -rn "NEXT_AGENT_HANDOFF" README.md INSTRUCTIONS.md` shows no stale open-work/risk promises; no leftover references to the root patch path in current files; `git status` clean. Do not commit the fetched prompt file or anything in /tmp.

13. STRICT BOUNDARIES / OUT OF SCOPE

- Do not push to the orchestrator branch `arena/01a0cb00-docsheet`; no tags; no releases; one PR only.
- Do not edit `.github/**`, `tests/**`, `docs/PROJECT_STATE.md` §1–§3, `orchestrator/INIT-RECORD.md`, the CORE file, `archive/*` files other than receiving the patch (and the optional one-line `archive/README.md` inventory note if that section exists), `docs/audits/**`, `review/**`, `decisions/**`, frontend, data, code.
- Do not delete the two stub files or the handoff HTML comment; do not "improve" prose beyond the exact replacements; do not add new tracker sections.
- Do not reintroduce any `.scoreboard/` path.
- Artifacts: none; if one appears, path + sha256 into the PR description and stop.

14. QUALITY CHECKS

Run and record (expected outcome in parentheses):
- `sha256sum "orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md"` (equals tracker §2 anchor)
- `grep -c "Run-log declaration (CORE duty 4)\|Dispatch-stub first line (CORE duty 1)" docs/PROJECT_STATE.md` (2 — §2 untouched)
- `python -m unittest tests.test_orchestrator_gate -v` (8 pass)
- `python -m unittest discover tests` (166 pass, or documented environmental caveat + CI reliance)
- `grep -n "CORE v4.9" AGENTS.md NEXT_AGENT_HANDOFF.md` (both say v4.9.1, not v4.9.0)
- `grep -n "docs/PROJECT_STATE.md" AGENTS.md NEXT_AGENT_HANDOFF.md orchestrator/prompts/README.md README.md INSTRUCTIONS.md` (redirects/pointers land on the tracker)
- `grep -n "NEXT_AGENT_HANDOFF" README.md INSTRUCTIONS.md` (remaining hits, if any, make no open-work/risk/roadmap promise — report what remains and why)
- `grep -n "\.orchestrator/local/recovery" .gitignore` (1 hit)
- `test -f archive/0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch && test ! -f 0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch` (moved)
- `grep -rn "0001-Init-v4.9.0" --exclude-dir=.git .` (no current-file hits outside `archive/` except unavoidable historical ones you list in the PR)
- `grep -n "Immediate Next Task\|Active Milestone\|166 Python tests" docs/PROJECT_STATE.md` (new §4 texts present)
- `git diff main -M --stat` (exactly: `AGENTS.md`, `NEXT_AGENT_HANDOFF.md`, `orchestrator/prompts/README.md`, `.gitignore`, `docs/PROJECT_STATE.md`, `README.md`, `INSTRUCTIONS.md`, rename `0001-Init-…patch` → `archive/0001-Init-…patch`, optional `archive/README.md`)
- `coverage run -m unittest discover tests && coverage report` (≥85%)
- `npm run lint` (zero errors)
- Confirm: work pushed, `git status` clean.

15. PR DESCRIPTION REQUIREMENTS

Title: same as the work order's first line.
Body must contain:
- **Summary** — what and why (pointer hygiene; owner-ruled patch move; tracker §4 advance).
- **Design rationale** — why redirects instead of deleting the stubs (inbound links); why §2 is untouched (gate pins bytes); why the patch moves to `archive/` (owner ruling 2026-09-22, quoted); how each pointer now resolves to the canonical tracker. Describe only this PR's changes.
- **Test results** — every §14 command + outcomes + skips/reasons.
- **Breaking changes / migration notes** — none; the rename is path-only; list any grep hits you intentionally left (historical).
- Claim-scope: every file named appears in the changed-file list.
- `#### Session Irregularities` per §16.

16. HARDENING REPORT — Session Irregularities

Under heading `#### Session Irregularities`: if none significant (threshold: interfered with the prompt AND cost >~10 min / blocked progress / required workaround AND reveals a recurring invariant or blind spot), write `None significant`. Otherwise one row: `Category | Symptom | Impact | Workaround | Hardening candidate` (3–6 lines). Branch-lock friction already fixed in §8 — report only what still bites. No padding with trivial retries or expected platform behavior.
