const { test, expect } = require('@playwright/test');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await page.locator('.tabulator-row').first().waitFor();
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

test('Everything view parks the Work column between Legacy ID and Location Physical', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const fields = await columnFields(page);
  const work = fields.indexOf('work_id');
  const legacy = fields.indexOf('legacy_tempid');
  const physical = fields.indexOf('location_physical');

  expect(work, 'work_id column must exist').toBeGreaterThan(-1);
  expect(legacy, 'legacy_tempid column must exist').toBeGreaterThan(-1);
  expect(physical, 'location_physical column must exist').toBeGreaterThan(-1);
  expect(work).toBe(legacy + 1);
  expect(physical).toBe(work + 1);
});

test('columns are sized to their widest rendered entry', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

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

  const uuidHeader = page.locator('#spreadsheet .tabulator-col[tabulator-field="uuid"]');

  // Ascending: 1, 2, 3 … — a lexical string sort would show 1, 10, 100.
  await uuidHeader.click();
  await expect(uuidHeader).toHaveAttribute('aria-sort', 'ascending');
  await expect(uuidCellInRow(page, 0)).toHaveText('1');
  await expect(uuidCellInRow(page, 1)).toHaveText('2');
  await expect(uuidCellInRow(page, 2)).toHaveText('3');

  // Descending: the highest Master ID first (IDs run 1-361; 249 and 264 are
  // retired, so max is 361 after academic promotion 359-361). Empty candidate IDs must stay pinned to the
  // bottom, not jump to the top.
  await uuidHeader.click();
  await expect(uuidHeader).toHaveAttribute('aria-sort', 'descending');
  await expect(uuidCellInRow(page, 0)).toHaveText('361');
  await expect(uuidCellInRow(page, 1)).toHaveText('360');
});
