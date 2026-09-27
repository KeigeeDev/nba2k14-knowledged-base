# 05 — File formats and conversion

## .n2km (model) — `scripts/n2km_tools.py`
```
"2KM\0"  int32 partCount  int32 20
per part: char[8] name | int32 nVerts | nVerts × (f32 x,y,z,u,v) | int32 nFaces | nFaces × (u16 a,b,c)
```
Stored axes = Blender (x, z, −y). The `io_n2km` exporter writes every mesh named with `-` at index 1
(`DEF_` backups are ignored), needs triangles + a UV map, and duplicates verts at UV seams (0 for untouched topology).
- `python scripts/n2km_tools.py info model.n2km`
- `python scripts/n2km_tools.py compare original.N2KM edited.n2km` → exit code 0 + `SAFE to import` only if parts,
  vert/face counts, face lists and UVs are identical (positions may differ). Run before every 3DM import.

## .dds (textures) — `scripts/dds_tools.py`
A DDS file = 128-byte header ("DDS " + 124-byte DDS_HEADER) + pixel data. Check any file with
`python scripts/dds_tools.py info file.dds`.

| File (2K14) | Format | How to write it |
|---|---|---|
| `hair.dds` | 256² **A8R8G8B8**, uncompressed, no mips, pitch field 0 | **Python directly** (`dds_tools.write_argb`) |
| `face_color.dds` | 512² **DXT5** (block-compressed, with alpha) | NVIDIA DDS tools / Photoshop |
| `skin_colour.dds` | 512² **DXT1** (block-compressed) | NVIDIA DDS tools / Photoshop |

### Uncompressed A8R8G8B8 (why Python can write it)
- Pixel data = width × height × 4 bytes, **top row first**, each pixel in **B, G, R, A** order
  (size check: 128 + 256·256·4 = 262,272 bytes).
- Header offsets: height @12, width @16 (u32), pitch @20, mip count @28, pixel-format flags @80, FourCC @84,
  bit count @88, R/G/B/A masks @92 (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000).
- Write recipe: copy the **original file's 128-byte header** (exact flags/masks the game expects), patch
  width/height, keep pitch as the original has it (2K14 leaves it 0), append pixels as BGRA.
  `read_argb` → modify → `write_argb` round-trips byte-identical (tested on KQ `hair.dds`).
- Blender cannot load A8R8G8B8 DDS → `dds_tools.read_argb` + `to_numpy` / `to_blender_image`.
  Blender stores image rows bottom-up — flip when converting.

### Compressed DXT1/DXT5
- Stored as 4×4 pixel blocks (colour endpoints + indices); needs a real encoder for good quality → use NVIDIA tools
  or Photoshop, same format as the original file. Blender *can read* DXT files (`bpy.data.images.load`).
- What worked in game (KQ): face exported as **512² DXT5 with mipmaps (10 levels)** — the 2048² PNG was
  downsized to 512 for the DDS. Larger DDS sizes are **untested**; the original game files have no mips.
