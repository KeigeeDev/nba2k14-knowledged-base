# Cyberface textures (`.dds`)

**Status:** [VERIFIED] for the byte layout of uncompressed A8R8G8B8 DDS files (checked on 2026-09-27 against Pillow's independent DDS reader and writer). [VERIFIED] for the in-game face texture result (tested in game by the repo owner on one cyberface). [DRAFT] for the format and size of each 2K14 file, which come from the owner's notes and haven't been checked on a file in this repo.
**Category:** file-format
**Last updated:** 2026-09-27

## Summary

A cyberface uses three DDS textures. The face and skin textures are block-compressed (DXT5 and DXT1), so they need a real encoder such as NVIDIA's tools or Photoshop. The hair texture is uncompressed 32-bit, which a short Python script can read and write directly. Blender can't open it.

## The files

| File | Format | Size | How to write it |
|---|---|---|---|
| `face_color.dds` | DXT5 (block-compressed, with alpha) | 512² | NVIDIA DDS tools or Photoshop, same format as the original |
| `skin_colour.dds` | DXT1 (block-compressed) | 512² | NVIDIA DDS tools or Photoshop |
| `hair.dds` | A8R8G8B8 (uncompressed), no mipmaps, pitch field 0 | 256² | Python directly: `dds_tools.write_argb` |

According to the notes, the original game files have no mipmaps.

### What worked in game (tested by the repo owner on KQ)

- The face texture was baked at 2048², downsized to 512² and saved as **DXT5 with mipmaps (10 levels)**. It worked in game even though the original has no mips. (512² down to 1² is 10 levels.)
- Sizes above the originals are **untested**, both for the face and for a 512² `hair.dds`.

## A8R8G8B8 DDS layout

A DDS file starts with the 4-byte magic `DDS `, then a 124-byte header, then the pixel data. Offsets below count from the start of the file.

| Offset | Field |
|---|---|
| 12 | Height (`u32`) |
| 16 | Width (`u32`) |
| 20 | Pitch (`u32`). 2K14's `hair.dds` leaves it 0; Pillow writes width × 4. |
| 28 | Mipmap count (`u32`) |
| 80 | Pixel-format flags (`0x4` = FourCC, i.e. compressed) |
| 84 | FourCC (`DXT1`, `DXT5`, ...) |
| 88 | Bits per pixel (32) |
| 92 | R, G, B, A masks: `0x00FF0000`, `0x0000FF00`, `0x000000FF`, `0xFF000000` |

- Pixel data is width × height × 4 bytes, **top row first**, with each pixel stored as **B, G, R, A**. A 256² hair texture is 128 + 256·256·4 = 262,272 bytes.
- **Recipe for writing one the game accepts:** copy the original file's 128-byte header, patch width and height, leave pitch as the original has it, and append the pixels as BGRA. `dds_tools.write_argb` does exactly this.
- Blender stores image rows bottom-up, so flip them when converting to or from a Blender image.

### How the layout was checked

- `dds_tools.write_argb` output opened in Pillow 12.3.0 gives exactly the intended RGBA pixels. A file Pillow wrote reads back correctly with `dds_tools.read_argb`.
- Read → write round-trips byte-identical on a synthetic 256² file. The owner's notes report the same on the real KQ `hair.dds`.

## Blender and DDS (owner's notes, Blender 5.2)

- Blender *can* load DXT1/DXT5 files (`bpy.data.images.load`).
- Blender *can't* load the A8R8G8B8 `hair.dds`. Use `dds_tools.read_argb` + `to_blender_image`.

## Sources

- [`sources/cyberface/guides/05_file_formats.md`](../../sources/cyberface/guides/05_file_formats.md) and [`sources/cyberface/scripts/dds_tools.py`](../../sources/cyberface/scripts/dds_tools.py) (owner's notes and script).
- Tested during review on 2026-09-27 with Pillow 12.3.0 (independent DDS implementation).
- In-game result: tested by the repo owner on the KQ cyberface, confirmed 2026-09-27.
- Per search excerpts, icecr's NLSC tutorial also saves the edited face texture as DXT5: https://forums.nba-live.com/viewtopic.php?f=154&t=113460

## Open questions

- Does the 3DM Tool or the game accept larger textures (1024² face, 512² hair)?
- Does the headband (`0-0`) texture live in its own file, and what format is it?
- Does the game use the mipmaps when present, or ignore them?
