/* ==========================================================================
   Live Spreadsheet — app.js
   Loads docs/data.json (+ docs/meta.json) and renders it as an
   interactive Tabulator table: sortable headers, global live search,
   all rows in a scrollable view, inline editing, CSV export, column resizing,
   horizontal overflow for every column, dark mode with localStorage persistence.
   ========================================================================== */
(function () {
  "use strict";

  const STORAGE_KEY = "docsheet-dark-mode";

  const $ = (id) => document.getElementById(id);
  const searchInput = $("global-search");
  const clearSearchBtn = $("clear-search-btn");
  const exportBtn = $("export-btn");
  const darkToggle = $("dark-toggle");
  const footerStats = $("footer-stats");
  const searchStatus = $("search-status");
  const footerUpdated = $("footer-updated");
  const footerNote = $("footer-note");
  const spreadsheet = $("spreadsheet");
  const reviewToolbar = $("review-toolbar");
  const reviewFilter = $("review-filter");
  const reviewFilterHint = $("review-filter-hint");

  const VIEWS = {
    master: { file: "master.json", label: "Everything", exportName: "hawkins-everything.csv" },
    reviewOverview: { file: "review-overview.json", label: "Review Overview", exportName: "hawkins-review-overview.csv" },
    manualCandidates: { file: "manual-candidates.json", label: "Master Candidates", exportName: "hawkins-master-candidates.csv" },
    manualLeads: { file: "manual-leads.json", label: "Manual Leads", exportName: "hawkins-manual-leads.csv" },
    masterExclusions: { file: "master-exclusions.json", label: "Master Exclusions", exportName: "hawkins-master-exclusions.csv" },
    migrationReview: { file: "migration-review.json", label: "Migration Review", exportName: "hawkins-migration-review.csv" },
    sourceOverrides: { file: "source-overrides.json", label: "Source Overrides", exportName: "hawkins-source-overrides.csv" },
    officialDiscovery: { file: "official-discovery.json", label: "Official Discovery", exportName: "hawkins-official-discovery.csv" },
    veritasMappingDecisions: { file: "veritas-mapping-decisions.json", label: "Veritas Decisions", exportName: "hawkins-veritas-decisions.csv" },
    veritasProducts: { file: "veritas-products.json", label: "Veritas Products", exportName: "hawkins-veritas-products.csv" },
    productRelationships: { file: "product-relationships.json", label: "Product Relationships", exportName: "hawkins-product-relationships.csv" },
    seriesCompilations: { file: "series-compilations.json", label: "Series Compilations", exportName: "hawkins-series-compilations.csv" },
    hayhouseProducts: { file: "hayhouse-products.json", label: "Hay House Products", exportName: "hawkins-hayhouse-products.csv" },
    audibleProducts: { file: "audible-products.json", label: "Audible Products", exportName: "hawkins-audible-products.csv" },
    internationalProducts: { file: "international-products.json", label: "International Editions", exportName: "hawkins-international-products.csv" },
    publishers: { file: "publishers.json", label: "Approved Publishers", exportName: "hawkins-approved-publishers.csv" },
    original: { file: "data.json", label: "Original Spreadsheet", exportName: "hawkins-original-spreadsheet.csv" },
  };

  const COLUMN_LABELS = {
    uuid: "Master UUID",
    raw_row_number: "Raw Row",
    catalog_code: "Catalogue Code",
    legacy_tempid: "Legacy ID",
    proposed_item_type: "Proposed Item Type",
    proposed_format: "Proposed Format",
    proposed_format_detail: "Proposed Format Detail",
    proposed_owned: "Proposed Owned",
    proposed_year: "Proposed Year",
    proposed_title: "Proposed Title",
    source_product_id: "Source Product ID",
    source_name: "Source",
    official_product_url: "Official Product URL",
    official_product_title: "Official Product Title",
    official_catalogue_url: "Official Catalogue URL",
    official_discovery_url: "Official Discovery URL",
    review_status: "Review Status",
    review_reason: "Review Reason",
    review_notes: "Review Notes",
    promotion_status: "Promotion Status",
    promotion_notes: "Promotion Notes",
    relationship_type: "Relationship Type",
    mapping_status: "Mapping Status",
    match_status: "Match Status",
    evidence_url: "Evidence URL",
    evidence_note: "Evidence Note",
    override_value: "Override Value",
    target_field: "Target Field",
  };
  const STATUS_FIELDS = new Set([
    "review_status", "promotion_status", "mapping_status", "match_status",
    "disposition", "approval", "owned", "proposed_owned", "relationship_type",
  ]);
  const REVIEW_FILTER_FIELDS = [
    "promotion_status", "review_status", "disposition", "approval", "mapping_status",
    "match_status", "relationship_type",
  ];

  let table = null;
  let allData = [];
  let activeView = "master";
  let metaLoaded = false;
  let activeSearchQuery = "";
  let activeReviewFilter = null;

  /* ------------------------------------------------------------------ *
   *  Helpers
   * ------------------------------------------------------------------ */
  function debounce(fn, ms) {
    let t;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  function formatTimestamp(iso) {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString(undefined, {
      year: "numeric", month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  }

  function updateSearchStatus() {
    if (!table) return;
    const visibleRows = table.getData("active").length;
    const isFiltering = Boolean(activeSearchQuery || activeReviewFilter);
    searchStatus.textContent = isFiltering
      ? `Showing: ${visibleRows} of ${allData.length}`
      : `Showing: ${visibleRows}`;
  }

  /* ------------------------------------------------------------------ *
   *  Data loading (meta.json first for a snappy footer)
   * ------------------------------------------------------------------ */
  async function loadMeta() {
    try {
      const res = await fetch("meta.json", { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const meta = await res.json();
      metaLoaded = true;
      footerStats.textContent = `Total Rows: ${meta.total_rows ?? "—"}`;
      footerUpdated.innerHTML =
        `Last Updated: <span class="updated">${formatTimestamp(meta.generated_at_utc)}</span>`;
      return meta;
    } catch (err) {
      console.warn("[docsheet] meta.json unavailable:", err);
      return null;
    }
  }

  async function loadData(viewName) {
    const view = VIEWS[viewName];
    const res = await fetch(view.file, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allData = await res.json();

    const lastModified = res.headers.get("Last-Modified");
    footerUpdated.innerHTML = lastModified
      ? `Last Updated: <span class="updated">${formatTimestamp(lastModified)}</span>`
      : "Last Updated: Unknown";
    footerStats.textContent = `${view.label}: ${allData.length} rows`;
    return allData;
  }

  /* ------------------------------------------------------------------ *
   *  Column definitions (built from the JSON keys — order preserved)
   * ------------------------------------------------------------------ */
  function looksLikeUrl(value) {
    return typeof value === "string" && /^https?:\/\//i.test(value.trim());
  }

  function humanizeField(key) {
    if (COLUMN_LABELS[key]) return COLUMN_LABELS[key];
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (character) => character.toUpperCase());
  }

  function statusClass(value) {
    const normalized = String(value ?? "").toLowerCase();
    if (/(excluded|rejected)/.test(normalized)) return "status-excluded";
    if (/(pending|needs|unmatched|not.promoted|unique_item|compilation_or_new_edition|^false$)/.test(normalized)) return "status-pending";
    if (/(approved|reviewed|matched|^item$|^true$)/.test(normalized)) return "status-approved";
    return "status-neutral";
  }

  function statusFormatter(cell) {
    const value = String(cell.getValue() ?? "");
    if (!value) return "";
    const badge = document.createElement("span");
    badge.className = `status-badge ${statusClass(value)}`;
    badge.textContent = value.replace(/_/g, " ");
    badge.title = value;
    return badge;
  }

  function buildColumns(data) {
    if (!Array.isArray(data) || data.length === 0) return [];

    const keys = Object.keys(data[0]);
    const sample = data.slice(0, 120);

    return keys.map((key) => {
      const nonEmpty = sample.map((r) => r[key]).filter((v) => v !== null && v !== undefined && v !== "");
      const urlRatio = nonEmpty.length
        ? nonEmpty.filter(looksLikeUrl).length / nonEmpty.length
        : 0;

      const col = {
        title: humanizeField(key),
        field: key,
        headerSort: true,          // click header to sort asc/desc
        resizable: true,           // drag column edge to resize
        minWidth: 110,
        editor: "input",           // double-click any cell to edit
        tooltip: (e, cell) => String(cell.getValue() ?? ""),
      };

      if (STATUS_FIELDS.has(key)) {
        col.formatter = statusFormatter;
      }
      // Presentation-only nicety: render URL-heavy columns as clickable links.
      // This does NOT modify the underlying data.
      if (urlRatio >= 0.6 && !STATUS_FIELDS.has(key)) {
        col.formatter = "link";
        col.formatterParams = { target: "_blank", urlPrefix: "" };
      }
      return col;
    });
  }

  function configureReviewFilter(data) {
    activeReviewFilter = null;
    reviewFilter.replaceChildren();
    reviewToolbar.hidden = true;
    reviewFilterHint.textContent = "";

    if (!Array.isArray(data) || data.length === 0) return;
    const field = REVIEW_FILTER_FIELDS.find((candidate) => {
      const values = new Set(
        data.map((row) => String(row[candidate] ?? "").trim()).filter(Boolean)
      );
      return values.size > 1;
    });
    if (!field) return;

    const values = [...new Set(
      data.map((row) => String(row[field] ?? "").trim()).filter(Boolean)
    )].sort((a, b) => a.localeCompare(b));
    const allOption = new Option(`All ${humanizeField(field)} values`, "");
    reviewFilter.add(allOption);
    values.forEach((value) => reviewFilter.add(new Option(value.replace(/_/g, " "), value)));
    reviewToolbar.hidden = false;
    reviewFilterHint.textContent = `${values.length} ${humanizeField(field).toLowerCase()} values`;
    reviewFilter.dataset.field = field;
  }

  function applyActiveFilters() {
    if (!table) return;
    if (!activeSearchQuery && !activeReviewFilter) {
      table.clearFilter();
      updateSearchStatus();
      return;
    }
    table.setFilter((data) => {
      const searchMatches = !activeSearchQuery || Object.values(data).some(
        (value) => value !== null && value !== undefined &&
          String(value).toLowerCase().includes(activeSearchQuery)
      );
      const reviewMatches = !activeReviewFilter ||
        String(data[activeReviewFilter.field] ?? "") === activeReviewFilter.value;
      return searchMatches && reviewMatches;
    });
    updateSearchStatus();
  }

  /* ------------------------------------------------------------------ *
   *  Tabulator init
   * ------------------------------------------------------------------ */
  function initTable(data) {
    spreadsheet.innerHTML = "";
    table = new Tabulator(spreadsheet, {
      data,
      columns: buildColumns(data),
      layout: "fitColumns",
      maxHeight: "100%",           // header stays frozen while rows scroll
      placeholder: "No data found",
      /* keep the table sized to its container on resize */
      renderComplete: () => fitTableToContainer(),
      /* sorting */
      headerSort: true,
      /* All records stay in one scrollable view — no pagination. */
      pagination: false,
      /* columns */
      resizableColumns: true,
      movableColumns: true,        // drag headers to reorder (bonus)
      responsiveLayout: false,     // keep every column visible; scroll horizontally when needed
      /* editing */
      editTriggerEvent: "dblclick", // double-click any cell to edit
      selectableRows: false,
    });

    configureReviewFilter(data);
    table.on("dataFiltered", updateSearchStatus);
    table.on("cellEdited", (cell) => {
      const row = cell.getRow().getData();
      const label = humanizeField(cell.getColumn().getField());
      const id = row.tempid || row.uuid || `row ${cell.getRow().getPosition(true)}`;
      flashNote(`✎ Edited “${label}” (${id}) — local only, not saved back to the CSV`);
    });
    spreadsheet.setAttribute("aria-busy", "false");
    updateSearchStatus();
  }

  /* Keep the table filling its container (frozen header + internal scroll).
     Measures the container in pixels so it works regardless of how the
     "100%" maxHeight is resolved by the browser. */
  function fitTableToContainer() {
    const container = $("spreadsheet");
    if (!container || !table) return;
    const height = Math.max(200, container.clientHeight || 0);
    // Avoid redundant re-layouts: only push a new height when it changed.
    if (height !== table._fitHeight) {
      table._fitHeight = height;
      table.setMaxHeight(height + "px");
    }
  }

  window.addEventListener("resize", debounce(fitTableToContainer, 150));

  function flashNote(message) {
    footerNote.textContent = message;
    clearTimeout(flashNote._t);
    flashNote._t = setTimeout(() => {
      footerNote.textContent = "Double-click any cell to edit (session only)";
    }, 3500);
  }

  /* ------------------------------------------------------------------ *
   *  Global live search (client-side, across every column)
   * ------------------------------------------------------------------ */
  function applySearch(query) {
    activeSearchQuery = query.trim().toLowerCase();
    clearSearchBtn.hidden = !activeSearchQuery;
    applyActiveFilters();
  }

  /* ------------------------------------------------------------------ *
   *  Export CSV (current filtered view)
   * ------------------------------------------------------------------ */
  function exportCsv() {
    if (!table) return;
    table.download("csv", VIEWS[activeView].exportName, { delimiter: ",", bom: true });
  }

  /* ------------------------------------------------------------------ *
   *  Dark mode (persisted in localStorage)
   * ------------------------------------------------------------------ */
  function setDarkMode(enabled) {
    // Class goes on <html> so the pre-paint inline script in index.html can
    // apply it before first paint (no flash of white for dark-mode users).
    document.documentElement.classList.toggle("dark", enabled);
    darkToggle.checked = enabled;
    // Swap the Tabulator stylesheet between the light and midnight themes.
    $("tabulator-light-css").disabled = enabled;
    $("tabulator-dark-css").disabled = !enabled;
    try {
      localStorage.setItem(STORAGE_KEY, enabled ? "1" : "0");
    } catch (err) {
      /* storage unavailable (private mode) — dark mode just won't persist */
    }
  }

  function initDarkMode() {
    let stored = null;
    try {
      stored = localStorage.getItem(STORAGE_KEY);
    } catch (err) { /* ignore */ }
    const prefersDark = window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDarkMode(stored !== null ? stored === "1" : prefersDark);
    darkToggle.addEventListener("change", () => setDarkMode(darkToggle.checked));
  }

  /* ------------------------------------------------------------------ *
   *  Boot
   * ------------------------------------------------------------------ */
  async function activateView(viewName) {
    activeView = viewName;
    const view = VIEWS[viewName];
    activeSearchQuery = "";
    activeReviewFilter = null;
    searchInput.value = "";
    clearSearchBtn.hidden = true;
    reviewToolbar.hidden = true;
    spreadsheet.setAttribute("aria-busy", "true");
    if (table) {
      table.destroy();
      table = null;
    }
    spreadsheet.innerHTML = `<div class="table-loading">Loading ${view.label.toLowerCase()}…</div>`;
    document.querySelectorAll(".dataset-tab").forEach((tab) => {
      const selected = tab.dataset.view === viewName;
      tab.classList.toggle("active", selected);
      tab.setAttribute("aria-selected", String(selected));
    });

    try {
      const data = await loadData(viewName);
      initTable(data);
      console.info(`[docsheet] Loaded ${data.length} ${viewName} rows`);
    } catch (err) {
      console.error(`[docsheet] Failed to load ${view.file}:`, err);
      spreadsheet.innerHTML =
        `<div class="load-error">Could not load ${view.file} — make sure the site is served over HTTP ` +
        '(e.g. GitHub Pages or `python -m http.server`), not opened directly from disk.</div>';
      spreadsheet.setAttribute("aria-busy", "false");
      footerStats.textContent = "Total Rows: —";
      searchStatus.textContent = "Showing: —";
      footerUpdated.textContent = "Last Updated: —";
    }
  }

  async function boot() {
    initDarkMode();
    searchInput.addEventListener("input", debounce((e) => applySearch(e.target.value), 250));
    clearSearchBtn.addEventListener("click", () => {
      searchInput.value = "";
      applySearch("");
      searchInput.focus();
    });
    exportBtn.addEventListener("click", exportCsv);
    reviewFilter.addEventListener("change", () => {
      const field = reviewFilter.dataset.field;
      activeReviewFilter = reviewFilter.value && field
        ? { field, value: reviewFilter.value }
        : null;
      applyActiveFilters();
    });
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { searchInput.value = ""; applySearch(""); }
    });
    document.querySelectorAll(".dataset-tab").forEach((tab) => {
      tab.addEventListener("click", () => activateView(tab.dataset.view));
    });
    await activateView(activeView);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
