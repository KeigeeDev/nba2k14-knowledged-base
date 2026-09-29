# `.ROS` player record

**Status:** [VERIFIED] for the fields in the "Mapped fields" table and for the skill-rating storage order. Each was confirmed on real rosters by the owner and cross-checked against Roster Lab, and the rating order also matches the cheat-table memory layout. [DRAFT] for the unmapped regions and the items under "Open questions".
**Category:** file-format
**Last updated:** 2026-09-27

## Summary

Each player is a **3,644-bit record** in section 0x0103 of a [`.ROS` file](ros-roster.md). There are 1,665 pre-allocated slots, and empty slots already carry their own ID. A record's position follows from the section start, so no searching is needed:

```
record_bit(i) = start(0x0103) + 3644 × i        (start = bit 324,960 in stock rosters)
```

Within a record, bit offsets are MSB-first and big-endian.

## Mapped fields

Record bit = offset from the record's first bit. "Anchor" is the older convention in the owner's notes: the first bit of BirthYear, which is record bit 273.

| Record bit | Width | Field | Encoding / notes |
|---|---|---|---|
| 0 | 16 | Stamp | `0x0103` |
| 16 | 16 | ID | Slot index |
| 32 | 32 | Last_Name | Heap handle ([string heap](ros-roster.md#string-heap)) |
| 64 | 32 | First_Name | Heap handle |
| 128 | 32 | Height | **float32, centimetres** (e.g. 203.20 = 6'8") |
| 160 | 32 | Weight | **float32, pounds** |
| 192 | 32 | Team | Reference `[010A][team index]`. Current team (`TeamID1`). |
| 273 | 11 | BirthYear | Raw year |
| 284 | 4 | BirthMonth | 1–12 |
| 288 | 5 | BirthDay | 1–31. Storage order is year, month, day, even though RED MC lists day, month, year. |
| 295–299 | 1 each | IsRegular, IsUnused, IsGener, IsDrafted, IsDraftee | Flags |
| 301 | 7 | Number (jersey) | |
| 320 | 32 | College | Reference `[010B][college]` |
| 352 | 32 | DraftedBy | Reference `[010A][team]` |
| 388 | 28 | Face block | Presence 388–391, group 392–402, HS_ID 403–415. **All zeros crashes the game.** |
| 456 | 3 | Pos | PG 0, SG 1, SF 2, PF 3, C 4 |
| 960 | 5 | YearsPro | |
| 1454 | 5 | PlayStyle | Index into the 31-entry PlayStyle enum |
| 1935 | 26 | CYear1 | Contract salary, year 1, in dollars |
| 1967 | 26 | CYear2 | Contract salary, year 2 |
| 2313 | 32 | Second team reference | `[010A]`. Equal to the current team for 1351/1351 players in one roster. Unnamed in Roster Lab. |
| 2377 | 32 | Skills boost | Reference `[012D]` |
| 2425 | 16 | ASA_ID | Second global player id. **Must be unique**, or box scores glitch. |
| 2631 | 16 | ID2 | Keep equal to ID |
| 2844 | 42 × 8 | **Skill ratings** | See below |

Roster Lab's schema places most other fields, but it only bounds 162 of its 343 player fields. Its schema files can't be copied here because of their licence.

## Skill ratings

There are 42 consecutive 8-bit values at record bit 2844, encoded as **`raw = 3 × (shown − 25)`**, i.e. `shown = raw / 3 + 25`. That covers 25–110 in 8 bits; Roster Lab's UI caps at 99. Every rating value in real rosters is a multiple of 3.

Storage order, with RED MC field keys:

| # | Key | # | Key | # | Key |
|---|---|---|---|---|---|
| 0 | SShtCls (Close Shot) | 14 | SStdDunk (Standing Dunk) | 28 | SEmotion |
| 1 | SShtMed (Medium Shot) | 15 | SShtInT (Shoot in Traffic) | 29 | SVertical |
| 2 | SBallHndl (Ball Handling) | 16 | SShtOfD (Shoot off Dribble) | 30 | SOReb |
| 3 | SSht3PT | 17 | SHustle | 31 | SDReb |
| 4 | SShtFT | 18 | SOffHDrib (Off-Hand Dribble) | 32 | SDurab |
| 5 | **SShtLoP** | 19 | SBallSec | 33 | SDAwar |
| 6 | SRunner | 20 | SPass | 34 | SOAwar |
| 7 | SLayUpStnd | 21 | SDLowPost | 35 | SConsis |
| 8 | SLayUp | 22 | SOLowPost | 36 | SOnBallD |
| 9 | SLayUpSpin | 23 | SBlock | 37 | SQuick |
| 10 | SLayUpEuro | 24 | SHands | 38 | SPOT (Potential) |
| 11 | SLayUpHop | 25 | SSteal | 39 | SStrength |
| 12 | SStpThru | 26 | SSpeed | 40 | SPstFdaway |
| 13 | SDunk | 27 | SStamina | 41 | SPstHook |

How this order is known:

1. **Roster Lab's schema** places the fields in this order.
2. **Height correlation:** across 1,375 rostered players, rebounding, blocks, post defense and standing dunk correlate strongly with height (+0.68 to +0.78), and speed, quickness, ball handling and 3PT correlate negatively. RED MC's display order gives physically impossible results.
3. **Independent match (review, 2026-09-27):** the MyCareer rating block in memory, mapped from two separate cheat tables ([memory map](mycareer-ratings-memory-map.md)), has **the same order at all 42 positions**. The byte the cheat tables couldn't name (+0x05) is `SShtLoP` here.

## Crash rules for writers

- Never write an all-zero face block to a 0x0103 record. The safe template is `0x11B0` at bit 388 (presence 1, group 216, HS_ID 0). The template sections 0x0104–0x0107 are *meant* to be zero.
- Name handles must hit a string start.
- Team membership is decided by the team's `Ros_R0`–`R19` slots, not the player's team reference. The two disagree for 372 players in a stock association. See [the container rules](ros-roster.md#rules-any-writer-must-respect).

## What changes when a player is created in game

On the owner's test, creating one custom player changed 233 bytes across about 10 regions:
- the CRC,
- the new player's record,
- the new name strings in the heap,
- several bookkeeping regions whose meaning is still a hypothesis (used-slot counters, list ordering).

An in-game re-save also changes about one byte in many unrelated tables, so always anchor on the player record rather than reading the raw diff.

## Sources

- [`sources/roster-editing/ai-docs/06-player-record-map.md`](../../sources/roster-editing/ai-docs/06-player-record-map.md) (controlled custom-player experiment and population statistics) and [`09-roster-lab.md`](../../sources/roster-editing/ai-docs/09-roster-lab.md) (Roster Lab's hand-proven `PLAYER_FIELDS` and schema).
- [`sources/roster-editing/ai-docs/08-official-field-spec.md`](../../sources/roster-editing/ai-docs/08-official-field-spec.md): RED MC's own field spec types Height as `Double` (really float32) and ratings as `Double Min: 25 Max: 110` (really scaled 8-bit).
- Review checks (2026-09-27):
  - The anchors the notes give for two known slots (121 at bit 766,157 and 1131 at bit 4,446,597) equal `324,960 + 3644 × slot + 273`.
  - The rating order matches [`sources/cheat-tables/nba2k14_1.CT`](../../sources/cheat-tables/nba2k14_1.CT) via the memory map.

## Open questions

- What does `SShtLoP` mean (its RED MC caption)?
- What are the fields Roster Lab only bounds, and the tendencies, hot zones, animations and gear region after the ratings (record bits 3180–3639)?
- Does the second team reference at bit 2313 ever differ from the current team, and what does that mean?
- Are the "−128..127" fields in Player_Ratings0–4 (sections 0x011D–0x0121) really signed? Nothing signed has been found elsewhere.
