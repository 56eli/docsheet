#!/usr/bin/env python3
"""Deterministic pipeline test suite (stdlib unittest; no browser required).

Two layers:

* Integration: run every generator end-to-end against a disposable copy of
  the repository inputs — write, --check, tamper-detect --check, and (for the
  two CSV generators) byte-for-byte regeneration of the committed artifacts.
* Unit: exercise the pure rule matrices (taxonomy dominance, matching
  helpers, format inference, validators) directly, including failure paths.

Run:  python -m unittest discover tests -v
Coverage run (see requirements-dev.txt):
  coverage run -m unittest discover tests && coverage report --include='*.py'
"""
from __future__ import annotations

import collections
import contextlib
import csv
import hashlib
import importlib
import inspect
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import build_catalogue_pages as bcp
import build_research_master as brm
import fetch_veritas_catalogue as fvc
import map_series_taxonomy as mst

SCRIPTS = [
    "process_data.py",
    "build_research_master.py",
    "build_catalogue_pages.py",
    "map_series_taxonomy.py",
    "reconcile_research_master.py",
]
INPUT_ROOT_FILES = [
    "hawkins archive clone - Sheet1.csv",
    "migration_review_ledger.csv",
    "lecture_series_review.csv",
]
GENERATOR_SCRIPTS_AND_OUTPUTS = [
    ("generate_lecture_review.py", "lecture_series_review.csv"),
    ("generate_migration_ledger.py", "migration_review_ledger.csv"),
]


def make_sandbox() -> tempfile.TemporaryDirectory[str]:
    """Copy every pipeline input into a disposable directory.

    Tests always get a pristine, hand-maintained ledger — generators that
    redraft review CSVs must never pollute a sibling test's inputs.
    """
    tempdir = tempfile.TemporaryDirectory(prefix="docsheet-pipeline-")
    sandbox = Path(tempdir.name)
    (sandbox / "data").mkdir()
    (sandbox / "docs").mkdir()
    for name in INPUT_ROOT_FILES:
        shutil.copy2(REPO / name, sandbox / name)
    for path in (REPO / "data").iterdir():
        if path.is_file():
            shutil.copy2(path, sandbox / "data" / path.name)
    for path in (REPO / "docs").glob("*.json"):
        shutil.copy2(path, sandbox / "docs" / path.name)
    return tempdir


def drop_edition_scoped_overrides(sandbox: Path) -> None:
    """Drop committed source overrides that target edition candidates.

    Fixture tests replace the edition layer (edition_candidates.csv and
    edition_promotions.csv) with synthetic content. The committed overrides
    keyed on real edition candidate ids would then reference items that no
    longer exist, breaking the build for reasons unrelated to the fixture.
    """
    overrides = sandbox / "data" / "research_master_source_overrides.csv"
    lines = overrides.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [lines[0], *[line for line in lines[1:] if not line.startswith("candidate:edition-")]]
    if len(kept) != len(lines):
        overrides.write_text("".join(kept), encoding="utf-8")


SCRIPT_MODULES = {
    "process_data.py": "process_data",
    "build_research_master.py": "build_research_master",
    "build_catalogue_pages.py": "build_catalogue_pages",
    "fetch_veritas_catalogue.py": "fetch_veritas_catalogue",
    "map_series_taxonomy.py": "map_series_taxonomy",
    "reconcile_research_master.py": "reconcile_research_master",
    "generate_lecture_review.py": "generate_lecture_review",
    "generate_migration_ledger.py": "generate_migration_ledger",
    "sync_inventory_mirrors.py": "sync_inventory_mirrors",
}


@contextlib.contextmanager
def working_directory(path: Path):
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def invoke_script(script: str, sandbox: Path, *args: str) -> SimpleNamespace:
    """Run a generator end-to-end in-process (argparse -> render -> write).

    In-process invocation lets coverage trace the whole pipeline; the CLI
    plumbing itself is proven separately by test_cli_entrypoint_smoke.
    """
    module = importlib.import_module(SCRIPT_MODULES[script])
    out, err = io.StringIO(), io.StringIO()
    returncode = 0
    previous_argv = sys.argv
    sys.argv = [script, *args]
    try:
        with working_directory(sandbox), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                if inspect.signature(module.main).parameters:
                    result = module.main(list(args))
                else:  # argparse reads (patched) sys.argv
                    result = module.main()
                returncode = result if isinstance(result, int) else 0
            except SystemExit as exc:
                returncode = exc.code if isinstance(exc.code, int) else 1
    finally:
        sys.argv = previous_argv
    return SimpleNamespace(returncode=returncode, stdout=out.getvalue(), stderr=err.getvalue())


def run_script(script: str, sandbox: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO / script), *args],
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )


class PipelineIntegrationTests(unittest.TestCase):
    """End-to-end runs of every generator against sandboxed inputs."""

    def setUp(self) -> None:
        self.tempdir = make_sandbox()
        self.sandbox = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_script(self, script: str, *args: str) -> SimpleNamespace:
        return invoke_script(script, self.sandbox, *args)

    def test_write_then_check_then_tamper_detection(self) -> None:
        for script in SCRIPTS:
            with self.subTest(script=script):
                write = self.run_script(script)
                self.assertEqual(write.returncode, 0, f"{script} write failed:\n{write.stderr}")
                check = self.run_script(script, "--check")
                self.assertEqual(check.returncode, 0, f"{script} --check failed:\n{check.stderr}")

        # Tamper detection: every --check must fail when an output drifts.
        targets = {
            "process_data.py": self.sandbox / "docs" / "data.json",
            "build_research_master.py": self.sandbox / "data" / "research_master_draft.csv",
            "build_catalogue_pages.py": self.sandbox / "docs" / "master.json",
        }
        for script, path in targets.items():
            with self.subTest(script=script, mode="tamper"):
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "\n", encoding="utf-8")
                check = self.run_script(script, "--check")
                self.assertEqual(check.returncode, 1, f"{script} --check did not detect tamper")
                path.write_text(original, encoding="utf-8")
                check = self.run_script(script, "--check")
                self.assertEqual(check.returncode, 0, f"{script} --check broke after restore")

    def test_csv_generators_are_deterministic(self) -> None:
        """Each generator must reproduce itself from identical fresh inputs.

        The committed CSVs are hand-maintained after generation (title fixes,
        review columns), so regenerating over them legitimately differs; what
        must hold is that two runs from identical inputs are byte-identical.
        Uses a dedicated sandbox per run so the shared pipeline sandbox keeps
        its pristine ledger.
        """
        for script, output in GENERATOR_SCRIPTS_AND_OUTPUTS:
            with self.subTest(script=script):
                runs = []
                for _ in range(2):
                    with make_sandbox() as sandbox:
                        result = invoke_script(script, Path(sandbox))
                        self.assertEqual(result.returncode, 0, f"{script} failed:\n{result.stderr}")
                        runs.append((Path(sandbox) / output).read_text(encoding="utf-8"))
                self.assertEqual(runs[0], runs[1], f"{script} is not deterministic")

    def test_cli_entrypoint_smoke(self) -> None:
        """The OS-level entrypoint (sys.exit(main())) still works end-to-end."""
        result = run_script("map_series_taxonomy.py", self.sandbox, "--check")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reduced_pending_view_differs_from_committed(self) -> None:
        # With zero pending candidates in committed data, --no-include-pending matches.
        # But when a pending candidate is present, --no-include-pending --check must detect divergence.
        result_clean = self.run_script("build_catalogue_pages.py", "--no-include-pending", "--check")
        self.assertEqual(result_clean.returncode, 0)

        # Add a temporary pending candidate to prove --no-include-pending strips it
        row = "manual-other-99999,Test Candidate,lecture,2026,CD,,true,other,99999,https://veritaspub.com/test,Test Candidate,evidence,reviewed_candidate,2026-08-03,not_promoted,pending note"
        with (self.sandbox / "data" / "manual_master_candidates.csv").open("a", encoding="utf-8") as f:
            f.write(f"{row}\n")
        result_pending = self.run_script("build_catalogue_pages.py", "--no-include-pending", "--check")
        self.assertEqual(result_pending.returncode, 1)
        self.assertIn("stale", result_pending.stdout)

        # The overview's Master records stat must remain the curated count,
        # even while the Everything view includes one pending candidate.
        result_full = self.run_script("build_catalogue_pages.py")
        self.assertEqual(result_full.returncode, 0, result_full.stderr)
        meta = json.loads((self.sandbox / "docs" / "catalogue-meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["master_items"], meta["migrated_items"])
        self.assertEqual(meta["master_items"], 363)
        self.assertEqual(meta["everything_record_types"]["candidate_pending_promotion"], 1)


class TaxonomyDominanceTests(unittest.TestCase):
    """Rule matrix for the Category Dominance Policy engine."""

    def dom(self, categories: list[str]) -> tuple[str, str, str]:
        return mst.choose_dominant(categories)

    def test_r1_lecture_highlights_beats_annual(self) -> None:
        dom, rule, reason = self.dom(["Highlights", "Lecture Highlights", "Lecture Series 2002: The Way to God"])
        self.assertEqual((dom, rule, reason), ("Lecture Highlights", "R1", ""))

    def test_r1_parent_highlights_only(self) -> None:
        dom, rule, reason = self.dom(["Highlights"])
        self.assertEqual((dom, rule, reason), ("Highlights", "R1", ""))

    def test_r2_satsang_plus_highlights_is_queued(self) -> None:
        dom, rule, reason = self.dom(["Satsang", "Lecture Highlights"])
        self.assertEqual((dom, rule), ("", "R2"))
        self.assertIn("conflict", reason)

    def test_r2_satsang_year_subcategory(self) -> None:
        dom, rule, _ = self.dom(["Satsang 2008", "Satsang"])
        self.assertEqual((dom, rule), ("Satsang", "R2"))
        dom, rule, _ = self.dom(["Satsang Series and Question & Answer Sessions"])
        self.assertEqual(rule, "R2")

    def test_r5_six_book_beats_linked_2002_series(self) -> None:
        dom, rule, _ = self.dom(
            ["* * New Products * *", "Books Published by Dr. Hawkins",
             "Lecture Series 2002: The Way to God", "The Six Book 2002 Transcription Series"]
        )
        self.assertEqual((dom, rule), ("The Six Book 2002 Transcription Series", "R5"))

    def test_r3_single_annual_maps_to_vocabulary(self) -> None:
        dom, rule, reason = self.dom(["Lecture Series 2006: Transcending Levels of Consciousness", "Lectures Series"])
        self.assertEqual((dom, rule, reason), ("Lecture Series 2006: Transcending Levels of Consciousness", "R3", ""))
        self.assertEqual(mst.mapped_series_for(dom), "Transcending Levels of Consciousness")

    def test_r3_multiple_annual_is_queued(self) -> None:
        dom, rule, reason = self.dom(["Lecture Series 2002: The Way to God", "Lecture Series 2007: Spiritual Reality & Modern Man"])
        self.assertEqual((dom, rule), ("", "R3"))
        self.assertIn("Multiple annual", reason)
        for annual in mst.ANNUAL_SERIES:
            self.assertTrue(mst.mapped_series_for(annual))

    def test_r4_on_the_road_without_annual(self) -> None:
        self.assertEqual(self.dom(["* * New Products * *", "On the Road - Talk Series"])[0], "On the Road - Talk Series")
        self.assertEqual(self.dom(["* On the Road \u2013 Talk Series"])[1], "R4")

    def test_r6_office_beats_media_misc(self) -> None:
        dom, rule, _ = self.dom(["Media Miscellaneous", "Archival Office Visit Series"])
        self.assertEqual((dom, rule), ("Archival Office Visit Series", "R6"))

    def test_r7_card_decks_and_collection_order(self) -> None:
        self.assertEqual(self.dom(["Card Decks"])[0], "Card Decks")
        self.assertEqual(self.dom(["Books Published by Dr. Hawkins", "Media Miscellaneous"])[0], "Books Published by Dr. Hawkins")
        self.assertEqual(self.dom(["Media Miscellaneous"])[0], "Media Miscellaneous")
        self.assertEqual(self.dom(["Discussion Series"])[0], "Discussion Series")
        self.assertEqual(self.dom(["Volume Series"])[0], "Volume Series")

    def test_r8_fallback_only_is_queued(self) -> None:
        dom, rule, reason = self.dom(["* * New Products * *", "Specials", "Lectures Series", "* @ Product Catalog"])
        self.assertEqual((dom, rule), ("", "R8"))
        self.assertTrue(reason)

    def test_r9_unknown_and_unresolved_are_queued(self) -> None:
        dom, rule, reason = self.dom(["Map of Consciousness \u00ae"])
        self.assertEqual((dom, rule), ("", "R9"))
        self.assertIn("No recognized dominant", reason)
        dom, rule, reason = self.dom(["unresolved-category-999"])
        self.assertEqual((dom, rule), ("", "R9"))
        self.assertIn("Unresolved", reason)

    def test_series_vocabulary_covers_every_annual(self) -> None:
        self.assertEqual(mst.mapped_series_for("Satsang"), "Satsang Series")
        self.assertEqual(mst.mapped_series_for("The Six Book 2002 Transcription Series"), "Transcription Series Books")
        self.assertEqual(mst.mapped_series_for(""), "")


class VeritasMatchingTests(unittest.TestCase):
    """Pure-function contract of the inventory fetch/match layer."""

    def test_norm_is_an_aggressive_loose_match_key(self) -> None:
        # norm() lowercases and strips whitespace, punctuation, and HTML
        # entity noise so renamed products still match their master record.
        self.assertEqual(fvc.norm("Love is a Way of Being (January 2004)"), "loveisawayofbeing")
        self.assertEqual(fvc.norm("  The  EGO &amp; I  "), "theegoi")

    def test_title_date_key(self) -> None:
        self.assertEqual(fvc.title_date_key("A Review of the Work  (Sep 2006)"), "2006-09")
        self.assertIsNone(fvc.title_date_key("No date here"))

    def test_satsang_detection(self) -> None:
        self.assertTrue(fvc.is_satsang("Satsang Series (Sep 2008)"))
        self.assertFalse(fvc.is_satsang("Regular Lecture"))
        self.assertEqual(fvc.satsang_date_key("Satsang Series (Sep 2008)"), "2008-09")

    def test_category_names_and_unresolved_marker(self) -> None:
        names = {"41": "Media Miscellaneous", "15": "Books Published by Dr. Hawkins"}
        text = fvc.category_names({"product_cat": [41, 15]}, names)
        self.assertEqual(text, "Media Miscellaneous; Books Published by Dr. Hawkins")
        text = fvc.category_names({"product_cat": [999]}, names)
        self.assertEqual(text, "unresolved-category-999")
        self.assertEqual(fvc.category_names({}, names), "")

    def test_split_uuids(self) -> None:
        self.assertEqual(fvc.split_uuids(" 12; 34 ;;56 "), ["12", "34", "56"])
        self.assertEqual(fvc.split_uuids(""), [])

    def make_master(self) -> list[dict[str, str]]:
        return [
            {
                "uuid": "10", "title": "Some Lecture", "legacy_title": "Some Lecture",
                "source_url_veritas": "https://veritaspub.com/product/some-lecture/",
            },
            {
                "uuid": "11", "title": "Satsang Series (Jan 2007)", "legacy_title": "Satsang Series (Jan 2007)",
                "source_url_veritas": "",
            },
        ]

    def product(self, *, pid: int, title: str, link: str, date: str = "2020-01-01T00:00:00", cats=None) -> dict:
        return {
            "id": pid, "date": date, "link": link,
            "title": {"rendered": title}, "product_cat": cats or [],
        }

    def test_build_inventory_primary_source_match(self) -> None:
        rows = fvc.build_inventory_rows(
            [self.product(pid=7, title="Renamed Product", link="https://veritaspub.com/product/some-lecture/")],
            self.make_master(), {},
        )
        row = rows[0]
        self.assertEqual(row["mapping_status"], "matched_by_primary_source")
        self.assertEqual(row["matched_master_uuids"], "10")
        self.assertEqual(row["normalized_title_match_count"], "1")
        self.assertEqual(row["matched_master_titles"], "Some Lecture")

    def test_build_inventory_satsang_date_match(self) -> None:
        rows = fvc.build_inventory_rows(
            [self.product(pid=8, title="Satsang Series (Jan 2007)", link="https://veritaspub.com/product/other/")],
            self.make_master(), {},
        )
        self.assertEqual(rows[0]["mapping_status"], "matched_by_date")
        self.assertEqual(rows[0]["matched_master_uuids"], "11")
        unknown = fvc.build_inventory_rows(
            [self.product(pid=9, title="Satsang Series (Mar 2007)", link="https://veritaspub.com/product/nope/")],
            self.make_master(), {},
        )
        self.assertEqual(unknown[0]["mapping_status"], "unmatched_official_product")

    def test_build_inventory_normalized_and_unreviewed(self) -> None:
        rows = fvc.build_inventory_rows(
            [self.product(pid=20, title="SOME LECTURE", link="https://veritaspub.com/product/x/"),
             self.product(pid=21, title="Totally New Thing", link="https://veritaspub.com/product/y/")],
            self.make_master(), {},
        )
        statuses = {row["veritas_product_id"]: row["mapping_status"] for row in rows}
        self.assertEqual(statuses["20"], "matched_by_normalized_title")
        self.assertEqual(statuses["21"], "unreviewed_official_product")

    def decisions_file(self, directory: Path, rows: list[dict[str, str]]) -> Path:
        path = directory / "decisions.csv"
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        path.write_text(buffer.getvalue(), encoding="utf-8")
        return path

    def test_apply_mapping_decisions_validation(self) -> None:
        original_decisions = fvc.DECISIONS
        self.addCleanup(setattr, fvc, "DECISIONS", original_decisions)
        master = self.make_master()
        inventory = fvc.build_inventory_rows(
            [self.product(pid=7, title="Other", link="https://veritaspub.com/product/none/")],
            master, {},
        )
        good = {
            "veritas_product_id": "7", "mapping_status": "matched_by_title",
            "matched_master_uuids": "10", "matched_master_titles": "Some Lecture",
            "review_notes": "noted", "review_status": "approved",
            "reviewed_on": "2026-08-03", "decision_reason": "evidence",
        }
        with tempfile.TemporaryDirectory() as tmp:
            fvc.DECISIONS = self.decisions_file(Path(tmp), [good])
            self.assertEqual(fvc.apply_mapping_decisions(inventory, master), 1)
            self.assertEqual(inventory[0]["mapping_status"], "matched_by_title")

            bad = dict(good, veritas_product_id="999")
            fvc.DECISIONS = self.decisions_file(Path(tmp), [bad])
            with self.assertRaises(ValueError):
                fvc.apply_mapping_decisions(inventory, master)

            bad = dict(good, matched_master_titles="Wrong Title")
            fvc.DECISIONS = self.decisions_file(Path(tmp), [bad])
            with self.assertRaises(ValueError):
                fvc.apply_mapping_decisions(inventory, master)

            bad = dict(good, review_status="pending", reviewed_on="not-a-date")
            fvc.DECISIONS = self.decisions_file(Path(tmp), [bad])
            with self.assertRaises(ValueError):
                fvc.apply_mapping_decisions(inventory, master)

        self.assertEqual(fvc.csv_text(inventory).splitlines()[0].split(",")[0], "veritas_product_id")


class InventoryValidationTests(unittest.TestCase):
    """Derived-field invariants enforced by the Pages builder."""

    def master(self) -> list[dict[str, str]]:
        return [{"uuid": "10", "title": "Some Lecture"}, {"uuid": "12", "title": "Other"}]

    def row(self, **overrides) -> dict[str, str]:
        base = {
            "veritas_product_id": "7", "normalized_title_match_count": "1",
            "matched_master_uuids": "10", "matched_master_titles": "Some Lecture",
        }
        base.update(overrides)
        return base

    def test_consistent_inventory_passes(self) -> None:
        bcp.validate_veritas_inventory([self.row()], self.master())
        multi = self.row(normalized_title_match_count="2", matched_master_uuids="10; 12",
                         matched_master_titles="Some Lecture | Other")
        bcp.validate_veritas_inventory([multi], self.master())

    def test_count_mismatch_fails(self) -> None:
        with self.assertRaises(ValueError):
            bcp.validate_veritas_inventory([self.row(normalized_title_match_count="2")], self.master())

    def test_unknown_uuid_fails(self) -> None:
        with self.assertRaises(ValueError):
            bcp.validate_veritas_inventory([self.row(matched_master_uuids="999")], self.master())

    def test_title_mismatch_fails(self) -> None:
        with self.assertRaises(ValueError):
            bcp.validate_veritas_inventory([self.row(matched_master_titles="Stale Title")], self.master())

    def test_orphan_master_source_url_fails(self) -> None:
        product = self.row(official_product_url="https://veritaspub.com/product/known/")
        master = [{"uuid": "10", "title": "Some Lecture", "source_url_veritas": "https://veritaspub.com/product/missing/"}]
        with self.assertRaisesRegex(ValueError, "absent from the official inventory"):
            bcp.validate_veritas_inventory([product], master)

    def test_mapping_decisions_match_committed_inventory(self) -> None:
        bcp.validate_veritas_mapping_decisions(
            bcp.read_csv(bcp.VERITAS_PRODUCTS),
            bcp.read_csv(bcp.MASTER),
        )

    def test_mapping_decision_rejects_malformed_overlay_fields(self) -> None:
        fields = [
            "veritas_product_id", "mapping_status", "matched_master_uuids",
            "matched_master_titles", "review_notes", "review_status", "reviewed_on",
            "decision_reason",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decisions.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "veritas_product_id": "54838",
                    "mapping_status": "not-a-status",
                    "matched_master_uuids": "999",
                    "matched_master_titles": "Wrong title",
                    "review_notes": "Wrong note",
                    "review_status": "pending",
                    "reviewed_on": "",
                    "decision_reason": "",
                })
            original = bcp.VERITAS_MAPPING_DECISIONS
            bcp.VERITAS_MAPPING_DECISIONS = path
            self.addCleanup(setattr, bcp, "VERITAS_MAPPING_DECISIONS", original)
            with self.assertRaisesRegex(ValueError, "unsupported mapping_status"):
                bcp.validate_veritas_mapping_decisions(
                    bcp.read_csv(bcp.VERITAS_PRODUCTS),
                    bcp.read_csv(bcp.MASTER),
                )

    def test_mapping_decision_rejects_exact_primary_url_overlay(self) -> None:
        fields = [
            "veritas_product_id", "mapping_status", "matched_master_uuids",
            "matched_master_titles", "review_notes", "review_status", "reviewed_on",
            "decision_reason",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decisions.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "veritas_product_id": "7",
                    "mapping_status": "matched_by_title",
                    "matched_master_uuids": "10",
                    "matched_master_titles": "Some Lecture",
                    "review_notes": "",
                    "review_status": "approved",
                    "reviewed_on": "2026-08-08",
                    "decision_reason": "legacy review",
                })
            original = bcp.VERITAS_MAPPING_DECISIONS
            bcp.VERITAS_MAPPING_DECISIONS = path
            self.addCleanup(setattr, bcp, "VERITAS_MAPPING_DECISIONS", original)
            url = "https://veritaspub.com/product/some-lecture/"
            product = {
                "veritas_product_id": "7",
                "official_product_url": url,
                "mapping_status": "matched_by_primary_source",
                "matched_master_uuids": "10",
                "matched_master_titles": "Some Lecture",
                "review_notes": "Exact master primary Veritas URL match.",
            }
            master = [{"uuid": "10", "title": "Some Lecture", "source_url_veritas": url}]
            with self.assertRaisesRegex(ValueError, "exact primary URL"):
                bcp.validate_veritas_mapping_decisions([product], master)

    def test_everything_record_defaults(self) -> None:
        record = bcp.everything_record("master", title="X")
        self.assertEqual(record["record_type"], "master")
        self.assertEqual(record["title"], "X")
        self.assertEqual(record["series"], "")

    def test_record_types_cover_every_row(self) -> None:
        items = [{"record_type": value} for value in ("master", "candidate_veritas")]
        record_types = {
            value: sum(row["record_type"] == value for row in items)
            for value in ("master", "candidate_veritas")
        }
        self.assertEqual(sum(record_types.values()), len(items))


class FormatInferenceTests(unittest.TestCase):
    """Deterministic format inference from official product evidence."""

    def infer(self, url: str) -> str:
        item = {"format": "", "title": "", "source_url_veritas": url}
        return brm.infer_format_from_official_source(item, {})

    def test_slug_signals(self) -> None:
        base = "https://veritaspub.com/product/"
        self.assertEqual(self.infer(base + "volume-i-power-vs-force-muscle-testing-video/"), "DVD")
        self.assertEqual(self.infer(base + "something-video/"), "DVD")
        self.assertEqual(self.infer(base + "spiritual-reality-3-cd-set/"), "CD")
        self.assertEqual(self.infer(base + "satsang-series-may-2008-cd/"), "CD")
        self.assertEqual(self.infer(base + "2011-01-question-answer-session-jan-2011/"), "streaming")
        self.assertEqual(self.infer(base + "dont-set-sail-without-a-compass/"), "")
        self.assertEqual(self.infer(base + "power-vs-force-the-hidden-determinants-book/"), "book")

    def test_never_overwrites_and_needs_url(self) -> None:
        item = {"format": "DVD", "title": "", "source_url_veritas": "https://veritaspub.com/product/x-cd-set/"}
        self.assertEqual(brm.infer_format_from_official_source(item, {}), "")
        item = {"format": "", "title": "", "source_url_veritas": ""}
        self.assertEqual(brm.infer_format_from_official_source(item, {}), "")

    def test_exact_url_lookup_resolves_word_slug_books(self) -> None:
        # Word-slug URLs carry no numeric ID prefix; the legacy pid guess
        # (slug.split('-')[0]) silently misses them. Exact-URL resolution must
        # find the product and its "(Book)" title marker.
        product = {
            "veritas_product_id": "50378",
            "official_product_url": "https://veritaspub.com/product/healing-and-recovery-copy/",
            "official_title": "Healing and Recovery (Book)",
            "official_categories": "Books Published by Dr. Hawkins",
        }
        by_url = {product["official_product_url"]: product}
        item = {
            "format": "",
            "title": "",
            "item_type": "book",
            "source_url_veritas": product["official_product_url"],
        }
        self.assertEqual(brm.infer_format_from_official_source(item, {}, by_url), "book")

    def test_category_signal_is_guarded_by_item_type_and_requires_lookup(self) -> None:
        product = {
            "veritas_product_id": "43728",
            "official_product_url": "https://veritaspub.com/product/the-map-of-consciousness-explained/",
            "official_title": "The Map of Consciousness Explained: A Proven Energy Scale to ...",
            "official_categories": "Books Published by Dr. Hawkins",
        }
        by_url = {product["official_product_url"]: product}
        url = product["official_product_url"]

        # item_type=book + publisher books category -> book
        item = {"format": "", "title": "", "item_type": "book", "source_url_veritas": url}
        self.assertEqual(brm.infer_format_from_official_source(item, {}, by_url), "book")
        # lecture-class record sharing the category must NOT be labeled book
        item = {"format": "", "title": "", "item_type": "lecture", "source_url_veritas": url}
        self.assertEqual(brm.infer_format_from_official_source(item, {}, by_url), "")
        # without the URL map (legacy pid guess) the word slug resolves nothing
        item = {"format": "", "title": "", "item_type": "book", "source_url_veritas": url}
        self.assertEqual(brm.infer_format_from_official_source(item, {}), "")

    def test_category_signal_never_overrides_existing_format(self) -> None:
        product = {
            "veritas_product_id": "43728",
            "official_product_url": "https://veritaspub.com/product/the-map-of-consciousness-explained/",
            "official_title": "The Map of Consciousness Explained",
            "official_categories": "Books Published by Dr. Hawkins",
        }
        by_url = {product["official_product_url"]: product}
        item = {"format": "audiobook", "title": "", "item_type": "book", "source_url_veritas": product["official_product_url"]}
        self.assertEqual(brm.infer_format_from_official_source(item, {}, by_url), "")

    def test_lecture_highlights_category_infers_streaming(self) -> None:
        """Annual Highlights products are streaming videos (official storefront
        'Product Details: Streaming', verified 2026-08-07 for 2003/2005 pages)."""
        product = {
            "veritas_product_id": "1824",
            "official_product_url": "https://veritaspub.com/product/highlights-of-the-lectures-of-2003/",
            "official_title": "Highlights of the 2003 Lectures",
            "official_categories": "Highlights; Lecture Highlights",
        }
        by_url = {product["official_product_url"]: product}
        item = {"format": "", "title": "", "item_type": "highlight",
                "source_url_veritas": product["official_product_url"]}
        self.assertEqual(brm.infer_format_from_official_source(item, {}, by_url), "streaming")
        # legacy pid guess (no URL map) also resolves via the numeric prefix slug
        item = {"format": "", "title": "", "item_type": "highlight",
                "source_url_veritas": "https://veritaspub.com/product/1824-highlights-of-the-lectures-of-2003/"}
        self.assertEqual(brm.infer_format_from_official_source(item, {}), "")

    def test_format_inference_cd_markers_beat_audio_title(self) -> None:
        """A '– Audio' official title does not imply audiobook when the slug or
        title carries a CD marker (master 265: product 1552 is a 3-CD set sold
        under the title 'Golden Word Book Signing – Audio')."""
        product = {
            "veritas_product_id": "1552",
            "official_product_url": "https://veritaspub.com/product/golden-word-book-signing-cd/",
            "official_title": "Golden Word Book Signing – Audio",
            "official_categories": "Media Miscellaneous",
        }
        by_url = {product["official_product_url"]: product}
        item = {"format": "", "title": "", "source_url_veritas": product["official_product_url"]}
        self.assertEqual(brm.infer_format_from_official_source(item, {}, by_url), "CD")
        # slug token alone (no URL map) also resolves
        item = {"format": "", "title": "", "source_url_veritas": "https://veritaspub.com/product/golden-word-book-signing-cd/"}
        self.assertEqual(brm.infer_format_from_official_source(item, {}), "CD")
        # title-level disc-set evidence resolves even without a cd slug token
        product2 = {
            "veritas_product_id": "9999",
            "official_product_url": "https://veritaspub.com/product/golden-word-book-signing/",
            "official_title": "Golden Word Book Signing – Audio (Three Compact Disc Set)",
            "official_categories": "Media Miscellaneous",
        }
        by_url2 = {product2["official_product_url"]: product2}
        item = {"format": "", "title": "", "source_url_veritas": product2["official_product_url"]}
        self.assertEqual(brm.infer_format_from_official_source(item, {}, by_url2), "CD")

    def test_format_inference_malformed_slug_returns_blank(self) -> None:
        """Publisher-verbatim malformed slugs (product 1552's
        'https-veritaspub-com-product-...' link) carry no carrier signal: the
        inference must not guess (master 265 ruling 2026-08-08)."""
        url = "https://veritaspub.com/product/https-veritaspub-com-product-golden-word-book-signing-january-13-2007/"
        product = {
            "veritas_product_id": "1552",
            "official_product_url": url,
            "official_title": "Golden Word Book Signing – Audio",
            "official_categories": "Media Miscellaneous",
        }
        by_url = {url: product}
        item = {"format": "", "title": "", "source_url_veritas": url}
        self.assertEqual(brm.infer_format_from_official_source(item, {}, by_url), "")
        self.assertEqual(brm.infer_format_from_official_source(item, {}), "")

    def test_compact_id_recognition(self) -> None:
        self.assertTrue(brm.is_compact_id("317"))
        self.assertFalse(brm.is_compact_id("019fc4e7-d1e7-7d0b-a52e-a0e4cdf23091"))
        self.assertFalse(brm.is_compact_id(""))


class JsonTextTests(unittest.TestCase):
    def test_json_text_shape(self) -> None:
        text = bcp.json_text({"a": 1})
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(json.loads(text), {"a": 1})

from unittest import mock

import reconcile_research_master as rrm


class ProcessDataFailurePathTests(unittest.TestCase):
    """The live-spreadsheet builder must fail loudly, never silently."""

    def setUp(self) -> None:
        self.tempdir = make_sandbox()
        self.sandbox = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_missing_outputs_fail_check(self) -> None:
        (self.sandbox / "docs" / "data.json").unlink()
        result = invoke_script("process_data.py", self.sandbox, "--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("data.json must exist", result.stderr)

    def test_stale_data_json_fails_check(self) -> None:
        path = self.sandbox / "docs" / "data.json"
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        result = invoke_script("process_data.py", self.sandbox, "--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/data.json is stale", result.stderr)

    def test_missing_source_csv_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as empty:
            result = invoke_script("process_data.py", Path(empty), "gone.csv")
            self.assertEqual(result.returncode, 1)
            self.assertIn("gone.csv", result.stderr)

    def test_fallback_csv_pickup(self) -> None:
        with tempfile.TemporaryDirectory() as bare:
            sandbox = Path(bare)
            shutil.copy2(REPO / "hawkins archive clone - Sheet1.csv", sandbox / "renamed.csv")
            write = invoke_script("process_data.py", sandbox, "missing.csv")
            self.assertIn("not found; using", write.stdout)
            self.assertEqual(write.returncode, 0, write.stderr)
            self.assertTrue((sandbox / "docs" / "data.json").is_file())
            check = invoke_script("process_data.py", sandbox, "renamed.csv", "--check")
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_fallback_rejects_unrelated_root_csv(self) -> None:
        with tempfile.TemporaryDirectory() as bare:
            sandbox = Path(bare)
            (sandbox / "migration_review_ledger.csv").write_text(
                "raw_row_number,disposition\n3,item\n", encoding="utf-8"
            )
            result = invoke_script("process_data.py", sandbox, "missing.csv")
            self.assertEqual(result.returncode, 1)
            self.assertIn("expected headers", result.stderr)

    def test_fallback_rejects_ambiguous_raw_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as bare:
            sandbox = Path(bare)
            for name in ("one.csv", "two.csv"):
                shutil.copy2(REPO / "hawkins archive clone - Sheet1.csv", sandbox / name)
            result = invoke_script("process_data.py", sandbox, "missing.csv")
            self.assertEqual(result.returncode, 1)
            self.assertIn("fallback is ambiguous", result.stderr)


class VeritasFetcherOfflineTests(unittest.TestCase):
    """Offline end-to-end fetcher runs against a synthetic replay of the API."""

    def setUp(self) -> None:
        self.tempdir = make_sandbox()
        self.sandbox = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def synthetic_live_api(self) -> tuple[list[dict], list[dict]]:
        """Rebuild pseudo-API payloads from the committed inventory."""
        with (self.sandbox / "data" / "veritas_official_products.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            committed = list(csv.DictReader(handle))
        term_ids: dict[str, int] = {}
        products = []
        for row in committed:
            cat_ids = []
            for name in [part.strip() for part in row["official_categories"].split(";") if part.strip()]:
                term_ids.setdefault(name, len(term_ids) + 1)
                cat_ids.append(term_ids[name])
            products.append({
                "id": int(row["veritas_product_id"]),
                "date": row["published_date"] + "T00:00:00",
                "link": row["official_product_url"],
                "title": {"rendered": row["official_title"]},
                "product_cat": cat_ids,
            })
        taxonomy = [{"id": term_id, "name": name} for name, term_id in term_ids.items()]
        return products, taxonomy

    def test_write_then_check_matches_committed_inventory(self) -> None:
        products, taxonomy = self.synthetic_live_api()
        with mock.patch.object(fvc, "fetch_products", return_value=products), \
             mock.patch.object(fvc, "fetch_category_names", return_value={str(t["id"]): t["name"] for t in taxonomy}):
            write = invoke_script("fetch_veritas_catalogue.py", self.sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            check = invoke_script("fetch_veritas_catalogue.py", self.sandbox, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
            # Tamper detection: a drifted committed inventory must fail --check.
            path = self.sandbox / "data" / "veritas_official_products.csv"
            original = path.read_text(encoding="utf-8")
            path.write_text(original + "\n", encoding="utf-8")
            check = invoke_script("fetch_veritas_catalogue.py", self.sandbox, "--check")
            self.assertEqual(check.returncode, 1)
            self.assertIn("differs from the live reviewed inventory", check.stderr)

    def test_check_with_custom_output_is_rejected(self) -> None:
        result = invoke_script("fetch_veritas_catalogue.py", self.sandbox, "--check", "--output", "x.csv")
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot be combined", result.stderr)

    def test_api_failure_fails_loud_and_preserves_inventory(self) -> None:
        before = (self.sandbox / "data" / "veritas_official_products.csv").read_text(encoding="utf-8")
        with mock.patch.object(fvc, "fetch_products", side_effect=RuntimeError("network down")):
            result = invoke_script("fetch_veritas_catalogue.py", self.sandbox)
        self.assertEqual(result.returncode, 1)
        self.assertIn("network down", result.stderr)
        after = (self.sandbox / "data" / "veritas_official_products.csv").read_text(encoding="utf-8")
        self.assertEqual(before, after)  # failed refresh must never truncate the inventory


class GetPageRetryTests(unittest.TestCase):
    """Retry ladder and failure taxonomy of the paged API client."""

    class FakeResponse:
        def __init__(self, body: bytes, content_type: str = "application/json") -> None:
            self.body = body
            self.headers = {"Content-Type": content_type}

        def read(self) -> bytes:
            return self.body

        def __enter__(self):
            return self

        def __exit__(self, *args) -> bool:
            return False

    def http_error(self, code: int) -> HTTPError:
        return HTTPError("https://veritaspub.com/wp-json/wp/v2/product", code, "err", {}, None)

    def test_paginates_until_terminal_400(self) -> None:
        calls = []

        def fake_urlopen(request, timeout=0):
            calls.append(request.full_url)
            if len(calls) == 1:
                return self.FakeResponse(b'[{"id": 1, "title": {"rendered": "A"}}]')
            raise self.http_error(400)

        with mock.patch.object(fvc, "urlopen", side_effect=fake_urlopen):
            self.assertEqual(fvc.fetch_products(), [{"id": 1, "title": {"rendered": "A"}}])
        self.assertEqual(len(calls), 2)
        self.assertIn("page=2", calls[1])

    def test_html_response_retries_then_raises(self) -> None:
        with mock.patch.object(fvc, "urlopen", return_value=self.FakeResponse(b"<html>block</html>", "text/html")), \
             mock.patch("time.sleep"), \
             self.assertRaisesRegex(RuntimeError, "non-JSON"):
            fvc.get_page(1)

    def test_non_list_payload_retries_then_raises(self) -> None:
        with mock.patch.object(fvc, "urlopen", return_value=self.FakeResponse(b'{"error": true}')), \
             mock.patch("time.sleep"), \
             self.assertRaisesRegex(RuntimeError, "not a product list"):
            fvc.get_page(1)

    def test_400_on_first_page_is_a_real_error(self) -> None:
        with mock.patch.object(fvc, "urlopen", side_effect=self.http_error(400)), \
             mock.patch("time.sleep"), \
             self.assertRaisesRegex(RuntimeError, "failed after"):
            fvc.get_page(1)

    def test_urlerror_retries_then_raises(self) -> None:
        with mock.patch.object(fvc, "urlopen", side_effect=URLError("tls eof")), \
             mock.patch("time.sleep"), \
             self.assertRaisesRegex(RuntimeError, "tls eof"):
            fvc.get_page(1)

    def test_taxonomy_endpoint_requests_compact_fields(self) -> None:
        calls = []
        pages = [[{"id": 7, "name": "Satsang"}], []]

        def fake_urlopen(request, timeout=0):
            calls.append(request.full_url)
            return self.FakeResponse(json.dumps(pages[len(calls) - 1]).encode())

        with mock.patch.object(fvc, "urlopen", side_effect=fake_urlopen):
            self.assertEqual(fvc.fetch_category_names(), {"7": "Satsang"})
        self.assertIn("id%2Cname", calls[0])


class ReconcileDriftTests(unittest.TestCase):
    """Drift rendering and staleness detection of the reconciliation report."""

    def setUp(self) -> None:
        self.tempdir = make_sandbox()
        self.sandbox = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_markdown_and_code_cell_hygiene(self) -> None:
        self.assertEqual(rrm.markdown_cell("a|b\nc"), "a\\|b c")
        self.assertEqual(rrm.markdown_cell(""), "—")
        self.assertEqual(rrm.code(""), "`∅`")
        self.assertEqual(rrm.raw_sort_key({"raw_row_number": "12", "title": "T"}), (0, 12, "T"))
        self.assertEqual(rrm.raw_sort_key({"raw_row_number": "", "title": "T"}), (1, "", "T"))

    def test_compare_drafts_surfaces_all_divergence(self) -> None:
        committed = [
            {"raw_row_number": "5", "title": "Old", "item_type": "lecture"},
            {"raw_row_number": "", "title": "Orphan"},
        ]
        expected = [
            {"raw_row_number": "5", "title": "New", "item_type": "lecture"},
            {"raw_row_number": "7", "title": "Added", "item_type": "book"},
        ]
        comparison = rrm.compare_drafts(committed, expected)
        self.assertEqual([row["title"] for row in comparison.extras], ["Orphan"])
        self.assertEqual([row["title"] for row in comparison.missing], ["Added"])
        self.assertEqual(len(comparison.changed), 1)
        current, projected, fields = comparison.changed[0]
        self.assertEqual((current["title"], projected["title"], fields), ("Old", "New", ["title"]))

    def test_compare_drafts_matches_promoted_candidate_provenance(self) -> None:
        """Candidate/edition rows have no raw row but are still durable master rows."""
        candidate = {
            "raw_row_number": "",
            "candidate_key": "candidate:manual-veritas-example",
            "title": "Promoted candidate",
            "item_type": "lecture",
        }
        comparison = rrm.compare_drafts([candidate], [dict(candidate)])
        self.assertEqual(comparison.extras, [])
        self.assertEqual(comparison.missing, [])
        self.assertEqual(comparison.changed, [])

    def test_committed_candidate_rows_are_not_reconciliation_extras(self) -> None:
        """The real 39 manual + 24 edition promotions reconcile by candidate key."""
        with working_directory(REPO):
            committed = rrm.read_csv(rrm.CURRENT_MASTER)
            expected = brm.build_master().items
        comparison = rrm.compare_drafts(committed, expected)
        self.assertEqual(comparison.extras, [])
        self.assertEqual(comparison.missing, [])
        self.assertEqual(comparison.changed, [])

    def test_report_renders_drift_sections_and_stale_check(self) -> None:
        drift = rrm.DraftComparison(
            extras=[{"raw_row_number": "9", "title": "Extra", "item_type": "lecture", "notes": "note"}],
            missing=[{"raw_row_number": "10", "title": "Missing", "item_type": "book"}],
            changed=[(
                {"raw_row_number": "11", "title": "Before", "format": ""},
                {"raw_row_number": "11", "title": "After", "format": "audiobook"},
                ["title", "format"],
            )],
        )
        with working_directory(self.sandbox), mock.patch.object(rrm, "compare_drafts", return_value=drift):
            report = rrm.render_report()
        self.assertIn("Extra", report)
        self.assertIn("Missing", report)
        self.assertIn("`∅` → `audiobook`", report)  # empty-before drift stays visible

        write = invoke_script("reconcile_research_master.py", self.sandbox)
        self.assertEqual(write.returncode, 0, write.stderr)
        path = self.sandbox / rrm.REPORT.name
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        check = invoke_script("reconcile_research_master.py", self.sandbox, "--check")
        self.assertEqual(check.returncode, 1)
        self.assertIn("is stale", check.stdout)


class DerivedPrimaryRelationshipTests(unittest.TestCase):
    """Primary item→product links are derived from the master's own URLs.

    Since every master with a ``source_url_veritas`` gets exactly one derived
    ``primary_product_for_item_part`` relationship, ``product_relationships.csv``
    only needs to hold the genuinely distinct non-primary rows
    (``related_material``). This replaces the old hand-maintained primary rows.
    """

    def test_derive_primary_relationships_builds_from_master_urls(self) -> None:
        product_a = {"veritas_product_id": "7", "official_product_url": "https://veritaspub.com/product/a/",
                     "official_title": "Alpha", "published_date": "2002-01-01", "mapping_status": "matched_by_primary_source"}
        product_b = {"veritas_product_id": "8", "official_product_url": "https://veritaspub.com/product/b/",
                     "official_title": "Beta", "published_date": "2003-01-01", "mapping_status": "matched_by_primary_source"}
        master = [
            {"uuid": "10", "source_url_veritas": product_a["official_product_url"],
             "raw_row_number": "7", "candidate_key": "", "catalog_code": "LECTURE-2002-001",
             "title": "Alpha", "item_type": "lecture", "year": "2002"},
            {"uuid": "12", "source_url_veritas": product_b["official_product_url"],
             "raw_row_number": "", "candidate_key": "candidate:edition-x", "catalog_code": "",
             "title": "Beta", "item_type": "book", "year": "2003"},
            {"uuid": "13", "source_url_veritas": "", "raw_row_number": "9", "candidate_key": "",
             "catalog_code": "", "title": "No URL", "item_type": "lecture", "year": ""},
        ]
        derived = bcp.derive_primary_relationships(master, [product_a, product_b])
        self.assertEqual(len(derived), 2)  # only URL-bearing masters
        by_uuid = {rel["master_uuid"]: rel for rel in derived}
        a = by_uuid["10"]
        self.assertEqual(a["relationship_id"], "rel-veritas-7-10")
        self.assertEqual(a["relationship_type"], "primary_product_for_item_part")
        self.assertEqual(a["review_status"], "reviewed")
        self.assertEqual(a["master_year"], "2002")
        self.assertEqual(a["source_product_published_date"], "2002-01-01")
        # edition-provenance master uses its candidate_key as raw provenance
        self.assertEqual(by_uuid["12"]["raw_row_number"], "candidate:edition-x")

    def test_primary_relationship_note_provenance(self) -> None:
        self.assertEqual(
            bcp.primary_relationship_note({"candidate_key": "candidate:edition-veritas-x"}),
            bcp.PRIMARY_RELATIONSHIP_NOTES["candidate:edition-"],
        )
        self.assertEqual(
            bcp.primary_relationship_note({"candidate_key": "candidate:manual-veritas-satsang-1304"}),
            bcp.PRIMARY_RELATIONSHIP_NOTES["candidate:manual-veritas-satsang-"],
        )
        self.assertEqual(
            bcp.primary_relationship_note({"candidate_key": "candidate:manual-veritas-47979"}),
            bcp.PRIMARY_RELATIONSHIP_NOTES["candidate:manual-"],
        )
        self.assertEqual(
            bcp.primary_relationship_note({"candidate_key": ""}),
            bcp.PRIMARY_RELATIONSHIP_NOTE,
        )

    def test_committed_state_derives_336_primary_plus_8_related(self) -> None:
        # The committed master + inventory + CSV must assemble to exactly the
        # published relationship count: 333 derived primary + 7 related_material
        # = 340 total. (Was 336 + 7 = 343 before the 2026-08-08 D-01 collapse
        # retired the duplicate streaming masters 225/226/227, which had shared
        # Veritas primary URLs with promoted DVD masters 311/310.)

        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            result = invoke_script("build_catalogue_pages.py", sandbox, "--check")
            self.assertEqual(result.returncode, 0, result.stderr)
            master = bcp.read_csv(bcp.MASTER)
            veritas = bcp.read_csv(bcp.VERITAS_PRODUCTS)
            derived = bcp.derive_primary_relationships(master, veritas)
            self.assertEqual(len(derived), 333)
            self.assertEqual(len(derived) + 7, 340)  # 340 total relationships (333 derived + 7 related)
            meta = json.loads((sandbox / "docs" / "catalogue-meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["reviewed_product_relationships"], 340)
        finally:
            tempdir.cleanup()

    def test_product_relationships_csv_holds_only_non_primary_rows(self) -> None:
        with (REPO / "data/product_relationships.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(rows, "product_relationships.csv must retain its header + rows")
        self.assertNotIn(
            "primary_product_for_item_part",
            {row["relationship_type"].strip() for row in rows},
            "primary relationships are derived from the master, not stored in the CSV",
        )

    def test_deleting_a_related_material_row_fails_check(self) -> None:
        # Tamper detection: dropping a curated related_material row must fail
        # --check loudly (the generator's failure contract is exit 1).
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            path = sandbox / "data" / "product_relationships.csv"
            lines = path.read_text(encoding="utf-8").splitlines()
            kept = [line for line in lines if "rel-veritas-1542-202" not in line]
            path.write_text("\n".join(kept) + "\n", encoding="utf-8")
            result = invoke_script("build_catalogue_pages.py", sandbox, "--check")
            self.assertEqual(result.returncode, 1)
        finally:
            tempdir.cleanup()


class WorkFamilyTests(unittest.TestCase):
    """Reviewed work-family input: validation and work_id assignment."""

    FAMILY_HEADER = "work_id,member_master_uuid,canonical_work_title,evidence_note,review_status,reviewed_on"

    def write_families(self, sandbox: Path, rows: list[str]) -> None:
        (sandbox / "data" / "work_families.csv").write_text(
            self.FAMILY_HEADER + "\n" + "\n".join(rows) + "\n", encoding="utf-8"
        )
        # The committed edition candidates reference the committed work ids;
        # custom family files invalidate them, so clear the edition layer.
        (sandbox / "data" / "edition_candidates.csv").write_text(
            "candidate_key,work_id,edition_role,matched_master_uuid,candidate_title,"
            "proposed_item_type,proposed_year,proposed_format,proposed_format_detail,"
            "proposed_owned,source_name,source_product_id,official_product_url,"
            "official_product_title,evidence_note,review_status,reviewed_on,"
            "promotion_status,promotion_notes\n", encoding="utf-8")
        (sandbox / "data" / "edition_promotions.csv").write_text(
            "candidate_key,master_uuid,work_id,edition_role,item_type,format,series,"
            "approval_status,approved_on,approval_reason\n", encoding="utf-8")
        drop_edition_scoped_overrides(sandbox)

    def approved_row(self, member: str = "289", work_id: str = "w-tvf") -> str:
        return (f"{work_id},{member},Truth vs Falsehood,"
                "Veritas book 50398 + Audible audiobook + CD&DVD set 1728 evidence,approved,2026-08-03")

    def test_committed_families_build_clean(self) -> None:
        # The committed work-families batch is fully approved: master rows
        # carry work_id (book rows + minted edition rows) and --check passes.
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            result = invoke_script("build_research_master.py", sandbox, "--check")
            self.assertEqual(result.returncode, 0, result.stderr)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
                rows = {row["uuid"]: row for row in csv.DictReader(handle)}
            self.assertIn("work_id", rows["1"])
            self.assertEqual(rows["289"]["work_id"], "w-truth-vs-falsehood")
            self.assertEqual(rows["320"]["work_id"], "w-power-vs-force")  # first minted edition row
            tvf_audio = next(r for r in rows.values() if r["title"] == "Truth Vs Falsehood (Audiobook)")
            self.assertEqual(tvf_audio["work_id"], "w-truth-vs-falsehood")
            self.assertTrue(any(row["work_id"] for row in rows.values()))
        finally:
            tempdir.cleanup()

    def test_approved_family_assigns_work_id_and_check_passes(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_families(sandbox, [self.approved_row()])
            write = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            self.assertIn("Applied 1 approved work-family memberships", write.stdout)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
                rows = {row["uuid"]: row for row in csv.DictReader(handle)}
            self.assertEqual(rows["289"]["work_id"], "w-tvf")
            self.assertEqual(rows["290"]["work_id"], "")
            check = invoke_script("build_research_master.py", sandbox, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
        finally:
            tempdir.cleanup()

    def test_proposed_rows_are_validated_but_not_applied(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_families(sandbox, [
                "w-tvf,289,Truth vs Falsehood,title-only grouping proposal,proposed,"
            ])
            write = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
                rows = {row["uuid"]: row for row in csv.DictReader(handle)}
            self.assertEqual(rows["289"]["work_id"], "")
        finally:
            tempdir.cleanup()

    def test_unknown_member_fails(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_families(sandbox, [self.approved_row(member="9999")])
            with self.assertRaisesRegex(ValueError, "unknown master ID"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_missing_columns_fail(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            (sandbox / "data" / "work_families.csv").write_text(
                "work_id,member_master_uuid\nw-tvf,289\n", encoding="utf-8")
            (sandbox / "data" / "edition_candidates.csv").write_text(
                "candidate_key,work_id,edition_role,matched_master_uuid,candidate_title,"
                "proposed_item_type,proposed_year,proposed_format,proposed_format_detail,"
                "proposed_owned,source_name,source_product_id,official_product_url,"
                "official_product_title,evidence_note,review_status,reviewed_on,"
                "promotion_status,promotion_notes\n", encoding="utf-8")
            (sandbox / "data" / "edition_promotions.csv").write_text(
                "candidate_key,master_uuid,work_id,edition_role,item_type,format,series,"
                "approval_status,approved_on,approval_reason\n", encoding="utf-8")
            drop_edition_scoped_overrides(sandbox)
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_approved_row_needs_date_evidence_and_canonical_title(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_families(sandbox, ["w-tvf,289,Truth vs Falsehood,,approved,"])
            with self.assertRaisesRegex(ValueError, "ISO reviewed_on"):
                invoke_script("build_research_master.py", sandbox)
            self.write_families(sandbox, ["w-tvf,289,Truth vs Falsehood,,approved,2026-08-03"])
            with self.assertRaisesRegex(ValueError, "explain the evidence"):
                invoke_script("build_research_master.py", sandbox)
            self.write_families(sandbox, ["w-tvf,289,,evidence,approved,2026-08-03"])
            with self.assertRaisesRegex(ValueError, "canonical work title"):
                invoke_script("build_research_master.py", sandbox)
            self.write_families(sandbox, ["w-tvf,289,Truth vs Falsehood,evidence,pending,2026-08-03"])
            with self.assertRaisesRegex(ValueError, "invalid review_status"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_duplicate_member_fails(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_families(sandbox, [
                self.approved_row(), "w-tvf2,289,Truth vs Falsehood,other evidence,approved,2026-08-03",
            ])
            with self.assertRaisesRegex(ValueError, "twice"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_tamper_detection_when_work_id_drifts(self) -> None:
        # Approved family applied, then the committed master loses the id:
        # --check must fail.
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_families(sandbox, [self.approved_row()])
            invoke_script("build_research_master.py", sandbox)
            path = sandbox / "data" / "research_master_draft.csv"
            lines = path.read_text(encoding="utf-8").splitlines()
            header = lines[0].split(",")
            work_idx = header.index("work_id")
            kept = [lines[0]]
            for line in lines[1:]:
                cells = line.split(",")
                if cells[0] == "289" and len(cells) > work_idx:
                    cells[work_idx] = ""
                kept.append(",".join(cells))
            path.write_text("\n".join(kept) + "\n", encoding="utf-8")
            result = invoke_script("build_research_master.py", sandbox, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("stale relative to the current ledger", result.stdout)
        finally:
            tempdir.cleanup()


class EditionCandidateTests(unittest.TestCase):
    """Edition-candidate layer: validation and promotion-to-master rows."""

    CAND_HEADER = ("candidate_key,work_id,edition_role,matched_master_uuid,candidate_title,"
                   "proposed_item_type,proposed_year,proposed_format,proposed_format_detail,"
                   "proposed_owned,source_name,source_product_id,official_product_url,"
                   "official_product_title,evidence_note,review_status,reviewed_on,"
                   "promotion_status,promotion_notes")
    PROMO_HEADER = ("candidate_key,master_uuid,work_id,edition_role,item_type,format,series,"
                    "approval_status,approved_on,approval_reason")

    def family_rows(self) -> list[str]:
        return ["w-tvf,289,Truth vs Falsehood,book 50398 + audiobook evidence,approved,2026-08-03"]

    def candidate_rows(self, promotion_status: str = "not_promoted") -> list[str]:
        return [
            (f"edition-audible-tvf,w-tvf,audio,289,Truth Vs Falsehood (Audiobook),book,,audiobook,Audiobook,true,"
            f"audible,https://www.audible.com/pd/Truths-vs-Falsehood-Audiobook/B00NWS4SQO,"
            f"https://www.audible.com/pd/Truths-vs-Falsehood-Audiobook/B00NWS4SQO,Truth Vs Falsehood,"
            f"audible inventory row,reviewed_candidate,2026-08-03,{promotion_status},audiobook edition"),
        ]

    def write_files(self, sandbox: Path, candidate_rows: list[str], promo_rows: list[str] | None = None,
                    family_rows: list[str] | None = None) -> None:
        (sandbox / "data" / "work_families.csv").write_text(
            "work_id,member_master_uuid,canonical_work_title,evidence_note,review_status,reviewed_on\n"
            + "\n".join(family_rows if family_rows is not None else self.family_rows()) + "\n",
            encoding="utf-8")
        (sandbox / "data" / "edition_candidates.csv").write_text(
            self.CAND_HEADER + "\n" + "\n".join(candidate_rows) + "\n", encoding="utf-8")
        (sandbox / "data" / "edition_promotions.csv").write_text(
            self.PROMO_HEADER + "\n" + ("\n".join(promo_rows) + "\n" if promo_rows else ""),
            encoding="utf-8")
        drop_edition_scoped_overrides(sandbox)

    def test_committed_candidates_validate_and_build_clean(self) -> None:
        tempdir = make_sandbox()
        try:
            result = invoke_script("build_research_master.py", Path(tempdir.name), "--check")
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            tempdir.cleanup()

    def test_approved_promotion_mints_edition_row(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_files(sandbox, self.candidate_rows("promoted"), [
                "edition-audible-tvf,320,w-tvf,audio,book,audiobook,,approved,2026-08-03,owner approved audiobook edition",
            ])
            write = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
                rows = {row["uuid"]: row for row in csv.DictReader(handle)}
            self.assertIn("320", rows)  # next compact ID above current max 319
            row = rows["320"]
            self.assertEqual(row["work_id"], "w-tvf")
            self.assertEqual(row["item_type"], "book")
            self.assertEqual(row["format"], "audiobook")
            self.assertEqual(row["source_url_audible"], "https://www.audible.com/pd/Truths-vs-Falsehood-Audiobook/B00NWS4SQO")
            self.assertEqual(row["candidate_key"], "candidate:edition-audible-tvf")
            # D3: the audiobook URL moved off the book row into its edition row
            self.assertEqual(rows["289"]["source_url_audible"], "")
            check = invoke_script("build_research_master.py", sandbox, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
        finally:
            tempdir.cleanup()

    def test_promotion_requires_candidate_status_flip(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_files(sandbox, self.candidate_rows("not_promoted"), [
                "edition-audible-tvf,320,w-tvf,audio,book,audiobook,,approved,2026-08-03,owner approved",
            ])
            with self.assertRaisesRegex(ValueError, "must be 'promoted'"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_unknown_work_id_or_master_fails(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            bad_work = [self.candidate_rows()[0].replace("w-tvf,audio,289", "w-nope,audio,289")]
            self.write_files(sandbox, bad_work)
            with self.assertRaisesRegex(ValueError, "unknown work_id"):
                invoke_script("build_research_master.py", sandbox)
            bad_master = [self.candidate_rows()[0].replace(",289,", ",9999,")]
            self.write_files(sandbox, bad_master)
            with self.assertRaisesRegex(ValueError, "unknown matched master ID"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_unknown_product_and_duplicate_key_fail(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            bad_product = [self.candidate_rows()[0].replace("B00NWS4SQO", "B00NOPE000")]
            self.write_files(sandbox, bad_product)
            with self.assertRaisesRegex(ValueError, "unknown audible product"):
                invoke_script("build_research_master.py", sandbox)
            self.write_files(sandbox, self.candidate_rows() * 2)
            with self.assertRaisesRegex(ValueError, "unique candidate_key"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_hayhouse_candidate_validates_and_mismatch_fails(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            url = "https://www.hayhouse.com/power-vs-force-paperback"
            row = (f"edition-hh-pvf,w-power-vs-force,book,286,Power vs Force (Paperback),book,,book,,true,"
                   f"hayhouse,{url},{url},Power vs Force,"
                   "hayhouse paperback evidence,reviewed_candidate,2026-08-03,not_promoted,paperback edition")
            families = ["w-power-vs-force,286,Power vs Force,book + audiobook evidence,approved,2026-08-03"]
            self.write_files(sandbox, [row], family_rows=families)
            write = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            # keep the valid product reference but corrupt the official URL copy
            bad_url = row.replace(f",{url},{url},", f",{url},https://www.hayhouse.com/other-page,")
            self.write_files(sandbox, [bad_url], family_rows=families)
            with self.assertRaisesRegex(ValueError, "differs from the inventory"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_candidate_shape_validation(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            base = self.candidate_rows()[0]
            cases = [
                (base.replace(",book,,audiobook,", ",book,,vinyl,"), "carrier format"),
                (base.replace("2026-08-03,not_promoted", "2026-08-03,maybe"), "must be 'not_promoted'"),
                (base.replace("reviewed_candidate,2026-08-03", "pending,2026-08-03"), "review_status must be"),
                (base.replace("reviewed_candidate,2026-08-03", "reviewed_candidate,"), "ISO reviewed_on"),
            ]
            for row, expected in cases:
                self.write_files(sandbox, [row])
                with self.assertRaisesRegex(ValueError, expected):
                    invoke_script("build_research_master.py", sandbox)
            # invalid year
            self.write_files(sandbox, [base.replace("Truth Vs Falsehood (Audiobook),book,,audiobook",
                                                    "Truth Vs Falsehood (Audiobook),book,20xx,audiobook")])
            with self.assertRaisesRegex(ValueError, "proposed_year"):
                invoke_script("build_research_master.py", sandbox)
            # invalid owned
            self.write_files(sandbox, [base.replace(",true,audible,", ",maybe,audible,")])
            with self.assertRaisesRegex(ValueError, "proposed_owned"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_promotion_edge_cases(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            promo = "edition-audible-tvf,320,w-tvf,audio,book,audiobook,,approved,2026-08-03,owner approved"
            # rejected promotion: no row minted, candidate stays not_promoted
            self.write_files(sandbox, self.candidate_rows(), [promo.replace("approved,2026-08-03", "rejected,2026-08-03")])
            write = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            # approved promotion missing date
            self.write_files(sandbox, self.candidate_rows("promoted"), [promo.replace(",2026-08-03,", ",,")])
            with self.assertRaisesRegex(ValueError, "ISO approved_on"):
                invoke_script("build_research_master.py", sandbox)
            # work_id mismatch with candidate
            self.write_files(sandbox, self.candidate_rows("promoted"), [promo.replace("w-tvf,audio", "w-other,audio")])
            with self.assertRaisesRegex(ValueError, "must match the candidate"):
                invoke_script("build_research_master.py", sandbox)
            # deprecated item_type in promotion
            self.write_files(sandbox, self.candidate_rows("promoted"), [promo.replace(",book,audiobook,", ",video,audiobook,")])
            with self.assertRaisesRegex(ValueError, "non-deprecated"):
                invoke_script("build_research_master.py", sandbox)
            # unknown approval status
            self.write_files(sandbox, self.candidate_rows("promoted"), [promo.replace("approved,2026-08-03", "pending,2026-08-03")])
            with self.assertRaisesRegex(ValueError, "approval_status"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_tamper_detection_when_edition_row_vanishes(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_files(sandbox, self.candidate_rows("promoted"), [
                "edition-audible-tvf,320,w-tvf,audio,book,audiobook,,approved,2026-08-03,owner approved",
            ])
            invoke_script("build_research_master.py", sandbox)
            path = sandbox / "data" / "research_master_draft.csv"
            kept = [line for line in path.read_text(encoding="utf-8").splitlines()
                    if not line.startswith("320,")]
            path.write_text("\n".join(kept) + "\n", encoding="utf-8")
            result = invoke_script("build_research_master.py", sandbox, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("stale relative to the current ledger", result.stdout)
        finally:
            tempdir.cleanup()


class SourceOverrideStatusTests(unittest.TestCase):
    """Proposed source overrides are validated but never applied."""

    HEADER = "raw_row_number,target_field,override_value,review_status,approval_date,review_reason,evidence_source"

    def write_overrides(self, sandbox: Path, rows: list[str]) -> None:
        (sandbox / "data" / "research_master_source_overrides.csv").write_text(
            self.HEADER + "\n" + "\n".join(rows) + "\n", encoding="utf-8"
        )
        # These focused fixtures intentionally replace the full source-override
        # layer with a one-row test file, which makes the committed filename
        # proposal mirrors stale for unrelated rows. Drop that optional proposal
        # input so the fixture exercises source overrides only.
        (sandbox / "data" / "filename_proposal_YYYYMM.csv").unlink(missing_ok=True)

    def row(self, status: str = "proposed") -> str:
        return (f"328,source_url_hay_house,https://www.hayhouse.com/truth-vs-falsehood-parperback/,"
                f"{status},,same-carrier paperback link,data/hayhouse_official_products.csv")

    def test_proposed_rows_validate_but_do_not_apply(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_overrides(sandbox, [self.row("proposed")])
            write = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            self.assertIn("Applied 0 approved source overrides", write.stdout)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
                row = {r["uuid"]: r for r in csv.DictReader(handle)}["289"]
            self.assertEqual(row["source_url_hay_house"], "")
            check = invoke_script("build_research_master.py", sandbox, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
        finally:
            tempdir.cleanup()

    def test_approved_rows_apply(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_overrides(sandbox, [self.row("approved")])
            write = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            self.assertIn("1 approved source overrides", write.stdout)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
                row = {r["uuid"]: r for r in csv.DictReader(handle)}["289"]
            self.assertEqual(row["source_url_hay_house"], "https://www.hayhouse.com/truth-vs-falsehood-parperback/")
        finally:
            tempdir.cleanup()

    def test_candidate_keyed_override_applies_to_promoted_row(self) -> None:
        # Promoted masters (raw_row_number = candidate:<key>) can take source
        # overrides too: the overrides layer runs after promotions.
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_overrides(sandbox, [
                ("candidate:manual-veritas-47979,source_url_hay_house,"
                "https://www.hayhouse.com/the-ego-is-not-the-real-you-paperback-us,"
                "approved,2026-08-03,paperback link for promoted master,data/hayhouse_official_products.csv"),
            ])
            write = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(write.returncode, 0, write.stderr)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
                row = {r["uuid"]: r for r in csv.DictReader(handle)}["316"]
            self.assertEqual(row["source_url_hay_house"], "https://www.hayhouse.com/the-ego-is-not-the-real-you-paperback-us")
            check = invoke_script("build_research_master.py", sandbox, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
        finally:
            tempdir.cleanup()

    def test_invalid_status_fails(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            self.write_overrides(sandbox, [self.row("pending")])
            with self.assertRaisesRegex(ValueError, "review_status must be"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()


class NewWorkQueueTests(unittest.TestCase):
    """The new-work review lane must stay aligned with the Veritas inventory."""

    def row(self, **overrides) -> dict[str, str]:
        base = {
            "candidate_title": "Satsang Series (Jan 2006)", "item_type": "lecture",
            "series": "Satsang", "year": "2006", "format": "CD",
            "source_product_id": "1304", "source_url_veritas": "https://veritaspub.com/product/satsang-series-1-january-11-2006-held-at-st-andrews-episcopal-church/",
            "match_status": "not_found_in_current_draft", "match_notes": "candidate new work",
            "approval": "", "review_notes": "",
        }
        base.update(overrides)
        return base

    def test_committed_queue_builds_clean(self) -> None:
        tempdir = make_sandbox()
        try:
            result = invoke_script("build_catalogue_pages.py", Path(tempdir.name), "--check")
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            tempdir.cleanup()

    def test_unknown_product_and_url_mismatch_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown Veritas product"):
            bcp.validate_new_work_queue([self.row(source_product_id="9999")], [])
        inventory = [{"veritas_product_id": "1304", "official_product_url": "https://veritaspub.com/product/real/" }]
        with self.assertRaisesRegex(ValueError, "differs from the inventory"):
            bcp.validate_new_work_queue([self.row()], inventory)

    def test_duplicate_and_empty_title_fail(self) -> None:
        inventory = [{"veritas_product_id": "1304", "official_product_url": "https://veritaspub.com/product/satsang-series-1-january-11-2006-held-at-st-andrews-episcopal-church/"}]
        with self.assertRaisesRegex(ValueError, "duplicates product"):
            bcp.validate_new_work_queue([self.row(), self.row()], inventory)
        with self.assertRaisesRegex(ValueError, "candidate_title"):
            bcp.validate_new_work_queue([self.row(candidate_title="")], inventory)


class SyncInventoryMirrorsTests(unittest.TestCase):
    """sync_inventory_mirrors.py re-derives the inventory's mirror columns."""

    def make_legacy_non_primary_53062(self, path: Path) -> None:
        """Seed a sandbox-only legacy overlay for contradiction tests."""
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        target = next(row for row in rows if row["veritas_product_id"] == "53062")
        target["mapping_status"] = "matched_by_title"
        target["review_notes"] = "legacy review"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_committed_inventory_mirrors_match_master(self) -> None:
        # The 2026-08-07 owner ruling resolved the last URL-evidence
        # contradictions (50411->286, 1542->331); committed mirrors are clean.
        result = invoke_script("sync_inventory_mirrors.py", REPO, "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already match", result.stdout)

    def test_sync_fixes_drifted_mirror_cells(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            inv = sandbox / "data" / "veritas_official_products.csv"
            text = inv.read_text(encoding="utf-8")
            drifted = text.replace(
                ",2,225; 311,Devotion to Truth Talk | Devotion to Truth Talk,",
                ",1,311,Devotion to Truth Talk,",
            )
            # After the 2026-08-08 D-01 collapse the committed inventory is
            # already a single-ID row; seed the drift in the opposite direction
            # (311 -> "225; 311") to prove sync re-derives it back to 311.
            if drifted == text:
                drifted = text.replace(
                    ",1,311,Devotion to Truth Talk,",
                    ",2,225; 311,Devotion to Truth Talk | Devotion to Truth Talk,",
                )
            self.assertNotEqual(drifted, text)  # fixture actually drifted the row
            inv.write_text(drifted, encoding="utf-8")

            result = invoke_script("sync_inventory_mirrors.py", sandbox)
            self.assertEqual(result.returncode, 0, result.stderr)
            with inv.open(newline="", encoding="utf-8") as handle:
                row = next(r for r in csv.DictReader(handle) if r["veritas_product_id"] == "55473")
            self.assertEqual(row["normalized_title_match_count"], "1")
            self.assertEqual(row["matched_master_uuids"], "311")
            self.assertEqual(
                row["matched_master_titles"],
                "Devotion to Truth Talk",
            )
            # reviewed columns are never rewritten
            self.assertEqual(row["mapping_status"], "matched_by_primary_source")
            self.assertEqual(row["review_notes"], "Exact master primary Veritas URL match.")
            check = invoke_script("sync_inventory_mirrors.py", sandbox, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn("already match", check.stdout)
        finally:
            tempdir.cleanup()

    def test_sync_check_flags_drift_without_writing(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            inv = sandbox / "data" / "veritas_official_products.csv"
            text = inv.read_text(encoding="utf-8")
            # After the 2026-08-08 D-01 collapse the committed inventory is
            # already a single-ID row (54219 -> 310); seed drift by re-introducing
            # the retired multi-ID form and assert --check refuses it.
            drifted = text.replace(",3,226; 227; 310,", ",1,310,")
            if drifted == text:
                drifted = text.replace(
                    ",1,310,",
                    ",3,226; 227; 310,",
                )
            self.assertNotEqual(drifted, text)
            inv.write_text(drifted, encoding="utf-8")

            result = invoke_script("sync_inventory_mirrors.py", sandbox, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("54219", result.stderr)
            self.assertEqual(inv.read_text(encoding="utf-8"), drifted)
        finally:
            tempdir.cleanup()

    def test_sync_flags_url_contradiction_on_reviewed_status(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            inv = sandbox / "data" / "veritas_official_products.csv"
            self.make_legacy_non_primary_53062(inv)
            text = inv.read_text(encoding="utf-8")
            drifted = text.replace(",1,300,In the World But Not Of It", ",1,202,In the World But Not Of It")
            self.assertNotEqual(drifted, text)
            inv.write_text(drifted, encoding="utf-8")

            result = invoke_script("sync_inventory_mirrors.py", sandbox, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("CONTRADICTION", result.stderr)
            self.assertIn("53062", result.stderr)
            self.assertEqual(inv.read_text(encoding="utf-8"), drifted)
        finally:
            tempdir.cleanup()

    def test_sync_flags_unknown_master_id(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            inv = sandbox / "data" / "veritas_official_products.csv"
            self.make_legacy_non_primary_53062(inv)
            text = inv.read_text(encoding="utf-8")
            drifted = text.replace(",1,300,In the World But Not Of It", ",1,9999,In the World But Not Of It")
            self.assertNotEqual(drifted, text)
            inv.write_text(drifted, encoding="utf-8")

            result = invoke_script("sync_inventory_mirrors.py", sandbox)
            self.assertEqual(result.returncode, 1)
            self.assertIn("VIOLATION", result.stderr)
            self.assertIn("unknown matched master ID", result.stderr)
            self.assertEqual(inv.read_text(encoding="utf-8"), drifted)
        finally:
            tempdir.cleanup()


class DocumentationCurrencyTests(unittest.TestCase):
    """Hand-maintained status documents must not drift from the generated data."""

    def catalogue_meta(self) -> dict:
        return json.loads((REPO / "docs/catalogue-meta.json").read_text(encoding="utf-8"))

    def master_rows(self) -> list[dict[str, str]]:
        with (REPO / "data/research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def current_state_numbers(self) -> dict[str, int]:
        meta = self.catalogue_meta()
        master = self.master_rows()
        codes = len({row["catalog_code"].strip() for row in master if row["catalog_code"].strip()})
        with (REPO / "data/manual_candidate_promotions.csv").open(newline="", encoding="utf-8") as handle:
            promotions = list(csv.DictReader(handle))
        promoted = sum(1 for row in promotions if row["approval_status"].strip() == "approved")
        return {
            "master": meta["migrated_items"],
            "catalogue codes": codes,
            "exclusions": meta["master_exclusion_rows"],
            "overrides": meta["approved_source_overrides"],
            "promoted candidates": promoted,
            "unpromoted candidates": meta["reviewed_manual_candidates"] - promoted,
            "relationships": meta["reviewed_product_relationships"],
            "compilations": meta["reviewed_series_compilations"],
            "everything rows": sum(meta["everything_record_types"].values()),
        }

    def test_everything_schema_matches_everything_fields_contract(self) -> None:
        """Published Everything rows must expose exactly ``record_type`` +
        EVERYTHING_FIELDS, and every field the app.js master preset references
        (including the Expert-hidden ones) must exist on those rows.

        QA-5 regression guard (2026-08-08): legacy_title and
        proposed_filename_display were missing from docs/master.json while the
        README promised them and the Expert toggle listed them.
        """
        rows = json.loads((REPO / "docs/master.json").read_text(encoding="utf-8"))
        self.assertTrue(rows)
        expected = ["record_type"] + list(bcp.EVERYTHING_FIELDS)
        for row in rows:
            self.assertEqual(list(row.keys()), expected)
        # The master CSV must be able to source every non-derived field.
        with (REPO / "data/research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
            csv_fields = set(csv.DictReader(handle).fieldnames or [])
        self.assertLessEqual(
            set(bcp.EVERYTHING_FIELDS) - {"proposed_filename_display"},
            csv_fields,
        )
        # app.js master preset: every hidden (Expert) field must exist.
        # COLUMN_PRESETS lives in docs/js/config.js (ES module extracted 2026-08-09).
        app_js = (REPO / "docs/js/config.js").read_text(encoding="utf-8")
        if not app_js.strip():
            app_js = (REPO / "docs/app.js").read_text(encoding="utf-8")
        preset = re.search(r"master: \{.*?hidden: \[([^\]]*)\]", app_js, re.DOTALL)
        self.assertIsNotNone(preset, "app.js master preset hidden list not found")
        hidden = re.findall(r'"([a-z_0-9]+)"', preset.group(1))
        self.assertTrue(hidden, "app.js master preset hidden list is empty")
        for field in hidden:
            self.assertIn(
                field, expected,
                f"app.js Expert-column field {field!r} missing from published master.json",
            )

    def test_readme_current_state_matches_generated_data(self) -> None:
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        section = readme.split("## Current reviewed catalogue state", 1)[1].split("## ", 1)[0]
        numbers = self.current_state_numbers()
        numbers.pop("everything rows")  # README states it in the record-type table, not this section
        for label, value in numbers.items():
            self.assertIn(
                f"**{value}**", section,
                f"README 'Current reviewed catalogue state' must document {label} as **{value}**",
            )

    def test_handoff_current_state_matches_generated_data(self) -> None:
        handoff = (REPO / "NEXT_AGENT_HANDOFF.md").read_text(encoding="utf-8")
        section = handoff.split("## 3. Current verified state", 1)[1].split("## 4.", 1)[0]
        numbers = self.current_state_numbers()
        self.assertIn(f"| Curated master | {numbers['master']} |", section)
        self.assertIn(f"| Everything view | **{numbers['everything rows']}** |", section)
        self.assertIn(
            f"| Exclusions / source overrides | {numbers['exclusions']} / {numbers['overrides']} |",
            section,
        )
        self.assertIn(
            f"| Everything relationships | {numbers['relationships']} product relationships, "
            f"{numbers['compilations']} series compilations |",
            section,
        )

    def test_migration_ledger_summary_matches_ledger(self) -> None:
        with (REPO / "migration_review_ledger.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        counts = collections.Counter(row["disposition"] for row in rows)
        doc = (REPO / "MIGRATION_REVIEW_LEDGER.md").read_text(encoding="utf-8")
        table = doc.split("## Current classification summary", 1)[1].split("## ", 1)[0]
        for disposition, expected in counts.items():
            self.assertIn(f"| `{disposition}` | {expected} |", table)
        self.assertIn(f"| **Total** | **{len(rows)}** |", table)

    def test_review_overview_master_candidates_state_matches_data(self) -> None:
        """The Review-Overview 'Master Candidates' state must reflect real promotion data.

        Regression guard for the 2026-08-04 stale-label fix: the row used to
        hardcode ``reviewed_candidate / not_promoted`` even after every
        candidate was promoted. It must now be derived from the actual
        ``promotion_status`` column so it can never drift again.
        """
        overview = json.loads((REPO / "docs/review-overview.json").read_text(encoding="utf-8"))
        row = next(item for item in overview if item["review_sheet"] == "Master Candidates")
        with (REPO / "data/manual_master_candidates.csv").open(newline="", encoding="utf-8") as handle:
            candidates = list(csv.DictReader(handle))
        promoted = sum(1 for c in candidates if c.get("promotion_status", "").strip() == "promoted")
        total = len(candidates)
        self.assertEqual(row["record_count"], total)
        self.assertEqual(row["current_state"], f"{promoted}/{total} promoted")
        self.assertIn("all", row["purpose"].lower())

    def test_filename_proposal_filenames_are_globally_unique(self) -> None:
        # v4.1 guard (2026-08-07): the pipeline validator re-checks global
        # uniqueness on every build. The 2026-08-08 D-01 collapse retired the
        # 225/226/227 streaming duplicates in favour of the single promoted
        # DVD masters 311/310, so the proposal now holds exactly one filename
        # per current master with no carrier-suffix collision to resolve.
        with (REPO / "data/filename_proposal_YYYYMM.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for column in ("proposed_filename", "proposed_filename_display"):
            names = [row[column].strip() for row in rows]
            self.assertEqual(len(names), len(set(names)), f"duplicate {column} values")
        by_uuid = {row["uuid"]: row for row in rows}
        # Retired UUIDs must be gone from the proposal.
        for retired in ("225", "226", "227"):
            self.assertNotIn(retired, by_uuid)
        # The surviving single-DVD masters use plain names with the OTR prefix
        # added by the 2026-08-09 REVISION1 ODS owner revision.
        self.assertEqual(
            by_uuid["311"]["proposed_filename"],
            "2003 - OTR - Devotion to Truth Talk.mp4",
        )
        self.assertEqual(
            by_uuid["310"]["proposed_filename"],
            "2003 - OTR - Mind, Heart and Service The Pathway of Devotional Non-Duality.mp4",
        )

    def test_same_work_audiobooks_use_source_suffixes_not_audiobook_labels(self) -> None:
        """Same-carrier editions remain unique without violating the label-free rule."""
        with (REPO / "data/filename_proposal_YYYYMM.csv").open(newline="", encoding="utf-8") as handle:
            rows = {row["uuid"]: row for row in csv.DictReader(handle)}
        self.assertEqual(rows["320"]["clean_title"], "Power vs. Force")
        self.assertEqual(rows["331"]["clean_title"], "Power vs. Force")
        self.assertEqual(rows["320"]["part_index"], "")
        self.assertEqual(rows["331"]["part_total"], "")
        self.assertEqual(rows["320"]["proposed_filename"], "1995 - Power vs. Force (Audible).m4b")
        self.assertEqual(rows["331"]["proposed_filename"], "1995 - Power vs. Force (Veritas).m4b")

    def test_cleaned_multi_part_titles_keep_part_detail_in_master(self) -> None:
        """Title cleanup must not hide Part 1–3 from the edition/export contract."""
        with (REPO / "data/research_master_draft.csv").open(newline="", encoding="utf-8") as handle:
            master = {row["uuid"]: row for row in csv.DictReader(handle)}
        expected = {
            "222": "Part 1", "223": "Part 2", "224": "Part 3",
            "230": "Part 1", "231": "Part 2", "232": "Part 3",
        }
        for uuid, part in expected.items():
            self.assertEqual(master[uuid]["format"], "DVD")
            self.assertEqual(master[uuid]["format_detail"], part)

    def test_filename_uniqueness_guard_fails_on_seeded_duplicate(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            proposal = sandbox / "data/filename_proposal_YYYYMM.csv"
            text = proposal.read_text(encoding="utf-8")
            # Introduce a deliberate duplicate: rename master 310's proposed
            # filename onto master 311's. The exact 225/311 carrier-suffix
            # collision was retired by the 2026-08-08 D-01 collapse, so seed
            # the duplicate from the current clean set.
            seeded = text.replace(
                "2003 - OTR - Mind, Heart and Service The Pathway of Devotional Non-Duality.mp4",
                "2003 - OTR - Devotion to Truth Talk.mp4",
                1,
            )
            self.assertNotEqual(seeded, text)
            proposal.write_text(seeded, encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                invoke_script("build_research_master.py", sandbox, "--check")
            self.assertIn("globally unique", str(ctx.exception))
        finally:
            tempdir.cleanup()

    def test_volume_series_filename_groups_match_volume_titles(self) -> None:
        """Volume Series filenames must not merge adjacent volumes into one part set.

        Regression guard for the 2026-08-07 Volume filename drift where Volume
        III was accidentally named as Volume II parts 3/4 and Volumes VI-VII
        were accidentally named as Volume V parts 4/5 and 5/5.
        """
        with (REPO / "data/filename_proposal_YYYYMM.csv").open(newline="", encoding="utf-8") as handle:
            rows = {row["uuid"]: row for row in csv.DictReader(handle)}
        expected = {
            "202": ("Volume I: Power vs. Force Muscle Testing", "1", "2"),
            "203": ("Volume I: Power vs. Force Muscle Testing", "2", "2"),
            "204": ("Volume II: Consciousness and Addiction", "1", "2"),
            "205": ("Volume II: Consciousness and Addiction", "2", "2"),
            "206": ("Volume III: Advanced States of Consciousness", "1", "2"),
            "207": ("Volume III: Advanced States of Consciousness", "2", "2"),
            "208": ("Volume IV: Consciousness: How to Tell the Truth About Anything", "1", "2"),
            "209": ("Volume IV: Consciousness: How to Tell the Truth About Anything", "2", "2"),
            "210": ("Volume V: Undoing the Barriers to Spiritual Progress", "1", "3"),
            "211": ("Volume V: Undoing the Barriers to Spiritual Progress", "2", "3"),
            "212": ("Volume V: Undoing the Barriers to Spiritual Progress", "3", "3"),
            "213": ("Volume VI: How to Raise Your Level of Consciousness", "1", "1"),
            "214": ("Volume VII: A Conversation with Knowingness", "1", "1"),
        }
        for uuid, (clean_title, part_index, part_total) in expected.items():
            row = rows[uuid]
            self.assertEqual(row["series"], "Volume Series")
            self.assertEqual(row["clean_title"], clean_title)
            self.assertEqual(row["part_index"], part_index)
            self.assertEqual(row["part_total"], part_total)
            # Filenames sanitize the clean title per the v4 rule (`/` maps
            # to `-`; other illegal chars <>:"\|?* stripped) before adding
            # the part suffix.
            safe_title = re.sub(r'[<>:"\\|?*]', "", clean_title.replace("/", "-"))
            self.assertTrue(
                row["proposed_filename"].startswith(safe_title),
                f"UUID {uuid} filename must start with its own volume title",
            )

    def test_backfill_month_guard_skips_listing_month_for_year_mismatch(self) -> None:
        """A lecture month is backfilled from the product date only when the
        product's year matches the record's year — a 2014 storefront-listing
        month must not leak into a 2003-2005 On-the-Road record."""
        with tempfile.TemporaryDirectory() as tmp:
            inv = Path(tmp) / "veritas.csv"
            inv.write_text(
                "veritas_product_id,official_product_url,published_date\n"
                "1,https://veritaspub.com/product/x/,2014-01-13\n",
                encoding="utf-8",
            )
            original = brm.VERITAS_PRODUCTS
            brm.VERITAS_PRODUCTS = inv
            self.addCleanup(setattr, brm, "VERITAS_PRODUCTS", original)
            url = "https://veritaspub.com/product/x/"
            items = [
                # year from ledger (2003), product listed 2014 -> month stays blank
                {"item_type": "lecture", "year": "2003", "month": "",
                 "source_url_veritas": url, "legacy_tempid": ""},
                # year matches product year -> month backfilled
                {"item_type": "lecture", "year": "2014", "month": "",
                 "source_url_veritas": url, "legacy_tempid": ""},
                # no year -> both year and month derive from the product date
                {"item_type": "lecture", "year": "", "month": "",
                 "source_url_veritas": url, "legacy_tempid": ""},
            ]
            brm.backfill_months_from_official_source(items)
        self.assertEqual(items[0]["year"], "2003")
        self.assertEqual(items[0]["month"], "", "listing month must not leak into a 2003 record")
        self.assertEqual(items[1]["year"], "2014")
        self.assertEqual(items[1]["month"], "01", "matching-year product month is backfilled")
        self.assertEqual(items[2]["year"], "2014")
        self.assertEqual(items[2]["month"], "01")

    def test_official_title_cleanup_only_changes_matching_titles(self) -> None:
        """Title hygiene is evidence-based: strip PART/DVD noise only when the
        cleaned title matches the official Veritas listing; otherwise keep the
        current title. The raw verbatim text stays in ``legacy_title``."""
        by_url = [
            {"official_product_url": "https://veritaspub.com/product/posa/",
             "official_title": "The Presence of Spiritual Awareness"},
            {"official_product_url": "https://veritaspub.com/product/vpf/",
             "official_title": "Volume I: Power vs. Force Muscle Testing"},
        ]
        items = [
            # PART noise, cleaned form matches official -> cleaned
            {"item_type": "lecture", "title": "The Presence of Spiritual Awareness PART1",
             "legacy_title": "The Presence of Spiritual Awareness PART1",
             "source_url_veritas": "https://veritaspub.com/product/posa/"},
            # PART noise, cleaned form does NOT match official -> kept
            {"item_type": "lecture", "title": "Volume I-Power vs Force (Part 1)",
             "legacy_title": "Volume I-Power vs Force (Part 1)",
             "source_url_veritas": "https://veritaspub.com/product/vpf/"},
            # non-lecture never touched
            {"item_type": "book", "title": "Power vs Force (Part 1)", "legacy_title": "",
             "source_url_veritas": "https://veritaspub.com/product/vpf/"},
        ]
        brm.apply_official_title_cleanup(items, by_url)
        self.assertEqual(items[0]["title"], "The Presence of Spiritual Awareness")
        self.assertIn("Title cleaned against official listing: The Presence of Spiritual Awareness",
                      items[0]["notes"])
        self.assertEqual(items[0]["legacy_title"], "The Presence of Spiritual Awareness PART1")
        self.assertEqual(items[1]["title"], "Volume I-Power vs Force (Part 1)",
                         "a non-matching cleaned title must be left unchanged")
        self.assertEqual(items[2]["title"], "Power vs Force (Part 1)")

    def test_books_use_first_publication_year_not_product_listing(self) -> None:
        """Book ``year`` must be the work's first publication year.

        Regression guard for the 2026-08-04 fix: the Veritas storefront lists a
        whole batch of books with ``published_date`` 2014-03-30 (the day they
        appeared on the site), which is not when they were first published.
        ``build_research_master.backfill_months_from_official_source`` now
        skips ``item_type='book'`` rows entirely, and book years come only from
        the reviewed ledger / candidate inputs. This pins the classic titles to
        their documented first-publication years so the product-listing date
        cannot silently creep back in.
        """
        master = {row["uuid"].strip(): row for row in self.master_rows()}
        expected = {
            "286": "1995",  # Power vs Force (product-listing date was 2014)
            "287": "2001",  # The Eye of the I
            "288": "2003",  # I: Reality and Subjectivity
            "289": "2005",  # Truth vs Falsehood
            "290": "2012",  # Letting Go
            "291": "2009",  # Healing and Recovery
            "293": "2008",  # Reality, Spirituality and Modern Man
            "294": "2006",  # Transcending the Levels of Consciousness
            "316": "2021",  # The Ego is Not the Real You (Hay House)
        }
        for uuid, year in expected.items():
            row = master.get(uuid)
            self.assertIsNotNone(row, f"expected a master record for UUID {uuid}")
            self.assertEqual(
                row["year"], year,
                f"master {uuid} ({row['title']!r}) must use its first-publication year {year}",
            )
        # Book rows (including audiobook/carrier editions) never get a
        # catalogue code; codes exist for lecture/discussion only.
        coded_books = [
            (row["uuid"], row["title"])
            for row in self.master_rows()
            if row["item_type"].strip() == "book" and row["catalog_code"].strip()
        ]
        self.assertEqual(coded_books, [], "book rows must never receive a catalogue code")


class OwnerOverrideAndDisplayOrderTests(unittest.TestCase):
    """Owner-reviewed overrides (year/notes) and the REVISION1 display order."""

    ORDER_HEADER = "uuid,block_id,block_position,review_status,reviewed_on,note"

    def test_master_json_follows_committed_display_order(self) -> None:
        """The published Everything view must match the reviewed display order.

        REVISION1 ODS rule: 2002-2011 lectures first, then the colour-group
        blocks (discussion, satsang, on-the-road, volume, office, books,
        transcription, media-misc), then undecided rows, and Fran Grace last.
        """
        with (REPO / "data/catalogue_display_order.csv").open(encoding="utf-8", newline="") as handle:
            order = list(csv.DictReader(handle))
        self.assertEqual(len(order), 363)
        rows = json.loads((REPO / "docs/master.json").read_text(encoding="utf-8"))
        self.assertEqual([row["uuid"] for row in rows], [row["uuid"] for row in order])
        blocks = [row["block_id"] for row in order]
        self.assertEqual(blocks[0], "lectures-2002-2011")
        self.assertEqual(blocks[-1], "fran-grace")
        self.assertEqual(rows[-1]["title"], "The Power of Love: A Transformed Heart Changes the World")
        # block positions are dense within each block
        from collections import Counter
        counts = Counter(blocks)
        seen: dict[str, int] = {}
        for row in order:
            seen[row["block_id"]] = seen.get(row["block_id"], 0) + 1
            self.assertEqual(int(row["block_position"]), seen[row["block_id"]])
        self.assertEqual(sum(counts.values()), 363)

    def test_display_order_duplicate_uuid_fails_build(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            order = (sandbox / "data/catalogue_display_order.csv").read_text(encoding="utf-8")
            lines = order.splitlines()
            lines.append(lines[1])  # duplicate the first uuid row
            (sandbox / "data/catalogue_display_order.csv").write_text(
                "\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                invoke_script("build_catalogue_pages.py", sandbox, "--check")
            self.assertIn("duplicates UUID", str(ctx.exception))
        finally:
            tempdir.cleanup()

    def test_display_order_missing_uuid_fails_build(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            order = (sandbox / "data/catalogue_display_order.csv").read_text(encoding="utf-8")
            lines = [line for line in order.splitlines() if not line.startswith("1,")]
            (sandbox / "data/catalogue_display_order.csv").write_text(
                "\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                invoke_script("build_catalogue_pages.py", sandbox, "--check")
            self.assertIn("missing master UUID", str(ctx.exception))
        finally:
            tempdir.cleanup()

    def test_year_and_notes_overrides_apply(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            (sandbox / "data/master_year_overrides.csv").write_text(
                "uuid,year,month,year_source,review_status,reviewed_on,reason\n"
                "230,2004,03,Test override year,approved,2026-08-09,fixture\n"
                "356,,,\"Blank: owner revision (REVISION1 ODS, 2026-08-09)\",approved,2026-08-09,committed\n"
                "357,2003,,\"Owner revision: 2003 (REVISION1 ODS, 2026-08-09)\",approved,2026-08-09,committed\n"
                "358,,,\"Blank: owner revision (REVISION1 ODS, 2026-08-09)\",approved,2026-08-09,committed\n",
                encoding="utf-8")
            # The filename proposal mirrors the final master year/month, so
            # keep the proposal row for 230 in sync with the override.
            proposal = sandbox / "data/filename_proposal_YYYYMM.csv"
            proposal.write_text(
                proposal.read_text(encoding="utf-8")
                .replace(
                    "230,w-verification-of-spiritual-realities,lecture,On The Road Talk Series,,,DVD,",
                    "230,w-verification-of-spiritual-realities,lecture,On The Road Talk Series,2004,03,DVD,",
                ),
                encoding="utf-8",
            )
            (sandbox / "data/master_notes_overrides.csv").write_text(
                "uuid,notes,review_status,reviewed_on,reason\n"
                "1,TEST NOTE OVERRIDE,approved,2026-08-09,fixture\n"
                "315,FRAN GRACE,approved,2026-08-09,committed\n",
                encoding="utf-8")
            result = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(result.returncode, 0)
            with (sandbox / "data/research_master_draft.csv").open(encoding="utf-8", newline="") as handle:
                rows = {row["uuid"]: row for row in csv.DictReader(handle)}
            self.assertEqual(rows["230"]["year"], "2004")
            self.assertEqual(rows["230"]["month"], "03")
            self.assertEqual(rows["230"]["year_source"], "Test override year")
            self.assertEqual(rows["1"]["notes"], "")
            self.assertEqual(rows["1"]["research"], "TEST NOTE OVERRIDE")
            # committed REVISION1 overrides still apply in the same build
            self.assertEqual(rows["357"]["year"], "2003")
            self.assertEqual(rows["357"]["year_source"], "Owner revision: 2003 (REVISION1 ODS, 2026-08-09)")
            self.assertEqual(rows["315"]["notes"], "FRAN GRACE")
        finally:
            tempdir.cleanup()

    def test_override_rejects_unknown_uuid(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            (sandbox / "data/master_year_overrides.csv").write_text(
                "uuid,year,month,year_source,review_status,reviewed_on,reason\n"
                "9999,2004,,Test,approved,2026-08-09,fixture\n",
                encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                invoke_script("build_research_master.py", sandbox)
            self.assertIn("not a master record", str(ctx.exception))
        finally:
            tempdir.cleanup()

    def test_override_rejects_unapproved_row(self) -> None:
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            (sandbox / "data/master_notes_overrides.csv").write_text(
                "uuid,notes,review_status,reviewed_on,reason\n"
                "1,NOT APPROVED,pending,2026-08-09,fixture\n",
                encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                invoke_script("build_research_master.py", sandbox)
            self.assertIn("is not approved", str(ctx.exception))
        finally:
            tempdir.cleanup()


class DefensiveDepthTests(unittest.TestCase):
    """Additional fail-safe tests for defensive-in-depth coverage."""

    def test_edition_promotions_uuid_stability(self) -> None:
        """Edition promotion UUIDs must be stable across rebuilds."""
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            # Build twice from identical inputs
            result1 = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(result1.returncode, 0, result1.stderr)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as f:
                rows1 = {r["uuid"]: r for r in csv.DictReader(f)}
            
            result2 = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(result2.returncode, 0, result2.stderr)
            with (sandbox / "data" / "research_master_draft.csv").open(newline="", encoding="utf-8") as f:
                rows2 = {r["uuid"]: r for r in csv.DictReader(f)}
            
            # Edition rows are identified by candidate_key, while UUIDs stay compact numeric IDs.
            edition_rows1 = {
                uuid: row for uuid, row in rows1.items()
                if row["candidate_key"].startswith("candidate:edition-")
            }
            edition_rows2 = {
                uuid: row for uuid, row in rows2.items()
                if row["candidate_key"].startswith("candidate:edition-")
            }
            self.assertTrue(edition_rows1, "fixture must include promoted edition rows")
            self.assertEqual(set(edition_rows1), set(edition_rows2), "Edition UUIDs drifted across rebuilds")
            
            # Verify the actual edition rows are identical
            for uuid in edition_rows1:
                self.assertEqual(rows1[uuid], rows2[uuid], f"Edition row {uuid} changed across rebuilds")
        finally:
            tempdir.cleanup()

    def test_source_override_idempotency(self) -> None:
        """Applying the same approved override twice must produce identical output."""
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            # Write an approved override
            header = "raw_row_number,target_field,override_value,review_status,approval_date,review_reason,evidence_source"
            row = "328,source_url_hay_house,https://www.hayhouse.com/truth-vs-falsehood-parperback/,approved,2026-08-03,same-carrier paperback link,data/hayhouse_official_products.csv"
            (sandbox / "data" / "research_master_source_overrides.csv").write_text(
                f"{header}\n{row}\n", encoding="utf-8"
            )
            # This fixture intentionally replaces the full source-override
            # layer with a one-row test file, so remove the optional filename
            # proposal input whose metadata mirrors depend on the full layer.
            (sandbox / "data" / "filename_proposal_YYYYMM.csv").unlink(missing_ok=True)
            
            # Build twice
            result1 = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(result1.returncode, 0, result1.stderr)
            output1 = (sandbox / "data" / "research_master_draft.csv").read_text(encoding="utf-8")
            
            result2 = invoke_script("build_research_master.py", sandbox)
            self.assertEqual(result2.returncode, 0, result2.stderr)
            output2 = (sandbox / "data" / "research_master_draft.csv").read_text(encoding="utf-8")
            
            self.assertEqual(output1, output2, "Source override application is not idempotent")
        finally:
            tempdir.cleanup()

    def test_missing_required_column_gives_clear_error(self) -> None:
        """Missing required columns must fail with a clear error message."""
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            # Remove a required column from work_families.csv
            work_families = (sandbox / "data" / "work_families.csv").read_text(encoding="utf-8")
            lines = work_families.split("\n")
            # Remove the 'review_status' column from header and first data row
            header_cols = lines[0].split(",")
            if "review_status" in header_cols:
                idx = header_cols.index("review_status")
                lines[0] = ",".join(header_cols[:idx] + header_cols[idx+1:])
                if len(lines) > 1 and lines[1]:
                    data_cols = lines[1].split(",")
                    lines[1] = ",".join(data_cols[:idx] + data_cols[idx+1:])
            (sandbox / "data" / "work_families.csv").write_text("\n".join(lines), encoding="utf-8")
            
            # The build raises ValueError with a clear message about the missing column
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_untyped_master_record_not_allowed(self) -> None:
        """Every master record must have a content class — no untyped exceptions."""
        item = {"uuid": "999", "title": "Some Title", "item_type": "", "work_id": "w-test"}
        with self.assertRaisesRegex(ValueError, "every master record must have a content class"):
            brm.validate_master_items_integrity([item])

    def test_malformed_work_id_fails_integrity(self) -> None:
        """A work_id not starting with 'w-' must fail integrity validation."""
        item = {"uuid": "100", "title": "Title", "item_type": "lecture", "work_id": "invalid-prefix"}
        with self.assertRaisesRegex(ValueError, "work_ids must start with 'w-'"):
            brm.validate_master_items_integrity([item])

    def test_missing_work_id_fails_catalogue_build(self) -> None:
        """Every master record in catalogue Pages build must have a work_id."""
        item = {"uuid": "100", "title": "Title", "item_type": "lecture", "work_id": ""}
        with self.assertRaisesRegex(ValueError, "has a missing work_id"):
            bcp.validate_work_family_coverage([item])

    def test_filename_proposal_group_coherence_fails(self) -> None:
        """A filename-proposal row may not join another title's part group.

        Regression guard for the 2026-08-07 Volume-Series fold (UUIDs 213/214
        were reviewed into Volume V's part set as ``[4/5]``/``[5/5]`` and
        UUIDs 206/207 into Volume II's ``[3/4]``/``[4/4]``): the builder
        applies the reviewed CSV verbatim, so incoherent part groups must
        fail the build instead of silently minting nonsense filenames.
        """
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            path = sandbox / "data" / "filename_proposal_YYYYMM.csv"
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            for row in rows:
                if row["uuid"] == "213":
                    # Reproduce the historical fold: the Volume VI row joins
                    # the Volume V part set as part 4 of 5.
                    row["clean_title"] = "Volume V Undoing the Barriers to Spiritual Progress"
                    row["part_index"] = "4"
                    row["part_total"] = "5"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "not derived from its own title"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_filename_proposal_part_index_out_of_range_fails(self) -> None:
        """part_index may never exceed part_total in the reviewed proposal."""
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            path = sandbox / "data" / "filename_proposal_YYYYMM.csv"
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            for row in rows:
                if row["uuid"] == "1":
                    row["part_index"] = "4"  # part_total is 3
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "exceeds part_total"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()


class FrontendDeliveryContractTests(unittest.TestCase):
    """Keep Pages asset URLs, the visible build ID, and manifest in lockstep."""

    @staticmethod
    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_versioned_assets_and_visible_manifest_match_committed_bytes(self) -> None:
        index = (REPO / "docs/index.html").read_text(encoding="utf-8")
        manifest = json.loads((REPO / "docs/build-manifest.json").read_text(encoding="utf-8"))

        expected = {
            "app.js": self.sha256(REPO / "docs/app.js"),
            "style.css": self.sha256(REPO / "docs/style.css"),
        }
        for filename, digest in expected.items():
            match = re.search(rf'{re.escape(filename)}\?v=([0-9a-f]{{12}})', index)
            self.assertIsNotNone(match, f"{filename} must have a 12-character content version")
            self.assertEqual(match.group(1), digest[:12], f"stale cache version for {filename}")
            self.assertEqual(manifest["assets"][filename], digest)

        expected_data = {
            "master.json": self.sha256(REPO / "docs/master.json"),
            "data.json": self.sha256(REPO / "docs/data.json"),
        }
        # The catalogue-block-map drives per-row block colours in the
        # Everything view (getRowBlockId in docs/js/formatters.js). A stale
        # block map paired with a fresh app.js would silently mis-render the
        # 11 colour washes, so the manifest contract now records its hash
        # alongside the master/data payloads.
        expected_data["catalogue-block-map.json"] = self.sha256(
            REPO / "docs/catalogue-block-map.json"
        )
        self.assertEqual(manifest["data"], expected_data)
        visible_revision = f"app-{expected['app.js'][:12]}/css-{expected['style.css'][:12]}"
        self.assertIn(f'id="build-revision">{visible_revision}</code>', index)
        self.assertIn('href="build-manifest.json"', index)
        self.assertEqual(manifest["acceptance"], "owner_visual_review_required")

    def test_block_map_drift_fails_manifest_contract(self) -> None:
        """A drift between the block map and its manifest hash must fail loudly.

        The catalogue-block-map is build-emitted by build_catalogue_pages.py
        from data/catalogue_display_order.csv. A hand-edit to the block map
        without bumping the manifest hash would silently mis-render the
        11 colour washes in the Everything view; this test re-reads the
        actual file, recomputes its hash, and compares against the manifest
        entry to catch that drift directly.
        """
        block_map_path = REPO / "docs/catalogue-block-map.json"
        if not block_map_path.exists():
            self.fail("catalogue-block-map.json must exist for this contract to be testable")
        manifest = json.loads((REPO / "docs/build-manifest.json").read_text(encoding="utf-8"))
        self.assertIn(
            "catalogue-block-map.json", manifest.get("data", {}),
            "build-manifest.json must record the catalogue-block-map hash in its data section",
        )
        self.assertEqual(
            manifest["data"]["catalogue-block-map.json"],
            self.sha256(block_map_path),
            "catalogue-block-map.json drifted from its manifest hash; rebuild the manifest",
        )

    def test_app_js_declares_critical_module_scope_variables(self) -> None:
        """Critical module-scope identifiers must be declared with let/var/const.

        Regression guard for the 019fe8d0 P0 incident: the 019fe8a5 ES-module
        refactor of docs/app.js dropped the `let table = null;` and
        `let allData = [];` declarations that lived at IIFE scope in the
        pre-modular version. The page then failed silently on the first
        ``boot()`` call (``ReferenceError: table is not defined``) and the
        browser stayed on the static "Loading research master…" skeleton
        forever.

        A future refactor that re-introduces a free-variable reference to
        one of these critical module-scope identifiers must fail this test
        before it can ship.
        """
        app_js = (REPO / "docs/app.js").read_text(encoding="utf-8")

        # The critical module-scope state. `table` holds the active Tabulator
        # instance, `allData` holds the current view's data array. Both must
        # be declared inside the IIFE so their references resolve.
        critical = ("table", "allData")
        # Match the variable name as the LHS of a let/var/const declaration
        # at IIFE scope (whitespace + `let` + whitespace + the name + ...).
        # We do not match imports (which use `as`) or destructuring (which
        # uses commas), so a positive match means the IIFE declares the
        # variable as a let/var/const at its top level.
        missing = [
            name for name in critical
            if not re.search(rf"^\s+(?:let|var|const)\s+{re.escape(name)}\b", app_js, re.MULTILINE)
        ]
        self.assertEqual(
            missing, [],
            f"docs/app.js must declare these critical module-scope identifiers "
            f"at IIFE scope; a free-variable reference will throw ReferenceError "
            f"on first use and silently break the page. Missing: {missing}",
        )

    def test_app_js_invokes_every_named_import(self) -> None:
        """Every destructured import in app.js must be used (called or read).

        Regression guard for the 019fe8d0 follow-up P0 incident: the 019fe8a5
        ES-module refactor of `docs/app.js` imported `loadCatalogueBlockMap`
        from `./js/formatters.js` but never called it. The block map singleton
        therefore stayed empty, every row fell back to ``data-block="undecided"``,
        and the 25/25 Playwright computed-style specs failed. A second P0 hotfix
        caught it. This test fails any future refactor that leaves a named
        import unused.

        Matches the `import { A, B, C } from "...";` block at the top of
        app.js and asserts that every destructured name appears as a token
        later in the file. This is approximate (it does not differentiate
        a call from a property access) but it catches the imported-but-
        never-called class of error.
        """
        app_js = (REPO / "docs/app.js").read_text(encoding="utf-8")
        # Extract the import block: from `import {` to the matching `};`.
        match = re.search(r"^import\s*\{([^}]*)\}\s*from\s*[\"'][^\"']*[\"'];",
                          app_js, re.MULTILINE | re.DOTALL)
        if not match:
            self.fail("docs/app.js must start with at least one `import {...}` block")
        names = [n.strip() for n in match.group(1).split(",") if n.strip()]
        self.assertTrue(names, "the import block must list at least one name")
        # Strip the import block out of the rest of the file so the "usage"
        # check doesn't see the import line itself.
        rest = app_js[match.end():]
        unused = [
            name for name in names
            if not re.search(rf"\b{re.escape(name)}\b", rest)
        ]
        self.assertEqual(
            unused, [],
            f"docs/app.js imports {unused} but never references them; "
            f"an unused import typically means a forgotten call (e.g. "
            f"loadCatalogueBlockMap in the 019fe8d0 follow-up P0). The "
            f"fix is either to invoke the import or remove it from the "
            f"destructuring list.",
        )


class RetiredVocabularyTests(unittest.TestCase):
    """The deprecated medium item types (audio/video) were retired 2026-08-03.

    Retirement means the validators now actively reject them: a review-input
    row reintroducing a medium value as ``item_type`` must fail the build
    loudly (the carrier belongs in ``format`` instead).
    """

    def test_vocabulary_excludes_medium_values(self) -> None:
        self.assertNotIn("audio", brm.CONTENT_ITEM_TYPES)
        self.assertNotIn("video", brm.CONTENT_ITEM_TYPES)

    def test_committed_review_inputs_are_vocabulary_clean(self) -> None:
        """No item_type field in any committed review input may use a medium value.

        Exception: ``official_discovery_queue.csv`` is an unreviewed triage
        lane whose free-text ``item_type`` describes what a listing appears
        to be (four Nightingale-Conant `audio` rows pending an owner
        content-class ruling); the controlled vocabulary governs master,
        candidate, promotion, and ledger lanes only.
        """
        exempt = {"official_discovery_queue.csv"}
        for path in (REPO / "data").glob("*.csv"):
            if path.name in exempt:
                continue
            with path.open(newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    for field, value in row.items():
                        if field and "item_type" in field:
                            self.assertNotIn(
                                (value or "").strip(),
                                {"audio", "video"},
                                f"{path}:{field} reintroduced a retired medium item_type",
                            )
        with (REPO / "migration_review_ledger.csv").open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                self.assertNotIn(
                    (row.get("proposed_item_type") or "").strip(),
                    {"audio", "video"},
                    "migration_review_ledger.csv reintroduced a retired medium item_type",
                )

    def test_manual_candidate_medium_item_type_fails_build(self) -> None:
        """A manual candidate proposing item_type=audio must fail validation."""
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            row = ("manual-veritas-99998,Retired Type Probe,audio,,CD,,,veritas,99998,"
                   "https://veritaspub.com/test,Probe,evidence,reviewed_candidate,"
                   "2026-08-03,not_promoted,probe")
            with (sandbox / "data" / "manual_master_candidates.csv").open("a", encoding="utf-8") as handle:
                handle.write(f"{row}\n")
            with self.assertRaisesRegex(ValueError, "valid proposed_item_type"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_ledger_medium_item_type_fails_build(self) -> None:
        """A ledger row proposing item_type=video must fail validation."""
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            ledger_path = sandbox / "migration_review_ledger.csv"
            with ledger_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
                columns = rows[0].keys()
            # Only disposition="item" rows are validated by build_master().
            item_row = next(row for row in rows if row["disposition"] == "item")
            item_row["proposed_item_type"] = "video"
            with ledger_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "unsupported proposed_item_type"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()

    def test_ledger_owned_casing_fails_build(self) -> None:
        """A ledger row with mixed-case proposed_owned must fail validation."""
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            ledger_path = sandbox / "migration_review_ledger.csv"
            with ledger_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
                columns = rows[0].keys()
            item_row = next(row for row in rows if row["disposition"] == "item")
            item_row["proposed_owned"] = "True"
            with ledger_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "proposed_owned must be blank, true, or false"):
                invoke_script("build_research_master.py", sandbox)
        finally:
            tempdir.cleanup()


class ViewsConfigConsistencyTests(unittest.TestCase):
    """docs/js/config.js#VIEWS must cover every view JSON the build emits.

    Without this contract, a new view added to build_catalogue_pages.py (an
    additional OUT_* path) could land in docs/ as a JSON file the Jump-to
    dropdown never offers — and conversely the VIEWS list could reference a
    file the build stopped producing. Either failure mode is a silent UX bug;
    this test parses the static VIEWS object from the ES module and asserts
    it matches the build's actual output set.
    """

    @staticmethod
    def parse_views_files(config_path: Path) -> set[str]:
        """Extract every ``file: "<name>.json"`` value from VIEWS.

        Avoids a Node dependency by regex-parsing the small, well-formed ES
        module. The regex is anchored to the VIEWS object literal so an
        identical ``file:`` line elsewhere in the module would not match.
        """
        text = config_path.read_text(encoding="utf-8")
        # Match the VIEWS object literal and capture every file: "*.json" pair.
        match = re.search(
            r"export const VIEWS = \{(?P<body>.*?)\n?\};",
            text, re.DOTALL,
        )
        assert match is not None, "docs/js/config.js must export a VIEWS object literal"
        files = set(re.findall(r'file:\s*"([^"]+\.json)"', match.group("body")))
        assert files, "VIEWS must contain at least one file: \"*.json\" entry"
        return files

    def test_views_covers_every_user_facing_catalogue_output(self) -> None:
        """VIEWS file keys must equal the set of build-emitted user-facing JSONs.

        Non-user-facing build outputs (catalogue-meta.json + catalogue-block-map.json)
        and the contract manifest (build-manifest.json) are intentionally
        excluded: they are loaded by the app but not exposed as Jump-to entries.
        """
        views_files = self.parse_views_files(REPO / "docs/js/config.js")

        # The build's declared output paths (paths are Path objects; we want
        # the relative file names so the contract reads naturally).
        declared_outputs = {
            path.name
            for name in (
                "OUT_MASTER", "OUT_REVIEW_OVERVIEW", "OUT_MANUAL_CANDIDATES",
                "OUT_MANUAL_LEADS", "OUT_MASTER_EXCLUSIONS", "OUT_MIGRATION_REVIEW",
                "OUT_SOURCE_OVERRIDES", "OUT_OFFICIAL_DISCOVERY",
                "OUT_NEW_WORK_REVIEW", "OUT_VERITAS_MAPPING_DECISIONS",
                "OUT_VERITAS_PRODUCTS", "OUT_PRODUCT_RELATIONSHIPS",
                "OUT_SERIES_COMPILATIONS", "OUT_HAYHOUSE_PRODUCTS",
                "OUT_AUDIBLE_PRODUCTS", "OUT_INTERNATIONAL",
                "OUT_FILENAME_PROPOSAL", "OUT_PUBLISHERS",
            )
            for path in (getattr(bcp, name),)
        }
        # data.json is the raw pass-through output, not a bcp OUT_*; add it.
        declared_outputs.add("data.json")

        non_viewing = {"catalogue-meta.json", "catalogue-block-map.json", "build-manifest.json"}
        user_facing = declared_outputs - non_viewing

        self.assertEqual(
            views_files, user_facing,
            f"VIEWS file set drifted from build outputs.\n"
            f"  In VIEWS but not built: {views_files - user_facing}\n"
            f"  Built but not in VIEWS: {user_facing - views_files}",
        )

    def test_views_file_exists_in_docs(self) -> None:
        """Every file named in VIEWS must actually be present in docs/.

        Catches a "VIEWS list grew but the JSON was never published" failure
        mode (e.g. a new view added to VIEWS without running the build).
        """
        views_files = self.parse_views_files(REPO / "docs/js/config.js")
        docs_dir = REPO / "docs"
        missing = sorted(name for name in views_files if not (docs_dir / name).exists())
        self.assertEqual(
            missing, [],
            f"VIEWS references JSON files that docs/ does not contain: {missing}",
        )

    def test_no_duplicate_file_keys_in_views(self) -> None:
        """VIEWS must not list the same JSON file under two view keys.

        A duplicate `file:` would silently overwrite one view's data with
        another's; the Jump-to dropdown would show both labels but only
        load one set of rows. The one legitimate exception is
        ``master`` + ``series`` both pointing at ``master.json``: the
        Series tab is a card browser over the same payload, a documented
        design choice. If any other file is shared, that is a real bug.
        """
        text = (REPO / "docs/js/config.js").read_text(encoding="utf-8")
        match = re.search(
            r"export const VIEWS = \{(?P<body>.*?)\n?\};",
            text, re.DOTALL,
        )
        assert match is not None
        entries = re.findall(
            r'^\s*(\w+):\s*\{[^}]*file:\s*"([^"]+\.json)"',
            match.group("body"), re.MULTILINE,
        )
        from collections import Counter
        counts = Counter(name for _, name in entries)
        # Documented exception: master + series share master.json because
        # the Series tab is a card browser over the same payload.
        allowed = {"master.json"}
        dupes = {
            name: n for name, n in counts.items() if n > 1 and name not in allowed
        }
        self.assertEqual(
            dupes, {},
            f"VIEWS must not list the same JSON file under multiple view keys: {dupes}",
        )
        # And pin the documented exception so it cannot silently grow.
        self.assertEqual(
            counts.get("master.json", 0), 2,
            "master + series both point at master.json (documented); if this changes, "
            "update the test and document the new exception.",
        )


if __name__ == "__main__":
    unittest.main()
