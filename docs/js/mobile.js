// =============================================================================
// docs/js/mobile.js — Mobile browse mode UI components.
// Renders work cards, edition cards, and discovery rails for browse mode.
// Depends on data-utils.js for pure data helpers and formatters.js for labels.
// =============================================================================

import {
  displayMobileDate, displayMobileEdition, mobilePrimaryUrl,
} from "./data-utils.js";
import { rowTitle } from "./formatters.js";

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

/**
 * Create an overview statistics card for the catalogue hero section.
 */
export function overviewCard(title, statLine, owned, total) {
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
