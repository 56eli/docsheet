// =============================================================================
// docs/js/config.js — Pure configuration constants for the DocSheet frontend.
// No DOM access, no mutable state. Imported by app.js.
// =============================================================================

export const VIEWS = {
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

export const VIEW_GROUPS = [
  { label: "Catalogue", views: ["master", "series", "productRelationships", "seriesCompilations"] },
  { label: "Review workspace", views: ["reviewOverview", "manualCandidates", "manualLeads", "masterExclusions", "sourceOverrides", "veritasMappingDecisions", "newWorkReview", "officialDiscovery", "internationalProducts"] },
  { label: "Sources", views: ["publishers", "veritasProducts", "hayhouseProducts", "audibleProducts", "filenameProposal", "migrationReview", "original"] },
];

export const EMPTY_STATE_MESSAGES = {
  officialDiscovery:
    "Standing intake lane — every queued item has been ruled out or promoted. " +
    "If a Veritas catalogue refresh surfaces unmatched products, they will land here for review.",
  newWorkReview:
    "Standing intake lane — no unmatched Veritas products are awaiting a new-work ruling right now.",
};
export const DEFAULT_EMPTY_MESSAGE = "No rows in this view.";

export const VIEW_DETAILS = {
  master: {
    type: "Complete curated catalogue",
    description: "The full curated catalogue of David R. Hawkins works — one row per edition, grouped by work. On phones it opens in Browse mode: compact work stacks with source and streaming actions; use Spreadsheet for the full grid. Product facts come first: title, series, type, edition (carrier), edition note (free-text distinction for same-work editions, e.g. Power vs Force B&W vs non-B&W), date, official store and streaming links, notes. Technical columns (Master ID, Work, proposed file names, provenance) stay hidden until you switch on Expert columns next to the Columns menu; clicking any row still shows every stored field. Candidate rows, when present, are marked by the Record Type badge and are not master records.",
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

export const COLUMN_LABELS = {
  record_type: "Record Type",
  uuid: "Master ID",
  work_id: "Work",
  edition: "Edition",
  edition_note: "Edition Note",
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
  research: "Research",
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

export const STATUS_FIELDS = new Set([
  "record_type", "review_status", "promotion_status", "mapping_status", "match_status",
  "disposition", "approval", "owned", "proposed_owned", "relationship_type",
]);

export const FORMAT_FIELDS = new Set(["format"]);

export const REVIEW_FILTER_FIELDS = [
  "record_type", "promotion_status", "review_status", "disposition", "approval",
  "mapping_status", "match_status", "relationship_type",
];

export const RECORD_TYPE_LABELS = {
  master: "CM",
  candidate_discovery: "Candidate · discovery",
  candidate_veritas: "Candidate · Veritas",
  candidate_hayhouse: "Candidate · Hay House",
  candidate_audible: "Candidate · Audible",
  candidate_pending_promotion: "Candidate · pending promotion",
};

export const RECORD_TYPE_TITLES = {
  master: "Curated master",
  candidate_discovery: "Candidate · discovery",
  candidate_veritas: "Candidate · Veritas",
  candidate_hayhouse: "Candidate · Hay House",
  candidate_audible: "Candidate · Audible",
  candidate_pending_promotion: "Candidate · pending promotion",
};

export const DEFAULT_PRIORITY_FIELDS = [
  "record_type",
  "title", "proposed_filename", "candidate_title", "official_title", "review_sheet", "publisher",
  "relationship_id", "raw_row_number", "disposition", "review_status",
  "mapping_status", "promotion_status", "match_status", "item_type", "series",
  "year", "year_source", "format", "owned", "source_name", "official_product_url",
  "evidence_url", "review_notes", "notes",
];

export const LOW_PRIORITY_FIELDS = [
  "uuid", "work_id", "master_uuid", "matched_master_uuids", "raw_uuid", "catalog_code",
  "legacy_tempid", "raw_tempid", "source_product_id", "veritas_product_id",
  "normalized_title_match_count", "raw_unnamed_5", "raw_unnamed_8", "raw_unnamed_9",
  "raw_unnamed_10", "raw_unnamed_11", "research",
];

export const COLUMN_BUDGETS = {
  record_type: { width: 52, minWidth: 48, maxWidth: 58 },
  owned: { width: 72, minWidth: 62, maxWidth: 85 },
  proposed_filename: { minWidth: 220 },
  title: { minWidth: 150 },
  series: { minWidth: 180 },
  edition_note: { minWidth: 180 },
};

export const COLUMN_PRESETS = {
  master: {
    priority: ["record_type", "proposed_filename", "item_type", "owned", "notes", "edition", "edition_note", "source_url_veritas", "source_url_hay_house", "source_url_audible", "source_url_amazon", "source_url_nightingale_conant", "reference_url_1", "catalog_code", "title", "series", "year_month"],
    frozen: ["record_type", "proposed_filename"],
    hidden: ["title", "series", "year", "month", "uuid", "work_id", "legacy_tempid", "proposed_filename_display", "year_source", "raw_row_number", "legacy_title", "research", "edition_note"],
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
};

// Detail-section layout for the row-details drawer.
export const DETAIL_SECTIONS = [
  { title: "Identity", fields: ["record_type", "uuid", "work_id", "catalog_code", "legacy_tempid", "title", "proposed_filename", "proposed_filename_display", "legacy_title"] },
  { title: "Content", fields: ["item_type", "series", "year", "month", "year_source", "edition", "edition_note", "format", "format_detail"] },
  { title: "Ownership", fields: ["owned"] },
  { title: "Official sources", fields: ["source_url_veritas", "source_url_hay_house", "source_url_nightingale_conant", "source_url_audible", "source_url_amazon", "reference_url_1"] },
  { title: "Notes", fields: ["notes"] },
  { title: "Research", fields: ["research"] },
];

/**
 * Produce a human-readable column label from a field key.
 * Uses COLUMN_LABELS when available, otherwise title-cases the key.
 */
export function humanizeField(key) {
  if (COLUMN_LABELS[key]) return COLUMN_LABELS[key];
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}
