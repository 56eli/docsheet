// =============================================================================
// docs/js/view-utils.js — View configuration, summary, and catalogue overview
// helpers. DOM-dependent but self-contained. Imported by app.js.
// =============================================================================

import { VIEWS, VIEW_DETAILS, COLUMN_LABELS, humanizeField } from "./config.js";
import { ownedValue, yearSpanFor } from "./data-utils.js";
import { overviewCard } from "./mobile.js";

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
    const metaItems = [
      ["Rows", rowCount === null ? "Loading…" : rowCount.toLocaleString()],
      ["Type", details.type || "Spreadsheet"],
      ["Export", view.exportName],
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
 * Render the catalogue collection overview cards.
 */
export function renderCollectionOverview(data, overviewCardsEl) {
  if (!overviewCardsEl) return;
  overviewCardsEl.replaceChildren();
  let ownedTrue = 0, ownedFalse = 0, ownedBlank = 0;
  data.forEach((row) => {
    const v = ownedValue(row);
    if (v === "true") ownedTrue += 1;
    else if (v === "false") ownedFalse += 1;
    else ownedBlank += 1;
  });
  const total = data.length;
  overviewCardsEl.append(overviewCard(
    "Overall collection",
    `${ownedTrue} owned · ${ownedFalse} not owned · ${ownedBlank} not stated`,
    ownedTrue,
    total,
  ));
  const bySeries = new Map();
  data.forEach((row) => {
    const series = row.series || "(unassigned)";
    if (!bySeries.has(series)) bySeries.set(series, { total: 0, owned: 0 });
    const stats = bySeries.get(series);
    stats.total += 1;
    if (ownedValue(row) === "true") stats.owned += 1;
  });
  [...bySeries.entries()]
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, 8)
    .forEach(([series, stats]) => {
      overviewCardsEl.append(overviewCard(
        series,
        `${stats.owned} of ${stats.total} owned`,
        stats.owned,
        stats.total,
      ));
    });
}

/**
 * Render the series strip chips in the catalogue overview.
 */
export function renderSeriesStrip(data, seriesStripListEl, onChipClick) {
  if (!seriesStripListEl) return;
  seriesStripListEl.replaceChildren();
  const counts = new Map();
  data.forEach((row) => {
    const series = row.series || "(unassigned)";
    counts.set(series, (counts.get(series) || 0) + 1);
  });
  [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .forEach(([series, count]) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "series-chip";
      chip.textContent = `${series} (${count})`;
      chip.setAttribute("data-series", series);
      chip.title = `Filter the catalogue to ${series}`;
      chip.addEventListener("click", () => onChipClick(series));
      seriesStripListEl.append(chip);
    });
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
