# Official RED MC Field Specification (Tutorials folder)

Two files in `Tutorials\NBA 2K14\` are the authoritative, author-written
specification of every editable field. They are the single most valuable
reference in the install and should be consulted **before** any
reverse-engineering guesswork.

## 1. `Fields & Values Tutorial - NBA 2K14.docx` (536 KB)

"RED MC General Editing Tutorial — NBA 2K14 roster files", 77 pages, Jan 2014.
Documents every tab: PLAYERS, ARENAS, TEAMS, COLLEGES, SCHEDULE, STAFF, COACH
STATS, PLAYBOOKS, PLAYER STATS, TEAM STATS, NAMES, JERSEYS, HEADSHAPES,
OVERRIDING ROTATIONS, PLAYER RATINGS, RECORDS, AWARDS, DRAFT PROJECTION,
TRADES, MATCHUPS, HALL OF FAME, ONLINE TEAM UP.

Content is held in **76 Word tables, 1160 rows**, each row:
`Field Name | Description | Values`. The *Values* column gives the **storage
type and range**, which the `Text/*.txt` caption files do **not** provide —
this is what makes it decisive for binary reverse engineering.

Extraction (no Word needed):

```bash
python -c "import zipfile,re,html; xml=zipfile.ZipFile(r'Fields & Values Tutorial - NBA 2K14.docx').read('word/document.xml').decode(); print(len(re.findall(r'<w:tbl>.*?</w:tbl>',xml,re.S)))"
```

Parse `<w:tbl>` → `<w:tr>` → `<w:tc>`, joining `<w:t>` runs per cell.

### Type vocabulary and what it means on disk

| Doc type | Meaning in the file | Confirmed example |
|----------|--------------------|-------------------|
| `Double` | **IEEE-754 float32, big-endian** (not a C double) | `Height` "Double Min: 0 Max: 9000" → float32 at anchor−145 decoding to 203.20 cm for LeBron |
| `Integer Min: 0 Max: N` | unsigned bitfield; the stored width can exceed what N needs | `ID` "Min: 0 Max: 9999" → **16 bits** at record bit 16 (values fit in 12–14, so the top bits read as zero) |
| `Integer Min: -128 Max: 127` | **[UNVERIFIED]** presumed signed 8-bit (stat/tendency deltas). Roster Lab found *no* two's-complement field anywhere it mapped (Players, Teams, Staff, stats…); it doesn't map Player_Ratings (011D–0121), so verify there with a bitdiff. Signed-looking values elsewhere turned out to be unsigned with an all-ones −1 sentinel (`uintn`) | `Dunk`, `Speed`, `Strength` in PLAYER RATINGS tab |
| `Enumerable: 0 - X 1 - Y …` | small unsigned enum; index = stored value | `Pos` (5 values, 3 bits), `PlayStyle` (31 values, 5 bits) |
| `String` | UTF-16BE, null-terminated, in the **string heap**; the record holds a 32-bit handle (02 § Strings) | player names |
| `Double Min: 25 Max: 110` | **8-bit scaled int**, `raw = 3 × (displayed − 25)` — *not* a float despite the label | the 42-entry skill array at anchor+2571 = record bit 2844 (order in 06) |

The last row is the important caveat: `Double` in this document means "RED MC
shows a fractional value", not "stored as floating point". Height and Weight
really are float32; the 25–110 skill ratings are 8-bit integers scaled by 3.
Always confirm against data.

### Enum extraction

The *Values* cells contain the full enumerations (identical content to
`Text/Enums.txt`, but keyed to a named field, which `Enums.txt` is not).
Word's run-splitting drops some index numbers, e.g. PlayStyle renders as
`0 - PG - Pass First 1 - PG - Scoring - PG - Defensive …`; the entries are
still in order, so re-index sequentially from 0 rather than trusting the
printed digits. Cross-check against the matching line in `Text/Enums.txt`.

## 2. `List Of Text Values.txt` (3.8 MB, UTF-16LE)

39,833 rows of `HASH;string` — the game's **in-game text/localization
table**, one 32-bit hex ID per displayed string:

```
Value;Definition
1A4977D9;{0:NAME:LONG} defeat {1:NAME:LONG} in {8:NUMBER} games to advance ({10:MONTH_DAY})
0002B7C7;Headband Color
00091A57;Head Package
```

Strings contain the game's templating syntax (`{0:NAME:LAST}`,
`{0:TEAM_1:CONFERENCE_RANK}`, `|PS3_MOVE|` button glyphs). This is the lookup
table behind RED MC's IFF in-game-text editing feature.

**These hashes are a different namespace from the `.ROS` struct-type hashes** —
none of the 31 struct hashes in the roster table directory appears here
(checked exhaustively). Do not use this file to try to name roster tables.

Useful for: resolving a UI string seen in-game to its ID, editing in-game text
via IFF, and identifying label/enum wording.

Read it with `encoding='utf-16-le'`; the first line is the header
`Value;Definition`.
