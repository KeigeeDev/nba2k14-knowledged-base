# Map an unknown `.ROS` field (differential editing)

**Status:** [VERIFIED]. This is the method that produced the owner's player-record map, and Roster Lab's schemas were built the same way.
**Category:** workflow
**Last updated:** 2026-09-27

## Summary

To find where and how a field is stored in a roster file, change exactly that one field, save, and compare the two files bit by bit. Then confirm the candidate across the whole roster with statistics. No disassembly is needed. The section layout is already known, so every record's position can be computed ([`.ROS` format](../file-formats/ros-roster.md#section-map)).

## Prerequisites

- [RED MC](../tools/red-mc.md) (or the in-game editor).
- `ros_inspect.py` ([roster scripts](../tools/roster-scripts.md)).
- A spare copy of a roster.

## Steps

1. **Read the spec first.** RED MC's `Fields & Values Tutorial - NBA 2K14.docx` gives each field's type and range. That tells you the likely width and encoding before you start. Note that `Double` there can mean float32 *or* a scaled integer.
2. Copy the roster and open the copy in RED MC.
3. **Change exactly one field on one row** (e.g. player 0's Height 200 → 201) and save.
4. Run `python ros_inspect.py bitdiff original.ROS modified.ROS`. Ignore the runs in bits 0–31 (the CRC). The remaining run is the field's absolute bit position.
5. Convert that to a record offset: `offset = bit − start(section) − bits_per_record × row`.
6. **Confirm the width.** Set an enum to its highest value, or a number to its maximum, and diff again.
7. **Validate across all players**, not just a few stars. The owner found these tests decisive:
   - **Distribution shape:** position values spread evenly over 0–4.
   - **Cross-field agreement:** PlayStyle's position group matched `Pos` for 98.5% of players, versus under 55% at any other offset.
   - **Encoding invariants:** the ratings block was delimited by "every value is a multiple of 3".
   - **Physical correlation:** big-man ratings rise with height, guard ratings fall.
8. Record the result per struct hash, not per tab, so it carries over to every table with the same layout. Then update [player record](../file-formats/ros-player-record.md).

## Pitfalls

- **An in-game re-save also changes small bookkeeping fields** all over the file. Diff files saved by RED MC where you can, and anchor on the record you edited.
- **Searching for a known value** (e.g. a birthdate bit pattern) can match other tables too. Check with a second player.
- **Float fields don't show up in integer scans.** A constant byte like `134` right before a field is a float32 exponent, which gives it away.

## Sources

- [`sources/roster-editing/ai-docs/06-player-record-map.md`](../../sources/roster-editing/ai-docs/06-player-record-map.md) (methodology section) and [`02-ros-format.md`](../../sources/roster-editing/ai-docs/02-ros-format.md).
