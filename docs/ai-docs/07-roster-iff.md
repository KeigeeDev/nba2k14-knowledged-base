# `roster.iff` — the Game's Default Roster (IFF Container)

Analyzed sample: `roster.iff` (880,916 bytes, dated 2013-08-29 — shipped with
NBA 2K14 PC). This is the game's **built-in default roster**; `.ROS` saves
are user copies of the same data model. All findings **[VERIFIED]** on this
sample.

## IFF outer container

| Offset | Content |
|--------|---------|
| 0x00 | Magic `94 EF 3B FF` |
| 0x04.. | Header fields, **little-endian** (PC-native): counts, sizes, subfile table info |
| 0x54 | Subfile block: `"ZLIB"` marker, then **big-endian** u32 uncompressed size (0x279C40 = 2,595,904), u32 compressed size (0x093A46 = 604,742), u32 flags, then a raw zlib (`78 DA`) stream |
| tail (~0xD7050) | "roster text" subfile: UTF-16 localization strings (`<english>…<context>DO NOT LOCALIZE</context><filename>roster text</filename>`), plus subfile type/name tags `DRAM`, `ROST`, `roster` |

Extraction: find `ZLIB`, read the two big-endian sizes, `zlib.decompress`
from the following `78 DA`. One ZLIB block in this file.

## The payload: same roster container, little-endian

The 2,595,904-byte decompressed payload is the **same table container as
.ROS but in little-endian, without the save wrapper** (no CRC, no magic
`501551AE`, no file-size field):

```
0x00  u32 LE  = 1                      (version/flag)
0x04  directory entries, 12 bytes each, little-endian:
      u32 table-id   (different numbering than .ROS: 0x235, 0x239, 0x504D…)
      u32 struct-type hash  — SAME hashes as .ROS (1CE26BF9 root 0101,
                              31BE80A1 CustomName, F50B0369 Players +
                              the four player templates, …)
      u32 value      — SAME values (5000 = CustomName count, 1665 = Players
                              count, 124/31/31/1 = templates, …)
```

> Labels corrected 2026-09-26 from the .ROS verification in 02: in a
> directory entry the hash belongs to the entry's own section, but `value` is
> the record count of the *next* section. The earlier "Players 5000 / Teams
> 1665" reading was off by one. `roster.iff` itself was not re-inspected;
> this assumes the same layout, as the identical triples suggest.

After the directory: the same bit-packed data area. Name strings are still
**UTF-16BE, null-terminated**, in the string heap after the last section
(see 02 § Strings) (byte-aligned in this
sample: "James" @0x25A99F, "Antetokounmpo" @0x25AC91, "Bryant" @0x25B933 —
2013 default roster content).

## Relationship .ROS ↔ roster.iff

- Struct hashes and table capacities are identical → **one data model, two
  wrappers**: PC game resource (IFF+zlib, LE) vs. save file (raw, BE,
  CRC-signed). The BE save format is shared with Xbox 360/PS3.
- RED MC edits both (its IFF support covers 2K12–2K15), and its `Parsers.dll`
  handles the container differences.
- Practical use: the payload is a full valid roster — a reference "vanilla"
  dataset to compare against modded .ROS files, and the target for
  distributing roster mods as game files.
