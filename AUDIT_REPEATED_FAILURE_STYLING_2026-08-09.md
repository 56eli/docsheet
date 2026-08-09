# Audit: Repeated Agent Failure — Styling Regression & Row Groups
> **Status correction (2026-08-09): Historical checkpoint, not current frontend/deployment truth.** PR #54 found that all 70 custom Tabulator rules used the dead descendant root `#spreadsheet .tabulator`; Tabulator attaches `.tabulator` to `#spreadsheet` itself. Current evidence, test counts, CI/Pages findings, and acceptance status live in [`docs/audits/2026-08-09-end-user-row-delivery-postmortem.md`](docs/audits/2026-08-09-end-user-row-delivery-postmortem.md). Point-in-time data findings below remain historical evidence.


**Date:** 2026-08-09  
**Branch:** `arena/019fe767-docsheet` @ `c884138` (single-commit history)  
**Trigger:** Owner reports (1) big regression to awkward blueish GitHub Page when before it had perfect grey-black scheme, (2) ~4 sessions no agent succeeded changing sheet rows from flat alternating greys to sleek greys with accented group per REVISION1.

> This is an **audit + plan**. No implementation in this ticket — plan only, to be approved before edits.

## 1. Why history is opaque (and why the bug recurs)

The repository on this host is a squashed single-commit (`c884138` is the only rev). `git log --follow docs/style.css` shows only the merge commit. All incremental style changes live only in `.scoreboard/history.md` summaries and PR descriptions, not in inspectable diffs here. That makes "what was the perfect grey-black?" unanswerable from `git diff` alone — agents have been guessing from handoff prose rather than from a committed baseline.

**Consequence:** Each agent re-invents the palette from scratch. No `docs/style.css` snapshot of the known-good neutral scheme was tagged, so regressions are invisible at review.

## 2. What the current stylesheet actually does

### 2.1 Palette is slate-blue, not neutral grey

| Token | Light (current) | Dark (current) | What neutral grey-black would be |
|---|---|---|---|
| `--bg` | `#f8fafc` (slate-50, blue 2%) | `#0f172a` (slate-900, saturated blue) | `~#f5f5f5 / #f9f9f9` (0 chroma) & `~#121212 / #0f0f0f` |
| `--surface` | `#ffffff` | `#1e293b` (slate-800 blue) | `#ffffff / #1a1a1a` or `#1d1d1d` |
| `--surface-2` | `#f1f5f9` (slate-100) | `#333b45` (odd warm-slate — not even in the same scale) | `#f3f3f3 / #252525` |
| `--border` | `#e2e8f0` (slate-200) | `#334155` (slate-700) | `~#e5e5e5 / #2a2a2a` |
| `--text` | `#0f172a` | `#f8fafc` | similar but warmer |

Every surface/border is drawn from Tailwind **slate** (hue ~210). On a calibrated display that reads as a cold, blueish page — the "perfect grey black" the owner remembers was hue 0 (neutral). The last session's PR title claims it "eliminated conflicting duplicate :root overrides that caused flat monochrome #1d1d1d/#1a1a1a alternating dark-grey zebra rows" — i.e. it *removed* the neutral greys and replaced them with slate. That matches the reported regression.

Evidence in `docs/style.css`:

```css
:root { --bg:#f8fafc; --surface:#ffffff; --surface-2:#f1f5f9; --zebra:#ffffff; }
:root.dark { --bg:#0f172a; --surface:#1e293b; --surface-2:#333b45; --zebra:#1e293b; }
```

`--zebra` equals `--surface` in both modes, so there is **no alternating stripe at all** — the table is a flat white / flat slate field with only faint 4% tints to differentiate blocks.

### 2.2 FINDING R-01 — Alternating grey rows are frozen (the row problem agents keep missing)

**Symptom (owner report):** Sheet rows remain flat alternating greys despite 4 sessions of "sleek greys with accented group" tickets. No visible change across implementations.

**Root cause — three stacked defects that cancel each other:**

1. **Zebra disabled by token equality.** `--zebra` was intentionally set to equal `--surface` in both modes (light `#ffffff==#ffffff`, dark `#1e293b==#1e293b`). The intent per last session's commit message was "replaced harsh alternating striping with clean, modern card surfaces" — i.e. zebra was *deliberately* deleted. Every subsequent agent treated that as the new design direction and left it, so the base alternating greys never returned. A correct sleek zebra needs `--zebra` distinct but close (e.g. `#ffffff`/`#f7f7f7` light, `#1a1a1a`/`#1e1e1e` dark); current file has none.

2. **Block washes are render-layer dead code.** The per-block rules target `.tabulator-row.row-block-*` with `background-color: var(--block-*-bg)` at `rgba(...,0.04)` light / `0.08` dark. On a white (`#ffffff`) base, 4% is ~Δ luminance 10/255 — below the perceptibility threshold on most displays. In dark, 8% on `#1e293b` (itself blue) is equally invisible; the eye reads it as flat. The rule exists but paints nothing the owner can verify. Agents kept lowering opacity ("elegant translucent tints 0.04/0.08 with crisp 3.5px left accents" — `NEXT_AGENT_HANDOFF:15`) because they never measured contrast — each iteration became *more* invisible while the ticket stayed open.

3. **Specificity + Tabulator even-row interaction makes the wash doubly ineffective.** The stylesheet duplicates every block over two selectors:
   ```css
   .tabulator-row.row-block-lectures, .tabulator-row.tabulator-row-even.row-block-lectures { background: var(--block-lectures-bg); }
   ```
   Tabulator adds `tabulator-row-even` on alternating rows for its own zebra engine. When `--zebra == --surface`, the second selector is redundant — both match the same flat color. If an agent tries to re-enable zebra by changing `--zebra` alone, these rules *still* override it on every block row because both selectors carry `background-color` and sit after the zebra rule — the zebra becomes unreachable for 100% of rows that carry a block (which is all 362). In other words, even if someone fixes the token, the block rules immediately re-flatten the rows back to a ghost wash.

**Why agents are blind to it:** (a) No visual regression test — `column-layout.spec.js` checks column width/sort, not `getComputedStyle(row).backgroundColor`. (b) Agents validate in light mode on white, where 4% renders as white in screenshots. (c) The commit message frames "flat monochrome #1d1d1d/#1a1a1a alternating zebra → sleek card surfaces" as a *success*, so agents assume stripping zebra is the approved direction and never challenge the token equality. (d) 362 rows all carry a block (including `undecided` 46 rows + `fran-grace` 1), so there is no un-blocked row where zebra would still be testable — the failure covers 100% of the table.

**Correct behavior (what owner asked for):** Neutral zebra first, block accent second. Light: `odd #ffffff`, `even #f7f7f7` (or `#f9f9f9`), each with `background: color-mix(left-accent-color 6%, zebra)` fallback or layered `background: var(--block-bg)` *over* the zebra via `background-image`. Dark: `odd #1e1e1e`, `even #252525`, with `rgba(...,0.10–0.12)` wash. Left border `3.5–4px` must be visible on both zebra stops. Acceptance is screenshot of alternating greys with accent border — not "flat white."

### 2.3 Group accent implementation — remaining defects beyond R-01

```css
--block-lectures-bg: rgba(5,150,105,0.04);  /* light: 4% */
:root.dark --block-lectures-bg: rgba(52,211,153,0.08); /* dark: 8% */
.tabulator-row.row-block-lectures-2002-2011 {
  background-color: var(--block-lectures-bg);
  border-left: 4px solid var(--block-lectures);
}
```

- **Opacity too low.** 4% on white is ΔE < 2 — invisible unless you stare at the left border. Dark 8% is only marginally better. Earlier proposals (PRESENTATION_UX_PROPOSAL, archive notes) suggested translucent tints but never specified contrast targets; agents kept lowering opacity to look "sleek" until it vanished.
- **Left border clips.** Tabulator rows are `overflow:hidden` + `border-radius` on the table; the 4px border is inside row box, not outside, so it is partially clipped by cell borders on the first column.
- **Specificity tie with Tabulator zebra.** Selector is `.tabulator-row.row-block-xxx` and `.tabulator-row.tabulator-row-even.row-block-xxx`. Tabulator also toggles `tabulator-row-even` for zebra — but since zebra is disabled (same color), the two selectors are identical and the even rule is redundant. If zebra is re-enabled, the order matters; current stylesheet places these rules *before* some later overrides, risking Tabulator's own `:nth-child` style winning.
- **`--surface-2` outlier.** Dark `--surface-2: #333b45` is not in the slate scale (should be ~`#283548` or `#242d3b`). Mixed warmness adds a second blue-grey inconsistency.
- **No neutral fallback.** "Sleek greys with accented group" asks for: a *subtle* neutral zebra (e.g. `#ffffff` / `#f9f9f9` light, `#1e1e1e` / `#262626` dark) so the eye can track rows, plus a *side accent* (or very light wash) per REVISION1 block. The current sheet has neither — flat field with ghost tints is neither sleek nor scannable.

### 2.4 Why 4 sessions failed on rows specifically (separate from blue)

1. No committed "good" CSS snapshot to diff against — agents edit blind.
2. Competing `:root` blocks (one at line 6, another at line ~380) — the earlier "elimination of duplicate :root overrides" left a single definition, but the *intended* neutral greys were removed with it. Later agents won't re-add them for fear of "duplicates".
3. Acceptance criteria are prose ("sleek greys with accented group according to recent revision") with no visual spec (no Figma/hex, no contrast ratio). Agents pick slate because it's the default Tailwind "modern" look.
4. No screenshot/snapshot test in `tests/` — `column-layout.spec.js` checks sort/width, not color. So CI never catches blue vs grey.

## 3. What "correct" should look like (inferred from owner description + REVISION1)

- **Neutral page chrome:** `--bg`/`--surface`/`--border` with **0 chroma** (grey), not slate blue. Light: `#f5f5f5`–`#ffffff` family. Dark: true greys `#121212` / `#1e1e1e` / `#262626` — not `slate-900`.
- **Rows:** *Subtle* neutral zebra — light: `#ffffff` ↔ `#f7f7f7` (or `#f9f9f9`); dark: `#1e1e1e` ↔ `#262626`. Keep hover slightly darker. This is "sleek greys" — readable but not candy-striped.
- **Group accent:** 3.5–4px left border in block hue + *faint* wash (6–10% light / 10–14% dark) so rows remain grey-first, accent-second. Wash must survive both zebra backgrounds (blend, not opaque).
- **11 REVISION1 blocks** (lectures → discussion → satsang → on-the-road → volume → office → books → transcription → media-misc → undecided → Fran Grace) each get one hue; undecided stays muted; Fran Grace stays distinct but not screaming red.

## 4. Plan (proposed, needs approval)

### Phase 0 — Establish baseline before any CSS edit

- Tag or commit the *current* `docs/style.css` as `docs/style.css.baseline` or `git tag style-baseline` so future agents can `diff` regressions.
- Add a tiny `tests/style-tokens.spec.js` or `test_style_tokens.py` that asserts page tokens are neutral (e.g. `chroma < 8` for `--bg`/`--surface`/`--border` or exact hex allowlist). This is the gate that would have caught the blue regression.

### Phase 1 — Neutralise the palette (single commit, easy to revert)

Replace only the `:root` / `:root.dark` token blocks:

```css
:root {
  --bg: #f5f5f7;
  --surface: #ffffff;
  --surface-2: #f2f2f3;
  --zebra: #f7f7f7;          /* was #ffffff → flat */
  --border: #e5e5e7;
  --header-bg: #fafafb;
  /* ... accent stays #188038 */
}
:root.dark {
  --bg: #0f0f0f;
  --surface: #1a1a1a;         /* was #1e293b */
  --surface-2: #252525;
  --zebra: #1e1e1e;           /* was #1e293b → flat */
  --border: #2a2a2a;
  --header-bg: #1e1e1e;
}
```

Keep block hues unchanged; only chrome becomes grey-black. Verify in light+dark screenshots.

### Phase 2 — Restore sleek zebra + tune block washes

- Re-enable zebra via Tabulator row rule:

```css
#spreadsheet .tabulator .tabulator-row.tabulator-row-even { background: var(--zebra); }
#spreadsheet .tabulator .tabulator-row:hover { background: var(--row-hover) !important; }
```

- Raise block washes to visible but still sleek:

```css
--block-lectures-bg: rgba(5,150,105,0.07);      /* was 0.04 */
:root.dark --block-lectures-bg: rgba(52,211,153,0.12); /* was 0.08 */
/* same pattern for other 10 blocks: 0.07 light / 0.12 dark ± hue */
```

- Ensure border is not clipped: `border-left: 4px solid var(...)` + `box-sizing:border-box` + verify first cell `border-right` doesn't overlap (add `margin-left:-1px` test if needed). Keep specificity higher than Tabulator zebra: order after `tabulator-row-even`.

### Phase 3 — Guard against recurrence

- Add a Playwright visual-snapshot spec (or at least a computed-style assertion for `getComputedStyle(document.documentElement).getPropertyValue('--bg')`) to CI — fails when someone re-introduces slate.
- Document the palette decision in `INSTRUCTIONS.md` or a `docs/STYLE_TOKENS.md`: "Chrome is neutral grey (chroma 0); chromatic color only in block accents / accent emerald."
- Update `NEXT_AGENT_HANDOFF.md` with "known-good palette" hex list to prevent future slate drift.

### Alternatives considered

- Full redesign (e.g. adopt Linear/Stripe dark neutrals completely) — rejected: owner asked for restoration of previous perfect scheme, not a new brand.
- Keeping slate and just fixing rows — rejected: slate *is* the blueish regression; fixing rows alone won't restore grey-black.

## 5. Risks & open questions

- Owner may actually prefer *some* warmth in neutrals (e.g. `#f8f7f5` warm grey) — need a yes/no: **pure neutral (chroma 0) or warm grey?** Pure neutral is the safest interpretation of "grey black".
- `color-mix()` blocks elsewhere in the sheet inherit from `--surface`; neutralising will desaturate those too — intentional, but verify focus rings still meet contrast.
- Dark mode `--row-hover` currently `#283548` (slate) — will need neutral `#333333`.

## 6. Acceptance criteria (for the implementation PR)

- [ ] No `--bg`/`--surface`/`--border` token contains visible blue hue (verify by `color` chroma check or manual hex review — e.g. `F8FAFC` must not appear).
- [ ] Row zebra is visible and neutral: light even rows `#f7f7f7` ±1, dark `#1e1e1e`; no flat white-on-white.
- [ ] 11 block accents render in both modes: left border + faint wash distinct from base zebra; Fran Grace distinct from undecided.
- [ ] All 132 tests + 6 `--check` + `node --check` + Playwright (CI) green.
- [ ] Screenshot or computed-style gate added so the blue regression cannot recur undetected.
