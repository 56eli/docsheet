#!/usr/bin/env python3
"""Crosscheck the owner's personally-owned file registry against the curated master.

Reads the owner-supplied ``final_registry.csv`` (259 files across 9 folders,
UTF-8 with CRLF line endings) and the published curated master
``docs/master.json`` (363 rows), and bucket-matches every registry file:

* **A** — matched to master work(s) with high confidence (recorded tier,
  normalized key, and evidence);
* **B** — ambiguous: several candidates or a weak score; surfaced for the
  owner's ruling, never auto-applied;
* **C** — registry-only: no plausible master counterpart (candidate new work
  or non-catalogue asset), with obvious part-families grouped;
* **D** — (report only) master rows ``owned=true`` with no registry
  counterpart, grouped by ``work_id``;
* **E** — (report only) registry-matched master rows whose ``owned`` is
  ``false`` or blank: evidence for a future owner ruling, never written.

Why plain slug equality cannot work: registry filenames are slug-style
WITHOUT a month prefix (``volume-i-power-vs-force.mp4``,
``what-is-meant-by-spiritual--the-importance-of-family-2014.mp4``), while
Veritas slugs are month-prefixed
(``2002-01-causality-the-egos-foundation-jan-2002``) and
``proposed_filename`` follows ``YYYY-MM - Title [n-m].mp4``.  The bridge is
explicit multi-tier normalization plus folder↔series priors.

The matcher is deterministic and offline (stdlib only): stable sort orders,
fixed two-decimal score formatting, and no timestamps in the outputs, so
``--check`` can byte-compare regenerated output against the committed files.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

REGISTRY = Path("final_registry.csv")
MASTER = Path("docs/master.json")
OUT_CSV = Path("review/final_registry_crosscheck.csv")
OUT_MD = Path("review/2026-09-22-final-registry-crosscheck.md")

REGISTRY_COLUMNS = {
    "Filename", "Size (bytes)", "Format (MimeType)", "Modified Date", "Full Path",
}

CSV_FIELDS = [
    "registry_path", "folder", "mime", "size_bytes", "bucket",
    "matched_uuid", "matched_title", "matched_series", "tier",
    "confidence", "evidence", "candidate_uuids",
]

# Annual (monthly lecture) series 2002-2011: the folder Lectures2002-2011
# names files only "mar-2008.mp4", so those match by year-month.
ANNUAL_SERIES = {
    "The Way to God", "Devotional Nonduality", "Transcending the Mind",
    "Nonduality Intensive",
    "Transcending Levels of Consciousness", "Spiritual Reality & Modern Man",
    "Advanced Spiritual Awareness", "In the World but Not of It",
    "Practical Spirituality", "Love & Spiritual Seeker Qualities",
}

# Folder → series/type priors (T2). A prior boosts candidate scores inside
# its scope; it never suppresses name-derived evidence from other rules.
FOLDER_SERIES_PRIORS = {
    "Ontheroad": {"On The Road Talk Series"},
    "VolumeSeries": {"Volume Series"},
    "Satsangs": {"Satsang Series"},
    "Archivalofficeseries": {"Office Series"},
    "DocandSusantalks": {"Discussion Series"},
    "Lectures2002-2011": set(ANNUAL_SERIES),
}

# Name-prefix → series priors, for CamelCase product names that carry their
# collection name ("OfficeVisitSetI:...", "TranscendingtheMindSeries:...").
PREFIX_SERIES_PRIORS = [
    ("office visit", {"Office Series"}),
    ("on the road", {"On The Road Talk Series"}),
    ("satsang", {"Satsang Series"}),
    ("question and answer series", {"Satsang Series"}),
    ("discussion series", {"Discussion Series"}),
    ("archival", {"Office Series"}),
    ("volume", {"Volume Series"}),
    # Fuzzy series prefixes below are matched on the compact form with a
    # ratio floor (e.g. "Advancing Spiritual Awareness" ~ "Advanced Spiritual
    # Awareness").
    ("transcending the mind series", {"Transcending the Mind"}),
    ("transcending the mind", {"Transcending the Mind"}),
    ("devotional nonduality intensive", {"Nonduality Intensive"}),
    ("homo spiritus devotional nonduality series", {"Devotional Nonduality"}),
    ("devotional nonduality series", {"Devotional Nonduality"}),
    ("advancing spiritual awareness", {"Advanced Spiritual Awareness"}),
    ("advanced spiritual awareness", {"Advanced Spiritual Awareness"}),
    ("transcending the levels of consciousness series", {"Transcending Levels of Consciousness"}),
    ("transcending the levels of consciousness", {"Transcending Levels of Consciousness"}),
    ("spiritual reality and modern man", {"Spiritual Reality & Modern Man"}),
    ("practical spirituality", {"Practical Spirituality"}),
    ("in the world but not of it", {"In the World but Not of It"}),
    ("the way to god", {"The Way to God"}),
]

MONTH_NAMES = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05",
    "jun": "06", "jul": "07", "aug": "08", "sep": "09", "oct": "10",
    "nov": "11", "dec": "12",
}
MONTH_NAME_TOKENS = {
    "jan": "01", "january": "01", "feb": "02", "february": "02",
    "mar": "03", "march": "03", "apr": "04", "april": "04",
    "may": "05", "jun": "06", "june": "06", "jul": "07", "july": "07",
    "aug": "08", "august": "08", "sep": "09", "sept": "09",
    "september": "09", "oct": "10", "october": "10", "nov": "11",
    "november": "11", "dec": "12", "december": "12",
}
ROMAN_NUMERALS = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7}

# Words ignored when comparing content tokens ("and" in "The Ego and The
# Self" vs "The Ego & The Self"; articles and short prepositions).
STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "in", "on", "to", "by", "for",
    "with", "is", "are", "it", "its", "as", "at", "from",
}

# Author markers stripped from registry ebook names after full-name matching
# failed ("...by David R. Hawkins", "... - Hawkins, David R.").
AUTHOR_SUFFIXES = [
    "by david r hawkins", "by dr david r hawkins", "by david hawkins",
    "david r hawkins", "dr david r hawkins", "hawkins david r",
    "hawkins david", "by hawkins",
]

# Edition markers removed from master titles when deriving match keys
# ("Power vs. Force (Audiobook)" → "power vs force").
EDITION_MARKERS = [
    "audiobook", "audio book", "audio", "cd", "video", "unabridged",
]

# Deterministic score thresholds (documented in the generated report).
A_THRESHOLD = 0.85        # best candidate at or above → bucket A …
A_MARGIN = 0.10           # … if no different-work rival is within this margin
B_FLOOR = 0.55            # candidates at or above → bucket B (review queue)
TOKEN_FUZZY_RATIO = 0.85  # per-token typo tolerance ("relationsips"~"relationships")
COMPACT_FUZZY_RATIO = 0.90  # compact-form fuzzy equality floor ("advancing"~"advanced")
CONTAINMENT_MIN_LEN = 12  # shortest compact containment accepted as evidence


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Fold a name to a canonical spaced form.

    NFKD + casefold, drop combining marks, delete apostrophes (``Ego's`` →
    ``egos`` so it equals the slug form ``egos``), strip ``[...]`` product
    IDs, map remaining punctuation to spaces, and collapse whitespace.
    """
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold()
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = text.replace("'", "").replace("’", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def compact(text: str) -> str:
    """Space-folded form of :func:`normalize` (CamelCase bridge)."""
    return normalize(text).replace(" ", "")


def content_compact(text: str) -> str:
    """Stopword-free compact form ("The Ego and The Self" → "theegotheself")."""
    return "".join(tok for tok in normalize(text).split() if tok not in STOPWORDS)


def content_tokens(text: str) -> list[str]:
    return [tok for tok in normalize(text).split() if tok not in STOPWORDS]


def strip_trailing_dates(text: str) -> str:
    """Remove trailing ``-2014`` / ``June 2003`` / glued ``June2003`` dates."""
    words = normalize(text).split()
    glued = re.compile(
        r"(" + "|".join(sorted(MONTH_NAME_TOKENS, key=len, reverse=True)) + r")((?:19|20)\d{2})"
    )
    while words:
        last = words[-1]
        if re.fullmatch(r"(19|20)\d{2}", last):
            words.pop()
            if words and words[-1] in MONTH_NAME_TOKENS:
                words.pop()
            continue
        if glued.fullmatch(last):
            words.pop()
            continue
        if len(words) >= 2 and f"{words[-2]} {last}" in MONTH_NAME_TOKENS:
            words.pop()
            words.pop()
            continue
        break
    return " ".join(words)


def strip_author_suffix(text: str) -> str:
    """Drop a trailing author marker if one survives normalization."""
    for marker in AUTHOR_SUFFIXES:
        if text.endswith(" " + marker):
            return text[: -len(marker)].strip()
    return text


def fuzzy_token(a: str, b: str) -> bool:
    """Token equality with documented typo tolerance.

    Long tokens (>=9 chars) get a slightly lower floor so near-identical
    forms ("spirituality"~"spiritual") still pair; short tokens stay strict.
    """
    if a == b:
        return True
    if len(a) < 4 or len(b) < 4:
        return False
    floor = 0.80 if len(a) >= 9 and len(b) >= 9 else TOKEN_FUZZY_RATIO
    return SequenceMatcher(None, a, b).ratio() >= floor


def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_registry(path: Path | None = None) -> list[dict[str, str]]:
    """Read the owner's registry CSV (utf-8-sig, CRLF-safe).

    Columns are validated here rather than through
    ``pipeline.helpers.require_columns`` because that helper opens with
    plain ``utf-8`` and would keep the byte-order mark in the first header
    cell, while the registry is UTF-8 with BOM and CRLF line endings.
    """
    path = path or REGISTRY
    if not path.exists():
        raise FileNotFoundError(f"Required CSV missing: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = set(reader.fieldnames or [])
        missing = REGISTRY_COLUMNS - header
        if missing:
            raise ValueError(f"{path.name} missing required columns: {sorted(missing)}")
        rows = list(reader)
    for row in rows:
        row["Filename"] = row["Filename"].strip()
        row["Full Path"] = row["Full Path"].strip().replace("\\", "/")
        row["folder"] = row["Full Path"].split("/")[0]
    rows.sort(key=lambda row: row["Full Path"])
    return rows


def load_master(path: Path | None = None) -> list[dict[str, str]]:
    """Read the published curated master rows."""
    path = path or MASTER
    with path.open(encoding="utf-8") as handle:
        rows = json.load(handle)
    return rows


class MasterIndex:
    """Precomputed lookup structures over the 363 master rows."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self.rows = rows
        self.by_uuid = {row["uuid"]: row for row in rows}
        self.families: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            self.families[row["work_id"]].append(row)
        for family in self.families.values():
            family.sort(key=lambda row: int(row["uuid"]))

        # key form → uuids that carry it, and per-key content-token counts
        self.keys: dict[str, set[str]] = defaultdict(set)
        self.key_tokens: dict[str, int] = {}
        for row in rows:
            for key, ntokens in self.master_keys(row).items():
                self.keys[key].add(row["uuid"])
                self.key_tokens[key] = max(self.key_tokens.get(key, 0), ntokens)

        # (year, month) → work_ids, annual series and Satsang rows
        self.lecture_ym: dict[tuple[str, str], set[str]] = defaultdict(set)
        self.satsang_ym: dict[tuple[str, str], set[str]] = defaultdict(set)
        for row in rows:
            if not (row["year"] and row["month"]):
                continue
            key = (row["year"], row["month"])
            if row["series"] in ANNUAL_SERIES:
                self.lecture_ym[key].add(row["work_id"])
            if row["series"] == "Satsang Series":
                self.satsang_ym[key].add(row["work_id"])

        # volume numeral → work_ids (Volume Series)
        self.volume_works: dict[int, set[str]] = defaultdict(set)
        for work_id, family in self.families.items():
            match = re.match(r"volume ([ivx]+)\b", normalize(family[0]["title"]))
            if match and family[0]["series"] == "Volume Series":
                self.volume_works[ROMAN_NUMERALS[match.group(1)]].add(work_id)

        self._tokens: dict[str, list[str]] = {}

    def row_tokens(self, row: dict[str, str]) -> list[str]:
        """Cached content tokens of a master row's title."""
        uuid = row["uuid"]
        if uuid not in self._tokens:
            self._tokens[uuid] = content_tokens(row["title"])
        return self._tokens[uuid]

    def primary_uuid(self, work_id: str) -> int:
        return int(self.families[work_id][0]["uuid"])

    @staticmethod
    def master_keys(row: dict[str, str]) -> dict[str, int]:
        """All normalized lookup keys a master row answers to, with token counts."""
        keyed: dict[str, int] = {}

        def add(form: str) -> None:
            for key in {compact(form), content_compact(form)}:
                if key:
                    keyed[key] = max(keyed.get(key, 0), len(content_tokens(form)))

        for form in title_variants(row["title"]):
            add(form)
        stem = proposed_stem(row.get("proposed_filename", ""))
        if stem:
            add(stem)
        slug = slug_tail(row.get("source_url_veritas", ""))
        if slug:
            add(slug)
        return keyed

    def works_for_uuids(self, uuids: set[str]) -> set[str]:
        return {self.by_uuid[u]["work_id"] for u in uuids}

    def family_rows(self, work_id: str) -> list[dict[str, str]]:
        return self.families[work_id]


def title_variants(title: str) -> list[str]:
    """Title forms a registry name may equal: full, head, edition-stripped."""
    variants = [title]
    head = title.split(":", 1)[0].strip()
    if head and head != title:
        variants.append(head)
    stripped = strip_edition_markers(title)
    if stripped and stripped != title:
        variants.append(stripped)
        stripped_head = stripped.split(":", 1)[0].strip()
        if stripped_head and stripped_head != stripped:
            variants.append(stripped_head)
    return variants


def strip_edition_markers(title: str) -> str:
    """Remove '(Audiobook)', '– Audio', '(CD)' edition markers from a title."""
    text = re.sub(r"\((audiobook|audio|cd|video)\)", " ", title, flags=re.IGNORECASE)
    text = re.sub(r"\b(audio book|audiobook)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"[\u2013\u2014-]\s*audio$", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\baudio$", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvideo$", " ", text, flags=re.IGNORECASE)
    return normalize(text)


def proposed_stem(name: str) -> str:
    """'2002-01 - Causality The Ego's Foundation [1-3].mp4' → 'causality the egos foundation'."""
    if not name:
        return ""
    stem = name.rsplit(".", 1)[0]
    stem = re.sub(r"^\d{4}-\d{2}\s*-\s*", "", stem)
    stem = re.sub(r"\s*\[\d+-\d+\]$", "", stem)
    return stem


def slug_tail(url: str) -> str:
    """'https://veritaspub.com/product/become-that-which-you-are-3/' →
    'become that which you are'."""
    if not url:
        return ""
    segment = [part for part in url.rstrip("/").split("/") if part]
    if not segment:
        return ""
    slug = segment[-1]
    slug = re.sub(r"^\d{4}-\d{2}-", "", slug)
    slug = re.sub(r"-(video|audio|session)$", "", slug)
    slug = re.sub(r"-(%s)-(\d{4})$" % "|".join(MONTH_NAME_TOKENS), "", slug)
    slug = re.sub(r"-(19|20)\d{2}$", "", slug)
    slug = re.sub(r"-\d+$", "", slug)
    return slug.replace("-", " ")


# ---------------------------------------------------------------------------
# Registry-side key derivation
# ---------------------------------------------------------------------------

PART_SUFFIX = re.compile(r"[- _]part\s*\d+$")


def registry_variants(stem: str) -> list[str]:
    """Ordered registry key variants (full name first, then stripped forms)."""
    variants: list[str] = []
    seen: set[str] = set()

    def add(form: str) -> None:
        if form and len(form) >= 2 and form not in seen:
            seen.add(form)
            variants.append(form)

    spaced = normalize(stem)
    add(spaced)
    add(strip_author_suffix(spaced))
    add(strip_trailing_dates(spaced))
    add(strip_trailing_dates(strip_author_suffix(spaced)))
    no_part = PART_SUFFIX.sub("", spaced)
    if no_part != spaced:
        add(no_part)
        add(strip_trailing_dates(no_part))
        add(strip_trailing_dates(strip_author_suffix(no_part)))
    return variants


def registry_compact_keys(stem: str) -> set[str]:
    """Compact + content-compact key forms for every variant of a name."""
    keys: set[str] = set()
    for variant in registry_variants(stem):
        keys.add(variant.replace(" ", ""))
        keys.add(content_compact(variant))
    return {key for key in keys if len(key) >= 2}


def camel_split(text: str) -> str:
    """Insert spaces at CamelCase/alpha-digit boundaries (raw, pre-normalize)."""
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = re.sub(r"(?<=[^\W\d_])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", text)
    return text


def registry_content_tokens(stem: str) -> list[str]:
    """Content tokens of the most-stripped variant (used for scoring).

    CamelCase gluing is undone on the RAW stem first ("SatsangSeries,VolumeVII"
    -> tokens satsang/series/volume/vii), then date and author suffixes are
    stripped from the normalized form.
    """
    spaced = strip_trailing_dates(strip_author_suffix(normalize(camel_split(stem))))
    return content_tokens(spaced)


def parse_month_year(stem: str) -> tuple[str, str] | None:
    """'june-2002' / 'mar-2008' → ('2002', '06')."""
    match = re.fullmatch(r"([a-z]+)[\s-]+((?:19|20)\d{2})", normalize(stem))
    if match and match.group(1) in MONTH_NAME_TOKENS:
        return match.group(2), MONTH_NAME_TOKENS[match.group(1)]
    return None


def parse_month_tokens(stem: str) -> tuple[list[str], str] | None:
    """'satsang qa jan mar jul 2011' → (['01','03','07'], '2011')."""
    words = normalize(camel_split(stem)).replace("-", " ").split()
    months: list[str] = []
    year = ""
    rest: list[str] = []
    for word in words:
        if word in MONTH_NAME_TOKENS:
            months.append(MONTH_NAME_TOKENS[word])
        elif re.fullmatch(r"(19|20)\d{2}", word):
            year = word
        else:
            rest.append(word)
    if len(months) >= 2 and year:
        return sorted(set(months)), year
    return None


def parse_volume_numerals(stem: str) -> list[int] | None:
    """'volume-vi-vii-raise-level-...' → [6, 7]; 'volume-i-...' → [1]."""
    words = normalize(camel_split(stem)).replace("-", " ").split()
    if not words or words[0] != "volume":
        return None
    numerals: list[int] = []
    for word in words[1:]:
        if word in ROMAN_NUMERALS:
            numerals.append(ROMAN_NUMERALS[word])
        else:
            break
    if not numerals:
        return None
    return sorted(set(numerals))


def split_title_segments(stem: str) -> list[str]:
    """Split a '--'-joined multi-title slug into per-work segments."""
    spaced = normalize(stem)
    segments = [seg.strip() for seg in re.split(r"\s+--\s+|--", spaced) if seg.strip()]
    return segments


def strip_prefix_keys(stem: str) -> tuple[set[str], set[str]] | None:
    """Strip a known collection prefix in compact space.

    CamelCase product names glue the collection title onto the work title
    ("OfficeVisitSetI:...", "TranscendingtheMindSeries:..."), so the prefix
    is removed on the compact form and the remainder is returned as extra
    lookup keys. The longest matching prefix wins (so
    "...levels of consciousness series" strips before "...levels of
    consciousness"). Returns ``(remainder_keys, prior_series)``.
    """
    target = compact(stem)
    target_content = content_compact(stem)
    best: tuple[int, str, set[str]] | None = None
    for prefix, series in PREFIX_SERIES_PRIORS:
        key = compact(prefix)
        if target.startswith(key) and len(target) > len(key):
            if best is None or len(key) > best[0]:
                best = (len(key), key, series)
    if best is None:
        return None
    remainder = target[best[0]:]
    keys = {remainder}
    # A second strip pass over the content form (stopwords removed on both
    # sides) catches remainders whose stopword boundaries differ.
    for prefix, series in PREFIX_SERIES_PRIORS:
        key = content_compact(prefix)
        if target_content.startswith(key) and len(target_content) > len(key):
            keys.add(target_content[len(key):])
            break
    # A third pass in token space with per-word fuzzy matching, for glued
    # CamelCase leftovers ("Transcendingthe Mind Series: TheEgo & TheSelf"):
    # the remainder is rebuilt from the content words after the prefix words.
    words = content_tokens(normalize(camel_split(stem)))
    token_match: tuple[int, list[str], set[str]] | None = None
    for prefix, series in PREFIX_SERIES_PRIORS:
        prefix_words = content_tokens(normalize(camel_split(prefix)))
        if len(words) > len(prefix_words) and all(
            fuzzy_token(word, prefix_word)
            for word, prefix_word in zip(words, prefix_words)
        ):
            if token_match is None or len(prefix_words) > token_match[0]:
                token_match = (len(prefix_words), words[len(prefix_words):], series)
    if token_match is not None:
        remainder_compact = "".join(token_match[1])
        if len(remainder_compact) >= 2:
            keys.add(remainder_compact)
    return keys, best[2]


# ---------------------------------------------------------------------------
# Matching engine
# ---------------------------------------------------------------------------

RULE_PRIORITY = {"T1x": 9, "T1h": 8, "T1p": 7, "T2ym": 6, "T2sm": 5,
                 "T2vol": 5, "T1c": 4, "T1f": 3, "T2t": 1}

PART_TOKEN = re.compile(r"part\d*")

# Compact forms of the collection prefixes: needles shaped like a collection
# label (or ending in the generic word "series") never mark a name ambiguous.
PREFIX_KEY_SET = {compact(prefix) for prefix, _ in PREFIX_SERIES_PRIORS}
PREFIX_KEY_SET |= {content_compact(prefix) for prefix, _ in PREFIX_SERIES_PRIORS}


def collection_shaped(key: str) -> bool:
    """True when a containment needle is a collection label, not a work name."""
    if key in PREFIX_KEY_SET:
        return True
    return key.endswith("series") and any(key.startswith(p) for p in PREFIX_KEY_SET)


def split_registry_segments(stem: str) -> list[str]:
    """Split a raw stem on double dashes into per-work segments.

    Must run on the RAW stem: normalization turns ``--`` into spaces.
    """
    return [seg for seg in re.split(r"\s*--\s*", stem) if seg.strip()]


def prior_series_for(stem: str, folder: str) -> set[str]:
    """Folder priors plus name-prefix priors for a registry file."""
    priors: set[str] = set(FOLDER_SERIES_PRIORS.get(folder, set()))
    target = compact(stem)
    for prefix, series in PREFIX_SERIES_PRIORS:
        if target.startswith(compact(prefix)):
            priors |= set(series)
    return priors


def prior_label(priors: set[str]) -> str:
    return "+".join(sorted(priors)) if priors else "none"


class FileResult:
    """Per-registry-file match state (deterministic by construction)."""

    def __init__(self) -> None:
        self.union_families: set[str] = set()   # unambiguous exact/structural
        self.ambiguous_families: set[str] = set()
        self.ambiguous = False
        self.union_rules: list[str] = []
        self.union_evidence: list[str] = []
        self.scores: dict[str, tuple[float, str, str]] = {}  # work -> (score, rule, evidence)
        self.c_group = ""

    def record_score(self, work_id: str, score: float, rule: str, evidence: str) -> None:
        current = self.scores.get(work_id)
        if current is None or (score, RULE_PRIORITY[rule]) > (current[0], RULE_PRIORITY[current[1]]):
            self.scores[work_id] = (score, rule, evidence)

    def best_score(self) -> tuple[float, str, str]:
        if not self.scores:
            return 0.0, "", "no candidate above the token floor"
        work = sorted(self.scores, key=lambda w: (-self.scores[w][0], w))[0]
        return self.scores[work]


def score_tokens(reg_tokens: list[str], row_tokens: list[str]) -> tuple[float, int]:
    """Greedy one-to-one fuzzy token overlap; returns (score, common count).

    Single-character tokens ("Q", "A", "I") are skipped on both sides: they
    carry no work identity and drown the overlap denominator.
    """
    reg_tokens = [t for t in reg_tokens if len(t) >= 2]
    row_tokens = [t for t in row_tokens if len(t) >= 2]
    if not reg_tokens or not row_tokens:
        return 0.0, 0
    used: set[int] = set()
    common = 0
    for token in reg_tokens:
        best_i, best_ratio = -1, 0.0
        for i, other in enumerate(row_tokens):
            if i in used:
                continue
            if token == other:
                best_i, best_ratio = i, 1.0
                break
            ratio_ = SequenceMatcher(None, token, other).ratio()
            if ratio_ > best_ratio and fuzzy_token(token, other):
                best_i, best_ratio = i, ratio_
        if best_i >= 0:
            used.add(best_i)
            common += 1
    return common / max(len(reg_tokens), len(row_tokens)), common


def tokens_covered(reg_tokens: list[str], row_tokens: list[str]) -> bool:
    """True when every significant registry token is matched in the title.

    Used for the segment-subset union rule: a file-name segment whose tokens
    (>=3) all appear in a master title names that work ("how to live like a
    prayer" ⊆ "How to Live Your Life Like A Prayer").
    """
    reg_tokens = [t for t in reg_tokens if len(t) >= 2]
    row_tokens = [t for t in row_tokens if len(t) >= 2]
    if len(reg_tokens) < 3 or not row_tokens:
        return False
    used: set[int] = set()
    for token in reg_tokens:
        found = False
        for i, other in enumerate(row_tokens):
            if i in used:
                continue
            if fuzzy_token(token, other):
                used.add(i)
                found = True
                break
        if not found:
            return False
    return True


def match_registry_file(stem: str, folder: str, index: MasterIndex) -> FileResult:
    """Run the tier pipeline for one registry file."""
    result = FileResult()
    segments = split_registry_segments(stem)
    reg_keys = registry_compact_keys(stem)
    result.c_group = max(reg_keys, key=lambda k: (len(k), k)) if reg_keys else compact(stem)
    priors = prior_series_for(stem, folder)

    # --- T1x/T1h/T1p: exact keys, title heads, per segment ------------------
    def exact_label(rule: str, keys: set[str], evidence_template: str) -> set[str]:
        """Record exact-key hits. Returns the families hit (possibly empty)."""
        matched = sorted(key for key in keys if key in index.keys)
        if not matched:
            return set()
        families: set[str] = set()
        for key in matched:
            families |= index.works_for_uuids(index.keys[key])
        evidence = evidence_template.format(keys=", ".join(matched))
        if len(families) == 1:
            result.union_families |= families
            result.union_rules.append(rule)
            result.union_evidence.append(evidence)
        else:
            result.ambiguous = True
            result.ambiguous_families |= families
        return families

    def head_keys(segment: str) -> set[str]:
        """Pre-colon head of a name as extra lookup keys ('Truths vs. Falsehood:…')."""
        head = segment.split(":", 1)[0].strip()
        if not head or normalize(head) == normalize(segment):
            return set()
        return {form for form in {compact(head), content_compact(head)} if len(form) >= 2}

    seg_exact: dict[int, set[str]] = {}
    for seg_idx, segment in enumerate(segments):
        seg_keys = registry_compact_keys(segment)
        t1x_families = exact_label("T1x", seg_keys, "exact name key(s): {keys}")
        t1p_families: set[str] = set()
        remainder_keys: set[str] = set()
        t1p_series: set[str] = set()
        for variant in [segment] + registry_variants(segment):
            stripped = strip_prefix_keys(variant)
            if stripped is not None:
                remainder_keys |= stripped[0]
                t1p_series |= stripped[1]
        if remainder_keys:
            # Remainder keys also join the fuzzy/containment key set, so a
            # near-miss remainder ("Realizaton" typo) still scores.
            reg_keys |= remainder_keys
            t1p_families = exact_label(
                "T1p", remainder_keys, "exact after collection-prefix strip: {keys}")
            if len(t1p_families) > 1 and t1p_series:
                # The prefix names the collection: scope an ambiguous
                # remainder to its series ("Experiential Reality" exists in
                # two series; the prefix says which one this file means).
                scoped = {
                    work_id for work_id in t1p_families
                    if index.families[work_id][0]["series"] in t1p_series
                }
                if len(scoped) == 1:
                    result.ambiguous = False
                    result.ambiguous_families.difference_update(t1p_families - scoped)
                    result.union_families |= scoped
                    result.union_rules.append("T1p")
                    result.union_evidence.append(
                        "prefix-scoped remainder to series: "
                        + ", ".join(sorted(t1p_series)))
                    t1p_families = scoped
        # T1h: a head that names exactly one work falls back to a union match
        # when the prefix-strip remainder missed; heads naming several works
        # are collection labels and are dropped entirely.
        for head in sorted(head_keys(segment)):
            uuids = index.keys.get(head, set())
            families = index.works_for_uuids(uuids) if uuids else set()
            if len(families) > 1:
                continue
            reg_keys.add(head)
            if len(families) == 1 and not t1p_families:
                result.union_families |= families
                result.union_rules.append("T1h")
                result.union_evidence.append(f"exact title head '{head}'")
                t1p_families = t1p_families or families
        seg_exact[seg_idx] = t1x_families | t1p_families

    # --- T2 structural: lecture year-month ---------------------------------
    if folder == "Lectures2002-2011":
        ym = parse_month_year(stem)
        if ym is not None and ym in index.lecture_ym:
            families = set(index.lecture_ym[ym])
            if len(families) == 1:
                result.union_families |= families
                result.union_rules.append("T2ym")
                result.union_evidence.append(
                    f"year-month {ym[0]}-{ym[1]} unique across annual lecture series")
            else:
                result.ambiguous = True
                result.ambiguous_families |= families
            seg_exact[0] = seg_exact.get(0, set()) | families

    # --- T2 structural: satsang month lists --------------------------------
    compact_stem = compact(stem)
    if ("satsang" in compact_stem or "questionandanswerseries" in compact_stem
            or folder == "Satsangs"):
        months = parse_month_tokens(stem)
        if months is not None:
            month_list, year = months
            families: set[str] = set()
            for month in month_list:
                families |= index.satsang_ym.get((year, month), set())
            if families:
                result.union_families |= families
                result.union_rules.append("T2sm")
                result.union_evidence.append(
                    f"months {'/'.join(month_list)} of {year} match Satsang Series session(s)")
            seg_exact[0] = seg_exact.get(0, set()) | families

    # --- T2 structural: Volume Series numerals ------------------------------
    if folder == "VolumeSeries":
        numerals = parse_volume_numerals(stem)
        if numerals is not None:
            families: set[str] = set()
            for numeral in numerals:
                families |= index.volume_works.get(numeral, set())
            if families:
                result.union_families |= families
                result.union_rules.append("T2vol")
                roman = sorted({r for r, n in ROMAN_NUMERALS.items() if n in numerals})
                result.union_evidence.append(f"volume numeral(s) {'/'.join(roman)} of Volume Series")
            seg_exact[0] = seg_exact.get(0, set()) | families

    # --- T1c/T1f: containment and fuzzy over master keys --------------------
    container = max(reg_keys, key=lambda k: (len(k), k)) if reg_keys else ""
    seg_containers = [
        max((registry_compact_keys(segment) | head_keys(segment)),
            key=lambda k: (len(k), k))
        if (registry_compact_keys(segment) or head_keys(segment)) else ""
        for segment in segments
    ]
    # forward containment: master key inside a registry segment; a segment
    # that already named its work exactly demotes the needle (collection-level
    # containment must not inflate the match)
    for key in sorted(index.keys):
        if (len(key) >= CONTAINMENT_MIN_LEN
                and key != container and index.key_tokens.get(key, 0) >= 2
                and (key in PREFIX_KEY_SET
                     or not any(key in prefix_key for prefix_key in PREFIX_KEY_SET))):
            families = index.works_for_uuids(index.keys[key])
            fired = [i for i, seg_container in enumerate(seg_containers)
                     if seg_container and key != seg_container and key in seg_container]
            if not fired or any(seg_exact.get(i) for i in fired):
                continue
            if len(families) == 1:
                result.union_families |= families
                result.union_rules.append("T1c")
                result.union_evidence.append(
                    f"containment: master key '{key}' inside registry name")
            elif not collection_shaped(key):
                result.ambiguous = True
                result.ambiguous_families |= families

    # reverse containment and fuzzy equality over master keys
    for key in sorted(index.keys):
        candidates = index.keys[key]
        for reg_key in sorted(reg_keys):
            if (len(reg_key) >= CONTAINMENT_MIN_LEN and reg_key != key
                    and reg_key in key):
                families = index.works_for_uuids(candidates)
                if len(families) == 1:
                    result.record_score(
                        next(iter(families)), 1.0, "T1c",
                        f"containment: registry key '{reg_key}' inside master key")
                elif not collection_shaped(reg_key):
                    result.ambiguous = True
                    result.ambiguous_families |= families
            # fuzzy equality, gated by length distance and quick ratio
            if (len(reg_key) >= 8 and abs(len(reg_key) - len(key)) <= 0.25 * max(len(reg_key), len(key))):
                matcher = SequenceMatcher(None, reg_key, key)
                if (matcher.real_quick_ratio() >= COMPACT_FUZZY_RATIO
                        and matcher.quick_ratio() >= COMPACT_FUZZY_RATIO
                        and matcher.ratio() >= COMPACT_FUZZY_RATIO):
                    families = index.works_for_uuids(candidates)
                    if len(families) == 1:
                        result.record_score(
                            next(iter(families)), matcher.ratio(), "T1f",
                            f"fuzzy {matcher.ratio():.2f} '{reg_key}' ~ '{key}'")
                    else:
                        for work_id in sorted(families):
                            result.record_score(
                                work_id, matcher.ratio(), "T1f",
                                f"fuzzy {matcher.ratio():.2f} '{reg_key}' ~ '{key}'")

    # --- T2t: token scoring with priors -------------------------------------
    # Tokens are scored per segment (a compilation name must score its
    # segments separately) and for the full name; the best wins.
    token_sets = [
        [tok for tok in content_tokens(normalize(segment)) if not PART_TOKEN.fullmatch(tok)]
        for segment in segments
    ]
    token_sets.append(
        [tok for tok in registry_content_tokens(stem) if not PART_TOKEN.fullmatch(tok)])
    token_sets = [tokens for tokens in token_sets if tokens]
    if token_sets:
        for work_id, family in sorted(index.families.items()):
            best = (0.0, 0, None)
            for tokens in token_sets:
                for row in family:
                    score, common = score_tokens(tokens, index.row_tokens(row))
                    if (score, common) > best[:2]:
                        best = (score, common, tokens)
            score = min(1.0, best[0] + (0.25 if family[0]["series"] in priors else 0.0))
            if any(tokens_covered(tokens, index.row_tokens(row))
                   for tokens in token_sets for row in family):
                # a whole segment names this work ("How to Live Like a
                # Prayer" ⊆ "How to Live Your Life Like A Prayer")
                result.union_families.add(work_id)
                result.union_rules.append("T2t")
                result.union_evidence.append(
                    "all significant tokens of a name segment match "
                    f"(prior: {prior_label(priors)})")
            elif score >= B_FLOOR:
                result.record_score(
                    work_id, score, "T2t",
                    f"tokens {best[1]}/{len(best[2])} significant (prior: {prior_label(priors)})")

    # A name whose collection prefix names one series may resolve its own
    # ambiguity: two works titled "Experiential Reality" exist in different
    # series, and the prefix says which one this file means.
    if result.ambiguous and len(result.ambiguous_families) > 1:
        scoped = {
            work_id for work_id in result.ambiguous_families
            if index.families[work_id][0]["series"] in priors
        }
        if len(scoped) == 1:
            result.ambiguous = False
            result.ambiguous_families.clear()
            result.union_families |= scoped
            result.union_rules.append("T1p")
            result.union_evidence.append(
                "series scope resolved ambiguity to series: " + prior_label(priors))

    return result


def assign_bucket(result: FileResult, index: MasterIndex) -> tuple[str, str, float, str, list[str]]:
    """Bucket one file result.

    Returns ``(bucket, tier, confidence, evidence, ranked_work_ids)``.
    Boundary rules (documented in the generated report):

    * an unambiguous exact/structural union wins outright → A (one or
      several works when the name is a compilation of segments);
    * a single-label key hitting several different works is ambiguous → B;
    * otherwise the top scored candidate decides: >= A_THRESHOLD with no
      different-work rival within A_MARGIN → A; >= B_FLOOR → B; else C.
    """
    ranked = sorted(result.scores, key=lambda w: (-result.scores[w][0], w))
    if result.ambiguous:
        floor_candidates = [w for w in ranked if result.scores[w][0] >= B_FLOOR]
        candidates = sorted(
            set(result.ambiguous_families) | set(result.union_families) | set(floor_candidates),
            key=lambda w: (-result.scores.get(w, (1.0, "", ""))[0], w))
        evidence = "; ".join(result.union_evidence) if result.union_evidence \
            else "a single name key matches several different works"
        top_rule = result.scores[candidates[0]][1] if candidates and candidates[0] in result.scores \
            else "T1x"
        return "B", top_rule, 1.0, f"ambiguous: {evidence}", candidates
    if result.union_families:
        rule = max(result.union_rules, key=lambda r: RULE_PRIORITY[r])
        works = sorted(result.union_families, key=index.primary_uuid)
        evidence = "; ".join(sorted(set(result.union_evidence)))
        return "A", rule, 1.0, evidence, works
    if ranked:
        top_work = ranked[0]
        top_score, top_rule, top_evidence = result.scores[top_work]
        if top_score >= A_THRESHOLD:
            rivals = [
                w for w in ranked[1:]
                if result.scores[w][0] >= A_THRESHOLD
                and abs(top_score - result.scores[w][0]) <= A_MARGIN
            ]
            if not rivals:
                return "A", top_rule, top_score, top_evidence, [top_work]
        if top_score >= B_FLOOR:
            return "B", top_rule, top_score, top_evidence, ranked
    return "C", "", result.best_score()[0], f"no candidate at or above {B_FLOOR:.2f}", []


# ---------------------------------------------------------------------------
# Crosscheck orchestration
# ---------------------------------------------------------------------------

def crosscheck(registry: list[dict[str, str]], master: list[dict[str, str]]):
    """Match every registry file.

    Returns ``(rows, index, bucket_counts, d_rows, e_rows, per_file)`` where
    ``per_file`` maps ``registry_path`` → its :class:`FileResult`.
    """
    index = MasterIndex(master)
    for row in master:
        index.row_tokens(row)  # warm the token cache deterministically

    rows: list[dict[str, str]] = []
    matched_families: set[str] = set()
    per_file: dict[str, FileResult] = {}
    bucketed: list[tuple[dict[str, str], tuple]] = []

    for entry in registry:
        stem = entry["Filename"].rsplit(".", 1)[0] if "." in entry["Filename"] else entry["Filename"]
        result = match_registry_file(stem, entry["folder"], index)
        bucket, tier, confidence, evidence, ranked = assign_bucket(result, index)
        per_file[entry["Full Path"]] = result
        if bucket == "A":
            matched_families |= set(ranked)
        bucketed.append((entry, (bucket, tier, confidence, evidence, ranked)))

    for entry, (bucket, tier, confidence, evidence, ranked) in bucketed:
        top_work = ranked[0] if ranked else ""
        matched_uuid = ""
        matched_title = ""
        matched_series = ""
        candidate_uuids = ""
        if bucket == "A":
            uuids: list[str] = []
            titles: list[str] = []
            for work_id in ranked:
                family = index.families[work_id]
                uuids.extend(row["uuid"] for row in family)
                titles.append(family[0]["title"])
                matched_series = matched_series or family[0]["series"]
            matched_uuid = ";".join(sorted(uuids, key=int))
            matched_title = " + ".join(titles)
            if bucket == "A" and len(ranked) > 1:
                evidence += f"; multi-work compilation ({len(ranked)} works)"
        elif top_work:
            parts = []
            for work_id in ranked[:8]:
                score = result.scores.get(work_id, (confidence, "", ""))[0]
                parts.append(f"{index.families[work_id][0]['uuid']}:{score:.2f}")
            more = len(ranked) - min(len(ranked), 8)
            candidate_uuids = ";".join(parts) + (f";+{more} more" if more > 0 else "")
            family = index.families[top_work]
            matched_title = family[0]["title"]
            matched_series = family[0]["series"]
        rows.append({
            "registry_path": entry["Full Path"],
            "folder": entry["folder"],
            "mime": entry["Format (MimeType)"],
            "size_bytes": entry["Size (bytes)"],
            "bucket": bucket,
            "matched_uuid": matched_uuid,
            "matched_title": matched_title,
            "matched_series": matched_series,
            "tier": tier if bucket in {"A", "B"} else "",
            "confidence": f"{confidence:.2f}",
            "evidence": evidence,
            "candidate_uuids": candidate_uuids,
        })

    counts = Counter(row["bucket"] for row in rows)

    # D: master rows owned=true whose work has no A-bucket counterpart.
    d_rows = [
        row for row in master
        if row["owned"] == "true" and row["work_id"] not in matched_families
    ]

    # E: master rows matched by bucket A whose owned is false or blank.
    e_rows = [
        row for row in master
        if row["owned"] != "true" and row["work_id"] in matched_families
    ]
    return rows, index, counts, d_rows, e_rows, per_file


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

def render_csv_text(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        cells = [str(cell).replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def format_bytes(num_bytes: int) -> str:
    return f"{num_bytes / 1_000_000_000:.1f} GB"


def build_report(
    registry: list[dict[str, str]],
    master: list[dict[str, str]],
    rows: list[dict[str, str]],
    index: MasterIndex,
    counts: Counter,
    d_rows: list[dict[str, str]],
    e_rows: list[dict[str, str]],
    per_file: dict[str, FileResult],
) -> str:
    lines: list[str] = []
    push = lines.append

    push("# Final registry crosscheck — `final_registry.csv` × `docs/master.json`")
    push("")
    push("Deterministic, offline crosscheck of the owner's personally-owned file")
    push("registry (259 files) against the published curated master (363 rows).")
    push("This is an **evidence-only analysis**: no `owned` value, master row, or")
    push("other frozen surface was modified — every suggested ruling below is")
    push("listed for the owner to decide, never applied.")
    push("")

    # --- Scope --------------------------------------------------------------
    push("## 1. Scope")
    push("")
    folders = Counter(entry["folder"] for entry in registry)
    mimes = Counter(entry["Format (MimeType)"] for entry in registry)
    total_bytes = sum(int(entry["Size (bytes)"]) for entry in registry)
    owned_master = Counter(
        "true" if row["owned"] == "true" else ("false" if row["owned"] == "false" else "blank")
        for row in master
    )
    push(f"- Registry rows: **{len(registry)}** files, {format_bytes(total_bytes)} total")
    push(f"- Registry folders: " + ", ".join(f"`{name}` {n}" for name, n in sorted(folders.items(), key=lambda kv: (-kv[1], kv[0]))))
    push("- Registry mime types: " + ", ".join(f"`{name}` {n}" for name, n in sorted(mimes.items(), key=lambda kv: (-kv[1], kv[0]))))
    push(f"- Master rows: **{len(master)}** (`owned`: " + ", ".join(f"{k} {v}" for k, v in sorted(owned_master.items())) + ")")
    push("")

    # --- Methodology --------------------------------------------------------
    push("## 2. Methodology")
    push("")
    push("### Why slug-exact matching cannot work")
    push("")
    push("Registry filenames are slug-style **without** a month prefix, while")
    push("Veritas slugs are month-prefixed and `proposed_filename` follows the")
    push("`YYYY-MM - Title [n-m].mp4` scheme. Live examples from the two inputs:")
    push("")
    if index.volume_works.get(1):
        vol = index.families[sorted(index.volume_works[1])[0]][0]
        push(f"- Registry `VolumeSeries/volume-i-power-vs-force.mp4` ↔ master {vol['uuid']}")
        push(f"  `{vol['title']}`; Veritas slug `{slug_tail(vol['source_url_veritas'])}`;")
        push(f"  `proposed_filename` `{vol['proposed_filename']}`.")
    if "283" in index.by_uuid:
        doc = index.by_uuid["283"]
        push("- Registry `DocandSusantalks/what-is-meant-by-spiritual--the-importance-of-family-2014.mp4`")
        push(f"  ↔ master {doc['uuid']} `{doc['title']}`; Veritas slug `{slug_tail(doc['source_url_veritas'])}`;")
        push(f"  `proposed_filename` `{doc['proposed_filename']}`.")
    push("")
    push("Exact slug-to-slug equality therefore fails in general; normalized-title")
    push("matching with folder/series priors is the bridge.")
    push("")
    push("### Normalization")
    push("")
    push("Unicode NFKD fold + casefold + combining-mark removal; apostrophes")
    push("deleted (`Ego's` → `egos`, matching slug `egos`); `[...]` product IDs")
    push("(ASIN/ISBN) stripped; remaining punctuation → spaces; whitespace")
    push("collapsed. Two key forms per name: *compact* (spaces removed, the")
    push("CamelCase bridge: `TheEyeoftheI` → `theeyeofthei`) and *content*")
    push("(stopwords also removed: `The Ego and The Self` → `theegotheself`).")
    push("Trailing date suffixes (`-2014`, `June 2003`, glued `June2003`) and")
    push("author markers (`… by David R. Hawkins`, `… Hawkins, David R.`) are")
    push("stripped into additional comparison variants.")
    push("")
    push("### Matcher tiers")
    push("")
    push(_md_table(
        ["Tier", "Rule", "Fires when"],
        [
            ["T1x", "exact key equality", "a normalized registry name/segment equals a normalized master `title` (full or pre-colon head, edition-marker-stripped), `proposed_filename` stem, or `source_url_veritas` slug tail"],
            ["T1p", "exact after prefix strip", "a known collection prefix (`On the Road…`, `Volume…`, `Satsang…`, `Office Visit…`, `Devotional Nonduality Intensive…`, …) is removed in compact space and the remainder equals a master key"],
            ["T1c", "containment", "a master key (>=12 chars) sits inside the registry name, or a registry key (>=12 chars) sits inside a master key"],
            ["T1f", "fuzzy equality", "compact forms score >= 0.90 (difflib `SequenceMatcher`, gated by length distance and quick ratios)"],
            ["T2ym", "lecture year-month", "`Lectures2002-2011/<month>-<year>.mp4` maps to the unique annual-series work of that year-month"],
            ["T2sm", "satsang month list", "names carrying >=2 month tokens + a year (`satsang-qa-jan-mar-jul-2011`) map to the Satsang Series session(s) of those months"],
            ["T2vol", "volume numerals", "`VolumeSeries/volume-<roman>…` maps to the Volume Series work(s) of that numeral"],
            ["T2t", "token + prior scoring", "significant-token overlap (greedy one-to-one, fuzzy at 0.85; 0.80 for tokens >=9 chars) plus a 0.25 boost from folder↔series or name-prefix priors"],
        ],
    ))
    push("")
    push("Thresholds: **A** = top score >= "
         f"{A_THRESHOLD:.2f} with no different-work rival within {A_MARGIN:.2f}; "
         f"**B** = top score >= {B_FLOOR:.2f} (or any ambiguous exact hit); "
         "**C** = nothing at or above the B floor. T1-channel exact matches carry")
    push("confidence 1.00. Scores print with fixed two-decimal formatting; sort")
    push("orders are stable and no timestamps enter the outputs, so regeneration")
    push("is byte-reproducible (`--check`).")
    push("")
    push("### Grouping rules (T3)")
    push("")
    push("- Double-dash names (`…--…`) split into per-work **segments**, each")
    push("  matched independently; one file covering several works stays ONE row")
    push("  listing every matched work (e.g. the six `Archivalofficeseries` files")
    push("  cover all 16 Office Series masters two-to-three titles at a time).")
    push("- `part1`/`part2` suffixes are stripped before matching so both parts of")
    push("  a split recording resolve to the same single master work.")
    push("- Master rows are grouped by `work_id` (the work × carrier edition")
    push("  model): a file matching a work counts once, whether the work holds 1")
    push("  or 40 master rows, so no edition family is reported as N discrepancies.")
    push("- Bucket-C files with identical normalized names (same title, different")
    push("  extension/brackets) collapse into one review family.")
    push("")

    # --- Bucket counts -------------------------------------------------------
    push("## 3. Bucket counts")
    push("")
    a_count, b_count, c_count = counts.get("A", 0), counts.get("B", 0), counts.get("C", 0)
    push(_md_table(
        ["Bucket", "Meaning", "Files"],
        [
            ["A", "matched to master work(s), high confidence", str(a_count)],
            ["B", "ambiguous — owner review queue", str(b_count)],
            ["C", "registry-only, no plausible master counterpart", str(c_count)],
            ["**A+B+C**", "must equal the registry row count", f"**{a_count + b_count + c_count} / {len(registry)}**"],
        ],
    ))
    push("")
    a_folders = Counter(row["folder"] for row in rows if row["bucket"] == "A")
    push("Bucket A by registry folder: " + ", ".join(
        f"`{name}` {n}" for name, n in sorted(a_folders.items(), key=lambda kv: (-kv[1], kv[0]))))
    push("")

    # --- Review queue (B) -----------------------------------------------------
    push("## 4. Owner review queue — bucket B (rules to decide, nothing applied)")
    push("")
    if b_count:
        queue_rows = []
        for row in rows:
            if row["bucket"] != "B":
                continue
            candidates = []
            for part in row["candidate_uuids"].split(";"):
                if ":" in part:
                    uuid, score = part.split(":")
                    if uuid in index.by_uuid:
                        master_row = index.by_uuid[uuid]
                        candidates.append(
                            f"{uuid} {master_row['title'][:48]} ({score})")
            queue_rows.append([
                f"`{row['registry_path']}`", row["folder"],
                f"{row['tier']} {row['confidence']}",
                "; ".join(candidates[:3]) + ("; …" if len(candidates) > 3 else ""),
            ])
        push(_md_table(["Registry file", "Folder", "Top tier/conf", "Top candidates (uuid, title, score)"], queue_rows))
    else:
        push("None — no ambiguous matches.")
    push("")

    # --- C --------------------------------------------------------------------
    push("## 5. Bucket C — registry-only (candidate new works / non-catalogue assets)")
    push("")
    c_rows = [row for row in rows if row["bucket"] == "C"]
    if c_rows:
        groups: dict[str, list[dict[str, str]]] = {}
        for row in c_rows:
            result = per_file[row["registry_path"]]
            groups.setdefault(result.c_group, []).append(row)
        c_table = []
        for group in sorted(groups):
            members = sorted(groups[group], key=lambda r: r["registry_path"])
            c_table.append([
                f"`{members[0]['registry_path'].rsplit('/', 1)[-1]}`"
                + (f" (+{len(members) - 1} same-name files)" if len(members) > 1 else ""),
                ", ".join(sorted({m['folder'] for m in members})),
                f"best score {members[0]['confidence']}",
            ])
        push(_md_table(["Registry name family", "Folder(s)", "Note"], c_table))
    else:
        push("None.")
    push("")

    # --- D --------------------------------------------------------------------
    push("## 6. Bucket D — master rows `owned=true` with no registry counterpart")
    push("")
    push("Grouped by work (`work_id`). These are the catalogue's flagged-owned")
    push("records for which the owner's file library shows no counterpart file —")
    push("streaming-only holdings, missing files, or files the matcher could not")
    push("attribute. Listed for owner review; **no flags are changed here**.")
    push("")
    d_works: dict[str, list[dict[str, str]]] = {}
    for row in d_rows:
        d_works.setdefault(row["work_id"], []).append(row)
    if d_rows:
        d_table = []
        for work_id in sorted(d_works, key=lambda w: index.primary_uuid(w)):
            family = sorted(d_works[work_id], key=lambda r: int(r["uuid"]))
            titles = sorted({r["title"] for r in family})
            d_table.append([
                ", ".join(r["uuid"] for r in family),
                "; ".join(titles),
                family[0]["series"],
                ", ".join(sorted({r["format"] for r in family})),
            ])
        push(_md_table(["Master uuid(s)", "Title(s)", "Series", "Format"], d_table))
        b_works = {
            part.split(":")[0] and index.by_uuid[part.split(":")[0]]["work_id"]
            for row in rows if row["bucket"] == "B"
            for part in row["candidate_uuids"].split(";") if ":" in part
            and part.split(":")[0] in index.by_uuid
        }
        overlap = sum(1 for work_id in d_works if work_id in b_works)
        push("")
        push(f"{len(d_rows)} rows in {len(d_works)} works. "
             f"{overlap} of those works also appear among bucket-B candidates — "
             "a B ruling could resolve them; the D definition above counts bucket-A "
             "counterparts only.")
    else:
        push("None — every `owned=true` master work has a registry counterpart.")
    push("")

    # --- E --------------------------------------------------------------------
    push("## 7. Bucket E — registry-matched master rows with `owned` false/blank")
    push("")
    push("Evidence for a **future** owner ruling: these master rows match files")
    push("present in the owner's library while the master's `owned` is `false` or")
    push("blank. Nothing is applied — the flags become follow-up work orders only")
    push("after the owner reviews this deck.")
    push("")
    if e_rows:
        file_by_work: dict[str, list[str]] = {}
        for row in rows:
            if row["bucket"] != "A":
                continue
            for uuid in row["matched_uuid"].split(";"):
                if uuid and uuid in index.by_uuid:
                    file_by_work.setdefault(index.by_uuid[uuid]["work_id"], []).append(row["registry_path"])
        e_table = []
        for master_row in sorted(e_rows, key=lambda r: int(r["uuid"])):
            files = sorted(set(file_by_work.get(master_row["work_id"], [])))
            shown = ", ".join(f"`{f}`" for f in files[:2]) + (f" (+{len(files) - 2})" if len(files) > 2 else "")
            e_table.append([
                master_row["uuid"], master_row["owned"] or "(blank)",
                master_row["title"][:60], master_row["series"],
                shown,
            ])
        push(_md_table(["Master uuid", "owned", "Title", "Series", "Matching registry file(s)"], e_table))
    else:
        push("None.")
    push("")

    # --- Related prior art ------------------------------------------------------
    push("## 8. Related prior art (non-authoritative)")
    push("")
    push("GitHub issue #18 (2026-08-04) reported a lak.nz-side Drive cross-check of")
    push("the same `owned` flags, and `review/LINKS_VIMEO_OWNED_FINDINGS.md` §3")
    push("summarizes it. That scan (350 files on an external mount) is **prior")
    push("external evidence only** — lak.nz treats this repo as helper reference")
    push("and opens no PRs here — and its numbers were neither trusted nor reused:")
    push("everything in this report was recomputed from the two committed inputs")
    push("(`final_registry.csv`, `docs/master.json`). Convergences and divergences")
    push("with issue #18's lists are observations, not authorities.")
    push("")

    # --- Reproduction ------------------------------------------------------------
    push("## 9. Reproduction")
    push("")
    push("```bash")
    push("python crosscheck_final_registry.py            # regenerate both outputs")
    push("python crosscheck_final_registry.py --check    # exit 0 iff byte-identical")
    push("python -m unittest tests.test_final_registry_crosscheck -v")
    push("```")
    push("")
    push("Inputs: `final_registry.csv` (read with `encoding=\"utf-8-sig\"`, CRLF-safe)")
    push("and `docs/master.json`. Outputs: `review/final_registry_crosscheck.csv`")
    push("(one row per registry file, 259 data rows) and this report. No network,")
    push("no new dependencies (stdlib only), no timestamps in outputs.")
    push("")
    return "\n".join(lines) + "\n"


def render_outputs() -> tuple[str, str, list[dict[str, str]], MasterIndex, Counter, list, list, dict]:
    """Run the full crosscheck and render both output documents."""
    registry = load_registry()
    master = load_master()
    rows, index, counts, d_rows, e_rows, per_file = crosscheck(registry, master)
    report = build_report(registry, master, rows, index, counts, d_rows, e_rows, per_file)
    return render_csv_text(rows), report, rows, index, counts, d_rows, e_rows, per_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed crosscheck outputs match their declared inputs; do not write files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    csv_text, report_text, rows, index, counts, d_rows, e_rows, _per_file = render_outputs()

    if args.check:
        stale = [
            path for path, text in ((OUT_CSV, csv_text), (OUT_MD, report_text))
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        if stale:
            print("Final-registry crosscheck outputs are stale relative to their inputs:")
            for path in stale:
                print(f"  - {path}")
            print("Run python crosscheck_final_registry.py after reviewing the input change.")
            return 1
        print(f"Crosscheck outputs match their inputs ({len(rows)} registry rows).")
        return 0

    OUT_CSV.write_text(csv_text, encoding="utf-8")
    OUT_MD.write_text(report_text, encoding="utf-8")
    d_works = {row["work_id"] for row in d_rows}
    print(f"Wrote {OUT_CSV} ({len(rows)} rows) and {OUT_MD}")
    print(f"Buckets: A {counts.get('A', 0)} | B {counts.get('B', 0)} | C {counts.get('C', 0)}"
          f"  (A+B+C == {counts.get('A', 0) + counts.get('B', 0) + counts.get('C', 0)} of {len(rows)})")
    print(f"D (owned=true master rows without registry counterpart): {len(d_rows)} rows in {len(d_works)} works")
    print(f"E (matched master rows with owned false/blank — evidence only): {len(e_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
