# Site UX / IA Redesign Proposal — 2026-08-08

**Prepared:** 2026-08-08 · **Status:** proposal — awaiting owner pick (phase(s)) · **Branch:** `arena/019fe098-docsheet`
**Applies to:** `docs/index.html`, `docs/app.js`, `docs/style.css`, Playwright specs. **No data changes.**
**Grounding:** current implementation reviewed line-by-line (15 flat tabs, Tabulator 6.5.2 + midnight dark theme, CSS custom properties + `color-mix`, badge classes `status-*`, aria-live footer, persisted Expert-columns toggle, 44px drawer close target).

---

## 1. Current state

- **15 tabs in one flat row:** Everything · Review Overview · Master Candidates · Manual Leads · Master Exclusions · Migration Review · Source Overrides · Official Discovery · New Work Review · Series Compilations · Veritas Decisions · Product Relationships · International Editions · Approved Publishers · Original Spreadsheet.
- Strengths to keep: visitor-first Everything column order; persisted dark mode + Expert toggle; aria-live "Showing: X of Y"; pinned Tabulator with SRI; 44px touch targets; phone adaptation.
- Friction points: (1) a long undifferentiated tab bar — review/provenance/catalogue views all look alike; (2) empty intake lanes (Official Discovery, New Work Review) show blank tables with no explanation; (3) tabs are click-only (no arrow-key roving focus); (4) provenance views (Migration Review, Original Spreadsheet) sit in the middle of the bar; (5) no column-grouping in the Columns menu; (6) theme is functional but generic.

---

## 2. Information architecture — group the tabs into three sections

Proposed order (category chips above a compact tab row):

```
[ Catalogue ]        Everything · Product Relationships · Series Compilations
[ Review workspace ] Review Overview · Master Candidates · Manual Leads · Master Exclusions
                     Source Overrides · Veritas Decisions · New Work Review · Official Discovery · International Editions
[ Sources ]          Approved Publishers · Migration Review · Original Spreadsheet
```

Rationale:
- **Visitors land on catalogue facts** (Everything + the two relationship sheets) — no review tooling in sight first.
- **Reviewers get one grouped workspace** (the 9 review sheets), headed by the Review Overview index.
- **Provenance and raw source go last** (Approved Publishers, Migration Review, Original Spreadsheet) — they answer "where did this come from?", not "what is this?".
- Implementation is cheap: the tabs are already driven by `data-view` attributes; grouping = a small `<optgroup>`-style section wrapper in `index.html` + a `data-group` attribute consumed by `style.css` (spacing + subtle section label), plus a grouping map in `app.js` for the keyboard/roving logic. IDs and `data-view` values stay stable so tests, exports, and deep links don't break. ("Everything" label stays — it's the established name in README/specs.)

## 3. Accessibility (WCAG-aligned, concrete)

1. **Roving tabindex + arrow-key navigation** on the tablist (currently click-only; only a global keydown exists). Home/End + Left/Right within the active group; `aria-selected` already present.
2. **Empty-state panels:** Official Discovery and New Work Review render a friendly card ("Standing intake lane — every queued item has been ruled. New Veritas refresh unmatched products land here.") instead of an empty grid, with `role="status"`. This converts a confusing blank table into information.
3. **Contrast pass on badges:** check `status-pending` (yellow) and `status-candidate` against both themes against WCAG AA (3:1 for UI components / 4.5:1 for text); add dark-mode-specific badge borders (some already exist).
4. **`:focus-visible` rings** on tabs, buttons, links, and row-details close (a consistent 2px ring in the accent color, never `outline: none`).
5. **`prefers-reduced-motion`:** disable the 0.25s background/border transitions and Tabulator's row animation (CSS media query + a `renderVertical`/animation flag in Tabulator options).
6. **External links:** consistent "↗" affordance + `aria-label="… (opens in new tab)"` on linkified cells (Veritas/Amazon/streaming columns) with `rel="noopener"` (Tabulator formatter change).
7. **Search UX:** Esc clears the box (already used for other shortcuts — add explicit handler); announce "N matches for '…'" in the existing `aria-live` status line.
8. **Sticky identity columns:** freeze **Title** (+ Series on Everything) so horizontal scroll never loses context (Tabulator `frozen` — the preset mechanism already exists).

## 4. Information presentation

- **Stats strip:** under the header, 4 stat chips (Curated master · Catalogue codes · Source overrides · Relationships) read from `docs/catalogue-meta.json` — the numbers are already generated; this just surfaces them visitor-first.
- **Columns menu grouped** into *Product facts / Technical (Expert) / Provenance* checkboxes instead of one flat list.
- **Row-details drawer:** add previous/next row buttons + "Copy row as text" (keeps the 44px close target).
- **Codes & IDs in monospace** (`catalog_code`, `uuid`, `work_id`, `veritas_product_id`) — tiny CSS class from the existing field-type formatter hook.
- **Badge palette harmonized:** one hue per semantic state across `status-*` (green=ok/reviewed, amber=review/pending, red=excluded, blue=master, neutral=other) — mostly exists; standardize `status-candidate` with the others.

## 5. Slick theme (token-driven, no new dependencies)

- Keep the CSS-variable + `color-mix` architecture; refine the palette: deep indigo accent (`--accent`) with a subtle gradient header, soft shadows, 8px radii, tighter type scale (Roboto kept — zero new font deps; optional Inter swap later).
- **Dark mode:** migrate off Tabulator's midnight defaults toward fully token-driven custom surfaces (`--bg`, `--surface`, `--surface-2`, borders) so both themes feel like one designed product rather than a framework default.
- **Header:** brand gradient bar + the stats chips; **footer:** add repo link + generated `Last-Modified` (already fetched) with a small "docs" badge.
- **Tabulator skin:** sticky header with backdrop blur, softer gridlines, row-hover + selection tint, rounded corner affordance on the scrollbar.

## 6. Phasing (each phase: no data changes, node checks + Playwright specs updated, all six pipeline `--check` untouched)

| Phase | Scope | Risk |
|---|---|---|
| **1 — IA** | Tab grouping + reorder, empty-state cards, stats strip, frozen Title/Series | Low — label/ID stability maintained; specs updated (column-layout asserts measured widths — re-measure) |
| **2 — A11y** | Roving tabs, focus rings, contrast, reduced motion, Esc-to-clear, link labels | Low — pure app.js/CSS additions |
| **3 — Theme** | Palette tokens, dark-mode surfaces, header/footer polish, Tabulator skin | Medium — visual only; width engine re-measured |

Suggested entry point: **Phase 1** (biggest usability win, smallest surface), then Phase 2, then Phase 3. Everything is committed-artifact-free (docs/ only) and reversible.
