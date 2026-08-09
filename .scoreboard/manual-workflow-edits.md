# Manual Workflow Edits

GitHub Actions workflow edits may need to be performed manually in the GitHub
web editor.

## Policy

Agents must not edit `.github/workflows/*` unless explicitly instructed by
the user. If workflow changes are needed, they are documented here with exact
steps, and the affected scoreboard aspects are marked
`blocked_manual_workflow_edit`.

## Needed Manual Edits

No manual workflow edits currently required.

- `.github/workflows/ci.yml` — current (runs all checks, coverage gate, 26
  browser specs; green on `main`).
- `.github/workflows/update_spreadsheet.yml` — current (regenerates
  `docs/data.json` on raw-CSV pushes / manual dispatch).
- `.github/workflows/map_veritas_catalogue.yml` — current (review-only
  refresh with artifact diff).

If the owner later wants, for example, a scheduled audit reminder, a
scoreboard-staleness CI check, or branch protection enforcement, the exact
patch would be added here first for the owner to apply in the web editor.
