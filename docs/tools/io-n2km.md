# io_n2km (Blender add-on)

**Status:** [COMMUNITY] for what the add-on is and does. [DRAFT] for using it on Blender 5.x: the owner uses it on Blender 5.2, but which build or port that is hasn't been documented.
**Category:** tool
**Last updated:** 2026-09-27

## Summary

io_n2km is a Blender add-on that imports and exports NBA 2K `.n2km` models, so you can edit a cyberface head in Blender. The original targeted old Blender versions (2.69/2.71). Community ports exist for newer ones.

## Details

- **Versions:**
  - The original was for Blender 2.69/2.71, according to the title of a download page found by search.
  - An NLSC thread offers a version for Blender 2.8x–2.9x. According to search excerpts, porting was hard because Blender's Python API changed a lot in 2.8.
  - The owner runs an `io_n2km` add-on on **Blender 5.2**. TODO: source needed for that build.
- **Operators** (owner's setup): `bpy.ops.import_scene.n2km(filepath=...)` and `bpy.ops.export_scene.n2km`. The operator lives in `import_scene`, not `import_mesh`.
- **Exporter behaviour** (owner's notes):
  - It exports every mesh whose name has `-` as its second character (`0-1`, `0-12`, ...). That means backup copies named `DEF_0-1` are skipped.
  - Meshes must be triangulated and have a UV map.
  - It splits vertices at UV seams. Unchanged game topology gains no extra vertices.
  - It writes raw vertex coordinates, so object transforms must be identity.

## Sources

- Owner's notes: [`sources/cyberface/guides/01_blender_mcp_setup.md`](../../sources/cyberface/guides/01_blender_mcp_setup.md) and [`guides/05_file_formats.md`](../../sources/cyberface/guides/05_file_formats.md).
- NLSC, "Blender2.8X -2.9X IO_N2KM": https://forums.nba-live.com/viewtopic.php?t=111897 (found through search 2026-09-27; not opened, the forum is blocked in the review environment).
- "NBA 2K14 io_n2km Blender 2.69/2.71 Model Import and Export Tool": https://www.shuajota.com/2021/02/nba-2k14-ion2km-blender-269271-model.html (found through search 2026-09-27; not opened. It's a third-party repost, so check its download before running it.)

## Open questions

- Who wrote the original add-on and the ports?
- Where does the Blender 5.x-compatible version come from?
- Does the exporter keep the original part order?
