# Bulk-edit a roster through RED MC's CSV export

**Status:** [VERIFIED] for the round trip: the owner ran export → edit → import on real rosters for the Teams, Staff, Players and Arenas tables. [DRAFT] for the other tables, which haven't been round-tripped.
**Category:** workflow
**Last updated:** 2026-09-27

## Summary

RED MC can export any roster table to CSV and import it back. That lets a script or an AI assistant do real data work (rebalancing ratings, bulk renames, audits) while RED MC still handles the binary file. The risk is in the CSV itself: RED MC's CSV dialect isn't documented, so any edit must keep the file byte-identical except for the changed cells.

## Prerequisites

- [RED MC](../tools/red-mc.md) 5.0.
- Optional: the owner's [`rmcsv.py`](../tools/roster-scripts.md#rmcsvpy), which preserves the format for you. Right now it also needs the owner's `turk.py`, which isn't in the repo.

## What RED MC's CSV looks like

The owner verified this on 38 real exports:
- Comma-delimited, **UTF-16 LE with BOM**, CRLF line endings, and an empty first column before `ID`.
- **A cell is quoted if and only if it contains a space.** `-1`, `O.J.`, `O'Neal` and `NO/OKC` are written bare.
- If you write a value containing a space without quotes, RED MC's importer splits it and shifts every later column in that row. You get errors like `"Juan" is not a valid integer value`, or silent corruption if the shifted row still parses.
- A normal CSV validator won't catch this, because the file is still valid CSV. Scan for unquoted spaces directly before importing.

## Steps

1. **Back up the roster.** Saves are in `%APPDATA%\2K Sports\NBA 2K14\Saves`.
2. In RED MC, open the roster and use **Export To CSV** (selected tab or whole file).
3. **Check the round trip** before editing: `python rmcsv.py inspect file.csv` must report a byte-identical round trip. If it doesn't, stop.
4. `python rmcsv.py validate file.csv` gives a baseline of existing problems, such as duplicate `ASA_ID`s.
5. **Dry run** the edit, e.g.:
   ```
   python rmcsv.py edit Players.csv --set "Loyalty=clamp(Loyalty+10,0,100)" --where "IsRegular == 1" --dry-run
   ```
   Then run it without `--dry-run`. The output goes to `<name>.edited.csv`; the input is never touched.
6. `python rmcsv.py diff Players.csv Players.edited.csv`, and read every change.
7. In RED MC, use **Import From CSV**, save, and test in game.

**Alternative for steps 7 onward:** `rlapply` writes the CSVs into the `.ROS` through Roster Lab's engine instead of RED MC, with its crash checks and a verify-after-save pass ([roster scripts](../tools/roster-scripts.md#rlapply)).

## Pitfalls

- **Enum columns hold integer indices.** RED MC doesn't record which list in `Enums.txt` belongs to which field, so `rmcsv` doesn't range-check them.
- **Keep `ID2` equal to `ID`, and `ASA_ID` unique.**
- **Save names:** use letters, digits and spaces only, at most 25 characters. According to Roster Lab, the game deletes other names.

## Sources

- [`sources/roster-editing/csv/README.md`](../../sources/roster-editing/csv/README.md) (owner's pipeline notes and the quoting rule) and [`rosterlab/README.md`](../../sources/roster-editing/rosterlab/README.md).
- The format-preserving behaviour of `rmcsv.py` was tested during review ([roster scripts](../tools/roster-scripts.md#what-was-tested-2026-09-27)).

## Open questions

- Do the other 34 tables survive the CSV round trip?
- Does Import From CSV handle added or removed rows, or only edits?
