const { test, expect } = require('@playwright/test');
const fs = require('node:fs/promises');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await expect(page.locator('.tabulator-row').first()).toBeVisible();
}

// The Everything view opens visitor-first (owner directive 2026-08-07);
// exports follow the visible columns, so specs asserting technical header
// names (e.g. "Master ID") switch Expert columns on first.
async function enableExpertColumns(page) {
  const toggle = page.locator('#expert-toggle-btn');
  await expect(toggle).toBeVisible();
  if ((await toggle.getAttribute('aria-pressed')) !== 'true') {
    await toggle.click();
    await expect(toggle).toHaveAttribute('aria-pressed', 'true');
  }
}

test('CSV export downloads the whole active view even when filtered', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await enableExpertColumns(page);

  await page.getByRole('searchbox', { name: /search across all columns/i }).fill('Causality');
  await expect(page.locator('#search-status')).toContainText(/Showing: \d+ of \d+/);

  await page.locator('#export-btn').click();
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.locator('#export-csv-btn').click(),
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

  // The Original Spreadsheet view was retired (2026-08-10); use a review sheet
  // to prove the export filename follows the active view.
  await page.locator('#view-jump').selectOption('manualLeads');
  await waitForTable(page);

  await page.locator('#export-btn').click();
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.locator('#export-csv-btn').click(),
  ]);

  expect(download.suggestedFilename()).toBe('hawkins-manual-leads.csv');
  const downloadPath = await download.path();
  expect(downloadPath).toBeTruthy();

  const csv = await fs.readFile(downloadPath, 'utf8');
  const lowerCsv = csv.toLowerCase();
  // Export headers are humanized column titles (e.g. "Title", "Lead Status").
  expect(lowerCsv).toContain('title');
  expect(lowerCsv).toContain('lead status');
});

test('published catalogue views are read-only', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const cell = page.locator('.tabulator-cell[tabulator-field="proposed_filename"]').first();
  await cell.dblclick();
  await expect(cell.locator('input, textarea, select')).toHaveCount(0);
  await expect(page.locator('#footer-note')).toContainText(/read-only/i);
});

test('Everything view separates curated master records from candidates', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  // The provenance column must exist and be frozen at the front of the sheet.
  // Curated master badges read "CM" (compact label; full phrase is in the
  // tooltip) per owner directive 2026-08-08.
  await expect(page.locator('.tabulator-col[tabulator-field="record_type"]')).toBeVisible();
  await expect(page.locator('.tabulator-cell[tabulator-field="record_type"]').first())
    .toContainText(/CM|Candidate/);

  // Derive the expected provenance state from the committed data: after the
  // 2026-08-08 D-01 collapse the Everything view holds 362 curated masters
  // and 0 unreviewed candidates, but a future candidate lane may reopen it.
  const { expectedMasterCount, expectedTotalCount, recordTypes } = await page.evaluate(async () => {
    const rows = await fetch('/docs/master.json').then((response) => response.json());
    return {
      expectedMasterCount: rows.filter((row) => row.record_type === 'master').length,
      expectedTotalCount: rows.length,
      recordTypes: [...new Set(rows.map((row) => row.record_type).filter(Boolean))],
    };
  });

  const reviewToolbar = page.locator('#review-toolbar');
  const reviewFilter = page.locator('#review-filter');
  if (recordTypes.length > 1) {
    // Candidates are present: the review filter must offer every provenance
    // value and filtering to curated master must exclude every candidate row.
    await expect(reviewFilter).toBeVisible();
    for (const recordType of recordTypes) {
      await expect(reviewFilter.locator(`option[value="${recordType}"]`)).toHaveCount(1);
    }
    await reviewFilter.selectOption('master');
    await expect(page.locator('#search-status'))
      .toContainText(`Showing: ${expectedMasterCount} of ${expectedTotalCount}`);
    await expect(page.locator('#filter-chips')).toContainText('Curated master');
  } else {
    // Every row is a curated master: the review filter is hidden by design
    // (app.js configureReviewFilter requires >1 distinct value to offer it).
    expect(recordTypes).toEqual(['master']);
    await expect(reviewToolbar).toBeHidden();
    // Unfiltered sheets show the bare visible count (no "of N" suffix).
    await expect(page.locator('#search-status'))
      .toHaveText(`Showing: ${expectedTotalCount}`);
  }

  const badges = page.locator('.tabulator-cell[tabulator-field="record_type"] .status-badge');
  expect(await badges.count()).toBeGreaterThan(0);
  for (const text of await badges.allTextContents()) {
    // In-cell badge is the compact "CM"; the full "Curated master" phrase
    // lives in its tooltip (title attribute).
    expect(text).toBe('CM');
  }
  await expect(badges.first()).toHaveAttribute('title', 'Curated master');
});

test('edition model columns render on the Everything tab', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await enableExpertColumns(page);

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

test('ODS export downloads a styled OpenDocument Spreadsheet (.ods) archive with colored groupings', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await page.locator('#export-btn').click();
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.locator('#export-ods-btn').click(),
  ]);

  expect(download.suggestedFilename()).toBe('hawkins-everything.ods');
  const downloadPath = await download.path();
  expect(downloadPath).toBeTruthy();

  const buf = await fs.readFile(downloadPath);
  expect(buf[0]).toBe(0x50); // P
  expect(buf[1]).toBe(0x4b); // K
  expect(buf[2]).toBe(0x03);
  expect(buf[3]).toBe(0x04);
  const text = buf.toString('utf8');
  expect(text).toContain('application/vnd.oasis.opendocument.spreadsheet');
  expect(text).toContain('#7C3AED'); // Books REVISION1 block border color
  expect(text).toContain('#F4EEFE'); // Books REVISION1 block background tint
  expect(text).toContain('Master ID');
  expect(text).toContain('Work');
});

test('XLSX export downloads a styled Excel workbook', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await page.locator('#export-btn').click();
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.locator('#export-xlsx-btn').click(),
  ]);
  expect(download.suggestedFilename()).toBe('hawkins-everything.xlsx');
  const buf = await fs.readFile(await download.path());
  expect([...buf.slice(0, 4)]).toEqual([0x50, 0x4b, 0x03, 0x04]);
  const text = buf.toString('utf8');
  expect(text).toContain('xl/worksheets/sheet1.xml');
  expect(text).toContain('state="frozen"');
  expect(text).toContain('<autoFilter');
  expect(text).toContain('Power vs. Force');
});

test('JSON export downloads the complete active view with metadata', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await page.getByRole('searchbox', { name: /search across all columns/i }).fill('Causality');
  await page.locator('#export-btn').click();
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.locator('#export-json-btn').click(),
  ]);
  expect(download.suggestedFilename()).toBe('hawkins-everything.json');
  const payload = JSON.parse(await fs.readFile(await download.path(), 'utf8'));
  expect(payload.schema_version).toBe(1);
  expect(payload.view).toBe('master');
  expect(payload.row_count).toBe(363);
  expect(payload.rows.some((row) => row.title === 'Satsang')).toBeTruthy();
  expect(payload.columns).toContain('uuid');
});

test('TSV export downloads a UTF-8 tab-separated complete view', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);
  await page.locator('#view-jump').selectOption('manualLeads');
  await waitForTable(page);
  await page.locator('#export-btn').click();
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.locator('#export-tsv-btn').click(),
  ]);
  expect(download.suggestedFilename()).toBe('hawkins-manual-leads.tsv');
  const tsv = await fs.readFile(await download.path(), 'utf8');
  expect(tsv.charCodeAt(0)).toBe(0xFEFF);
  expect(tsv).toContain('\t');
  expect(tsv.toLowerCase()).toContain('lead status');
});
