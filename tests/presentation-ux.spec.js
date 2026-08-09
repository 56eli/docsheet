const { test, expect } = require('@playwright/test');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await page.locator('.tabulator-row').first().waitFor();
}

// Presentation/UX improvements: sleek clean desktop layout, group row block
// color coding, desktop Browse mode toggle, review-workspace nav toggle, and
// the client-side Series browser.

test('desktop interface opens directly into the clean spreadsheet', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  // Hero, overview cards, and stats strip have been removed as requested for an unbloated desktop view.
  await expect(page.locator('#catalogue-intro')).toBeHidden();
  await expect(page.locator('#stats-strip')).toBeHidden();
  await expect(page.locator('#spreadsheet')).toBeVisible();
  await expect(page.locator('.tabulator-row').first()).toBeVisible();
});

test('desktop rows feature group block styling classes', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const firstRow = page.locator('.tabulator-row').first();
  await expect(firstRow).toHaveClass(/row-block-styled/);
});

test('desktop Browse cards toggle swaps the Everything view presentation', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const toggle = page.locator('#master-browse-toggle');
  await expect(toggle).toBeVisible();
  await expect(toggle).toHaveText('Browse cards');

  await toggle.click();
  await expect(page.locator('#mobile-browse')).toBeVisible();
  await expect(page.locator('#spreadsheet')).toBeHidden();
  await expect(page.locator('.mobile-work-card').first()).toBeVisible();
  await expect(page.locator('#mobile-series-shelf button').first()).toBeVisible();
  await expect(toggle).toHaveText('Spreadsheet');

  await toggle.click();
  await waitForTable(page);
  await expect(page.locator('#mobile-browse')).toBeHidden();
});

test('review workspace tabs collapse and expand via the nav toggle', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const groups = page.locator('#review-nav-groups');
  await expect(groups).toBeVisible();
  await expect(page.locator('#review-nav-toggle')).toHaveAttribute('aria-expanded', 'true');

  await page.locator('#review-nav-toggle').click();
  await expect(groups).toBeHidden();
  await expect(page.locator('#review-nav-toggle')).toHaveAttribute('aria-expanded', 'false');

  await page.locator('#review-nav-toggle').click();
  await expect(groups).toBeVisible();
  await expect(page.locator('#review-nav-toggle')).toHaveAttribute('aria-expanded', 'true');
});

test('Series browser lists every series and opens the filtered catalogue', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await page.getByRole('tab', { name: 'Series', exact: true }).click();
  await expect(page.locator('#series-landing')).toBeVisible();
  await expect(page.locator('#spreadsheet')).toBeHidden();
  await expect(page.locator('#series-landing-grid .series-landing-card').first()).toBeVisible();

  const { seriesCount, satsangCount } = await page.evaluate(async () => {
    const rows = await fetch('/docs/master.json').then((response) => response.json());
    return {
      seriesCount: new Set(rows.map((row) => row.series || '(unassigned)')).size,
      satsangCount: rows.filter((row) => row.series === 'Satsang Series').length,
    };
  });
  await expect(page.locator('#series-landing-grid .series-landing-card')).toHaveCount(seriesCount);
  await expect(page.locator('#footer-stats')).toContainText(`Series: ${seriesCount} series`);

  await page.locator('#series-landing-grid .series-landing-card', { hasText: 'Satsang Series' }).click();
  await waitForTable(page);
  await expect(page.locator('#search-status')).toContainText(`Showing: ${satsangCount} of 362`);
  await expect(page.locator('#filter-chips')).toContainText('Satsang Series');
});

test('presentation controls carry accessible names and states', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await expect(page.locator('#review-nav-toggle')).toHaveAttribute('aria-controls', 'review-nav-groups');
  await expect(page.locator('#master-browse-toggle')).toHaveAttribute('aria-pressed', 'false');
  await expect(page.locator('#series-landing')).toHaveAttribute('aria-label', 'Series browser');
});
