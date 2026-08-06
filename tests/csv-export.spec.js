const { test, expect } = require('@playwright/test');
const fs = require('node:fs/promises');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await expect(page.locator('.tabulator-row').first()).toBeVisible();
}

test('CSV export downloads the whole active view even when filtered', async ({ page }) => {
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
  // Whole-sheet export: rows the search filter hides must still be exported.
  expect(csv).toContain('Satsang');
  expect(csv).toContain('Year-Month');
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

test('published catalogue views are read-only', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const cell = page.locator('.tabulator-cell[tabulator-field="title"]').first();
  await cell.dblclick();
  await expect(cell.locator('input, textarea, select')).toHaveCount(0);
  await expect(page.locator('#footer-note')).toContainText(/read-only/i);
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
  const expectedMasterCount = await page.evaluate(async () => {
    const rows = await fetch('/docs/master.json').then((response) => response.json());
    return rows.filter((row) => row.record_type === 'master').length;
  });
  const expectedTotalCount = await page.evaluate(async () => {
    const rows = await fetch('/docs/master.json').then((response) => response.json());
    return rows.length;
  });
  await reviewFilter.selectOption('master');
  await expect(page.locator('#search-status'))
    .toContainText(`Showing: ${expectedMasterCount} of ${expectedTotalCount}`);
  await expect(page.locator('#filter-chips')).toContainText('Curated master');

  const badges = page.locator('.tabulator-cell[tabulator-field="record_type"] .status-badge');
  expect(await badges.count()).toBeGreaterThan(0);
  for (const text of await badges.allTextContents()) {
    expect(text).toBe('Curated master');
  }
});

test('edition model columns render on the Everything tab', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  // Work + Edition columns exist (edition model, 2026-08-03).
  await expect(page.locator('.tabulator-col[tabulator-field="work_id"]').first()).toBeVisible();
  await expect(page.locator('.tabulator-col[tabulator-field="edition"]').first()).toBeVisible();

  // The raw format columns are hidden in favour of the merged Edition column.
  await expect(page.locator('.tabulator-col[tabulator-field="format"]')).toHaveCount(0);
  await expect(page.locator('.tabulator-col[tabulator-field="format_detail"]')).toHaveCount(0);

  // Narrow to one work family so the virtual-DOM window contains its rows:
  // the book row and its minted audiobook edition row share the work id.
  await page.getByRole('searchbox', { name: /search across all columns/i }).fill('w-truth-vs-falsehood');
  const workCells = page.locator('.tabulator-cell[tabulator-field="work_id"]');
  await expect(workCells.first()).toHaveText('w-truth-vs-falsehood');

  // The audiobook edition row renders with its merged edition label.
  // After filename proposal v4, edition still merges format + format_detail, e.g. "audiobook · Audiobook" and "book"
  const editionCells = page.locator('.tabulator-cell[tabulator-field="edition"]');
  await expect(editionCells.filter({ hasText: 'Audiobook' }).first()).toBeVisible();

  // The book row shows its own edition label.
  await expect(editionCells.filter({ hasText: 'book' }).first()).toBeVisible();
});
