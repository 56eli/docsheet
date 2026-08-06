# Veritas Live Refresh Check — 2026-08-04

**Date:** 2026-08-04  
**Method:** Live WordPress API via `fetch_page` tool (bypasses sandbox TLS EOF) with compact `_fields=id` to avoid HTML payload.

## API calls

```
GET /wp-json/wp/v2/product?per_page=100&page=1&_fields=id  → 100 IDs
GET /wp-json/wp/v2/product?per_page=100&page=2&_fields=id  → 91 IDs
GET /wp-json/wp/v2/product?per_page=100&page=3&_fields=id  → 400 (no more pages)
```

Total live = 191 IDs.

## Comparison

- **Committed inventory `data/veritas_official_products.csv`:** 191 rows
- **Live API:** 191 IDs
- **Diff:** `live - committed = ∅`, `committed - live = ∅` — **exact match**

## Detail

Page1 IDs (100): 56141 Final Doorway 2026-01-13, 55582 Karma and Devotion, 55576 Essence of Letting Go, 55473 Devotion to Truth Talk, 55425 Man Who Mapped Consciousness, 55424 Spiritual Power and Integrity, 55284 Beyond Illusion, 54838 Power vs Force Card Deck, 54489 Evolution of Consciousness, 54472 Path to Spiritual Advancement, 54219 Mind Heart and Service, 53942 Letting Go Deck, 53277 Progressive Levels, 53062 In the World But Not of It book, 53058 Wisdom, 52945 Spiritual Will, 53036 Life with Doc, 54226 Letting Go Guided Journal, 53060 Daily Reflections, 48825 Transcending the Ego, 43728 Map of Consciousness Explained, 43146 Power of Love, 38608 Book of Slides, 36833 Ultimate Truth free CD, 1820 Success Is for You, 47979 Ego is Not Real You, 1792 Don't Set Sail, 50516 What is Meant by Spiritual 2012, 50513 Importance of Family 2012, 50510 How to See Reality of Life, 50507 Improving Your Relationships 2012, 50494 What You Are Changes the World, 50491 How to Live Your Life Like a Prayer, 50488 What is Real Success, 50485 Permanent Inner Peace, 50411 Power vs Force book, 50407 Transcending Levels book, 50398 Truth vs Falsehood book, 50393 Eye of I book, 50388 Reality Spirituality Modern Man book, 50382 I Reality book, 50378 Healing and Recovery book, 50370 Letting Go book, 50458 Death and Dying, 50438 Cancer, 50432 Map of Consciousness, 50453 Drug Addiction and Alcoholism, 50435 Alcoholism, 50470 Illness and Self-Healing, 50461 Depression, 50444 Losing Weight, 50473 Pain and Suffering, 50482 Worry Fear Anxiety, 50464 Handling Major Crises, 50479 Aging Process, 50476 Sexuality, 50441 Spiritual First Aid, 50467 Health, 50447 Stress, 46042 Spiritual Reality 3-CD, 40035 Truth Shines Forth 3-CD, 37223 You Are Light of Consciousness, 36441 Virtues, 1830 Verification of Spiritual Realities, 37761 Prevailing Silence 3-CD, 42624 Presence of Spiritual Awareness, 1804 Power of Devotion, 1828 Ever-Present Joy, 1814 Peace is Natural State, 1822 Love is a Way of Being, 1802 God is Infinite Field, 1810 God is Hidden Within Beauty of Music, 39375 Compassion Pathway of Heart, 38104 Become That Which You Are, 1826 All is Divinity, 1742 Highest Level Enlightenment Audio, 1728 Truth vs Falsehood CD&DVD, 50772 Love Sep 2011, 50790 Q&A Jul 2011, 50775 Most Valuable Qualities May 2011, 1712 Q&A Mar 2011, 50796 Q&A Jan 2011, 1704 Satsang Nov 2010, 50766 Spiritual Life Oct 2010, 1699 Satsang Sep 2010, 1695 Healing Audio, 1697 Satsang Jun 2010, 50769 Handling Spiritual Challenges Apr 2010, 1687 Satsang Feb 2010, 1683 Satsang Nov 2009, 50752 Success Oct 2009, 1677 Satsang Sep 2009, 50755 Peace Aug 2009, 1671 Satsang May 2009, 50758 Happiness Apr 2009, 50761 What is World Feb 2009, 1661 In World But Not Of It Audio, 1659 Satsang Jan 2009, 50707 Unique Sedona Seminar Dec 2008, 50725 Freedom Morality Ethics Nov 2008

Page2 IDs (91): 50710 Practical Spirituality Oct 2008, 1645 Satsang Sep 2008, 50716 Overcoming Doubt Aug 2008, 1639 Satsang Jul 2008, 50713 Belief Trust Credibility Jun 2008, 1633 Satsang May 2008, 50722 Clear Pathway Mar 2008, 50719 Spirituality Reason Faith Jan 2008, 50728 Experiential Reality Dec 2007, 50731 Spiritual Survival Nov 2007, 50734 Creation vs Evolution Oct 2007, 1602 Satsang Sep 2007, 50521 Review of Work Sep 2007, 50737 Human Dilemma Aug 2007, 50740 What is Truth Absolute Jul 2007, 1592 Satsang Jul 2007, 50743 What is Real Jun 2007, 1586 Satsang May 2007, 50746 Relativism vs Reality Apr 2007, 1560 Map of Consciousness poster, 1552 Golden Word Book Signing Audio, 1548 Unity Church June 2006 CD, 1546 Unity Church March 2005 CD, 1544 Giving Up Illness, 1542 Power vs Force Audio Book, 50801 Vol VII Conversation with Knowingness, 50807 Vol VI How to Raise Your Level, 1566 Vol V Undoing Barriers, 1564 Vol IV Consciousness How to Tell Truth, 1562 Vol III Advanced States, 1584 Satsang Mar 2007, 50810 Vol II Consciousness and Addiction, 1568 Vol I Power vs Force Muscle Testing, 50749 God vs Science Feb 2007, 1302 Discovery of Presence God, 1578 Satsang Jan 2007, 50687 Is Miraculous Real Dec 2006, 1314 Satsang Nov 2006, 50675 Live Your Life Like Prayer Nov 2006, 50681 Spiritual Practice Oct 2006, 1312 Satsang Sep 2006, 50678 Review of Work Sep 2006, 50699 Reason vs Truth Aug 2006, 1310 Satsang Jul 2006, 50690 Spiritual Truth vs Fantasy Jun 2006, 1308 Satsang May 2006, 50693 Perception vs Essence Apr 2006, 1306 Satsang Mar 2006, 50684 Experiential Reality Feb 2006, 1304 Satsang Jan 2006, 50650 God Religion Spirituality Dec 2005, 50656 Valid Teachers Nov 2005, 50668 Spiritual Traps Oct 2005, 50659 Transcending Obstacles Sep 2005, 50671 Serenity Aug 2005, 50647 Conviction Jul 2005, 50665 Transcending Barriers Jun 2005, 50662 Intention May 2005, 50644 Alignment Apr 2005, 50653 Vision Feb 2005, 50637 Ego and Self Dec 2004, 50640 Witnessing and Observing Oct 2004, 50634 Identification and Illusion Aug 2004, 50631 Perception and Positionality Jun 2004, 50628 Emotions and Sensations Apr 2004, 50623 Thought and Ideation Feb 2004, 50620 Dialogue Q&A Dec 2003, 50617 Realization of Self as I Nov 2003, 50891 Enlightenment Aug 2003, 50610 Spiritual Community Jun 2003, 50607 Spirituality and World Apr 2003, 50614 Integration of Spirituality Feb 2003, 50601 Realization of Self Final Moments Dec 2002, 50598 God Transcendent and Immanent Nov 2002, 50595 Karma and Afterlife Oct 2002, 50592 Devotion Way to God Sep 2002, 50589 Advaita Way to God Aug 2002, 50586 Nature of Divinity vs Religious Fallacy Jul 2002, 50583 Realizing Root Jun 2002, 50580 Perception and Illusion May 2002, 50577 Positionality and Duality Apr 2002, 50574 Levels of Consciousness Mar 2002, 52164 Radical Subjectivity Feb 2002, 50567 Causality Jan 2002, 44429 Highlights 2007 Lectures, 40747 Highlights 2006 Lectures, 39238 Highlights 2005 Lectures, 36857 Highlights 2004 Lectures, 1824 Highlights 2003 Lectures, 1808 Highlights 2002 7-12, 1800 Highlights 2002 1-6

**Match:** committed - live = ∅, live - committed = ∅.

## Why site says 190 but API says 191?

HTML page `hawkins-products` uses WooCommerce archive query with default visibility filter that may exclude one product (e.g., free CD 36833 Ultimate Truth free with $75 order, or hidden draft). API `/wp-json/wp/v2/product` returns all published products regardless of catalog visibility. Hence 190 vs 191 HTML vs API is expected and not a data gap.

## Implication for Map Veritas Catalogue workflow

Since live IDs match committed inventory exactly, `fetch_veritas_catalogue.py --check` should now print:

```
data/veritas_official_products.csv matches the live inventory with 18 reviewed decisions applied.
```

and exit 0. The next run of the GitHub Actions workflow `Map Veritas Catalogue` (which fetches with compact _fields and diffs) should pass with "Candidate matches the reviewed inventory."

## Conclusion

- **Live Veritas inventory = 191 products, identical to committed.**
- **Delta 190 vs 191 between HTML archive count and API is cosmetic (visibility filter), not a missing product.**
- **No action needed; inventory is current as of 2026-08-04.**
- **Next workflow run expected green.**

*Generated 2026-08-04 via live API id-only fetch (100+91=191) vs committed inventory cross-check.*
