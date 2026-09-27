# NBA 2K14 PC `.ROS` Roster File Format

Findings from direct binary analysis of 29 roster files in
`%APPDATA%\2K Sports\NBA 2K14\Saves` (2026-08-02). Every claim is tagged:

- **[VERIFIED]** — reproduced programmatically on multiple files
  (see `tools/ros_inspect.py`).
- **[HYPOTHESIS]** — consistent with observations but not yet proven.

## Container basics

- **[VERIFIED]** Every NBA 2K14 PC `.ROS` file is exactly **2,672,672 bytes
  (0x28C820)** — a fixed-size container. Free space inside is managed by the
  editor (hence RED MC's "Free Space Indicator").
- **[VERIFIED]** All multi-byte integers are **big-endian** (the format is
  shared with Xbox 360/PS3, both big-endian platforms).
- **[VERIFIED]** Table data is **not compressed and not encrypted** (byte
  entropy 0.5–6.9 bits/byte across the file; empty record space shows as
  low-entropy regions).

## Header

| Offset | Size | Value | Meaning |
|--------|------|-------|---------|
| 0x00 | 4 | varies | **[VERIFIED] CRC32 checksum** — standard zlib/IEEE polynomial over bytes `0x04..EOF`, stored big-endian. Matched on every file tested. |
| 0x04 | 4 | `50 15 51 AE` | **[VERIFIED]** Magic/format ID (constant across all files) |
| 0x08 | 4 | `00 00 00 05` | **[VERIFIED]** Format id: ROS=0x05, FXG=0x08, CMG=0x10, FDC=0x16 (Roster Lab `fdc`) |
| 0x0C | 4 | `00 28 C8 20` | **[VERIFIED]** Total file size (2,672,672) |
| 0x10 | 8 | zeros | Unknown/reserved |
| 0x18 | 4 | varies per file | **[VERIFIED]** End-of-data pointer (Roster Lab `eod`), close to the end of the string heap (it stops ~24 bytes short in some files). Basis of the Free Space Indicator. |
| 0x1C | 4 | `01 00 00 00` | Unknown |
| 0x20 | 4 | `00 00 00 01` | Record count of section 0x0101 (see the directory note below) |
| 0x24 | 12×46 | — | Table directory, 0x24–0x24B, ids 0101–012E (below) |
| 0x240 | 12 | `012E…`, `0C9545EB`, `012F0000` | Last directory entry (012E); its `value` word is `012F0000` (the heap's stamp) instead of a count |
| 0x24C | 4 | `00007D00` | 32000: string-heap arena A capacity in characters |
| 0x250 / 0x254 | 4+4 | varies | **[VERIFIED]** Next-free handles of heap arenas A (`012F`) and B (`0130`) |
| 0x26C | — | — | **[VERIFIED]** Bitstream starts here (bit 4960) with section 0x0102 |

> This header table was verified 2026-09-26 against Roster Lab by Q2K
> 1.7.0's `ros_core` (which validates every section start against the stamp +
> id stored in the records) and `FIBA 2017 SEABA.ROS`. See
> [09-roster-lab.md](09-roster-lab.md).

**Re-signing [VERIFIED]:** after any byte edit, recompute
`crc32(file[4:])` and write it big-endian at offset 0. `ros_inspect.py resign`
does this; RED MC and the game accept files fixed this way (RED MC-written
files round-trip the same checksum).

## Table directory (offset 0x24)

**[VERIFIED — Roster Lab + record stamps]** 46 consecutive 12-byte entries,
0x24–0x24B, one per section 0x0101..0x012E:

```
+0  u32  id     — 0x01xx0000, = 0x0101 + entry index (see the empty-section quirk)
+4  u32  hash   — struct-type hash of section `id`
+8  u32  value  — RECORD COUNT OF THE NEXT SECTION (id + 1)
```

The pairing is **off by one** and easy to misread:

- `hash` belongs to the `id` in the same entry.
- `value` is the record count of the *following* section. Section 0x0101's
  count (1) sits in the word just before the directory, at 0x20.

Proof:

- Counts: Roster Lab walks the bitstream using `value` of the entry at
  0x24+12k as the count of stamp 0x0102+k. It checks that the first record of
  each section carries `[stamp][id 0]` and the last carries `[stamp][count−1]`.
  Every section in a real roster passes.
- Hashes: with hash paired to its own `id`, each of the 28 distinct hashes
  covers exactly one record size. Paired with the count instead, 5 hashes span
  two sizes (e.g. `33D3CC02` would cover both 134-bit schedules and 1148-bit
  Staff).
- Roster Lab's own `KNOWN_HASH` table uses the wrong pairing. It only
  produces warnings, so the tool is unaffected.

`value` is an exact **record count**, not a capacity. Arenas (99–102) and
Staff (238–386) differ between files, which is what shifts the bit phase of
everything after them.

Empty-section quirk: the entries for the empty sections 0x0129 and 0x012A
carry id `0x012B`. Derive the stamp from the entry's position, not from the id
word.

Section map (2K14; names from Roster Lab `ros_core13.NAMES` + `TO_2K14`; bits
per record from `ros_core.SECTION_BITS`; counts from `FIBA 2017 SEABA.ROS`):

| Stamp | Section | Hash | Bits/rec | Count |
|------|---------|------|---------|-------|
| 0101 | (root, not in the bitstream) | 1CE26BF9 | — | 1 |
| 0102 | CustomName | 31BE80A1 | 64 | 5000 |
| 0103 | **Players** | F50B0369 | 3644 | **1665** |
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
| 012B | unnamed; RED MC `Struct735767AE.txt` (only `IsUnused`) | 735767AE | 1121 | 1885 |
| 012C | free list for 012B | 8A6C4520 | 64048 | 1 |
| 012D | Skills Boosts | 10F7F0BD | 449 | 2057 |
| 012E | free list | 0C9545EB | 64048 | 1 |
| 012F / 0130 | string heap, arenas A / B | — | — | — |

The hash → RED MC caption link stands: `735767AE` = `Struct735767AE.txt`, and
tables sharing a hash share a record layout (the five 3644-bit player-shaped
sections, the five schedules, the five Player_Ratings, the three name
tables, the two playbooks).

## Data area: one continuous bitstream

- **[VERIFIED]** Records are **bit-packed with no byte alignment**, MSB-first.
  The stream starts at bit 4960 (byte 0x26C).
- **[VERIFIED]** Sections are stored back to back in stamp order. Every record
  has a **fixed width** (table above) and begins with `[u16 stamp][u16 id]`.
  Section start = previous start + bits × count. No table is variable-width,
  names included.
- **[VERIFIED]** The bit phase of later structures differs between rosters
  because **record counts** differ (Arenas, Staff), not because of
  variable-length strings. Strings live only in the heap after the last
  section.
- **[VERIFIED]** References are 32 bits: `[u16 target stamp][u16 record
  index]`, and all zero means none. For example, player bit 192 = `[010A][team]`.

## Strings: the heap and name handles

- **[VERIFIED]** All strings are **null-terminated UTF-16BE** in one heap
  after section 012E, in two arenas (Roster Lab `ros_names`):

  ```
  heap byte     4 .. 64007   arena A, handles [012F]   heap_byte = 2*(v + 2)
  heap byte 64008 .. end     arena B, handles [0130]   heap_byte = 2*(v + 32004)
  ```

  Heap bytes are relative to the heap start (`heap_bit`, not byte-aligned).
  Next-free handles are at 0x250/0x254.
- **[VERIFIED]** Non-ASCII works (e.g. `Schröder` — `ö` = U+00F6).
- **[VERIFIED — corrects the earlier claim]** Players do **not** store indices
  into First_Names/Last_Names. `Last_Name` (bit 32) and `First_Name` (bit 64)
  are **heap handles**: a character offset, not a row number. In
  `FIBA 2017 SEABA.ROS` all 1665 player handles land exactly on a string
  start, and handle values reach 65526 while Last_Names has only 1882 rows.
- The name tables 0117/0118/0119 are the commentary name pool (`NameData`
  captions: name + audio ids). Their name column is itself a heap handle
  (e.g. First_Names row 5 → `[0130]:07B6` → "Aaron").
- Placeholder strings of `*` (1413 in the sample) are reserved heap slots,
  which explains the `***…` padding seen around CAP names (06).
- The handle arithmetic has a known quirk that the game itself triggers; see
  `fix_namehandles` in [09-roster-lab.md](09-roster-lab.md). When appending
  names, only use arena A. Arena B's handle space is nearly full.


## Other RED MC-relevant formats

- `.FDC` draft class and console `.ROS` variants share the same table/caption
  system (RED MC uses one caption set for all platforms). Console saves add
  wrappers: X360 STFS packages (must be rehashed/resigned), PS3 encrypted
  saves (decrypt with Bruteforce Save Data first).
- 2K13 rosters use the parallel caption set in `Text/NBA2K13/`.

## Methodology for further mapping

Section geometry is fully known (table above), so strides and bases never
need guessing: `record_bit = section_start + bits_per_rec × index`. Most
field layouts of Players, Teams, Staff, Stats, Jerseys, Awards, Records and
Trades are already placed by Roster Lab's correlation schemas
([09-roster-lab.md](09-roster-lab.md)). Use them as a cross-check; licence
terms rule out copying them. For anything unplaced or uncertain (`bmin`/`wmax`
set), the recovery procedure is (no disassembly needed):

1. Copy a roster; open the copy in RED MC.
2. Change **exactly one field on one row** (e.g. Player 0 `Height` 200→201).
   Save.
3. `python tools/ros_inspect.py bitdiff original.ros modified.ros`
   → the differing bit run (minus the CRC at bytes 0–3) is the field's
   absolute bit position and width.
4. Repeat for the same field on row 1 → the delta between the two bit
   positions is the **record stride in bits**; the table's base offset falls
   out of `pos(row0) - stride*0`.
5. Editing a name does not shift any section: names are appended to the
   heap after the last section and the record's 32-bit handle changes. Only
   adding or removing *records* moves later sections.
6. Enum widths: set a field to its max enum index (see `Text/Enums.txt`) to
   confirm the bit width.

Record this mapping per struct hash (not per tab) so it transfers across the
five schedule tables, etc.
