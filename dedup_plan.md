# Deduplication and URL Fill Plan

## Current Issues

### 1. UUID 264 vs UUID 329 (Duplicate Audio Editions)

**UUID 264:**
- Title: "In the World But Not of It" – Audio
- work_id: w-in-the-world-but-not-of-it-audio
- Status: Untyped, no format, no year, no URLs
- Series: Media Miscellaneous
- Raw row: 296

**UUID 329:**
- Title: "In the World But Not of It" – Audio
- work_id: w-in-the-world-but-not-of-it
- Status: lecture/CD/2009/01
- Series: Books
- Has Veritas URL: https://veritaspub.com/product/in-the-world-but-not-of-it-cd/
- format_detail: 6-CD set (Nightingale-Conant)
- Missing: Nightingale-Conant URL

**Analysis:** These are the same audio recording. UUID 329 is the properly catalogued edition.

### 2. Nightingale-Conant URL Misplacement

**Current state:**
- UUID 300 (book) has: source_url_nightingale_conant = https://www.nightingale.com/products/in-the-world-but-not-of-it
- UUID 329 (audio) has: source_url_nightingale_conant = (empty)

**Problem:** The Nightingale-Conant URL is for the audio edition, not the book.

### 3. Missing Hay House URLs

**Current state:**
- 38 total book records
- 20 have Hay House URLs
- 18 don't have Hay House URLs

**Need to:** Find and add Hay House URLs for the 18 books.

## Deduplication Plan

### Step 1: Remove UUID 264 from master
- Delete UUID 264 from data/research_master_draft.csv
- Delete UUID 264 from data/research_master_draft.json
- Remove work family w-in-the-world-but-not-of-it-audio from data/work_families.csv
- Update docs/master.json (Everything view)

### Step 2: Fix Nightingale-Conant URL
- Remove source_url_nightingale_conant from UUID 300
- Add source_url_nightingale_conant to UUID 329: https://www.nightingale.com/products/in-the-world-but-not-of-it
- Update source_overrides.csv to reflect correct raw_row_number

### Step 3: Fill Hay House URLs
- For each of the 18 books without Hay House URLs:
  - Search Hay House website for the book
  - Add URL to source_url_hay_house field
  - Create source override if needed

### Step 4: Update documentation
- Update README.md counts
- Update NEXT_AGENT_HANDOFF.md
- Regenerate reconciliation report

## Questions for Owner

1. Should I remove UUID 264 entirely, or mark it as excluded?
2. For the 18 books without Hay House URLs, should I search the Hay House website or do you have the URLs?
3. Are there any other records that need Nightingale-Conant URLs?

