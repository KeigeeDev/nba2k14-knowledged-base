# How player ratings work in NBA 2K14

**Status:** [VERIFIED] for the list, storage order and roster-file encoding of the ratings (two cheat tables and the mapped `.ROS` player record agree). [DRAFT] for how ratings are encoded in memory and how the overall is computed.
**Category:** game mechanics
**Last updated:** 2026-09-27

## Summary

In NBA 2K14, each player has about 40 individual **ratings** (also called attributes). Each rating is stored as **one byte**. How much each rating matters in a game is scaled by global **sliders**, which have separate User and CPU values. To mod a player you change the ratings. To change how much a rating matters for everyone, you change the sliders.

```
 per-player ratings (bytes)  ──►  gameplay simulation  ◄──  global sliders (floats, User/CPU)
   "how good is this player"                              "how much does a rating count"
```

## The ratings

These are all the ratings found in the MyCareer rating block (see [MyCareer ratings memory map](../file-formats/mycareer-ratings-memory-map.md) for exact offsets). The grouping below was made for this doc to make the list easier to read. The game stores the ratings in a different order.

| Group | Ratings |
|---|---|
| Jump shooting | Close Shot, Medium Shot, 3PT Shot, Free Throw, Shoot Off Dribble, Shoot in Traffic |
| Finishing | Layup, Standing Layup, Spin Layup, Euro Step Layup, Hop Step Layup, Runner, Step Through, Dunk, Standing Dunk |
| Post game | Low Post Offense, Post Fadeaway, Post Hook |
| Playmaking | Ball Handling, Off-Hand Dribbling, Ball Security, Passing, Hands |
| Defense | On-Ball Defense, Low Post Defense, Steal, Block |
| Rebounding | Offensive Rebound, Defensive Rebound |
| Athleticism | Speed, Quickness, Strength, Vertical, Stamina, Durability |
| Mental / hidden | Offensive Awareness, Defensive Awareness, Consistency, Hustle, Emotion, Potential |
| Unknown meaning | `SShtLoP`, at position 5. Named by its RED MC field key; its caption isn't known yet. |

Notes:

- **Potential** is stored with the other ratings. Hexorg's table notes that changing it in MyCareer is "probably useless". It likely matters more for how players progress in franchise/association modes, but that hasn't been tested.
- **Emotion** is stored with the other ratings too, though it isn't a skill in the usual sense.
- Height, weight, and birth year are separate from the rating block (float, float, and byte). The [memory map](../file-formats/mycareer-ratings-memory-map.md) lists their addresses.

## How ratings are stored

- **One byte per rating, in the same order in memory and in the roster file.** In roster files (`.ROS`) each byte is `raw = 3 × (shown − 25)`, so shown = raw / 3 + 25, a range of 25–110 ([player record](../file-formats/ros-player-record.md#skill-ratings)). Whether the in-memory MyCareer bytes use the same encoding hasn't been tested.
- **Overall rating (OVR) isn't stored with the ratings.** Base rosters store `Overall_I = 1`; only career saves hold real values. Roster Lab estimates the overall with a per-position linear fit of the 42 ratings and claims 91% exact matches ([Roster Lab](../tools/roster-lab.md)), which fits the idea that the game computes it with position-based weights. The actual formula is still unknown. If you want a different overall, change the individual ratings.
- **Every player's ratings are in the roster file**, not just the MyCareer player's ([`.ROS` player record](../file-formats/ros-player-record.md)).

## How sliders change the effect of ratings

The slider menu groups sliders as **Offense**, **Defense**, and **Attributes** (see [sliders memory map](../file-formats/gameplay-sliders-memory-map.md)):

- **Attribute sliders** (Speed, Strength, Ball Handling, Stealing, and so on) set how strongly each rating affects gameplay, for every player at once.
- **Offense and Defense sliders** (Inside/Close/Mid/3PT Success, Layup Defense Strength, and so on) adjust success rates and how often certain plays happen, on top of what the ratings produce.
- Every slider has separate **User** and **CPU** values. Common modding uses:
  - To make one player better: edit their ratings.
  - To make every CPU three-pointer less accurate: lower the CPU 3PT Success slider.

## Ways to edit ratings

| Method | Scope | Persistence | Doc |
|---|---|---|---|
| Cheat Engine with a `.CT` table | MyCareer player only (fixed addresses) | Written to memory; whether it's kept after saving hasn't been tested | [Cheat Engine](../tools/cheat-engine.md) |
| In-game roster editor | Any player | Saved in the roster file | TODO |
| RED MC | Any player | Saved in the roster file | [RED MC](../tools/red-mc.md), [bulk edits through CSV](../workflows/roster-edit-csv.md) |
| Roster Lab by Q2K | Any player | Saved in the roster file | [Roster Lab](../tools/roster-lab.md) |
| Direct binary edit | Any player | Saved in the roster file (re-sign the CRC) | [player record](../file-formats/ros-player-record.md) |

## Sources

- `sources/cheat-tables/nba2k14_1.CT`
- Hexorg `nba_2k14_cheat_table_v2_179.ct` (see `sources/cheat-tables/README.md`)
- Roster file: [`sources/roster-editing/ai-docs/06-player-record-map.md`](../../sources/roster-editing/ai-docs/06-player-record-map.md) and [`09-roster-lab.md`](../../sources/roster-editing/ai-docs/09-roster-lab.md)

## Open questions

- Are the in-memory MyCareer bytes encoded the same way as the roster file (`raw = 3 × (shown − 25)`)?
- What does `SShtLoP` (position 5) mean in game?
- What's the exact overall-rating formula?
- Are ratings changed with Cheat Engine written to the MyCareer save when the game saves?
