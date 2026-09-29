# RED MC Overview

**RED Modding Center v5.0** ("Courtesy of Visual Concepts" — the final, free
release). Author: Vl@d Zola Jr. (Vladislav Durmanenko). Contributors credited:
M@dDog, JaoSming, Leftos, hokupguy, Rondo is GOD, vnardella5, HAWK23.

RED MC is the de-facto standard editor for NBA 2K13/2K14 roster files and 2K
IFF resource archives. It is a **closed-source, native 32-bit Windows
application** (Delphi-era toolchain, executable is packed/protected with
randomized PE section names) — it cannot be meaningfully decompiled with
standard .NET tooling. Reverse engineering therefore relies on its data files
and on analyzing the files it produces (see `02-ros-format.md`).

## Supported file types

| Extension | Content | Games | Platforms |
|-----------|---------|-------|-----------|
| `.ROS` | Roster | NBA 2K13, NBA 2K14 | PC, Xbox 360, PS3 |
| `.FDC` | Draft class | NBA 2K14 | PC, Xbox 360 |
| `.OFG` | Online association | NBA 2K13 | PC |
| `.IFF` | Resource archive (textures, audio, in-game text, name/number indices) | NBA 2K12–2K15, MLB 2K12 | PC only |
| Association/MyCareer saves | Contain an embedded roster | 2K13/2K14 | PC, X360, PS3 |

PC NBA 2K14 saves live in `%APPDATA%\2K Sports\NBA 2K14\Saves`.

## Install layout (`C:\Editing Tools\RED MC`)

| Path | Purpose |
|------|---------|
| `RED_MC.exe` | Main app (packed native x86, run as Administrator) |
| `Parsers.dll` | Helper DLL (UPX-packed native); file parsing |
| `ogg.dll`, `vorbis*.dll` | Ogg Vorbis codecs — used for IFF audio editing |
| `Text\Enums.txt` | Enum value lists for combo-box fields (see 03-data-dictionary.md) |
| `Text\NBA2K14\GridNames.txt` | Internal table (tab) list for 2K14 rosters |
| `Text\NBA2K14\Captions\*.txt` | Per-table field dictionaries (name, caption, description) |
| `Text\NBA2K13\...` | Same for 2K13 |
| `Text\IFF\Contents.txt` | Column captions for the IFF file browser |
| `Scripts\*.TURK` | Sample TURK scripts |
| `Filters\` | Empty folder tree for row-filter presets (`N4` = NBA 2K14) |
| `Tutorials\` | TURK docs, console (X360/PS3) workflows, `Version History.doc` |
| `RED_MC.log` | Session log (log subsystem with severity levels) |

## Operational notes (from the release notes)

- Run as Administrator; always back up files before editing.
- Xbox 360: never extract inner files from saves; always Rehash & Resign
  before returning a file to the console; don't rename files off-console.
- PS3: decrypt saves before editing (recommended: Bruteforce Save Data),
  re-encrypt after. "Save As..." is disabled for PS3 (multi-file saves).
- Files edited with RED MC are guaranteed compatible with RED MC and the
  original games only — other 3rd-party tools may choke.

## Feature summary (from Version History)

- Tab-per-table grid editor for every roster table (Players, Teams, Jerseys,
  Staff, Stats, Schedules, Draft classes, Skills Boosts, ...).
- **Full Roster Control**: clone / delete / move records inside files.
- **Global Editor** and search/filter panels.
- **Roster Free Space Indicator** (the container is fixed-size; string data
  competes for free space).
- **TURK scripting** for batch edits (see 04-turk-scripting.md).
- IFF editing: texture import/export, audio (via Vorbis DLLs), in-game text,
  name/number indices; NBA 2K15 repository import/export.

## Version history (condensed)

| Version | Highlights |
|---------|-----------|
| 1.0–1.2 | 2K13 rosters (PC→PS3), Full Roster Control, OFG support |
| 2.0–2.2 | NBA 2K14 support (all platforms), FDC draft classes, Skills Boosts tab, shoe colors |
| 3.0 | IFF support (textures, text, indices), GoesTo3PT field, MNF folder indexing |
| 4.0–4.3 | NBA 2K15 PC files (audio, textures), 2K15 repository import/export |
| 5.0 | Everything free; final release |
