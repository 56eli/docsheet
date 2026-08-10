# Mobile spreadsheet scrolling fix — 2026-08-10

## Reported behavior

On phone-sized viewports, switching from Browse to **Spreadsheet** could make
horizontal swipes ineffective and vertical movement rubber-band back instead of
remaining in the table.

## Cause and correction

The page is intentionally a fixed application shell with a scrollable table inside
it, but the scroll ownership was not explicit enough for mobile touch browsers. A
gesture at the table edge could be handed to the document instead of staying with
Tabulator’s `.tabulator-tableholder`.

The fix makes the scroll hierarchy explicit:

1. the document shell uses the dynamic visible viewport (`100dvh`) and does not
   scroll;
2. the catalogue container clips overflow, leaving its active inner view as the
   only scroll owner;
3. Tabulator’s table holder is explicitly two-axis scrollable with native touch
   momentum, `touch-action: pan-x pan-y`, and contained overscroll.

This preserves Browse mode’s own internal vertical scroller while making
Spreadsheet mode’s table holder the direct target for both horizontal and vertical
panning.

## Regression coverage

A Playwright mobile test now opens Spreadsheet mode at 390×844, asserts that the
table holder overflows in both dimensions, then verifies that programmatic
horizontal and vertical scrolling both retain nonzero positions. The test is ready
for CI browser execution; local browser installation remains unavailable in this
sandbox because required Debian/Chromium packages cannot be fetched.
