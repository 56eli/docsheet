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
- **Run-log declaration (CORE duty 4):** trigger-phrase fires ("handoff", "timeout", "new orchestrator", plus milestone re-grounding runs) append a dated entry to `## Run Log` in `.orchestrator/local/ORCHESTRATOR_STATE.md` on the orchestrator branch — entries are never silently dropped; this declared line is what `tests/test_orchestrator_gate.py` verifies on `main`.
- **Dispatch-stub first line (CORE duty 1):** every dispatch stub's first line is exactly `<repo> agent. Fetch your work order from the orchestrator branch:` where `<repo>` is the name part of `git remote get-url origin` (here: `docsheet`).

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
- **Immediate Next Task:** Handoff-pointer hygiene — reconcile the retired `AGENTS.md` / `NEXT_AGENT_HANDOFF.md` stubs, the superseded `orchestrator/prompts/README.md` claims-on-main text, and add `.orchestrator/local/recovery/` to `.gitignore`; surface the root `0001-Init-v4.9.0-orchestrator-and-dismantle-scoreboard.patch` placement question to the owner at that hand-back.
