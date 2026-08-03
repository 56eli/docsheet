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
