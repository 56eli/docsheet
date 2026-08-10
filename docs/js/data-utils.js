// =============================================================================
// docs/js/data-utils.js — Pure data utility functions.
// No DOM access, no mutable state. Imported by app.js.
// =============================================================================

/**
 * Format a row's date for mobile browse cards.
 */
export function displayMobileDate(row) {
  if (!row.year) return "Date unknown";
  const year = row.year === "198X" ? "c. 1980s" : row.year;
  return row.month ? `${year} · ${row.month}` : year;
}

/**
 * Format a row's edition for mobile browse cards.
 */
export function displayMobileEdition(row) {
  return [row.format, row.format_detail].filter(Boolean).join(" · ") || "Edition not stated";
}

/**
 * Only the Power vs. Force double (extra hardcover row 373) shows the Extra badge.
 */
export function isExtraEditionRow(row) {
  const workId = String(row.work_id || "").trim();
  const uuid = String(row.uuid || "").trim();
  return workId === "w-power-vs-force" && uuid === "373";
}

/**
 * Get the primary source URL for a row (mobile browse cards).
 */
export function mobilePrimaryUrl(row) {
  return row.source_url_veritas || row.source_url_hay_house ||
    row.source_url_audible || row.source_url_nightingale_conant ||
    row.source_url_amazon || "";
}

/**
 * Group rows by work_id for the mobile browse work-card view.
 */
export function mobileWorkGroups(rows) {
  const groups = new Map();
  rows.forEach((row, index) => {
    const key = row.work_id || row.uuid || row.candidate_key || `record-${index}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  });
  return [...groups.values()];
}

/**
 * Check if a row is owned (boolean string or blank).
 */
export function ownedValue(row) {
  return String(row.owned ?? "").toLowerCase();
}

/**
 * Compute a year span string for a set of rows (e.g. "2002–2011").
 */
export function yearSpanFor(rows) {
  const years = [...new Set(
    rows.map((row) => String(row.year || "").trim())
      .filter((year) => /^\d{4}$/.test(year))
      .map(Number),
  )].sort((a, b) => a - b);
  if (!years.length) return "years unrecorded";
  return years.length === 1 ? String(years[0]) : `${years[0]}–${years[years.length - 1]}`;
}

/**
 * Format an ISO timestamp for display.
 */
export function formatTimestamp(iso) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

/**
 * Debounce a function by `ms` milliseconds.
 */
export function debounce(fn, ms) {
  let t;
  return function (...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), ms);
  };
}
