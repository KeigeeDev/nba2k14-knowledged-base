# Roster Lab by Q2K

**Status:** [VERIFIED] for the details below, which the owner inspected in an installed copy of version 1.7.0 (2026-09-26). [DRAFT] for anything the notes flag as the tool's own claim.
**Category:** tool
**Last updated:** 2026-09-27

## Summary

Roster Lab by Q2K is a third-party NBA 2K14 roster editor written in Python (PySide6/Qt 6). It reads and writes `.ROS`, `.FXG` and `.CMG` saves directly, and it runs safety checks on save that catch the known crash causes. Its engine is also the most complete independent reference for the [`.ROS` format](../file-formats/ros-roster.md).

## Details

- **Licence:** closed, "all rights reserved" freeware. Don't copy its files or schemas into this repo. Describing how it behaves is fine.
- **Stack:** Python 3.14 bytecode shipped as loose `.pyc` files in `_internal\`, packaged with PyInstaller. It has no network code. The engine was originally called "Sigil 2K14" and was rebranded by runtime patches.
- **What it covers:**
  - Players, Teams, Staff, Stats, Jerseys, Awards, Records, Trades, Headshapes and draft classes (`.FDC`).
  - Trades that reproduce what an in-game trade writes.
  - Rotation tidy-up.
  - An Overall-rating estimate (a per-position linear fit of the 42 ratings; the tool claims 91% exact).
  - Player cards as JSON, and porting 2K13 rosters.
- **Six tools are hidden, not removed:** Browse Artwork, Repack Artwork, Browse Sounds, Soundtrack, Mod Manager and Scorebug Tweaker. Their code still ships.

### Save checks it enforces

- **Save name:** letters, digits and spaces only, at most 25 characters including the extension. According to Roster Lab, the game deletes other names.
- **Face block:** it asks before saving players with an all-zero face block, which crashes the game, and can heal them.
- **Other checks:** bad name handles, duplicated players, and roster slots / `PlNum` kept in sync after trades.
- **Same file:** the size must not change, and the CRC is recomputed.
- **Automatic backups:** every opened file is copied to `%LOCALAPPDATA%\2k14-roster-editor\backups\` (up to 5 per name, 512 MB in total).

## Known issues

- **Its README says it never writes to the file it opened, but it does.** Save overwrites the original after a one-time confirmation. The automatic backup is the real safety net.
- **Its directory hash table (`KNOWN_HASH`) pairs hashes with the wrong sections**, off by one. This only causes spurious warnings.
- **Trades had a crash bug in builds before 1.6** (roster-slot gaps). The Q2K patch layer fixes it after every trade.

## Headless use

The owner's `rlapply` script drives Roster Lab's engine without the GUI, to apply RED MC CSV exports to a `.ROS`. See [roster scripts](roster-scripts.md#rlapply).

## Sources

- [`sources/roster-editing/ai-docs/09-roster-lab.md`](../../sources/roster-editing/ai-docs/09-roster-lab.md) (owner's inspection of version 1.7.0; only the pure-data modules were imported).
- Where to get it: TODO: source needed.

## Open questions

- Does its licence allow the kind of inspection in the owner's notes? Worth checking before publishing more detail from it.
