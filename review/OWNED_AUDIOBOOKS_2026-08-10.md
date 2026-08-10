# Owned-status correction — audiobooks (2026-08-10)

## Owner instruction

Remove the `Owned` label from every curated record whose carrier `format` is
`audiobook`.

## What was corrected

The preceding change on PR #66 blanked `proposed_owned` for 41 unrelated
raw-ledger rows (raw rows 297 onward) and for the non-audiobook Power vs. Force
hardcover (master 373). That broad raw-row cutoff did not target the promoted
audiobook editions that render with `Owned`; it also changed unrelated DVD, CD,
streaming, and print-book ownership values. Those source edits were restored to
the immediately preceding reviewed state.

The correction is instead applied at the actual generated-master sources:

- `data/edition_candidates.csv`: cleared `proposed_owned` on 21 promoted
  audiobook candidates;
- `data/manual_master_candidates.csv`: cleared `proposed_owned` on the one
  promoted audiobook candidate, *How to Surrender to God*.

Five other audiobook candidates were already blank. Consequently all 27
curated `format=audiobook` records are blank/not-stated for `owned`. No
non-audiobook record’s ownership value changes under this correction.

## Verification expectation

Rebuild the curated master and Pages artifacts, then verify that the Everything
view contains 27 audiobooks with 27 blank `owned` values and that the prior
non-audiobook ownership distribution is restored.
