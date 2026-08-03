# Official Category Dominance Policy

**Status:** Owner-approved 2026-08-03

This policy maps the official Veritas product taxonomy to the catalogue `series`
field. It makes category precedence explicit while preserving all official
categories as source evidence. It does **not** automatically change `item_type`;
content-class changes require a separate record-level review.

## Dominance rules

1. **Lecture Highlights** is primary over an annual lecture series.
2. **Satsang** is primary over every other category except that a simultaneous
   Satsang + Lecture Highlights assignment is **flagged for review**.
3. An **annual lecture series** is primary over broad collection categories and
   over On the Road.
4. **On the Road Talk Series** is primary when no annual lecture-series category
   is present.
5. **The Six Book 2002 Transcription Series** is primary over the linked annual
   2002 lecture series.
6. **Archival Office Visit Series** is primary over Media Miscellaneous.
7. A specific non-lecture category such as **Card Decks** maps to its own series.
8. **New Products** is only a fallback category and never outranks a descriptive
   category.
9. An item with no recognized dominant category remains blank and is placed in a
   review queue; title-based inference is not allowed.

## Operational rules

- Official categories are publisher taxonomic assertions, not direct proof of
  `item_type`; do not change a record from book, lecture, or discussion without
  a separately documented review decision.
- When multiple categories are present, persist the complete publisher category
  list and the chosen dominant category/reason in the category-mapping input.
- The `series` field receives the human-readable series mapped from the dominant
  category; lower-ranking categories are relationship/provenance evidence, not
  discarded facts.
- Category rules must be applied from a reproducible committed mapping input,
  not by hand-editing generated master or Pages JSON files.
