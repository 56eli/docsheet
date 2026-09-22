Bootstrap canonical tracker docs/PROJECT_STATE.md and record CORE v4.9.1 anchor

0. FETCH AND VERIFY

use `git fetch --depth 1 origin +arena/01a0cb00-docsheet:refs/remotes/origin/_orch && git show refs/remotes/origin/_orch:.orchestrator/prompts/001-bootstrap-project-state-tracker.md > /tmp/task.md`

Read this file from /tmp/task.md. Do NOT use `origin/arena/01a0cb00-docsheet` (single-branch clones do not create it). Do NOT use `FETCH_HEAD` (the next fetch of main overwrites it). Do NOT `git checkout` or `git show` orchestrator paths into your worktree. Write outside the repository; never commit this file; never push to the orchestrator branch `arena/01a0cb00-docsheet`.
Halt conditions: if /tmp/task.md is empty, or if `head -1 /tmp/task.md` does not equal the Expected title below, stop and report — do not improvise. If this stub and the fetched file disagree, the fetched file wins.
If GitHub auth fails mid-session with HTTP 401/403 "Bad credentials", that is a known sandbox issue: checkpoint locally first, then ask the operator via `ask_user` with the option "I reconnected GitHub — retry now" (plus one neutral alternative, custom answer enabled). Ask at most once per expiry event. Never improvise credentials, remotes, or git config.

1. TASK TITLE AND SCOPE

Bootstrap this repository's governance layer: create the canonical project tracker `docs/PROJECT_STATE.md` (Knowledge Bridge structure) and record the governing CORE v4.9.1 sha256 anchor in it, and correct the stale anchor row in `orchestrator/INIT-RECORD.md`.
Complete this in ONE pull request.

2. REQUIRED READING ORDER

1. `orchestrator/INIT-RECORD.md` — owner orders, init provenance, current (stale) anchor row you will correct.
2. `README.md` — project identity, owner vision material, documentation layout, current reviewed catalogue state (skim; do not read line-by-line).
3. `NEXT_AGENT_HANDOFF.md` and `AGENTS.md` — retired stubs; evidence that governance moved to `orchestrator/` and that no canonical tracker exists yet.
4. `.github/pull_request_template.md` — read only, for context on a known dead `.scoreboard/` reference. DO NOT EDIT IT IN THIS PR (queued as a separate task).
Not required reading: the CORE prompt file (`orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md`, 122 KB) — its applicable rules are inlined below. `archive/`, `docs/audits/`, `data/`, and generator scripts are out of scope.

3. PROJECT CONTEXT AND OWNER VISION

This repo is a governed research catalogue + GitHub Pages spreadsheet (363 curated master records) with a raw CSV pass-through lane, six generator `--check` gates, 158 Python tests at 92% coverage (floor 85), and an ESLint/Playwright CI. On 2026-09-22 the owner initialized Orchestrator CORE v4.9.1 (`orchestrator/INIT-RECORD.md`, PR #73 lineage) and then dismantled the scoreboard system.
Owner Vision Context: the owner wants orchestrator 4.9 functionality fully operational as soon as possible, with maintenance/governance cleanup completed BEFORE any research work ("We'll do research after we cleaned up the maintenance stuff."). This tracker is the first governance artifact every later task and audit will cite — it must exist before the behavior gate and cleanup tasks can be anchored.

4. CONFIRMED FACTS, ARCHITECTURAL INVARIANTS, AND SCOPE BOUNDARIES

Confirmed facts (treat as true without re-deriving):
- `docs/PROJECT_STATE.md` does NOT exist on `main` (verified 2026-09-22). There is no `STATUS.md`/`ROADMAP.md` equivalent either; `NEXT_AGENT_HANDOFF.md` is a retired stub. The resolved canonical tracker path for this repo is exactly `docs/PROJECT_STATE.md`.
- The governing prompt file is `orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md`. Confirm, do not copy: `sha256sum "orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md"` must print `37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52`. If it differs, HALT AND REPORT — do not write the anchor.
- The stale row in `orchestrator/INIT-RECORD.md` currently reads (confirm with grep, do not copy from memory):
  `- **CORE Specification SHA-256:** \`e33886acbd12448bd2f91ce477c8dd733a49d1fbf12f9bd96f96734433bc18da\` (\`orchestrator/ORCHESTRATOR CORE v4.9.0 — GENERAL PURPOSE.md\`)`
  (anchor string `grep -n "CORE Specification SHA-256" orchestrator/INIT-RECORD.md`)
- The v4.9.0 CORE file is NOT present on `main` (upgraded in place to v4.9.1); its historical sha is the e33886ac… value above. HUB `56eli/REPOTESTER` is presumed private; do not attempt to fetch it.
- Orchestrator distribution (owner-confirmed 2026-09-22 via structured question): prompts live at `.orchestrator/prompts/` and working state at `.orchestrator/local/ORCHESTRATOR_STATE.md` on orchestrator branch `arena/01a0cb00-docsheet`, which never merges. INIT-RECORD's "Governing Shape" line (`orchestrator/prompts/` on `main`) is superseded by this ruling — record the supersession in the tracker; do not edit that INIT-RECORD line (leave Governing Shape as historical text; the anchor-row edit below is the only INIT-RECORD change you make).
- Priority order (owner 2026-09-22): maintenance/governance cleanup first; research work only afterward.

Architectural invariants this task must respect and record for future agents:
- Research byte-freeze during the maintenance phase: `data/`, the schemas, and the research docs/outputs are not modified by maintenance tasks; research resumes only on explicit owner instruction.
- Scoreboard is dismantled ("it definitely has to go"); no `.scoreboard/` path may be reintroduced.
- Generated artifacts are never hand-edited: change reviewed inputs, rebuild via the generators, keep all six `--check` gates green.
- The frontend delivery contract stands: shipped asset/payload changes must refresh `docs/index.html` version IDs and `docs/build-manifest.json` in the same PR.
- Controlled vocabularies hold (`item_type` = content class, `format` = carrier; `audio`/`video` retired; master ids and catalogue codes never renumbered).
- Agents never push to the orchestrator branch; the orchestrator never opens PRs absent express per-PR authorization and never merges.

Scope boundaries (this PR must NOT):
- Must NOT touch `data/`, any `docs/*.json`, `docs/app.js`, `docs/js/`, `docs/index.html`, `docs/style.css`, `*.py`, `tests/`, `.github/workflows/`, `archive/`, `docs/audits/`, or `orchestrator/prompts/README.md`.
- Must NOT edit `.github/pull_request_template.md` (scoreboard remnant cleanup is the NEXT queued task, not this one).
- Must NOT create any tracker other than `docs/PROJECT_STATE.md`, and must NOT rename/repurpose `NEXT_AGENT_HANDOFF.md`.
- Must NOT create tags, releases, or additional branches beyond the single target branch below.

5. CORE OBJECTIVE

A single PR that (a) creates `docs/PROJECT_STATE.md` containing the four-section Knowledge Bridge structure with the exact content in section 6, including the CORE v4.9.1 sha256 anchor row, and (b) corrects the one stale anchor row in `orchestrator/INIT-RECORD.md` to point at the v4.9.1 file + sha while preserving the v4.9.0 value as historical lineage.
Done criteria: PR is open against `main`; `docs/PROJECT_STATE.md` exists byte-for-byte as specified (modulo nothing — use the exact text); `INIT-RECORD.md` contains the corrected anchor row; the Python suite still passes; the PR description includes the required sections (§15–16).

6. EXACT DELIVERABLES

Create: `docs/PROJECT_STATE.md` with EXACTLY this content:

```markdown
# Project State

Canonical project tracker.

## 1. Owner Vision & Scope Boundaries

- **Product Vision:** A governed, public live catalogue of the Hawkins/Veritas research archive: a byte-stable raw CSV lane rendered as a searchable GitHub Pages spreadsheet, plus a curated research master (363 records) with review workspaces, official-inventory intake lanes, and export/delivery-contract tooling — accurate, reproducible, and owner-ruled.
- **Scope Boundaries (Non-Goals):**
  - Research inputs and outputs (`data/`, the schemas, and the research docs/outputs) are **byte-frozen during the maintenance phase**. Owner direction 2026-09-22: "We'll do research after we cleaned up the maintenance stuff." Research work resumes only on explicit owner instruction.
  - The scoreboard system is dismantled (owner: "it definitely has to go") and must not be reintroduced; no new `.scoreboard/` paths may appear in current files.
  - No feature work, schema changes, or data edits land inside maintenance tasks.
  - `archive/` and superseded audits stay historical and non-normative; they are not rewritten.
  - Agents never commit to the orchestrator branch; the orchestrator never opens PRs (absent express per-PR authorization) and never merges.

## 2. Architectural Invariants

- **CORE anchor (authority for every audit/gate):** governing prompt = `orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md`, sha256 `37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52`, source channel: owner-directed paste (Arena session 2026-09-22 pointing at the `main` file). Behavior audits diff against this pinned text, never against memory. Recompute with `sha256sum` and compare before trusting it; on mismatch, halt and re-materialize from the owner-designated channel.
- **Distribution shape (owner-confirmed 2026-09-22):** task prompts live at `.orchestrator/prompts/` and the orchestrator working state at `.orchestrator/local/ORCHESTRATOR_STATE.md`, both on orchestrator branch `arena/01a0cb00-docsheet`; that branch never merges, is never an agent base, and receives only those two paths. This supersedes the init-era "Governing Shape" line in `orchestrator/INIT-RECORD.md` that put prompts under `orchestrator/prompts/` on `main` (that line remains as historical record; this ruling governs).
- Generated artifacts are never hand-edited: change reviewed inputs, rebuild via the generators (`build_research_master.py`, `build_catalogue_pages.py`, `map_series_taxonomy.py`, `sync_inventory_mirrors.py`, `reconcile_research_master.py`, `process_data.py`), and keep every `--check` gate green before opening a PR.
- The frontend delivery contract stands: any change to shipped assets or payloads must refresh the version IDs in `docs/index.html` and the hashes in `docs/build-manifest.json` in the same PR (`FrontendDeliveryContractTests` fails otherwise).
- Controlled vocabularies hold: `item_type` is content class, `format` is carrier; retired values `audio`/`video` stay rejected; master ids (`uuid`, stable compact integers) and catalogue codes are never renumbered or reissued.
- Raw CSV contract: a PR that changes `hawkins archive clone - Sheet1.csv` must include regenerated `docs/data.json`; CI on `main` ignores raw-only pushes so the Update Spreadsheet workflow owns regeneration (do not race it).
- `.github/workflows/*` change only on explicit owner instruction. The former `.scoreboard/manual-workflow-edits.md` tracking path is defunct with the scoreboard; any pending manual workflow edit must be raised with the owner before dispatch.

## 3. Settled Decisions & Rationale

- 2026-09-22 — Orchestrator CORE **v4.9.1** governs this repository (owner-applied, hub-gated upgrade from v4.9.0; D49 correctness patch). Initialization provenance: `orchestrator/INIT-RECORD.md`.
- 2026-09-22 — Distribution shape = CORE default, owner answer to structured question: `.orchestrator/` on `arena/01a0cb00-docsheet` (not prompts-on-`main`). Rationale: keeps the private working state off the mergeable default branch and matches the governing prompt's branch model.
- 2026-09-22 — Priority order (owner): maintenance/governance cleanup first; research work afterward ("We'll do research after we cleaned up the maintenance stuff.").
- 2026-09-22 — Bootstrap sequence (owner choice): this tracker + CORE anchor record first; then scoreboard remnant cleanup; then the orchestrator behavior gate; then handoff-pointer hygiene; then owner-picked product work.
- 2026-09-22 — Scoreboard dismantling is complete in substance (`.scoreboard/` absent); leftover references in current files (`.github/pull_request_template.md` → `.scoreboard/manual-workflow-edits.md`) are queued as the next cleanup task per owner "it definitely has to go".
- Lineage note — the v4.9.0 CORE file was upgraded in place and is not retained on `main`; its historical anchor is `e33886acbd12448bd2f91ce477c8dd733a49d1fbf12f9bd96f96734433bc18da` (recorded in `orchestrator/INIT-RECORD.md`). Re-materialization only if the owner re-designates a source; HUB `56eli/REPOTESTER` is presumed private and is not fetched.

## 4. Active Milestone & Current State

- **Active Milestone:** Maintenance & governance hardening — tracker/anchor bootstrap, scoreboard remnants, orchestrator behavior gate, handoff-pointer hygiene — before any research or feature work.
- **Current State:** 363-record curated catalogue; six generator `--check` gates green in CI; 158 Python tests at 92% coverage (floor 85 in `.coveragerc`); 9 Node unit tests; ESLint + Playwright e2e in CI; declared-current audit `docs/audits/2026-08-10-arena-019febe9-full-audit.md` (healthy / conditional pass, 8.1/10). Orchestrator initialized at CORE v4.9.1; this tracker is the first governance artifact on `main`.
- **Immediate Next Task:** Scoreboard remnant cleanup — remove or replace the dead `.scoreboard/manual-workflow-edits.md` references in `.github/pull_request_template.md` (current files only; `archive/` and `docs/audits/` stay historical), then continue the maintenance queue above.
```

Modify: `orchestrator/INIT-RECORD.md` — replace ONLY this line:

OLD (verify first with `grep -n "CORE Specification SHA-256" orchestrator/INIT-RECORD.md`; the line must match, else HALT AND REPORT):

```
- **CORE Specification SHA-256:** `e33886acbd12448bd2f91ce477c8dd733a49d1fbf12f9bd96f96734433bc18da` (`orchestrator/ORCHESTRATOR CORE v4.9.0 — GENERAL PURPOSE.md`)
```

NEW:

```
- **CORE Specification SHA-256:** `37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52` (`orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md`) — governing; canonical anchor recorded in `docs/PROJECT_STATE.md`. Prior v4.9.0 anchor (lineage file no longer present on `main`): `e33886acbd12448bd2f91ce477c8dd733a49d1fbf12f9bd96f96734433bc18da`.
```

No other INIT-RECORD edits — every other line stays byte-identical.

Do NOT touch: anything else in the deliverable-exclusion list of section 4.

7. SUB-TASK BREAKDOWN AND CHECKPOINTS

1. Verify prerequisites: `sha256sum` of the CORE file equals the expected value; `grep` finds the expected stale INIT-RECORD row; confirm `docs/PROJECT_STATE.md` is absent (`test ! -e docs/PROJECT_STATE.md`). If any check fails → HALT and report (no push needed yet).
2. Create `docs/PROJECT_STATE.md` with the exact content above → commit + push.
3. Apply the single-line `orchestrator/INIT-RECORD.md` anchor replacement → commit + push.
4. Run the quality checks (section 14); fix nothing outside scope if something unexpected fails — halt and report instead → commit + push (no-op if clean).
5. Open ONE pull request against `main` with the description required by section 15.

8. BRANCH AND TARGET

Base branch: `main` — never the orchestrator branch.
Target branch: `docs/project-state-tracker`
Orchestrator branch: `arena/01a0cb00-docsheet` — fetch source only; never a base or target; never push to it.
Dependencies: none — no open PRs touch these paths (verified 2026-09-22).
Resuming: fresh branch from main.
Before the first checkpoint, align HEAD to a remote tip — being on a branch named `docs/project-state-tracker` is not evidence it is the remote `docs/project-state-tracker`:

use `git fetch --depth 50 origin +docs/project-state-tracker:refs/remotes/origin/_resume && git checkout -B docs/project-state-tracker refs/remotes/origin/_resume`

If that fetch cannot find the remote ref, the branch is new:

use `git fetch --depth 1 origin +main:refs/remotes/origin/main && git checkout -B docs/project-state-tracker origin/main`

Do not skip the fetch because you appear to be on the target. Do not commit on `main`. "couldn't find remote ref" here is not an environment failure.

9. WORK PERSISTENCE AND PUSH CADENCE

Checkpoint after each sub-task in section 7, before any long or risky operation, and at the end. Your session can expire without warning; unpushed work is lost. Section 7 is your push schedule; there is no time-based rule.
A checkpoint is ONE command — first push, later pushes, and the nothing-to-push no-op are the same form. Do not run status/diff inspections around it:

```
git add -A && (git diff --cached --quiet || git commit -qm "chore: wip <sub-task>") && git push -qu origin docs/project-state-tracker
```

Match the project's commit convention for the subject (`git log` shows plain descriptive subjects; `chore: wip <sub-task>` is a valid fallback). Open ONE pull request at the end, when quality checks pass. Do not open a draft PR first. Checkpoint commits may be broken — that is expected. Never commit secrets. Never push to the orchestrator branch.
Sync rule: rebase onto `origin/main` ONLY before your first push. After the first push, integrate with `git fetch --depth 50 origin +main:refs/remotes/origin/main && git merge --no-edit origin/main` then `git push origin HEAD`. Never force-push unless explicitly instructed, and then only with `--force-with-lease`. On merge conflict: halt and report the conflicting files. Same for "refusing to merge unrelated histories" — never pass `--allow-unrelated-histories`.
If a push or fetch fails with an authentication or network error, report it plainly and keep working locally; retry the push at the next checkpoint. Never claim work is pushed while a push has failed; never modify credentials, remotes, or git config to work around it. If a push is rejected non-fast-forward, halt and report the raw rejection — do not `git pull`, do not force-push.

10. TECHNICAL REQUIREMENTS

- Documentation-only PR: Markdown exactly as specified in section 6 (byte-level fidelity for `docs/PROJECT_STATE.md`; single-line replacement in `INIT-RECORD.md`). No code, no scripts, no YAML.
- Reference `README.md` for project phrasing if you need context, but do not paraphrase or "improve" the mandated tracker text — copy it verbatim from section 6 (including the fenced markdown block content, without the outer fences).
- Preserve `INIT-RECORD.md` line endings/encoding; only the one identified line changes.
- TEST_COMMAND: `python -m unittest discover tests` — expect 158 tests, all pass (this docs-only change must not perturb the pipeline).
- INTEGRATION_TEST_COMMAND: not applicable — no component, persistence, API, queue, configuration, or deployment boundary is crossed; the change adds one Markdown file and edits another.
- FULL_SUITE_COMMAND: `python -m unittest discover tests && npm run lint` — risk-based equivalent: the Python suite plus frontend lint (zero errors). Playwright e2e is skipped locally because zero JS/HTML/CSS/data files change; CI runs it on the PR anyway. Record this skip and reason in the PR description.
- COVERAGE_COMMAND: `coverage run -m unittest discover tests && coverage report` — existing threshold 85% (`.coveragerc`), currently 92%; expect pass, no percentage invented.
- MUTATION_TEST_COMMAND: not warranted — no production logic paths change in this PR.
- LINT_COMMAND: `npm run lint` — zero errors.
- BUILD_COMMAND: not applicable — no build step; do not re-run generators (no inputs changed).

11. SAFETY AND COMPATIBILITY RULES

- Must NOT break: any `--check` gate, the delivery contract, the test suite, CI on `main`.
- Must NOT change: `data/`, schemas, research docs/outputs (byte-freeze), generated `docs/*.json`, frontend assets, workflows, tests, `package.json`, requirements files.
- Backward compatibility: additive tracker file + one metadata line edit; nothing user-facing changes on the live site (a new static Markdown file under `docs/` is served but unreferenced — that is acceptable and expected; do not link it from `index.html`).
- No migrations apply.

12. CLEANUP RULES

By the final push: no commented-out code, temporary debug logs, ad-hoc scripts, TODO markers introduced by this PR; no unrelated file modifications; no reformatting outside scope. Do not commit the fetched prompt file or anything written to /tmp. Intermediate checkpoint commits are exempt — clean up once before opening the PR.

13. STRICT BOUNDARIES / OUT OF SCOPE

- Do not push to the orchestrator branch `arena/01a0cb00-docsheet`.
- Do not open more than one PR; do not create tags or GitHub releases.
- Do not "fix" `.github/pull_request_template.md`, `orchestrator/prompts/README.md`, `AGENTS.md`, `NEXT_AGENT_HANDOFF.md`, or any `archive/`/`docs/audits/` file — those belong to later queued tasks or stay historical.
- Do not add CI jobs, scripts, or a behavior-gate checker in this PR (that is a subsequent task).
- Do not invent additional tracker sections, rename the four H2 headings, or create second trackers (`STATUS.md`, `ROADMAP.md`, a new handoff file).
- Do not fetch HUB `56eli/REPOTESTER` or any external repo.
- Artifacts: none are produced. If anything that looks like a build artifact appears, do not commit it — write its path and sha256 into the PR description and stop.

14. QUALITY CHECKS

Run and record (expected outcome in parentheses):
- `sha256sum "orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md"` (equals the anchor value in §6)
- `test -f docs/PROJECT_STATE.md && head -5 docs/PROJECT_STATE.md` (starts with `# Project State`)
- `grep -n "37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52" orchestrator/INIT-RECORD.md docs/PROJECT_STATE.md` (both files list the v4.9.1 sha)
- `grep -n "e33886acbd12448bd2f91ce477c8dd733a49d1fbf12f9bd96f96734433bc18da" orchestrator/INIT-RECORD.md` (historical value preserved)
- `git diff main --stat` (touches ONLY `docs/PROJECT_STATE.md` and `orchestrator/INIT-RECORD.md`)
- `python -m unittest discover tests` (158 pass)
- `coverage run -m unittest discover tests && coverage report` (pass, ≥85%)
- `npm run lint` (zero errors)
- Confirm: all work is pushed; `git status` clean.

15. PR DESCRIPTION REQUIREMENTS

Title: same as the work order title (first line above).
Body must contain:
- **Summary** — what and why (tracker bootstrap + anchor correction).
- **Design rationale** — why `docs/PROJECT_STATE.md` (resolved canonical path; no existing equivalent), why the anchor lives in the tracker (Initialization spec record law), why `INIT-RECORD` keeps the v4.9.0 value as lineage. Describe only this PR's changes.
- **Test results** — paste outcomes of every §14 command, including the recorded e2e skip reason.
- **Breaking changes / migration notes** — none expected; state so explicitly.
- Confirm claim-scope: every file named in the description appears in the changed-file list.
- `#### Session Irregularities` per §16.

16. HARDENING REPORT — Session Irregularities

Under heading `#### Session Irregularities` in the PR description: if no significant irregularity (threshold: interfered with the prompt AND cost >~10 min / blocked progress / required workaround AND reveals a recurring invariant or blind spot), write `None significant`. Otherwise one row per item: `Category | Symptom | Impact | Workaround | Hardening candidate` (3–6 lines). Do not pad with trivial retries or expected platform behavior (the three refresh triggers, non-fast-forward halt, rewind alignment are all expected). This report does not affect review verdicts unless it reveals a missing deliverable.
