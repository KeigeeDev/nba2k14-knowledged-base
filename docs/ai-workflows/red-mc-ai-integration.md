# Using AI tools with RED MC and roster files

**Status:** [VERIFIED] for pattern 2: the owner has round-tripped real rosters through CSV. [DRAFT] for patterns 1, 3 and 4 as end-to-end AI workflows. Their building blocks are documented, but no complete AI-driven run is recorded yet.
**Category:** ai-workflow
**Last updated:** 2026-09-27

## Summary

RED MC has no command line, API or plugin system, so an AI assistant (Claude Code, Codex, Gemini CLI) has to work *around* it. There are four patterns, safest first. In all of them the AI supplies the logic, and something that understands the file format writes the roster.

## 1. Generate TURK scripts (safest)

1. The assistant reads the field dictionary: `Text\NBA2K14\Captions\*.txt` and `Text\Enums.txt`.
2. It writes a `.TURK` script for the requested batch edit, e.g. "heal all injuries" or "set every 2024 draftee's peak age to 24". See the [language reference](../tools/turk.md).
3. You run the script inside RED MC, which handles bits, strings and the checksum.

Limits: only fields RED MC exposes, and a person has to click Run.

## 2. Edit data through CSV

The assistant edits RED MC CSV exports with a format-preserving tool, and RED MC or Roster Lab imports them. This is good for data-heavy work: rebalancing, renames, generating rookie classes, audits. See [bulk-edit through CSV](../workflows/roster-edit-csv.md).

## 3. Edit `.ROS` files directly (headless)

The [container format](../file-formats/ros-roster.md) and much of the [player record](../file-formats/ros-player-record.md) are mapped, and the CRC can be recomputed. That means a script can change mapped fields with no GUI at all. Before saving, any such script must respect the crash rules:
- no all-zero face block,
- name handles on a string start,
- team slots packed with `PlNum` in sync,
- same file size, and a re-signed CRC.

Start with fixed-width numeric fields (ratings, bio). Map new fields with the [differential method](../workflows/ros-field-mapping.md).

## 4. Drive the RED MC GUI (last resort)

UI automation (AutoHotkey, pywinauto, or an agent with computer use) could click through RED MC for one-off jobs that need RED MC's own logic, such as console rehash/resign. It would be fragile: custom grids, admin elevation, timing.

## Setting up the workspace

The owner keeps the notes inside the RED MC folder, with a `CLAUDE.md` pointing sessions at them. Other assistants read `AGENTS.md` (Codex) or `GEMINI.md` (Gemini CLI); all three can just say "read the notes before touching any 2K14 file". House rules for any assistant:
- Never write to a roster in `Saves\` without making a backup copy first.
- After a direct binary edit, re-sign the CRC and check it with `ros_inspect.py header`.

## Sources

- [`sources/roster-editing/ai-docs/05-ai-integration.md`](../../sources/roster-editing/ai-docs/05-ai-integration.md) and [`04-turk-scripting.md`](../../sources/roster-editing/ai-docs/04-turk-scripting.md).

## Open questions

- Has an AI-generated TURK script been run on a real roster yet? Adding one as a worked example would help.
