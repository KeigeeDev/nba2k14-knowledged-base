# Cyberface head model: parts

**Status:** [DRAFT]. The counts come from the owner's notes on one project. Two of them are backed by other evidence (see "Consistency checks").
**Category:** file-format
**Last updated:** 2026-09-27

## Summary

A 2K14 cyberface head model (`.n2km`) is split into 13 parts named `0-0` to `0-12`. Most edits touch only `0-1` (face, head and neck skin), `0-12` (hair) and sometimes `0-0` (headband). The mouth and eye parts are said to be bone-driven and should stay where they are.

## Part map

The counts are vertices/edges/faces as Blender shows them after import. For some parts the notes only give a vertex count.

| Part | Verts / Edges / Faces | What it is | Texture |
|---|---|---|---|
| `0-0` | 145 / 338 / 196 | Headband. Only visible in game with Headband = Yes. | Its own full-UV texture |
| `0-1` | 1399 / 4065 / 2664 | Face + head skin + neck | `face_color` |
| `0-2` | 91 / 185 / 100 | Mouth interior (inner lips, gums) | |
| `0-3`, `0-4`, `0-5` | 44, 66, 68 verts | Teeth / tongue | |
| `0-6`, `0-7` | 113 / 322 / 210 each | Eyeballs | |
| `0-8`, `0-9` | 50, 108 verts | Eyelash / eyelid strips | |
| `0-10`, `0-11` | 31 / 66 / 36 each | Eye-socket inner parts | |
| `0-12` | 457 / 959 / 536 | Hair: a scalp cap plus separate hair cards | `hair` |

**Orientation in Blender:** the face points to −Y, Z is up, and +X is the character's left. The head is roughly 60+ units tall.

For the pieces inside `0-12` (scalp cap, fringe cards, top fins, nape cards), see [hair](../ai-workflows/cyberface-hair.md).

## Parts not to move

According to the owner's notes, `0-2`–`0-5` (mouth interior), `0-6`/`0-7` (eyeballs) and `0-8`–`0-11` (eye parts) are bone-driven, so the photo is fitted around them rather than the other way round. The notes contradict themselves on this point; see [the workflow](../workflows/cyberface-blender.md#contradictions-in-the-source-notes).

## Consistency checks

Done during review, 2026-09-27:

- **Headband vertex count:** an NLSC thread (seen only as a search excerpt) says the game expects 145 vertices in the headband. That matches `0-0` above.
- **`0-1` has four holes:** for a single connected surface, vertices − edges + faces = 2 − (number of holes). 1399 − 4065 + 2664 = −2 means 4 holes. That matches the four boundary loops the notes work with: two eye holes, the mouth hole and the neck.
- **`0-12` has 34 pieces:** 457 − 959 + 536 = 34, which fits 34 separate open pieces. That's the number of unconnected mesh components the hair guide counts.

## Sources

- [`sources/cyberface/CYBERFACE_MODDING_GUIDE.md`](../../sources/cyberface/CYBERFACE_MODDING_GUIDE.md) (part map, rules) and [`sources/cyberface/guides/04_hair.md`](../../sources/cyberface/guides/04_hair.md) (`0-12` pieces).
- Headband 145 vertices: NLSC forum thread found through search on 2026-09-27. TODO: exact thread URL.

## Open questions

- Is this topology the same for every 2K14 cyberface, or only for some heads? The hair guide says to "re-check per model".
- Which bones drive which parts, and what happens in game if those parts are moved?
