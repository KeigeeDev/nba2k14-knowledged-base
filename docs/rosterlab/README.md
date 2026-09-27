# rlapply: headless roster updates through Roster Lab

`rlapply.py` takes RED MC CSV exports (`Players`, `Teams`, `Staff`, `Arenas`)
and writes them into a 2K14 `.ROS` **using Roster Lab by Q2K's own engine**.
It opens the roster with Roster Lab's `document.RosterDocument`, calls its
`set()` for every cell that differs, and saves through its `save_as()`. You get
the same safety checks as clicking through the Roster Lab window: the save-name
rule, face and name audits, roster-slot/`PlNum` bookkeeping, CRC and the
automatic backup. There's no GUI.

Roster Lab is closed freeware. This tool imports it from its install folder
at run time and never copies it.

## Requirements

- Roster Lab 1.7.0 installed at `C:\Editing Tools\Roster Lab by Q2K`, or set
  `ROSTER_LAB` to its folder.
- **Python 3.14** (`py -3.14`), because Roster Lab ships 3.14 bytecode.
  `rlapply.cmd` calls it for you.

## Usage

A bare roster name is looked up in `%APPDATA%\2K Sports\NBA 2K14\Saves`.

```bat
rem 1. What differs between the save and the CSVs?  (-v lists every cell)
.ai\rosterlab\rlapply.cmd diff "FIBA 2027 TEST 1" --csv "csv\FIBA 2026\v8"

rem 2. Dry run: apply in memory, verify, save nothing
.ai\rosterlab\rlapply.cmd apply "FIBA 2027 TEST 1" --csv "csv\FIBA 2026\v9" --teams 20

rem 3. The same, written to a new roster
.ai\rosterlab\rlapply.cmd apply "FIBA 2027 TEST 1" --csv "csv\FIBA 2026\v9" --teams 20 --out "FIBA 2027 TEST 2"
```

### Choosing what to apply (scope)

The tool only writes rows you name. Save files and exports always disagree
somewhere, so you must name the scope. Options can be combined:

| Option | Rows written |
|---|---|
| `--teams 2,5,15-16` | Each team's row, every player in its **CSV** roster slots, its staff (`Staff_HC`, `Staff_AC`, …) and its arena (`ArenaID`) |
| `--rows Players:1360-1361,1437` | Exactly these rows (repeatable; tables: Players, Teams, Staff, Arenas) |
| `--changes "csv\FIBA 2026\v8"` | The rows listed in checkpoint `changes.json` files |
| `--all` | Every row that differs. Careful: this also "fixes" old disagreements between the save and the export |

### Other options

| Option | Meaning |
|---|---|
| `--out NAME` | Save here. Without it the run is a dry run |
| `--overwrite` | Allow `--out` to replace an existing file. It is copied to `.bak` first |
| `--yes` | Accept Roster Lab's save-time questions. Without it the save stops at the first question and prints it |
| `--report FILE` | Write a JSON report of scope, writes and side effects |

Exit codes: `0` ok or dry run, `1` failed verification or cell errors (nothing
saved, or saved but verification failed), `2` usage error or save refused.

## What happens on `apply`

1. Every mapped cell of the four CSVs is read from the roster.
2. Differing in-scope cells are written in this order: roster slots
   (`Ros_*`), situational slots (`Sit_*`), other team fields, player fields,
   then `TeamID1`.
3. Roster Lab's membership logic can clear situational slots when later
   slot writes move players around. A second pass rewrites anything that no
   longer matches, and repeats up to 4 times.
4. Report: writes, errors, in-scope cells still different, **cells changed
   outside the scope** (Roster Lab side effects), fields Roster Lab can't
   write, zero faces, name-handle problems, per-team player counts and problems.
5. On `--out`: save through Roster Lab, check the CRC, reopen the file from
   disk and confirm every in-scope cell matches the CSV.

## Known behaviour

- **The save name must be letters, digits and spaces only** and at most 25
  characters. Roster Lab refuses anything else (for example `TEST_1`)
  because the game deletes such saves.
- **Players dropped from a roster** get `TeamID1`/`TeamID2` = -1 when they
  are on no other team. That is Roster Lab's rule and shows as an
  outside-scope change. A RED MC import would leave the old team ID.
- **Shared players:** `--teams` warns when a player it rewrites is also in
  another team's CSV roster (for example the Stars team 90).
- **Not writable:** `NickName` (Roster Lab calls it a text field it does not
  set). All other columns of the four tables are written. The other 34 RED MC
  tables are ignored.
- The source roster is never modified unless it is also `--out` with
  `--overwrite`.

Verified 2026-09-26: `--teams 2,5,15,16` with `csv\FIBA 2026\v8` on
`FIBA 2027 TEST_1.ROS` reproduces the hand-verified `FIBA 2027 TEST 1.ROS`
byte for byte (sha256 `0352246e…168d`).
