# Book Relationship Decisions

**Approved:** 2026-08-03  
**Scope:** Bounded review of the twelve non-primary Veritas product matches whose existing master record is typed `book`.

## Primary book sources added

Nine exact-title book products are now approved primary Veritas sources through `data/research_master_source_overrides.csv`:

- *The Final Doorway to Enlightenment: Prayer, Transcendence and Realization of the Self* (product 56141)
- *Karma and Devotion: The Sacred Path to God through the Heart* (55582)
- *Spiritual Power and Integrity: Uncovering Spiritual Reality and Realizing Peace, Love, and Divinity* (55424)
- *The Evolution of Consciousness: Navigating the Levels of Awareness and Unlocking Spiritual Potential* (54489)
- *The Path to Spiritual Advancement: How to Transcend the Ego and Experience the Presence of God* (54472)
- *Transcending the Levels of Consciousness* (50407)
- *The Eye of the I* (50393)
- *Reality, Spirituality and Modern Man* (50388)
- *I: Reality and Subjectivity* (50382)

Each product page identifies a matching book/transcription product. The master build now retains the official URL as the primary source and creates the corresponding exact primary item/product relationship.

## Cross-format edition records

The edition model now gives each reviewed carrier its own master row. The
following exact book products are therefore the **primary sources of the book
masters**, not non-primary overlay decisions; their separate audio/CD/DVD
products remain separate edition rows:

| Book master | Primary book product | Separate carrier record |
|---|---|---|
| *In the World, But Not of It* (300) | Product 53062 | Product 1661 → edition master 329 (Nightingale-Conant CD) |
| *Truth vs Falsehood* (289) | Product 50398 | Product 1728 → edition master 327 (CD/DVD set) |
| *Healing and Recovery* (291) | Product 50378 | Product 1695 → edition master 328 (audio program) |

The four stale non-primary overlay rows for these exact primary URLs were
removed on 2026-08-08. No title-only candidate was bulk-promoted; the current
candidate/edition registries and `PRODUCT_RELATIONSHIP_SCHEMA.md` define the
remaining review boundary.
