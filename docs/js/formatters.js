// =============================================================================
// docs/js/formatters.js — Cell rendering, status badges, search highlighting,
// and catalogue-block classification. Imported by app.js.
// =============================================================================

import { COLUMN_LABELS, RECORD_TYPE_LABELS, RECORD_TYPE_TITLES } from "./config.js?v=94f497018c49";

// ---------------------------------------------------------------------------
// Status badges — CSS class + human-readable label for status-typed fields.
// ---------------------------------------------------------------------------

export function statusClass(value) {
  const normalized = String(value ?? "").toLowerCase();
  if (normalized === "master") return "status-master";
  if (normalized.startsWith("candidate_")) return "status-candidate";
  if (/(excluded|rejected)/.test(normalized)) return "status-excluded";
  if (/(pending|needs|unmatched|not\.promoted|unique_item|compilation_or_new_edition|^false$)/.test(normalized)) return "status-pending";
  if (/(approved|reviewed|matched|^item$|^true$)/.test(normalized)) return "status-approved";
  return "status-neutral";
}

export function formatClass(value) {
  const normalized = String(value ?? "").toLowerCase().trim();
  if (normalized === "dvd") return "status-approved";
  if (normalized === "cd") return "status-approved";
  if (normalized === "streaming") return "status-pending";
  if (normalized === "audio") return "status-neutral";
  if (normalized === "book") return "status-master";
  return "status-neutral";
}

export function statusLabel(field, value) {
  if (field === "record_type" && RECORD_TYPE_LABELS[value]) {
    return RECORD_TYPE_LABELS[value];
  }
  if (field === "owned" || field === "proposed_owned") {
    const v = String(value ?? "").toLowerCase();
    if (v === "true") return "Owned";
    return "";
  }
  return value.replace(/_/g, " ");
}

export function statusFormatter(cell) {
  const value = String(cell.getValue() ?? "");
  if (!value) return "";
  const field = cell.getColumn().getField();
  const label = statusLabel(field, value);
  if (!label) return "";
  const badge = document.createElement("span");
  badge.className = `status-badge ${statusClass(value)}`;
  badge.textContent = label;
  badge.title = (field === "record_type" && RECORD_TYPE_TITLES[value]) || value;
  return badge;
}

// ---------------------------------------------------------------------------
// Search highlighting lives in app.js (closure over activeSearchQuery).
// escapeRegex and renderHighlightedText are defined there, not here.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Row title — the display title for row details and mobile browse cards.
// ---------------------------------------------------------------------------

export function rowTitle(data) {
  return data.title || data.candidate_title || data.official_title ||
    data.official_product_title || data.master_title || data.review_sheet ||
    data.publisher || data.relationship_id || data.raw_title || "Selected row";
}

export function primaryIdentifier(data) {
  return data?.uuid || data?.master_uuid || data?.veritas_product_id ||
    data?.source_product_id || data?.candidate_key || "";
}

// ---------------------------------------------------------------------------
// Catalogue block classification — maps each master row to a colour block.
// ---------------------------------------------------------------------------

let _catalogueBlockMap = {};

export function loadCatalogueBlockMap() {
  return fetch("catalogue-block-map.json", { cache: "no-store" })
    .then((res) => (res.ok ? res.json() : null))
    .then((map) => {
      if (map) _catalogueBlockMap = map;
    })
    .catch(() => {});
}

export function getRowBlockId(data) {
  if (!data) return "undecided";
  const uuid = String(data.uuid || "").trim();
  if (_catalogueBlockMap && _catalogueBlockMap[uuid]) {
    return _catalogueBlockMap[uuid];
  }
  const series = String(data.series || "").trim();
  const type = String(data.item_type || "").trim();
  const notes = String(data.notes || "").trim();

  if (uuid === "315" || notes.includes("FRAN GRACE")) return "fran-grace";
  if (series === "Lecture Highlights" || type === "highlight") return "lecture-highlights";
  if (series === "Discussion Series" || type === "discussion") return "discussion";
  if (series === "Satsang Series") return "satsang";
  if (series === "On The Road Talk Series") return "on-the-road";
  if (series === "Volume Series") return "volume-series";
  if (series === "Office Series") return "office-series";
  if (series === "Transcription Series Books") return "transcription-books";
  if (series === "Books" || type === "book") return "books";
  if (series === "Media Miscellaneous") return "media-misc";
  return "undecided";
}
