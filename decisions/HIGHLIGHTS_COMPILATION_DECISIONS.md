# Annual Highlights Compilation Decisions

**Approved:** 2026-08-03  
**Scope:** Model the seven official Veritas Highlights products without overstating which individual DVD part supplied each clip.

## Decision

Seven reviewed `compilation_draws_from_series` rows are recorded in `data/series_compilation_relationships.csv`:

- Highlights of the 2002 Lectures 1–6 → *The Way to God*, January–June 2002 (six lectures)
- Highlights of the 2002 Lectures 7–12 → *The Way to God*, July–December 2002 (six lectures)
- Highlights of the 2003 Lectures → *Devotional Nonduality* (six lectures)
- Highlights of the 2004 Lectures → *Transcending the Mind* (six lectures)
- Highlights of the 2005 Lectures → *Nonduality Intensive* (ten lectures)
- Highlights of the 2006 Lectures → *Transcending Levels of Consciousness* (eight lectures)
- Highlights of the 2007 Lectures → *Spiritual Reality & Modern Man* (nine lectures)

The official product pages explicitly identify clips or segments from every lecture in the named scope. The generated Series Compilations sheet shows the evidence, matching lecture count, part count, and exact lecture-title list.

## Deliberate boundary

The master holds each DVD part as a separate top-level item, while the Highlights pages identify lectures rather than individual DVD parts. Therefore no `compilation_includes_item` relationships are created for the 171 parts in the covered annual scopes. The Highlights products remain broad official candidates in Everything, not master items.

## SUPERSEDED 2026-08-07 (owner ruling)

The seven Highlights products are **promoted to curated master records** (UUIDs
362–368, `item_type=highlight`, `series=Lecture Highlights`, year from the
title, proposed filename = title, format streaming per the official storefront
"Product Details: Streaming"). The `compilation_draws_from_series` rows in
`data/series_compilation_relationships.csv` are **kept** — they document what
each Highlights product draws from. The seven inventory rows are now
`matched_by_primary_source`; the seven mapping-decision suppression rows were
lifted and the taxonomy mapping approves `Lecture Highlights` (rule R1) for
them.

**Slug note (2026-08-09):** product 1800's official URL slug still contains
`-dvd` (`…/the-way-to-god-highlights-of-the-first-6-lectures-of-2002-dvd/`)
even though the storefront product detail declares the carrier Streaming
(verified 2026-08-07 for the 2003/2005 Highlights pages; see
`build_research_master.py` `infer_format_from_official_source`). The master
therefore keeps `format=streaming` for all seven Highlights rows — the slug is
a publisher URL artifact, not a carrier statement.
