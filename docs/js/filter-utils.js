// =============================================================================
// docs/js/filter-utils.js — Pure filter/facet utility functions.
// No DOM access. Imported by app.js for facet matching and label helpers.
// =============================================================================

import { COLUMN_LABELS, humanizeField } from "./config.js?v=5189225f358d";

/**
 * Check if a row matches all active facet selections.
 * `activeFacets` maps facet IDs to arrays of selected values.
 * `facetsConfig` is the FACETS array from app.js.
 */
export function rowMatchesFacets(row, activeFacets, facetsConfig) {
  return facetsConfig.every((facet) => {
    const selected = activeFacets[facet.id];
    if (!selected || selected.length === 0) return true;
    const value = String(row[facet.field] ?? "").trim();
    return selected.includes(value);
  });
}

/**
 * Check if all facet selections are empty.
 */
export function facetsEmpty(activeFacets, facetsConfig) {
  return facetsConfig.every((facet) => {
    const selected = activeFacets[facet.id];
    return !selected || selected.length === 0;
  });
}

/**
 * Build a human-readable label for a mobile discovery chip.
 */
export function mobileFacetLabel(facet, value) {
  if (facet.id === "year") {
    if (!value) return "Unknown date";
    return value === "198X" ? "c. 1980s" : value;
  }
  return facet.buildOptionLabel ? facet.buildOptionLabel(value) : (value || "Not stated");
}
