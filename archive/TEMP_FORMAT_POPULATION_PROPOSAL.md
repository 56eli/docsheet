# Temporary: Format Population Implementation Proposal (2026-08-03)

**One-sentence task summary:** Analyzed 113 blank-format master rows; strong SKU/slug/title evidence exists in veritas_official_products.csv for deterministic population of most (DVD, CD, streaming, audio, book).

## Evidence gathered
- 113 rows lack `format` (mostly Q&A sessions, Volume series, Satsang, Office Series, etc.).
- Veritas product slugs + official_title contain reliable signals:
  - `volume-*-video`, `muscle-testing-video` → DVD
  - `3-cd-set`, `satsang-series-*-cd` → CD
  - `question-answer-session`, `q&a` → streaming (or "audio" for older)
  - `– Audio` or `audio` in title → audio
  - `(Book)` or book slugs → book
- Existing `format_detail` and `notes` provide secondary signals.
- 100+ of the 113 have Veritas URLs → direct lookup possible.

## Proposed change (non-destructive)
Add a new helper in `build_research_master.py`:

```python
def infer_format_from_official_source(item: dict[str, str], veritas_by_id: dict) -> str:
    """Infer format from Veritas product slug/title when blank."""
    url = item.get("source_url_veritas", "")
    if not url:
        return ""
    slug = url.rstrip("/").split("/")[-1].lower()
    pid = slug.split("-")[0] if "-" in slug else slug
    prod = veritas_by_id.get(pid, {})
    title = (prod.get("official_title", "") or item.get("title", "")).lower()

    if any(k in slug for k in ["video", "muscle-testing-video", "volume-"]):
        return "DVD"
    if any(k in slug for k in ["cd-set", "3-cd-set"]) or "satsang" in slug and "cd" in slug:
        return "CD"
    if any(k in slug for k in ["question-answer", "q&a"]):
        return "streaming"
    if "audio" in slug or "– audio" in title:
        return "audio"
    if "book" in slug or "(book)" in title:
        return "book"
    return ""
```

Then call it during master item construction (after source overrides, before writing) and only set if current format is blank. Also update the `--check` validation to report how many were inferred.

This keeps the change reviewable, deterministic, and only fills blanks.

**Risk:** 10-15 rows may still need manual review (international or edge cases); we can emit them to a review note or leave blank.

This file is temporary. Ready to implement once approved.