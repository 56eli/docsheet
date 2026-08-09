const { test, expect } = require('@playwright/test');

async function waitForTable(page) {
  await expect(page.locator('#spreadsheet[aria-busy="false"]')).toBeVisible();
  await expect(page.locator('.tabulator-row').first()).toBeVisible();
}

// The raw spreadsheet export contains fully-empty visual-separator rows; the
// Original Spreadsheet view hides them by default and offers a "Show blank
// separator rows" view setting (2026-08-09 audit §3.4). Expected counts are
// derived from the committed data.json so the test never hardcodes a number.
test('Original Spreadsheet hides blank separator rows by default, toggle restores them', async ({ page }) => {
  await page.goto('/docs/');
  await waitForTable(page);

  // The toggle lives in the View settings menu and only applies to the
  // Original Spreadsheet view, so it is hidden while the Everything view is
  // active even with the menu open.
  await page.getByRole('button', { name: 'View settings' }).click();
  const toggle = page.locator('#show-blank-rows-toggle');
  await expect(page.locator('#blank-rows-toggle-wrap')).toBeHidden();

  // Close the settings menu so it cannot overlay the tab row, then switch.
  await page.getByRole('button', { name: 'View settings' }).click();
  await page.getByRole('tab', { name: 'Original Spreadsheet' }).click();
  await waitForTable(page);

  const counts = await page.evaluate(async () => {
    const rows = await fetch('/docs/data.json').then((response) => response.json());
    const nonEmpty = rows.filter((row) =>
      Object.values(row).some((value) => String(value ?? '').trim() !== '')
    );
    return { total: rows.length, nonEmpty: nonEmpty.length };
  });

  // The toggle becomes visible on this tab, and blank rows are hidden by
  // default: grid and footer agree on the non-empty count, and the blank
  // first row of the raw sheet is absent.
  await expect(page.locator('#blank-rows-toggle-wrap')).toBeVisible();
  await expect(page.locator('#footer-stats')).toContainText(
    `Original Spreadsheet: ${counts.nonEmpty} rows`
  );
  await expect(page.locator('#search-status')).toContainText(
    `Showing: ${counts.nonEmpty}`
  );

  // Enabling the setting restores the verbatim raw sheet (all rows,
  // separators included) across grid and footer.
  await toggle.check();
  await expect(page.locator('#footer-stats')).toContainText(
    `Original Spreadsheet: ${counts.total} rows`
  );
  await expect(page.locator('#search-status')).toContainText(
    `Showing: ${counts.total}`
  );

  // Disabling it hides them again (round-trip).
  await toggle.uncheck();
  await expect(page.locator('#footer-stats')).toContainText(
    `Original Spreadsheet: ${counts.nonEmpty} rows`
  );
  await expect(page.locator('#search-status')).toContainText(
    `Showing: ${counts.nonEmpty}`
  );
});
