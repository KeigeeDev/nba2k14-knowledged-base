# Roster Lab by Q2K v1.7.0 — reverse-engineering notes

Source: the installed copy at `C:\Editing Tools\Roster Lab by Q2K`, inspected
2026-09-26. Nothing was executed except the pure-data modules (`ros_core`,
`document`, `backups`), which were imported to read their constants.
Re-run the inspection with `ai-docs/tools/roster_lab_inspect.py`.

Licence note: Roster Lab is closed, "all rights reserved" freeware (see its
`LICENSE.txt`). The notes below describe how it works. Its schema JSON files
are useful as a **cross-check** for our own differential mapping, but do not
copy them into our tools or ship them.

## 1. Tech stack

| Layer | What |
|---|---|
| Language | **Python 3.14** (bytecode magic `2b0e0d0a`) |
| GUI | **PySide6 / Qt 6** (Widgets, Svg, Multimedia), Fusion style + a big dark QSS |
| Packaging | **PyInstaller onedir**. The exe (2.4 MB) holds the bootloader, a PYZ of 130 stdlib modules only, and one entry script `Roster Lab by Q2K.py` |
| App code | ~95 modules shipped as **loose `.pyc` files** in `_internal\` (and duplicated in `_internal\modules\`), *not* inside the PYZ. Docstrings are intact, so the code is well documented |
| Data | JSON: 11 `*_schema.json` bit maps, `data\layouts.json` / `enums.json` / `tips.json` / `recordings.json`, `overall_model.json`, `slider_names.json` |
| Other deps | Pillow, zstandard, FFmpeg DLLs (Qt Multimedia), Windows WMA DMOs through `ctypes` (retired audio tools only), optional external `ffmpeg.exe` (boot movie only) |
| Network | **None.** No `urllib`/socket/QtNetwork use in app code |

Heritage: the engine was written as **"Sigil 2K14"** (internal name; project
files are `.sigil`, the spec is `packaging/sigil.spec`, and the source tree had
`tools/` and `ui/` folders). It was rebranded "2K14 Lab by Q2K" and then
"Roster Lab by Q2K" **without recompiling**: the rebrand is done by runtime
monkey-patching.

## 2. Architecture — three layers

```
Roster Lab by Q2K.exe  (PyInstaller bootloader)
 └─ entry script "Roster Lab by Q2K.py"      <- LAUNCHER / SKIN (frozen in exe)
     • sys.path += _internal, add_dll_directory(PySide6, shiboken6)
     • globally monkey-patches Qt: QTableView.setModel (header "rec"->"id"),
       QTableView/QTableWidget.__init__, QMainWindow.showEvent/setWindowTitle
       ("Sigil" -> brand), setStyleSheet; applies a black QSS + SVG icon set
     • imports `app`, then calls q2k_lab.install_app_patches(app)
         │
         ▼
 _internal\version.py   (plain .py; wins over version.pyc on import)
     • imports q2k_seal and q2k_lab  <- PATCH LAYER (plain .py, readable)
         q2k_seal.py  wraps make_trade.apply_plan -> compacts roster slots +
                      re-syncs PlNum after every trade (fixes a crash bug)
         q2k_lab.py   prunes app.MENUS / MainWindow.TOOLBAR (removes 6 tools),
                      restyles + renames the trade dialog "Perform Trade",
                      adds "Trade player..." to the Players right-click menu,
                      adds Help > Quick Guide (q2k_guide.py)
         sitecustomize.py  dead code (never imported in an onedir build)
         │
         ▼
 _internal\*.pyc   <- ENGINE (the original "Sigil 2K14", compiled)
     UI:    ui -> app (MainWindow, MENUS, TOOLBAR) -> views -> one tab module
            per table (teams, staff, arenas, jerseys, records, awards, hof,
            picks, playbooks, schedule, seasons, shoes, templates, namepool,
            commentary, settings, career, rotation) + widgets/theme/icons/msg
    Model: document  (Document / RosterDocument / ClassDocument: undo, dirty
           tracking, save gates, "problems" audits)
    Data:  ros_core (bit I/O, section walk, CRC) · ros_names (string heap)
           · ros_<table> (one schema-driven accessor per section)
    Ops:   make_trade · fix_rotations · player_card · load_draft_class
           · fix_namehandles · port_2k13 · roster_export · overall_model
    Safety: atomicwrite · backups · sigilfile
```

The six "removed" tools (Browse Artwork, Repack Artwork, Browse Sounds,
Soundtrack, Mod Manager, Scorebug Tweaker) are **only hidden**. Their modules
(`browse`, `repack`, `audio*`, `soundtrack`, `mods`, `modvault`, `deploy`,
`iff_*`, `cdf_archive`, `mov_movie`, `wma_codec`, …, about 40% of the code) still
ship and `app` still imports them.

## 3. Engine core: how it reads a roster

`ros_core.Roster(path)` loads the whole file into a `bytearray` and walks the
section table in O(sections):

- **Container → image base** (`IMAGE_BASE`): `.ROS` 0 · `.FXG` 8 ·
  `.CMG` `0x216BA8` (image ends `0x4A33C8`). Every public bit position is
  image-relative. One code path serves all three file types.
- **Section table**: stamps `0102..012E`, each `(stamp, schema_hash, count)`.
  Record bit-length per stamp is hard-coded in `SECTION_BITS` (e.g. `03`
  Players 3644, `0A` Teams 5764, `11` Staff 1148, `2C`/`2E` 64048). Section
  starts are cumulative, and **each start is verified** against the stamp +
  record id stored in the stream (`[u16 0x01TT][u16 id]`), so a wrong
  assumption fails loudly. `KNOWN_HASH` pins an expected schema hash per
  stamp, but it is **off by one**. Roster Lab reads each entry's hash together
  with that entry's count, and they belong to adjacent sections (02 § Table
  directory). This only affects its warnings, not reads or writes. It also
  explains its docstring's claim that 0103 and 0104–0107 have "different
  schemas": all five actually share `F50B0369`.
- **Bit I/O**: `getbits`/`setbits(buf, bitpos, n)`, big-endian, unaligned.
  `Roster.get(stamp, index, bitoff, nbits)` = `rec_bit(stamp,index)+bitoff`.
- **Save**: `zlib.crc32(d[4:])` big-endian into bytes 0–3, size never
  changes. Only the outer header is re-signed; the image embedded in a `.CMG`/
  `.FXG` has a zeroed CRC slot that the engine does not check.

### String heap (`ros_names`), which corrects our 02/03 docs

Section `012F` is not records. It is a flat heap of null-terminated
**UTF-16BE** strings with two arenas:

```
heap byte     4 .. 64007   arena A   handles [012F]   BASE = 2
heap byte 64008 .. end     arena B   handles [0130]   BASE = 32004
heap_byte = 2 * (v + BASE[stamp])        handle = [u16 stamp][u16 v]
```

Name fields in records are **character-offset handles into this heap, not
table indices**. Next-free watermarks are the u32s at image `0x250`/`0x254`.
New names are appended to arena A (almost empty in stock rosters), which needs
no relayout. Never append to arena B: V70 has 10 bytes of headroom left. A
known game quirk folds an out-of-arena `[012F]` handle into `[0130]:(v-32000)`,
which lands 2 characters into the string ("Duncan" → "ncan").
`fix_namehandles` repairs this.

### Schemas: how the field map was built

Each `ros_<table>_schema.json` was generated by a (not shipped) `correlate.py`
that **bit-correlates a roster against RED MC's own CSV export** of the same
table. That is our planned differential method, run at scale. Each field is
`{bit, w, enc}`. Where the correlation could only bound a field, it adds
`bmin`/`wmax`/`wmin` uncertainty bounds.

| Schema | Stamp | Rec bits | Fields | Uncertain |
|---|---|---|---|---|
| player | 0103 (also 0104–0107) | 3644 | 343 | 162 |
| team | 010A | 5764 | 130 + 6 handles | 117 |
| staff | 0111 | 1148 | 47 + 2 handles | 28 |
| stats / team_stats | 0115 / 0116 | 341 / 368 | 31 / 23 | 16 / 23 |
| jerseys / awards / records / trades | 011A / 0123 / 0122 / 0125 | | 35 / 8 / 7 / 27 | |
| headshapes | 011B | 816 | 51 (`bytepair`) | 0 |
| fdc | .FDC, 968-byte LE records | | 240 | 0 |

Encodings: `int` (raw), `uintn` (all-ones = −1), `rating` (**raw = 3·shown −
75**, 25..99 in 8 bits, which matches our 06 doc), `f32be`, `masked` (low half
of a 32-bit ref, −1 = absent), `hexint`, `handle`, `bytepair` (byte − byte).
There is no two's-complement anywhere. Hand-proven overrides live in
`ros_core.PLAYER_FIELDS` and are useful as ground truth for our
`06-player-record-map.md`:

```
stamp 0/16  id 16/16  name_last 32/32  name_first 64/32  height_cm 128/32(f32)
weight_lb 160/32(f32)  team_ref 192/32  IsRegular 295  IsUnused 296  IsGener 297
IsDrafted 298  IsDraftee 299  face_block 388/28 (presence 388..391, group
392..402, HS_ID 403..415)  YearsPro 960/5  ASA_ID 2425/16  ID2 2631/16
refs: 192 team[010A] · 320 college[010B] · 352 drafted-by[010A] · 2377 skills-boost[012D]
```

### The mapping pipeline, end to end (traced from the bytecode)

Verified by running Roster Lab's own data layer read-only on a scratch copy
of `FIBA 2017 SEABA.ROS`.

1. **Container → image.** `Roster.__init__` reads the whole file into a
   `bytearray` and picks `base` from the extension (`IMAGE_BASE`).
   `filesize` = BE u32 at file byte 12. `eod` = BE u32 at `base+0x18`.
2. **Section table.** `_parse_table` reads 12-byte entries from image `0x24`
   up to `TABLE_END` = `0x240` (45 entries). The stamp is *implied by
   position* (0x0102, 0x0103, …). Per entry, `[4:8]` = schema hash (hex) and
   `[8:12]` = record count (BE). Heap watermarks = BE u32 at `0x250`/`0x254`.
3. **Section layout.** `_layout` starts at bit `(0x240+44)*8` = **4960**
   (byte 0x26C) and, for each section with count > 0:
   - takes `L = SECTION_BITS[stamp & 0xFF]` (it raises if the stamp is unknown),
   - warns if the hash is not in `KNOWN_HASH`,
   - **checks record 0**: 16 bits at `pos` = stamp, next 16 = id 0,
   - **checks the last record**: stamp matches and id = count−1,
   - stores `secs[stamp] = (pos, L, count)` and advances `pos += L*count`.

   After the last section, `pos` is `heap_bit`. Sample file: 0102 at bit 4960
   (5000×64), 0103 at bit 324960, 010A at 7153216, heap at 19441198.
4. **Record address.** `rec_bit(stamp, i) = start + L*i`, bounds-checked.
   Each record begins with its own `[u16 stamp][u16 id]`.
5. **Raw bits.** `getbits(buf, bitpos, n)` slices the covering bytes
   `bitpos>>3 .. ceil`, reads them as one big-endian int, shifts right by
   `nb*8 - bitpos%8 - n` and masks `n` bits. `setbits` is the inverse and
   raises if the value does not fit. `Roster.get(stamp, i, off, n)` =
   `getbits(data, base*8 + rec_bit + off, n)`.
6. **Field → raw.** `PlayerTable` loads `ros_player_schema.json`, then
   replaces entries with the hand-proven `BIT_OVERRIDES` (ID, ID2, ASA_ID,
   IsDraftee, DraftYear as `year2`, …) and adds `HEXINT_FIELDS`. `get(rec,
   name)` reads **only `bit` and `w`**. `bmin`/`wmax` are uncertainty
   metadata, used only in the "does not fit" error message.
7. **Raw → shown value** (decode in `get`, exact inverse in `set`):
   `rating` (raw+75)/3 · `uintn` all-ones→−1 · `masked` raw==sentinel→−1 ·
   `f32be` `struct '>f'` · `hexint` zero-padded hex string · `year2`
   47..99→19xx, else 20xx · `int` raw − `add`.
   Special routes are taken *before* the schema:
   - `REF_OF` names (TeamID1/2, CollegeID, DraftedBy, SklBst) go to
     `get_ref`: 32 bits at `REFS[which]`, 0 → −1, and the high 16 must equal
     the target stamp (0x010A/0x010B/0x012D) or it raises. It returns the low 16.
   - `HS_ID` → −1 if the presence nibble (388/4) is 0, else 403/13.
   - `SgndTYWith` → −1 unless the marker at 2288/16 is set.
   - Name fields go through `ros_names.Heap` (handle → heap byte → UTF-16BE string).
8. **UI key → table.** `layouts.json` holds bare RED MC column names per
   layout (player 355, team 154, staff 48, …). Views prefix them (`team:Name`,
   `pool:17:…`, `sched:0C:…`). `RosterDocument.get(key, field)` is one
   `is_*_field` dispatch chain: team → pick → stat → award → record → coach →
   staff → HoF → pool → playbook → schedule → template → jersey → arena →
   career → names → player refs → player schema. `field_info` returns
   `{enc, editable, locked, reason, bit, w, lo, hi, ref}` for the widget.
   `enums.enum_for(field, table)` consults `TABLE_MAP[table]` first, then
   `MAP`, and returns one of the 129 lists in `enums.json`. An out-of-list
   value shows as `raw N (out of range)` and is written back unchanged.
9. **Write-back.** Edits change the in-memory buffer. `save()` checks the size
   is unchanged, sets `data[0:4]` = `crc32(data[4:])` big-endian, and writes
   through `atomicwrite`.

Sample decode, rec 0 of the sample file:

```
Last_Name handle 0130:0000 -> heap byte 2*(0+32004) = 64008 -> 'Carter-Williams'
SShtCls  bit 2844 w8 rating  raw 135 -> 70
Height   bit 128 f32be       -> 198.12 cm
DraftYear bit 1489 year2     raw 13 -> 2013
face (presence, group, HS_ID) = (1, 216, 1223)
```

## 4. Domain logic and the rules it enforces

Every mutating operation is split into **`plan_*()`** (read-only, may refuse,
feeds the preview) and **`apply_*()`** (writes, then re-audits). A loop that
failed halfway would corrupt a fixed-size file.

- **Save gates** (`Document.check_target`): basename ≤ **25 chars** including
  extension, `\A[A-Za-z0-9 ]+\Z` (the game deletes other names), the extension
  must match the source, the tool warns if the file changed on disk since it
  was opened, and it asks before saving with zero-face records, bad name handles or
  duplicated players.
- **Zero face block = crash**. An all-zero face block (bits 388–415) makes
  the featured-player serializer dereference null. `heal_face` writes the
  HS_ID=0 template (`0x11b0` at bit 388: presence 1, group 216). This is
  applied only to 0103; templates 0104–0107 are *meant* to be zero.
- **Team membership is the 20-slot `Ros_R0..R19` array at bit 32 of 010A**,
  not the player's `TeamID1` (these disagree for 372 players in a pristine
  association). `PlNum` (bit 1035, 5 bits) must equal the number of filled
  slots with no gaps. `q2k_seal` fixes gaps and counts after every trade
  (a crash bug in pre-1.6 builds).
- **Trades** (`make_trade`), reproducing what an in-game trade writes: the
  team ref at bit 192, `SgndTYWith` (bit 2308/5) = old team, marker `0x8500`
  at 2288..2303, bit 1383 = 1. The arrival takes the departing player's roster
  slot and minutes, and the 35 situational lineup slots are substituted. On `.FXG` only, it
  also writes a row in 0125 plus a block in the transaction log (250 × 3176-bit
  blocks from absolute bit 39205076) and moves draft-pick ownership (120 ×
  24-bit entries at `0x492545`). Limits: 20 per roster, and with logging 3 teams
  / 4 assets (without logging, 6 / 10).
- **Rotation tidy-up** (`fix_rotations`) is the editor's *own* rule, not
  the game's: it sorts by estimated Overall with the first five by position, and
  seven lineups each ranked by one rating. Ties go to the lower record number.
- **Overall estimate** (`overall_model`): a per-position least-squares linear
  fit of the 42 ratings, trained on 3329 career players. Claimed 91% exact
  and 99.6% within 1. Base rosters store `Overall_I = 1`; only careers hold
  real values.
- **Player cards** (`player_card`): JSON with values on RED MC's display
  scale and references resolved **by name** (college lists, skills-boost
  tables and ASA_IDs differ between files). ID/ID2/ASA_ID/DraftYear are not copied.
- **Draft classes** (`fdc`, `load_draft_class`): `.FDC` = 77,472 B, a BE
  header (CRC, hash `f50b0369`, format id 0x16), then 80 × 968-byte
  **little-endian, LSB-first** records. Import overwrites the career's
  `IsDraftee` slots in pick order. The face block is deliberately *not*
  copied.
- **2K13 → 2K14 port** (`ros_core13`, `port_2k13`): a 2K13 `.ROS` (2,432,032 B)
  has 42 sections. From Jerseys onward its stamps are one below the 2K14
  stamps, and player records are 3821 bits. Port projects are saved as
  `.sigil` zips (a manifest plus sha256 per part).
- **Settings** (`stg_settings`): `.STG` = 77,024 B. The slider bank is 126
  BE f32 at `0x129D0`. A `.CMG` embeds a settings block at `0x695F08`
  and its own slider bank at `0x6A84E1`.

## 5. File safety and persisted state

- `atomicwrite`: writes to a sibling `.part` file, then renames. The rename is
  retried because the game holds saves open.
- `backups`: **every opened file** is copied to
  `%LOCALAPPDATA%\2k14-roster-editor\backups\<name>.<stamp>.<digest>.bak`,
  keeping at most 5 per name and 512 MB in total.
- Preferences: a `QSettings` ini (`ui.ini`) in the same folder. Patch-layer
  logs go to `%TEMP%\q2k_lab.log` and `%TEMP%\rosterlab_q2k_seal.log`.
- **README discrepancy**: the README says the tool "never writes to the file
  it opened", but `Document.save()` is `save_as(self.path)`. It overwrites
  the original after a one-time confirmation. The automatic backup is the
  real safety net.

## 6. Relevance to our RED MC work

1. Their correlation approach (RED MC CSV export ↔ bitstream) is the one we
   planned. It works, and it leaves about half the player fields only bounded
   (`bmin`/`wmax`). Our `.ai/csv/rmcsv.py` exports are the right input for
   doing the same ourselves.
2. `PLAYER_FIELDS` and the face/membership/`PlNum` rules above are
   independent ground truth to validate `ros_inspect.py` against.
   Roster Lab does not place everything: player records also carry a second
   `[010A]` team reference at bit 2313 (equal to the current team in
   1351/1351 players; found by our 06 doc, unnamed in Roster Lab).
3. Done 2026-09-26: 02/03/06/07/08/README were corrected against this
   (names are heap handles; directory pairing; section names; rating order).
4. Hazards any editor of ours must respect: zero face blocks, name-handle
   arenas, roster-slot gaps and `PlNum`, the 25-character alphanumeric save
   names, and the unmapped ~2.65 MB `.FXG` tail that references record ids
   (never renumber records).
