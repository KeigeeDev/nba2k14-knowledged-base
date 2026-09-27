# NBA 2K14 Cyberface Modding — Main Guide (index)

Reference for making NBA 2K14 cyberfaces in Blender, driven through the Blender MCP.
Based on icecr's NLSC tutorial (https://forums.nba-live.com/viewtopic.php?f=153&t=113460) plus what was learned here.

## Keeping these docs up to date (rule for Claude)
- **Every new process, fix, gotcha or improvement gets written down** — in the sub-guide it belongs to
  (or a new one), never left only in chat.
- **Keep this file small**: index, hard rules, part map. Details → `guides/`, per-player history → `projects/`,
  reusable code → `scripts/`. Prefer updating an existing section over appending a new one.
- If a fact turns out wrong, correct it in place (and note the correction in the project log).

## Folder map
```
CYBERFACE_MODDING_GUIDE.md   this index
guides/01_blender_mcp_setup.md   connect, import, scene setup, screenshots, MCP quirks
guides/02_reshaping.md           reference scaling, measuring, displacement fields, validation
guides/03_texture_projection.md  face texture from photos (TPS warp, weights, colour match)
guides/04_hair.md                hair part 0-12: anatomy, reshaping cards, hair texture + alpha
guides/05_file_formats.md        .n2km and .dds formats, which tool writes what
scripts/cf_blender.py            Blender-side helpers (snap, tps_fit, raster_uv, depth_map, validate…)
scripts/dds_tools.py             read/write uncompressed A8R8G8B8 DDS, DDS header info (CLI)
scripts/n2km_tools.py            n2km info + safety compare vs original (CLI)
projects/<PLAYER>.md             per-player log: measurements, decisions, outputs, open issues
<PLAYER>/                        per-player files (originals never overwritten)
```

## Toolchain
| Tool | Notes |
|---|---|
| RED MC (`C:\Editing Tools\RED MC`) | roster editor → player's **CyberFace ID** (Appearance); eye colour etc. |
| 3DM Tool (`C:\2K Modding\Tools\3DM`) | open `png<ID>.iff`, export `.n2km` + `.dds`, re-import edited model/textures |
| Blender 5.2 + `io_n2km` add-on | `bpy.ops.import_scene.n2km` / `bpy.ops.export_scene.n2km` |
| Blender MCP | drives Blender; see `guides/01_blender_mcp_setup.md` |
| Photoshop / NVIDIA DDS tools | DXT1/DXT5 DDS conversion (compressed formats) |

## Workflow
1. **Find** – RED MC → CyberFace ID 326 → `png0326.iff`.
2. **Extract** – 3DM Tool → `<hash>.N2KM`, `face_color.dds`, `hair.dds`, `skin_colour.dds`.
3. **Set up** Blender scene + references → guide 01.
4. **Reshape** the head → guide 02.   5. **Face texture** → guide 03.   6. **Hair** → guide 04.
7. **Validate + export** (`n2km_tools.py compare` must say SAFE), convert textures (guide 05), import with 3DM Tool.
8. **In-game test** (Edit Player: front, 3/4, side, back screenshots) → log issues in `projects/<PLAYER>.md`.

## Hard rules
- **Never add or delete geometry.** Vertex/edge/face counts per part must stay identical, or the 3DM Tool fails.
- Uniform head scaling (e.g. 1.03) applies to **every** part.
- Don't move the mouth interior (`0-2…0-5`), eyes (`0-6`,`0-7`) or eye parts (`0-8…0-11`) — bone-driven.
- Keep the neck's bottom boundary loop fixed (meets the body mesh).
- Object transforms must be identity at export (exporter writes raw vertex coords).
- Never overwrite game originals (`.iff`, original `.N2KM`, original `.dds`) — write `_edit` / `_kq` / `_v2` files.

## Part map (2K14 cyberface; Blender axes: face → −Y, Z up, +X = character's left)
| Part | Verts/Edges/Faces | What it is |
|---|---|---|
| 0-0 | 145/338/196 | **headband** (own full-UV texture; only visible with Headband = Yes) |
| 0-1 | 1399/4065/2664 | face + head skin + neck (`face_color`) |
| 0-2 | 91/185/100 | mouth interior (inner lips/gums) |
| 0-3, 0-4, 0-5 | 44, 66, 68 verts | teeth / tongue |
| 0-6, 0-7 | 113/322/210 each | eyeballs |
| 0-8, 0-9 | 50, 108 verts | eyelash / eyelid strips |
| 0-10, 0-11 | 31/66/36 each | eye-socket inner parts |
| 0-12 | 457/959/536 | **hair**: scalp cap + separate hair cards (`hair.dds`) → guide 04 |

## Projects
- KQ → `projects/KQ.md`
