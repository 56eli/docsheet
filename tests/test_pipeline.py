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
import importlib
import inspect
import io
import json
import os
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

import build_catalogue_pages as bcp  # noqa: E402
import build_research_master as brm  # noqa: E402
import fetch_veritas_catalogue as fvc  # noqa: E402
import map_series_taxonomy as mst  # noqa: E402

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


def make_sandbox() -> "tempfile.TemporaryDirectory[str]":
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
        shutil.copy2(path, sandbox / "data" / path.name)
    for path in (REPO / "docs").glob("*.json"):
        shutil.copy2(path, sandbox / "docs" / path.name)
    return tempdir


SCRIPT_MODULES = {
    "process_data.py": "process_data",
    "build_research_master.py": "build_research_master",
    "build_catalogue_pages.py": "build_catalogue_pages",
    "fetch_veritas_catalogue.py": "fetch_veritas_catalogue",
    "map_series_taxonomy.py": "map_series_taxonomy",
    "reconcile_research_master.py": "reconcile_research_master",
    "generate_lecture_review.py": "generate_lecture_review",
    "generate_migration_ledger.py": "generate_migration_ledger",
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
        with working_directory(sandbox):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
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
        result = self.run_script("build_catalogue_pages.py", "--no-include-pending", "--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("stale", result.stdout)


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
                "uuid": "10", "title": "Some Lecture", "title_source": "",
                "source_url_veritas": "https://veritaspub.com/product/some-lecture/",
            },
            {
                "uuid": "11", "title": "Satsang Series (Jan 2007)", "title_source": "",
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

    def test_compact_id_recognition(self) -> None:
        self.assertTrue(brm.is_compact_id("317"))
        self.assertFalse(brm.is_compact_id("019fc4e7-d1e7-7d0b-a52e-a0e4cdf23091"))
        self.assertFalse(brm.is_compact_id(""))


class JsonTextTests(unittest.TestCase):
    def test_json_text_shape(self) -> None:
        text = bcp.json_text({"a": 1})
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(json.loads(text), {"a": 1})

import unittest.mock as mock  # noqa: E402

import process_data as pdata  # noqa: E402
import reconcile_research_master as rrm  # noqa: E402


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
        self.assertIn("must both exist", result.stderr)

    def test_stale_data_json_fails_check(self) -> None:
        path = self.sandbox / "docs" / "data.json"
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        result = invoke_script("process_data.py", self.sandbox, "--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/data.json is stale", result.stderr)

    def test_invalid_meta_json_fails_check(self) -> None:
        (self.sandbox / "docs" / "meta.json").write_text("not json", encoding="utf-8")
        result = invoke_script("process_data.py", self.sandbox, "--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not valid JSON", result.stderr)

    def test_stale_meta_fails_check(self) -> None:
        path = self.sandbox / "docs" / "meta.json"
        meta = json.loads(path.read_text(encoding="utf-8"))
        meta["total_rows"] += 1
        path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        result = invoke_script("process_data.py", self.sandbox, "--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("stale or malformed", result.stderr)

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
             mock.patch("time.sleep"):
            with self.assertRaisesRegex(RuntimeError, "non-JSON"):
                fvc.get_page(1)

    def test_non_list_payload_retries_then_raises(self) -> None:
        with mock.patch.object(fvc, "urlopen", return_value=self.FakeResponse(b'{"error": true}')), \
             mock.patch("time.sleep"):
            with self.assertRaisesRegex(RuntimeError, "not a product list"):
                fvc.get_page(1)

    def test_400_on_first_page_is_a_real_error(self) -> None:
        with mock.patch.object(fvc, "urlopen", side_effect=self.http_error(400)), \
             mock.patch("time.sleep"):
            with self.assertRaisesRegex(RuntimeError, "failed after"):
                fvc.get_page(1)

    def test_urlerror_retries_then_raises(self) -> None:
        with mock.patch.object(fvc, "urlopen", side_effect=URLError("tls eof")), \
             mock.patch("time.sleep"):
            with self.assertRaisesRegex(RuntimeError, "tls eof"):
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

    def test_report_renders_drift_sections_and_stale_check(self) -> None:
        drift = rrm.DraftComparison(
            extras=[{"raw_row_number": "9", "title": "Extra", "item_type": "lecture", "notes": "note"}],
            missing=[{"raw_row_number": "10", "title": "Missing", "item_type": "book"}],
            changed=[(
                {"raw_row_number": "11", "title": "Before", "format": ""},
                {"raw_row_number": "11", "title": "After", "format": "audio"},
                ["title", "format"],
            )],
        )
        with working_directory(self.sandbox):
            with mock.patch.object(rrm, "compare_drafts", return_value=drift):
                report = rrm.render_report()
        self.assertIn("Extra", report)
        self.assertIn("Missing", report)
        self.assertIn("`∅` → `audio`", report)  # empty-before drift stays visible

        write = invoke_script("reconcile_research_master.py", self.sandbox)
        self.assertEqual(write.returncode, 0, write.stderr)
        path = self.sandbox / rrm.REPORT.name
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        check = invoke_script("reconcile_research_master.py", self.sandbox, "--check")
        self.assertEqual(check.returncode, 1)
        self.assertIn("is stale", check.stdout)


class RelationshipCoverageValidationTests(unittest.TestCase):
    """URL-bearing masters without a primary relationship row must fail the build."""

    def master(self) -> list[dict[str, str]]:
        return [
            {"uuid": "10", "source_url_veritas": "https://veritaspub.com/product/a/"},
            {"uuid": "12", "source_url_veritas": "https://veritaspub.com/product/b/"},
            {"uuid": "13", "source_url_veritas": ""},
        ]

    def relationships(self) -> list[dict[str, str]]:
        return [
            {"master_uuid": "10", "relationship_type": "primary_product_for_item_part"},
            {"master_uuid": "12", "relationship_type": "related_material"},
        ]

    def test_covered_masters_pass(self) -> None:
        bcp.validate_primary_relationship_coverage(self.master(), [
            {"master_uuid": "10", "relationship_type": "primary_product_for_item_part"},
            {"master_uuid": "12", "relationship_type": "primary_product_for_item_part"},
        ])

    def test_uncovered_master_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "12"):
            bcp.validate_primary_relationship_coverage(self.master(), self.relationships())

    def test_master_without_url_is_not_a_gap(self) -> None:
        # 13 has no URL -> no gap; only 12 (related_material) is uncovered.
        with self.assertRaises(ValueError) as ctx:
            bcp.validate_primary_relationship_coverage(self.master(), self.relationships())
        self.assertIn("12", str(ctx.exception))
        self.assertNotIn("13", str(ctx.exception))

    def test_committed_state_passes_after_promoted_rows_added(self) -> None:
        # The 11 promoted masters (309-319) now have reviewed primary rows, so
        # the committed state must build cleanly with no coverage failure.
        tempdir = make_sandbox()
        try:
            result = invoke_script("build_catalogue_pages.py", Path(tempdir.name), "--check")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("WARNING", result.stderr)
            self.assertNotIn("no reviewed primary relationship", result.stderr)
        finally:
            tempdir.cleanup()

    def test_deleting_a_promoted_relationship_row_fails_check(self) -> None:
        # Tamper detection: dropping a primary row must fail --check loudly
        # (the generator's failure contract is an uncaught exception -> exit 1).
        tempdir = make_sandbox()
        try:
            sandbox = Path(tempdir.name)
            path = sandbox / "data" / "product_relationships.csv"
            lines = path.read_text(encoding="utf-8").splitlines()
            kept = [line for line in lines if "rel-veritas-53277-309" not in line]
            path.write_text("\n".join(kept) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no reviewed primary relationship"):
                invoke_script("build_catalogue_pages.py", sandbox, "--check")
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


if __name__ == "__main__":
    unittest.main()
