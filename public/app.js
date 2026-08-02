/* ==========================================================================
   Live Spreadsheet — app.js
   Loads public/data.json (+ public/meta.json) and renders it as an
   interactive Tabulator table: sortable headers, global live search,
   pagination (25/page), inline editing, CSV export, column resizing,
   responsive collapsing, dark mode with localStorage persistence.
   ========================================================================== */
(function () {
  "use strict";

  const PAGE_SIZE = 25;
  const STORAGE_KEY = "docsheet-dark-mode";

  const $ = (id) => document.getElementById(id);
  const searchInput = $("global-search");
  const exportBtn = $("export-btn");
  const darkToggle = $("dark-toggle");
  const footerStats = $("footer-stats");
  const footerUpdated = $("footer-updated");
  const footerNote = $("footer-note");

  let table = null;
  let allData = [];
  let metaLoaded = false;

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

  async function loadData() {
    const res = await fetch("data.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allData = await res.json();

    // Fallback timestamp: the file's Last-Modified header, when meta.json
    // could not be read (e.g. served from a static host without meta.json).
    if (!metaLoaded) {
      const lastModified = res.headers.get("Last-Modified");
      if (lastModified) {
        footerUpdated.innerHTML =
          `Last Updated: <span class="updated">${formatTimestamp(lastModified)}</span>`;
      } else {
        footerUpdated.textContent = "Last Updated: Unknown";
      }
    }
    footerStats.textContent = `Total Rows: ${allData.length}`;
  }

  /* ------------------------------------------------------------------ *
   *  Column definitions (built from the JSON keys — order preserved)
   * ------------------------------------------------------------------ */
  function looksLikeUrl(value) {
    return typeof value === "string" && /^https?:\/\//i.test(value.trim());
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
        title: key,
        field: key,
        headerSort: true,          // click header to sort asc/desc
        resizable: true,           // drag column edge to resize
        minWidth: 110,
        editor: "input",           // double-click any cell to edit
        tooltip: (e, cell) => String(cell.getValue() ?? ""),
      };

      // Presentation-only nicety: render URL-heavy columns as clickable links.
      // This does NOT modify the underlying data.
      if (urlRatio >= 0.6) {
        col.formatter = "link";
        col.formatterParams = { target: "_blank", urlPrefix: "" };
      }
      return col;
    });
  }

  /* ------------------------------------------------------------------ *
   *  Tabulator init
   * ------------------------------------------------------------------ */
  function initTable(data) {
    table = new Tabulator($("spreadsheet"), {
      data,
      columns: buildColumns(data),
      layout: "fitColumns",
      maxHeight: "100%",           // header stays frozen while rows scroll
      placeholder: "No data found",
      /* keep the table sized to its container on resize */
      renderComplete: () => fitTableToContainer(),
      /* sorting */
      headerSort: true,
      /* pagination — 25 rows per page by default */
      pagination: true,
      paginationSize: PAGE_SIZE,
      paginationSizeSelector: [10, 25, 50, 100],
      paginationCounter: "rows",
      /* columns */
      resizableColumns: true,
      movableColumns: true,        // drag headers to reorder (bonus)
      responsiveLayout: "collapse",// stacks columns on narrow screens
      /* editing */
      selectableRows: false,
    });

    table.on("cellEdited", (cell) => {
      const row = cell.getRow().getData();
      const label = `${cell.getColumn().getField()}`;
      const id = row.tempid || row.uuid || `row ${cell.getRow().getPosition(true)}`;
      flashNote(`✎ Edited “${label}” (${id}) — local only, not saved back to the CSV`);
    });
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
    if (!table) return;
    const q = query.trim().toLowerCase();
    if (!q) {
      table.clearFilter();
      table.setPage(1);
      return;
    }
    table.setFilter((data) =>
      Object.values(data).some(
        (v) => v !== null && v !== undefined && String(v).toLowerCase().includes(q)
      )
    );
    table.setPage(1);
  }

  /* ------------------------------------------------------------------ *
   *  Export CSV (current filtered view)
   * ------------------------------------------------------------------ */
  function exportCsv() {
    if (!table) return;
    table.download("csv", "hawkins-archive.csv", { delimiter: ",", bom: true });
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
  async function boot() {
    initDarkMode();
    searchInput.addEventListener("input", debounce((e) => applySearch(e.target.value), 250));
    exportBtn.addEventListener("click", exportCsv);
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { searchInput.value = ""; applySearch(""); }
    });

    try {
      await loadMeta();          // fire and await footer info (fast, optional)
    } catch (err) {
      footerStats.textContent = "Total Rows: —";
      footerUpdated.textContent = "Last Updated: —";
    }

    try {
      const data = await loadData();
      initTable(data);
      console.info(`[docsheet] Loaded ${data.length} rows`);
    } catch (err) {
      console.error("[docsheet] Failed to load data.json:", err);
      $("spreadsheet").innerHTML =
        '<div class="load-error">Could not load data.json — make sure the site is served over HTTP ' +
        '(e.g. GitHub Pages or `python -m http.server`), not opened directly from disk.</div>';
      footerStats.textContent = "Total Rows: —";
      footerUpdated.textContent = "Last Updated: —";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
