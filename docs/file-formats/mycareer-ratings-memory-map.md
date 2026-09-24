# MyCareer player ratings — in-memory layout

**Status:** [COMMUNITY] — addresses match across two separately obtained cheat tables. They haven't been tested in-game by this repo yet.
**Category:** file-format (runtime memory)
**Last updated:** 2026-09-24

## Summary

While the game is running, the MyCareer player's ratings sit in a block of **42 bytes, one byte per rating**, at a fixed address inside `nba2k14.exe`: `nba2k14.exe+11DD6A0` through `nba2k14.exe+11DD6C9`. Because the address is fixed, you don't need pointer chains to find it. 41 of the 42 bytes have been identified.

This is the **MyCareer player only**. The data for other players (roster/franchise players) lives elsewhere and hasn't been mapped yet.

## Addressing

- Addresses are written relative to the module (`nba2k14.exe+RVA`). In Cheat Engine, entering the address in exactly that form resolves it correctly.
- The Hexorg table writes some of the same entries as absolute addresses (e.g. `015DD6A1`). Each one equals `0x400000 + RVA`, so the two tables point to the same bytes. This implies the exe loads at the default base `0x400000` (no ASLR relocation) on the builds these tables were made for.
- **These addresses are only valid for the specific `nba2k14.exe` build the tables were made for.** A different patch or executable will likely move them. Note: the `v2_179` in Hexorg's filename might be a game version, but that hasn't been confirmed.

## Rating byte map

Base = `nba2k14.exe+11DD6A0`. "Both" means the entry appears at this address in both source tables. "Upload only" means only `nba2k14_1.CT` has it.

| Offset | Address (RVA) | Rating | Sources |
|---|---|---|---|
| +0x00 | 11DD6A0 | Close Shot | Both |
| +0x01 | 11DD6A1 | Medium Shot | Both |
| +0x02 | 11DD6A2 | Ball Handling | Both |
| +0x03 | 11DD6A3 | 3PT Shot | Both |
| +0x04 | 11DD6A4 | Free Throw | Both |
| +0x05 | 11DD6A5 | **Unknown** | Neither (see open questions) |
| +0x06 | 11DD6A6 | Runner | Both |
| +0x07 | 11DD6A7 | Standing Layup | Upload only |
| +0x08 | 11DD6A8 | Layup | Both |
| +0x09 | 11DD6A9 | Spin Layup | Both |
| +0x0A | 11DD6AA | Euro Step Layup | Both |
| +0x0B | 11DD6AB | Hop Step Layup | Both |
| +0x0C | 11DD6AC | Step Through | Both |
| +0x0D | 11DD6AD | Dunk | Both |
| +0x0E | 11DD6AE | Standing Dunk | Both |
| +0x0F | 11DD6AF | Shoot in Traffic | Both |
| +0x10 | 11DD6B0 | Shoot Off Dribble | Both |
| +0x11 | 11DD6B1 | Hustle | Both |
| +0x12 | 11DD6B2 | Off-Hand Dribbling (labeled "Off Ball Handling" in the upload) | Both |
| +0x13 | 11DD6B3 | Ball Security | Both |
| +0x14 | 11DD6B4 | Passing | Both |
| +0x15 | 11DD6B5 | Low Post Defense | Both |
| +0x16 | 11DD6B6 | Low Post Offense | Both |
| +0x17 | 11DD6B7 | Block | Both |
| +0x18 | 11DD6B8 | Hands | Both |
| +0x19 | 11DD6B9 | Steal | Both |
| +0x1A | 11DD6BA | Speed | Both |
| +0x1B | 11DD6BB | Stamina | Both |
| +0x1C | 11DD6BC | Emotion | Both |
| +0x1D | 11DD6BD | Vertical | Both |
| +0x1E | 11DD6BE | Offensive Rebound | Both |
| +0x1F | 11DD6BF | Defensive Rebound | Both |
| +0x20 | 11DD6C0 | Durability | Both |
| +0x21 | 11DD6C1 | Defensive Awareness | Both |
| +0x22 | 11DD6C2 | Offensive Awareness | Both |
| +0x23 | 11DD6C3 | Consistency | Both |
| +0x24 | 11DD6C4 | On-Ball Defense | Both |
| +0x25 | 11DD6C5 | Quickness | Both |
| +0x26 | 11DD6C6 | Potential | Both (Hexorg notes "probably useless in Career") |
| +0x27 | 11DD6C7 | Strength | Both |
| +0x28 | 11DD6C8 | Post Fadeaway | Both |
| +0x29 | 11DD6C9 | Post Hook | Both |

The byte order doesn't follow the in-game menu categories. For example, Ball Handling sits between Medium Shot and 3PT, and the post shots come last. Don't assume the order matches what the menu shows.

## Other MyCareer fields near the ratings block

From `nba2k14_1.CT`:

| Address (RVA) | Field | Type |
|---|---|---|
| 11DD52C | Height | Float |
| 11DD530 | Weight | Float |
| 11DD53E | Birth Year | Byte |

These are 0x174 bytes before the ratings block, which suggests they belong to the same player struct. The units of the Height and Weight floats (inches, cm, lbs?) haven't been checked. Birth Year is a single byte, so it's probably stored as an offset from some base year rather than a full year. This is unverified.

## Non-static entries (don't rely on these)

Hexorg's table also lists **Difficulty**, **Number Of Games In Season**, **Number Of Fans**, **Draft Position**, and **Skill Points** at absolute addresses like `1827D9BC`. These are heap addresses and will almost certainly be different in every session. To use them reliably, someone would have to find pointer paths first.

## How to verify / extend

1. Load `sources/cheat-tables/nba2k14_1.CT` in Cheat Engine and attach it to `nba2k14.exe` with a MyCareer save loaded.
2. Open the MyCareer attributes screen. For a few ratings, compare the displayed value with the byte value (in Cheat Engine, set the display to decimal).
3. **Encoding check:** if the byte doesn't match the displayed number, spend one skill point on a rating and note how much the byte changes. See the open questions.
4. **Offset +0x05:** put the byte at `nba2k14.exe+11DD6A5` in the table, change it by a large amount, and see which rating changes on the attributes screen.
5. Record the game build you tested on, the exe's file size or hash, and the results in this doc. Then upgrade the status to `[VERIFIED]`.

## Sources

- `sources/cheat-tables/nba2k14_1.CT` (the "My Career → Attributes", "Vitals", and "Body and Head" groups)
- Hexorg `nba_2k14_cheat_table_v2_179.ct` (the "MyCareer → Attributes" group). The link is in `sources/cheat-tables/README.md`.

## Open questions

- **What is offset +0x05?** Neither table labels it. One lead: the game's sliders have separate "Inside Shot Success" and "Close Shot Success" values (see [sliders map](gameplay-sliders-memory-map.md)), so a separate "Shot Inside" rating is plausible. This is a hypothesis only.
- **How are values encoded?** Does the byte store the displayed rating (e.g. 0–99) directly, or a scaled or offset form? Community tools for some older 2K roster files have described ratings as stored in scaled form. It's unconfirmed whether that applies to NBA 2K14 or to this memory block, so test it (step 3 above) before writing a tool that depends on it.
- Does this block mirror the rating section of the player record in the roster/save file? If it does, the same byte order could help map the roster format.
- Which game build(s) do these addresses match?
