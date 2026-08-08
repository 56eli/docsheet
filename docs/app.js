/* ==========================================================================
   Live Spreadsheet — app.js
   Loads the per-view sheet JSON files and renders them as
   interactive Tabulator table: sortable headers, global live search,
   all rows in a scrollable view, CSV export, column resizing,
   horizontal overflow for every column, dark mode with localStorage
   persistence. Editing is intentionally disabled (editor: false):
   generated catalogue data is corrected in the declared CSV review
   inputs and republished, never patched session-locally in the UI.
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
  const spreadsheet = $("spreadsheet");
  const emptyState = $("empty-state");
  const statsStrip = $("stats-strip");
  const reviewToolbar = $("review-toolbar");
  const reviewFilter = $("review-filter");
  const reviewFilterHint = $("review-filter-hint");
  const viewTitle = $("view-title");
  const viewDescription = $("view-description");
  const viewMeta = $("view-meta");
  const columnMenuBtn = $("column-menu-btn");
  const columnMenu = $("column-menu");
  const expertToggleBtn = $("expert-toggle-btn");
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
    newWorkReview: { file: "new-work-review.json", label: "New Work Review", exportName: "hawkins-new-work-review.csv" },
    veritasMappingDecisions: { file: "veritas-mapping-decisions.json", label: "Veritas Decisions", exportName: "hawkins-veritas-decisions.csv" },
    productRelationships: { file: "product-relationships.json", label: "Product Relationships", exportName: "hawkins-product-relationships.csv" },
    seriesCompilations: { file: "series-compilations.json", label: "Series Compilations", exportName: "hawkins-series-compilations.csv" },
    internationalProducts: { file: "international-products.json", label: "International Editions", exportName: "hawkins-international-products.csv" },
    publishers: { file: "publishers.json", label: "Approved Publishers", exportName: "hawkins-approved-publishers.csv" },
    original: { file: "data.json", label: "Original Spreadsheet", exportName: "hawkins-original-spreadsheet.csv" },
  };

  // Standing intake lanes show a friendly explanation instead of an empty
  // grid (2026-08-08 IA redesign, Phase 1).
  const EMPTY_STATE_MESSAGES = {
    officialDiscovery:
      "Standing intake lane — every queued item has been ruled out or promoted. " +
      "If a Veritas catalogue refresh surfaces unmatched products, they will land here for review.",
    newWorkReview:
      "Standing intake lane — no unmatched Veritas products are awaiting a new-work ruling right now.",
  };
  const DEFAULT_EMPTY_MESSAGE = "No rows in this view.";

  const VIEW_DETAILS = {    master: {
      type: "Complete curated catalogue",
      description: "The full curated catalogue of David R. Hawkins works — one row per edition, grouped by work. Product facts come first: title, series, type, edition, date, official store and streaming links, notes. Technical columns (Master ID, Work, proposed file names, provenance) stay hidden until you switch on Expert columns next to the Columns menu; clicking any row still shows every stored field. Candidate rows, when present, are marked by the Record Type badge and are not master records.",
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
    newWorkReview: {
      type: "Review queue",
      description: "Official Veritas products with no master match (Satsang monthlies, Unity Church CDs, unique audio programs) awaiting a new-work ruling.",
    },
    veritasMappingDecisions: {
      type: "Refresh decisions",
      description: "Approved Veritas product-ID dispositions reapplied after every live catalogue refresh.",
    },
    productRelationships: {
      type: "Relationship evidence",
      description: "Reviewed item-to-product assertions kept separate from master identity and source inventory.",
    },
    seriesCompilations: {
      type: "Series evidence",
      description: "Compilation links to annual lecture series where evidence supports a series/month scope rather than individual DVD parts.",
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
    record_type: "Record Type",
    uuid: "Master ID",
    work_id: "Work",
    edition: "Edition",
    master_uuid: "Master ID",
    year_month: "Year-Month",
    year_source: "Year Source",
    item_type: "Item Type",
    series: "Series",
    owned: "Owned",
    source_url_veritas: "Veritas (Official Store)",
    source_url_hay_house: "Hay House",
    source_url_nightingale_conant: "Nightingale-Conant",
    source_url_audible: "Audible",
    source_url_amazon: "Amazon",
    reference_url_1: "Streaming",
    legacy_title: "Original Spreadsheet Title",
    raw_row_number: "Raw Row",
    catalog_code: "Catalogue Code",
    legacy_tempid: "Legacy ID",
    proposed_filename: "Proposed File Name",
    proposed_filename_display: "Proposed File Name Display",
    proposed_item_type: "Proposed Item Type",
    proposed_format: "Proposed Format",
    proposed_format_detail: "Proposed Format Detail",
    proposed_owned: "Proposed Owned",
    proposed_year: "Proposed Year",
    proposed_title: "Proposed Title",
    matched_master_uuids: "Matched Master IDs",
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
    "record_type", "review_status", "promotion_status", "mapping_status", "match_status",
    "disposition", "approval", "owned", "proposed_owned", "relationship_type",
  ]);
  const FORMAT_FIELDS = new Set(["format"]);
  const REVIEW_FILTER_FIELDS = [
    "record_type", "promotion_status", "review_status", "disposition", "approval",
    "mapping_status", "match_status", "relationship_type",
  ];
  // Human-readable Everything-view provenance labels. Curated master records and
  // official candidates share the sheet, so the difference must be explicit.
  const RECORD_TYPE_LABELS = {
    master: "Curated master",
    candidate_discovery: "Candidate · discovery",
    candidate_veritas: "Candidate · Veritas",
    candidate_hayhouse: "Candidate · Hay House",
    candidate_audible: "Candidate · Audible",
    candidate_pending_promotion: "Candidate · pending promotion",
  };
  const DEFAULT_PRIORITY_FIELDS = [
    "record_type",
    "title", "proposed_filename", "candidate_title", "official_title", "review_sheet", "publisher",
    "relationship_id", "raw_row_number", "disposition", "review_status",
    "mapping_status", "promotion_status", "match_status", "item_type", "series",
    "year", "year_source", "format", "owned", "source_name", "official_product_url",
    "evidence_url", "review_notes", "notes",
  ];
  const LOW_PRIORITY_FIELDS = [
    "uuid", "work_id", "master_uuid", "matched_master_uuids", "raw_uuid", "catalog_code",
    "legacy_tempid", "raw_tempid", "source_product_id", "veritas_product_id",
    "normalized_title_match_count", "raw_unnamed_5", "raw_unnamed_8", "raw_unnamed_9",
    "raw_unnamed_10", "raw_unnamed_11",
  ];
  const COLUMN_PRESETS = {
    master: {
      // Visitor-first (owner directive 2026-08-07 PM): a first-time visitor sees
      // the product-relevant facts — what it is, when, which edition, where to
      // buy/listen — before any technical metadata comes into view.
      priority: ["record_type", "title", "series", "item_type", "edition", "year_month", "catalog_code", "owned", "source_url_veritas", "source_url_hay_house", "source_url_audible", "source_url_amazon", "source_url_nightingale_conant", "reference_url_1", "notes"],
      frozen: ["record_type", "title"],
      // Expert columns: internal IDs, file-naming proposes, and provenance
      // fields. Hidden by default so the catalogue opens on product info;
      // the "Expert columns" toggle (or the Columns menu) reveals them.
      hidden: ["uuid", "work_id", "legacy_tempid", "proposed_filename", "proposed_filename_display", "year_source", "raw_row_number", "legacy_title"],
      // Owner-directed 2026-08-04: park the Work grouping column right after
      // Legacy ID (the empty Location placeholders it used to precede were
      // dropped from the schema by owner ruling 2026-08-07).
      // Owner-directed 2026-08-04 v2: proposed_filename between Title and Item Type.
      moveAfter: { work_id: "legacy_tempid" },
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
    newWorkReview: { priority: ["candidate_title", "item_type", "series", "year", "format", "source_product_id", "match_status", "approval", "source_url_veritas", "match_notes", "review_notes"], frozen: ["candidate_title"] },
    veritasMappingDecisions: { priority: ["veritas_product_id", "mapping_status", "matched_master_uuids", "matched_master_titles", "review_status", "decision_reason"], frozen: ["veritas_product_id"] },
    productRelationships: { priority: ["master_uuid", "master_title", "relationship_type", "review_status", "official_product_title", "evidence_note", "source_name", "reviewed_on"], frozen: ["master_uuid", "master_title"] },
    seriesCompilations: { priority: ["official_product_title", "target_series", "target_year", "relationship_type", "included_lecture_count", "review_status", "target_lecture_titles"], frozen: ["official_product_title"] },
    internationalProducts: { priority: ["candidate_title", "publisher", "market", "language", "item_type", "match_status", "source_url", "review_notes"], frozen: ["candidate_title"] },
    publishers: { priority: ["publisher", "status", "role", "official_catalogue_url"], frozen: ["publisher"] },
  };

  let table = null;
  let allData = [];
  let activeView = "master";
  let activeSearchQuery = "";
  let activeReviewFilter = null;

  /* ------------------------------------------------------------------ *
   *  Expert columns (per-view, persisted): views whose preset declares a
   *  `hidden` list open in reader mode — product facts first, technical
   *  metadata (Master ID, Work, file-name proposes, provenance) hidden.
   *  The "Expert columns" toggle reveals/hides that list; the Columns menu
   *  can still show any single column, and the row-details drawer always
   *  shows every stored field.
   * ------------------------------------------------------------------ */
  const EXPERT_STORAGE_KEY = "docsheet-expert-columns";

  function readExpertState() {
    try {
      const parsed = JSON.parse(localStorage.getItem(EXPERT_STORAGE_KEY) || "{}");
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (err) {
      return {};
    }
  }

  function expertColumnsOn(viewName) {
    return Boolean(readExpertState()[viewName]);
  }

  function setExpertColumns(viewName, on) {
    const state = readExpertState();
    state[viewName] = on;
    try {
      localStorage.setItem(EXPERT_STORAGE_KEY, JSON.stringify(state));
    } catch (err) {
      /* storage unavailable (private mode) — toggle just won't persist */
    }
  }

  function expertHiddenFields(viewName) {
    const preset = COLUMN_PRESETS[viewName];
    return (preset && preset.hidden) || [];
  }

  function configureExpertToggle(viewName) {
    if (!expertToggleBtn) return;
    const hasHidden = expertHiddenFields(viewName).length > 0;
    expertToggleBtn.hidden = !hasHidden;
    if (!hasHidden) return;
    expertToggleBtn.setAttribute("aria-pressed", String(expertColumnsOn(viewName)));
  }

  function applyExpertVisibility() {
    if (!table) return;
    const on = expertColumnsOn(activeView);
    const present = new Set(table.getColumns().map((column) => column.getField()));
    expertHiddenFields(activeView).filter((field) => present.has(field)).forEach((field) => {
      const column = table.getColumn(field);
      if (on) {
        column.show();
      } else {
        column.hide();
      }
    });
    fitTableToContainer();
  }

  function toggleExpertColumns() {
    const on = !expertColumnsOn(activeView);
    setExpertColumns(activeView, on);
    applyExpertVisibility();
    configureExpertToggle(activeView);
    configureColumnChooser();
  }

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
      chips.push([
        humanizeField(activeReviewFilter.field),
        statusLabel(activeReviewFilter.field, activeReviewFilter.value),
      ]);
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
    // Showing everything is the expert superset: keep the toggle state
    // consistent so a later toggle-off restores the reader view.
    if (expertHiddenFields(activeView).length > 0) {
      setExpertColumns(activeView, true);
      configureExpertToggle(activeView);
    }
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
      anchor.setAttribute("aria-label", `${anchor.textContent} (opens in new tab)`);
      return anchor;
    }
    if (STATUS_FIELDS.has(field)) {
      const badge = document.createElement("span");
      badge.className = `status-badge ${statusClass(text)}`;
      badge.textContent = statusLabel(field, text);
      badge.title = text;
      return badge;
    }
    return document.createTextNode(text);
  }

  function openRowDetails(data) {
    rowDetailsTitle.textContent = rowTitle(data);
    rowDetailsBody.replaceChildren();
    Object.entries(data).forEach(([field, value]) => {
      // Year/Month are shown merged as "Year-Month" (see loadData).
      if ("year_month" in data && (field === "year" || field === "month")) return;
      // Format/Format Detail are shown merged as "Edition" (see loadData).
      if ("edition" in data && (field === "format" || field === "format_detail")) return;
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
   *  Data loading
   * ------------------------------------------------------------------ */
  async function loadData(viewName) {
    const view = VIEWS[viewName];
    const res = await fetch(view.file, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allData = await res.json();

    // Merge separate Year/Month fields into one "Year-Month" display column
    // ("YYYY-MM"). Applies to any view whose rows carry both fields (today:
    // Everything). The raw year/month keys stay on each row object for the
    // global search, but buildColumns, the row drawer, and CSV exports show
    // only the merged column.
    allData.forEach((row) => {
      if ("year" in row && "month" in row) {
        row.year_month = row.year ? (row.month ? `${row.year}-${row.month}` : row.year) : "";
      }
      // Merge Format + Format Detail into one "Edition" display column
      // (e.g. "audio · Audiobook", "DVD · CD & DVD set"). Only curated rows
      // carry format_detail, so the raw Original Spreadsheet view keeps its
      // verbatim format column. The raw keys stay on each row object for the
      // global search, but buildColumns, the row drawer, and CSV exports
      // show only the merged column.
      if ("format" in row && "format_detail" in row) {
        const fmt = row.format || "";
        const detail = row.format_detail || "";
        row.edition = fmt ? (detail && detail !== fmt ? `${fmt} · ${detail}` : fmt) : detail;
      }
    });

    const lastModified = res.headers.get("Last-Modified");
    footerUpdated.replaceChildren();
    if (lastModified) {
      const stamp = document.createElement("span");
      stamp.className = "updated";
      stamp.textContent = formatTimestamp(lastModified);
      footerUpdated.append("Last Updated: ", stamp);
    } else {
      footerUpdated.textContent = "Last Updated: Unknown";
    }
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
    anchor.setAttribute("aria-label", `${anchor.textContent} (opens in new tab)`);
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
    // Everything-view provenance: curated master vs. unpromoted candidate.
    if (normalized === "master") return "status-master";
    if (normalized.startsWith("candidate_")) return "status-candidate";
    if (/(excluded|rejected)/.test(normalized)) return "status-excluded";
    if (/(pending|needs|unmatched|not.promoted|unique_item|compilation_or_new_edition|^false$)/.test(normalized)) return "status-pending";
    if (/(approved|reviewed|matched|^item$|^true$)/.test(normalized)) return "status-approved";
    return "status-neutral";
  }

  function formatClass(value) {
    const normalized = String(value ?? "").toLowerCase().trim();
    if (normalized === "dvd") return "status-approved";
    if (normalized === "cd") return "status-approved";
    if (normalized === "streaming") return "status-pending";
    if (normalized === "audio") return "status-neutral";
    if (normalized === "book") return "status-master";
    return "status-neutral";
  }

  function statusLabel(field, value) {
    if (field === "record_type" && RECORD_TYPE_LABELS[value]) {
      return RECORD_TYPE_LABELS[value];
    }
    // Owned vocabulary: true = owned, false = explicitly not owned, empty =
    // not stated (minted editions/programs without a raw ownership marker).
    if ((field === "owned" || field === "proposed_owned") &&
        (value === "true" || value === "false")) {
      return value === "true" ? "Owned" : "Not owned";
    }
    return value.replace(/_/g, " ");
  }

  function statusFormatter(cell) {
    const value = String(cell.getValue() ?? "");
    if (!value) return "";
    const badge = document.createElement("span");
    badge.className = `status-badge ${statusClass(value)}`;
    badge.textContent = statusLabel(cell.getColumn().getField(), value);
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

  /* ------------------------------------------------------------------ *
   *  Column width engine — every column is sized to its widest rendered
   *  entry. Widths are measured in real pixels with an offscreen canvas
   *  (never character counts), across ALL rows (not a sample), and what
   *  gets measured is what gets rendered: URL columns measure their link
   *  label (e.g. "Veritas product"), badge columns measure the humanized
   *  badge text, and the header title (with sort indicator) is included.
   *  Earlier char-count heuristics truncated real content and oversized
   *  URL columns; measuring rendered text is what finally fits.
   * ------------------------------------------------------------------ */
  const measureContext = document.createElement("canvas").getContext("2d");
  const CELL_FONT = '14px Roboto, "Segoe UI", Arial, sans-serif';
  const BADGE_FONT = '500 11px Roboto, "Segoe UI", Arial, sans-serif';
  const HEADER_FONT = '500 14px Roboto, "Segoe UI", Arial, sans-serif';
  const CELL_PADDING = 24;   // left/right cell padding + breathing room
  const BADGE_PADDING = 18;  // badge inner padding
  const HEADER_EXTRA = 26;   // header padding + sort-indicator reserve
  const MAX_TEXT_WIDTH = 560;      // guardrail for title/note-style columns
  const MAX_COLUMN_WIDTH = 720;    // absolute guardrail for anything else

  function measureText(text, font) {
    measureContext.font = font;
    return measureContext.measureText(text).width;
  }

  function renderedValueForWidth(key, value) {
    const raw = String(value ?? "").trim();
    if (!raw) return "";
    if (looksLikeUrl(raw)) return urlLabelFor(key, raw);
    if (STATUS_FIELDS.has(key)) return statusLabel(key, raw);
    return raw;
  }

  function measuredColumnWidth(key, headerTitle, rows) {
    const isBadge = STATUS_FIELDS.has(key) || FORMAT_FIELDS.has(key);
    const font = isBadge ? BADGE_FONT : CELL_FONT;
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

  function buildColumns(data) {
    if (!Array.isArray(data) || data.length === 0) return [];

    let keys = orderKeysForView(Object.keys(data[0]), activeView);
    // Hide the raw Year/Month columns when the merged "Year-Month" column is
    // present (see loadData).
    if (keys.includes("year_month")) {
      keys = keys.filter((key) => key !== "year" && key !== "month");
    }
    // Hide the raw Format columns when the merged "Edition" column is present.
    if (keys.includes("edition")) {
      keys = keys.filter((key) => key !== "format" && key !== "format_detail");
    }
    const preset = columnPresetFor(activeView);
    // Expert columns (preset.hidden) stay out of the first-sight view unless
    // the user has switched them on for this view (persisted per view).
    const hiddenByDefault = new Set(expertColumnsOn(activeView) ? [] : (preset.hidden || []));

    return keys.map((key) => {
      const nonEmpty = data.map((r) => r[key]).filter((v) => v !== null && v !== undefined && v !== "");
      const urlRatio = nonEmpty.length
        ? nonEmpty.filter(looksLikeUrl).length / nonEmpty.length
        : 0;

      const col = {
        title: humanizeField(key),
        field: key,
        headerSort: true,          // click header to sort asc/desc
        resizable: true,           // drag column edge to resize
        minWidth: 60,              // narrow floor; the measured width fits anyway
        // Pages publishes generated catalogue/review data. Edits must occur in
        // the declared CSV review inputs, never as misleading session-only UI edits.
        editor: false,
        tooltip: (e, cell) => String(cell.getValue() ?? ""),
      };

      // Size the column to its widest rendered entry (see width engine above);
      // long free-text columns are capped so one verbose note cannot dominate.
      const measured = measuredColumnWidth(key, col.title, data);
      const cap = /title|note|reason|purpose|role/i.test(key) ? MAX_TEXT_WIDTH : MAX_COLUMN_WIDTH;
      col.width = Math.min(measured, cap);

      // Numeric columns count up in numeric order, never lexically. Without an
      // explicit number sorter Tabulator guesses the sorter from the FIRST
      // row's value, and when that row is blank (official candidates sit
      // above some sheets) it fell back to a string sort — the "Master ID
      // counts 1, 10, 100, 2, 20, ..." bug. Tabulator's built-in number
      // sorter with alignEmptyValues "bottom" pins empty cells (candidate
      // rows without a Master ID) to the bottom in BOTH sort directions.
      if (nonEmpty.length > 0 &&
          nonEmpty.every((v) => /^-?\d+(\.\d+)?$/.test(String(v).trim()))) {
        col.sorter = "number";
        col.sorterParams = { alignEmptyValues: "bottom" };
      }

      // Pre-2000 Office Series lectures carry the evidence-backed decade
      // placeholder "198X" in year / year_month / proposed_year (ledger:
      // "most are believed 1982"; see README field semantics and
      // archive/RULING_PREP_YEAR_198X_OFFICE_SERIES.md). Display it as
      // "c. 1980s" while the raw value stays in the data (search, CSV export,
      // row details), and force a deterministic string sort — a number sorter
      // would turn the placeholder into NaN and place the 16 rows arbitrarily.
      if (key === "year" || key === "year_month" || key === "proposed_year") {
        col.formatter = (cell) => {
          const value = String(cell.getValue() ?? "");
          return value === "198X" ? "c. 1980s" : value;
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
      if (FORMAT_FIELDS.has(key)) {
        col.formatter = (cell) => {
          const value = String(cell.getValue() ?? "");
          if (!value) return "";
          const badge = document.createElement("span");
          badge.className = `status-badge ${formatClass(value)}`;
          badge.textContent = value;
          badge.title = value;
          return badge;
        };
      }
      // Presentation-only nicety: render URL-heavy columns as clickable links.
      // This does NOT modify the underlying data.
      if (urlRatio >= 0.6 && !STATUS_FIELDS.has(key)) {
        col.formatter = urlFormatter;
      }
      if (hiddenByDefault.has(key)) {
        col.visible = false;
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
    values.forEach((value) => reviewFilter.add(new Option(statusLabel(field, value), value)));
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
    configureExpertToggle(activeView);
    table.on("dataFiltered", updateSearchStatus);
    // The synchronous call below can run before Tabulator has processed its
    // initial data ("active" row pipeline is still empty), leaving the footer
    // stuck on "Showing: 0"; tableBuilt corrects the count once rows exist.
    table.on("tableBuilt", updateSearchStatus);
    table.on("rowClick", (event, row) => {
      if (event.target.closest && event.target.closest("a, button, input, select, textarea")) return;
      openRowDetails(row.getData());
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

  /* ------------------------------------------------------------------ *
   *  Global live search (client-side, across every column)
   * ------------------------------------------------------------------ */
  function applySearch(query) {
    activeSearchQuery = query.trim().toLowerCase();
    clearSearchBtn.hidden = !activeSearchQuery;
    applyActiveFilters();
  }

  /* ------------------------------------------------------------------ *
   *  Export CSV (whole active view — filters never shrink downloads)
   * ------------------------------------------------------------------ */
  function exportCsv() {
    if (!table) return;
    // Export the whole active sheet ("all" rows) even when a search filter
    // narrows the on-screen rows; the on-screen subset stays visible via the
    // search box, while downloads are always the complete view.
    table.download("csv", VIEWS[activeView].exportName, { delimiter: ",", bom: true }, "all");
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
      // Roving tabindex: only the active tab stays in the Tab order
      // (Phase 2 a11y, 2026-08-08).
      tab.setAttribute("tabindex", selected ? "0" : "-1");
    });

    try {
      const data = await loadData(viewName);
      updateViewSummary(viewName, data.length);
      if (data.length === 0) {
        // Standing intake lanes (and any future empty view) get an
        // explanatory card instead of a blank grid (IA redesign 2026-08-08).
        emptyState.replaceChildren(
          document.createTextNode(EMPTY_STATE_MESSAGES[viewName] || DEFAULT_EMPTY_MESSAGE),
        );
        emptyState.hidden = false;
        spreadsheet.hidden = true;
        spreadsheet.setAttribute("aria-busy", "false");
        searchStatus.textContent = "Showing: 0";
        return;
      }
      emptyState.hidden = true;
      spreadsheet.hidden = false;
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

  async function loadStatsStrip() {
    // Catalogue overview chips, read from the generated catalogue-meta.json
    // (single source of truth — never hand-counted here).
    try {
      const res = await fetch("catalogue-meta.json", { cache: "no-store" });
      if (!res.ok) return;
      const meta = await res.json();
      const chips = [
        ["stat-master-items", meta.master_items],
        ["stat-exclusions", meta.master_exclusion_rows],
        ["stat-overrides", meta.approved_source_overrides],
        ["stat-relationships", meta.reviewed_product_relationships],
        ["stat-compilations", meta.reviewed_series_compilations],
      ];
      for (const [id, value] of chips) {
        const el = document.getElementById(id);
        if (el && Number.isFinite(value)) el.textContent = String(value);
      }
      statsStrip.hidden = false;
    } catch (err) {
      /* meta unavailable — the strip simply stays hidden */
    }
  }

  async function boot() {
    initDarkMode();
    loadStatsStrip();
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
    if (expertToggleBtn) {
      expertToggleBtn.addEventListener("click", toggleExpertColumns);
    }
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
    // Arrow-key roving navigation across the grouped tab bar (Phase 2 a11y).
    const tabsNav = document.querySelector(".dataset-tabs");
    if (tabsNav) {
      tabsNav.addEventListener("keydown", (e) => {
        const list = [...document.querySelectorAll(".dataset-tab")];
        if (list.length === 0) return;
        const current = list.findIndex((tab) => tab.dataset.view === activeView);
        let target = -1;
        if (e.key === "ArrowRight") target = (current + 1) % list.length;
        else if (e.key === "ArrowLeft") target = (current - 1 + list.length) % list.length;
        else if (e.key === "Home") target = 0;
        else if (e.key === "End") target = list.length - 1;
        else return;
        e.preventDefault();
        const tab = list[target];
        tab.focus();
        activateView(tab.dataset.view);
      });
    }
    await activateView(activeView);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
