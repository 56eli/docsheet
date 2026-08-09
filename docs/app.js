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
  const viewJump = $("view-jump");
  const exportBtn = $("export-btn");
  const settingsBtn = $("settings-btn");
  const settingsMenu = $("settings-menu");
  const expandEverythingBtn = $("expand-everything-btn");
  const wrapCellsToggle = $("wrap-cells-toggle");
  const compactModeToggle = $("compact-mode-toggle");
  const showSummaryToggle = $("show-summary-toggle");
  const showStatsToggle = $("show-stats-toggle");
  const showFiltersToggle = $("show-filters-toggle");
  const showBlankRowsToggle = $("show-blank-rows-toggle");
  const blankRowsToggleWrap = $("blank-rows-toggle-wrap");
  // Catalogue overview (hero / collection stats / series strip) + presentation controls
  const masterBrowseToggle = $("master-browse-toggle");
  const overviewBtn = $("overview-btn");
  const catalogueIntro = $("catalogue-intro");
  const hero = $("hero");
  const heroDismiss = $("hero-dismiss");
  const overviewCards = $("overview-cards");
  const seriesStripList = $("series-strip-list");
  const reviewNavToggle = $("review-nav-toggle");
  const reviewNavGroups = $("review-nav-groups");
  const seriesLanding = $("series-landing");
  const seriesLandingGrid = $("series-landing-grid");
  const descToggleBtn = $("desc-toggle-btn");
  const facetToggleBtn = $("facet-toggle-btn");
  const mobileViewToggle = $("mobile-view-toggle");
  const mobileBrowse = $("mobile-browse");
  const mobileBrowseList = $("mobile-browse-list");
  const mobileBrowseSheetBtn = $("mobile-browse-sheet-btn");
  const mobileSeriesShelf = $("mobile-series-shelf");
  const mobileYearRail = $("mobile-year-rail");
  const mobileDiscoveryClear = $("mobile-discovery-clear");
  const resetViewBtn = $("reset-view-btn");
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
  const viewSummary = $("view-summary");
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
  const facetBar = $("facet-bar");
  const facetSeries = $("facet-series");
  const facetYear = $("facet-year");
  const facetItemType = $("facet-item-type");
  const facetFormat = $("facet-format");
  const facetOwned = $("facet-owned");
  const facetClear = $("facet-clear");
  const copyFilenameBtn = $("copy-filename-btn");
  const copyIdBtn = $("copy-id-btn");

  const VIEWS = {
    master: { file: "master.json", label: "Everything", exportName: "hawkins-everything.csv" },
    series: { file: "master.json", label: "Series", exportName: "hawkins-series.csv" },
    reviewOverview: { file: "review-overview.json", label: "Review Overview", exportName: "hawkins-review-overview.csv" },
    manualCandidates: { file: "manual-candidates.json", label: "Candidates", exportName: "hawkins-master-candidates.csv" },
    manualLeads: { file: "manual-leads.json", label: "Manual Leads", exportName: "hawkins-manual-leads.csv" },
    masterExclusions: { file: "master-exclusions.json", label: "Exclusions", exportName: "hawkins-master-exclusions.csv" },
    migrationReview: { file: "migration-review.json", label: "Migration Review", exportName: "hawkins-migration-review.csv" },
    sourceOverrides: { file: "source-overrides.json", label: "Source Overrides", exportName: "hawkins-source-overrides.csv" },
    officialDiscovery: { file: "official-discovery.json", label: "Official Discovery", exportName: "hawkins-official-discovery.csv" },
    newWorkReview: { file: "new-work-review.json", label: "New Work Review", exportName: "hawkins-new-work-review.csv" },
    veritasMappingDecisions: { file: "veritas-mapping-decisions.json", label: "Decisions", exportName: "hawkins-veritas-decisions.csv" },
    productRelationships: { file: "product-relationships.json", label: "Product Relationships", exportName: "hawkins-product-relationships.csv" },
    seriesCompilations: { file: "series-compilations.json", label: "Compilations", exportName: "hawkins-series-compilations.csv" },
    internationalProducts: { file: "international-products.json", label: "International Editions", exportName: "hawkins-international-products.csv" },
    publishers: { file: "publishers.json", label: "Publishers", exportName: "hawkins-approved-publishers.csv" },
    veritasProducts: { file: "veritas-products.json", label: "Veritas Products", exportName: "hawkins-veritas-products.csv" },
    hayhouseProducts: { file: "hayhouse-products.json", label: "Hay House Products", exportName: "hawkins-hayhouse-products.csv" },
    audibleProducts: { file: "audible-products.json", label: "Audible Products", exportName: "hawkins-audible-products.csv" },
    filenameProposal: { file: "filename-proposal.json", label: "Filename Proposal", exportName: "hawkins-filename-proposal.csv" },
    original: { file: "data.json", label: "Original Spreadsheet", exportName: "hawkins-original-spreadsheet.csv" },
  };

  const VIEW_GROUPS = [
    { label: "Catalogue", views: ["master", "series", "productRelationships", "seriesCompilations"] },
    { label: "Review workspace", views: ["reviewOverview", "manualCandidates", "manualLeads", "masterExclusions", "sourceOverrides", "veritasMappingDecisions", "newWorkReview", "officialDiscovery", "internationalProducts"] },
    { label: "Sources", views: ["publishers", "veritasProducts", "hayhouseProducts", "audibleProducts", "filenameProposal", "migrationReview", "original"] },
  ];

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
      description: "The full curated catalogue of David R. Hawkins works — one row per edition, grouped by work. On phones it opens in Browse mode: compact work stacks with source and streaming actions; use Spreadsheet for the full grid. Product facts come first: title, series, type, edition, date, official store and streaming links, notes. Technical columns (Master ID, Work, proposed file names, provenance) stay hidden until you switch on Expert columns next to the Columns menu; clicking any row still shows every stored field. Candidate rows, when present, are marked by the Record Type badge and are not master records.",
    },
    series: {
      type: "Series browser",
      description: "Every curated series as a card: record count, ownership, and year span. Pick a series to open the Everything view filtered to it.",
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
    veritasProducts: {
      type: "Official inventory",
      description: "Reviewed Veritas Publishing product inventory with product IDs, official categories, mapping status, and matched master records.",
    },
    hayhouseProducts: {
      type: "Official inventory",
      description: "Reviewed Hay House product inventory used for book and audio-edition source matching.",
    },
    audibleProducts: {
      type: "Platform inventory",
      description: "Reviewed Audible catalogue entries and their current mapping notes, including international editions routed out of the English master.",
    },
    filenameProposal: {
      type: "Filename review",
      description: "Reviewed proposed output filenames with master metadata mirrors and display-safe part labels.",
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
  // Record-type badges are intentionally compact (owner directive 2026-08-08):
  // curated master rows read "CM" to keep the first column narrow. The full
  // phrase stays in the badge's `title` tooltip (see statusFormatter) and in
  // the column header / filter chips. Candidate lanes are empty today but
  // their labels stay descriptive for when a refresh surfaces new products.
  const RECORD_TYPE_LABELS = {
    master: "CM",
    candidate_discovery: "Candidate · discovery",
    candidate_veritas: "Candidate · Veritas",
    candidate_hayhouse: "Candidate · Hay House",
    candidate_audible: "Candidate · Audible",
    candidate_pending_promotion: "Candidate · pending promotion",
  };
  const RECORD_TYPE_TITLES = {
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
  // Width budgets are a presentation contract: content columns may use the
  // measured-width engine, but compact controls and the frozen identity rail
  // must never grow just because a label is long.
  const COLUMN_BUDGETS = {
    record_type: { width: 54, minWidth: 54, maxWidth: 54 },
    proposed_filename: { maxWidth: 340 },
    title: { minWidth: 150, maxWidth: 560 },
    series: { minWidth: 180 },
    notes: { maxWidth: 560 },
  };

  const COLUMN_PRESETS = {
    master: {
      // Visitor-first (owner directive 2026-08-07 PM; refined 2026-08-08): a
      // first-time visitor sees the proposed output file name (the most
      // important column) immediately after the Record Type badge, then the
      // product facts — title, series, type, edition, date, where to buy/
      // listen — before any technical metadata comes into view.
      priority: ["record_type", "proposed_filename", "title", "series", "item_type", "edition", "year_month", "catalog_code", "owned", "source_url_veritas", "source_url_hay_house", "source_url_audible", "source_url_amazon", "source_url_nightingale_conant", "reference_url_1", "notes"],
      frozen: ["record_type", "proposed_filename", "title"],
      // Expert columns: internal IDs and provenance fields. Hidden by default
      // so the catalogue opens on the file name + product info; the "Expert
      // columns" toggle (or the Columns menu) reveals them. proposed_filename
      // is intentionally NOT here anymore — it is visible by default (owner
      // directive 2026-08-08).
      hidden: ["uuid", "work_id", "legacy_tempid", "proposed_filename_display", "year_source", "raw_row_number", "legacy_title"],
      // Owner-directed 2026-08-04: park the Work grouping column right after
      // Legacy ID (the empty Location placeholders it used to precede were
      // dropped from the schema by owner ruling 2026-08-07).
      // Owner-directed 2026-08-04 v2: proposed_filename between Title and Item Type.
      moveAfter: { work_id: "legacy_tempid" },
    },
    original: {
      priority: ["title", "tempid", "WE HAVE?", "original source", "notes", "format", "product link"],
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
    veritasProducts: { priority: ["veritas_product_id", "official_title", "mapping_status", "matched_master_uuids", "matched_master_titles", "published_date", "official_product_url", "official_categories", "review_notes"], frozen: ["veritas_product_id", "official_title"] },
    hayhouseProducts: { priority: ["official_title", "format", "mapping_status", "official_product_url", "review_notes"], frozen: ["official_title"] },
    audibleProducts: { priority: ["official_title", "mapping_status", "audible_url", "review_notes"], frozen: ["official_title"] },
    filenameProposal: { priority: ["uuid", "title", "proposed_filename_display", "proposed_filename", "work_id", "item_type", "series", "year", "month", "format", "part_index", "part_total"], frozen: ["uuid", "title"] },
  };

  let table = null;
  let allData = [];
  let activeView = "master";
  let activeSearchQuery = "";
  let activeReviewFilter = null;
  // Faceted (multi-select) filters for the catalogue view. Each maps a field
  // to a Set of selected raw values. Persisted per view in localStorage.
  let activeFacets = {};
  let mobileBrowseRows = [];
  let renderedAsMobileBrowse = false;
  let viewActivation = 0;
  let activeDataRequest = null;
  const MOBILE_BROWSE_STORAGE_KEY = "docsheet-mobile-master-mode";
  const MASTER_PRESENTATION_KEY = "docsheet-master-presentation";
  const INTRO_STORAGE_KEY = "docsheet-intro-dismissed";
  const REVIEW_NAV_KEY = "docsheet-review-nav-collapsed";
  const mobileBrowseMedia = window.matchMedia
    ? window.matchMedia("(max-width: 720px)")
    : { matches: false };

  /* ------------------------------------------------------------------ *
   *  Per-view UI state persistence (sort, scroll, column widths) on top
   *  of the existing view-settings/expert persistence. Lets a reviewer
   *  return to a tab without losing their place.
   * ------------------------------------------------------------------ */
  const GRID_STATE_KEY = "docsheet-grid-state";

  function readGridState() {
    try {
      const parsed = JSON.parse(localStorage.getItem(GRID_STATE_KEY) || "{}");
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (err) {
      return {};
    }
  }

  function writeGridState(viewName, patch) {
    const state = readGridState();
    state[viewName] = { ...(state[viewName] || {}), ...patch };
    try {
      localStorage.setItem(GRID_STATE_KEY, JSON.stringify(state));
    } catch (err) {
      /* storage unavailable — ignore */
    }
  }

  function FACET_STORAGE_KEY(viewName) {
    return `docsheet-facets-${viewName}`;
  }

  function readFacetState(viewName) {
    try {
      const parsed = JSON.parse(localStorage.getItem(FACET_STORAGE_KEY(viewName)) || "{}");
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (err) {
      return {};
    }
  }

  function writeFacetState(viewName, state) {
    try {
      localStorage.setItem(FACET_STORAGE_KEY(viewName), JSON.stringify(state));
    } catch (err) {
      /* storage unavailable */
    }
  }

  // Facet configuration: which Everything-view fields become faceted filters.
  // `buildOptionLabel` lets us map raw values (e.g. "" for not-owned) to a
  // human-readable option; `matchValue` extracts the comparable value(s).
  const FACETS = [
    { id: "series", el: () => facetSeries, field: "series" },
    {
      id: "year",
      el: () => facetYear,
      field: "year",
      // 198X renders as "c. 1980s" but is filtered by its raw value.
      buildOptionLabel: (value) => (value === "198X" ? "c. 1980s (198X)" : value),
      sort: (a, b) => {
        const na = parseInt(a, 10);
        const nb = parseInt(b, 10);
        if (Number.isFinite(na) && Number.isFinite(nb)) return na - nb;
        return a.localeCompare(b);
      },
    },
    { id: "itemType", el: () => facetItemType, field: "item_type", label: humanizeField.bind(null, "item_type") },
    { id: "format", el: () => facetFormat, field: "format" },
    {
      id: "owned",
      el: () => facetOwned,
      field: "owned",
      buildOptionLabel: (value) => { const v = String(value ?? "").toLowerCase(); return v === "true" ? "Owned" : v === "false" ? "Not owned" : "Not stated"; },
    },
  ];

  function populateFacets(data) {
    if (!facetBar) return;
    activeFacets = readFacetState(activeView);
    FACETS.forEach((facet) => {
      const select = facet.el();
      if (!select) return;
      const counts = new Map();
      data.forEach((row) => {
        const value = String(row[facet.field] ?? "").trim();
        counts.set(value, (counts.get(value) || 0) + 1);
      });
      let values = [...counts.keys()];
      if (facet.sort) values.sort(facet.sort);
      else values.sort((a, b) => a.localeCompare(b));
      // Keep the blank ("not stated"/"unknown") option last.
      values = values.filter((v) => v !== "").concat(values.includes("") ? [""] : []);
      const selected = new Set(activeFacets[facet.id] || []);
      select.replaceChildren();
      values.forEach((value) => {
        const count = counts.get(value);
        const label = facet.buildOptionLabel ? facet.buildOptionLabel(value) : value || "(blank)";
        const option = document.createElement("option");
        option.value = value;
        option.textContent = `${label} (${count})`;
        option.selected = selected.has(value);
        select.add(option);
      });
      select.size = Math.min(6, Math.max(3, values.length));
    });
    facetClear.hidden = Object.values(activeFacets).every((list) => !list || list.length === 0);
  }

  function clearFacets() {
    activeFacets = {};
    writeFacetState(activeView, {});
    FACETS.forEach((facet) => {
      const select = facet.el();
      if (select) [...select.options].forEach((option) => { option.selected = false; });
    });
    if (facetClear) facetClear.hidden = true;
    applyActiveFilters();
  }

  function rowMatchesFacets(row) {
    return FACETS.every((facet) => {
      const selected = activeFacets[facet.id];
      if (!selected || selected.length === 0) return true;
      const value = String(row[facet.field] ?? "").trim();
      return selected.includes(value);
    });
  }

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
   *  Minimal display settings: compact vs. expanded rows, wrapped text,
   *  summary visibility, and one-click "Expand everything".
   * ------------------------------------------------------------------ */
  const VIEW_SETTINGS_STORAGE_KEY = "docsheet-view-settings";
  const DEFAULT_VIEW_SETTINGS = { wrapCells: false, compactRows: true, showSummary: true, showStats: false, showFilters: false, showBlankRows: false };

  function readViewSettings() {
    try {
      const parsed = JSON.parse(localStorage.getItem(VIEW_SETTINGS_STORAGE_KEY) || "{}");
      return { ...DEFAULT_VIEW_SETTINGS, ...(parsed && typeof parsed === "object" ? parsed : {}) };
    } catch (err) {
      return { ...DEFAULT_VIEW_SETTINGS };
    }
  }

  function writeViewSettings(settings) {
    try {
      localStorage.setItem(VIEW_SETTINGS_STORAGE_KEY, JSON.stringify(settings));
    } catch (err) {
      /* storage unavailable — settings just won't persist */
    }
  }

  function applyViewSettings(settings = readViewSettings()) {
    document.documentElement.classList.toggle("wrap-cells", Boolean(settings.wrapCells));
    document.documentElement.classList.toggle("compact-density", Boolean(settings.compactRows));
    if (viewSummary) viewSummary.hidden = !settings.showSummary;
    if (statsStrip) statsStrip.hidden = !settings.showStats;
    if (facetToggleBtn) {
      facetToggleBtn.setAttribute("aria-pressed", String(settings.showFilters));
    }
    if (facetBar) {
      facetBar.hidden = !(activeView === "master" && settings.showFilters);
    }
    if (wrapCellsToggle) wrapCellsToggle.checked = Boolean(settings.wrapCells);
    if (compactModeToggle) compactModeToggle.checked = Boolean(settings.compactRows);
    if (showSummaryToggle) showSummaryToggle.checked = Boolean(settings.showSummary);
    if (showStatsToggle) showStatsToggle.checked = Boolean(settings.showStats);
    if (showFiltersToggle) showFiltersToggle.checked = Boolean(settings.showFilters);
    if (showBlankRowsToggle && blankRowsToggleWrap) {
      showBlankRowsToggle.checked = Boolean(settings.showBlankRows);
      // The raw spreadsheet is the only view with blank separator rows.
      blankRowsToggleWrap.hidden = activeView !== "original";
    }
    if (table) {
      try {
        table.redraw(true);
        fitTableToContainer();
      } catch (err) {
        // Tabulator can still be booting when settings are first applied;
        // the classes above are enough and the normal tableBuilt/render pass
        // will size the table moments later.
      }
    }
  }

  function updateViewSetting(key, value) {
    const settings = readViewSettings();
    settings[key] = value;
    writeViewSettings(settings);
    applyViewSettings(settings);
  }

  function closeSettingsMenu() {
    if (!settingsMenu || !settingsBtn) return;
    settingsMenu.hidden = true;
    settingsBtn.setAttribute("aria-expanded", "false");
  }

  function expandEverything() {
    const settings = { wrapCells: true, compactRows: false, showSummary: true };
    writeViewSettings(settings);
    setExpertColumns(activeView, true);
    if (table) {
      table.getColumns().forEach((column) => column.show());
    }
    applyViewSettings(settings);
    configureExpertToggle(activeView);
    configureColumnChooser();
    closeSettingsMenu();
  }

  function resetCurrentView() {
    writeViewSettings({ ...DEFAULT_VIEW_SETTINGS });
    setExpertColumns(activeView, false);
    closeSettingsMenu();
    activateView(activeView);
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
    const visibleRows = table
      ? table.getData("active").length
      : (renderedAsMobileBrowse ? mobileBrowseRows.length : allData.length);
    const isFiltering = Boolean(activeSearchQuery || activeReviewFilter || !facetsEmpty());
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
      const field = activeReviewFilter.field;
      const raw = activeReviewFilter.value;
      // Filter chips spell out the full record-type label (e.g. "Curated
      // master") even though the in-cell badge is the compact "CM".
      const full = field === "record_type" && RECORD_TYPE_TITLES[raw]
        ? RECORD_TYPE_TITLES[raw]
        : statusLabel(field, raw);
      chips.push([humanizeField(field), full]);
    }
    // Facet selections become chips (e.g. "Series: Satsang Series ×").
    FACETS.forEach((facet) => {
      const selected = activeFacets[facet.id];
      if (!selected) return;
      selected.forEach((value) => {
        const label = facet.buildOptionLabel ? facet.buildOptionLabel(value) : (value || "(blank)");
        chips.push([COLUMN_LABELS[facet.field] || humanizeField(facet.field), label, { facet: facet.id, value }]);
      });
    });

    activeFilters.hidden = chips.length === 0;
    chips.forEach(([label, value, data]) => {
      const chip = document.createElement("span");
      chip.className = "filter-chip";
      if (data && data.facet) {
        chip.classList.add("filter-chip-removable");
        chip.title = "Remove this filter";
        chip.addEventListener("click", () => {
          activeFacets[data.facet] = (activeFacets[data.facet] || []).filter((v) => v !== data.value);
          writeFacetState(activeView, activeFacets);
          const select = (FACETS.find((f) => f.id === data.facet) || {}).el?.();
          if (select) [...select.options].forEach((option) => {
            if (option.value === data.value) option.selected = false;
          });
          if (facetClear) facetClear.hidden = Object.values(activeFacets).every((list) => !list || list.length === 0);
          applyActiveFilters();
        });
      }
      chip.append(
        document.createTextNode(`${label}: ${value}`),
      );
      filterChips.append(chip);
    });
  }

  function clearAllFilters() {
    activeSearchQuery = "";
    activeReviewFilter = null;
    activeFacets = {};
    writeFacetState(activeView, {});
    searchInput.value = "";
    clearSearchBtn.hidden = true;
    reviewFilter.value = "";
    if (facetBar) {
      FACETS.forEach((facet) => {
        const select = facet.el();
        if (select) [...select.options].forEach((option) => { option.selected = false; });
      });
      facetClear.hidden = true;
    }
    applyActiveFilters();
  }

  /* ------------------------------------------------------------------ *
   *  Mobile catalogue browse mode
   *
   *  A phone is a poor spreadsheet viewport, so the Everything view becomes
   *  a work-first catalogue on narrow screens. The full Tabulator sheet
   *  remains one tap away for expert comparison/export work. Cards are built
   *  only from the same generated master.json rows; no separate mobile data
   *  contract or browser-side editing exists.
   * ------------------------------------------------------------------ */
  function mobileMasterMode() {
    try {
      return localStorage.getItem(MOBILE_BROWSE_STORAGE_KEY) || "browse";
    } catch (err) {
      return "browse";
    }
  }

  function setMobileMasterMode(mode) {
    try {
      localStorage.setItem(MOBILE_BROWSE_STORAGE_KEY, mode);
    } catch (err) {
      /* Storage is optional; browse remains the safe default. */
    }
  }

  function masterPresentationMode() {
    try {
      return localStorage.getItem(MASTER_PRESENTATION_KEY) || "table";
    } catch (err) {
      return "table";
    }
  }

  function setMasterPresentationMode(mode) {
    try {
      localStorage.setItem(MASTER_PRESENTATION_KEY, mode);
    } catch (err) {
      /* storage unavailable — table remains the fallback */
    }
  }

  // Browse mode: phones default to it (per-viewport), desktops opt in via the
  // "Browse cards" toolbar toggle. Both render the same work-card UI.
  function mobileBrowseIsActive() {
    if (activeView !== "master") return false;
    if (mobileBrowseMedia.matches) return mobileMasterMode() !== "spreadsheet";
    return masterPresentationMode() === "browse";
  }

  function updateMobileViewToggle() {
    const isMobileMaster = activeView === "master" && mobileBrowseMedia.matches;
    const browsing = mobileBrowseIsActive();
    if (mobileViewToggle) {
      mobileViewToggle.hidden = !isMobileMaster;
      mobileViewToggle.textContent = browsing ? "Spreadsheet" : "Browse cards";
      mobileViewToggle.setAttribute("aria-pressed", String(browsing));
      mobileViewToggle.title = browsing
        ? "Switch to the full spreadsheet"
        : "Switch to the mobile work-card browser";
    }
    if (mobileBrowseSheetBtn) {
      mobileBrowseSheetBtn.hidden = !browsing;
    }
    if (masterBrowseToggle) {
      // Desktop presentation toggle: hidden on phones (the mobile UI owns
      // that choice) and on every non-catalogue view.
      masterBrowseToggle.hidden = activeView !== "master" || mobileBrowseMedia.matches;
      masterBrowseToggle.textContent = browsing ? "Spreadsheet" : "Browse cards";
      masterBrowseToggle.setAttribute("aria-pressed", String(browsing));
    }
  }

  function displayMobileDate(row) {
    if (!row.year) return "Date unknown";
    const year = row.year === "198X" ? "c. 1980s" : row.year;
    return row.month ? `${year} · ${row.month}` : year;
  }

  function displayMobileEdition(row) {
    return [row.format, row.format_detail].filter(Boolean).join(" · ") || "Edition not stated";
  }

  function mobilePrimaryUrl(row) {
    return row.source_url_veritas || row.source_url_hay_house ||
      row.source_url_audible || row.source_url_nightingale_conant ||
      row.source_url_amazon || "";
  }

  function mobileSourceLink(row, url, label) {
    if (!url) return null;
    const anchor = document.createElement("a");
    anchor.className = "mobile-edition-link";
    anchor.href = url;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    anchor.textContent = label;
    anchor.setAttribute("aria-label", `${label} for ${rowTitle(row)} (opens in new tab)`);
    return anchor;
  }

  function mobileEditionCard(row) {
    const article = document.createElement("article");
    article.className = "mobile-edition-card";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "mobile-edition-main";
    button.setAttribute("aria-label", `Inspect ${rowTitle(row)}`);

    const filename = document.createElement("span");
    filename.className = "mobile-edition-filename";
    filename.textContent = row.proposed_filename || rowTitle(row);
    const title = document.createElement("strong");
    title.className = "mobile-edition-title";
    title.textContent = rowTitle(row);
    const meta = document.createElement("span");
    meta.className = "mobile-edition-meta";
    meta.textContent = `${displayMobileDate(row)} · ${displayMobileEdition(row)}`;
    button.append(filename, title, meta);
    button.addEventListener("click", () => openRowDetails(row, button));
    article.append(button);

    const actions = document.createElement("div");
    actions.className = "mobile-edition-actions";
    const source = mobileSourceLink(row, mobilePrimaryUrl(row), "Source");
    const streaming = row.reference_url_1 && row.reference_url_1 !== mobilePrimaryUrl(row)
      ? mobileSourceLink(row, row.reference_url_1, "Stream")
      : null;
    if (source) actions.append(source);
    if (streaming) actions.append(streaming);
    if (actions.childElementCount) article.append(actions);
    return article;
  }

  function mobileWorkGroups(rows) {
    const groups = new Map();
    rows.forEach((row, index) => {
      const key = row.work_id || row.uuid || row.candidate_key || `record-${index}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(row);
    });
    return [...groups.values()];
  }

  function syncFacetSelect(facetId) {
    const facet = FACETS.find((item) => item.id === facetId);
    const select = facet && facet.el();
    if (!select) return;
    const selected = new Set(activeFacets[facetId] || []);
    [...select.options].forEach((option) => { option.selected = selected.has(option.value); });
  }

  function mobileFacetLabel(facet, value) {
    if (facet.id === "year") {
      if (!value) return "Unknown date";
      return value === "198X" ? "c. 1980s" : value;
    }
    return facet.buildOptionLabel ? facet.buildOptionLabel(value) : (value || "Not stated");
  }

  function toggleMobileFacet(facet, value) {
    const selected = new Set(activeFacets[facet.id] || []);
    if (selected.has(value)) selected.delete(value);
    else selected.add(value);
    activeFacets[facet.id] = [...selected];
    writeFacetState(activeView, activeFacets);
    syncFacetSelect(facet.id);
    if (facetClear) facetClear.hidden = facetsEmpty();
    applyActiveFilters();
  }

  function mobileFacetButton(facet, value, count, label = mobileFacetLabel(facet, value)) {
    const button = document.createElement("button");
    const selected = (activeFacets[facet.id] || []).includes(value);
    button.type = "button";
    button.className = "mobile-discovery-chip";
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
    button.dataset.mobileFacet = facet.id;
    button.dataset.mobileValue = value;
    button.textContent = count == null ? label : `${label} (${count})`;
    button.addEventListener("click", () => toggleMobileFacet(facet, value));
    return button;
  }

  function renderMobileDiscovery(data) {
    if (!mobileSeriesShelf || !mobileYearRail) return;
    const renderRail = (container, facet, compare) => {
      const counts = new Map();
      data.forEach((row) => {
        const value = String(row[facet.field] ?? "").trim();
        counts.set(value, (counts.get(value) || 0) + 1);
      });
      const values = [...counts.keys()].sort(compare);
      container.replaceChildren();
      const clear = document.createElement("button");
      const selected = activeFacets[facet.id] || [];
      clear.type = "button";
      clear.className = "mobile-discovery-chip mobile-discovery-all";
      clear.classList.toggle("active", selected.length === 0);
      clear.setAttribute("aria-pressed", String(selected.length === 0));
      clear.textContent = facet.id === "year" ? "All years" : "All series";
      clear.addEventListener("click", () => {
        activeFacets[facet.id] = [];
        writeFacetState(activeView, activeFacets);
        syncFacetSelect(facet.id);
        if (facetClear) facetClear.hidden = facetsEmpty();
        applyActiveFilters();
      });
      container.append(clear);
      values.forEach((value) => container.append(
        mobileFacetButton(facet, value, counts.get(value))
      ));
    };
    const seriesFacet = FACETS.find((facet) => facet.id === "series");
    const yearFacet = FACETS.find((facet) => facet.id === "year");
    renderRail(
      mobileSeriesShelf,
      seriesFacet,
      (a, b) => (data.filter((row) => row.series === b).length - data.filter((row) => row.series === a).length) || a.localeCompare(b)
    );
    renderRail(mobileYearRail, yearFacet, yearFacet.sort);
    if (mobileDiscoveryClear) mobileDiscoveryClear.hidden = facetsEmpty();
  }

  function renderMobileBrowse(data = allData) {
    if (!mobileBrowseList) return;
    renderMobileDiscovery(data);
    const rows = data.filter(rowMatchesActiveFilters);
    mobileBrowseRows = rows;
    mobileBrowseList.replaceChildren();
    if (!rows.length) {
      const message = document.createElement("p");
      message.className = "mobile-browse-empty";
      message.textContent = "No works match the current search and filters.";
      mobileBrowseList.append(message);
      updateSearchStatus();
      return;
    }

    mobileWorkGroups(rows).forEach((group) => {
      const first = group[0];
      if (group.length === 1) {
        const single = document.createElement("section");
        single.className = "mobile-work-card mobile-work-card-single";
        single.append(mobileEditionCard(first));
        mobileBrowseList.append(single);
        return;
      }

      const card = document.createElement("details");
      card.className = "mobile-work-card";
      const summary = document.createElement("summary");
      const eyebrow = document.createElement("span");
      eyebrow.className = "mobile-work-eyebrow";
      const formats = [...new Set(group.map((row) => row.format).filter(Boolean))];
      eyebrow.textContent = `${group.length} editions / parts${formats.length ? ` · ${formats.join(", ")}` : ""}`;
      const title = document.createElement("strong");
      title.className = "mobile-work-title";
      title.textContent = rowTitle(first);
      const hint = document.createElement("span");
      hint.className = "mobile-work-hint";
      hint.textContent = "Show editions";
      summary.append(eyebrow, title, hint);
      card.append(summary);

      const editions = document.createElement("div");
      editions.className = "mobile-work-editions";
      group.forEach((row) => editions.append(mobileEditionCard(row)));
      card.append(editions);
      mobileBrowseList.append(card);
    });
    updateSearchStatus();
  }

  function renderLoadedView(data, force = false) {
    const useMobileBrowse = mobileBrowseIsActive();
    updateMobileViewToggle();
    if (seriesLanding) seriesLanding.hidden = true;
    if (!force && useMobileBrowse === renderedAsMobileBrowse) {
      if (useMobileBrowse) renderMobileBrowse(data);
      return;
    }
    if (table) {
      table.destroy();
      table = null;
    }
    renderedAsMobileBrowse = useMobileBrowse;
    document.documentElement.classList.toggle("mobile-browse-active", useMobileBrowse);
    document.documentElement.classList.toggle("browse-active", useMobileBrowse);

    if (useMobileBrowse) {
      spreadsheet.hidden = true;
      mobileBrowse.hidden = false;
      configureReviewFilter(data);
      configureFacetBar(data);
      configureExpertToggle(activeView);
      configureColumnChooser();
      renderMobileBrowse(data);
      spreadsheet.setAttribute("aria-busy", "false");
      return;
    }

    mobileBrowse.hidden = true;
    spreadsheet.hidden = false;
    initTable(data);
  }

  function toggleMobilePresentation() {
    if (activeView !== "master" || !mobileBrowseMedia.matches) return;
    setMobileMasterMode(mobileBrowseIsActive() ? "spreadsheet" : "browse");
    closeRowDetails();
    renderLoadedView(allData, true);
  }

  /* ------------------------------------------------------------------ *
   *  Catalogue overview (hero, collection stats, series strip) and the
   *  client-side Series browser. All data comes from the same generated
   *  master.json rows already loaded into allData — no extra data files.
   * ------------------------------------------------------------------ */
  function introDismissed() {
    try {
      return localStorage.getItem(INTRO_STORAGE_KEY) === "1";
    } catch (err) {
      return false;
    }
  }

  function setIntroDismissed(dismissed) {
    try {
      localStorage.setItem(INTRO_STORAGE_KEY, dismissed ? "1" : "0");
    } catch (err) {
      /* storage unavailable — the overview just stays visible */
    }
  }

  function ownedValue(row) {
    return String(row.owned ?? "").toLowerCase();
  }

  function updateCatalogueIntro(data = allData) {
    if (!catalogueIntro) return;
    const show = activeView === "master" && data.length > 0 && !introDismissed();
    catalogueIntro.hidden = !show;
    if (overviewBtn) overviewBtn.hidden = activeView !== "master" || show;
    if (!show) return;
    renderCollectionOverview(data);
    renderSeriesStrip(data);
  }

  function overviewCard(title, statLine, owned, total) {
    const card = document.createElement("div");
    card.className = "overview-card";
    const name = document.createElement("strong");
    name.textContent = title;
    const stat = document.createElement("span");
    stat.className = "overview-stat";
    stat.textContent = statLine;
    card.append(name, stat);
    if (total > 0) {
      const track = document.createElement("div");
      track.className = "progress-track";
      track.setAttribute("role", "img");
      track.setAttribute("aria-label", `${owned} of ${total} owned`);
      const fill = document.createElement("div");
      fill.className = "progress-fill";
      fill.style.width = `${Math.round((owned / total) * 100)}%`;
      track.append(fill);
      card.append(track);
    }
    return card;
  }

  function renderCollectionOverview(data) {
    if (!overviewCards) return;
    overviewCards.replaceChildren();
    let ownedTrue = 0, ownedFalse = 0, ownedBlank = 0;
    data.forEach((row) => {
      const v = ownedValue(row);
      if (v === "true") ownedTrue += 1;
      else if (v === "false") ownedFalse += 1;
      else ownedBlank += 1;
    });
    const total = data.length;
    overviewCards.append(overviewCard(
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
        overviewCards.append(overviewCard(
          series,
          `${stats.owned} of ${stats.total} owned`,
          stats.owned,
          stats.total,
        ));
      });
  }

  function renderSeriesStrip(data) {
    if (!seriesStripList) return;
    seriesStripList.replaceChildren();
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
        chip.addEventListener("click", () => openSeriesFromStrip(series));
        seriesStripList.append(chip);
      });
  }

  // Apply a facet value to the master view (used by the strip and the Series
  // browser). The facet state is written for "master" regardless of the view
  // we are coming from, then the master view is (re)activated.
  function applyMasterFacet(facetId, value) {
    activeFacets = readFacetState("master");
    activeFacets[facetId] = [value];
    writeFacetState("master", activeFacets);
    syncFacetSelect(facetId);
    if (facetClear) facetClear.hidden = facetsEmpty();
  }

  function ensureTablePresentation() {
    if (mobileBrowseMedia.matches) return; // phones keep their own mode
    if (masterPresentationMode() !== "table") {
      setMasterPresentationMode("table");
      renderLoadedView(allData, true);
    }
  }

  function openSeriesFromStrip(series) {
    applyMasterFacet("series", series);
    ensureTablePresentation();
    applyActiveFilters();
    if (spreadsheet && !spreadsheet.hidden) spreadsheet.scrollIntoView({ block: "start" });
  }

  function openSeriesFromLanding(series) {
    applyMasterFacet("series", series);
    setMasterPresentationMode("table");
    activateView("master").then(() => {
      // populateFacets restores the persisted selection; apply it to the rows.
      applyActiveFilters();
      if (spreadsheet && !spreadsheet.hidden) spreadsheet.scrollIntoView({ block: "start" });
    });
  }

  function yearSpanFor(rows) {
    const years = [...new Set(
      rows.map((row) => String(row.year || "").trim())
        .filter((year) => /^\d{4}$/.test(year))
        .map(Number),
    )].sort((a, b) => a - b);
    if (!years.length) return "years unrecorded";
    return years.length === 1 ? String(years[0]) : `${years[0]}–${years[years.length - 1]}`;
  }

  function renderSeriesLanding(data) {
    if (!seriesLanding || !seriesLandingGrid) return;
    spreadsheet.hidden = true;
    mobileBrowse.hidden = true;
    emptyState.hidden = true;
    seriesLanding.hidden = false;
    // Spreadsheet-only controls don't apply to the card browser.
    if (expertToggleBtn) expertToggleBtn.hidden = true;
    if (columnMenuBtn) columnMenuBtn.hidden = true;
    seriesLandingGrid.replaceChildren();
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
      card.addEventListener("click", () => openSeriesFromLanding(series));
      seriesLandingGrid.append(card);
    });
    footerStats.textContent = `Series: ${entries.length} series`;
    searchStatus.textContent = `${entries.length} series · ${data.length} records`;
    spreadsheet.setAttribute("aria-busy", "false");
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

  function configureViewJump() {
    if (!viewJump) return;
    viewJump.replaceChildren();
    VIEW_GROUPS.forEach((group) => {
      const optgroup = document.createElement("optgroup");
      optgroup.label = group.label;
      group.views.forEach((viewName) => {
        const option = new Option(VIEWS[viewName].label, viewName);
        optgroup.append(option);
      });
      viewJump.append(optgroup);
    });
    viewJump.value = activeView;
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

  function copyValue(value, button) {
    const text = String(value || "").trim();
    if (!text || !navigator.clipboard || !button) return;
    navigator.clipboard.writeText(text).then(() => {
      const original = button.textContent;
      button.textContent = "Copied!";
      setTimeout(() => { button.textContent = original; }, 1500);
    }).catch(() => { /* clipboard blocked — no-op */ });
  }

  function copyFilename(data) {
    copyValue(data?.proposed_filename, copyFilenameBtn);
  }

  function primaryIdentifier(data) {
    return data?.uuid || data?.master_uuid || data?.veritas_product_id ||
      data?.source_product_id || data?.candidate_key || "";
  }

  function copyIdentifier(data) {
    copyValue(primaryIdentifier(data), copyIdBtn);
  }

  const DETAIL_SECTIONS = [
    {
      title: "Identity",
      fields: ["record_type", "proposed_filename", "title", "series", "item_type", "edition", "year_month", "catalog_code"],
    },
    {
      title: "Ownership & status",
      fields: ["owned", "review_status", "promotion_status", "mapping_status", "match_status", "disposition", "approval", "relationship_type"],
    },
    {
      title: "Sources",
      fields: ["source_url_veritas", "source_url_hay_house", "source_url_nightingale_conant", "source_url_audible", "source_url_amazon", "reference_url_1", "official_product_url", "evidence_url", "source_url"],
    },
    {
      title: "Provenance",
      fields: ["uuid", "work_id", "master_uuid", "legacy_tempid", "raw_tempid", "raw_row_number", "candidate_key", "source_product_id", "veritas_product_id", "year_source", "legacy_title", "notes", "evidence_note", "review_reason", "decision_reason", "provenance_note", "source_file"],
    },
  ];

  let currentRowData = null;
  let lastRowTrigger = null;

  function appendDetailField(container, field, value) {
    const item = document.createElement("div");
    item.className = "row-detail-field";
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = humanizeField(field);
    description.append(valueNode(field, value));
    item.append(term, description);
    container.append(item);
  }

  function appendDetailSection(container, title, entries) {
    if (!entries.length) return;
    const section = document.createElement("section");
    section.className = "row-detail-section";
    const heading = document.createElement("h3");
    heading.className = "row-details-section-title";
    heading.textContent = title;
    section.append(heading);
    entries.forEach(([field, value]) => appendDetailField(section, field, value));
    container.append(section);
  }

  function openRowDetails(data, trigger = null) {
    currentRowData = data;
    if (trigger && trigger instanceof HTMLElement) {
      trigger.tabIndex = 0;
      lastRowTrigger = trigger;
    }
    rowDetailsTitle.textContent = rowTitle(data);
    if (copyFilenameBtn) {
      const hasFilename = Boolean(String(data.proposed_filename || "").trim());
      copyFilenameBtn.hidden = !hasFilename;
    }
    if (copyIdBtn) {
      copyIdBtn.hidden = !Boolean(primaryIdentifier(data));
    }
    const entries = Object.entries(data).filter(([field]) => {
      // Year/Month and Format/Format Detail are shown through merged columns.
      if ("year_month" in data && (field === "year" || field === "month")) return false;
      if ("edition" in data && (field === "format" || field === "format_detail")) return false;
      return true;
    });
    const rendered = new Set();
    rowDetailsBody.replaceChildren();
    DETAIL_SECTIONS.forEach((section) => {
      const sectionEntries = entries.filter(([field]) => section.fields.includes(field));
      if (sectionEntries.length) {
        appendDetailSection(rowDetailsBody, section.title, sectionEntries);
        sectionEntries.forEach(([field]) => rendered.add(field));
      }
    });
    const additional = entries.filter(([field]) => !rendered.has(field));
    appendDetailSection(rowDetailsBody, "Additional fields", additional);
    rowDetails.hidden = false;
    bindDrawerFocusTrap();
    requestAnimationFrame(() => closeRowDetailsBtn.focus({ preventScroll: true }));
  }

  function closeRowDetails() {
    if (rowDetails.hidden) return;
    rowDetails.hidden = true;
    const trigger = lastRowTrigger;
    lastRowTrigger = null;
    if (trigger && document.contains(trigger)) {
      requestAnimationFrame(() => trigger.focus({ preventScroll: true }));
    }
  }

  function drawerFocusableControls() {
    // The drawer is a true modal: its official/evidence links are as important
    // as header buttons. Include every visible focusable descendant so Tab
    // cycles through the entire detail sheet rather than trapping keyboard
    // users above the source links.
    return [...rowDetails.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), ' +
      'textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )].filter((control) => !control.hidden && control.getClientRects().length > 0);
  }

  function trapRowDetailsFocus(event) {
    if (event.key !== "Tab" || rowDetails.hidden) return;
    if (event.currentTarget !== rowDetails) event.stopPropagation();
    const controls = drawerFocusableControls();
    if (!controls.length) return;
    const current = controls.indexOf(document.activeElement);
    const delta = event.shiftKey ? -1 : 1;
    const nextIndex = current === -1
      ? (event.shiftKey ? controls.length - 1 : 0)
      : (current + delta + controls.length) % controls.length;
    event.preventDefault();
    controls[nextIndex].focus();
  }

  function bindDrawerFocusTrap() {
    // Header controls persist between openings while body links are rebuilt.
    // Mark each element so a repeated row inspection never stacks handlers.
    drawerFocusableControls().forEach((control) => {
      if (control._docsheetFocusTrapBound) return;
      control.addEventListener("keydown", trapRowDetailsFocus);
      control._docsheetFocusTrapBound = true;
    });
  }

  /* ------------------------------------------------------------------ *
   *  Data loading
   * ------------------------------------------------------------------ */
  async function loadData(viewName, signal) {
    const view = VIEWS[viewName];
    const res = await fetch(view.file, { cache: "no-store", signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // Merge separate Year/Month fields into one "Year-Month" display column
    // ("YYYY-MM"). Applies to any view whose rows carry both fields (today:
    // Everything). The raw year/month keys stay on each row object for the
    // global search, but buildColumns, the row drawer, and CSV exports show
    // only the merged column.
    data.forEach((row) => {
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
    // The raw spreadsheet export contains 31 fully-empty visual-separator
    // rows (2026-08-09 audit §3.4). Hide them by default in the Original
    // Spreadsheet view; the "Show blank separator rows" view setting restores
    // the verbatim 374-row sheet (grid, counts, and CSV export all follow).
    const viewRows =
      viewName === "original" && !readViewSettings().showBlankRows
        ? data.filter((row) => Object.values(row).some((value) => String(value ?? "").trim() !== ""))
        : data;
    return { data: viewRows, lastModified: res.headers.get("Last-Modified") };
  }

  function applyLoadedViewMeta(viewName, data, lastModified) {
    const view = VIEWS[viewName];
    allData = data;
    footerUpdated.replaceChildren();
    if (lastModified) {
      const stamp = document.createElement("span");
      stamp.className = "updated";
      stamp.textContent = formatTimestamp(lastModified);
      footerUpdated.append("Last Updated: ", stamp);
    } else {
      footerUpdated.textContent = "Last Updated: Unknown";
    }
    footerStats.textContent = `${view.label}: ${data.length} rows`;
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
    // Comparison is case-insensitive so legacy capitalised values ("True"/"False")
    // render the same badge as the normalised "true"/"false" vocabulary.
    if (field === "owned" || field === "proposed_owned") {
      const v = String(value ?? "").toLowerCase();
      if (v === "true" || v === "false") return v === "true" ? "Owned" : "Not owned";
    }
    return value.replace(/_/g, " ");
  }

  function statusFormatter(cell) {
    const value = String(cell.getValue() ?? "");
    if (!value) return "";
    const field = cell.getColumn().getField();
    const badge = document.createElement("span");
    badge.className = `status-badge ${statusClass(value)}`;
    badge.textContent = statusLabel(field, value);
    // Compact record-type badges (e.g. "CM") carry their full label in the
    // tooltip; everything else shows the raw status value on hover.
    badge.title = (field === "record_type" && RECORD_TYPE_TITLES[value]) || value;
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
    // The proposed-filename column renders in a smaller monospace face, so
    // measure it with that face — otherwise the Roboto estimate is too narrow
    // and the frozen lead column's content overlaps the next header's click
    // target (caught by the column-layout sort spec in CI).
    const isMono = key === "proposed_filename";
    const font = isMono
      ? '12.5px ui-monospace, "SF Mono", Menlo, Consolas, monospace'
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

      const budget = COLUMN_BUDGETS[key] || {};
      const compactRecordType = key === "record_type";
      const col = {
        title: humanizeField(key),
        field: key,
        headerSort: true,          // click header to sort asc/desc
        resizable: true,           // drag column edge to resize
        minWidth: budget.minWidth ?? 60,
        maxWidth: budget.maxWidth,
        // Pages publishes generated catalogue/review data. Edits must occur in
        // the declared CSV review inputs, never as misleading session-only UI edits.
        editor: false,
        tooltip: (e, cell) => String(cell.getValue() ?? ""),
      };

      // Size the column to its widest rendered entry (see width engine above);
      // explicit budgets override the measurement for identity/control fields.
      const measured = measuredColumnWidth(key, col.title, data);
      let cap = budget.maxWidth ?? MAX_COLUMN_WIDTH;
      if (/title|note|reason|purpose|role/i.test(key)) cap = Math.min(cap, MAX_TEXT_WIDTH);
      if (key === "proposed_filename") cap = Math.min(cap, 340);
      if (budget.width != null) {
        col.width = budget.width;
      } else {
        col.width = Math.min(measured, cap);
      }

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
      if (key === "proposed_filename") {
        // The lead column renders like a file explorer: monospace (CSS) with
        // the extension shown in a muted color so the carrier is scannable.
        col.formatter = (cell) => {
          const value = String(cell.getValue() ?? "");
          if (!value) return "";
          const match = value.match(/^(.*?)(\.[A-Za-z0-9]+)$/);
          if (!match) return document.createTextNode(value);
          const frag = document.createDocumentFragment();
          frag.append(document.createTextNode(match[1]));
          const ext = document.createElement("span");
          ext.className = "ext";
          ext.textContent = match[2];
          frag.append(ext);
          return frag;
        };
      } else if (key === "edition") {
        // Edition cell: a small color dot by carrier (DVD/CD/audiobook/
        // streaming/book), then the merged "format · detail" label.
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
          frag.append(document.createTextNode(value));
          return frag;
        };
      } else if (FORMAT_FIELDS.has(key)) {
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

  function configureFacetBar(data) {
    if (!facetBar) return;
    // Faceted filtering applies to the curated catalogue (Everything) only.
    if (activeView !== "master") {
      facetBar.hidden = true;
      return;
    }
    const settings = readViewSettings();
    facetBar.hidden = !settings.showFilters;
    populateFacets(data);
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
    values.forEach((value) => {
      // Dropdown options spell out the full record-type label (e.g. "Curated
      // master") even though the in-cell badge is the compact "CM".
      const label = field === "record_type" && RECORD_TYPE_TITLES[value]
        ? RECORD_TYPE_TITLES[value]
        : statusLabel(field, value);
      reviewFilter.add(new Option(label, value));
    });
    reviewToolbar.hidden = false;
    reviewFilterHint.textContent = `${values.length} ${humanizeField(field).toLowerCase()} values`;
    reviewFilter.dataset.field = field;
  }

  function rowMatchesActiveFilters(data) {
    const searchMatches = !activeSearchQuery || Object.values(data).some(
      (value) => value !== null && value !== undefined &&
        String(value).toLowerCase().includes(activeSearchQuery)
    );
    const reviewMatches = !activeReviewFilter ||
      String(data[activeReviewFilter.field] ?? "") === activeReviewFilter.value;
    return searchMatches && reviewMatches && rowMatchesFacets(data);
  }

  function applyActiveFilters() {
    if (renderedAsMobileBrowse) {
      renderMobileBrowse(allData);
      return;
    }
    if (!table) return;
    if (!activeSearchQuery && !activeReviewFilter && facetsEmpty()) {
      table.clearFilter();
      updateSearchStatus();
      return;
    }
    table.setFilter(rowMatchesActiveFilters);
    updateSearchStatus();
  }

  function facetsEmpty() {
    return FACETS.every((facet) => {
      const selected = activeFacets[facet.id];
      return !selected || selected.length === 0;
    });
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
      /* editing disabled in column definitions; double-click is reserved for any future explicit editor */
      editTriggerEvent: "dblclick",
      selectableRows: false,
      // Work-group striping: mark the first row in each run of consecutive
      // rows sharing a work_id so a left accent visually groups parts/
      // editions of a work. Runs after the data is sorted/filtered.
      rowFormatter: (row) => {
        const data = row.getData();
        const element = row.getElement();
        // Make rows a keyboard-focusable source for the details drawer. Focus
        // returns here after close, so keyboard review does not lose context.
        // Programmatically focusable, but not 365 extra Tab stops in the page.
        element.tabIndex = -1;
        element.setAttribute("aria-label", rowTitle(data));
        if (!data.work_id) {
          element.classList.remove("work-group-start");
          return;
        }
        const siblings = table.getRows();
        const position = siblings.findIndex((r) => r === row);
        const prev = position > 0 ? siblings[position - 1].getData() : null;
        if (!prev || prev.work_id !== data.work_id) {
          element.classList.add("work-group-start");
        } else {
          element.classList.remove("work-group-start");
        }
      },
    });

    configureReviewFilter(data);
    configureFacetBar(data);
    configureColumnChooser();
    configureExpertToggle(activeView);
    applyViewSettings();
    restoreGridState();
    table.on("dataFiltered", updateSearchStatus);
    table.on("dataSorted", saveSortState);
    // Listeners are attached once (guarded) so tab switches don't accumulate
    // duplicate scroll handlers.
    if (!spreadsheet._docsheetScrollBound) {
      spreadsheet.addEventListener("scroll", onTableScroll, true);
      spreadsheet._docsheetScrollBound = true;
    }
    // The synchronous call below can run before Tabulator has processed its
    // initial data ("active" row pipeline is still empty), leaving the footer
    // stuck on "Showing: 0"; tableBuilt corrects the count once rows exist.
    table.on("tableBuilt", updateSearchStatus);
    table.on("rowClick", (event, row) => {
      if (event.target.closest && event.target.closest("a, button, input, select, textarea")) return;
      const element = row.getElement();
      element.focus({ preventScroll: true });
      openRowDetails(row.getData(), element);
    });
    spreadsheet.setAttribute("aria-busy", "false");
    updateSearchStatus();
  }

  /* Persist and restore per-view sort + horizontal scroll so a reviewer
     returns to a tab without losing their place. Column widths are left
     to the measured-width engine for now (they are deterministic). */
  function saveSortState() {
    if (!table) return;
    try {
      const sorters = table.getSorters().map((sorter) => ({
        field: sorter.field,
        dir: sorter.dir,
      }));
      writeGridState(activeView, { sorters });
    } catch (err) { /* table tearing down — ignore */ }
  }

  let scrollPersistTimer = null;
  function onTableScroll() {
    const element = spreadsheet.querySelector(".tabulator-tableholder");
    if (!element) return;
    clearTimeout(scrollPersistTimer);
    scrollPersistTimer = setTimeout(() => {
      writeGridState(activeView, { scrollLeft: element.scrollLeft });
    }, 150);
  }

  function restoreGridState() {
    if (!table) return;
    const state = readGridState()[activeView];
    if (!state) return;
    if (Array.isArray(state.sorters) && state.sorters.length) {
      try {
        table.setSort(state.sorters);
      } catch (err) { /* a field may have been renamed — ignore */ }
    }
    if (Number.isFinite(state.scrollLeft)) {
      const element = spreadsheet.querySelector(".tabulator-tableholder");
      if (element) {
        // Defer until Tabulator has laid out its columns.
        requestAnimationFrame(() => { element.scrollLeft = state.scrollLeft; });
      }
    }
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
    // Export the whole active sheet (not the filtered/card subset) so mobile
    // Browse mode keeps the same export contract as the Tabulator spreadsheet.
    if (table) {
      table.download("csv", VIEWS[activeView].exportName, { delimiter: ",", bom: true }, "all");
      return;
    }
    if (!allData.length) return;
    const fields = Object.keys(allData[0]);
    const quote = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;
    const csv = [fields.map(quote).join(","), ...allData.map((row) =>
      fields.map((field) => quote(row[field])).join(",")
    )].join("\n");
    const href = URL.createObjectURL(new Blob([`\uFEFF${csv}\n`], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = VIEWS[activeView].exportName;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(href);
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
    // A tab change may arrive before its predecessor's JSON fetch resolves.
    // Abort the old request where supported and retain a monotonic token as a
    // second guard: stale responses must never mutate global data/footer/UI.
    const activation = ++viewActivation;
    if (activeDataRequest) activeDataRequest.abort();
    const request = new AbortController();
    activeDataRequest = request;
    activeView = viewName;
    if (viewJump) viewJump.value = viewName;
    const view = VIEWS[viewName];
    if (facetToggleBtn) {
      facetToggleBtn.hidden = (viewName !== "master");
    }
    updateMobileViewToggle();
    if (catalogueIntro) catalogueIntro.hidden = true;
    if (overviewBtn) overviewBtn.hidden = true;
    if (seriesLanding) seriesLanding.hidden = true;
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
    renderedAsMobileBrowse = false;
    mobileBrowseRows = [];
    document.documentElement.classList.remove("mobile-browse-active");
    document.documentElement.classList.remove("browse-active");
    if (mobileBrowse) mobileBrowse.hidden = true;
    spreadsheet.hidden = false;
    spreadsheet.innerHTML = `<div class="table-loading" role="status"><span class="table-loading-text">Loading ${view.label.toLowerCase()}…</span><span class="skeleton-line" aria-hidden="true"></span><span class="skeleton-line" aria-hidden="true"></span><span class="skeleton-line skeleton-line-short" aria-hidden="true"></span></div>`;
    document.querySelectorAll(".dataset-tab").forEach((tab) => {
      const selected = tab.dataset.view === viewName;
      tab.classList.toggle("active", selected);
      tab.setAttribute("aria-selected", String(selected));
      // Roving tabindex: only the active tab stays in the Tab order
      // (Phase 2 a11y, 2026-08-08).
      tab.setAttribute("tabindex", selected ? "0" : "-1");
    });

    try {
      const { data, lastModified } = await loadData(viewName, request.signal);
      if (activation !== viewActivation) return;
      if (activeDataRequest === request) activeDataRequest = null;
      applyLoadedViewMeta(viewName, data, lastModified);
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
        if (facetBar) facetBar.hidden = true;
        return;
      }
      emptyState.hidden = true;
      if (viewName === "series") {
        renderSeriesLanding(data);
        console.info(`[docsheet] Loaded ${data.length} ${viewName} rows`);
        return;
      }
      if (viewName === "master") updateCatalogueIntro(data);
      renderLoadedView(data, true);
      console.info(`[docsheet] Loaded ${data.length} ${viewName} rows`);
    } catch (err) {
      // A replacement tab activation owns the surface. AbortError is expected
      // during normal rapid navigation and should never flash a load failure.
      if (activation !== viewActivation || (err && err.name === "AbortError")) return;
      if (activeDataRequest === request) activeDataRequest = null;
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
      applyViewSettings();
    } catch (err) {
      /* meta unavailable — the strip simply stays hidden */
    }
  }

  async function boot() {
    initDarkMode();
    loadStatsStrip();
    configureViewJump();
    if (viewJump) {
      viewJump.addEventListener("change", () => activateView(viewJump.value));
    }
    searchInput.addEventListener("input", debounce((e) => applySearch(e.target.value), 250));
    clearSearchBtn.addEventListener("click", () => {
      searchInput.value = "";
      applySearch("");
      searchInput.focus();
    });
    clearAllFiltersBtn.addEventListener("click", clearAllFilters);
    exportBtn.addEventListener("click", exportCsv);
    applyViewSettings();
    if (settingsBtn && settingsMenu) {
      settingsBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        const willOpen = settingsMenu.hidden;
        settingsMenu.hidden = !willOpen;
        settingsBtn.setAttribute("aria-expanded", String(willOpen));
        closeColumnMenu();
      });
      settingsMenu.addEventListener("click", (event) => event.stopPropagation());
    }
    if (expandEverythingBtn) expandEverythingBtn.addEventListener("click", expandEverything);
    if (resetViewBtn) resetViewBtn.addEventListener("click", resetCurrentView);
    [mobileViewToggle, mobileBrowseSheetBtn].filter(Boolean).forEach((button) => {
      button.addEventListener("click", toggleMobilePresentation);
    });
    if (mobileDiscoveryClear) mobileDiscoveryClear.addEventListener("click", clearFacets);
    if (masterBrowseToggle) {
      masterBrowseToggle.addEventListener("click", () => {
        if (activeView !== "master") return;
        const browsing = mobileBrowseIsActive();
        setMasterPresentationMode(browsing ? "table" : "browse");
        closeRowDetails();
        renderLoadedView(allData, true);
      });
    }
    if (heroDismiss) {
      heroDismiss.addEventListener("click", () => {
        setIntroDismissed(true);
        if (catalogueIntro) catalogueIntro.hidden = true;
        if (overviewBtn) overviewBtn.hidden = false;
      });
    }
    if (overviewBtn) {
      overviewBtn.addEventListener("click", () => {
        setIntroDismissed(false);
        updateCatalogueIntro();
        if (catalogueIntro && !catalogueIntro.hidden) {
          catalogueIntro.scrollIntoView({ block: "start" });
        }
      });
    }
    if (hero) {
      hero.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-hero-action]");
        if (!button) return;
        const action = button.dataset.heroAction;
        if (action === "browse") {
          if (!mobileBrowseMedia.matches) {
            setMasterPresentationMode("browse");
            renderLoadedView(allData, true);
          }
        } else if (action === "series") {
          const strip = document.getElementById("series-strip-list");
          if (strip) strip.scrollIntoView({ block: "start" });
        } else if (action === "overview") {
          const overview = document.getElementById("collection-overview-title");
          if (overview) overview.scrollIntoView({ block: "start" });
        } else if (action === "not-owned") {
          applyMasterFacet("owned", "false");
          ensureTablePresentation();
          applyActiveFilters();
          if (spreadsheet && !spreadsheet.hidden) spreadsheet.scrollIntoView({ block: "start" });
        }
      });
    }
    if (reviewNavToggle && reviewNavGroups) {
      let navCollapsed = false;
      try {
        navCollapsed = localStorage.getItem(REVIEW_NAV_KEY) === "1";
      } catch (err) {
        /* storage unavailable — expanded default */
      }
      const applyNavState = (collapsed) => {
        reviewNavGroups.hidden = collapsed;
        reviewNavToggle.setAttribute("aria-expanded", String(!collapsed));
        reviewNavToggle.classList.toggle("collapsed", collapsed);
      };
      applyNavState(navCollapsed);
      reviewNavToggle.addEventListener("click", () => {
        navCollapsed = !reviewNavGroups.hidden;
        applyNavState(navCollapsed);
        try {
          localStorage.setItem(REVIEW_NAV_KEY, navCollapsed ? "1" : "0");
        } catch (err) {
          /* storage unavailable */
        }
      });
    }
    if (mobileBrowseMedia.addEventListener) {
      mobileBrowseMedia.addEventListener("change", () => {
        updateMobileViewToggle();
        if (activeView === "master" && allData.length) renderLoadedView(allData, true);
      });
    }
    if (wrapCellsToggle) {
      wrapCellsToggle.addEventListener("change", () => updateViewSetting("wrapCells", wrapCellsToggle.checked));
    }
    if (compactModeToggle) {
      compactModeToggle.addEventListener("change", () => updateViewSetting("compactRows", compactModeToggle.checked));
    }
    if (showSummaryToggle) {
      showSummaryToggle.addEventListener("change", () => updateViewSetting("showSummary", showSummaryToggle.checked));
    }
    if (showStatsToggle) {
      showStatsToggle.addEventListener("change", () => updateViewSetting("showStats", showStatsToggle.checked));
    }
    if (showFiltersToggle) {
      showFiltersToggle.addEventListener("change", () => updateViewSetting("showFilters", showFiltersToggle.checked));
    }
    if (showBlankRowsToggle) {
      showBlankRowsToggle.addEventListener("change", () => {
        updateViewSetting("showBlankRows", showBlankRowsToggle.checked);
        // The setting changes which rows the raw view loads, so re-activate it.
        if (activeView === "original") activateView("original");
      });
    }
    if (facetToggleBtn) {
      facetToggleBtn.addEventListener("click", () => {
        const settings = readViewSettings();
        const nextShow = !settings.showFilters;
        updateViewSetting("showFilters", nextShow);
      });
    }
    if (descToggleBtn && viewDescription) {
      descToggleBtn.addEventListener("click", () => {
        const isHidden = viewDescription.hidden;
        viewDescription.hidden = !isHidden;
        descToggleBtn.setAttribute("aria-expanded", isHidden ? "true" : "false");
        descToggleBtn.classList.toggle("active", isHidden);
      });
    }
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
      closeSettingsMenu();
    });
    columnMenu.addEventListener("click", (event) => event.stopPropagation());
    if (expertToggleBtn) {
      expertToggleBtn.addEventListener("click", toggleExpertColumns);
    }
    showAllColumnsBtn.addEventListener("click", showAllColumns);
    closeRowDetailsBtn.addEventListener("click", closeRowDetails);
    if (copyFilenameBtn) {
      copyFilenameBtn.addEventListener("click", () => currentRowData && copyFilename(currentRowData));
    }
    if (copyIdBtn) {
      copyIdBtn.addEventListener("click", () => currentRowData && copyIdentifier(currentRowData));
    }
    if (facetClear) facetClear.addEventListener("click", clearFacets);
    FACETS.forEach((facet) => {
      const select = facet.el();
      if (!select) return;
      select.addEventListener("change", () => {
        activeFacets[facet.id] = [...select.selectedOptions].map((option) => option.value);
        writeFacetState(activeView, activeFacets);
        if (facetClear) {
          facetClear.hidden = facetsEmpty();
        }
        applyActiveFilters();
      });
    });
    // Stats chips navigate to their corresponding sheet (P0 UX).
    document.querySelectorAll(".stat-chip[data-jump]").forEach((chip) => {
      chip.addEventListener("click", () => activateView(chip.dataset.jump));
    });
    document.addEventListener("click", () => {
      closeColumnMenu();
      closeSettingsMenu();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeColumnMenu();
        closeSettingsMenu();
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
    document.addEventListener("keydown", handleGlobalShortcuts);
  }

  /* Power-user keyboard shortcuts:
       /  focus search
       j  next row / k previous row (opens details)
       y  copy the proposed filename of the focused/last row
       ?  toggle a shortcut help overlay
     Ignored while typing in a field/select/textarea. */
  let focusedRowIndex = -1;
  function isTypingTarget(event) {
    const tag = (event.target && event.target.tagName) || "";
    return ["INPUT", "SELECT", "TEXTAREA"].includes(tag) ||
      (event.target && event.target.isContentEditable);
  }
  function moveRowFocus(delta) {
    if (!table) return;
    const rows = [...table.getRows()];
    if (rows.length === 0) return;
    focusedRowIndex = Math.max(0, Math.min(rows.length - 1, focusedRowIndex + delta));
    const row = rows[focusedRowIndex];
    const element = row.getElement();
    element.scrollIntoView({ block: "nearest" });
    element.classList.add("row-keyboard-focus");
    element.focus({ preventScroll: true });
    rows.forEach((r, i) => { if (i !== focusedRowIndex) r.getElement().classList.remove("row-keyboard-focus"); });
    openRowDetails(row.getData(), element);
  }
  function handleGlobalShortcuts(event) {
    if (isTypingTarget(event)) {
      if (event.key === "Escape" && event.target === searchInput) {
        searchInput.value = "";
        applySearch("");
      }
      return;
    }
    if (event.key === "/") {
      event.preventDefault();
      searchInput.focus();
      searchInput.select();
    } else if (event.key === "j") {
      event.preventDefault();
      moveRowFocus(1);
    } else if (event.key === "k") {
      event.preventDefault();
      moveRowFocus(-1);
    } else if (event.key === "y") {
      event.preventDefault();
      if (currentRowData) copyFilename(currentRowData);
    } else if (event.key === "?") {
      event.preventDefault();
      toggleShortcutsHelp();
    }
  }

  function toggleShortcutsHelp() {
    let overlay = document.getElementById("shortcuts-help");
    if (overlay) {
      overlay.remove();
      return;
    }
    overlay = document.createElement("div");
    overlay.id = "shortcuts-help";
    overlay.className = "shortcuts-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-label", "Keyboard shortcuts");
    overlay.innerHTML = `
      <div class="shortcuts-card">
        <h2>Keyboard shortcuts</h2>
        <dl>
          <dt><kbd>/</kbd></dt><dd>Focus search</dd>
          <dt><kbd>j</kbd> / <kbd>k</kbd></dt><dd>Next / previous row (opens details)</dd>
          <dt><kbd>y</kbd></dt><dd>Copy the proposed file name of the open row</dd>
          <dt><kbd>←</kbd> / <kbd>→</kbd></dt><dd>Switch tabs</dd>
          <dt><kbd>Esc</kbd></dt><dd>Close dialogs / menus / clear search</dd>
          <dt><kbd>?</kbd></dt><dd>Toggle this help</dd>
        </dl>
        <button type="button" class="shortcuts-close">Close</button>
      </div>`;
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay || event.target.classList.contains("shortcuts-close")) {
        overlay.remove();
      }
    });
    document.body.append(overlay);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
