const { test, expect } = require('@playwright/test');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await page.locator('.tabulator-row').first().waitFor();
}

// Tabulator virtualizes the row DOM with maxHeight:100%, so read the active
// (post-filter) row count from the footer status that updateSearchStatus
// keeps in sync ("Showing: N" or "Showing: N of M").
async function activeRowCount(page) {
  const text = await page.locator('#search-status').textContent();
  const match = /Showing:\s*(\d+)/.exec(text || '');
  return match ? parseInt(match[1], 10) : 0;
}

test('faceted filters narrow the Everything view and add removable chips', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  // Filters are now hidden by default to save space. Turn them on.
  await page.locator('#facet-toggle-btn').click();

  // The facet bar is present only on the catalogue (Everything) view.
  await expect(page.locator('#facet-bar')).toBeVisible();

  const totalRows = await activeRowCount(page);
  expect(totalRows).toBe(365);

  // Select one series in the faceted Series dropdown (programmatic select +
  // change event, since a native multi-select would need Ctrl/Cmd).
  const seriesSelect = page.locator('#facet-series');
  await seriesSelect.locator('option', { hasText: 'Satsang Series' })
    .evaluate((el) => { el.selected = true; });
  await seriesSelect.dispatchEvent('change');

  // The active rows narrow and a removable chip appears.
  await expect.poll(activeRowCount.bind(null, page)).toBeLessThan(totalRows);
  await expect(page.locator('#filter-chips')).toContainText('Satsang Series');

  // Clicking the chip removes the filter and restores the full set.
  await page.locator('.filter-chip-removable').first().click();
  await expect.poll(activeRowCount.bind(null, page)).toBe(totalRows);
});

test('facet bar is hidden on non-catalogue views', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await page.getByRole('tab', { name: 'Original Spreadsheet' }).click();
  await waitForTable(page);
  await expect(page.locator('#facet-bar')).toBeHidden();
});

test('stats chips and task jump menu navigate to their sheets', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await expect(page.locator('#view-jump')).toBeVisible();
  await expect(page.locator('#view-jump optgroup[label="Catalogue"]')).toHaveCount(1);
  await expect(page.locator('#view-jump optgroup[label="Review workspace"]')).toHaveCount(1);
  await expect(page.locator('#view-jump optgroup[label="Sources"]')).toHaveCount(1);
  await page.locator('#view-jump').selectOption('manualLeads');
  await waitForTable(page);
  await expect(page.locator('#view-title')).toHaveText('Manual Leads');
  await page.locator('#view-jump').selectOption('master');
  await waitForTable(page);

  // Stats are hidden by default now to save space. Turn them on.
  await page.locator('#settings-btn').click();
  await page.locator('#show-stats-toggle').check();
  await page.locator('#settings-btn').click(); // close settings menu

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

test('row details use sections and return focus to the source row', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  const row = page.locator('#spreadsheet .tabulator-row').first();
  await row.click();
  await expect(page.locator('#row-details')).toBeVisible();
  await expect(page.locator('#close-row-details')).toBeFocused();
  await expect(page.locator('.row-details-section-title')).toContainText(['Identity', 'Ownership & status', 'Sources', 'Provenance']);
  await page.keyboard.press('Tab');
  await expect(page.locator('#copy-filename-btn')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.locator('#copy-id-btn')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.locator('#close-row-details')).toBeFocused();
  await page.locator('#close-row-details').click();
  await expect(page.locator('#row-details')).toBeHidden();
  await expect(row).toBeFocused();
});

test('keyboard slash focuses search', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await page.keyboard.press('/');
  await expect(page.locator('#global-search')).toBeFocused();
});
