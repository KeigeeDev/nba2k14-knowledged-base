# RED MC

**Status:** [VERIFIED] for the version, author, file types, install layout and data files, which the owner read from an installed copy of RED MC 5.0. [COMMUNITY] for the download source, which is still unknown.
**Category:** tool
**Last updated:** 2026-09-27

## Summary

RED Modding Center (RED MC) is the standard editor for NBA 2K13/2K14 roster files and 2K `.iff` resource archives. Version 5.0 is the final release and is free. It's a closed-source, packed, 32-bit Windows GUI with no command line or plugin API. Its only automation is its own scripting language, [TURK](turk.md), plus CSV export/import.

## Details

- **Author:** Vl@d Zola Jr. (Vladislav Durmanenko). The credits also list M@dDog, JaoSming, Leftos, hokupguy, Rondo is GOD, vnardella5 and HAWK23.
- **Platform:** Windows, run as Administrator. Back up files before editing.
- **File types:**

  | Extension | Content | Games |
  |---|---|---|
  | `.ROS` | Roster ([format](../file-formats/ros-roster.md)) | 2K13, 2K14 (PC, Xbox 360, PS3) |
  | `.FDC` | Draft class | 2K14 |
  | `.OFG` | Online association | 2K13 |
  | `.IFF` | Resource archive (textures, audio, in-game text, name/number indices) | 2K12–2K15, PC only |
  | Association / MyCareer saves | Contain an embedded roster | 2K13/2K14 |

- **Features:**
  - One grid tab per roster table.
  - Clone, delete and move records ("Full Roster Control").
  - Global Editor, search and filters.
  - Free Space Indicator (the roster container has a fixed size).
  - TURK scripting.
  - Export To CSV / Import From CSV per tab or whole file ([CSV workflow](../workflows/roster-edit-csv.md)).
  - IFF texture, audio and text editing.
- **Console files:** Xbox 360 saves must be rehashed and resigned before going back to the console. PS3 saves must be decrypted first (the release notes recommend Bruteforce Save Data).

### Data files worth knowing

| Path in the install | What it gives you |
|---|---|
| `Text\NBA2K14\GridNames.txt` | The 38 table names, also used as TURK array names |
| `Text\NBA2K14\Captions\*.txt` | Every field of every table: internal key, caption, description. `Player.txt` has 355 fields. |
| `Text\Enums.txt` | 129 value lists for combo-box fields. It doesn't say which field uses which list. |
| `Tutorials\NBA 2K14\Fields & Values Tutorial - NBA 2K14.docx` | The author's field spec: 1,160 rows with storage types and ranges. Read this first when mapping a field. |
| `Tutorials\NBA 2K14\List Of Text Values.txt` | 39,833 in-game text strings keyed by hash (UTF-16LE). A different hash namespace from the roster struct hashes. |
| `Scripts\*.TURK` | Sample scripts |

The owner's notes give the parse rules for these files ([source](../../sources/roster-editing/ai-docs/03-data-dictionary.md), [spec notes](../../sources/roster-editing/ai-docs/08-official-field-spec.md)). One caveat about the spec: its type `Double` means "shown with decimals". Height and weight really are float32, but skill ratings are scaled 8-bit integers ([player record](../file-formats/ros-player-record.md#skill-ratings)).

### Cyberface use

- Open the roster and go to the player's Appearance → CyberFace ID (field key `CF_ID`). ID 326 means the file `png0326.iff`. Related fields: `GenericF` (generic face vs cyberface), `HS_ID` (headshape row), `SkinTone`.
- Eye colour is a roster setting, not part of the face texture.

## Known issues

- According to its release notes, files edited with RED MC are only guaranteed to work with RED MC and the games. Other third-party tools may fail on them.

## Sources

- Owner's notes from an installed RED MC 5.0: [`sources/roster-editing/ai-docs/01-overview.md`](../../sources/roster-editing/ai-docs/01-overview.md), [`03-data-dictionary.md`](../../sources/roster-editing/ai-docs/03-data-dictionary.md), [`08-official-field-spec.md`](../../sources/roster-editing/ai-docs/08-official-field-spec.md).
- Cyberface use: [`sources/cyberface/CYBERFACE_MODDING_GUIDE.md`](../../sources/cyberface/CYBERFACE_MODDING_GUIDE.md). RED MC is also listed as a required tool in icecr's NLSC cyberface tutorial (per search excerpts): https://forums.nba-live.com/viewtopic.php?f=154&t=113460
- NLSC news, "RED MC & REDitor II Updated; All Functionality Now Free!": https://www.nba-live.com/red-mc-reditorii-updated-free/ (found through search 2026-09-27; not opened, the site is blocked in the review environment).
- Where to get it: TODO: source needed.

## Open questions

- Which field uses which list in `Enums.txt`? RED MC keeps that mapping internally; Roster Lab hand-built one.
