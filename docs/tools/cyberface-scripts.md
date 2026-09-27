# Cyberface helper scripts (`n2km_tools`, `dds_tools`, `cf_blender`)

**Status:** [VERIFIED] for the behaviour listed under "What was tested", which was run during review on 2026-09-27. [DRAFT] for the Blender-only functions, which weren't run (no Blender in the review environment).
**Category:** tool
**Last updated:** 2026-09-27

## Summary

The owner wrote three Python scripts for cyberface work. They live in [`sources/cyberface/scripts/`](../../sources/cyberface/scripts/). `n2km_tools.py` and `dds_tools.py` are standard-library command-line tools. `cf_blender.py` runs inside Blender, usually through [MCP for Blender](mcp-for-blender.md).

## What each script does

| Script | Runs in | Main functions |
|---|---|---|
| `n2km_tools.py` | Any Python 3 | `info model.n2km`: part list with vertex and face counts. `compare original.N2KM edited.n2km`: the pre-import safety check. Exits 0 and prints `SAFE to import` only if part names, vertex/face counts, face lists and UVs are identical. |
| `dds_tools.py` | Any Python 3 (numpy helpers need Blender) | `info file.dds`: size, format, mip count, pitch. `read_argb` / `write_argb`: uncompressed A8R8G8B8 only. DXT files are identified but not decoded or encoded. |
| `cf_blender.py` | Blender (`bpy`, numpy) | `snap`: offscreen ortho render to PNG. `tps_fit`: thin-plate-spline landmark warp. `raster_uv`: surface position and normal for each texel. `depth_map` / `depth_lookup`. `person_mask`. `blur`, `erode`, `dilate`. `mesh_components`. `validate_parts`. |

**Loading in Blender:** the notes' snippet appends `C:\2K Modding\Cyberface\scripts` to `sys.path`. Point it at wherever you keep the scripts.

## What was tested (2026-09-27)

Tested with Python 3.11, numpy 2.4.6 and Pillow 12.3.0, on synthetic files:

- **`dds_tools`**
  - A 256² A8R8G8B8 file is 262,272 bytes.
  - `read_argb` → `write_argb` round-trips byte-identical.
  - Writing at 512² with a 256² template header gives a valid 512² file.
  - Files written by `write_argb` decode correctly in Pillow, and files written by Pillow decode correctly with `read_argb`.
  - `read_argb` refuses DXT5 with a clear error.
- **`n2km_tools compare`**
  - Moved vertices → `SAFE to import` (exit 0).
  - Changed UVs → `DO NOT IMPORT` (exit 1).
  - An added vertex and face → `DO NOT IMPORT` (exit 1).
- **`n2km_tools compare` on a real file (owner's run):** it parsed the real KQ head and its edit, and the reported size matches the documented layout to the byte. [Output](../../sources/cyberface/compare-47F01028-v7.txt).
- **`cf_blender.tps_fit`**
  - With `reg=0` it reproduces an affine map exactly, including outside the landmarks.
  - With 2 px landmark noise, `reg=0.5` leaves about 0.3 px residual at the landmarks and `reg=5` about 1.5 px. The notes' "fit error < 1 px" target is reachable, but it depends on `reg`.
- **`cf_blender.mesh_components`** correctly separates disconnected pieces.
- **`cf_blender.person_mask`** keeps the subject, drops a flat background and drops a blue shirt band.

## Known issues

Found in review. None of these has been seen to cause a problem in game.

1. **`compare` ignores part order and the header's second `int32`.** A file with the same parts in a different order, or with a different value at offset 8, still reports `SAFE to import`. Whether the 3DM Tool cares is unknown ([n2km open questions](../file-formats/n2km.md#open-questions)).
2. **`validate_parts()` skips the topology check when a part has no `DEF_` copy.** It then reports `OK` based on transforms alone. It also only checks `location`, `rotation_euler` and `scale`: a quaternion rotation mode, delta transforms or a parent aren't caught.
3. **`blur()` and `dilate()` wrap around image edges**, because they're built on `np.roll`. `blur()` on a texture-space weight map also mixes weights between UV islands that happen to sit next to each other in the texture. That's the same problem the texture guide warns about for inpainting. It's probably harmless for 30-pass weight feathering, but it hasn't been checked.
4. **Small mismatch:** `person_mask` defaults to a threshold of 0.12, while the reshaping guide describes the mask at 0.10.

## Sources

- [`sources/cyberface/scripts/`](../../sources/cyberface/scripts/) (SHA-256 in [`sources/cyberface/README.md`](../../sources/cyberface/README.md)).
- Review tests: run in a scratch environment on 2026-09-27. The test scripts weren't committed.

## Open questions

- Run `snap`, `raster_uv`, `depth_map` and `validate_parts` in Blender 5.x on a real head, then upgrade this entry.
