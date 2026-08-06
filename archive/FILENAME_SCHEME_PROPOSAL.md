# Filename Scheme — Proposal to make local copies actually usable

**Date:** 2026-08-04  
**Status:** Proposal — no code/data changed yet (follow-up to `CATALOGUE_READABILITY_ROADMAP.md`)  
**Problem:** docsheet's purpose is to make *all* Hawkins material findable in a sophisticated way, but its current public titles are archival-fidelity and hostile as filenames:  

- `Power vs Force.pdf` — easy
- `The Levels of Consciousness: Subjective & Social Consequences (Mar 2002) DVD01` + `The Way to God: The Nature of Divinity vs. Religious Fallacy (Audiobook)` — redundant, long, contains `:` `/` `&` illegal on Windows, buries the thing a human actually remembers (“oh yeah, that Feb 2004 talk”).

We need *two truths at once*: the catalogue must stay complete/accurate, but the *filesystem name* must be short, sortable, memorable, and still traceable back to the catalogue.

---

## 1. What humans actually remember

From community usage + how titles are spoken:

- **Books:** remembered by *work title* + *year first published* → `Power vs Force (1995)`
- **Lecture series (2002-2011):** remembered by *year-month* + *theme* or *monthly topic* → “Feb 2004 — Thought and Ideation”, “June 2003 — Spiritual Community”
- **On-The-Road talks:** remembered by *year* + *quirky title* → “2003 — Progressive Levels of Consciousness — Oxford special”
- **Volume series / single discs:** remembered by *Volume* + *topic* → “Vol I — Power vs Force” or “Vol II — Consciousness and Addiction”
- **Discussion / Interview:** remembered by *year* + *topic* → “2012 — Permanent Inner Peace”
- **Multi-part works:** 3 DVDs share same Veritas product URL (e.g., Causality Jan 2002) — user needs `DVD01 / DVD02 / DVD03` disambiguator but not in the *primary* name.

Current `title` mashes all of that together: `2002-01-Causality: The Ego's Foundation (Jan 2002) DVD01` carries date three times and part info twice.

### Implication

Filename should be:

1. **Sortable** — lexicographic sort = chronological within series
2. **Unique** — no collision even for 3-part Volume sets
3. **Human-scannable** — year first, then short title, not essay-length
4. **Safe** — no `: / \ ? % * | " < >` ; max ~80 chars before extension
5. **Reversible** — can map filename → master UUID without guesswork

A single filename cannot also be a bibliography entry. We solve with *layers*: short filename + sidecar JSON + folder hierarchy.

---

## 2. Design: three filename profiles

Don't force one compromise. Generate three derived names per master row from the same rule engine.

### Profile A — `canonical` (archival, for scripts)

For ingest, dedup, hardlink trees. Always unique, always reversible.

```
{uuid}__{catalog_code}__{work_id}__{safe_slug}.ext
```

Example:

```
202__LECTURE-2004-022__w-thought-and-ideation__thought-and-ideation__DVD01.mp4
286__BOOK-1995-001__w-power-vs-force__power-vs-force.pdf
320__BOOK-1995-001A__w-power-vs-force__power-vs-force__audiobook.m4b
```

- `uuid` guarantees uniqueness even if everything else collides
- Machine-parseable with `__`
- Never shown to end users, but used as the ground-truth key in `filename_mapping.csv`

### Profile B — `human` (recommended default for local library)

For humans browsing in Finder/Explorer/VLC. What you asked for — “oh yeah that 2004 one”.

```
{Year}[-{Month}] {SeriesAbbr} - {ShortTitle} [{EditionDetail}].{ext}
```

Rules:

- **Year** mandatory when present (271 codes have year). Month optional (when known)
- **SeriesAbbr** from a curated 3-6 char map (see §3) — not the full 40-char series string
- **ShortTitle** = first 5-7 words of cleaned public title, truncated at 48 chars, no subtitle after `:` / `—` unless needed for uniqueness
- **EditionDetail** only when disambiguating multi-part: `DVD01`, `DVD02`, `Audiobook`, `CD set`, etc. Omitted for single-part.
- Extension from `format` → `mp4` for DVD, `mp3/m4b` for audiobook/CD, `pdf` for book

Examples (real master rows):

```
Books:
  1995 - Power vs Force.pdf
  1995 - Power vs Force [Audiobook].m4b
  2001 - The Eye of the I.pdf
  2021 - The Ego is Not the Real You.pdf

Lectures ( yearly series ):
  2002-01 WTG - Causality [DVD01].mp4
  2002-01 WTG - Causality [DVD02].mp4
  2004-02 TM - Thought and Ideation [DVD01].mp4
  2004-02 TM - Thought and Ideation [DVD02].mp4
  2005-06 NI - Transcending Barriers [DVD01].mp4

On-The-Road:
  2003 OTR - Progressive Levels of Consciousness - Oxford [DVD].mp4
  2004 OTR - Spiritual Reality [CD].mp3
  2005 OTR - The Prevailing Silence [CD].mp3

Discussion:
  2012 DS - Permanent Inner Peace [DVD].mp4
  2012 DS - What is Real Success [DVD].mp4

Office / Satsang:
  1982 OS - Worry Fear Anxiety [CD].mp3
  2006-01 SATSANG - Jan 2006 [CD01].mp3
```

Why it works:

- **Sorts chronologically** even in flat folder: `2002-01 ...`, `2002-02 ...`, `2004-02 ...`
- **Scannable:** year jumps out left; series abbr 3-4 chars tells you which run; title short enough for VLC list
- **Still connects:** short title contains the hook (“Causality”, “Thought and Ideation”) so user maps to memory
- **Unique without being verbose:** `DVD01/02` only when needed

### Profile C — `plex` (optional, for Jellyfin/Plex/Kodi)

Media servers want `Show/Season/Episode` hierarchy. Derive season = year, episode = month sequence or catalogue sequence.

```
Hawkins Lectures/
  Season 2002 - The Way to God/
    S2002E01 - Causality - DVD01.mp4
    S2002E01 - Causality - DVD02.mp4
  Season 2004 - Transcending the Mind/
    S2004E02 - Thought and Ideation - DVD01.mp4
Books/
  Power vs Force (1995) - Book.pdf
  Power vs Force (1995) - Audiobook.m4b
```

This profile reuses the same slugger but under a different folder root. Generates NFO sidecar with full Veritas URL, work_id, catalogue code.

**Recommendation:** implement Profile B as default, generate A+C as alternative columns in the same mapping file. User picks.

---

## 3. Supporting artifacts needed

### 3.1 Series abbreviation map

New reviewed input `data/series_abbreviations.csv`:

| series | abbr | parent | notes |
|--------|------|--------|-------|
| The Way to God | WTG | Lectures Series | yearly 2002 |
| Devotional Nonduality | DN | Lectures Series | 2003 |
| Transcending the Mind | TM | Lectures Series | 2004 |
| Nonduality Intensive | NI | Lectures Series | 2005 |
| Transcending Levels of Consciousness | TLC | Lectures Series | 2006 |
| Spiritual Reality & Modern Man | SRMM | Lectures Series | 2007 |
| Advanced Spiritual Awareness | ASA | Lectures Series | 2008 |
| In the World but Not of It | IWBN | Lectures Series | 2009 |
| Practical Spirituality | PS | Lectures Series | 2010 |
| Love & Spiritual Seeker Qualities | LSSQ | Lectures Series | 2011 |
| On The Road Talk Series | OTR | — | umbrella |
| Office Series | OS | — | |
| Satsang Series | SATSANG | — | |
| Discussion Series | DS | — | |
| Volume Series | VOL | — | |
| Books | BOOK | — | keep for grouping, but abbr not used in filename root |
| Media Miscellaneous | MISC | — | untyped 246 lives here pending ruling |

Controlled vocabulary, validated, never inferred from titles.

### 3.2 Title shortener

Deterministic function `short_title(title)`:

- Start from *cleaned* public title (already stripped of `PART1`/`DVD01`/`-converted`/`.mp4` where official match exists)
- Take substring before first `:` / `—` / ` - ` / `(` that introduces location/date
- Keep first 5-7 words (hungry but stop before 48 chars)
- Title-case, filesystem-safe: replace `:` `"` `?` `*` with ` - ` or remove; collapse whitespace; strip trailing `.`

Edge: Volume series — keep `Vol I`, `Vol II` as prefix because it is the remembered key: `Vol II - Consciousness and Addiction`.

### 3.3 Safe filename builder

Shared helpers in `_common.py`:

```python
ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
def safe_filename(s: str, max_len=80) -> str:
    s = ILLEGAL.sub('', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:max_len].rstrip(' .')
```

Uniqueness guard: after building Profile B name, check `Counter` of all names per folder — on collision, append ` [{EditionDetail}]` or `[2]` counter.

### 3.4 Filename mapping output

New generator `build_filenames.py` → `data/filename_mapping.csv` + `docs/filenames.json`:

| uuid | work_id | catalog_code | year_month | series | format | canonical | human | plex_path | short_title | safe_slug |
|------|---------|--------------|------------|--------|--------|-----------|-------|-----------|-------------|-----------|
| 1 | w-causality | LECTURE-2002-001 | 2002-01 | The Way to God | DVD | ... | `2002-01 WTG - Causality [DVD01].mp4` | ... | Causality | causality |

And `docs/catalogue-meta.json` augmented with `filename_profiles: ["canonical","human","plex"]`.

Already covered by existing pipeline — new file is consumed by `build_catalogue_pages.py` for a new Frontend tab **Filenames**.

---

## 4. Folder hierarchy (local organizer)

Flat folder with 356 files is unwieldy; nested is better. Propose two hierarchy modes (user choice):

**By Year (for “that 2004 one” browsing):**

```
Hawkins Archive/
  1995/
    1995 - Power vs Force.pdf
    1995 - Power vs Force [Audiobook].m4b
  2002/
    2002-01 WTG - Causality [DVD01].mp4
  2004/
    2004-02 TM - Thought and Ideation [DVD01].mp4
```

**By Series (for thematic browsing):**

```
Hawkins Archive/
  Books/
  The Way to God (2002)/
  Transcending the Mind (2004)/
  On The Road Talk Series/
  Satsang Series/
```

Implementation: a tiny local script `organize_files.py --hierarchy year --profile human --source ~/Downloads/Hawkins --dest ~/Hawkins --link hard` that reads `filename_mapping.csv` and creates hardlinks (no copy) with suggested names + sidecar `.json` per file carrying UUID, work_id, source URLs, Notes.

Hardlinks preserve disk space, keep original filenames untouched, filesystem remains reversible to catalogue.

---

## 5. Roadmap — 5 phases, no breaking changes

### Phase 0 — Decisions (owner, 30 min, no code)
1. Confirm **Profile B** as default human profile (Year[-Month] Abbr - ShortTitle [Detail])
2. Approve **series abbreviation table** (3-6 chars) — does `WTG`, `TM`, etc feel right? Alternative: full yearly name abbreviated differently?
3. Confirm **short title rule** (5-7 words, 48 char cap, keep Vol I/II prefix)
4. Choose **folder hierarchy default**: Year vs Series? Or offer both via organizer flag?
5. Confirm **edition detail UX**: show `[DVD01]` only for multi-part, or always?
6. Decide if books grouped under `Books/` or by year?

### Phase 1 — Data inputs (low effort, 1 file + 1 helper)
- Add `data/series_abbreviations.csv` (reviewed, validated)
- Add helpers to `_common.py`: `safe_filename`, `short_title`, `series_abbr`, `format_to_extension`
- Unit tests: illegal char removal, max len, uniqueness, extension mapping

### Phase 2 — Generator (medium effort)
- New `build_filenames.py` with `--check` mode (mirrors other generators)
- Consumes: research_master_draft, work_families, series_abbreviations, series_taxonomy (for yearly name if we decide yearly display)
- Outputs: `data/filename_mapping.csv` (reviewable), `docs/filenames.json`, `docs/filename-meta.json` (collision warnings, truncated count, max len)
- Validation: filenames unique per profile per folder, no illegal chars, no Windows reserved names (`CON`, `PRN`, etc), ≤80 chars (configurable), extension matches format
- Integrate into `build_catalogue_pages.py`: new **Filenames** tab exposing canonical/human/plex + sidecar metadata + copy-to-clipboard
- Add doc-currency test: mapping rows = master rows 356; human filenames unique

### Phase 3 — Frontend (low-medium)
- New Tab **Filenames** (after Everything) showing Suggested Filename (Human), Plex Path, Canonical, Short Title, extension
- Row drawer adds **Copy filename** button + sidecar JSON preview
- Footer stats: show max filename length, collisions resolved
- No editing — filenames are derived, corrected only via reviewed abbreviation input

### Phase 4 — Local organizer script (low-medium)
- `organize_files.py` — standalone, uses only stdlib + mapping CSV
- CLI: `--profile human|canonical|plex --hierarchy year|series --source DIR --dest DIR --mode copy|hardlink|symlink --dry-run`
- Generates sidecar `.json` per file: `{uuid, work_id, catalog_code, title, legacy_title, source_url_veritas, ...}`
- README docs: how to use with existing downloads without re-downloading

### Phase 5 — Docs & migration (low)
- Update README / INSTRUCTIONS with filename scheme + organizer usage
- Add `FILENAME_SCHEME.md` (final spec) distinct from this proposal; archive proposal
- Add regression tests for filename length, safety, and collision handling
- Optional: publish `docs/filenames.csv` export for spreadsheet filters

---

## 6. Examples — before vs after (real catalogue rows)

Current title → proposed human filename (Profile B):

| uuid | Current public title | Proposed human filename | Note |
|------|----------------------|-------------------------|------|
| 1 | Causality: The Ego's Foundation (Jan 2002) DVD01 | `2002-01 WTG - Causality [DVD01].mp4` | short title, abbr |
| 22 | Thought and Ideation (Feb 2004) DVD01 | `2004-02 TM - Thought and Ideation [DVD01].mp4` | sortable |
| 221 | Progressive Levels of Consciousness - A Special Talk Presented in Oxford (2003) | `2003 OTR - Progressive Levels - Oxford [DVD].mp4` | truncated, still recognizable |
| 202 | Power vs Force: The Hidden Determinants of Human Behavior (Part 1) DVD01(?) actually Vol I | `VOL Vol I - Power vs Force [DVD01].mp4` or `1995 BOOK - Power vs Force.pdf` depending on work edition | Vol prefix kept |
| 286 | Power vs Force (book) | `1995 - Power vs Force.pdf` | dead simple |
| 320 | Power vs Force (Audiobook) | `1995 - Power vs Force [Audiobook].m4b` | year = work's first-pub year |
| 333 | The Way to God: The Nature of Divinity vs Religious Fallacy (Audiobook) | `2002 WTG - Nature of Divinity [Audiobook].m4b` | lecture audiobook, year from matched master |
| 316 | On The Road - Unity Church March 2005 | `2005-03 OTR - Unity Church March [CD].mp3` | year-month from Audible © |

Folder view with 2004 as folder:

```
2004/
  2004-02 TM - Thought and Ideation [DVD01].mp4
  2004-02 TM - Thought and Ideation [DVD02].mp4
  2004-04 TM - Emotions and Sensations [DVD01].mp4
  2004-06 TM - Perception and Positionality [DVD01].mp4
  2004-02 OTR - Spiritual Reality [CD].mp3   (if OTR mixed in same year folder, abbr disambiguates)
```

Browsing experience: Finder sorted by name → chronological; user scrolls to 2004, sees 4-5 memorable lines, not 4 essays.

---

## 7. Tradeoffs & why not other schemes

| Alternative | Problem |
|-------------|---------|
| Use full public title as filename | 80+ chars, illegal `:` `?`, duplicate date info, not sortable |
| Use only `catalog_code` e.g. `LECTURE-2004-022.mp4` | Perfectly unique & short, but zero human signal — user must look up mapping every time |
| Use only `short_title` e.g. `Thought and Ideation.mp4` | Collisions (same short title across years: “Causality” appears once, but “Love” appears many times?), not sortable |
| Use `work_id` e.g. `w-thought-and-ideation__DVD01.mp4` | Unique and groups editions, but work_id is technical, not memorable |
| Use legacy `LSyyyy nn_p` | Internal ordinal, not date-based, already known to be wrong for year-month distinction |
| Use full 200-char Veritas product URL slug | Redundant, still long, contains `vol-ii-` vs `Volume II` mismatch retained |

Chosen hybrid **Year + Abbr + ShortTitle + EditionDetail** combines all strengths: sort key = year, human hook = short title, disambiguator = abbr + detail, uniqueness = catalog_code sidecar.

---

## 8. Implementation sketch (no code yet, but shape)

```python
# build_filenames.py (future)
SERIES_ABBR = read_csv("data/series_abbreviations.csv")  # reviewed
def short_title(title: str) -> str:
    # use cleaned title, cut before ':'/'—'/'(' and first 5-7 words, 48 chars
    ...

def human_filename(row, abbr_map):
    ym = row["year"] + (f"-{row['month']}" if row["month"] else "")
    abbr = abbr_map[row["series"]]
    st = short_title(row["title"])
    detail = row["format_detail"] if needs_detail(row) else ""
    base = f"{ym} {abbr} - {st}" if ym else f"{abbr} - {st}"
    if detail:
        base += f" [{detail}]"
    ext = FORMAT_TO_EXT[row["format"]]  # DVD→mp4, audiobook→m4b etc
    return safe_filename(f"{base}.{ext}", 80)

# collision resolution
seen = Counter()
for row in master:
    name = human_filename(row, ...)
    if seen[name]: name = insert_counter(name, seen[name])
    seen[name]+=1
```

Validation checklist (part of `--check`):

- [ ] All 356 master rows have filename (all profiles)
- [ ] Human profile filenames unique (per folder mode)
- [ ] No illegal chars, no Windows reserved names
- [ ] ≤80 chars (config)
- [ ] Extension matches format vocabulary
- [ ] Plex profile paths use `Season YYYY` convention
- [ ] `data/filename_mapping.csv` byte-stable deterministic (twice)

---

## 9. Open questions for you (owner)

1. **Year-first vs Series-first in filename?** I propose year-first (`2004-02 TM - ...`) because your stated use-case is “that 2004 one”. Alternative is series-first (`TM 2004-02 - ...`) — better if users browse by series rather than year. Which feels more natural?
2. **Folder hierarchy default:** Year folders (`2004/`, `Books/`) or Series folders (`The Way to God (2002)/`)? Year is simpler for “that 2004 one”; Series is thematic.
3. **Length cap:** 80 chars before ext? 60? 100? Shorter = cleaner VLC list, but truncates more titles.
4. **Multi-part display:** Show `[DVD01]` always, or only when work has >1 part? Always is more explicit, only-when-needed is shorter.
5. **Books:** `1995 - Power vs Force.pdf` feels right, but do you want `BOOK 1995 - Power vs Force.pdf` prefix for sorting? Or keep books in separate `Books/` folder so prefix unnecessary?
6. **Edition grouping:** Should audiobook of same lecture sit next to DVD version via identical base name differing only `[Audiobook]` vs `[DVD01]`? Yes — proposed scheme groups by short title already.
7. **Sidecar:** JSON per file with full metadata, or single master `filename_mapping.json`? Both possible; sidecar is more resilient for offline USB sticks.
8. **Unicode:** Titles contain `–` en-dash, `“”` smart quotes — safe filename strips to `-` and `"` removed. OK, or keep Unicode (modern FS support Unicode but sorting differs)?

Pick 1-2 profiles to implement first; I recommend **Phase 0 decisions → Phase 1+2 minimal (human profile only, year hierarchy)** which solves 80% of the pain with <200 lines of new code and zero changes to existing master.

---

## 10. One-sentence pitch

A **year-first, abbr-middle, short-title-last** filename (`2004-02 TM - Thought and Ideation [DVD01].mp4`) derived from `catalog_code` + `series_abbr` + `short_title` + `format_detail` gives you a library that sorts chronologically, scans in VLC at a glance, stays unique, and still maps back to the full sophisticated catalogue via a sidecar JSON — you get “oh yeah that 2004 one” without losing “Power vs Force is 1995”.

*Next step: confirm the 8 owner decisions in §9, and I can implement `data/series_abbreviations.csv` + `build_filenames.py` + Filenames tab in one pass, all checks green.*
