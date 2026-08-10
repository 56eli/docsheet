// =============================================================================
// docs/js/columns.js — Column definitions, width measurement, and ordering.
// Pure column-building logic extracted from app.js. Imported by app.js.
// =============================================================================

import {
  COLUMN_LABELS, STATUS_FIELDS, FORMAT_FIELDS,
  DEFAULT_PRIORITY_FIELDS, LOW_PRIORITY_FIELDS, COLUMN_BUDGETS,
  COLUMN_PRESETS, humanizeField,
} from "./config.js";
import {
  statusClass, formatClass, statusLabel, statusFormatter,
} from "./formatters.js";
import { isExtraEditionRow } from "./data-utils.js";

/**
 * Check if a string looks like a URL.
 */
export function looksLikeUrl(value) {
  return typeof value === "string" && /^https?:\/\//i.test(value.trim());
}

/**
 * Produce a human-readable label for a URL field (e.g. "Veritas product").
 */
export function urlLabelFor(field, value) {
  const normalizedField = field.toLowerCase();
  const sourceLabels = [
    ["veritas", "Veritas product"],
    ["hay_house", "Hay House product"],
    ["nightingale_conant", "Nightingale-Conant listing"],
    ["amazon", "Amazon page"],
    ["audible", "Audible listing"],
    ["evidence", "Evidence"],
    ["reference", "Streaming link"],
    ["catalogue", "Catalogue"],
    ["official", "Official product"],
    ["source", "Source"],
  ];
  const matched = sourceLabels.find(([needle]) => normalizedField.includes(needle));
  if (matched) return matched[1];

  try {
    return new URL(value).hostname.replace(/^www\./, "");
  } catch (err) {
    return "Open link";
  }
}

/**
 * Cell formatter for URL columns — renders clickable links with meaningful labels.
 */
export function urlFormatter(cell) {
  const value = String(cell.getValue() ?? "").trim();
  if (!looksLikeUrl(value)) return value;
  const anchor = document.createElement("a");
  anchor.className = "url-link";
  anchor.href = value;
  anchor.target = "_blank";
  anchor.rel = "noopener noreferrer";
  anchor.title = value;
  anchor.textContent = urlLabelFor(cell.getColumn().getField(), value);
  anchor.setAttribute("aria-label", `${anchor.textContent} (opens in new tab)`);
  return anchor;
}

/**
 * Get the column preset for a view (priority, frozen, hidden columns).
 */
export function columnPresetFor(viewName) {
  return COLUMN_PRESETS[viewName] || { priority: DEFAULT_PRIORITY_FIELDS, frozen: [] };
}

/**
 * Order column keys for a view: priority fields first, then dynamic, then low-priority.
 */
export function orderKeysForView(keys, viewName) {
  const preset = columnPresetFor(viewName);
  const priority = [...new Set([...(preset.priority || []), ...DEFAULT_PRIORITY_FIELDS])]
    .filter((key) => keys.includes(key));
  const lowPriority = LOW_PRIORITY_FIELDS.filter((key) => keys.includes(key));
  const ordered = [
    ...priority,
    ...keys.filter((key) => !priority.includes(key) && !lowPriority.includes(key)),
    ...lowPriority,
  ];
  const deduped = [...new Set(ordered)];
  // Per-view placement overrides: park a column immediately after another.
  Object.entries(preset.moveAfter || {}).forEach(([field, anchor]) => {
    const from = deduped.indexOf(field);
    if (from === -1) return;
    deduped.splice(from, 1);
    const at = deduped.indexOf(anchor);
    deduped.splice(at === -1 ? deduped.length : at + 1, 0, field);
  });
  return deduped;
}

/* --------------------------------------------------------------------------- *
 *  Column width engine — measures rendered text in real pixels via an offscreen
 *  canvas, across ALL rows (not a sample). URL columns measure their link
 *  label, badge columns measure humanized badge text, and header titles
 *  (with sort indicators) are included in the measurement.
 * --------------------------------------------------------------------------- */
const _measureContext = document.createElement("canvas").getContext("2d");
const CELL_FONT = '14px Roboto, "Segoe UI", Arial, sans-serif';
const BADGE_FONT = '600 11px Roboto, "Segoe UI", Arial, sans-serif';
const HEADER_FONT = '600 13px Roboto, "Segoe UI", Arial, sans-serif';
const CELL_PADDING = 20;
const BADGE_PADDING = 14;
const HEADER_EXTRA = 24;
const MAX_TEXT_WIDTH = 560;
const MAX_COLUMN_WIDTH = 720;

function measureText(text, font) {
  _measureContext.font = font;
  return _measureContext.measureText(text).width;
}

function renderedValueForWidth(key, value) {
  const raw = String(value ?? "").trim();
  if (!raw) return "";
  if (looksLikeUrl(raw)) return urlLabelFor(key, raw);
  if (STATUS_FIELDS.has(key)) return statusLabel(key, raw);
  return raw;
}

export function measuredColumnWidth(key, headerTitle, rows) {
  const isBadge = STATUS_FIELDS.has(key) || FORMAT_FIELDS.has(key);
  const isMono = key === "proposed_filename";
  const font = isMono
    ? '13.5px ui-monospace, "SF Mono", Menlo, Consolas, monospace'
    : (isBadge ? BADGE_FONT : CELL_FONT);
  const padding = isBadge ? BADGE_PADDING : CELL_PADDING;
  let maxPx = measureText(headerTitle, HEADER_FONT) + HEADER_EXTRA;
  for (const row of rows) {
    const text = renderedValueForWidth(key, row[key]);
    if (!text) continue;
    const px = measureText(text, font) + padding;
    if (px > maxPx) maxPx = px;
  }
  return Math.ceil(maxPx);
}

/**
 * Build Tabulator column definitions from data rows for the given view.
 * `renderHighlightedText` and `activeSearchQuery` are passed in from app.js
 * (they close over the module-scope search state).
 */
export function buildColumns(data, viewName, expertColumnsOn, expertHiddenFields, renderHighlightedText, activeSearchQuery) {
  if (!Array.isArray(data) || data.length === 0) return [];

  let keys = orderKeysForView(Object.keys(data[0]), viewName);
  if (keys.includes("year_month")) {
    keys = keys.filter((key) => key !== "year" && key !== "month");
  }
  if (keys.includes("edition")) {
    keys = keys.filter((key) => key !== "format" && key !== "format_detail");
  }
  const preset = columnPresetFor(viewName);
  const hiddenByDefault = new Set(expertColumnsOn(viewName) ? [] : expertHiddenFields(viewName));

  return keys.map((key) => {
    const nonEmpty = data.map((r) => r[key]).filter((v) => v !== null && v !== undefined && v !== "");
    const urlRatio = nonEmpty.length
      ? nonEmpty.filter(looksLikeUrl).length / nonEmpty.length
      : 0;

    const budget = COLUMN_BUDGETS[key] || {};
    const col = {
      title: humanizeField(key),
      field: key,
      headerSort: true,
      resizable: true,
      minWidth: budget.minWidth ?? 60,
      maxWidth: budget.maxWidth,
      editor: false,
      tooltip: (e, cell) => String(cell.getValue() ?? ""),
    };

    const measured = measuredColumnWidth(key, col.title, data);
    let cap = budget.maxWidth ?? MAX_COLUMN_WIDTH;
    if (/title|note|reason|purpose|role/i.test(key)) cap = Math.min(cap, MAX_TEXT_WIDTH);
    if (budget.width != null) {
      col.width = budget.width;
    } else {
      col.width = Math.min(measured, cap);
    }

    if (nonEmpty.length > 0 &&
        nonEmpty.every((v) => /^-?\d+(\.\d+)?$/.test(String(v).trim()))) {
      col.sorter = "number";
      col.sorterParams = { alignEmptyValues: "bottom" };
    }

    if (key === "year" || key === "year_month" || key === "proposed_year") {
      col.formatter = (cell) => {
        const value = String(cell.getValue() ?? "");
        const display = value === "198X" ? "c. 1980s" : value;
        return renderHighlightedText(display, activeSearchQuery);
      };
      col.sorter = "string";
      col.sorterParams = { alignEmptyValues: "bottom" };
    }

    if ((preset.frozen || []).includes(key)) {
      col.frozen = true;
    }
    if (STATUS_FIELDS.has(key)) {
      col.formatter = statusFormatter;
    }
    if (key === "proposed_filename") {
      col.formatter = (cell) => {
        const value = String(cell.getValue() ?? "");
        if (!value) return "";
        const match = value.match(/^(.*?)(\.[A-Za-z0-9]+)$/);
        if (!match) return renderHighlightedText(value, activeSearchQuery);
        const frag = document.createDocumentFragment();
        frag.append(renderHighlightedText(match[1], activeSearchQuery));
        const ext = document.createElement("span");
        ext.className = "ext";
        ext.textContent = match[2];
        frag.append(ext);
        return frag;
      };
    } else if (key === "edition") {
      col.formatter = (cell) => {
        const value = String(cell.getValue() ?? "");
        if (!value) return "";
        const row = cell.getRow().getData();
        const carrier = (row.format || value.split(" · ")[0] || "").trim();
        const dotClass = ["DVD", "CD", "audiobook", "streaming", "book"].includes(carrier)
          ? `dot-${carrier}`
          : "";
        const frag = document.createDocumentFragment();
        if (dotClass) {
          const dot = document.createElement("span");
          dot.className = `carrier-dot ${dotClass}`;
          dot.title = carrier;
          frag.append(dot);
        }
        frag.append(renderHighlightedText(value, activeSearchQuery));
        const isExtraEdition = isExtraEditionRow(row);
        if (isExtraEdition) {
          const badge = document.createElement("span");
          badge.className = "extra-edition-badge";
          badge.textContent = "Extra";
          badge.title = "Extra edition of this work (same work, different carrier or printing) — see Edition Note for distinction";
          frag.append(document.createTextNode(" "));
          frag.append(badge);
        }
        return frag;
      };
    } else if (FORMAT_FIELDS.has(key)) {
      col.formatter = (cell) => {
        const value = String(cell.getValue() ?? "");
        if (!value) return "";
        const badge = document.createElement("span");
        badge.className = `status-badge ${formatClass(value)}`;
        badge.replaceChildren(renderHighlightedText(value, activeSearchQuery));
        badge.title = value;
        return badge;
      };
    }
    if (urlRatio >= 0.6 && !STATUS_FIELDS.has(key)) {
      col.formatter = urlFormatter;
    }
    if (!col.formatter && !STATUS_FIELDS.has(key)) {
      col.formatter = (cell) => {
        const val = cell.getValue();
        if (val === null || val === undefined || val === "") return "";
        return renderHighlightedText(val, activeSearchQuery);
      };
    }
    if (hiddenByDefault.has(key)) {
      col.visible = false;
    }
    return col;
  });
}
