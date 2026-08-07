const { test, expect } = require('@playwright/test');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await page.locator('.tabulator-row').first().waitFor();
}

// The Everything view opens visitor-first (owner directive 2026-08-07):
// technical columns (Master ID, Work, Legacy ID, provenance) are hidden until
// the "Expert columns" toggle is switched on. Specs that assert those columns
// enable them first.
async function enableExpertColumns(page) {
  const toggle = page.locator('#expert-toggle-btn');
  await expect(toggle).toBeVisible();
  if ((await toggle.getAttribute('aria-pressed')) !== 'true') {
    await toggle.click();
    await expect(toggle).toHaveAttribute('aria-pressed', 'true');
  }
}

async function columnFields(page) {
  return page.locator('#spreadsheet .tabulator-col[tabulator-field]').evaluateAll(
    (cols) => cols.map((col) => col.getAttribute('tabulator-field')),
  );
}

function uuidCellInRow(page, rowIndex) {
  return page.locator('#spreadsheet .tabulator-row').nth(rowIndex)
    .locator('.tabulator-cell[tabulator-field="uuid"]');
}

test('Everything view parks the Work column right after Legacy ID', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await enableExpertColumns(page);

  const fields = await columnFields(page);
  const work = fields.indexOf('work_id');
  const legacy = fields.indexOf('legacy_tempid');

  expect(work, 'work_id column must exist').toBeGreaterThan(-1);
  expect(legacy, 'legacy_tempid column must exist').toBeGreaterThan(-1);
  expect(work).toBe(legacy + 1);
  // Dropped by owner ruling 2026-08-07 (always-empty placeholders): the Work
  // column used to be followed by location_physical; neither it nor
  // reference_url_2 may reappear silently.
  expect(fields.indexOf('location_physical')).toBe(-1);
  expect(fields.indexOf('location_digital')).toBe(-1);
  expect(fields.indexOf('location_streaming')).toBe(-1);
  expect(fields.indexOf('reference_url_2')).toBe(-1);
});

test('columns are sized to their widest rendered entry', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await enableExpertColumns(page);

  const widthOf = (field) => page
    .locator(`#spreadsheet .tabulator-col[tabulator-field="${field}"]`)
    .evaluate((col) => col.getBoundingClientRect().width);

  // Measured widths must actually be applied (no collapsed or oversized columns):
  const [title, uuid, series, notes] = await Promise.all([
    widthOf('title'), widthOf('uuid'), widthOf('series'), widthOf('notes'),
  ]);
  expect(title).toBeGreaterThan(150);
  expect(title).toBeLessThanOrEqual(560);
  expect(notes).toBeLessThanOrEqual(560);
  expect(uuid, 'short ID column must stay narrow').toBeLessThan(title);
  expect(series, 'series column must fit the longest series name').toBeGreaterThan(180);
});

test('Master ID column sorts numerically, not lexically', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await enableExpertColumns(page);

  const uuidHeader = page.locator('#spreadsheet .tabulator-col[tabulator-field="uuid"]');

  // Ascending: 1, 2, 3 … — a lexical string sort would show 1, 10, 100.
  await uuidHeader.click();
  await expect(uuidHeader).toHaveAttribute('aria-sort', 'ascending');
  await expect(uuidCellInRow(page, 0)).toHaveText('1');
  await expect(uuidCellInRow(page, 1)).toHaveText('2');
  await expect(uuidCellInRow(page, 2)).toHaveText('3');

  // Descending: the highest Master ID first (IDs run 1-372; 246/249/264/281/284/302
  // are retired, so max is 372 after the 2026-08-07 promotions 362-372).
  // Empty candidate IDs must stay pinned to the bottom, not jump to the top.
  await uuidHeader.click();
  await expect(uuidHeader).toHaveAttribute('aria-sort', 'descending');
  await expect(uuidCellInRow(page, 0)).toHaveText('372');
  await expect(uuidCellInRow(page, 1)).toHaveText('371');
});

test('Everything view opens visitor-first and the Expert toggle reveals technical columns', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  // Tabulator keeps invisible columns' header nodes in the DOM, so hidden
  // state is asserted with toBeHidden (visibility), never toHaveCount(0).
  const header = (field) => page.locator(`#spreadsheet .tabulator-col[tabulator-field="${field}"]`).first();

  // First sight = product facts: the technical extras stay out of the way.
  for (const field of ['uuid', 'work_id', 'legacy_tempid', 'proposed_filename', 'year_source']) {
    await expect(header(field), `${field} must be hidden until Expert mode`).toBeHidden();
  }
  for (const field of ['record_type', 'title', 'series', 'edition', 'year_month', 'source_url_veritas', 'source_url_amazon', 'reference_url_1', 'notes']) {
    await expect(header(field), `${field} must be visible at first sight`).toBeVisible();
  }

  // The toggle reveals the technical columns and can hide them again.
  await page.locator('#expert-toggle-btn').click();
  await expect(header('uuid')).toBeVisible();
  await expect(header('work_id')).toBeVisible();
  await page.locator('#expert-toggle-btn').click();
  await expect(header('uuid')).toBeHidden();
});
