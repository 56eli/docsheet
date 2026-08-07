# Hygiene / Ledger / Complexity & Bloat — Improvement Assessment (2026-08-07)

**Scope:** owner question — what improvements to project hygiene, ledger/register
handling, complexity and bloat are possible. Every finding is verified against
the committed tree at `04ff5ba`. Ranked by value vs. risk, with concrete
execution notes. Nothing here touches catalogue *content*.

---

## 1. Quick wins — do first (low risk, immediate orientation gain)

### A. Root-document triage: 27 Markdown files → ~12

The repo root carries 27 `.md` files (~250 KB). Many are **completed** work —
marked implemented inside the file itself:

| Root doc (verified status) | Disposition |
|---|---|
| `TITLE_HYGIENE_PROPOSAL.md` — "✅ Applied 2026-08-03" | → archive |
| `ITEM_TYPE_CLASSIFICATION_PROPOSAL.md` — "✅ Implemented 2026-08-03" | → archive |
| `RULING_PREP_PROGRESSIVE_LEVELS_309_221.md` — executed 2026-08-07 | → archive |
| `FULL_STACK_AUDIT_2026-08-04_FINAL_358_V2.md` — superseded by the 2026-08-07 audit + archive audits | → archive |
| `LECTURE_YEAR_INVESTIGATION.md`, `VERITAS_ARTIFACT_REVIEW.md`, `VERITAS_PRODUCT_MAPPING.md` — historical evidence, findings closed | → archive |
| `OFFICIAL_CATALOGUE_DISCOVERY.md`, `GITHUB_PAGES_DEPLOYMENT_ANALYSIS.md` — one-off analyses, decisions landed | → archive |
| Living/schema docs stay: `README`, `INSTRUCTIONS`, `NEXT_AGENT_HANDOFF`, `FULL_STACK_AUDIT_2026-08-07_DEEP`, `MIGRATION_REVIEW_LEDGER`, `SERIES_TAXONOMY_MAPPING`, `PRODUCT_RELATIONSHIP_SCHEMA`, `SERIES_COMPILATION_SCHEMA`, `EDITION_MODEL_PROPOSAL`, `FILENAME_PROPOSAL_…V4`, `CATEGORY_DOMINANCE_POLICY`, `OFFICIAL_SOURCE_REGISTRY`, `RECONCILIATION_REPORT` (generated) | root |
| Open items stay: `SERIES_WORK_REGROUPING_PROPOSAL` (⏳ ruling pending), `REVIEW_MODEL_SLIM_ANALYSIS`, `CATALOGUE_READABILITY_ROADMAP`, `YEAR_COLUMN_PROVENANCE` (see 1B) | root |

Execution: `git mv` into `archive/`, add one-line entries to `archive/README.md`
index, grep-and-fix intra-doc links ("do not treat archive counts as current"
boilerplate already exists). **Value:** root orients at a glance; provenance
untouched. **Risk:** broken relative links — mitigated by a grep pass.

### B. Retire the `year_provenance.csv` mirror (proof of the drift it invites)

`data/year_provenance.csv` (367 rows) is hand-maintained and consumed by **no
script** (grep across `*.py`, `*.js`, workflows: zero references). Its
companion doc claimed "358 rows" while the CSV actually had 368 — the mirror
had already drifted before I corrected it today. Since 2026-08-07 the master
itself exposes `year_source` per row, so the register's whole purpose is now
served by the curated data.

**Proposal:** delete `data/year_provenance.csv`, slim
`YEAR_COLUMN_PROVENANCE.md` to a summary audit that points at the master
`year_source` column (drop the "full inventory" framing). **Value:** eliminates
an entire defect class (stale hand mirrors). **Risk:** none — unreferenced.

### C. Raise the coverage gate to lock in what we have

`.coveragerc` enforces `fail_under = 80`; actual coverage is **91%** with every
pipeline module ≥ 88%. Raising the gate to **85** (or 88) costs one line and
converts silent future drift into a CI failure.

### D. Checkpoint the handoff's history section

`NEXT_AGENT_HANDOFF.md` is 46 KB and grows every session. The "current verified
state" + recent sessions are the living part; dated batch entries from older
sessions are history. Move entries older than ~1–2 sessions into
`archive/HANDOFF_HISTORY.md`, keep the handoff for current state + last
sessions + open rulings. **Value:** the next agent (human or AI) reads 15 KB
instead of 46 KB. **Risk:** none if the pointer line is kept.

## 2. Ledger / register hygiene

### E. Stop hand-maintaining derivable mirror columns (the real defect source)

`data/veritas_official_products.csv` carries `matched_master_uuids` /
`matched_master_titles` — **derived facts** (the build's own
`derive_primary_relationships` computes exactly these joins from master
`source_url_veritas`). They are edited by hand after every retitle/retarget,
and have corrupted twice: once via `;` vs ` | ` separator mix-up, once via a
stale match (50491). The same fact is mirrored a *third* time in
`data/series_category_mapping.csv`.

**Proposal:** a `sync_mirrors.py` (or a `--sync-mirrors` mode on an existing
script) that recomputes the `matched_*` columns from the master and rewrites
only those columns, keeping the reviewed `mapping_status`/`review_notes`
columns untouched; then run it inside the normal regeneration sequence. The
existing `--check` validations already guard the result. **Value:** the
corruption class becomes impossible by construction; retitle sessions stop
requiring three-file manual resync. **Effort:** ~100 lines + tests.
**Risk:** low-moderate — must preserve multi-match separator conventions;
cover with a golden-row test.

### F. Collapse the 4-row taxonomy queue

`data/series_taxonomy_review_queue.csv` holds 4 rows; the main mapping file
already has a `proposed` vocabulary. Fold the queue into
`data/series_category_mapping.csv` as proposed rows → one taxonomy register
instead of two. Small win, zero risk.

### G. Verify-and-keep (no action needed, worth stating)

- `new_work_review_queue.csv` / `official_discovery_queue.csv` sit at 0 rows —
they are **intake lanes** for future official listings, not dead files. Their
empty published sheets (`docs/new-work-review.json`, `docs/official-discovery.json`)
cost ~2 lines each. Keep; one README sentence so nobody "cleans" them.
- `research_master_exclusions.csv` (72) and `research_master_source_overrides.csv`
(134) are append-only provenance registers guarded by vocabulary checks — this
is the correct pattern; do not compact.
- `veritas_mapping_decisions.csv` (12/12 approved) is reviewed evidence —
keep as-is.

### H. Optional: drop `research_master_draft.json`

Its only consumer is one count-parity line in `reconcile_research_master.py`
("JSON records = CSV records"). Dropping the JSON output + that parity line
removes a second serialization of every build. Low value; only if you want the
outputs directory minimal. My lean: skip — CSV/JSON parity is a cheap canary.

## 3. Complexity & bloat

### I. `build_research_master.py` (1,472 lines = 38% of all code)

The complexity hotspot. A clean split exists on paper (ledger validation /
candidate validation / minting / mirrors), **but** the module is 89% covered,
fully `--check`-guarded, and still changing every session. Refactoring now buys
readability at real regression risk.

**Recommendation:** defer the split until feature work slows; if done, do it as
pure file-moves with zero behavior change and rely on the committed-state
tests. **Priority: low.**

### J. Four always-empty master columns (standing item)

`location_physical`, `location_digital`, `location_streaming`,
`reference_url_2` are empty on all 365 rows and flow through every CSV/JSON/
test/schema doc. Populate-from-evidence or drop-from-schema — genuine bloat,
but it is a **schema ruling**, so it stays its own owner decision (already
offered separately).

### K. CI maintenance (owner action — I cannot push workflow files)

`.github/workflows/ci.yml` pins **Node 20**, which is past EOL (2026-04); the
sandbox runs Node 22.22.3 and `node --check` is green on 22. One-line bump
(`node-version: "20"` → `node-version: "22"`) — needs the GitHub App's
workflows permission or a manual web edit.

## Already clean (do not "fix")

- Derived primary relationships (single source of truth: master URLs; CSV holds
  only the 7 non-primary rows) — this design eliminated a whole sync class.
- Doc-parity tests (README/handoff counts asserted against generated meta);
  ledger-summary parity test; hand-edit drift guard on generated files.
- Five `--check` modes that fail on any committed-output divergence.
- Archive convention with "not normative" boilerplate + index.

---

## Proposed execution order

1. **A + B + F** (triage, year-mirror retirement, queue fold) — one commit, pure hygiene.
2. **C + D** (gate bump, handoff checkpoint) — one commit.
3. **E** (mirror-deriving tool + golden tests) — its own commit with full verification.
4. **K** (Node 22) — owner one-click; I supply the exact line.
5. **I, J, H** — only on explicit ruling.
