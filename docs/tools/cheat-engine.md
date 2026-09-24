# Cheat Engine

**Status:** [COMMUNITY]
**Category:** tool
**Last updated:** 2026-09-24

## Summary

Cheat Engine is a general-purpose memory scanner and editor for Windows. For NBA 2K14 it lets you read and write MyCareer ratings, gameplay sliders, and game clock values in live memory using community `.CT` table files. It's also the main tool for mapping new values that nobody has documented yet.

## Using a table

1. Start NBA 2K14 and load whatever mode you want to edit (for example, a MyCareer save).
2. Open Cheat Engine, click the process selector, and attach to `nba2k14.exe`.
3. Use File → Load to open the `.CT` file (for example `sources/cheat-tables/nba2k14_1.CT`).
4. Expand a group and double-click a value to change it.

## Things to know for NBA 2K14

- **Address format:** tables use module-relative addresses (`nba2k14.exe+11DD6A0`). The Hexorg table also has absolute ones (`015DD6A1`). On the tested builds, absolute = `0x400000 +` offset, meaning the exe loads at its default base.
- **Tables only match one build:** a table's static offsets only work with the exact `nba2k14.exe` it was made for. If the values look like garbage, you probably have a different build.
- **Heap addresses:** plain addresses such as `1827D9BC` (Skill Points in the Hexorg table) change from one session to the next. They'll only work reliably once someone finds pointer paths for them.
- **Data types:** ratings are `Byte`. Sliders and clocks are `Float`. When you add new entries to a table, match these types.
- **Back up saves** before you change anything and then save in-game.

## Mapping new values (general method)

1. Pick a value you can see and change in the game (for example, a slider).
2. Scan for it (exact value for integers, or "unknown initial value" for floats). Change it in the game, then use "changed/unchanged" scans until only a few results remain.
3. Look near the address you found: related values usually sit next to each other. The ratings block and the slider array are both examples.
4. Write down what you find in the matching `docs/file-formats/` doc, including the game build.

## Sources

- Tables: see `sources/cheat-tables/README.md`
- Download the tool from its official site only. Many third-party mirrors bundle adware. TODO: add the official URL once someone has checked it.

## Open questions

- Which NBA 2K14 PC builds do the existing tables work with?
