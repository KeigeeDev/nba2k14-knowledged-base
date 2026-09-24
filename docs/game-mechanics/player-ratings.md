# How player ratings work in NBA 2K14

**Status:** [COMMUNITY] for the list of ratings and their storage (backed by two cheat tables). [DRAFT] for anything about how ratings are encoded or computed.
**Category:** game mechanics
**Last updated:** 2026-09-24

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
| Unknown | One unidentified byte at offset +0x05 |

Notes:

- **Potential** is stored with the other ratings. Hexorg's table notes that changing it in MyCareer is "probably useless". It likely matters more for how players progress in franchise/association modes, but that hasn't been tested.
- **Emotion** is stored with the other ratings too, though it isn't a skill in the usual sense.
- Height, weight, and birth year are separate from the rating block (float, float, and byte). The [memory map](../file-formats/mycareer-ratings-memory-map.md) lists their addresses.

## How ratings are stored

- **One byte per rating.** Whether the byte holds the rating number you see in the game or an encoded version of it is **not yet known**. Before building any tool, test it using the steps in the memory map doc.
- **Overall rating (OVR) isn't in this block.** The game probably calculates the overall from the individual ratings, possibly with position-based weights, but that's unverified. If you want a different overall, change the individual ratings.
- The mapped block covers **only the MyCareer player**, at a fixed address in the exe. The other players' ratings, and the roster/save file format, still need to be mapped.

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
| External roster editor tool | Any player | Saved in the roster file | TODO: tool and source needed |

## Sources

- `sources/cheat-tables/nba2k14_1.CT`
- Hexorg `nba_2k14_cheat_table_v2_179.ct` (see `sources/cheat-tables/README.md`)

## Open questions

- How is the byte encoded? (raw 0–99 vs. scaled)
- What is the byte at offset +0x05?
- How is the overall rating calculated from the individual ratings?
- Where is the player record stored in the roster/save file, and does it use the same rating order?
- Are ratings changed with Cheat Engine written to the MyCareer save when the game saves?
