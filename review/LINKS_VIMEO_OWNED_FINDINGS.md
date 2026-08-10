# Data-integrity answers: links, Vimeo, and the "Owned" flags

**Date:** 2026-08-10 · Session 019feb3e · Working tree at `54b37f7` (+ mobile branch `ccd945f`)
**Method:** full URL-domain scan of the curated master + raw source; full-tree + shallow-history search for "vimeo"; pipeline/ledger provenance trace for `owned`; GitHub issue #18 review.

---

## 1. Legal / no-filesharing links — ✅ Confirmed (with one nuance)

**Curated catalogue (`docs/master.json` → the "Everything" view):** every URL belongs to exactly **five official/legal sources**, all HTTPS, **zero** filesharing/torrent/pirate/unofficial domains:

| Domain | Count | What it is |
|---|---:|---|
| veritaspub.com | 387 | Veritas Publishing — the official publisher (product + streaming) |
| hayhouse.com | 27 | Hay House — official publisher |
| amazon.com | 21 | Amazon — official retailer |
| audible.com | 21 | Audible — official retailer |
| nightingale.com | 6 | Nightingale-Conant — official publisher/retailer |

(`reference_url_1` streaming links are all 54 veritaspub.com — official Veritas streaming.)

**Nuance — the raw "Original Spreadsheet" tab:** `docs/data.json` is a *verbatim pass-through* of the source Google Sheet, so it additionally carries a few non-product links that are **not** in the curated master:

- `goodreads.com` ×2 — book listing/review pages (informational, legal)
- `github.com/56eli/bookbot/...` ×1 — your own reference repo
- `discord.com/channels/...` ×2 — community/discussion channels (legal, not filesharing)

None are filesharing. They exist only in the raw view (mirroring the source sheet) and never enter the curated catalogue. If you want them stripped from the raw view too, that's a one-line `process_data.py` filter — but it would deviate from the "raw is passed through unchanged" contract.

---

## 2. What happened to the Vimeo links — Veritas removed the trailers; they were never in the catalogue

There are **no Vimeo links anywhere in the data** — not in `master.json`, not in any CSV, not in the raw source sheet. Vimeo appears **only in historical review/provenance docs** under `archive/` and `decisions/`. The story those docs tell:

- Veritas Publishing originally hosted **Vimeo trailers** for several **On-The-Road (OTR)** lectures — e.g. *Verification of Spiritual Realities* / *God is Hidden* (trailer ID `654479044`), and the OTR block around masters 215–232.
- **Veritas took those trailer pages down** ("Vimeo trailer (654479044) — Page removed"; "Vimeo trailer removed" — `decisions/YEAR_COLUMN_PROVENANCE.md`, `archive/LECTURE_YEAR_INVESTIGATION.md`).
- The project investigated them while trying to establish recording **years** for the OTR talks; with the trailers gone, they yielded no year evidence, so per the **no-guessing rule** those years were left blank ("under investigation").
- Vimeo was **never promoted into the curated master** — only the five official source domains above are. So nothing "happappened" to a live Vimeo link in the sheet; it was a publisher-side trailer that disappeared and was only ever referenced in investigation notes.

Caveat on method: this checkout is a **shallow clone**, so `git log -S vimeo` can't see deep history — but the full working-tree scan is conclusive (no Vimeo in any current data), and the archive/decisions docs document the trailer-removal directly.

---

## 3. "Owned" flags — provenance + **partial** confirmation; a known unresolved mismatch is open

### How `owned` is set
`owned` is **reviewer-set**, not auto-derived. It flows from `proposed_owned` (true/false/blank) in:
- `migration_review_ledger.csv` — 299 item rows: **274 true / 25 false**
- candidate/edition inputs (`manual_master_candidates.csv`, `edition_promotions.csv`) — bring the master to **312 true / 25 false / 26 blank**

The 26 blank = minted edition rows + Nightingale-Conant/Hay House programs that carry **no** ownership marker (intentional tri-state). The 25 false = explicitly-not-owned.

### What confirmation exists
- **archive.org cross-check (2026-08-09, session 019fe844):** the `Hawkins_Lectures_transcoded_actual_files` archive.org directory was scanned and **16 records were independently confirmed and promoted to owned=true** (274→290 in the ledger; 295→311 master-side). So 16 have external file-evidence.
- **The other ~296 `owned=true` are reviewer-asserted** via the ledger's `review_reason`, **not** machine-verified against a file inventory.

### The open gap — GitHub issue #18 (OPEN since 2026-08-04)
A cross-check **from the lak.nz working-library side** (rclone `gdrive:mother-of-all-torrents`, 350 files / 310 catalogue rows, reflected on hawkins-test.lak.nz) flagged concrete deltas against this repo's `owned` flags:

- **A. `owned=true` here but NO matching file on their Drive (12 items):** Progressive Levels of Consciousness (Oxford OTR), Devotion to Truth (OTR), Mind/Heart/Service parts, Spiritual Will parts, Daily Reflections, Along the Path to Enlightenment, Dissolving the Ego, The Path to Spiritual Advancement, and four Transcription-Series titles (Evolution of Consciousness, Beyond Illusion, Karma and Devotion, Final Doorway). *Possible causes: a different definition of "owned" (commercial product owned vs. present in the working file library), renamed files, or rows to revisit.*
- **B. File present on their Drive but `owned` not true here:** multiple Satsang Series (2007–2010) month rows.

Issue #18 also notes that **lak.nz treats their own catalogue as the source of truth** and this docsheet as "helper reference only," so the canonical ownership record may live on their side.

### Bottom line on "Owned"
- **Not fully confirmed.** 16 records have archive.org file evidence; the rest are reviewer-asserted.
- A **specific, itemized mismatch is already documented and OPEN** (issue #18): ~12 owned=true items with no matching file, plus Drive files not marked owned. Resolving it needs **owner access to the lak.nz Drive working library** to reconcile definitions and re-match renamed files. This is the same blocker the scoreboard has tracked since 2026-08-04.

---

## Suggested next steps (your call)
1. **Owned reconciliation:** I can open a `data/` review overlay (e.g. `data/owned_reconciliation_queue.csv`) seeded from issue #18's 12 "owned=true but no file" items so they're triaged through the normal review lane once you have Drive access — without touching the live `owned` values yet.
2. **Raw-view link hygiene:** optionally strip the goodreads/discord/github cells from the raw `data.json` view (keeps the curated master clean, which it already is).
3. **Nothing data-side:** leave as-is; the catalogue links are clean and the owned gap is already tracked in issue #18.
