# Final registry crosscheck — `final_registry.csv` × `docs/master.json`

Deterministic, offline crosscheck of the owner's personally-owned file
registry (259 files) against the published curated master (363 rows).
This is an **evidence-only analysis**: no `owned` value, master row, or
other frozen surface was modified — every suggested ruling below is
listed for the owner to decide, never applied.

## 1. Scope

- Registry rows: **259** files, 184.7 GB total
- Registry folders: `Audiobooks` 122, `Lectures2002-2011` 66, `PDFsandEPUBs` 18, `more` 16, `Satsangs` 11, `Ontheroad` 10, `Archivalofficeseries` 6, `VolumeSeries` 6, `DocandSusantalks` 4
- Registry mime types: `audio/x-m4b` 106, `video/mp4` 93, `audio/mpeg` 24, `application/pdf` 23, `application/epub+zip` 12, `application/x-zip` 1
- Master rows: **363** (`owned`: blank 49, false 25, true 289)

## 2. Methodology

### Why slug-exact matching cannot work

Registry filenames are slug-style **without** a month prefix, while
Veritas slugs are month-prefixed and `proposed_filename` follows the
`YYYY-MM - Title [n-m].mp4` scheme. Live examples from the two inputs:

- Registry `VolumeSeries/volume-i-power-vs-force.mp4` ↔ master 202
  `Volume I: Power vs. Force Muscle Testing`; Veritas slug `volume i power vs force muscle testing`;
  `proposed_filename` `Volume_I_Power_vs._Force_Muscle_Testing_[1-2].mp4`.
- Registry `DocandSusantalks/what-is-meant-by-spiritual--the-importance-of-family-2014.mp4`
  ↔ master 283 `What is Meant by Spiritual`; Veritas slug `what is meant by spiritual`;
  `proposed_filename` `2012_DISCUSSION_What_is_Meant_by_Spiritual.mp4`.

Exact slug-to-slug equality therefore fails in general; normalized-title
matching with folder/series priors is the bridge.

### Normalization

Unicode NFKD fold + casefold + combining-mark removal; apostrophes
deleted (`Ego's` → `egos`, matching slug `egos`); `[...]` product IDs
(ASIN/ISBN) stripped; remaining punctuation → spaces; whitespace
collapsed. Two key forms per name: *compact* (spaces removed, the
CamelCase bridge: `TheEyeoftheI` → `theeyeofthei`) and *content*
(stopwords also removed: `The Ego and The Self` → `theegotheself`).
Trailing date suffixes (`-2014`, `June 2003`, glued `June2003`) and
author markers (`… by David R. Hawkins`, `… Hawkins, David R.`) are
stripped into additional comparison variants.

### Matcher tiers

| Tier | Rule | Fires when |
|---|---|---|
| T1x | exact key equality | a normalized registry name/segment equals a normalized master `title` (full or pre-colon head, edition-marker-stripped), `proposed_filename` stem, or `source_url_veritas` slug tail |
| T1p | exact after prefix strip | a known collection prefix (`On the Road…`, `Volume…`, `Satsang…`, `Office Visit…`, `Devotional Nonduality Intensive…`, …) is removed in compact space and the remainder equals a master key |
| T1c | containment | a master key (>=12 chars) sits inside the registry name, or a registry key (>=12 chars) sits inside a master key |
| T1f | fuzzy equality | compact forms score >= 0.90 (difflib `SequenceMatcher`, gated by length distance and quick ratios) |
| T2ym | lecture year-month | `Lectures2002-2011/<month>-<year>.mp4` maps to the unique annual-series work of that year-month |
| T2sm | satsang month list | names carrying >=2 month tokens + a year (`satsang-qa-jan-mar-jul-2011`) map to the Satsang Series session(s) of those months |
| T2vol | volume numerals | `VolumeSeries/volume-<roman>…` maps to the Volume Series work(s) of that numeral |
| T2t | token + prior scoring | significant-token overlap (greedy one-to-one, fuzzy at 0.85; 0.80 for tokens >=9 chars) plus a 0.25 boost from folder↔series or name-prefix priors |

Thresholds: **A** = top score >= 0.85 with no different-work rival within 0.10; **B** = top score >= 0.55 (or any ambiguous exact hit); **C** = nothing at or above the B floor. T1-channel exact matches carry
confidence 1.00. Scores print with fixed two-decimal formatting; sort
orders are stable and no timestamps enter the outputs, so regeneration
is byte-reproducible (`--check`).

### Grouping rules (T3)

- Double-dash names (`…--…`) split into per-work **segments**, each
  matched independently; one file covering several works stays ONE row
  listing every matched work (e.g. the six `Archivalofficeseries` files
  cover all 16 Office Series masters two-to-three titles at a time).
- `part1`/`part2` suffixes are stripped before matching so both parts of
  a split recording resolve to the same single master work.
- Master rows are grouped by `work_id` (the work × carrier edition
  model): a file matching a work counts once, whether the work holds 1
  or 40 master rows, so no edition family is reported as N discrepancies.
- Bucket-C files with identical normalized names (same title, different
  extension/brackets) collapse into one review family.

## 3. Bucket counts

| Bucket | Meaning | Files |
|---|---|---|
| A | matched to master work(s), high confidence | 234 |
| B | ambiguous — owner review queue | 11 |
| C | registry-only, no plausible master counterpart | 14 |
| **A+B+C** | must equal the registry row count | **259 / 259** |

Bucket A by registry folder: `Audiobooks` 108, `Lectures2002-2011` 66, `PDFsandEPUBs` 18, `more` 15, `Ontheroad` 10, `Archivalofficeseries` 6, `VolumeSeries` 6, `DocandSusantalks` 4, `Satsangs` 1

## 4. Owner review queue — bucket B (rules to decide, nothing applied)

| Registry file | Folder | Top tier/conf | Top candidates (uuid, title, score) |
|---|---|---|---|
| `Satsangs/SatsangSeries-VolumeI/SatsangSeries,VolumeI[B00BOV7ODK].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeries-VolumeII/SatsangSeries,VolumeII[B00BOV9X8E].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeries-VolumeIII/CopyofSatsangSeries,VolumeIII[B00BOV7JE4].mp3` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeries-VolumeIII/SatsangSeries,VolumeIII[B00BOV7JE4].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeries-VolumeIV/SatsangSeries,VolumeIV[B00BOV8VXW].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeries-VolumeV/SatsangSeries,VolumeV[B00BOV9RUS].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeries-VolumeVI/SatsangSeries,VolumeVI[B00BOVA7Z2].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeries-VolumeVII/SatsangSeries,VolumeVII[B00BOV9W26].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeries-VolumeVIII/SatsangSeries,VolumeVIII[B00BOV8K4C].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `Satsangs/SatsangSeriesVolumeIX/SatsangSeriesVolumeIX[B00JU2A62Q].m4b` | Satsangs | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |
| `more/SatsangSeriesVolumeIX.mp3` | more | T2t 0.75 | 262 Satsang Series (Feb 2010) (0.75); 344 Satsang Series (Jan 2006) (0.75); 251 Satsang Series (Jan 2007) (0.75); … |

## 5. Bucket C — registry-only (candidate new works / non-catalogue assets)

| Registry name family | Folder(s) | Note |
|---|---|---|
| `ANewEarth:AwakeningYourLife'sPurpose[B00FGGVZUM].m4b` | Audiobooks | best score 0.00 |
| `Glamour:AWorldProblem[B0CQRK3N1F].m4b` (+1 same-name files) | Audiobooks | best score 0.00 |
| `IAmNottheBody:DiscoveringtheTruthBeyondBondage[B092LKVN1K].m4b` | Audiobooks | best score 0.00 |
| `LiveontheCrestoftheMoment[B09YFMQZJ2].m4b` | Audiobooks | best score 0.00 |
| `TalkswithSriRamanaMaharshi[B0FTDGCWTP].m4b` | Audiobooks | best score 0.00 |
| `TheBiologyofBelief:UnleashingthePowerofConsciousness,Matter,andMiracles[1683649079].m4b` (+1 same-name files) | Audiobooks | best score 0.00 |
| `TheCloudofUnknowing[B0DNRK5BY1].m4b` (+1 same-name files) | Audiobooks | best score 0.00 |
| `TheHolographicUniverse:TheRevolutionaryTheoryofReality[1662083998].m4b` | Audiobooks | best score 0.00 |
| `ThePowerofNow:AGuidetoSpiritualEnlightenment[B00FGF9FXM].m4b` | Audiobooks | best score 0.00 |
| `TheUltimateTruth[B09YFVXQTP].m4b` | Audiobooks | best score 0.00 |
| `TheZenTeachingofHuangPo:OntheTransmissionofMind[B09FBQLB2G].m4b` | Audiobooks | best score 0.00 |

## 6. Bucket D — master rows `owned=true` with no registry counterpart

Grouped by work (`work_id`). These are the catalogue's flagged-owned
records for which the owner's file library shows no counterpart file —
streaming-only holdings, missing files, or files the matcher could not
attribute. Listed for owner review; **no flags are changed here**.

| Master uuid(s) | Title(s) | Series | Format |
|---|---|---|---|
| 221 | Progressive Levels of Consciousness - A Special Talk Presented in Oxford (2003) | On The Road Talk Series | streaming |
| 265 | Golden Word Book Signing – Audio | Media Miscellaneous | CD |
| 306 | Spiritual Power and Integrity: Uncovering Spiritual Reality and Realizing Peace, Love, and Divinity | Transcription Series Books | book |
| 307 | Karma and Devotion: The Sacred Path to God through the Heart | Transcription Series Books | book |
| 308 | The Final Doorway to Enlightenment: Prayer, Transcendence and Realization of the Self | Transcription Series Books | book |
| 344 | Satsang Series (Jan 2006) | Satsang Series | CD |
| 345 | Satsang Series (Mar 2006) | Satsang Series | CD |
| 346 | Satsang Series (May 2006) | Satsang Series | CD |
| 347 | Satsang Series (Jul 2006) | Satsang Series | CD |
| 348 | Satsang Series (Sep 2006) | Satsang Series | CD |
| 349 | Satsang Series (Nov 2006) | Satsang Series | CD |
| 354 | Unity Church of Sedona 2005 March (CD) | On The Road Talk Series | CD |
| 355 | Unity Church of Sedona 2006 June (CD) | On The Road Talk Series | CD |
| 357 | Peace is the Natural State | On The Road Talk Series | CD |
| 359 | Orthomolecular Psychiatry: Treatment of Schizophrenia | Academic | book |

15 rows in 15 works. 2 of those works also appear among bucket-B candidates — a B ruling could resolve them; the D definition above counts bucket-A counterparts only.

## 7. Bucket E — registry-matched master rows with `owned` false/blank

Evidence for a **future** owner ruling: these master rows match files
present in the owner's library while the master's `owned` is `false` or
blank. Nothing is applied — the flags become follow-up work orders only
after the owner reviews this deck.

| Master uuid | owned | Title | Series | Matching registry file(s) |
|---|---|---|---|---|
| 266 | false | All is Divinity | On The Road Talk Series | `Audiobooks/AllIsDivinity[B09W72KQWM]/AllIsDivinity[B09W72KQWM].m4b` |
| 269 | false | God is The Infinite Field | On The Road Talk Series | `Audiobooks/GodIstheInfiniteField[B09VYFVGN7]/GodIstheInfiniteField[B09VYFVGN7].m4b` |
| 270 | false | Spiritual Reality | On The Road Talk Series | `Audiobooks/SpiritualityReality[B09VYFT4XK]/SpiritualityReality[B09VYFT4XK].m4b` |
| 271 | false | The Ever-Present Joy | On The Road Talk Series | `Audiobooks/TheEver-PresentJoy[B09VYFCMZH]/TheEver-PresentJoy[B09VYFCMZH].m4b` |
| 273 | false | The Prevailing Silence | On The Road Talk Series | `Audiobooks/ThePrevailingSilence[B09VYF8F1V]/ThePrevailingSilence[B09VYF8F1V].m4b` |
| 274 | false | Transcending the Ego | On The Road Talk Series | `Audiobooks/TranscendingtheEgo[B09VYBV6PQ]/TranscendingtheEgo[B09VYBV6PQ].m4b` |
| 275 | false | Truth Shines Forth | On The Road Talk Series | `Audiobooks/TruthShinesForth[B09VYD8PXN]/TruthShinesForth[B09VYD8PXN].m4b` |
| 277 | false | You Are the Light of Consciousness | On The Road Talk Series | `Audiobooks/YouAretheLightofConsciousness[B09VYC9VZF]/YouAretheLightofConsciousness[B09VYC9VZF].m4b` |
| 316 | (blank) | The Ego is Not the Real You | Books | `PDFsandEPUBs/TheEgoIsNottheRealYou.epub` |
| 318 | (blank) | The Wisdom of Dr. David R. Hawkins: Classic Teachings on Spi | Books | `PDFsandEPUBs/TheWisdomofDrDavidRHawkins.epub` |
| 320 | (blank) | Power vs. Force (Audiobook) | Books | `Audiobooks/Powervs.ForceTheHiddenDeterminantsofHumanBehavior.mp3`, `Audiobooks/Powervs.Force[B002V5GOH0]/Powervs.Force:TheHiddenDeterminantsofHumanBehavior[B002V5GOH0].m4b` (+2) |
| 321 | (blank) | The Eye of the I (Audiobook) | Books | `Audiobooks/TheEyeoftheIFromWhichNothingIsHidden.mp3`, `Audiobooks/TheEyeoftheI[1401962459]/TheEyeoftheI:FromWhichNothingisHidden[1401962459].m4b` (+2) |
| 322 | (blank) | Truth Vs Falsehood (Audiobook) | Books | `Audiobooks/Truthsvs.FalsehoodTheArtofSpiritualDiscernment.mp3`, `Audiobooks/Truthsvs.Falsehood[B00NWS4SQO]/Truthsvs.Falsehood:TheArtofSpiritualDiscernment[B00NWS4SQO].m4b` (+3) |
| 323 | (blank) | Letting Go (Audiobook) | Books | `Audiobooks/LettingGoThePathwayofSurrender.mp3`, `PDFsandEPUBs/LettingGo_ThePathwayofSurrenderbyDavidR.Hawkins.epub` |
| 324 | (blank) | Healing and Recovery (Audiobook) | Books | `Audiobooks/Healing[B00NPBHS2Y]/Healing:AchievingTotalWellnessThroughHigherLevelsofConsciousness[B00NPBHS2Y].m4b`, `Audiobooks/Healing[B00NPBHS2Y]/Healing:AchievingTotalWellnessThroughHigherLevelsofConsciousness[B00NPBHS2Y].pdf` (+4) |
| 325 | (blank) | Transcending the Levels of Consciousness (Audiobook) | Books | `Audiobooks/TranscendingtheLevelsofConsciousnessTheStairwaytoEnlightenment.mp3`, `PDFsandEPUBs/TranscendingtheLevelsofConsciousness_TheStairwaytoEnlightenmentbyDavidR.Hawkins.epub` |
| 326 | (blank) | In The World But Not Of It (Audiobook) | Books | `Audiobooks/IntheWorld,butNotofIt[B00NMUQ8DS]/IntheWorld,butNotofIt:LivingSpirituallyintheModernWorld[B00NMUQ8DS].m4b`, `Audiobooks/IntheWorld,butNotofIt[B00NMUQ8DS]/IntheWorld,butNotofIt:LivingSpirituallyintheModernWorld[B00NMUQ8DS].pdf` (+1) |
| 327 | (blank) | Truth vs. Falsehood: The Art of Spiritual Discernment (CD &  | Books | `Audiobooks/Truthsvs.FalsehoodTheArtofSpiritualDiscernment.mp3`, `Audiobooks/Truthsvs.Falsehood[B00NWS4SQO]/Truthsvs.Falsehood:TheArtofSpiritualDiscernment[B00NWS4SQO].m4b` (+3) |
| 328 | (blank) | Healing: Achieving Total Wellness Through Higher Levels of C | Books | `Audiobooks/Healing[B00NPBHS2Y]/Healing:AchievingTotalWellnessThroughHigherLevelsofConsciousness[B00NPBHS2Y].m4b`, `Audiobooks/Healing[B00NPBHS2Y]/Healing:AchievingTotalWellnessThroughHigherLevelsofConsciousness[B00NPBHS2Y].pdf` (+4) |
| 329 | (blank) | “In the World But Not of It” – Audio | Books | `Audiobooks/IntheWorld,butNotofIt[B00NMUQ8DS]/IntheWorld,butNotofIt:LivingSpirituallyintheModernWorld[B00NMUQ8DS].m4b`, `Audiobooks/IntheWorld,butNotofIt[B00NMUQ8DS]/IntheWorld,butNotofIt:LivingSpirituallyintheModernWorld[B00NMUQ8DS].pdf` (+1) |
| 330 | (blank) | The Highest Level of Enlightenment – Audio | Books | `Audiobooks/TheHighestLevelofEnlightenment[B00O3I950G]/TheHighestLevelofEnlightenment:TaptheDatabaseofConsciousnessforTotalSelf-Realization[B00O3I950G].m4b`, `Audiobooks/TheHighestLevelofEnlightenment[B00O3I950G]/TheHighestLevelofEnlightenment:TaptheDatabaseofConsciousnessforTotalSelf-Realization[B00O3I950G].pdf` (+1) |
| 331 | (blank) | Power vs. Force Audio Book | Books | `Audiobooks/Powervs.ForceTheHiddenDeterminantsofHumanBehavior.mp3`, `Audiobooks/Powervs.Force[B002V5GOH0]/Powervs.Force:TheHiddenDeterminantsofHumanBehavior[B002V5GOH0].m4b` (+2) |
| 332 | (blank) | The Highest Level of Enlightenment (Audiobook) | Books | `Audiobooks/TheHighestLevelofEnlightenment[B00O3I950G]/TheHighestLevelofEnlightenment:TaptheDatabaseofConsciousnessforTotalSelf-Realization[B00O3I950G].m4b`, `Audiobooks/TheHighestLevelofEnlightenment[B00O3I950G]/TheHighestLevelofEnlightenment:TaptheDatabaseofConsciousnessforTotalSelf-Realization[B00O3I950G].pdf` (+1) |
| 333 | (blank) | The Way to God: The Nature of Divinity vs. Religious Fallacy | The Way to God | `Audiobooks/TheWaytoGod[B006ZBQNBS]/TheWaytoGod:TheNatureofDivinityvs.ReligiousFallacy[B006ZBQNBS].m4b`, `Lectures2002-2011/2002/jul-2002.mp4` |
| 334 | (blank) | The Way to God: Advaita - The Way to God Through Mind (Audio | The Way to God | `Lectures2002-2011/2002/aug-2002.mp4` |
| 335 | (blank) | The Way to God: Realizing the Root of Consciousness (Audiobo | The Way to God | `Audiobooks/TheWaytoGod[B006W15XZI]/TheWaytoGod:RealizingtheRootofConsciousness:Meditative&ComtemplativeTechniques[B006W15XZI].m4b`, `Lectures2002-2011/2002/june-2002.mp4` |
| 336 | (blank) | Devotional Nonduality Intensive: Intention (Audiobook) | Nonduality Intensive | `Audiobooks/DevotionalNondualityIntensive[B009LKPYRY]/DevotionalNondualityIntensive:Intention[B009LKPYRY].m4b`, `Lectures2002-2011/2005/may-2005.mp4` |
| 337 | (blank) | Devotional Nonduality Intensive: Alignment (Audiobook) | Nonduality Intensive | `Audiobooks/DevotionalNondualityIntensive[B009LLI07Y]/DevotionalNondualityIntensive:Alignment[B009LLI07Y].m4b`, `Lectures2002-2011/2005/apr-2005.mp4` (+1) |
| 338 | (blank) | Transcending the Mind Series: Identification & Illusion (Aud | Transcending the Mind | `Audiobooks/TranscendingtheMindSeries[B008Y23T9U]/TranscendingtheMindSeries:Identification&Illusion[B008Y23T9U].m4b`, `Lectures2002-2011/2004/aug-2004.mp4` |
| 339 | (blank) | Transcending the Mind Series: Emotions & Sensations (Audiobo | Transcending the Mind | `Audiobooks/TranscendingtheMindSeries[B008Y2962E]/TranscendingtheMindSeries:Emotions&Sensations[B008Y2962E].m4b`, `Lectures2002-2011/2004/apr-2004.mp4` |
| 340 | (blank) | Spiritual Reality and Modern Man: God vs. Science: Limits of | Spiritual Reality & Modern Man | `Lectures2002-2011/2007/feb-2007.mp4` |
| 341 | (blank) | Transcending the Levels of Consciousness Series: Perception  | Transcending Levels of Consciousness | `Audiobooks/TranscendingtheLevelsofConsciousnessSeries[B00APLSQJG]/TranscendingtheLevelsofConsciousnessSeries:Perceptionvs.Essence[B00APLSQJG].m4b`, `Lectures2002-2011/2006/apr-2006.mp4` |
| 343 | (blank) | Live Life As A Prayer (Audio) | Transcending Levels of Consciousness | `Audiobooks/DiscussionSeries2012[B00JS2MZIQ]/DiscussionSeries2012:LiveYourLifeLikeaPrayer,WhatYouAreChangestheWorld,WhatisRealSuccess?PermanentInnerPeace[B00JS2MZIQ].m4b`, `Audiobooks/LiveLifeAsAPrayer[140196270X]/LiveLifeAsAPrayer[140196270X].m4b` (+3) |
| 353 | (blank) | Giving Up Illness through A Course in Miracles© – Audio | Media Miscellaneous | `Audiobooks/GivingUpIllnessThrough'ACourseinMiracles'[B00KXCFHAS]/GivingUpIllnessThrough'ACourseinMiracles'[B00KXCFHAS].m4b`, `more/GivingUpIllnessThroughACourseinMiracles.mp3` |
| 356 | (blank) | Don’t Set Sail Without A Compass – Audio | Media Miscellaneous | `Audiobooks/Don'tSetSailwithoutaCompass![B00LCE5MRE]/Don'tSetSailwithoutaCompass![B00LCE5MRE].m4b`, `more/Don'tSetSailwithoutaCompass.mp3` |
| 358 | (blank) | The Essence of Letting Go: A Living Transmission of Truth | Media Miscellaneous | `Audiobooks/TheEssenceofLettingGo[B0FNDM2JNX]/TheEssenceofLettingGo:ALivingTransmissionofTruth[B0FNDM2JNX].m4b` |
| 369 | (blank) | The Discovery | Nightingale-Conant | `Audiobooks/TheDiscovery[B00NO7TMRI]/TheDiscovery:RevealingthePresenceofGodinYourLife[B00NO7TMRI].m4b`, `Audiobooks/TheDiscovery[B00NO7TMRI]/TheDiscovery:RevealingthePresenceofGodinYourLife[B00NO7TMRI].pdf` |
| 370 | (blank) | The Ultimate David Hawkins Library | Nightingale-Conant | `Audiobooks/TheUltimateDavidHawkinsLibrary[B01ENWKFOQ]/TheUltimateDavidHawkinsLibrary[B01ENWKFOQ].m4b`, `Audiobooks/TheUltimateDavidHawkinsLibrary[B01ENWKFOQ]/TheUltimateDavidHawkinsLibrary[B01ENWKFOQ].pdf` (+1) |
| 371 | (blank) | OM | Media Miscellaneous | `Audiobooks/OM[B09YFZQ121]/OM[B09YFZQ121].m4b` |
| 372 | (blank) | How to Surrender to God | Hay House | `Audiobooks/HowtoSurrendertoGod[1401960502]/HowtoSurrendertoGod:ThePathtoEnlightenmentThroughLettingGo[1401960502].m4b`, `Audiobooks/HowtoSurrendertoGod[1401960502]/HowtoSurrendertoGod:ThePathtoEnlightenmentThroughLettingGo[1401960502].pdf` |
| 373 | (blank) | Power vs. Force — Original Hardcover (non-B&W dust jacket) | Books | `Audiobooks/Powervs.ForceTheHiddenDeterminantsofHumanBehavior.mp3`, `Audiobooks/Powervs.Force[B002V5GOH0]/Powervs.Force:TheHiddenDeterminantsofHumanBehavior[B002V5GOH0].m4b` (+2) |

## 8. Related prior art (non-authoritative)

GitHub issue #18 (2026-08-04) reported a lak.nz-side Drive cross-check of
the same `owned` flags, and `review/LINKS_VIMEO_OWNED_FINDINGS.md` §3
summarizes it. That scan (350 files on an external mount) is **prior
external evidence only** — lak.nz treats this repo as helper reference
and opens no PRs here — and its numbers were neither trusted nor reused:
everything in this report was recomputed from the two committed inputs
(`final_registry.csv`, `docs/master.json`). Convergences and divergences
with issue #18's lists are observations, not authorities.

## 9. Reproduction

```bash
python crosscheck_final_registry.py            # regenerate both outputs
python crosscheck_final_registry.py --check    # exit 0 iff byte-identical
python -m unittest tests.test_final_registry_crosscheck -v
```

Inputs: `final_registry.csv` (read with `encoding="utf-8-sig"`, CRLF-safe)
and `docs/master.json`. Outputs: `review/final_registry_crosscheck.csv`
(one row per registry file, 259 data rows) and this report. No network,
no new dependencies (stdlib only), no timestamps in outputs.

