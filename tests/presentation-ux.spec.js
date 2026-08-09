const { test, expect } = require('@playwright/test');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await page.locator('.tabulator-row').first().waitFor();
}

// Presentation/UX improvements from the 2026-08-09 proposal: catalogue
// overview (hero, collection stats, series strip), desktop Browse mode,
// review-workspace nav toggle, and the client-side Series browser. Expected
// counts are derived from the committed master.json so nothing is hardcoded.

test('hero shows on Everything, dismisses, and restores via Show overview', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await expect(page.locator('#catalogue-intro')).toBeVisible();
  await expect(page.locator('#hero')).toContainText('David R. Hawkins — Archive Catalogue');
  await expect(page.locator('#overview-btn')).toBeHidden();

  await page.locator('#hero-dismiss').click();
  await expect(page.locator('#catalogue-intro')).toBeHidden();
  await expect(page.locator('#overview-btn')).toBeVisible();

  await page.locator('#overview-btn').click();
  await expect(page.locator('#catalogue-intro')).toBeVisible();
  await expect(page.locator('#overview-btn')).toBeHidden();
});

test('collection overview cards match the master data', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const counts = await page.evaluate(async () => {
    const rows = await fetch('/docs/master.json').then((response) => response.json());
    const owned = rows.filter((row) => String(row.owned ?? '').toLowerCase() === 'true').length;
    const notOwned = rows.filter((row) => String(row.owned ?? '').toLowerCase() === 'false').length;
    return { total: rows.length, owned, notOwned, blank: rows.length - owned - notOwned };
  });

  const overall = page.locator('#overview-cards .overview-card').first();
  await expect(overall).toContainText(
    `${counts.owned} owned · ${counts.notOwned} not owned · ${counts.blank} not stated`
  );
  // Progress bar aria-label states owned-of-total on the overall card.
  await expect(overall.locator('.progress-track')).toHaveAttribute(
    'aria-label',
    `${counts.owned} of ${counts.total} owned`
  );
});

test('series strip chip filters the Everything view', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const expected = await page.evaluate(async () => {
    const rows = await fetch('/docs/master.json').then((response) => response.json());
    return rows.filter((row) => row.series === 'Satsang Series').length;
  });

  await page.locator('#series-strip-list .series-chip', { hasText: 'Satsang Series' }).first().click();
  await expect(page.locator('#search-status')).toContainText(`Showing: ${expected} of 362`);
  await expect(page.locator('#filter-chips')).toContainText('Satsang Series');
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

test('new presentation controls carry accessible names and states', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await expect(page.locator('#hero-dismiss')).toHaveAttribute('aria-label', /Dismiss/);
  await expect(page.locator('#review-nav-toggle')).toHaveAttribute('aria-controls', 'review-nav-groups');
  await expect(page.locator('#master-browse-toggle')).toHaveAttribute('aria-pressed', 'false');
  await expect(page.locator('#series-strip-list')).toHaveAttribute('role', 'group');
  await expect(page.locator('#series-landing')).toHaveAttribute('aria-label', 'Series browser');
});
