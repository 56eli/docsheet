# UX Rework Suggestions — Hawkins Archive Live Spreadsheet

**Prepared:** 2026-08-08
**Context:** The 2026-08-08 redesign (three labelled tab groups, stats strip,
empty states, a11y, minimalist theme, View settings with "Expand everything")
is a solid foundation. This document proposes the next layer of UX improvements
to make the catalogue genuinely easy to use for both visitors and reviewers.

Two owner directives are already applied in this session:
- **Proposed File Name is now the lead column** (visible by default, frozen
  right after the compact `CM` record-type badge).
- **Curated-master badges read "CM"** (full phrase stays in the tooltip,
  column header, filter dropdown, and active-filter chip).

---

## 1. Information architecture

### 1a. Default to the filename-first, scannable layout
The Everything sheet is the landing view. With Proposed File Name first, each
row reads like an actual file on disk, which matches the mental model of
someone organizing the collection. Consider:

- **Fixed left rail (3 frozen columns):** `CM` · `Proposed File Name` ·
  `Title`. These identify a row no matter how far right a reviewer scrolls.
- **Group the remaining columns into collapsible sections** via a column-group
  header row:
  - **Identity** — Series, Item Type, Edition, Year-Month, Catalogue Code,
    Owned
  - **Sources (buy/listen)** — Veritas, Hay House, Audible, Amazon,
    Nightingale-Conant, Streaming
  - **Review / provenance** — Notes, and (Expert) Master ID, Work, Legacy ID,
    Year Source, Raw Row, Original Title
  Tabulator supports nested column groups (`columns: [{title, columns}]`);
  this adds structure without removing any field.

### 1b. De-emphasize the 19-tab wall
19 tabs is a lot. The three groups help, but reviewers mostly use a handful:

- **Reorder by frequency:** Everything, Filename Proposal, Product
  Relationships, Veritas Products, then the review lanes, then the rest.
- **Shorten labels where unambiguous:** "Veritas Decisions" → "Decisions",
  "Series Compilations" → "Compilations", "Master Exclusions" → "Exclusions",
  "Approved Publishers" → "Publishers".
- **Consider a "Review" dropdown menu** for the 9 review-workspace tabs
  (Review Overview, Master Candidates, Manual Leads, Exclusions, Source
  Overrides, Decisions, New Work Review, Official Discovery, International)
  instead of nine tabs. The Catalogue and Sources groups stay as tabs.

### 1c. Add a saved/view-state per tab
Right now the View settings (wrap, density, summary) are global. Column
visibility (Expert toggle) is already per-view. Extend persistence to: sort
column + direction, horizontal scroll position, and column widths. A reviewer
mid-way through a pass shouldn't lose their place on tab switch.

---

## 2. The Everything sheet (catalogue)

### 2a. Filename cell as the primary affordance
The proposed filename is now the lead column — make it work harder:

- **Monospace, slightly denser** so filenames line up and scan like a file
  explorer (e.g. `ui-monospace, "SF Mono", Menlo, monospace` at 13px).
- **Color-code the extension** (`.mp4`, `.mp3`, `.m4b`, `.pdf`) with a tiny
  muted suffix so carriers are visually distinguishable without reading the
  Edition column.
- **Part badges:** `[1/3]`, `[2/3]` could render as small pills (already
  display-safe), reinforcing multi-part lectures.
- **On hover/click, offer a "copy filename" button** in the row-details drawer
  (one click to clipboard is a frequent organizer action).

### 2b. Make the series and type filterable, not just searchable
Global search is powerful but undiscoverable for "show me all 2003 Satsang
lectures". Add:

- **A compact filter bar** (faceted filters) below the stats strip: **Series**,
  **Year**, **Item type**, **Format**, **Owned**. Each is a multi-select
  dropdown populated from distinct column values; selecting updates the active
  filter chips that already exist.
- **Quick-year range** (e.g. `198X` sorts as "c. 1980s" — already handled; a
  decade facet would group pre-2000 cleanly).

### 2c. Surface "work grouping" visually
Multi-part lectures and editions share a `work_id` but look like unrelated
rows today:

- **Subtle row-striping per work:** when consecutive rows share a `work_id`,
  give them a faint shared left border or alternating band so parts/editions
  read as a family at a glance.
- **A "collapse parts" toggle** in View settings that rolls a work's parts
  into one row (count badge "3 parts") and expands on click — useful for a
  high-level browse mode, with the current one-row-per-edition as the default
  "expanded" review mode.

### 2d. Linkify more cells consistently
URL columns already render links. Extend linkification to:

- **Catalogue code** (e.g. `LECTURE-2008-023`) could copy to clipboard or
  anchor-link to that row.
- **Series cell** → click to filter the sheet to that series.
- **Master ID / Work ID** in Expert mode → click to copy (IDs are copied into
  review notes constantly).

---

## 3. Review workspace

### 3a. A proper review queue / inbox
The review sheets are currently flat tables. Since almost every queue is at 0
(Official Discovery, New Work Review) and the rest are historical, the most
useful addition would be:

- **A "Needs your decision" view** that unions across review sheets any row
  whose `review_status` is not `approved`/`reviewed`/`promoted`, sorted oldest
  first. Today that's empty by design — but it becomes the single place a
  future Veritas refresh lands work.
- **Inline status badges** that are color-coded consistently: green =
  approved/promoted/matched, amber = pending/needs_review, red =
  excluded/rejected, grey = blank/not stated. The `statusClass()` helper
  already does most of this; audit it for contrast (AA) across themes.

### 3b. Diff/decision context on each row
Reviewers need to know *why* a row exists:

- In row-details, show a **"Provenance"** section at the top: raw row number
  linked to the Original Spreadsheet tab, the candidate key, the approval
  date/reason, and a link to the relevant `decisions/*.md` memo when one is
  referenced.
- For product relationships, show the **derived-vs-stored distinction**
  visually (a "primary (auto)" vs "related (reviewed)" badge) so reviewers
  trust the 336 derived rows and focus on the 7 hand-curated ones.

### 3c. Keyboard-driven review
For someone processing a queue:

- **`j`/`k`** to move between rows, **`e`** to open details, **`y`** to copy
  the filename/ID, **`/`** to focus search (the search box already exists;
  add a hotkey), **`?`** for a shortcut overlay.
- Preserve the existing arrow-key roving tabs for accessibility.

---

## 4. Visual design

### 4a. Tighter density by default, "expanded" on demand
The current default is already compact (`compactRows: true`). Good. Push it
further for the catalogue:

- **Row height ~28px**, 13px text, and a 1px hairline divider between rows.
- Reserve the "roomy/wrapped" mode (Expand everything) for deep review.
- Use the **carrier color dots** (DVD/CD/audiobook/streaming/book) in the
  Edition column instead of full badges — color is faster than text; the text
  stays in the tooltip and drawer.

### 4b. One neutral accent, used purposefully
The green accent (selection/hover) is good. Restrict color to:
- selection, the active tab, and primary links = green
- status badges = muted semantic colors (green/amber/red/grey)
- everything else = neutral grey/text

Avoid coloring arbitrary columns; the data itself should dominate.

### 4c. Empty states that guide action
Official Discovery and New Work Review already have empty-state cards. Make
them do something:

- Show the **last refresh date** and a link to the **Map Veritas Catalogue**
  action (even if it just links to the Actions tab on GitHub).
- Explain in one sentence what *would* land there and how to trigger it.

---

## 5. Performance and data

### 5a. Virtualization is fine; keep payloads lean
365 master rows is small. The 378 KB `master.json` and 326 KB
`product-relationships.json` are fine over broadband but heavy on mobile.

- The current per-fetch JSON is already split per tab, which is good.
- Optional: serve a **gzip/brotli-compressed** `master.json` (GitHub Pages
  supports this automatically if the file is compressed at build time, or rely
  on Pages' transparent compression — verify).
- Keep the full row object for the drawer, but the initial table columns
  don't need every field on every row. Not worth the complexity at 365 rows.

### 5b. Make the stats strip interactive
The five chips (365 records, 72 exclusions, 131 overrides, 343 relationships,
7 compilations) are currently display-only. Clicking a chip could:
- "365 records" → switch to Everything
- "72 exclusions" → switch to Master Exclusions
- "343 relationships" → switch to Product Relationships
etc. Cheap navigation win.

---

## 6. Suggested priority

| Priority | Item | Effort | Impact |
|---|---|---|---|
| **P0** | 2b faceted filters (Series/Year/Type/Format/Owned) | M | High — turns search into browsing |
| **P0** | 5b make stats chips clickable | XS | High — instant navigation |
| **P1** | 1b shorten tab labels / move review lanes to a menu | S | Medium — declutters the tab bar |
| **P1** | 2a monospace filename + copy button | S | Medium — reinforces lead column |
| **P1** | 4a tighter row density + carrier color dots | S | Medium — more rows on screen |
| **P2** | 2c work-group row striping / collapse parts | M | Medium — reveals edition model |
| **P2** | 1c persist sort/scroll/widths per tab | S | Medium — review ergonomics |
| **P2** | 3a "Needs your decision" inbox view | M | Medium–High when queues reopen |
| **P3** | 3c keyboard shortcuts (j/k/y/?) | S | Nice-to-have for power reviewers |
| **P3** | 1a nested column groups | M | Visual structure; adds Tabulator config |

None of these require catalogue-data changes; they are all frontend
(`docs/index.html`, `docs/app.js`, `docs/style.css`) plus optional Playwright
coverage. The 115 Python tests and six `--check` modes are unaffected.
