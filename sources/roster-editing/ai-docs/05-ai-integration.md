# Integrating AI CLI Tools with RED MC

RED MC is a closed-source, packed native GUI app with **no CLI, no API, no
plugin system**. AI tools therefore integrate *around* it, not *inside* it.
Four workable patterns, in order of practicality:

## 1. AI generates TURK scripts (safest, recommended)

TURK is RED MC's only automation surface (see 04-turk-scripting.md). An AI CLI
(Claude Code, Codex, Gemini CLI) running in this folder can:

1. Read the data dictionary (`Text/NBA2K14/Captions/*.txt`, `Text/Enums.txt`)
   to know every field and legal value.
2. Generate a `.TURK` script into `Scripts\` implementing the requested batch
   edit ("set all 2024 draftees' PeakAgeS to 24", "heal all injuries", ...).
3. The user runs the script inside RED MC — RED MC handles the bit packing,
   string pool, checksum, and platform quirks.

Division of labor: AI does the *logic*, RED MC does the *file format*. No
corruption risk. Limitation: TURK can only touch fields RED MC exposes, and a
human clicks "run".

## 2. AI edits `.ROS` files directly (headless, no RED MC)

Enabled by the findings in 02-ros-format.md:

- The container checksum is cracked (**CRC32 of bytes 4..EOF at offset 0**),
  so externally modified files can be re-signed: `ros_inspect.py resign`.
- The remaining work is per-field bit mapping via differential editing
  (methodology in 02-ros-format.md). Each mapped field becomes directly
  editable by any script an AI CLI writes — fully headless, no GUI.

This is the path to a true "AI roster editor": e.g. a Python library
(`ros_inspect.py` is the seed) that the AI extends field-by-field as mappings
are confirmed. The section layout and the string-heap allocator are now
mapped (02 § Table directory, § Strings). Appending a name means writing to
heap arena A and bumping the watermark at 0x250, with no relayout. Start with
fixed-width numeric fields (ratings, bio). Before any save, run the crash
checks from [09-roster-lab.md](09-roster-lab.md): no zero face block, name
handles on string starts, team slots packed with `PlNum` in sync.

## 3. AI drives the RED MC GUI (automation of last resort)

Windows UI automation (AutoHotkey, pywinauto, or an agent with computer use)
can click through RED MC. Fragile (custom Delphi grids, admin elevation,
timing), but usable for one-off tasks that need RED MC's own logic, like
Save As with rehash/resign for consoles.

## 4. This folder as an AI workspace (already set up)

A `CLAUDE.md` at the repo root points AI sessions at `ai-docs/`. Any AI CLI
launched in `C:\Editing Tools\RED MC` should:

- Load `ai-docs/README.md` first (facts + doc map).
- Never write to a roster in `Saves\` without making a `.bak` copy first.
- After any direct binary edit, re-sign the CRC and verify with
  `python ai-docs/tools/ros_inspect.py header <file>`.

### Tool-specific notes

| Tool | How to point it at the docs |
|------|------------------------------|
| Claude Code | Reads `CLAUDE.md` automatically when launched in this directory |
| OpenAI Codex CLI | Create `AGENTS.md` with the same content |
| Gemini CLI | Create `GEMINI.md` (or configure `contextFileName`) with the same content |

All three memory files can simply say: *"Read `ai-docs/README.md` before
touching any 2K14 file."* — keeping one source of truth in `ai-docs/`.
