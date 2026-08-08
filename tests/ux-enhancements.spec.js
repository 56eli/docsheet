const { test, expect } = require('@playwright/test');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await page.locator('.tabulator-row').first().waitFor();
}

test('faceted filters narrow the Everything view and add removable chips', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  // The facet bar is present only on the catalogue (Everything) view.
  await expect(page.locator('#facet-bar')).toBeVisible();

  const totalRows = await page.locator('#spreadsheet .tabulator-row').count();
  expect(totalRows).toBeGreaterThan(100);

  // Select one series in the faceted Series dropdown.
  const seriesSelect = page.locator('#facet-series');
  const option = seriesSelect.locator('option', { hasText: 'Satsang Series' });
  await option.evaluate((el) => { el.selected = true; });
  await seriesSelect.dispatchEvent('change');

  // The visible rows narrow and a removable chip appears.
  await expect.poll(async () => page.locator('#spreadsheet .tabulator-row').count()).toBeLessThan(totalRows);
  await expect(page.locator('#filter-chips')).toContainText('Satsang Series');

  // Clicking the chip removes the filter and restores the full set.
  await page.locator('.filter-chip-removable').first().click();
  await expect.poll(async () => page.locator('#spreadsheet .tabulator-row').count()).toBe(totalRows);
});

test('facet bar is hidden on non-catalogue views', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await page.getByRole('tab', { name: 'Original Spreadsheet' }).click();
  await waitForTable(page);
  await expect(page.locator('#facet-bar')).toBeHidden();
});

test('stats chips navigate to their sheets', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await page.locator('.stat-chip[data-jump="productRelationships"]').click();
  await waitForTable(page);
  await expect(page.locator('#view-title')).toHaveText('Product Relationships');
});

test('compact CM badge carries the full Curated master tooltip', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  const badge = page.locator('.tabulator-cell[tabulator-field="record_type"] .status-badge').first();
  await expect(badge).toHaveText('CM');
  await expect(badge).toHaveAttribute('title', 'Curated master');
});

test('proposed filename renders with a muted extension', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  const cell = page.locator('.tabulator-cell[tabulator-field="proposed_filename"]').first();
  await expect(cell.locator('.ext')).toContainText('.mp4');
});

test('keyboard slash focuses search', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await page.keyboard.press('/');
  await expect(page.locator('#global-search')).toBeFocused();
});
