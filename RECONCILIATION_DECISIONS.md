# Research-Master Reconciliation Decisions

**Approved:** 2026-08-03  
**Scope:** Reconcile the curated research-master build without altering the preserved raw spreadsheet.

## Source associations

- Preserve the current inventory-verified official source associations through `data/research_master_source_overrides.csv`.
  - The initial reconciliation approved **32 Veritas** and **8 Audible** URLs; later book and date-specific Satsang reviews add **22 Veritas** URLs, for 62 approved source overrides.
  - Every URL is present in the committed official source inventory and has the recorded mapping evidence.
  - The generator only permits approved HTTPS additions to an empty Veritas or Audible source field on an existing ledger item; it cannot overwrite a raw-ledger value.
- *Live Your Life Like a Prayer* has two official Veritas products, now modeled in `data/product_relationships.csv`:
  - Keep the raw-ledger **November 2006** three-disc lecture-set URL as the primary master source URL for DVD01–DVD03.
  - Record the distinct **2012** one-DVD 60-minute interview as reviewed `related_material` for DVD01; it is not a replacement URL or a duplicate master item.

## CSV-only master records

The six records that existed only in the prior master CSV are not approved as current master items:

| Lead | Decision |
|---|---|
| *Qualitative and Quantitative Analysis and Calibration of the Level of Human Consciousness* (raw 368) | Retain as a ledger research lead pending title/year/identity evidence; if approved later, classify as `dissertation`, not `book`. |
| *Dialogues on Consciousness and Spirituality* (raw 371) | Retain as a ledger research lead; do not infer ownership from the Discord note. |
| *The Scorpion Book* (raw 375) | Retain as a ledger research lead pending identity evidence. |
| *Orthomolecular Psychiatry* (raw 376) | Retain one ledger research lead pending title/edition/authorship evidence; remove the duplicate derived CSV records. |
| *Power vs Force (Original old edition, non B&W cover)* | Retain outside the master in `data/research_manual_leads.csv`; no demonstrated content difference supports a separate item yet. |

This aligns the generated master CSV and JSON at 308 records while retaining every unresolved lead in a reviewable input.

## Rebuild order

```bash
python build_research_master.py
python build_catalogue_pages.py
python reconcile_research_master.py
python build_research_master.py --check
python build_catalogue_pages.py --check
python reconcile_research_master.py --check
```

The raw CSV is not an input modified by this sequence. The resulting Pages JSON reflects the reviewed master and source associations.
