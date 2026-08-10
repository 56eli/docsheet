// =============================================================================
// docs/js/view-utils.js — View summary, Series browser, and navigation helpers.
// DOM-dependent but self-contained. Imported by app.js.
// =============================================================================

import { VIEWS, VIEW_DETAILS, COLUMN_LABELS, humanizeField } from "./config.js?v=94f497018c49";
import { ownedValue, yearSpanFor } from "./data-utils.js?v=0288c69670bb";

/**
 * Update the view summary section (title, description, meta chips).
 */
export function updateViewSummary(viewName, rowCount, viewTitleEl, viewDescEl, viewMetaEl) {
  const view = VIEWS[viewName];
  const details = VIEW_DETAILS[viewName] || {};
  if (viewTitleEl) viewTitleEl.textContent = view.label;
  if (viewDescEl) viewDescEl.textContent = details.description || "Search, filter, sort, and export this spreadsheet view.";
  if (viewMetaEl) {
    viewMetaEl.innerHTML = "";
    // The Export formats are listed in the Export button menu (XLSX, ODS,
    // CSV, JSON, TSV); we deliberately omit a summary chip here so a partial
    // "csv / .ods" listing cannot mislead when other formats exist.
    const metaItems = [
      ["Rows", rowCount === null ? "Loading…" : rowCount.toLocaleString()],
      ["Type", details.type || "Spreadsheet"],
    ];
    metaItems.forEach(([label, value]) => {
      const wrapper = document.createElement("div");
      const term = document.createElement("dt");
      const description = document.createElement("dd");
      term.textContent = label;
      description.textContent = value;
      wrapper.append(term, description);
      viewMetaEl.append(wrapper);
    });
  }
}

/**
 * Render the Series browser landing page.
 */
export function renderSeriesLanding(data, seriesLandingEl, seriesLandingGridEl, footerStatsEl, searchStatusEl, onSeriesClick) {
  if (!seriesLandingEl || !seriesLandingGridEl) return;
  seriesLandingGridEl.replaceChildren();
  const bySeries = new Map();
  data.forEach((row) => {
    const series = row.series || "(unassigned)";
    if (!bySeries.has(series)) bySeries.set(series, []);
    bySeries.get(series).push(row);
  });
  const entries = [...bySeries.entries()].sort((a, b) => b[1].length - a[1].length);
  entries.forEach(([series, rows]) => {
    const owned = rows.filter((row) => ownedValue(row) === "true").length;
    const card = document.createElement("button");
    card.type = "button";
    card.className = "series-landing-card";
    const name = document.createElement("strong");
    name.textContent = series;
    const meta = document.createElement("span");
    meta.textContent = `${rows.length} record${rows.length === 1 ? "" : "s"} · ${owned} owned`;
    const years = document.createElement("span");
    years.className = "series-card-years";
    years.textContent = yearSpanFor(rows);
    card.append(name, meta, years);
    card.addEventListener("click", () => onSeriesClick(series));
    seriesLandingGridEl.append(card);
  });
  if (footerStatsEl) footerStatsEl.textContent = `Series: ${entries.length} series`;
  if (searchStatusEl) searchStatusEl.textContent = `${entries.length} series · ${data.length} records`;
}

/**
 * Configure the view-jump dropdown from VIEWS + VIEW_GROUPS.
 */
export function configureViewJump(viewJumpEl, VIEW_GROUPS, activeView) {
  if (!viewJumpEl) return;
  viewJumpEl.replaceChildren();
  VIEW_GROUPS.forEach((group) => {
    const optgroup = document.createElement("optgroup");
    optgroup.label = group.label;
    group.views.forEach((viewName) => {
      const option = new Option(VIEWS[viewName].label, viewName);
      optgroup.append(option);
    });
    viewJumpEl.append(optgroup);
  });
  viewJumpEl.value = activeView;
}
