# Make or edit a cyberface in Blender

**Status:** [COMMUNITY] for the toolchain and the overall order of steps. They match icecr's NLSC tutorial as described in search results (the forum itself couldn't be opened for this review). [VERIFIED] for the eye and mouth part rules, which the owner tested in game on KQ. [DRAFT] for the other rules and the Blender 5.x details, which come from one project ("KQ") in the repo owner's notes.
**Category:** workflow
**Last updated:** 2026-09-27

## Summary

Each cyberface is stored in a `png<ID>.iff` file. You extract the head model (`.n2km`) and its textures (`.dds`) with the 3DM Tool, edit them in Blender, and import them back with the 3DM Tool. You can move vertices, but the model's topology (vertex, edge and face counts) must not change.

## Prerequisites

- [RED MC](../tools/red-mc.md): roster editor, used to look up the player's CyberFace ID.
- [3DM Tool](../tools/3dm-tool.md): opens `.iff` files, exports and re-imports the model and textures.
- Blender with an [io_n2km add-on](../tools/io-n2km.md) that works with your Blender version.
- A DDS converter that writes DXT1/DXT5 (the notes use NVIDIA DDS tools or Photoshop). TODO: source needed for a current download.
- Optional: [MCP for Blender](../tools/mcp-for-blender.md), so an AI assistant can drive Blender (see the AI workflows linked in step 5).
- Optional: the owner's [helper scripts](../tools/cyberface-scripts.md) (`n2km_tools.py`, `dds_tools.py`, `cf_blender.py`).

## Steps

1. **Find the file.** Open the roster in RED MC and read the player's **CyberFace ID** under Appearance. The notes' example: ID 326 → `png0326.iff`. TODO: document where the `png*.iff` files live in the game install.
2. **Back up** the original `.iff`. Never overwrite game originals: always write edited files under new names (`_edit`, `_v2`, ...).
3. **Extract.** Open `png<ID>.iff` in the 3DM Tool. Export the model (`<hash>.N2KM`) and the textures `face_color.dds`, `hair.dds` and `skin_colour.dds`.
4. **Import into Blender** with the io_n2km add-on (`bpy.ops.import_scene.n2km` in the owner's setup). Keep an untouched copy of every part to compare against later. The owner keeps `DEF_0-*` copies with their own mesh data in a hidden collection.
5. **Edit.** Only move vertices. Methods used in the owner's project:
   - [Reshaping the head to reference photos](../ai-workflows/cyberface-reshaping.md)
   - [Baking photos into the face texture](../ai-workflows/cyberface-texture-projection.md)
   - [Hair: part `0-12` and `hair.dds`](../ai-workflows/cyberface-hair.md)
6. **Check before export.** Every part must keep its original vertex, edge and face counts. Every object must have identity transforms (location 0, rotation 0, scale 1), because according to the notes the exporter writes raw vertex coordinates.
7. **Export** to a new `.n2km` file. Then run the safety check, which must print `SAFE to import`:
   ```
   python sources/cyberface/scripts/n2km_tools.py compare original.N2KM edited.n2km
   ```
   The check doesn't compare part order (see [known issues](../tools/cyberface-scripts.md#known-issues)).
8. **Convert textures** to the same format as the originals. See [cyberface textures](../file-formats/cyberface-textures.md).
9. **Import** the edited model and textures back into the `.iff` with the 3DM Tool.
10. **Test in game.** Use Edit Player and look at the front, 3/4, side and back views. Write down what's wrong before the next pass.

## Rules

| Rule | Confidence | Why |
|---|---|---|
| Never add or delete geometry (vertices, edges, faces) | [COMMUNITY] | The owner's notes say the 3DM Tool fails otherwise. NLSC threads (seen only as search excerpts) report import errors when a part's vertex count differs from what the game expects (e.g. a headband with 124 verts instead of 145), or when an edited `0-1` is larger than the original. The [`.n2km` face list](../file-formats/n2km.md) refers to vertices by index, which fits this rule. |
| Object transforms must be identity at export | [DRAFT] | Owner's notes: the exporter writes raw vertex coordinates. |
| Keep the neck's bottom boundary loop fixed | [DRAFT] | Owner's notes: it meets the body mesh. |
| Never move the mouth interior, teeth or eyeballs (`0-2`–`0-7`) | [VERIFIED] | Owner's notes say they're bone-driven. The KQ edit `v7` left them at 0.00 movement and looked right in game. |
| Eye parts `0-8`–`0-11` may move a little (up to about 0.6 units) to follow reshaped eyelids | [VERIFIED] | KQ `v7` moved them 0.39–0.64 units, and lids, lashes and eyes looked right in game. Bigger moves are untested. |
| Don't scale the whole head uniformly including `0-2`–`0-11` | [DRAFT] | Never tried. The owner expects it wouldn't look good. Resize with displacement fields on the visible head parts instead ([reshaping](../ai-workflows/cyberface-reshaping.md#4-apply-smooth-displacement-fields)). |
| Never overwrite game originals | Standard practice | Keeps a way back. |

### How the eye and mouth rules were settled

The source notes contradicted themselves on two points:

- The index says "Uniform head scaling (e.g. 1.03) applies to **every** part". It also says not to move the eyes, eye parts or mouth interior, but scaling every part would move them (about 1 unit at eye height for a 1.03 scale).
- The index says not to move eye parts `0-8`–`0-11`. The reshaping guide's eyelid method moves them on purpose.

The owner's KQ edit `v7` settles both. Its [compare output](../../sources/cyberface/compare-47F01028-v7.txt) shows these moves, and the owner confirmed on 2026-09-27 that `v7` looked right in game (eyes in their sockets, lids, lashes, mouth and teeth normal):

| Parts | Max move in `v7` (units) |
|---|---|
| `0-2`–`0-7` (mouth interior, teeth, eyeballs) | 0.00 |
| `0-8`–`0-11` (eye parts) | 0.39–0.64 |
| `0-0` (headband) | 0.14 |
| `0-1` (face/head) | 3.33 |
| `0-12` (hair) | 12.63 |

The rules table above reflects this. The index's "uniform scaling applies to every part" line was never tested and is superseded here. The source file is kept unchanged as evidence.

## Common pitfalls

- Blender can't open `hair.dds` (uncompressed A8R8G8B8). Use `dds_tools.read_argb`, see [cyberface textures](../file-formats/cyberface-textures.md).
- The headband (`0-0`) only shows in game when Headband = Yes. After an ear edit, check it still clears the ears.
- Photos never show the back of the head, so the default player's hair texture stays there. See [texture projection limitations](../ai-workflows/cyberface-texture-projection.md#known-limitations).

## Sources

- Owner's notes: [`sources/cyberface/CYBERFACE_MODDING_GUIDE.md`](../../sources/cyberface/CYBERFACE_MODDING_GUIDE.md) (SHA-256 in [`sources/cyberface/README.md`](../../sources/cyberface/README.md)).
- icecr, "Tutorial: How to Create Any Cyber Face in Blender", NLSC forum: https://forums.nba-live.com/viewtopic.php?f=154&t=113460. The owner's notes cite it as their base. It couldn't be opened from the review environment (the forum is blocked there). According to search excerpts it lists Blender 2.69/2.72, the 3DM Tool, an import/export script for Blender, NVIDIA DDS Texture Tools, Photoshop and RED MC, and uses `png0326.iff` as its example.
- Vertex-count import errors: NLSC forum threads seen only as search excerpts on 2026-09-27. TODO: pin down the exact thread URLs.

## Open questions

- Where do the `png*.iff` files sit in the install, and what are the exact 3DM Tool menu steps for export and import?
- What happens in game if eye parts `0-8`–`0-11` move more than about 0.6 units?
- Does the 3DM Tool accept textures larger than the originals (hair 512², face above 512²)?
- Do all 2K14 cyberfaces share the same part topology, or does it vary by head?
