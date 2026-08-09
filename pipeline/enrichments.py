#!/usr/bin/env python3
"""Master draft data transformation and enrichment functions."""

from __future__ import annotations

import re
from pathlib import Path

from _common import read_csv
from pipeline.helpers import (
    index_csv,
    require_columns,
    veritas_products_by_url,
)

# Constants & Paths
DATA_DIR = Path("data")
LEDGER = Path("migration_review_ledger.csv")
OUTPUT_CSV = DATA_DIR / "research_master_draft.csv"
OUTPUT_JSON = DATA_DIR / "research_master_draft.json"
EXCLUSIONS = DATA_DIR / "research_master_exclusions.csv"
SOURCE_OVERRIDES = DATA_DIR / "research_master_source_overrides.csv"
MANUAL_CANDIDATES = DATA_DIR / "manual_master_candidates.csv"
VERITAS_PRODUCTS = DATA_DIR / "veritas_official_products.csv"
AUDIBLE_PRODUCTS = DATA_DIR / "audible_official_products.csv"
HAYHOUSE_PRODUCTS = DATA_DIR / "hayhouse_official_products.csv"
PROMOTIONS = DATA_DIR / "manual_candidate_promotions.csv"
SERIES_MAPPING = DATA_DIR / "series_category_mapping.csv"
WORK_FAMILIES = DATA_DIR / "work_families.csv"
EDITION_CANDIDATES = DATA_DIR / "edition_candidates.csv"
EDITION_PROMOTIONS = DATA_DIR / "edition_promotions.csv"
VERITAS_STREAMING = DATA_DIR / "veritas_streaming_urls.csv"
FILENAME_PROPOSAL = DATA_DIR / "filename_proposal_YYYYMM.csv"
YEAR_OVERRIDES = DATA_DIR / "master_year_overrides.csv"
NOTES_OVERRIDES = DATA_DIR / "master_notes_overrides.csv"

SOURCE_OVERRIDE_FIELDS = {
    "source_url_veritas",
    "source_url_hay_house",
    "source_url_nightingale_conant",
    "source_url_audible",
    "source_url_amazon",
}
SOURCE_OVERRIDE_REQUIRED_COLUMNS = {
    "raw_row_number",
    "target_field",
    "override_value",
    "review_status",
}
WORK_FAMILY_REQUIRED_COLUMNS = {
    "work_id",
    "member_master_uuid",
    "canonical_work_title",
    "evidence_note",
    "review_status",
    "reviewed_on",
}
WORK_FAMILY_STATUSES = {"approved", "proposed", "rejected"}
SERIES_MAPPING_REQUIRED_COLUMNS = {
    "veritas_product_id",
    "official_title",
    "matched_master_uuids",
    "mapped_series",
    "review_status",
}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def backfill_months_from_official_source(items: list[dict[str, str]]) -> int:
    """Derive missing year/month from Veritas inventory published_date."""
    import generate_migration_ledger as ledger_tools

    veritas_by_url = veritas_products_by_url() if VERITAS_PRODUCTS.exists() else {}
    DO_NOT_BACKFILL_YEAR = {"254", "255", "256", "302"}

    filled = 0
    for item in items:
        item_type = item.get("item_type", "")
        if item_type == "book":
            continue
        if item.get("series", "").strip() == "Volume Series":
            continue
        if item.get("raw_row_number", "").strip() in DO_NOT_BACKFILL_YEAR and not item.get("year", "").strip():
            continue
        url = item.get("source_url_veritas", "").strip()

        if url and url in veritas_by_url:
            pub_date = veritas_by_url[url].get("published_date", "").strip()
            if pub_date:
                try:
                    date_parts = pub_date.split("-")
                    if len(date_parts) >= 2:
                        year = date_parts[0]
                        month = date_parts[1]
                        if not item.get("year", "").strip():
                            item["year"] = year
                            item["month"] = month
                            filled += 1
                        elif item["year"] == year:
                            if not item.get("month", "").strip():
                                item["month"] = month
                                filled += 1
                        continue
                except (ValueError, IndexError):
                    pass

        if item["month"] or not item["legacy_tempid"]:
            continue
        month = ledger_tools.proposed_month(
            item["legacy_tempid"].strip(), item["source_url_veritas"]
        )
        if month:
            item["month"] = month
            filled += 1
    return filled


def infer_format_from_official_source(
    item: dict[str, str],
    veritas_by_id: dict[str, dict[str, str]],
    veritas_by_url: dict[str, dict[str, str]] | None = None,
) -> str:
    """Infer a missing format from Veritas product slug, title, and category."""
    if item.get("format"):
        return ""
    url = item.get("source_url_veritas", "").strip()
    slug = url.rstrip("/").split("/")[-1].lower() if url else ""

    prod: dict[str, str] = {}
    if url:
        if veritas_by_url:
            prod = veritas_by_url.get(url, {})
        if not prod:
            pid = slug.split("-")[0] if "-" in slug else slug
            prod = veritas_by_id.get(pid, {})
    ot = (prod.get("official_title", "") or item.get("title", "")).lower()

    if url:
        if any(k in slug for k in ("video", "muscle-testing-video")) or slug.startswith(("volume-", "vol-")):
            return "DVD"
        if "cd-set" in slug or ("satsang" in slug and "cd" in slug):
            return "CD"
        if any(k in slug for k in ("question-answer", "question-and-answer", "q&a")):
            return "streaming"
        if "https-" in slug or "https" == slug[:5]:
            return ""
        cd_tokens = {"cd", "cds", "cd-set", "cdset"}
        if any(seg in cd_tokens for seg in slug.split("-")) or re.search(
            r"\bcd set\b|\bcds\b|compact disc|disc set", ot
        ):
            return "CD"
        if "audio" in slug or "– audio" in ot or " audio" in ot:
            return "audiobook"
        if "book" in slug or "(book)" in ot:
            return "book"
    if (
        item.get("item_type") == "book"
        and "Books Published by Dr. Hawkins" in prod.get("official_categories", "")
    ):
        return "book"
    cats = prod.get("official_categories", "")
    if "On the Road - Talk Series" in cats or "Archival Office Visit Series" in cats or "Volume Series" in cats:
        return "DVD"
    if "Satsang" in cats:
        return "CD"
    if "Discussion Series" in cats:
        return "streaming"
    if "Lecture Highlights" in cats:
        return "streaming"
    if item.get("item_type") == "book" and not url:
        return "book"
    return ""


def _strip_title_part_noise(title: str) -> str:
    """Remove trailing part/disc and transcoding noise from a lecture title."""
    title = re.sub(r"\s*(\(\s*part\s*\d+\s*\)|part\s*\d+|dvd\d*|cd\d*)\s*$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\s*-\s*converted\s*$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\.mp4\s*$", "", title, flags=re.IGNORECASE).strip()
    return title


def _normalized_title(title: str) -> str:
    """Lowercase, punctuation-free, whitespace-collapsed key for title matching."""
    lowered = title.lower()
    lowered = re.sub(r"[^a-z0-9 ]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def apply_official_title_cleanup(items: list[dict[str, str]], veritas_products: list[dict[str, str]]) -> int:
    """Clean a lecture's public title only when the stripped form matches the official listing."""
    by_url = {product["official_product_url"]: product for product in veritas_products}
    changed = 0
    for item in items:
        if item.get("item_type") != "lecture":
            continue
        url = item.get("source_url_veritas", "").strip()
        if not url or url not in by_url:
            continue
        official = by_url[url].get("official_title", "")
        current = item.get("title", "")
        cleaned = _strip_title_part_noise(current)
        if cleaned != current and _normalized_title(cleaned) == _normalized_title(official):
            item["title"] = cleaned
            evidence = f"Title cleaned against official listing: {official}"
            item["notes"] = f"{item.get('notes', '')}; {evidence}".lstrip("; ")
            changed += 1
    return changed


def apply_veritas_streaming_urls(items: list[dict[str, str]]) -> int:
    """Apply approved Veritas streaming page URLs as reference_url_1."""
    if not VERITAS_STREAMING.exists():
        return 0
    require_columns(VERITAS_STREAMING, {"veritas_product_id", "streaming_url", "review_status"})
    streaming = {row["veritas_product_id"].strip(): row for row in read_csv(VERITAS_STREAMING) if row["review_status"].strip() == "approved"}
    if not streaming:
        return 0
    veritas_by_url = veritas_products_by_url() if VERITAS_PRODUCTS.exists() else {}
    applied = 0
    for item in items:
        v_url = item.get("source_url_veritas", "").strip()
        if not v_url:
            continue
        prod = veritas_by_url.get(v_url)
        if not prod:
            continue
        pid = prod.get("veritas_product_id", "").strip()
        s_row = streaming.get(pid)
        if not s_row:
            continue
        s_url = s_row.get("streaming_url", "").strip()
        if not s_url or not s_url.startswith("https://"):
            continue
        if not item.get("reference_url_1", "").strip():
            item["reference_url_1"] = s_url
            applied += 1
    if applied:
        print(
            f"[streaming] Filled reference_url_1 on {applied} master rows "
            f"from {len(streaming)} approved Veritas streaming products"
        )
    return applied


def apply_filename_proposal(items: list[dict[str, str]]) -> int:
    """Apply proposed filenames from data/filename_proposal_YYYYMM.csv as proposed_filename column."""
    if not FILENAME_PROPOSAL.exists():
        return 0
    from pipeline.validators import validate_filename_proposal_groups
    validate_filename_proposal_groups()
    require_columns(FILENAME_PROPOSAL, {"uuid", "proposed_filename"})
    mapping = {row["uuid"].strip(): row["proposed_filename"].strip() for row in read_csv(FILENAME_PROPOSAL)}
    applied = 0
    for item in items:
        uuid = item.get("uuid", "").strip()
        if not uuid:
            continue
        prop = mapping.get(uuid, "")
        if prop:
            if item.get("proposed_filename", "") != prop:
                item["proposed_filename"] = prop
                applied += 1
        else:
            item.setdefault("proposed_filename", "")
    if applied:
        print(f"[filename] Applied {applied} proposed filenames from {FILENAME_PROPOSAL}")
    return applied


def apply_source_overrides(items: list[dict[str, str]]) -> int:
    """Apply explicit, approved official-source links after ledger migration."""
    if not SOURCE_OVERRIDES.exists():
        return 0

    require_columns(SOURCE_OVERRIDES, SOURCE_OVERRIDE_REQUIRED_COLUMNS)
    overrides = read_csv(SOURCE_OVERRIDES)

    items_by_raw = {}
    for row in items:
        if row["raw_row_number"]:
            items_by_raw[row["raw_row_number"]] = row
        if row.get("candidate_key"):
            items_by_raw[row["candidate_key"]] = row
    
    seen: set[tuple[str, str]] = set()
    for line_number, override in enumerate(overrides, start=2):
        raw_row = override["raw_row_number"].strip()
        target_field = override["target_field"].strip()
        value = override["override_value"].strip()
        status = override["review_status"].strip()
        key = (raw_row, target_field)

        if not raw_row or raw_row not in items_by_raw:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} references a non-item raw row: {raw_row!r}"
            )
        if target_field not in SOURCE_OVERRIDE_FIELDS:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} cannot override {target_field!r}; "
                f"allowed fields: {', '.join(sorted(SOURCE_OVERRIDE_FIELDS))}"
            )
        if status not in {"approved", "proposed"}:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} review_status must be 'approved' or 'proposed'"
            )
        if not value.startswith("https://"):
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} must contain an HTTPS URL"
            )
        if key in seen:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} duplicates an override for {raw_row}/{target_field}"
            )
        if items_by_raw[raw_row][target_field] and items_by_raw[raw_row][target_field] != value:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} conflicts with the raw-ledger value for "
                f"{raw_row}/{target_field}; model a separate relationship instead"
            )
        if status == "approved":
            items_by_raw[raw_row][target_field] = value
        seen.add(key)
    return sum(1 for override in overrides if override["review_status"].strip() == "approved")


def apply_work_families(items: list[dict[str, str]]) -> int:
    """Assign ``work_id`` from the reviewed work-families input."""
    if not WORK_FAMILIES.exists():
        return 0
    require_columns(WORK_FAMILIES, WORK_FAMILY_REQUIRED_COLUMNS)
    rows = read_csv(WORK_FAMILIES)

    master_by_uuid = {item["uuid"]: item for item in items}
    work_id_by_member: dict[str, str] = {}
    for line_number, row in enumerate(rows, start=2):
        work_id = row["work_id"].strip()
        member = row["member_master_uuid"].strip()
        status = row["review_status"].strip()
        reviewed_on = row["reviewed_on"].strip()
        if not work_id or not member:
            raise ValueError(
                f"{WORK_FAMILIES.name}:{line_number} needs non-empty work_id and member_master_uuid"
            )
        if status not in WORK_FAMILY_STATUSES:
            raise ValueError(
                f"{WORK_FAMILIES.name}:{line_number} has invalid review_status {status!r}; "
                f"allowed values are {', '.join(sorted(WORK_FAMILY_STATUSES))}"
            )
        if member not in master_by_uuid:
            raise ValueError(
                f"{WORK_FAMILIES.name}:{line_number} references an unknown master ID: {member!r}"
            )
        if member in work_id_by_member:
            raise ValueError(
                f"{WORK_FAMILIES.name}:{line_number} lists master ID {member} twice; "
                "one row per family member"
            )
        if status == "approved":
            if not ISO_DATE.fullmatch(reviewed_on):
                raise ValueError(
                    f"{WORK_FAMILIES.name}:{line_number} approved rows need an ISO reviewed_on date"
                )
            if not row["evidence_note"].strip():
                raise ValueError(
                    f"{WORK_FAMILIES.name}:{line_number} approved rows must explain the evidence"
                )
            if not row["canonical_work_title"].strip():
                raise ValueError(
                    f"{WORK_FAMILIES.name}:{line_number} approved rows need a canonical work title"
                )
            work_id_by_member[member] = work_id

    applied = 0
    for item in items:
        work_id = work_id_by_member.get(item["uuid"], "")
        if work_id:
            item["work_id"] = work_id
            applied += 1
    if applied:
        print(f"[work-families] Applied {applied} approved work-family memberships")
    return applied


def apply_series_approvals(items: list[dict[str, str]]) -> int:
    """Apply approved taxonomy-to-series mappings after item assembly."""
    if not SERIES_MAPPING.exists():
        return 0
    by_uuid = {item["uuid"]: item for item in items}
    approved: dict[str, str] = {}
    require_columns(SERIES_MAPPING, SERIES_MAPPING_REQUIRED_COLUMNS)
    for line_number, row in enumerate(read_csv(SERIES_MAPPING), start=2):
        if row["review_status"].strip() != "approved":
            continue
        series = row["mapped_series"].strip()
        if not series:
            raise ValueError(
                f"{SERIES_MAPPING}:{line_number} approved rows require a mapped_series"
            )
        uuids = [part.strip() for part in row["matched_master_uuids"].split(";") if part.strip()]
        for uuid in uuids:
            if uuid not in by_uuid:
                raise ValueError(
                    f"{SERIES_MAPPING}:{line_number} references an unknown master ID: {uuid!r}"
                )
            prior = approved.get(uuid)
            if prior is not None and prior != series:
                raise ValueError(
                    f"{SERIES_MAPPING}:{line_number} gives master ID {uuid} "
                    f"conflicting approved series ({prior!r} vs {series!r})"
                )
            approved[uuid] = series
    changed = 0
    for uuid, series in approved.items():
        item = by_uuid[uuid]
        if item["series"] != series:
            item["series"] = series
            changed += 1
    if approved:
        print(
            f"[series-taxonomy] {len(approved)} approved mappings cover "
            f"{len(approved)} master IDs; {changed} series values changed"
        )
    return changed


def apply_year_overrides(items: list[dict[str, str]]) -> int:
    """Apply reviewed owner year overrides after all derivation steps."""
    if not YEAR_OVERRIDES.exists():
        return 0
    require_columns(YEAR_OVERRIDES, {"uuid", "year", "month", "year_source", "review_status"})
    overrides = read_csv(YEAR_OVERRIDES)
    by_uuid = {item["uuid"]: item for item in items}
    applied = 0
    for line_number, row in enumerate(overrides, start=2):
        uuid = row["uuid"].strip()
        if row["review_status"].strip() != "approved":
            raise ValueError(
                f"{YEAR_OVERRIDES.name}:{line_number} uuid {uuid} is not approved"
            )
        if uuid not in by_uuid:
            raise ValueError(
                f"{YEAR_OVERRIDES.name}:{line_number} uuid {uuid} is not a master record"
            )
        year = row["year"].strip()
        month = row["month"].strip()
        if year and not (year.isdigit() and len(year) == 4 or year == "198X"):
            raise ValueError(
                f"{YEAR_OVERRIDES.name}:{line_number} uuid {uuid} has malformed year {year!r}"
            )
        if month and not (month.isdigit() and 1 <= int(month) <= 12):
            raise ValueError(
                f"{YEAR_OVERRIDES.name}:{line_number} uuid {uuid} has malformed month {month!r}"
            )
        item = by_uuid[uuid]
        item["year"] = year
        item["month"] = month
        item["year_source"] = row["year_source"].strip()
        applied += 1
    if applied:
        print(f"[year-overrides] Applied {applied} owner year overrides from {YEAR_OVERRIDES.name}")
    return applied


def apply_notes_overrides(items: list[dict[str, str]]) -> int:
    """Apply reviewed owner notes overrides last."""
    if not NOTES_OVERRIDES.exists():
        return 0
    require_columns(NOTES_OVERRIDES, {"uuid", "notes", "review_status"})
    overrides = read_csv(NOTES_OVERRIDES)
    by_uuid = {item["uuid"]: item for item in items}
    applied = 0
    for line_number, row in enumerate(overrides, start=2):
        uuid = row["uuid"].strip()
        if row["review_status"].strip() != "approved":
            raise ValueError(
                f"{NOTES_OVERRIDES.name}:{line_number} uuid {uuid} is not approved"
            )
        if uuid not in by_uuid:
            raise ValueError(
                f"{NOTES_OVERRIDES.name}:{line_number} uuid {uuid} is not a master record"
            )
        by_uuid[uuid]["notes"] = row["notes"].strip()
        applied += 1
    if applied:
        print(f"[notes-overrides] Applied {applied} owner notes overrides from {NOTES_OVERRIDES.name}")
    return applied


def apply_year_source_provenance(items: list[dict[str, str]], ledger: list[dict[str, str]]) -> None:
    """Set ``year_source`` — a human-readable explanation of how each row's ``year`` was derived."""
    ledger_by_raw: dict[str, dict[str, str]] = {}
    try:
        ledger_by_raw = {r["raw_row_number"]: r for r in ledger if r.get("raw_row_number")}
    except (KeyError, TypeError):
        pass
    manual_by_key: dict[str, dict[str, str]] = {}
    edition_by_key: dict[str, dict[str, str]] = {}
    v_by_url: dict[str, dict[str, str]] = {}
    if MANUAL_CANDIDATES.exists():
        try:
            manual_by_key = index_csv(MANUAL_CANDIDATES, "candidate_key")
        except (KeyError, ValueError, OSError):
            pass
    if EDITION_CANDIDATES.exists():
        try:
            edition_by_key = index_csv(EDITION_CANDIDATES, "candidate_key")
        except (KeyError, ValueError, OSError):
            pass
    if VERITAS_PRODUCTS.exists():
        try:
            v_by_url = veritas_products_by_url()
        except (KeyError, ValueError, OSError):
            pass
    by_uuid = {it["uuid"]: it for it in items}

    for it in items:
        year = it.get("year", "").strip()
        raw = it.get("raw_row_number", "").strip()
        ckey = it.get("candidate_key", "").strip()
        series = it.get("series", "").strip()
        item_type = it.get("item_type", "").strip()
        veritas_url = it.get("source_url_veritas", "").strip()
        src = ""

        if raw and raw in ledger_by_raw:
            lrow = ledger_by_raw[raw]
            prop_year = (lrow.get("proposed_year") or "").strip()
            if prop_year:
                if item_type == "book":
                    src = f"Ledger: first-publication {prop_year}"
                else:
                    src = f"Ledger: recording date {prop_year}" if prop_year == year else f"Ledger: {prop_year} → final {year}"
            else:
                if series == "Volume Series":
                    src = "Blank: intentional pre-2000 (Volume Series)"
                elif not year:
                    src = "Blank: under investigation"
                else:
                    prod = v_by_url.get(veritas_url)
                    if prod:
                        pd = prod.get("published_date", "")
                        src = f"Veritas listing backfill (product {prod.get('veritas_product_id')} {pd})"
                    else:
                        src = f"Veritas listing backfill (year {year})"
        elif ckey:
            orig = ckey.replace("candidate:", "")
            if orig.startswith("manual-"):
                mc = manual_by_key.get(orig)
                if mc:
                    src_name = mc.get("source_name", "")
                    py = (mc.get("proposed_year") or "").strip()
                    if src_name == "academic":
                        src = f"Academic: {year} first-publication"
                    elif py:
                        src = f"Manual candidate: {year} ({orig})"
                    else:
                        src = "Blank: manual candidate blank" if not year else f"Manual candidate blank → {year}"
                else:
                    src = f"Manual candidate unknown {orig}"
            elif orig.startswith("edition-"):
                ec = edition_by_key.get(orig)
                if ec:
                    py = (ec.get("proposed_year") or "").strip()
                    matched = ec.get("matched_master_uuid", "")
                    if py and py == year:
                        matched_item = by_uuid.get(matched, {})
                        matched_year = matched_item.get("year", "") if matched_item else ""
                        if matched_year and matched_year == py and orig not in {
                            "edition-veritas-pvf-audiobook", "edition-audible-pvf", "edition-audible-eye",
                            "edition-audible-tvf", "edition-audible-lettinggo", "edition-audible-healing",
                            "edition-audible-transcending", "edition-audible-itwbnoi", "edition-audible-hle",
                        }:
                            src = f"Edition inherited from matched master {matched} ({year})"
                        else:
                            src = f"Edition promotion: {year}"
                    elif not py and year:
                        prod = v_by_url.get(veritas_url)
                        if prod:
                            src = f"Veritas listing backfill (edition) product {prod.get('veritas_product_id')} {prod.get('published_date')}"
                        else:
                            src = f"Edition inherited / backfill: {year}"
                    elif not year:
                        src = "Blank: edition candidate blank"
                    else:
                        src = f"Edition: candidate {py} → final {year}"
                else:
                    src = f"Edition unknown {orig}"
            else:
                src = f"Unknown candidate {orig}"
        else:
            src = "Unknown"

        it["year_source"] = src[:200]


def migrate_notes_to_research(items: list[dict[str, str]]) -> int:
    """Move provenance/audit-trail content from the notes column into a
    dedicated research column. Only the FRAN GRACE owner-applied marker
    stays in notes (owner directive 2026-08-09).

    Returns the number of rows migrated.
    """
    migrated = 0
    for item in items:
        notes = item.get("notes", "").strip()
        if not notes:
            item.setdefault("research", "")
            continue
        # Keep FRAN GRACE in notes — it's an owner-applied marker, not provenance.
        if "FRAN GRACE" in notes:
            item.setdefault("research", "")
            continue
        # Move everything else to the research column.
        item["research"] = notes
        item["notes"] = ""
        migrated += 1
    if migrated:
        print(f"[notes→research] Migrated {migrated} provenance entries from notes to research column")
    return migrated
