"""Orchestrator compliance gate (CORE v4.9.1 behavior gating, fail-closed).

Deterministic unittest stage that mechanically verifies the five checkable
orchestrator duties from `orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL
PURPOSE.md` (section "Orchestrator behavior gating"), anchored in
`docs/PROJECT_STATE.md` §2 by sha256. Discovered by the existing suite:
`python -m unittest discover tests`.

Boundary, verbatim from the CORE's "Orchestrator behavior gating" section:
this mechanical check covers ONLY this checkable subset; a failing check blocks the release/boot that invoked it, exit non-zero. Judgment duties — plan quality, advice honesty, verdict soundness — are NOT machine-checkable and stay with review lanes and adversarial audits. A checker that pretends to verify everything is worse than one that honestly verifies the mechanical half.

Duty -> check mapping (file anchor -> assertion):

* Duty 1 (stub first line)
    -> docs/PROJECT_STATE.md §2, "Dispatch-stub first line (CORE duty 1)"
       bullet: declares the golden identity line
       `<repo> agent. Fetch your work order from the orchestrator branch:`
       with `<repo>` computed from `git remote get-url origin`; the same
       golden line must appear in the CORE's "The dispatch stub standard and
       the command placement law" section.
* Duty 2 (guarded publish/verify form)
    -> the CORE file carries the guarded-publish markers (the
       `git ls-remote --exit-code --heads` probe, the staged-path publication
       allowlist guard plus its HALT message, and both
       `git merge-base --is-ancestor` directions) AND docs/PROJECT_STATE.md
       §2 declares the guarded publication invariant (Distribution-shape
       bullet: the orchestrator branch "receives only those two paths" and
       "never merges"; CORE-anchor bullet names the CORE "authority for every
       audit/gate").
* Duty 3 (anchor sha256)
    -> recomputes hashlib.sha256 over the CORE file bytes and compares to the
       single 64-hex anchor parsed from the §2 CORE-anchor bullet.
* Duty 4 (run-log entry)
    -> docs/PROJECT_STATE.md §2 carries the byte-exact
       "Run-log declaration (CORE duty 4)" declared line — repos without an
       in-tree run log declare it here; the entries themselves live in
       `## Run Log` of `.orchestrator/local/ORCHESTRATOR_STATE.md` on the
       orchestrator branch.
* Duty 5 (no orchestrator-branch merges)
    -> bounded `git fetch --depth 50` of `arena/01a0cb00-docsheet` into the
       throwaway ref `refs/remotes/origin/_orch_gate_check` (HEAD and the
       working tree are never moved), then `git rev-list --min-parents=2
       --count <ref> ^<governance-baseline>` must be 0: no merge commits
       received since the orchestrator branch was established (baseline
       `df85a20`, the bootstrap merge that combined the v4.9.0 init commit
       into this branch; PR merges at or below it predate orchestrator
       governance and are excluded). This is the only network touch in the
       suite. Any fetch/git error FAILS (fail-closed); the ONLY skip is the
       explicit `ORCH_GATE_OFFLINE=1` escape hatch, which skips duty 5 loudly.


Stdlib only: hashlib, os, re, subprocess, sys, unittest, pathlib.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORE_PATH = REPO / "orchestrator" / "ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md"
TRACKER_PATH = REPO / "docs" / "PROJECT_STATE.md"

ORCHESTRATOR_BRANCH = "arena/01a0cb00-docsheet"
GATE_REF = "refs/remotes/origin/_orch_gate_check"
OFFLINE_HATCH_VAR = "ORCH_GATE_OFFLINE"
# The commit that established the orchestrator on this branch: the bootstrap
# merge ("Merge pull request #73") that combined the v4.9.0 init commit
# (`472b6ec` "Init v4.9.0 orchestrator and dismantle scoreboard") into the
# pre-existing session line. Merge commits reachable from the branch tip but
# not from this baseline were received AFTER orchestrator governance began
# and violate duty 5; merges at or below the baseline are the branch's
# founding history.
ORCH_GOVERNANCE_BASELINE = "df85a206966ca40e6659fa7033a8cee47d8aa946"


# Verbatim boundary statement from the CORE's "Orchestrator behavior gating"
# section; the module docstring above must carry the same bytes (GateHeader-
# BoundaryTests enforces it, per the CORE's "Name the boundary plainly").
BOUNDARY_STATEMENT = (
    "this mechanical check covers ONLY this checkable subset; a failing check "
    "blocks the release/boot that invoked it, exit non-zero. Judgment duties — "
    "plan quality, advice honesty, verdict soundness — are NOT machine-checkable "
    "and stay with review lanes and adversarial audits. A checker that pretends "
    "to verify everything is worse than one that honestly verifies the mechanical "
    "half."
)

# Golden dispatch-stub identity line (CORE dispatch stub standard, v4.9.0);
# `{repo}` is the name part of `git remote get-url origin`.
STUB_FIRST_LINE_TEMPLATE = "{repo} agent. Fetch your work order from the orchestrator branch:"

# Byte-exact tracker declaration bullets the gate verifies (docs/PROJECT_STATE.md §2).
RUN_LOG_DECLARATION = (
    '- **Run-log declaration (CORE duty 4):** trigger-phrase fires ("handoff", '
    '"timeout", "new orchestrator", plus milestone re-grounding runs) append a '
    "dated entry to `## Run Log` in `.orchestrator/local/ORCHESTRATOR_STATE.md` "
    "on the orchestrator branch — entries are never silently dropped; this "
    "declared line is what `tests/test_orchestrator_gate.py` verifies on `main`."
)
STUB_DECLARATION_TEMPLATE = (
    "- **Dispatch-stub first line (CORE duty 1):** every dispatch stub's first "
    "line is exactly `<repo> agent. Fetch your work order from the orchestrator "
    "branch:` where `<repo>` is the name part of `git remote get-url origin` "
    "(here: `{repo}`)."
)

# Guarded publish / verify form markers shipped in the CORE (duty 2).
GUARDED_PUBLISH_MARKERS = (
    # Probe the exact branch before trusting any local pin.
    "git ls-remote --exit-code --heads origin refs/heads/<ORCHESTRATOR_BRANCH>",
    # Reject staged paths outside the publication allowlist before publishing.
    "git diff --cached --quiet -- . ':(exclude).orchestrator/prompts/**' "
    "':(exclude).orchestrator/local/ORCHESTRATOR_STATE.md'",
    "HALT: staged paths outside the publication allowlist",
    # Both merge-base --is-ancestor directions (ahead = safe, behind = rewind lane).
    "git merge-base --is-ancestor refs/remotes/origin/_orch HEAD",
    "git merge-base --is-ancestor HEAD refs/remotes/origin/_orch",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collapse_ws(text: str) -> str:
    """Collapse all whitespace runs to single spaces (the CORE wraps prose)."""
    return " ".join(text.split())


def run_git(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run git read-only in the repo; never mutates HEAD, refs, or the tree."""
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def repo_name_from_remote() -> str:
    """`<repo>` slot: the name part of `git remote get-url origin`."""
    proc = run_git("remote", "get-url", "origin")
    if proc.returncode != 0 or not proc.stdout.strip():
        raise AssertionError(
            "Duty 1: `git remote get-url origin` failed — cannot compute the "
            "<repo> substitution slot for the dispatch-stub first line."
        )
    url = proc.stdout.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    name = url.rsplit("/", 1)[-1].rsplit(":", 1)[-1]
    if not name:
        raise AssertionError(
            f"Duty 1: could not derive the repository name from origin URL {url!r}."
        )
    return name


def tracker_section(text: str, number: int) -> str:
    """Body of `## <number>. ...` up to the next `## ` heading."""
    lines = text.splitlines()
    header = f"## {number}. "
    start = next((i for i, ln in enumerate(lines) if ln.startswith(header)), None)
    if start is None:
        raise AssertionError(
            f"docs/PROJECT_STATE.md §{number} header missing — the tracker "
            "restructure broke this gate's anchor; re-anchor the gate."
        )
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start + 1 : end])


class Duty1DispatchStubFirstLineTests(unittest.TestCase):
    """Duty 1: every dispatch stub's first line is the standard identity line."""

    def test_tracker_section_2_declares_the_golden_first_line(self) -> None:
        repo = repo_name_from_remote()
        expected = STUB_DECLARATION_TEMPLATE.format(repo=repo)
        section2 = tracker_section(read_text(TRACKER_PATH), 2)
        self.assertEqual(
            section2.count(expected),
            1,
            "Duty 1: docs/PROJECT_STATE.md §2 must declare the dispatch-stub "
            "first line exactly once and with the current <repo> slot value "
            f"({repo!r}); re-add/amend the 'Dispatch-stub first line (CORE "
            "duty 1)' bullet if a rename or tracker edit dropped it.",
        )

    def test_core_dispatch_stub_standard_carries_the_identity_line(self) -> None:
        core = collapse_ws(read_text(CORE_PATH))
        start_marker = "#### The dispatch stub standard and the command placement law"
        end_marker = "#### Artifact 2 — the Dispatch Stub"
        self.assertIn(start_marker, core, "Duty 1: the CORE lost its dispatch-stub standard section heading.")
        self.assertIn(end_marker, core, "Duty 1: the CORE dispatch-stub standard section boundary moved; re-anchor the gate.")
        section = core[core.index(start_marker) : core.index(end_marker)]
        golden = STUB_FIRST_LINE_TEMPLATE.format(repo="<repo>")
        self.assertIn(
            golden,
            section,
            "Duty 1: the CORE's dispatch stub standard no longer states the "
            f"identity line {golden!r} — the governing prompt drifted; "
            "re-materialize it from the owner channel.",
        )


class Duty2GuardedPublishFormTests(unittest.TestCase):
    """Duty 2: publishes use the guarded publish/verify form, never push-and-assume."""

    def test_core_carries_the_guarded_publish_form_markers(self) -> None:
        core = collapse_ws(read_text(CORE_PATH))
        for marker in GUARDED_PUBLISH_MARKERS:
            with self.subTest(marker=marker):
                self.assertIn(
                    marker,
                    core,
                    "Duty 2: the CORE's guarded publish/verify form lost a "
                    f"marker ({marker!r}) — the fail-closed publish procedure "
                    "drifted; re-materialize the governing prompt from the "
                    "owner channel.",
                )

    def test_tracker_declares_the_guarded_publication_invariant(self) -> None:
        section2 = tracker_section(read_text(TRACKER_PATH), 2)
        self.assertIn(
            "authority for every audit/gate",
            section2,
            "Duty 2: docs/PROJECT_STATE.md §2 must keep the CORE-anchor bullet "
            "naming the governing prompt as the authority the publish/verify "
            "form is checked against.",
        )
        self.assertIn(
            "receives only those two paths",
            section2,
            "Duty 2: docs/PROJECT_STATE.md §2 must keep the Distribution-shape "
            "bullet declaring the publication allowlist (the orchestrator "
            "branch receives only the two .orchestrator paths).",
        )
        self.assertIn(
            "never merges",
            section2,
            "Duty 2: docs/PROJECT_STATE.md §2 must keep the Distribution-shape "
            "bullet's never-merge clause for the orchestrator branch.",
        )


class Duty3CoreAnchorSha256Tests(unittest.TestCase):
    """Duty 3: the CORE file's sha256 equals the tracker's pinned anchor."""

    def test_core_file_sha256_matches_tracker_anchor(self) -> None:
        section2 = tracker_section(read_text(TRACKER_PATH), 2)
        anchor_lines = [
            line
            for line in section2.splitlines()
            if "CORE anchor (authority for every audit/gate)" in line
        ]
        self.assertEqual(
            len(anchor_lines),
            1,
            "Duty 3: expected exactly one CORE-anchor bullet in "
            "docs/PROJECT_STATE.md §2 — re-record the anchor there.",
        )
        candidates = re.findall(r"\b[0-9a-f]{64}\b", anchor_lines[0])
        self.assertEqual(
            len(candidates),
            1,
            "Duty 3: the CORE-anchor bullet must pin exactly one 64-hex "
            "sha256 — fix the tracker anchor line.",
        )
        actual = hashlib.sha256(CORE_PATH.read_bytes()).hexdigest()
        self.assertEqual(
            actual,
            candidates[0],
            "Duty 3: CORE sha256 mismatch — re-materialize from the owner "
            "channel and re-record the tracker anchor.",
        )


class Duty4RunLogDeclarationTests(unittest.TestCase):
    """Duty 4: every trigger-phrase fire gets a run-log entry (declared line)."""

    def test_run_log_declared_line_exists_in_tracker_section_2(self) -> None:
        section2 = tracker_section(read_text(TRACKER_PATH), 2)
        self.assertEqual(
            section2.count(RUN_LOG_DECLARATION),
            1,
            "Duty 4: docs/PROJECT_STATE.md §2 must carry the byte-exact "
            "'Run-log declaration (CORE duty 4)' declared line exactly once — "
            "this repo keeps its run log on the orchestrator branch "
            "(`.orchestrator/local/ORCHESTRATOR_STATE.md` ## Run Log), and the "
            "declared line on main is what the gate verifies instead of "
            "silently dropping entries; restore it if a tracker edit removed it.",
        )


class Duty5NoOrchestratorBranchMergesTests(unittest.TestCase):
    """Duty 5: the orchestrator branch receives no merges — distribution only."""

    def test_orchestrator_branch_has_no_merge_commits(self) -> None:
        if os.environ.get(OFFLINE_HATCH_VAR) == "1":
            self.skipTest(
                f"{OFFLINE_HATCH_VAR}=1: skipping the duty-5 bounded network "
                f"fetch of {ORCHESTRATOR_BRANCH}; every other duty still runs."
            )
        fetch = run_git(
            "fetch", "--depth", "50", "origin", f"+{ORCHESTRATOR_BRANCH}:{GATE_REF}",
            timeout=120,
        )
        self.assertEqual(
            fetch.returncode,
            0,
            "Duty 5: bounded fetch of the orchestrator branch "
            f"{ORCHESTRATOR_BRANCH} failed (fail-closed; network/git errors "
            "are not skipped — set ORCH_GATE_OFFLINE=1 only deliberately):\n"
            f"{fetch.stderr}",
        )
        try:
            rev_list = run_git(
                "rev-list", "--min-parents=2", "--count", GATE_REF, f"^{ORCH_GOVERNANCE_BASELINE}"
            )
            self.assertEqual(
                rev_list.returncode,
                0,
                "Duty 5: could not enumerate commits on the fetched "
                f"orchestrator branch (if the governance baseline {ORCH_GOVERNANCE_BASELINE[:7]} "
                "fell outside the fetched depth window, deepen the fetch or "
                f"re-anchor the baseline):\n{rev_list.stderr}",
            )
            self.assertEqual(
                rev_list.stdout.strip(),
                "0",
                f"Duty 5: {ORCHESTRATOR_BRANCH} received merge commits since "
                f"the orchestrator governance baseline ({ORCH_GOVERNANCE_BASELINE[:7]}) — "
                "the orchestrator branch is distribution only; un-merge and "
                "publish via the guarded publish form instead.",
            )
        finally:
            # Best-effort cleanup of the throwaway ref; never touches HEAD or the tree.
            run_git("update-ref", "-d", GATE_REF, timeout=15)


class GateHeaderBoundaryTests(unittest.TestCase):
    """The CORE requires the checker's own header to name its boundary plainly."""

    def test_module_header_states_the_mechanical_boundary(self) -> None:
        module_doc = sys.modules[__name__].__doc__ or ""
        self.assertIn(
            BOUNDARY_STATEMENT,
            module_doc,
            "The gate's header must state the mechanical boundary verbatim "
            "(CORE: 'Name the boundary plainly') — restore the boundary "
            "statement to the module docstring.",
        )


if __name__ == "__main__":
    unittest.main()
