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
