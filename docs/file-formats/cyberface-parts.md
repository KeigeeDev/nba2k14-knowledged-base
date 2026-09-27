# Cyberface head model: parts

**Status:** [VERIFIED] for the vertex and triangle counts of KQ's head (`47F01028`): they're read from the real game file. [DRAFT] for what each part is, and for whether other heads use the same counts.
**Category:** file-format
**Last updated:** 2026-09-27

## Summary

A 2K14 cyberface head model (`.n2km`) is split into 13 parts named `0-0` to `0-12`. Most edits touch only `0-1` (face, head and neck skin), `0-12` (hair) and sometimes `0-0` (headband). The mouth and eye parts are said to be bone-driven and should stay where they are.

## Part map

Vertex and triangle counts come from the real KQ head file ([compare output](../../sources/cyberface/compare-47F01028-v7.txt)). Edge counts come from Blender, per the owner's notes, and only exist for some parts.

| Part | Verts | Triangles | Edges | What it is | Texture |
|---|---|---|---|---|---|
| `0-0` | 145 | 196 | 338 | Headband. Only visible in game with Headband = Yes. | Its own full-UV texture |
| `0-1` | 1399 | 2664 | 4065 | Face + head skin + neck | `face_color` |
| `0-2` | 91 | 100 | 185 | Mouth interior (inner lips, gums) | |
| `0-3` | 44 | 66 | | Teeth / tongue | |
| `0-4` | 66 | 60 | | Teeth / tongue | |
| `0-5` | 68 | 60 | | Teeth / tongue | |
| `0-6`, `0-7` | 113 each | 210 each | 322 each | Eyeballs | |
| `0-8` | 50 | 60 | | Eyelash / eyelid strip | |
| `0-9` | 108 | 128 | | Eyelash / eyelid strip | |
| `0-10`, `0-11` | 31 each | 36 each | 66 each | Eye-socket inner parts | |
| `0-12` | 457 | 536 | 959 | Hair: a scalp cap plus separate hair cards | `hair` |
| **Total** | **2716** | **4362** | | | |

**Orientation in Blender:** the face points to −Y, Z is up, and +X is the character's left. The head is roughly 60+ units tall.

For the pieces inside `0-12` (scalp cap, fringe cards, top fins, nape cards), see [hair](../ai-workflows/cyberface-hair.md).

## Parts not to move

According to the owner's notes, `0-2`–`0-5` (mouth interior), `0-6`/`0-7` (eyeballs) and `0-8`–`0-11` (eye parts) are bone-driven, so the photo is fitted around them rather than the other way round. The notes contradict themselves on this point; see [the workflow](../workflows/cyberface-blender.md#contradictions-in-the-source-notes).

How far each part actually moved in the owner's KQ edit `v7`, per the [compare output](../../sources/cyberface/compare-47F01028-v7.txt):

| Parts | Max vertex move (units) |
|---|---|
| `0-2`–`0-7` (mouth interior, teeth, eyeballs) | 0.00 |
| `0-8`, `0-9` (lash/lid strips) | 0.39 |
| `0-10`, `0-11` (eye-socket parts) | 0.56, 0.64 |
| `0-0` (headband) | 0.14 |
| `0-1` (face/head) | 3.33 |
| `0-12` (hair) | 12.63 |

## Consistency checks

Done during review, 2026-09-27:

- **Headband vertex count:** an NLSC thread (seen only as a search excerpt) says the game expects 145 vertices in the headband. That matches `0-0` in the real file.
- **Blender vs file counts:** the notes' Blender face counts (196, 2664, 100, 210, 36, 536) equal the file's triangle counts, so importing adds no extra vertices or faces.
- **`0-1` has four holes:** for a single connected surface, vertices − edges + faces = 2 − (number of holes). 1399 − 4065 + 2664 = −2 means 4 holes. That matches the four boundary loops the notes work with: two eye holes, the mouth hole and the neck.
- **`0-12` has 34 pieces:** 457 − 959 + 536 = 34, which fits 34 separate open pieces. That's the number of unconnected mesh components the hair guide counts.

## Sources

- [`sources/cyberface/compare-47F01028-v7.txt`](../../sources/cyberface/compare-47F01028-v7.txt): counts and per-part moves from the real KQ file.
- [`sources/cyberface/CYBERFACE_MODDING_GUIDE.md`](../../sources/cyberface/CYBERFACE_MODDING_GUIDE.md) (part map, rules) and [`sources/cyberface/guides/04_hair.md`](../../sources/cyberface/guides/04_hair.md) (`0-12` pieces).
- Headband 145 vertices: NLSC forum thread found through search on 2026-09-27. TODO: exact thread URL.

## Open questions

- Is this topology the same for every 2K14 cyberface, or only for some heads? The hair guide says to "re-check per model".
- Which bones drive which parts, and what happens in game if those parts are moved?
