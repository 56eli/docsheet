import assert from "node:assert/strict";
import { mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import test, { after } from "node:test";

class MockNode {
  constructor(tagName = "") {
    this.tagName = tagName;
    this.children = [];
    this.className = "";
    this.textContent = "";
    this.title = "";
  }

  append(...children) {
    this.children.push(...children);
  }

  replaceChildren(...children) {
    this.children = [...children];
  }
}

globalThis.document = {
  createElement(tagName) {
    if (tagName === "canvas") {
      return {
        getContext: () => ({
          font: "",
          measureText: (text) => ({ width: String(text).length * 8 }),
        }),
      };
    }
    return new MockNode(tagName);
  },
  createDocumentFragment() {
    return new MockNode("fragment");
  },
  createTextNode(text) {
    const node = new MockNode("text");
    node.textContent = String(text);
    return node;
  },
};

// Browser cache-busting query strings are valid URL identities, but Node's
// module mode differs across CI platforms. Mirror the browser modules into an
// explicit ESM temp package and strip only the query suffixes for this runtime
// unit test; the Python delivery contract independently verifies every real
// import edge and hash in the committed graph.
const sourceModules = new URL("../docs/js/", import.meta.url);
const moduleSandbox = await mkdtemp(join(tmpdir(), "docsheet-frontend-modules-"));
await writeFile(join(moduleSandbox, "package.json"), '{"type":"module"}\n');
for (const filename of await readdir(sourceModules)) {
  if (!filename.endsWith(".js")) continue;
  const source = await readFile(new URL(filename, sourceModules), "utf8");
  await writeFile(join(moduleSandbox, filename), source.replace(/\?v=[0-9a-f]{12}/g, ""));
}
after(() => rm(moduleSandbox, { recursive: true, force: true }));

const { buildColumns } = await import(pathToFileURL(join(moduleSandbox, "columns.js")).href);

function editionFormatter() {
  const seed = {
    uuid: "373",
    work_id: "w-power-vs-force",
    format: "book",
    format_detail: "Hardcover",
    edition: "book · Hardcover",
  };
  const columns = buildColumns(
    [seed],
    "master",
    () => true,
    () => [],
    (text) => document.createTextNode(text),
    () => "",
  );
  const column = columns.find(({ field }) => field === "edition");
  assert.ok(column, "edition column must be generated");
  assert.equal(typeof column.formatter, "function");
  return column.formatter;
}

function format(formatter, row) {
  return formatter({
    getValue: () => row.edition,
    getRow: () => ({ getData: () => row }),
  });
}

// The intended, owner-reviewed REVISION1 block palette. Keeping the expected
// color values explicit here makes them reviewable; the set of production
// block ids is derived from the committed block map below so coverage cannot
// drift from the published data.
const EXPECTED_BLOCK_COLORS = {
  "lectures-2002-2011": { border: "#059669", bg: "#EAF6F2" },
  discussion: { border: "#E11D48", bg: "#FCECEF" },
  satsang: { border: "#D97706", bg: "#FDF4E8" },
  "on-the-road": { border: "#0D9488", bg: "#EBF7F6" },
  "volume-series": { border: "#6366F1", bg: "#F1F2FE" },
  "office-series": { border: "#0284C7", bg: "#E7F4FC" },
  books: { border: "#7C3AED", bg: "#F4EEFE" },
  "transcription-books": { border: "#C026D3", bg: "#FAF0FC" },
  "media-misc": { border: "#71717A", bg: "#F3F3F3" },
  "lecture-highlights": { border: "#EA580C", bg: "#FEEFE8" },
  "fran-grace": { border: "#BE123C", bg: "#FAECEF" },
  undecided: { border: "#E2E8F0", bg: "#FFFFFF" },
};

// Derive the real production block ids from the committed published block
// map (uuid -> block_id), never from assumed names.
const catalogueBlockMap = JSON.parse(
  await readFile(new URL("../docs/catalogue-block-map.json", import.meta.url), "utf8"),
);
const productionBlocks = [...new Set(Object.values(catalogueBlockMap))].sort();

function odsBlockStyleXml(content, blockId) {
  const marker = `style:name="ce-block-left-${blockId}"`;
  const start = content.indexOf(marker);
  assert.notEqual(start, -1, `ODS must define the left style for block "${blockId}"`);
  const close = content.indexOf("/>", start);
  assert.notEqual(close, -1, `ODS left style for "${blockId}" must close with "/>"`);
  return content.slice(start, close);
}

test("removed overview UI has no dormant JavaScript or CSS", async () => {
  const [app, style] = await Promise.all([
    readFile(new URL("../docs/app.js", import.meta.url), "utf8"),
    readFile(new URL("../docs/style.css", import.meta.url), "utf8"),
  ]);
  const removedTokens = [
    "catalogue-intro", "hero-dismiss", "overview-btn", "overview-cards",
    "series-strip-list", "review-nav-toggle", "review-nav-groups",
    "show-stats-toggle", "stats-strip", "stat-chip",
  ];
  for (const token of removedTokens) {
    assert.equal(app.includes(token), false, `${token} must not remain in app.js`);
    assert.equal(style.includes(token), false, `${token} must not remain in style.css`);
  }
});

test("column formatters read the current search query on every redraw", () => {
  let query = "";
  const seenQueries = [];
  const row = { title: "Power vs Force" };
  const columns = buildColumns(
    [row],
    "master",
    () => true,
    () => [],
    (text, currentQuery) => {
      seenQueries.push(currentQuery);
      return document.createTextNode(text);
    },
    () => query,
  );
  const formatter = columns.find(({ field }) => field === "title").formatter;
  const cell = { getValue: () => row.title };

  formatter(cell);
  query = "power";
  formatter(cell);

  assert.deepEqual(seenQueries, ["", "power"]);
});

test("edition formatter imports and executes the extra-edition helper", () => {
  const formatter = editionFormatter();
  const extra = format(formatter, {
    uuid: "373",
    work_id: "w-power-vs-force",
    format: "book",
    edition: "book · Hardcover",
  });

  assert.ok(extra instanceof MockNode);
  const extraBadge = extra.children.find(
    (node) => node instanceof MockNode && node.className === "extra-edition-badge",
  );
  assert.ok(extraBadge, "Power vs. Force row 373 must render its Extra badge");
  assert.equal(extraBadge.textContent, "Extra");

  const regular = format(formatter, {
    uuid: "286",
    work_id: "w-power-vs-force",
    format: "book",
    edition: "book · Paperback",
  });
  assert.equal(
    regular.children.some(
      (node) => node instanceof MockNode && node.className === "extra-edition-badge",
    ),
    false,
    "the primary edition must not receive the Extra badge",
  );
});

test("block-map fallback equals the approved display order for all masters", async () => {
  // In Node the block-map fetch cannot resolve a relative URL, so the
  // module-level _catalogueBlockMap stays empty and getRowBlockId exercises
  // the embedded FALLBACK_BLOCK_MAP snapshot. Every approved row of
  // data/catalogue_display_order.csv must classify to its own block — a
  // drift (e.g. a display-order change without refreshing the snapshot)
  // fails here, and a failed block-map fetch in the browser can no longer
  // strip the REVISION1 groupings (incl. the 201-row lectures block).
  const { getRowBlockId } = await import("../docs/js/formatters.js");
  const csv = await readFile(
    new URL("../data/catalogue_display_order.csv", import.meta.url),
    "utf8",
  );
  const lines = csv.split(/\r?\n/).slice(1);
  let checked = 0;
  for (const line of lines) {
    if (!line.trim()) continue;
    const [uuid, blockId] = line.split(",");
    if (!uuid || !blockId) continue;
    assert.equal(
      getRowBlockId({ uuid: uuid.trim() }),
      blockId.trim(),
      `approved display-order uuid ${uuid.trim()} must map to its block`,
    );
    checked += 1;
  }
  assert.ok(checked >= 363, `expected >=363 approved rows, checked ${checked}`);
});

test("ODS export creates valid OpenDocument Spreadsheet archives with colored groupings", async () => {
  const { createOdsArchive } = await import("../docs/js/ods-export.js");
  const sample = [
    {
      uuid: 99,
      work_id: "w-lecture",
      title: "Lecture Series Sample",
      series: "Lecture Series",
      year_month: "2002-01",
      notes: "",
    },
    {
      uuid: 100,
      work_id: "w-power-vs-force",
      title: "Power vs. Force",
      series: "Books",
      year_month: "1995",
      notes: "Seminal work",
    },
    {
      uuid: 101,
      work_id: "w-healing-and-recovery",
      title: "Healing and Recovery",
      series: "Lecture Highlights",
      year_month: "2009",
      notes: "",
    },
  ];

  const getRowBlockId = (row) => {
    if (row.series === "Books") return "books";
    if (row.series === "Lecture Series") return "lectures-2002-2011";
    return "lecture-highlights";
  };
  const archive = createOdsArchive(sample, "master", getRowBlockId);

  assert.ok(archive instanceof Uint8Array, "createOdsArchive must return Uint8Array");
  assert.equal(archive[0], 0x50, "must start with PK signature (0x50)");
  assert.equal(archive[1], 0x4b, "must start with PK signature (0x4b)");
  assert.equal(archive[2], 0x03, "must start with PK signature (0x03)");
  assert.equal(archive[3], 0x04, "must start with PK signature (0x04)");

  const text = new TextDecoder().decode(archive);
  assert.ok(text.includes("application/vnd.oasis.opendocument.spreadsheet"), "must contain uncompressed mimetype");
  assert.ok(text.includes("META-INF/manifest.xml"), "must contain manifest path");
  assert.ok(text.includes("styles.xml"), "must contain styles path");
  assert.ok(text.includes("content.xml"), "must contain content path");

  // Verify REVISION1 block background colors are in content.xml
  assert.ok(text.includes("#059669"), "must include Lecture Series block border color (#059669)");
  assert.ok(text.includes("#EAF6F2"), "must include Lecture Series background tint (#EAF6F2)");
  assert.ok((text.match(/table:style-name="ce-block-left-lectures-2002-2011"/g) || []).length >= 1,
    "a Lecture Series data row must use the exact published block style");
  assert.ok(text.includes("#7C3AED"), "must include Books block border color (#7C3AED)");
  assert.ok(text.includes("#F4EEFE"), "must include Books block background tint (#F4EEFE)");
  assert.ok(text.includes("#EA580C"), "must include Lecture Highlights block border (#EA580C)");
  assert.ok(text.includes("#FEEFE8"), "must include Lecture Highlights block background (#FEEFE8)");

  // Verify humanized column headers are in content.xml
  assert.ok(text.includes("Master ID"), "must export humanized header 'Master ID'");
  assert.ok(text.includes("Work"), "must export humanized header 'Work'");
  assert.ok(text.includes("Power vs. Force"), "must export string cell value");
  assert.ok(text.includes('office:value-type="float" office:value="100"'), "must export numeric cell value");
});


test("XLSX export creates a styled Excel workbook with frozen header and filters", async () => {
  const { createXlsxArchive } = await import("../docs/js/ods-export.js");
  const archive = createXlsxArchive([
    { uuid: "001", title: "=Unsafe title", series: "Books", year_month: "1995" },
    { uuid: "002", title: "Healing & Recovery", series: "Lecture Highlights", year_month: "2009" },
  ], "master", (row) => row.series === "Books" ? "books" : "lecture-highlights");
  assert.ok(archive instanceof Uint8Array);
  assert.deepEqual([...archive.slice(0, 4)], [0x50, 0x4b, 0x03, 0x04]);
  const text = new TextDecoder().decode(archive);
  assert.ok(text.includes("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"));
  assert.ok(text.includes("xl/worksheets/sheet1.xml"));
  assert.ok(text.includes('state="frozen"'));
  assert.ok(text.includes("<autoFilter"));
  assert.ok(text.includes("FF7C3AED") || text.includes("FFF4EEFE"));
  assert.ok(text.includes("=Unsafe title"), "inline strings must preserve the displayed value");
  assert.ok(!text.includes("<f>"), "text values must never become Excel formulas");
});

test("JSON and TSV exports preserve structured values and neutralise formulas", async () => {
  const { createJsonExport, createTsv } = await import("../docs/js/ods-export.js");
  const rows = [{ uuid: "001", title: "=2+2", notes: "Tab\there\nnext", owned: false }];
  const payload = JSON.parse(createJsonExport(rows, "master"));
  assert.equal(payload.schema_version, 1);
  assert.equal(payload.view, "master");
  assert.equal(payload.row_count, 1);
  assert.equal(payload.rows[0].uuid, "001");
  assert.equal(payload.rows[0].owned, false);

  const tsv = createTsv(rows, "master");
  assert.ok(tsv.startsWith("\uFEFF"), "TSV must include a UTF-8 BOM");
  assert.ok(tsv.includes("'=2+2"), "formula-like cells must be neutralised");
  assert.ok(tsv.includes('"Tab\there\nnext"'), "tabs and newlines must be quoted");
  assert.ok(tsv.endsWith("\r\n"));
});

test("export block styles cover every production block with the intended REVISION1 palette", async () => {
  const { EXPORT_BLOCK_STYLES } = await import("../docs/js/ods-export.js");
  const styleKeys = Object.keys(EXPORT_BLOCK_STYLES).sort();

  // Every block id present in the published block map must have an export
  // style. This fails loudly when a production block is added or renamed
  // without updating the export palette.
  for (const blockId of productionBlocks) {
    assert.ok(
      styleKeys.includes(blockId),
      `production block "${blockId}" is missing an export style`,
    );
  }
  // No export style may exist without a matching production block. This fails
  // when a production block is removed (or renamed) without removing/updating
  // the now-orphaned export style.
  for (const blockId of styleKeys) {
    assert.ok(
      productionBlocks.includes(blockId),
      `export style "${blockId}" has no corresponding production block`,
    );
  }
  // The committed export palette must exactly match the reviewable intended
  // palette (colors are explicit here; coverage is derived from the map above).
  assert.deepEqual(EXPORT_BLOCK_STYLES, EXPECTED_BLOCK_COLORS);
});

test("ODS export colors every production block and falls back to undecided for unknown blocks", async () => {
  const { createOdsArchive } = await import("../docs/js/ods-export.js");
  const rows = productionBlocks.map((blockId) => ({
    uuid: blockId,
    title: `Row for ${blockId}`,
    series: blockId,
  }));
  const archive = createOdsArchive(rows, "master", (row) => row.series);
  const text = new TextDecoder().decode(archive);

  for (const blockId of productionBlocks) {
    const colors = EXPECTED_BLOCK_COLORS[blockId];
    // A data row must reference the exact block-specific left style.
    assert.ok(
      text.includes(`table:style-name="ce-block-left-${blockId}"`),
      `ODS data row for production block "${blockId}" must use its exact left style`,
    );
    // The block style must declare the intended border and background colors.
    const styleXml = odsBlockStyleXml(text, blockId);
    assert.ok(
      styleXml.includes(`fo:background-color="${colors.bg}"`),
      `ODS style "${blockId}" must use background ${colors.bg}`,
    );
    assert.ok(
      styleXml.includes(`fo:border-left="0.04in solid ${colors.border}"`),
      `ODS style "${blockId}" must use border-left ${colors.border}`,
    );
  }

  // Unknown block ids must safely fall back to the undecided style, and no
  // style may be minted for the unknown id.
  const unknownOnly = createOdsArchive(
    [{ uuid: "x", title: "X", series: "totally-unknown-block" }],
    "master",
    (row) => row.series,
  );
  const unknownText = new TextDecoder().decode(unknownOnly);
  assert.ok(
    unknownText.includes('table:style-name="ce-block-left-undecided"'),
    "ODS unknown block id must fall back to the undecided style",
  );
  assert.ok(
    !unknownText.includes("ce-block-left-totally-unknown-block"),
    "ODS must not mint a style for an unknown block id",
  );
});

test("XLSX export colors every production block and falls back to undecided for unknown blocks", async () => {
  const { createXlsxArchive, EXPORT_BLOCK_STYLES } = await import("../docs/js/ods-export.js");
  const styleKeys = Object.keys(EXPORT_BLOCK_STYLES);

  const rows = productionBlocks.map((blockId) => ({
    uuid: blockId,
    title: `Row for ${blockId}`,
    series: blockId,
  }));
  const archive = createXlsxArchive(rows, "master", (row) => row.series);
  const text = new TextDecoder().decode(archive);

  // Parse the fills from styles.xml. Order: [none, gray125, header(1A1A1A),
  // blocks...], so block i lives at fillColors[i + 1].
  const styleSheet = text.slice(text.indexOf("<styleSheet"), text.indexOf("</styleSheet>"));
  const fillColors = [...styleSheet.matchAll(/fgColor rgb="FF([0-9A-F]{6})"/g)].map((m) => m[1]);
  assert.ok(
    fillColors.length >= productionBlocks.length + 1,
    "XLSX styles must include a fill for every production block plus the header",
  );

  rows.forEach((row, i) => {
    const bi = styleKeys.indexOf(row.series);
    assert.notEqual(bi, -1, `XLSX must style production block "${row.series}"`);
    // The first data cell of this row must carry the exact style index for its block.
    const expectedStyle = 2 + bi;
    assert.ok(
      text.includes(`<c r="A${i + 2}" s="${expectedStyle}"`),
      `XLSX row for production block "${row.series}" must use style index ${expectedStyle}`,
    );
    // That style's fill must be the intended background color.
    assert.equal(
      fillColors[bi + 1],
      EXPECTED_BLOCK_COLORS[row.series].bg.slice(1),
      `XLSX fill for "${row.series}" must be ${EXPECTED_BLOCK_COLORS[row.series].bg}`,
    );
  });

  // Unknown block ids fall back to the undecided style index.
  const undecidedIndex = 2 + styleKeys.indexOf("undecided");
  const unknownOnly = createXlsxArchive(
    [{ uuid: "x", title: "X", series: "totally-unknown-block" }],
    "master",
    (row) => row.series,
  );
  const unknownText = new TextDecoder().decode(unknownOnly);
  assert.ok(
    unknownText.includes(`<c r="A2" s="${undecidedIndex}"`),
    "XLSX unknown block id must fall back to the undecided style index",
  );
});
