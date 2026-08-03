const { test, expect } = require('@playwright/test');
const fs = require('node:fs/promises');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await expect(page.locator('.tabulator-row').first()).toBeVisible();
}

test('CSV export downloads the active filtered spreadsheet view', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await page.getByRole('searchbox', { name: /search across all columns/i }).fill('Causality');
  await expect(page.locator('#search-status')).toContainText(/Showing: \d+ of \d+/);

  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: /export csv/i }).click(),
  ]);

  expect(download.suggestedFilename()).toBe('hawkins-everything.csv');
  const downloadPath = await download.path();
  expect(downloadPath).toBeTruthy();

  const csv = await fs.readFile(downloadPath, 'utf8');
  expect(csv).toContain('Causality');
  expect(csv).toContain('Master ID');
});

test('CSV export uses the selected view filename', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await page.getByRole('tab', { name: 'Original Spreadsheet' }).click();
  await waitForTable(page);

  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: /export csv/i }).click(),
  ]);

  expect(download.suggestedFilename()).toBe('hawkins-original-spreadsheet.csv');
  const downloadPath = await download.path();
  expect(downloadPath).toBeTruthy();

  const csv = await fs.readFile(downloadPath, 'utf8');
  const lowerCsv = csv.toLowerCase();
  expect(lowerCsv).toContain('tempid');
  expect(lowerCsv).toContain('title');
});

test('Everything view separates curated master records from candidates', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  // The provenance column must exist and be frozen at the front of the sheet.
  await expect(page.locator('.tabulator-col[tabulator-field="record_type"]')).toBeVisible();
  await expect(page.locator('.tabulator-cell[tabulator-field="record_type"]').first())
    .toContainText(/Curated master|Candidate/);

  // The review filter must offer the provenance values.
  const reviewFilter = page.locator('#review-filter');
  await expect(reviewFilter).toBeVisible();
  await expect(reviewFilter.locator('option[value="master"]')).toHaveCount(1);
  await expect(reviewFilter.locator('option[value="candidate_veritas"]')).toHaveCount(1);

  // Filtering to curated master must exclude every candidate row.
  await reviewFilter.selectOption('master');
  await expect(page.locator('#search-status')).toContainText('Showing: 308 of 344');
  await expect(page.locator('#filter-chips')).toContainText('Curated master');

  const badges = page.locator('.tabulator-cell[tabulator-field="record_type"] .status-badge');
  expect(await badges.count()).toBeGreaterThan(0);
  for (const text of await badges.allTextContents()) {
    expect(text).toBe('Curated master');
  }
});
