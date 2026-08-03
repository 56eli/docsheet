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
  const viewTitle = $("view-title");
  const viewDescription = $("view-description");
  const viewMeta = $("view-meta");
  const columnMenuBtn = $("column-menu-btn");
  const columnMenu = $("column-menu");
  const columnList = $("column-list");
  const showAllColumnsBtn = $("show-all-columns");
  const rowDetails = $("row-details");
  const rowDetailsTitle = $("row-details-title");
  const rowDetailsBody = $("row-details-body");
  const closeRowDetailsBtn = $("close-row-details");
  const activeFilters = $("active-filters");
  const filterChips = $("filter-chips");
  const clearAllFiltersBtn = $("clear-all-filters");

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

  const VIEW_DETAILS = {
    master: {
      type: "Catalogue + candidates",
      description: "The primary working view: curated master records plus selected official candidates that are visible for review but not necessarily promoted master items.",
    },
    reviewOverview: {
      type: "Review index",
      description: "A guide to the review sheets, their source files, row counts, and current decision state.",
    },
    manualCandidates: {
      type: "Promotion queue",
      description: "Evidence-backed official candidates that are validated but intentionally not promoted until a separate approval path exists.",
    },
    manualLeads: {
      type: "Research leads",
      description: "Manual edition, copy, or source leads that remain outside the master until reviewed.",
    },
    masterExclusions: {
      type: "Exclusion ledger",
      description: "Raw spreadsheet rows intentionally excluded from the curated master, retained with disposition and review reason.",
    },
    migrationReview: {
      type: "Migration ledger",
      description: "Raw-row provenance and proposed migration metadata used to regenerate the curated master.",
    },
    sourceOverrides: {
      type: "Approved overrides",
      description: "Reviewed official-source links applied after the original migration ledger pass without editing generated master files.",
    },
    officialDiscovery: {
      type: "Discovery queue",
      description: "Nightingale-Conant and platform candidates awaiting source, duplicate, or relationship review.",
    },
    veritasMappingDecisions: {
      type: "Refresh decisions",
      description: "Approved Veritas product-ID dispositions reapplied after every live catalogue refresh.",
    },
    veritasProducts: {
      type: "Official inventory",
      description: "Reviewed Veritas product inventory and mapping status; commercial products are not automatically master records.",
    },
    productRelationships: {
      type: "Relationship evidence",
      description: "Reviewed item-to-product assertions kept separate from master identity and source inventory.",
    },
    seriesCompilations: {
      type: "Series evidence",
      description: "Compilation links to annual lecture series where evidence supports a series/month scope rather than individual DVD parts.",
    },
    hayhouseProducts: {
      type: "Official inventory",
      description: "Hay House product listings used for source discovery and deduplication review.",
    },
    audibleProducts: {
      type: "Platform inventory",
      description: "Audible listings used for source discovery, edition review, and international leads.",
    },
    internationalProducts: {
      type: "International leads",
      description: "Non-English and market-specific products tracked separately from the current English-focused master.",
    },
    publishers: {
      type: "Source registry",
      description: "Approved publisher/platform sources and their role in the catalogue review process.",
    },
    original: {
      type: "Raw source view",
      description: "The original spreadsheet rendered unchanged; use this for provenance checks, not curated master decisions.",
    },
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
  const DEFAULT_PRIORITY_FIELDS = [
    "title", "candidate_title", "official_title", "review_sheet", "publisher",
    "relationship_id", "raw_row_number", "disposition", "review_status",
    "mapping_status", "promotion_status", "match_status", "item_type", "series",
    "year", "format", "owned", "source_name", "official_product_url",
    "evidence_url", "review_notes", "notes",
  ];
  const LOW_PRIORITY_FIELDS = [
    "uuid", "master_uuid", "matched_master_uuids", "raw_uuid", "catalog_code",
    "legacy_tempid", "raw_tempid", "source_product_id", "veritas_product_id",
    "normalized_title_match_count", "location_physical", "location_digital",
    "location_streaming", "raw_unnamed_5", "raw_unnamed_8", "raw_unnamed_9",
    "raw_unnamed_10", "raw_unnamed_11",
  ];
  const COLUMN_WIDTHS = {
    title: 300,
    raw_title: 300,
    proposed_title: 300,
    candidate_title: 300,
    official_title: 320,
    official_product_title: 320,
    matched_master_titles: 320,
    target_lecture_titles: 340,
    notes: 320,
    review_notes: 320,
    review_reason: 320,
    evidence_note: 340,
    promotion_notes: 320,
    match_notes: 320,
    purpose: 360,
    role: 300,
  };
  const COLUMN_PRESETS = {
    master: {
      priority: ["title", "item_type", "series", "year", "month", "format", "owned", "source_url_veritas", "source_url_audible", "notes"],
      frozen: ["title"],
    },
    original: {
      priority: ["title", "tempid", "WE HAVE?", "original source", "format", "product link", "other links"],
      frozen: ["title"],
    },
    reviewOverview: { priority: ["review_sheet", "record_count", "purpose", "current_state", "source_file"], frozen: ["review_sheet"] },
    manualCandidates: { priority: ["candidate_title", "proposed_item_type", "proposed_year", "proposed_format", "proposed_owned", "review_status", "promotion_status", "official_product_title", "evidence_note"], frozen: ["candidate_title"] },
    manualLeads: { priority: ["title", "proposed_item_type", "proposed_year", "proposed_owned", "lead_status", "review_reason", "provenance_note"], frozen: ["title"] },
    masterExclusions: { priority: ["raw_title", "disposition", "review_reason", "raw_row_number", "raw_tempid", "raw_we_have", "raw_product_link"], frozen: ["raw_title"] },
    migrationReview: { priority: ["proposed_title", "disposition", "review_reason", "proposed_item_type", "proposed_series", "proposed_year", "proposed_owned", "raw_row_number", "raw_title"], frozen: ["proposed_title"] },
    officialDiscovery: { priority: ["candidate_title", "item_type", "series", "year", "format", "match_status", "approval", "source_url_audible", "review_notes"], frozen: ["candidate_title"] },
    veritasProducts: { priority: ["official_title", "mapping_status", "published_date", "official_product_url", "matched_master_titles", "review_notes"], frozen: ["official_title"] },
    productRelationships: { priority: ["master_title", "relationship_type", "review_status", "official_product_title", "evidence_note", "source_name", "reviewed_on"], frozen: ["master_title"] },
    seriesCompilations: { priority: ["official_product_title", "target_series", "target_year", "relationship_type", "included_lecture_count", "review_status", "target_lecture_titles"], frozen: ["official_product_title"] },
    hayhouseProducts: { priority: ["official_title", "format", "mapping_status", "official_product_url", "review_notes"], frozen: ["official_title"] },
    audibleProducts: { priority: ["official_title", "mapping_status", "audible_url", "review_notes"], frozen: ["official_title"] },
    internationalProducts: { priority: ["candidate_title", "publisher", "market", "language", "item_type", "match_status", "source_url", "review_notes"], frozen: ["candidate_title"] },
    publishers: { priority: ["publisher", "status", "role", "official_catalogue_url"], frozen: ["publisher"] },
  };

  let table = null;
  let allData = [];
  let activeView = "master";
  let metaLoaded = false;
  let activeSearchQuery = "";
  let activeReviewFilter = null;
  const FOOTER_IDLE_NOTE = "Click a row for details; double-click a cell to edit (session only)";

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
    updateActiveFilterChips();
  }

  function updateActiveFilterChips() {
    filterChips.replaceChildren();
    const chips = [];
    if (activeSearchQuery) {
      chips.push(["Search", activeSearchQuery]);
    }
    if (activeReviewFilter) {
      chips.push([humanizeField(activeReviewFilter.field), activeReviewFilter.value.replace(/_/g, " ")]);
    }

    activeFilters.hidden = chips.length === 0;
    chips.forEach(([label, value]) => {
      const chip = document.createElement("span");
      chip.className = "filter-chip";
      chip.textContent = `${label}: ${value}`;
      filterChips.append(chip);
    });
  }

  function clearAllFilters() {
    activeSearchQuery = "";
    activeReviewFilter = null;
    searchInput.value = "";
    clearSearchBtn.hidden = true;
    reviewFilter.value = "";
    if (table) table.clearFilter();
    updateSearchStatus();
  }

  function updateViewSummary(viewName, rowCount = null) {
    const view = VIEWS[viewName];
    const details = VIEW_DETAILS[viewName] || {};
    viewTitle.textContent = view.label;
    viewDescription.textContent = details.description || "Search, filter, sort, and export this spreadsheet view.";
    viewMeta.innerHTML = "";

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
      viewMeta.append(wrapper);
    });
  }

  function closeColumnMenu() {
    columnMenu.hidden = true;
    columnMenuBtn.setAttribute("aria-expanded", "false");
  }

  function configureColumnChooser() {
    columnList.replaceChildren();
    closeColumnMenu();
    if (!table) return;

    table.getColumns().forEach((column) => {
      const field = column.getField();
      if (!field) return;
      const label = document.createElement("label");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = column.isVisible();
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
          column.show();
        } else {
          column.hide();
        }
        fitTableToContainer();
      });
      label.append(checkbox, document.createTextNode(humanizeField(field)));
      columnList.append(label);
    });
  }

  function showAllColumns() {
    if (!table) return;
    table.getColumns().forEach((column) => column.show());
    columnList.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
      checkbox.checked = true;
    });
    fitTableToContainer();
  }

  function rowTitle(data) {
    return data.title || data.candidate_title || data.official_title ||
      data.official_product_title || data.master_title || data.review_sheet ||
      data.publisher || data.relationship_id || data.raw_title || "Selected row";
  }

  function valueNode(field, value) {
    const text = String(value ?? "").trim();
    if (!text) return document.createTextNode("—");
    if (looksLikeUrl(text)) {
      const anchor = document.createElement("a");
      anchor.href = text;
      anchor.target = "_blank";
      anchor.rel = "noopener noreferrer";
      anchor.title = text;
      anchor.textContent = urlLabelFor(field, text);
      return anchor;
    }
    if (STATUS_FIELDS.has(field)) {
      const badge = document.createElement("span");
      badge.className = `status-badge ${statusClass(text)}`;
      badge.textContent = text.replace(/_/g, " ");
      return badge;
    }
    return document.createTextNode(text);
  }

  function openRowDetails(data) {
    rowDetailsTitle.textContent = rowTitle(data);
    rowDetailsBody.replaceChildren();
    Object.entries(data).forEach(([field, value]) => {
      const item = document.createElement("div");
      item.className = "row-detail-field";
      const term = document.createElement("dt");
      const description = document.createElement("dd");
      term.textContent = humanizeField(field);
      description.append(valueNode(field, value));
      item.append(term, description);
      rowDetailsBody.append(item);
    });
    rowDetails.hidden = false;
  }

  function closeRowDetails() {
    rowDetails.hidden = true;
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

  function urlLabelFor(field, value) {
    const normalizedField = field.toLowerCase();
    const sourceLabels = [
      ["veritas", "Veritas product"],
      ["hay_house", "Hay House product"],
      ["nightingale_conant", "Nightingale-Conant listing"],
      ["audible", "Audible listing"],
      ["evidence", "Evidence"],
      ["reference", "Reference"],
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

  function urlFormatter(cell) {
    const value = String(cell.getValue() ?? "").trim();
    if (!looksLikeUrl(value)) return value;
    const anchor = document.createElement("a");
    anchor.className = "url-link";
    anchor.href = value;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    anchor.title = value;
    anchor.textContent = urlLabelFor(cell.getColumn().getField(), value);
    return anchor;
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

  function columnPresetFor(viewName) {
    return COLUMN_PRESETS[viewName] || { priority: DEFAULT_PRIORITY_FIELDS, frozen: [] };
  }

  function orderKeysForView(keys, viewName) {
    const preset = columnPresetFor(viewName);
    const priority = [...new Set([...(preset.priority || []), ...DEFAULT_PRIORITY_FIELDS])]
      .filter((key) => keys.includes(key));
    const lowPriority = LOW_PRIORITY_FIELDS.filter((key) => keys.includes(key));
    const ordered = [
      ...priority,
      ...keys.filter((key) => !priority.includes(key) && !lowPriority.includes(key)),
      ...lowPriority,
    ];
    return [...new Set(ordered)];
  }

  function widthForColumn(key, urlRatio) {
    if (COLUMN_WIDTHS[key]) return COLUMN_WIDTHS[key];
    if (/title|note|reason|purpose|role/i.test(key)) return 280;
    if (urlRatio >= 0.6 || /url|link/i.test(key)) return 175;
    if (/status|disposition|approval|owned|year|month|format|count/i.test(key)) return 135;
    return null;
  }

  function buildColumns(data) {
    if (!Array.isArray(data) || data.length === 0) return [];

    const keys = orderKeysForView(Object.keys(data[0]), activeView);
    const sample = data.slice(0, 120);
    const preset = columnPresetFor(activeView);

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

      const preferredWidth = widthForColumn(key, urlRatio);
      if (preferredWidth) {
        col.width = preferredWidth;
      }
      if ((preset.frozen || []).includes(key)) {
        col.frozen = true;
      }
      if (STATUS_FIELDS.has(key)) {
        col.formatter = statusFormatter;
      }
      // Presentation-only nicety: render URL-heavy columns as clickable links.
      // This does NOT modify the underlying data.
      if (urlRatio >= 0.6 && !STATUS_FIELDS.has(key)) {
        col.formatter = urlFormatter;
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
    configureColumnChooser();
    table.on("dataFiltered", updateSearchStatus);
    table.on("rowClick", (event, row) => {
      if (event.target.closest && event.target.closest("a, button, input, select, textarea")) return;
      openRowDetails(row.getData());
    });
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
      footerNote.textContent = FOOTER_IDLE_NOTE;
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
    updateActiveFilterChips();
    closeRowDetails();
    updateViewSummary(viewName);
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
      updateViewSummary(viewName, data.length);
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
    clearAllFiltersBtn.addEventListener("click", clearAllFilters);
    exportBtn.addEventListener("click", exportCsv);
    reviewFilter.addEventListener("change", () => {
      const field = reviewFilter.dataset.field;
      activeReviewFilter = reviewFilter.value && field
        ? { field, value: reviewFilter.value }
        : null;
      applyActiveFilters();
    });
    columnMenuBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      const willOpen = columnMenu.hidden;
      columnMenu.hidden = !willOpen;
      columnMenuBtn.setAttribute("aria-expanded", String(willOpen));
    });
    columnMenu.addEventListener("click", (event) => event.stopPropagation());
    showAllColumnsBtn.addEventListener("click", showAllColumns);
    closeRowDetailsBtn.addEventListener("click", closeRowDetails);
    document.addEventListener("click", closeColumnMenu);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeColumnMenu();
        closeRowDetails();
      }
    });
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { searchInput.value = ""; applySearch(""); closeColumnMenu(); }
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
