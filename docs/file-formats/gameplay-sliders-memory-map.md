# Gameplay sliders — in-memory layout

**Status:** [DRAFT]. There's only one source (`nba2k14_1.CT`, whose own header labels its sliders section "Work in Progress"), and nothing has been tested in-game.
**Category:** file-format (runtime memory)
**Last updated:** 2026-09-24

## Summary

Sliders are **global** tuning values. They aren't stored per player. Player ratings say how good a specific player is. Sliders scale how much ratings, and certain outcomes, count in the gameplay simulation. Each slider is a 4-byte `Float` at a fixed address inside `nba2k14.exe`, in a region starting around `nba2k14.exe+F0C970`.

## Layout pattern

- Every slider slot takes 8 bytes: **User value at +0, CPU value at +4**. The Offense and Defense groups are listed with both halves.
- The "Attributes" slider group is listed only at 8-byte-aligned addresses, which would be the User half under this pattern. **Hypothesis:** each attribute slider's CPU value is at the same address + 4. Not verified.
- It isn't known how a float maps to the in-game slider number (0–100, 0.0–1.0, or something else). Read a value while looking at the slider menu to find out.

## Attribute sliders (effect of each rating)

| Address (RVA) | Slider | Note |
|---|---|---|
| F0C970 | Stealing | |
| F0C978 | Blocking | |
| F0C980 | Speed | |
| F0C988 | Ball Handling | |
| F0C990 | Dunking Ability | |
| F0C998 | Offensive Awareness | |
| F0C9A0 | Defensive Awareness | |
| F0C9A8 | Offensive Rebounding | |
| F0C9B0 | Defensive Rebounding | |
| F0C9B8 | Strength | |
| F0C9C0 | Quickness | |
| F0C9C8 | Hustle | |
| F0C9D0 | Consistency | |
| F0C9D8 | Durability | |
| F0C9E0 | Stamina | |
| F0C9E8 | Hands | |
| F0C9F0 | Vertical | |
| F0C9F8 | On-Ball Defense | |
| F0CAC0 | Injury Frequency | listed under "Attributes" in the table |
| F0CAC8 | Injury Severity | listed under "Attributes" in the table |
| F0CAD0 | Fatigue Rate | listed under "Attributes" in the table |

## Offense sliders

| User (RVA) | CPU (RVA) | Slider |
|---|---|---|
| F0CA00 | F0CA04 | Alley-Oop Success |
| F0CA08 | F0CA0C | Contact Shot Success |
| F0CA10 | F0CA14 | Inside Shot Success |
| F0CA18 | F0CA1C | Close Shot Success |
| F0CA20 | F0CA24 | Mid-Range Success |
| F0CA28 | F0CA2C | 3PT Success |
| F0CA30 | F0CA34 | Layup Success |
| F0CA38 | F0CA3C | Dunk in Traffic Frequency |
| F0CA40 | F0CA44 | Dunk in Traffic Success |
| F0CA48 | F0CA4C | **Unknown** (gap) |
| F0CA50 | F0CA54 | Pass Accuracy |

## Defense sliders

| User (RVA) | CPU (RVA) | Slider |
|---|---|---|
| F0CA58 | F0CA5C | Steal Success |
| F0CA60 | F0CA64 | Driving Contact Shot Frequency |
| F0CA68 | F0CA6C | Inside Contact Shot Frequency |
| F0CA70 | F0CA74 | Layup Defense Strength (Takeoff) |
| F0CA78 | F0CA7C | Layup Defense Strength (Release) |
| F0CA80 | F0CA84 | Jump Shot Defense Strength (Gather) |
| F0CA88 | F0CA8C | Jump Shot Defense Strength (Release) |
| F0CB28 | F0CB2C | Help Defense Strength |

## Unmapped gaps

The region is laid out as one contiguous array. These slots haven't been identified:

- `F0CA48`/`F0CA4C`: one slot, between Dunk in Traffic Success and Pass Accuracy
- `F0CA90`–`F0CABC`: six slots, between the jump-shot defense sliders and Injury Frequency
- `F0CAD8`–`F0CB24`: ten slots, between Fatigue Rate and Help Defense Strength
- Anything below `F0C970` or above `F0CB2C`

The game's slider menu has more entries than this table maps, including tendency and foul sliders. They're probably in these gaps. To find them, change one slider in the menu and watch which float changes in Cheat Engine.

## Other fixed-address game settings

| Address (RVA) | Field | Type | Source |
|---|---|---|---|
| 19EE5EC | Quarter (current) | Byte | Hexorg |
| 19EE5F0 | Quarter Length | 4 Bytes | upload |
| 19EE638 | Game Clock | Float | Hexorg |
| 19EE654 | Shot Clock | Float | upload |
| 1A17018 | Drill Clock | Float | Hexorg |
| 1A85AAC | Game Speed | Float | Hexorg |

## Sources

- `sources/cheat-tables/nba2k14_1.CT` (the "Sliders (Work in Progress)" and "In-Game Settings" groups)
- Hexorg `nba_2k14_cheat_table_v2_179.ct` ("In-Game" and "Options" groups; see `sources/cheat-tables/README.md`)

## Open questions

- How do the floats map to the 0–100 values shown in the menu?
- Are the CPU values for the attribute sliders at +4, as the pattern suggests?
- Which sliders fill the gaps listed above?
- Do slider changes made in memory persist, or does the game overwrite them from its settings when a game starts?
