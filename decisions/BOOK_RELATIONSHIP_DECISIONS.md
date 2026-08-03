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

## Cross-format related material recorded

The following official book products are recorded as reviewed `related_material` without replacing the master’s existing audio/CD/DVD primary source URL:

| Master record | Official book product | Basis |
|---|---|---|
| *In the World, But Not of It* | Product 53062 | The official book page says it is based on the popular audio program. |
| *Truth vs Falsehood* | Product 50398 | The print book is a separate 496-page commercial product; the master primary source remains the CD/DVD set. |
| *Healing and Recovery* | Product 50378 | The official book page calls the print book a companion to the lectures; the master primary source remains audio. |

No title-only candidate was bulk-promoted. The remaining candidate pool remains subject to the evidence and controlled-type requirements in `PRODUCT_RELATIONSHIP_SCHEMA.md`.
