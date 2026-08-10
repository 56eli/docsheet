import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

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

const { buildColumns } = await import("../docs/js/columns.js");

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
    "",
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
