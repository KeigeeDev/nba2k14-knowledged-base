# `roster.iff` (the game's default roster)

**Status:** [VERIFIED] for the IFF wrapper and zlib payload, which the owner extracted from the shipped file. [DRAFT] for the payload's directory labels, which are assumed to follow the `.ROS` layout but weren't re-inspected after that layout was corrected.
**Category:** file-format
**Last updated:** 2026-09-27

## Summary

`roster.iff` ships with NBA 2K14 PC (880,916 bytes, dated 2013-08-29) and holds the built-in default roster. Inside an IFF wrapper is a zlib stream that decompresses to the **same table container as a [`.ROS`](ros-roster.md) save, but little-endian and without the save header**. It's a clean "vanilla" roster to compare modded files against.

## IFF wrapper

| Offset | Content |
|---|---|
| 0x00 | Magic `94 EF 3B FF` |
| 0x04.. | Header fields, **little-endian**: counts, sizes, subfile table |
| 0x54 | `"ZLIB"` marker, then **big-endian** u32 uncompressed size (2,595,904), u32 compressed size (604,742), u32 flags, then a raw zlib stream (`78 DA`) |
| tail (~0xD7050) | A "roster text" subfile of UTF-16 localization strings, plus the tags `DRAM`, `ROST`, `roster` |

**Extraction:** find `ZLIB`, read the two big-endian sizes, and `zlib.decompress` from the `78 DA` that follows. This file has one ZLIB block.

## Payload

- `u32 LE = 1`, then 12-byte **little-endian** directory entries: a table id (numbered differently from `.ROS`, e.g. 0x235), then the **same struct hashes and the same count values** as a `.ROS` directory (5000, 1665, 124/31/31/1, ...). Presumably the same off-by-one pairing applies (hash = own section, value = next section's count), but that hasn't been checked on this file.
- Then the same bit-packed data area. Names are still UTF-16BE, null-terminated, in the heap after the last section. In this sample they happen to be byte-aligned ("James" at 0x25A99F).
- There's no CRC, no `50 15 51 AE` magic and no file-size field.

RED MC edits both wrappers; its `Parsers.dll` handles the differences.

## Sources

- [`sources/roster-editing/ai-docs/07-roster-iff.md`](../../sources/roster-editing/ai-docs/07-roster-iff.md) (owner's analysis of the shipped file).

## Open questions

- Re-check the directory pairing on the decompressed payload.
- How does the IFF table id numbering map to `.ROS` stamps?
- Does the game accept a re-compressed, modified `roster.iff`?
