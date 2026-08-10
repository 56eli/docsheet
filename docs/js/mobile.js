// =============================================================================
// docs/js/mobile.js — Mobile browse mode UI components.
// Renders work cards, edition cards, and discovery rails for browse mode.
// Depends on data-utils.js for pure data helpers and formatters.js for labels.
// =============================================================================

import {
  displayMobileDate, displayMobileEdition, mobilePrimaryUrl,
} from "./data-utils.js?v=0288c69670bb";
import { rowTitle } from "./formatters.js?v=ee2398b737f4";

/**
 * Create a source/stream link element for a mobile edition card.
 */
export function mobileSourceLink(row, url, label) {
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

/**
 * Create a mobile edition card element for a single row.
 */
export function mobileEditionCard(row, openRowDetails) {
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
