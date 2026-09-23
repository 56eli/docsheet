#!/usr/bin/env python3
"""Focused tests for the final-registry crosscheck matcher.

Covers the pure matcher logic (normalization, T1 key forms, folder↔series
priors, structural parses, part-family grouping, bucket boundaries) on small
inline fixtures, plus a CLI smoke test that regenerates and --checks the
committed outputs against fixture-sized copies in a temp directory. The real
259-row registry is never embedded here.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import crosscheck_final_registry as cfr


def master_row(**overrides) -> dict[str, str]:
    """A minimal curated-master row; every consumed field has a default."""
    row = {
        "record_type": "master", "uuid": "1", "work_id": "w-test",
        "catalog_code": "", "legacy_tempid": "", "title": "Test Work",
        "proposed_filename": "", "proposed_filename_display": "",
        "legacy_title": "", "item_type": "lecture", "series": "Volume Series",
        "year": "", "month": "", "year_source": "", "format": "DVD",
        "format_detail": "", "edition_note": "", "owned": "true",
        "source_url_veritas": "", "source_url_hay_house": "",
        "source_url_nightingale_conant": "", "source_url_audible": "",
        "source_url_amazon": "", "reference_url_1": "", "notes": "",
        "research": "", "raw_row_number": "",
    }
    row.update(overrides)
    return row


def registry_row(path: str, mime: str = "video/mp4", size: str = "1") -> dict[str, str]:
    folder = path.split("/")[0]
    return {
        "Filename": path.rsplit("/", 1)[-1], "Size (bytes)": size,
        "Format (MimeType)": mime, "Modified Date": "", "Full Path": path,
        "folder": folder,
    }


class NormalizationTests(unittest.TestCase):
    def test_normalize_casefold_punctuation_and_brackets(self) -> None:
        self.assertEqual(cfr.normalize("The Ego's Foundation"), "the egos foundation")
        self.assertEqual(cfr.normalize("Truth [B00NWS4SQO]"), "truth")
        self.assertEqual(cfr.normalize("Don’t"), "dont")

    def test_compact_bridges_camelcase(self) -> None:
        self.assertEqual(cfr.compact("TheEyeoftheI"), "theeyeofthei")
        self.assertEqual(cfr.compact("the eye of the i"), "theeyeofthei")

    def test_content_compact_drops_stopwords(self) -> None:
        self.assertEqual(cfr.content_compact("The Ego and The Self"), "ego self".replace(" ", ""))

    def test_strip_trailing_dates_plain_glued_and_month_name(self) -> None:
        self.assertEqual(cfr.strip_trailing_dates("family 2014"), "family")
        self.assertEqual(cfr.strip_trailing_dates("community june2003"), "community")
        self.assertEqual(cfr.strip_trailing_dates("self february 2002"), "self")
        self.assertEqual(cfr.strip_trailing_dates("family 2014 reunited"), "family 2014 reunited")

    def test_strip_author_suffix(self) -> None:
        self.assertEqual(
            cfr.strip_author_suffix("reality spirituality and modern man hawkins david r"),
            "reality spirituality and modern man")
        self.assertEqual(
            cfr.strip_author_suffix("letting go the pathway of surrender by david r hawkins"),
            "letting go the pathway of surrender")

    def test_fuzzy_token_thresholds(self) -> None:
        self.assertTrue(cfr.fuzzy_token("relationsips", "relationships"))
        self.assertTrue(cfr.fuzzy_token("spirituality", "spiritual"))
        self.assertFalse(cfr.fuzzy_token("truth", "falsehood"))


class T1KeyTests(unittest.TestCase):
    def test_slug_tail_strips_prefixes_and_suffixes(self) -> None:
        self.assertEqual(
            cfr.slug_tail("https://veritaspub.com/product/2002-01-causality-the-egos-foundation-jan-2002/"),
            "causality the egos foundation")
        self.assertEqual(
            cfr.slug_tail("https://veritaspub.com/product/become-that-which-you-are-3/"),
            "become that which you are")

    def test_proposed_stem(self) -> None:
        stem = cfr.proposed_stem("2002-01 - Causality The Ego's Foundation [1-3].mp4")
        self.assertEqual(cfr.compact(stem), "causalitytheegosfoundation")
        # Underscored owner standard (2026-09-23): the same record name in the
        # underscore convention must fold to an identical key, so the crosscheck
        # keys never shift when the CSV moves between conventions.
        underscored = cfr.proposed_stem("2002-01_Causality_The_Ego's_Foundation_[1-3].mp4")
        self.assertEqual(cfr.compact(underscored), "causalitytheegosfoundation")
        self.assertEqual(cfr.content_compact(underscored), cfr.content_compact(stem))

    def test_master_keys_cover_title_head_and_edition_variants(self) -> None:
        keys = cfr.MasterIndex.master_keys(master_row(
            title="Power vs. Force (Audiobook)"))
        self.assertIn("powervsforce", keys)
        self.assertIn("powervsforceaudiobook", keys)

    def test_exact_year_suffix_name_matches_master_key(self) -> None:
        index = cfr.MasterIndex([master_row(title="What is Meant by Spiritual")])
        families = set()
        for key in cfr.registry_compact_keys("what-is-meant-by-spiritual-2014"):
            families |= index.works_for_uuids(index.keys.get(key, set()))
        self.assertIn("w-test", families)


class PriorTests(unittest.TestCase):
    def test_folder_series_priors_cover_the_documented_folders(self) -> None:
        documented = {
            "Ontheroad": {"On The Road Talk Series"},
            "VolumeSeries": {"Volume Series"},
            "Satsangs": {"Satsang Series"},
            "Archivalofficeseries": {"Office Series"},
            "DocandSusantalks": {"Discussion Series"},
        }
        for folder, series in documented.items():
            self.assertEqual(cfr.FOLDER_SERIES_PRIORS[folder], series, folder)
        self.assertEqual(cfr.FOLDER_SERIES_PRIORS["Lectures2002-2011"], cfr.ANNUAL_SERIES)

    def test_prior_series_for_detects_camelcase_name_prefixes(self) -> None:
        self.assertEqual(
            cfr.prior_series_for("OfficeVisitSetI:Stress", "Audiobooks"),
            {"Office Series"})
        self.assertIn(
            "Transcending the Mind",
            cfr.prior_series_for("TranscendingtheMindSeries:TheEgo&TheSelf", "Audiobooks"))
        self.assertEqual(cfr.prior_series_for("unknown-name", "Audiobooks"), set())


class StructuralParseTests(unittest.TestCase):
    def test_parse_month_year(self) -> None:
        self.assertEqual(cfr.parse_month_year("june-2002"), ("2002", "06"))
        self.assertEqual(cfr.parse_month_year("mar-2008"), ("2008", "03"))
        self.assertIsNone(cfr.parse_month_year("volume-i"))

    def test_parse_month_tokens_including_glued_camelcase(self) -> None:
        self.assertEqual(cfr.parse_month_tokens("satsang-qa-jan-mar-jul-2011"),
                         (["01", "03", "07"], "2011"))
        self.assertEqual(
            cfr.parse_month_tokens("QuestionandAnswerSeries:Jan,March,&July2011[B00K6P58EM]"),
            (["01", "03", "07"], "2011"))
        self.assertIsNone(cfr.parse_month_tokens("may-2005"))

    def test_parse_volume_numerals(self) -> None:
        self.assertEqual(cfr.parse_volume_numerals("volume-i-power-vs-force"), [1])
        self.assertEqual(cfr.parse_volume_numerals("volume-vi-vii-raise-level"), [6, 7])
        self.assertIsNone(cfr.parse_volume_numerals("how-to-raise-your-level"))


class GroupingTests(unittest.TestCase):
    def test_segments_split_on_double_dash_only(self) -> None:
        self.assertEqual(
            cfr.split_registry_segments("what-is-meant-by-spiritual--the-importance-of-family-2014"),
            ["what-is-meant-by-spiritual", "the-importance-of-family-2014"])
        self.assertEqual(
            cfr.split_registry_segments("archival-cancer--death-and-dying"),
            ["archival-cancer", "death-and-dying"])
        self.assertEqual(cfr.split_registry_segments("plain-name"), ["plain-name"])

    def test_part_suffix_stripped_from_variants(self) -> None:
        variants = cfr.registry_variants("spiritual-will-part1")
        self.assertIn("spiritual will", variants)

    def test_work_id_collapse_one_file_matches_whole_family(self) -> None:
        master = [
            master_row(uuid="10", work_id="w-family", title="Same Work"),
            master_row(uuid="11", work_id="w-family", title="Same Work"),
            master_row(uuid="12", work_id="w-other", title="Other Work", owned="false"),
        ]
        registry = [registry_row("Folder/same-work.mp4")]
        rows, index, counts, d_rows, e_rows, _per_file = cfr.crosscheck(registry, master)
        self.assertEqual(rows[0]["bucket"], "A")
        self.assertEqual(rows[0]["matched_uuid"], "10;11")

    def test_d_and_e_are_report_side_lists(self) -> None:
        master = [
            master_row(uuid="10", work_id="w-owned", title="Owned Work", owned="true"),
            master_row(uuid="11", work_id="w-false", title="False Work", owned="false"),
        ]
        registry = [registry_row("Folder/false-work.mp4")]
        _rows, _index, _counts, d_rows, e_rows, _per_file = cfr.crosscheck(registry, master)
        self.assertEqual([row["uuid"] for row in d_rows], ["10"])
        self.assertEqual([row["uuid"] for row in e_rows], ["11"])


class BucketBoundaryTests(unittest.TestCase):
    def build_index(self) -> cfr.MasterIndex:
        return cfr.MasterIndex([
            master_row(uuid="10", work_id="w-a", title="Alpha Work"),
            master_row(uuid="20", work_id="w-b", title="Beta Work"),
        ])

    def result(self, **kwargs) -> cfr.FileResult:
        result = cfr.FileResult()
        for name, value in kwargs.items():
            setattr(result, name, value)
        return result

    def test_unique_exact_hit_is_a(self) -> None:
        result = self.result()
        result.union_families = {"w-a"}
        result.union_rules = ["T1x"]
        result.union_evidence = ["exact"]
        bucket, _tier, confidence, _ev, works = cfr.assign_bucket(result, self.build_index())
        self.assertEqual(bucket, "A")
        self.assertEqual(confidence, 1.0)
        self.assertEqual(works, ["w-a"])

    def test_single_key_hitting_two_works_is_b(self) -> None:
        result = self.result()
        result.ambiguous = True
        result.ambiguous_families = {"w-a", "w-b"}
        bucket, _tier, _conf, _ev, works = cfr.assign_bucket(result, self.build_index())
        self.assertEqual(bucket, "B")
        self.assertEqual(set(works), {"w-a", "w-b"})

    def test_multi_work_union_is_a_compilation(self) -> None:
        result = self.result()
        result.union_families = {"w-b", "w-a"}
        result.union_rules = ["T1p"]
        result.union_evidence = ["exact remainder"]
        bucket, _tier, _conf, _ev, works = cfr.assign_bucket(result, self.build_index())
        self.assertEqual(bucket, "A")
        self.assertEqual(works, ["w-a", "w-b"])

    def test_strong_unique_score_is_a(self) -> None:
        result = self.result()
        result.record_score("w-a", 0.9, "T2t", "tokens")
        bucket, _tier, confidence, _ev, works = cfr.assign_bucket(result, self.build_index())
        self.assertEqual(bucket, "A")
        self.assertEqual(confidence, 0.9)
        self.assertEqual(works, ["w-a"])

    def test_close_rivals_at_threshold_are_b(self) -> None:
        result = self.result()
        result.record_score("w-a", 0.9, "T2t", "tokens a")
        result.record_score("w-b", 0.87, "T2t", "tokens b")
        bucket, _tier, _conf, _ev, works = cfr.assign_bucket(result, self.build_index())
        self.assertEqual(bucket, "B")
        self.assertEqual(works[0], "w-a")

    def test_mid_score_is_b(self) -> None:
        result = self.result()
        result.record_score("w-a", 0.7, "T2t", "tokens")
        bucket, _tier, _conf, _ev, _works = cfr.assign_bucket(result, self.build_index())
        self.assertEqual(bucket, "B")

    def test_no_candidate_is_c(self) -> None:
        result = self.result()
        bucket, tier, _conf, _ev, works = cfr.assign_bucket(result, self.build_index())
        self.assertEqual(bucket, "C")
        self.assertEqual(tier, "")
        self.assertEqual(works, [])


class CollectionPrefixTests(unittest.TestCase):
    def test_collection_shaped_labels(self) -> None:
        self.assertTrue(cfr.collection_shaped("transcendingthemindseries"))
        self.assertTrue(cfr.collection_shaped("satsangseries"))
        self.assertFalse(cfr.collection_shaped("agingprocess"))

    def test_prefix_keys_strip_to_remainder(self) -> None:
        stripped = cfr.strip_prefix_keys("transcendingthemindseriesthoughtideation")
        self.assertIsNotNone(stripped)
        keys, series = stripped
        self.assertIn("thoughtideation", keys)
        self.assertEqual(series, {"Transcending the Mind"})

    def test_prefix_survives_glued_dates_via_variants(self) -> None:
        stem = "HomoSpiritusDevotionalNondualitySeries(Enlightenment-August2003)"
        remainders: set[str] = set()
        for variant in cfr.registry_variants(stem):
            stripped = cfr.strip_prefix_keys(variant)
            if stripped is not None:
                remainders |= stripped[0]
        self.assertIn("enlightenment", remainders)


class RegistryLoaderTests(unittest.TestCase):
    def test_load_registry_reads_utf8_sig_crlf_and_sorts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "final_registry.csv"
            path.write_bytes(
                "\ufeffFilename,Size (bytes),Format (MimeType),Modified Date,Full Path\r\n"
                "b.mp4,2,video/mp4,x,B/b.mp4\r\n"
                "a.mp4,1,video/mp4,x,A/a.mp4\r\n".encode("utf-8"))
            rows = cfr.load_registry(path)
            self.assertEqual([row["Full Path"] for row in rows], ["A/a.mp4", "B/b.mp4"])
            self.assertEqual(rows[0]["folder"], "A")


class CrosscheckFixtureTests(unittest.TestCase):
    def test_full_pipeline_on_fixture_sized_copies(self) -> None:
        master = [
            master_row(uuid="1", work_id="w-lect", title="Causality",
                       series="The Way to God", year="2002", month="01"),
            master_row(uuid="2", work_id="w-book", title="Letting Go",
                       series="Books", item_type="book", format="book",
                       owned="", source_url_veritas=""),
        ]
        registry = [
            registry_row("Lectures2002-2011/jan-2002.mp4"),
            registry_row("PDFsandEPUBs/letting-go.epub", mime="application/epub+zip"),
            registry_row("Folder/nonexistent-thing.mp4"),
        ]
        rows, index, counts, d_rows, e_rows, per_file = cfr.crosscheck(registry, master)
        by_path = {row["registry_path"]: row for row in rows}
        self.assertEqual(by_path["Lectures2002-2011/jan-2002.mp4"]["bucket"], "A")
        self.assertEqual(by_path["Lectures2002-2011/jan-2002.mp4"]["tier"], "T2ym")
        self.assertEqual(by_path["PDFsandEPUBs/letting-go.epub"]["bucket"], "A")
        self.assertEqual(by_path["Folder/nonexistent-thing.mp4"]["bucket"], "C")
        self.assertEqual(counts["A"], 2)
        self.assertEqual(counts["C"], 1)
        # w-lect is owned=true and matched; w-book is matched but unowned.
        self.assertEqual(d_rows, [])
        self.assertEqual([row["uuid"] for row in e_rows], ["2"])
        self.assertIn("PDFsandEPUBs/letting-go.epub", per_file)


class CheckSmokeTests(unittest.TestCase):
    """Run the real CLI against fixture-sized copies inside a temp tree."""

    REGISTRY_TEXT = (
        "Filename,Size (bytes),Format (MimeType),Modified Date,Full Path\r\n"
        "jan-2002.mp4,10,video/mp4,x,Lectures2002-2011/jan-2002.mp4\r\n"
        "nonexistent.mp4,20,video/mp4,x,Folder/nonexistent.mp4\r\n"
    )
    MASTER = [
        master_row(uuid="1", work_id="w-lect", title="Causality",
                   series="The Way to God", year="2002", month="01"),
    ]

    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(REPO / "crosscheck_final_registry.py"), *args],
            cwd=root, capture_output=True, text=True, check=False)

    def test_write_check_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "review").mkdir()
            (root / "final_registry.csv").write_bytes(self.REGISTRY_TEXT.encode("utf-8"))
            (root / "docs" / "master.json").write_text(json.dumps(self.MASTER))

            write = self.run_cli(root)
            self.assertEqual(write.returncode, 0, write.stderr)
            self.assertTrue((root / "review" / "final_registry_crosscheck.csv").exists())
            self.assertTrue((root / "review" / "2026-09-22-final-registry-crosscheck.md").exists())

            check = self.run_cli(root, "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn("match their inputs", check.stdout)

            csv_path = root / "review" / "final_registry_crosscheck.csv"
            csv_path.write_text(csv_path.read_text(encoding="utf-8").replace("A,", "Z,", 1))
            tampered = self.run_cli(root, "--check")
            self.assertEqual(tampered.returncode, 1)
            self.assertIn("stale", tampered.stdout)


class MatcherChannelTests(unittest.TestCase):
    """Each tier exercised through crosscheck() on tiny fixtures."""

    def rows_for(self, master, registry):
        rows, _index, _counts, _d, _e, _per = cfr.crosscheck(registry, master)
        return {row["registry_path"]: row for row in rows}

    def test_t1f_fuzzy_typo_matches(self) -> None:
        master = [master_row(uuid="1", work_id="w-x", title="Realization of the Self")]
        rows = self.rows_for(master, [registry_row("A/TheWaytoGod:RealizatonoftheSelf.mp4")])
        self.assertEqual(rows["A/TheWaytoGod:RealizatonoftheSelf.mp4"]["tier"], "T1f")

    def test_t1h_head_fallback_unions_one_work(self) -> None:
        master = [master_row(uuid="1", work_id="w-x", title="The Discovery",
                             series="Nightingale-Conant", format="audiobook")]
        rows = self.rows_for(
            master,
            [registry_row("A/TheDiscovery:RevealingthePresenceofGodinYourLife.m4b")])
        row = rows["A/TheDiscovery:RevealingthePresenceofGodinYourLife.m4b"]
        self.assertEqual(row["bucket"], "A")
        self.assertEqual(row["matched_title"], "The Discovery")

    def test_t1c_reverse_containment_scores(self) -> None:
        master = [master_row(uuid="1", work_id="w-x",
                             title="Book of Slides (The Complete Collection)")]
        rows = self.rows_for(master, [registry_row("P/BookofSlides.pdf")])
        self.assertEqual(rows["P/BookofSlides.pdf"]["bucket"], "A")

    def test_t2sm_structural_satsang_months(self) -> None:
        master = [master_row(uuid="1", work_id="w-s1", title="Question/Answer Session (Jan 2011)",
                             series="Satsang Series", year="2011", month="01",
                             format="streaming")]
        rows = self.rows_for(
            master, [registry_row("Satsangs/satsang-qa-jan-mar-jul-2011.mp4")])
        self.assertEqual(rows["Satsangs/satsang-qa-jan-mar-jul-2011.mp4"]["tier"], "T2sm")

    def test_t2vol_structural_volume_numerals(self) -> None:
        master = [master_row(uuid="1", work_id="w-vol2",
                             title="Volume II: Consciousness and Addiction",
                             series="Volume Series")]
        rows = self.rows_for(master, [registry_row("VolumeSeries/volume-ii-consciousness.mp4")])
        self.assertEqual(rows["VolumeSeries/volume-ii-consciousness.mp4"]["bucket"], "A")

    def test_series_scope_resolves_two_work_tie(self) -> None:
        master = [
            master_row(uuid="1", work_id="w-er-tlc", title="Experiential Reality",
                       series="Transcending Levels of Consciousness"),
            master_row(uuid="2", work_id="w-er-mystic", title="Experiential Reality: The Mystic",
                       series="Spiritual Reality & Modern Man"),
        ]
        rows = self.rows_for(
            master,
            [registry_row("A/TranscendingtheLevelsofConsciousnessSeries:ExperientialReality.m4b")])
        row = rows["A/TranscendingtheLevelsofConsciousnessSeries:ExperientialReality.m4b"]
        self.assertEqual(row["bucket"], "A")
        self.assertEqual(row["matched_title"], "Experiential Reality")

    def test_part_files_collapse_into_one_work(self) -> None:
        master = [master_row(uuid="1", work_id="w-x",
                             title="Spiritual Will Inspiring Q & A",
                             series="On The Road Talk Series")]
        registry = [
            registry_row("Ontheroad/spiritual-will-part1.mp4"),
            registry_row("Ontheroad/spiritual-will-part2.mp4"),
        ]
        rows = self.rows_for(master, registry)
        self.assertEqual(
            rows["Ontheroad/spiritual-will-part1.mp4"]["matched_uuid"],
            rows["Ontheroad/spiritual-will-part2.mp4"]["matched_uuid"])

    def test_b_candidates_formatted_with_scores(self) -> None:
        master = [
            master_row(uuid=str(i), work_id=f"w-satsang-{i}",
                       title=f"Satsang Series ({month} 2007)",
                       series="Satsang Series", year="2007", month=month,
                       format="CD", owned="false")
            for i, month in enumerate(["Jan", "Mar", "May"], start=1)
        ]
        registry = [registry_row("Satsangs/SatsangSeries,VolumeI[B00BOV7ODK].m4b",
                                 mime="audio/x-m4b")]
        rows = self.rows_for(master, registry)
        row = rows["Satsangs/SatsangSeries,VolumeI[B00BOV7ODK].m4b"]
        self.assertEqual(row["bucket"], "B")
        self.assertRegex(row["candidate_uuids"], r"^\d+:0\.\d{2}")

    def test_c_rows_and_name_family_grouping(self) -> None:
        master = [master_row(uuid="1", work_id="w-x", title="Some Work")]
        registry = [
            registry_row("A/UnknownTitle.m4b", mime="audio/x-m4b"),
            registry_row("A/UnknownTitle.pdf", mime="application/pdf"),
        ]
        _rows, _index, _counts, _d, _e, per_file = cfr.crosscheck(registry, master)
        self.assertEqual(
            per_file["A/UnknownTitle.m4b"].c_group,
            per_file["A/UnknownTitle.pdf"].c_group)

    def test_author_suffix_registry_names_match(self) -> None:
        master = [master_row(uuid="1", work_id="w-x",
                             title="Reality, Spirituality and Modern Man")]
        rows = self.rows_for(
            master, [registry_row("P/Reality,SpiritualityandModernMan-Hawkins,DavidR.epub")])
        self.assertEqual(
            rows["P/Reality,SpiritualityandModernMan-Hawkins,DavidR.epub"]["bucket"], "A")


class ReportAndCliTests(unittest.TestCase):
    """build_report / render_outputs / main in-process on fixture copies."""

    def setUp(self) -> None:
        self._old = {name: getattr(cfr, name) for name in
                     ("REGISTRY", "MASTER", "OUT_CSV", "OUT_MD")}
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "docs").mkdir()
        (root / "review").mkdir()
        self.root = root
        cfr.REGISTRY = root / "final_registry.csv"
        cfr.MASTER = root / "docs" / "master.json"
        cfr.OUT_CSV = root / "review" / "final_registry_crosscheck.csv"
        cfr.OUT_MD = root / "review" / "2026-09-22-final-registry-crosscheck.md"
        cfr.REGISTRY.write_bytes(
            b"Filename,Size (bytes),Format (MimeType),Modified Date,Full Path\r\n"
            b"jan-2002.mp4,10,video/mp4,x,Lectures2002-2011/jan-2002.mp4\r\n"
            b"unknown.mp4,20,video/mp4,x,Folder/unknown.mp4\r\n")
        cfr.MASTER.write_text(json.dumps([
            master_row(uuid="1", work_id="w-lect", title="Causality",
                       series="The Way to God", year="2002", month="01"),
        ]))

    def tearDown(self) -> None:
        self.tmp.cleanup()
        for name, value in self._old.items():
            setattr(cfr, name, value)

    def test_main_writes_outputs_and_prints_summary(self) -> None:
        exit_code = cfr.main([])
        self.assertEqual(exit_code, 0)
        self.assertTrue(cfr.OUT_CSV.exists())
        text = cfr.OUT_MD.read_text(encoding="utf-8")
        for marker in ("## 1. Scope", "## 2. Methodology", "## 3. Bucket counts",
                       "## 4. Owner review queue", "## 5. Bucket C", "## 6. Bucket D",
                       "## 7. Bucket E", "## 8. Related prior art", "## 9. Reproduction"):
            self.assertIn(marker, text)
        self.assertIn("python crosscheck_final_registry.py --check", text)
        self.assertIn("non-authoritative", text.lower())

    def test_main_check_mode_exits_zero_then_flags_drift(self) -> None:
        self.assertEqual(cfr.main([]), 0)
        self.assertEqual(cfr.main(["--check"]), 0)
        cfr.OUT_CSV.write_text("tampered", encoding="utf-8")
        self.assertEqual(cfr.main(["--check"]), 1)

    def test_parse_args(self) -> None:
        self.assertFalse(cfr.parse_args([]).check)
        self.assertTrue(cfr.parse_args(["--check"]).check)

    def test_render_csv_text_is_deterministic(self) -> None:
        rows = [
            {"registry_path": "A/a.mp4", "folder": "A", "mime": "video/mp4",
             "size_bytes": "1", "bucket": "C", "matched_uuid": "",
             "matched_title": "", "matched_series": "", "tier": "",
             "confidence": "0.00", "evidence": "e", "candidate_uuids": ""},
        ] * 2
        self.assertEqual(cfr.render_csv_text(rows), cfr.render_csv_text(rows))
        self.assertIn("registry_path,folder,mime", cfr.render_csv_text(rows))

    def test_format_bytes_and_md_table_escaping(self) -> None:
        self.assertEqual(cfr.format_bytes(1_500_000_000), "1.5 GB")
        table = cfr._md_table(["H"], [["a|b"]])
        self.assertIn("a\\|b", table)


if __name__ == "__main__":
    unittest.main()
