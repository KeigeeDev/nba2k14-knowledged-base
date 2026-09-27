# Roster scripts (`ros_inspect`, `rmcsv`, `rlapply`, `roster_lab_inspect`)

**Status:** [VERIFIED] for the behaviour listed under "What was tested", which was run during review on 2026-09-27. For everything else, the owner's reports on their own machine.
**Category:** tool
**Last updated:** 2026-09-27

## Summary

The owner wrote four Python tools for roster work. They live in [`sources/roster-editing/`](../../sources/roster-editing/README.md):

| Script | What it does | Needs |
|---|---|---|
| `ai-docs/tools/ros_inspect.py` | Inspect `.ROS` files: `header` (CRC, directory), `names` (string scan), `resign` (fix CRC), `bitdiff` (differing bit runs), `player` / `dump` (find a player by birthdate and decode them) | Python 3, standard library |
| `csv/rmcsv.py` | Format-preserving tool for RED MC CSV exports: `inspect`, `validate`, `stats`, `edit --set/--where`, `diff` | The owner's `turk.py` (not uploaded) and RED MC's `Text/` files |
| `rosterlab/rlapply.py` | Apply RED MC CSV exports to a `.ROS` headlessly through [Roster Lab](roster-lab.md)'s engine, with its save checks | Python 3.14, a Roster Lab 1.7.0 install, `rmcsv` |
| `ai-docs/tools/roster_lab_inspect.py` | Read Roster Lab's modules, docstrings, constants and schemas without running it | Python 3.14, a Roster Lab install |

**Folder layout:** the scripts expect the owner's layout, where these folders sit inside the RED MC install (`ai-docs\`, `.ai\csv\`, `.ai\turk\`, `.ai\rosterlab\`). From this repo's paths, `rmcsv`, its tests and `rlapply` won't find their imports.

## `ros_inspect.py`

- **`header`** checks the CRC, magic and size field, and lists the directory with the correct off-by-one pairing ([format](../file-formats/ros-roster.md#table-directory)).
- **`resign`** rewrites the CRC in place. Back up first.
- **`bitdiff a b`** lists differing bit runs. It's the core of the [field-mapping method](../workflows/ros-field-mapping.md). The first runs are always the CRC (bytes 0–3).
- **`dump y m d`** decodes height, weight, position, jersey, team, play style and all 42 ratings for players with that birthdate. It rejects hits with implausible height or weight.
- **`player y m d`** is a quicker version of `dump` with fewer fields. See the bug below.

## `rmcsv.py`

- It detects the delimiter and encoding, and re-emits untouched cells byte-for-byte, so an unedited file round-trips identically.
- Edited cells are quoted by RED MC's rule: **a cell is quoted if and only if it contains a space**. The owner verified the rule on 38 real exports. An unquoted space makes RED MC's importer shift the rest of the row.
- `--set`/`--where` expressions go through an allow-list parser: arithmetic, comparisons, `and/or/not`, and the functions `int float str abs min max round len clamp lower upper`.
- `validate` checks for duplicate `ASA_ID`s, text in numeric columns, short rows, and the few ranges RED MC's captions state (3 of 355 player fields).

## `rlapply`

1. Reads four CSVs (Players, Teams, Staff, Arenas).
2. Writes only the rows you scope (`--teams`, `--rows`, `--changes` or `--all`) through Roster Lab's `set()`.
3. Re-runs up to 4 passes, because slot writes can clear situational slots.
4. Reports side effects outside the scope.
5. With `--out NAME`, saves through Roster Lab, then reopens the file and checks every in-scope cell. Without `--out` it's a dry run.

`NickName` can't be written. The owner reports that one run reproduced a hand-made roster byte-for-byte.

## What was tested (2026-09-27)

Tested with Python 3.11, on synthetic files built to the documented layout:

- **`ros_inspect.py`**
  - `header` validates the CRC.
  - `resign` fixes a deliberately broken CRC.
  - `bitdiff` reports the changed jersey bits exactly (after the CRC runs).
  - `dump` decodes every field correctly, including float height/weight and all 42 ratings.
  - Players placed in slots 121 and 1131 were found at bits 766,157 and 4,446,597, which are the anchor positions the owner's notes report for those slots in real rosters.
- **`rmcsv.py`** (core only, with a stand-in for the missing `turk` module):
  - A UTF-16LE-with-BOM, CRLF export with an empty first column round-trips byte-identically.
  - Edits change only the edited cells.
  - A value with a space gets quoted, and `O'Neal`, `O.J.` and `-1` stay bare.
  - The expression parser rejects `__import__`, attribute access, lambdas, comprehensions and `open()`.
- **Not run:** `test_rmcsv.py` and `validate`/`inspect` (they need the missing `turk.py` and RED MC's `Text/`), `rlapply.py` and `roster_lab_inspect.py` (they need Roster Lab and Python 3.14).

## Known issues

1. **`ros_inspect.py player` misreads the jersey number.** It reads 8 bits starting at anchor + 27, but the jersey is 7 bits at anchor + 28 (record bit 301), and its own docstring says so. If record bit 300 is set, the jersey comes out 128 too high. In the test, a jersey of 19 was reported as 147. `dump` reads it correctly, so use `dump` until this is fixed.
2. **`rmcsv.py` can't run from the upload.** It imports `turk.py` from a `turk/` folder that wasn't pushed. `test_rmcsv.py` needs it too.
3. **`ros_inspect.py` reads IDs as 12 bits** (record bits 20–31, the low 12 bits of the 16-bit ID). That's fine for the 1,665 player slots, but it would truncate any ID above 4,095.
4. **`ros_inspect.py names` is a heuristic.** It scans the last 20% of the file at all 8 bit phases. Now that the heap position and handle rules are known ([string heap](../file-formats/ros-roster.md#string-heap)), names could be decoded exactly.

## Sources

- [`sources/roster-editing/`](../../sources/roster-editing/README.md): the scripts and their READMEs (SHA-256 in that README).
- Review tests: run in a scratch environment on 2026-09-27. The test scripts weren't committed.
