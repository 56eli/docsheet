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

test("ODS export creates valid OpenDocument Spreadsheet archives with colored groupings", async () => {
  const { createOdsArchive } = await import("../docs/js/ods-export.js");
  const sample = [
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

  const getRowBlockId = (row) => (row.series === "Books" ? "books" : "lecture-highlights");
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
