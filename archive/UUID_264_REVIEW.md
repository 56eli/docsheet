# UUID 264 Review — "In the World But Not of It" – Audio

## Current State

**UUID 264** is the only untyped record in the master (1 out of 350 records).

| Field | Value |
|-------|-------|
| UUID | 264 |
| Title | "In the World But Not of It" – Audio |
| item_type | *(blank)* |
| format | *(blank)* |
| series | Media Miscellaneous |
| year | *(blank)* |
| work_id | w-in-the-world-but-not-of-it-audio |
| source_url_veritas | *(blank)* |
| owned | true |

## Documentation Status

This record is **intentionally deferred** per `NEXT_AGENT_HANDOFF.md`:

> **Record 264** (`"In the World But Not of It" – Audio`, the 1 untyped record):
> deferred pending physical-edition confirmation; product 1661 is mapping-row
> only — do **not** add a source override yet.

And per `decisions/SERIES_REGROUPING_DECISIONS.md`:

> | Deferred (246, 249, 264) | 3 | *(none)* |

## Related Records

There are 3 other records with similar titles:

| UUID | Title | item_type | format | year | work_id |
|------|-------|-----------|--------|------|---------|
| 300 | In the World, But Not of It | book | book | 2023 | w-in-the-world-but-not-of-it |
| 326 | In The World But Not Of It (Audiobook) | book | audio | — | w-in-the-world-but-not-of-it |
| 329 | "In the World But Not of It" – Audio | lecture | CD | 2009 | w-in-the-world-but-not-of-it |

**Key observation**: UUID 329 has the same title as UUID 264, but is typed as `lecture` with `format=CD` and `year=2009`.

## Context from Migration Ledger

**Raw row 296**:
- Disposition: `item`
- Proposed title: `"In the World But Not of It" – Audio`
- Proposed item_type: *(blank)*
- Proposed format: *(blank)*
- Proposed year: *(blank)*
- Source URL: *(blank)*
- Owned: ✅
- Review reason: "Item candidate indicated by ownership status and/or legacy tempid."

**Surrounding context**:
- Row 294: "Media Miscellaneous" (series_context heading)
- Row 295: Research note: "❌❌ MOST ARE MISSING ❌❌ NOT YET IN THE SPREADSHEET"
- Row 296: **This record**
- Row 297: "Golden Word Book Signing – Audio" (item_type=lecture)

## Analysis

**Evidence for `item_type=lecture`**:
1. Title includes "Audio" suggesting an audio recording
2. Surrounding record (row 297) is a lecture
3. Similar record UUID 329 with same title is typed as `lecture`
4. Located in "Media Miscellaneous" series which contains audio recordings

**Evidence for `item_type=book`**:
1. There's a book edition (UUID 300, year 2023)
2. There's an audiobook edition (UUID 326, format=audio)

**Evidence for deferral**:
1. Documentation explicitly states "deferred pending physical-edition confirmation"
2. No source URL available for verification
3. No year/format data in ledger
4. Part of "Media Miscellaneous" section marked "MOST ARE MISSING"

## Options

### Option A: Assign `item_type=lecture`, `format=CD`, `year=2009`
**Rationale**: Matches UUID 329 which has identical title
**Risk**: May be a different edition/recording; no verification possible

### Option B: Assign `item_type=lecture`, leave format/year blank
**Rationale**: Conservative — we know it's audio, likely a lecture
**Risk**: Still unverified

### Option C: Keep deferred (no changes)
**Rationale**: Follow existing documentation; wait for owner decision
**Risk**: Leaves 1 untyped record in master

### Option D: Exclude from master
**Rationale**: Insufficient data; move to exclusions
**Risk**: Loss of provenance; record is marked as owned

## Recommendation

**Option C (Keep deferred)** is recommended unless the owner can confirm:
1. Is this the same recording as UUID 329 (year 2009, CD format)?
2. Or is it a different edition/recording?
3. What is the physical format (CD, audio download, etc.)?

---

**Status**: Awaiting owner decision  
**Date**: 2026-08-03
