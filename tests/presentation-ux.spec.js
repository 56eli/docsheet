const { test, expect } = require('@playwright/test');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await page.locator('.tabulator-row').first().waitFor();
}

async function rowVisual(row) {
  return row.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      backgroundColor: style.backgroundColor,
      boxShadow: style.boxShadow,
      borderTopWidth: style.borderTopWidth,
      blockLectures: style.getPropertyValue('--block-lectures').trim(),
      className: element.className,
      matchesLectureRule: element.matches('#spreadsheet.tabulator .tabulator-row[data-block="lectures-2002-2011"]'),
      styleSheets: [...document.styleSheets].map((sheet) => sheet.href || 'inline'),
    };
  });
}

async function findBlockRow(page, query, blockId) {
  await page.locator('#global-search').fill(query);
  const row = page.locator(`.tabulator-row[data-block="${blockId}"]`).first();
  await expect(row).toBeVisible();
  return row;
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

test('computed row styles preserve zebra and REVISION1 accents across blocks', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('docsheet-dark-mode', '0');
    localStorage.setItem('docsheet-master-presentation', 'table');
  });
  await page.goto('/docs/');
  await waitForTable(page);

  const firstRow = page.locator('.tabulator-row').first();
  const secondRow = page.locator('.tabulator-row').nth(1);
  await expect(firstRow).toHaveClass(/row-block-styled/);
  await expect(firstRow).toHaveAttribute('data-block', 'lectures-2002-2011');
  await expect(secondRow).toHaveClass(/tabulator-row-even/);

  const firstVisual = await rowVisual(firstRow);
  const secondVisual = await rowVisual(secondRow);
  expect(firstVisual.className).toContain('row-block-lectures-2002-2011');
  expect(firstVisual.matchesLectureRule).toBe(true);
  expect(firstVisual.blockLectures).toBe('#059669');
  // The hard-coded style.css hash here is the *current* revision
  // (936c444be89d) — the test catches a stale cache by failing when the
  // browser delivers an older version. If the style.css bytes change,
  // update this hash and the matching `?v=` in docs/index.html together.
  expect(firstVisual.styleSheets.some((href) => href.includes('/docs/style.css?v=936c444be89d'))).toBe(true);
  expect(firstVisual.backgroundColor).not.toBe(secondVisual.backgroundColor);
  expect(firstVisual.boxShadow).toContain('rgb(5, 150, 105)');
  expect(firstVisual.borderTopWidth).toBe('2px');

  // A filtered result becomes the first (odd, work-group-start) row. This is
  // the exact cascade case that used to replace every block color with the
  // global green work-group shadow.
  const discussionRow = await findBlockRow(page, 'Permanent Inner Peace', 'discussion');
  const discussionLight = await rowVisual(discussionRow);
  expect(discussionLight.boxShadow).toContain('rgb(225, 29, 72)');
  expect(discussionLight.borderTopWidth).toBe('2px');

  const officeRow = await findBlockRow(page, 'Spiritual First Aid', 'office-series');
  const officeLight = await rowVisual(officeRow);
  expect(officeLight.boxShadow).toContain('rgb(2, 132, 199)');

  // Dark mode must preserve the block identity rather than reverting to the
  // generic accent; it must also produce a different computed row surface.
  await page.locator('#dark-toggle').evaluate((input) => {
    input.checked = true;
    input.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await expect(page.locator('html')).toHaveClass(/dark/);
  const officeDark = await rowVisual(officeRow);
  expect(officeDark.backgroundColor).not.toBe(officeLight.backgroundColor);
  expect(officeDark.boxShadow).toContain('rgb(56, 189, 248)');
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

test('Jump to selector switches catalogue and review workspace views', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  const jumpSelect = page.locator('#view-jump');
  await expect(jumpSelect).toBeVisible();

  await jumpSelect.selectOption('veritasProducts');
  await waitForTable(page);
  await expect(page.locator('#view-title')).toHaveText('Veritas Products');

  await jumpSelect.selectOption('master');
  await waitForTable(page);
  await expect(page.locator('#view-title')).toHaveText('Everything');
});

test('Series browser lists every series and opens the filtered catalogue', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  await page.locator('#view-jump').selectOption('series');
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

  await expect(page.locator('#view-jump')).toHaveAttribute('aria-label', 'Jump to a catalogue view');
  await expect(page.locator('#master-browse-toggle')).toHaveAttribute('aria-pressed', 'false');
  await expect(page.locator('#series-landing')).toHaveAttribute('aria-label', 'Series browser');
});
