# `.ROS` roster files (container)

**Status:** [VERIFIED] for the header, CRC, table directory, section map and string heap. The owner reproduced these on 29 real PC rosters, Roster Lab's engine independently checks every section start against the stamps stored in the file, and the numbers were checked for internal consistency during review. [DRAFT] for the fields marked "unknown".
**Category:** file-format
**Last updated:** 2026-09-27

## Summary

An NBA 2K14 PC roster save (`.ROS`) is a **fixed-size, 2,672,672-byte, big-endian** container. After a short header and a table directory, all tables are packed into **one continuous bitstream** of fixed-width records, followed by a heap of UTF-16BE strings. A **CRC32 at offset 0** covers the rest of the file. Recompute it after any edit and both the game and RED MC accept the file.

PC saves live in `%APPDATA%\2K Sports\NBA 2K14\Saves`. The same data model, little-endian and zlib-compressed, is the game's built-in default roster ([`roster.iff`](roster-iff.md)). For player fields, see the [player record](ros-player-record.md).

## Header

All integers are big-endian (the format is shared with Xbox 360 and PS3).

| Offset | Size | Value | Meaning |
|---|---|---|---|
| 0x00 | 4 | varies | **CRC32** (zlib/IEEE polynomial) of bytes `0x04`..EOF |
| 0x04 | 4 | `50 15 51 AE` | Magic |
| 0x08 | 4 | `00 00 00 05` | Format id: ROS 0x05, FXG 0x08, CMG 0x10, FDC 0x16 |
| 0x0C | 4 | `00 28 C8 20` | File size (2,672,672) |
| 0x10 | 8 | zeros | Unknown / reserved |
| 0x18 | 4 | varies | End-of-data pointer. It sits close to the end of the string heap and is the basis of RED MC's Free Space Indicator. |
| 0x1C | 4 | `01 00 00 00` | Unknown |
| 0x20 | 4 | `00 00 00 01` | Record count of section 0x0101 |
| 0x24–0x24B | 46 × 12 | | Table directory (below) |
| 0x24C | 4 | `00007D00` | 32,000: capacity of heap arena A, in characters |
| 0x250 / 0x254 | 4 + 4 | varies | Next-free handles of heap arenas A (`012F`) and B (`0130`) |
| 0x26C | | | Bitstream starts here (bit 4960) |

**Re-signing:** after any edit, write `zlib.crc32(file[4:])` big-endian at offset 0. According to the owner's notes, RED MC and the game accept files fixed this way, and RED MC-written files have the same checksum. `ros_inspect.py resign` does it ([roster scripts](../tools/roster-scripts.md)).

## Table directory

There are 46 consecutive 12-byte entries, one per section 0x0101–0x012E:

```
+0  u32  id     0x01xx0000
+4  u32  hash   struct-type hash of THIS entry's section
+8  u32  value  record count of the NEXT section (id + 1)
```

- **The pairing is off by one:** `hash` belongs to the entry's own section, but `value` is the count of the following section. Section 0x0101's count is the word at 0x20.
- **Take the stamp from the entry's position, not the id word:** the entries for the empty sections 0x0129 and 0x012A carry id `0x012B`.
- Tables that share a hash share a record layout (for example the five player-shaped sections and the five schedules). The hashes match RED MC's caption file names, e.g. `Struct735767AE.txt`.
- Roster Lab's own `KNOWN_HASH` table uses the wrong pairing. That only produces warnings.

## Section map

Record sizes are in bits. Counts are from one sample roster; the ones marked "varies" differ between files.

| Stamp | Section | Hash | Bits/rec | Count |
|---|---|---|---|---|
| 0101 | root (not in the bitstream) | 1CE26BF9 | — | 1 |
| 0102 | CustomName | 31BE80A1 | 64 | 5000 |
| 0103 | **Players** | F50B0369 | 3644 | 1665 |
| 0104–0107 | Rookie_Templates, CAP_Templates, MP_Templates, My_Legend | F50B0369 | 3644 | 124, 31, 31, 1 |
| 0108 | FreeAgentsList | 08CC304D | 32048 | 1 |
| 0109 | Arenas | 50F71DDB | 480 | 99 (varies) |
| 010A | **Teams** | 72F85B2C | 5764 | 105 |
| 010B | Colleges | B6988C73 | 171 | 544 |
| 010C–0110 | ScheduleBase_82/58/29/14/PreSeason | 33D3CC02 | 134 | 1232, 872, 437, 212, 209 |
| 0111 | Staff | 030FD8D0 | 1148 | 742 (varies) |
| 0112 | Old_Coach_Stats | 4D8F5711 | 98 | 238 |
| 0113–0114 | Playbooks_actual / _default | BBAE91A6 | 1721 | 69, 69 |
| 0115 | Player_Stats | 0A338252 | 341 | 7394 |
| 0116 | Team_Stats | C8126D3B | 368 | 248 |
| 0117–0119 | First_Names, Last_Names, City_Names | B394B954 | 119 | 1547, 1882, 33 |
| 011A | Jerseys | 99EBEE25 | 548 | 482 |
| 011B | Headshapes | ECFC0782 | 816 | 2160 |
| 011C | Overriding_Rotations | 017D966B | 448 | 8 |
| 011D–0121 | Player_Ratings0–4 | 331A8B50 | 208 | 5 each |
| 0122 | Records | 04471BE3 | 159 | 1342 |
| 0123 | Awards | 6A9B729B | 320 | 4318 |
| 0124 | Draft_Projection | 0A7FFCF1 | 96 | 60 |
| 0125 | Trades | D90FB077 | 808 | 77 |
| 0126 | Matchups | 48882A21 | 112 | 870 |
| 0127 | Hall_Of_Fame | 40C9BEA2 | 333 | 276 |
| 0128 | OnLine_TeamUp | DE8A423D | 96 | 30 |
| 0129, 012A | (empty) | 86C46F54, 5D283880 | — | 0 |
| 012B | unnamed (RED MC `Struct735767AE.txt`) | 735767AE | 1121 | 1885 |
| 012C | free list for 012B | 8A6C4520 | 64048 | 1 |
| 012D | Skills Boosts | 10F7F0BD | 449 | 2057 |
| 012E | free list | 0C9545EB | 64048 | 1 |
| 012F / 0130 | string heap, arenas A / B | — | — | — |

Section names come from Roster Lab. Bits per record come from Roster Lab's `SECTION_BITS`.

## The bitstream

- Records are **bit-packed, MSB-first, with no byte alignment**, starting at bit 4960.
- Sections are stored back to back in stamp order: `start(next) = start + bits × count`. **Every record has a fixed width** and begins with `[u16 stamp][u16 index]`.
- The bit position of later sections differs between rosters only because record counts differ (Arenas, Staff). Strings are never inline.
- **References** are 32 bits, `[u16 target stamp][u16 record index]`, and all zeros means "none". For example, player bit 192 holds `[010A][team]`.
- Editing a name doesn't move anything. Only adding or removing records shifts later sections.

**Consistency check (review, 2026-09-27):** summing bits × count over the table above gives Players at bit 324,960, Teams at bit 7,153,216 and the heap at bit 19,441,198. Those are exactly the positions Roster Lab reported when it walked a real file.

## String heap

After section 012E comes a heap of **null-terminated UTF-16BE** strings in two arenas. Records point into it with 32-bit handles `[u16 stamp][u16 v]`:

```
heap byte     4 .. 64007   arena A   handles [012F]   heap_byte = 2 * (v + 2)
heap byte 64008 .. end     arena B   handles [0130]   heap_byte = 2 * (v + 32004)
```

- Heap bytes count from the heap start, which isn't byte-aligned in the file.
- **Player names are heap handles, not row numbers** in First_Names/Last_Names. Those tables are the commentary name pool, and their own name column is also a handle.
- Placeholder strings of `*` are reserved slots (1,413 in the sample). Non-ASCII works (`Schröder`).
- **When adding names, append to arena A** and bump the watermark at 0x250. Arena B's u16 handle space is almost full (10 bytes of headroom in one stock roster).
- A known game quirk folds an out-of-arena `[012F]` handle into `[0130]:(v − 32000)`, which lands 2 characters into the string ("Duncan" → "ncan"). Roster Lab's `fix_namehandles` repairs it.

## Rules any writer must respect

These come from Roster Lab's save checks, as documented in the owner's notes:

- **Never change the file size**, and re-sign the CRC.
- **No all-zero player face block** (record bits 388–415). The game crashes on it.
- **Name handles must land on a string start.**
- **A team's 20 roster slots** (`Ros_R0`–`R19` at bit 32 of each Teams record) must be packed with no gaps, and `PlNum` (Teams bit 1035, 5 bits) must equal the number of filled slots.
- **Save names:** letters, digits and spaces only, at most 25 characters including the extension. According to Roster Lab, the game deletes other names.
- **Never renumber records.** Other files (`.FXG`) refer to record ids.

## Related formats

- `.FXG` (association) and `.CMG` (career) embed the same image at offsets 8 and 0x216BA8. The embedded image's CRC slot is zeroed and not checked.
- `.FDC` draft classes are 77,472 bytes: a big-endian header, then 80 × 968-byte **little-endian, LSB-first** records.
- NBA 2K13 `.ROS` files are 2,432,032 bytes with 42 sections and 3,821-bit player records.
- Console saves add wrappers: Xbox 360 files must be rehashed and resigned, and PS3 saves must be decrypted first.

## Sources

- [`sources/roster-editing/ai-docs/02-ros-format.md`](../../sources/roster-editing/ai-docs/02-ros-format.md) and [`09-roster-lab.md`](../../sources/roster-editing/ai-docs/09-roster-lab.md) (owner's notes, 29 real rosters plus Roster Lab 1.7.0's engine run read-only on `FIBA 2017 SEABA.ROS`).
- Review checks (2026-09-27): section-start arithmetic above. A synthetic file built to this layout parses correctly with `ros_inspect.py` (header, CRC, re-sign).

## Open questions

- What are the fields at 0x10 and 0x1C?
- What's in sections 012B, 012C and 012E, and in the `.FXG`/`.CMG` tails?
