# `.n2km` model files

**Status:** [DRAFT]. The layout comes from one source: the owner's `n2km_tools.py` parser, which the notes say is used on real 2K14 cyberface files. It hasn't been checked against a real file in this repo yet.
**Category:** file-format
**Last updated:** 2026-09-27

## Summary

`.n2km` is the model format the 3DM Tool exports from a cyberface `.iff` and imports back. The file is a short header followed by a list of named parts. Each part holds its vertices (position + UV) and triangles. Triangles refer to vertices by index, which is why topology must not change between export and re-import.

## Layout

All values are little-endian.

| Offset | Type | Field |
|---|---|---|
| 0 | `char[4]` | Magic `2KM\0` |
| 4 | `int32` | Part count |
| 8 | `int32` | `20` in the owner's files. Meaning unknown. It matches the vertex record size (5 × 4 bytes), but that's a guess. |
| 12 | parts | One record per part, back to back |

Each part record:

| Type | Field |
|---|---|
| `char[8]` | Part name, null-padded (e.g. `0-1`) |
| `int32` | Vertex count `V` |
| `V` × (`f32` x, y, z, u, v) | Vertices, 20 bytes each |
| `int32` | Triangle count `F` |
| `F` × (`u16` a, b, c) | Triangles as vertex indices, 6 bytes each |

- File size = 12 + Σ over parts of (8 + 4 + 20·V + 4 + 6·F).
- Indices are `u16`, so a part can have at most 65,536 vertices.
- **Axes:** the file stores Blender's (x, z, −y). The file's y is Blender's up (Z), and the face, which points to −Y in Blender, points to +z in the file.
- According to the notes, the io_n2km exporter splits vertices at UV seams. For topology that came from the game unchanged, no extra vertices get added.

For what each part is, see [cyberface parts](cyberface-parts.md).

## Tools that read or write it

- [3DM Tool](../tools/3dm-tool.md): exports from and imports into `.iff`.
- [io_n2km](../tools/io-n2km.md): Blender import/export.
- [`n2km_tools.py`](../tools/cyberface-scripts.md): prints part counts (`info`) and checks an edited file against the original (`compare`).

## Sources

- [`sources/cyberface/guides/05_file_formats.md`](../../sources/cyberface/guides/05_file_formats.md) and [`sources/cyberface/scripts/n2km_tools.py`](../../sources/cyberface/scripts/n2km_tools.py) (owner's notes and parser).
- Checked during review (2026-09-27): synthetic files written to this layout parse as expected with `n2km_tools.py`. That only shows the parser matches the documented layout, not that the layout matches the game.

## Open questions

- What does the `int32` at offset 8 mean?
- Is the v coordinate flipped compared to Blender's UV convention?
- Does the 3DM Tool care about part order, or only part names and counts?
- To upgrade this entry: add the output of `n2km_tools.py info` for an original game `.N2KM` (or a sample file, if redistribution is OK).
