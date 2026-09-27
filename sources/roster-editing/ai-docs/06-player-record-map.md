# NBA 2K14 `.ROS` Player Record — Field Map

Derived 2026-08-02 from a controlled experiment: a custom player
(a PG with a known college and birthdate, jersey
19, assigned to the LA Lakers) was created in-game, giving a minimal
before/after pair (`RosterDefault.ROS` → `Roster02Aug2026.ROS`, only **233
differing bytes**).

All claims **[VERIFIED]** unless marked otherwise.

## Record geometry

- **Player record stride: 3644 bits (455.5 bytes).** Confirmed two ways:
  empty-slot autocorrelation (98.8% self-similarity at period 3644, only 55%
  at 1822) and five known players' birthdate fields all landing at the same
  residue (917) mod 3644.
- Records are **pre-allocated slots**: empty slots already carry their own ID
  fields (slot index) and template filler (alternating `1010...` patterns in
  some fields). Creating a CAP writes into the first free slot.
- **[VERIFIED 2026-09-26, Roster Lab]** The anchor used below is **record bit
  273**. A record starts at anchor−273 with `[u16 0x0103][u16 index]`, so
  `record field bit = anchor offset + 273`. Every offset in this file maps
  onto Roster Lab's schema with this one constant (Pos +183 → 456, Height
  −145 → 128, BirthYear +0 → 273).
- The "mirrored sub-record" is two separate things:
  - The ID mirror is **`ID2`** (bit 2631, 16 bits).
  - The team mirror is a **second `[010A]` team reference at bit 2313**. It is
    unnamed in Roster Lab, and wherever present (1351/1351 players in
    `FIBA 2017 SEABA.ROS`) it equals the current team.
  - The "133" seen at −76 and +2045 is not a value. It is bits 5–14 of the
    stamp word `0x010A` of these two references (`0x010A>>1 & 0x3FF = 133`),
    and it is 0 when the reference is empty.

## Slot addressing (self-calibrating)

Records sit at a constant stride, so one anchor locates the whole table:

```
anchor(slot) = anchor(known) + (slot - known_slot) * 3644
slot_id      = uint @ anchor-253, 12 bits      # lets you self-calibrate
```

Verified: LeBron slot 121 @ bit 766157, Kobe 173, Durant 338, Curry 380, the
custom CAP 1131 @ 4446597 — every one satisfies the formula exactly.
**Correction:** the Players table is section 0x0103 and holds **1665**
records. 5000 is the count of 0x0102 CustomName (02 § Table directory). The
table start is computable from the directory, so no content anchor is
needed: `record_bit(i) = start(0103) + 3644·i`.

## Anchor convention

Field offsets below are **relative to the first bit of the BirthYear field**
("anchor"). To find any player's anchor: search the file's MSB-first
bitstream for `year(11 bits) month(4 bits) day(5 bits)`:

```
pattern = f"{year:011b}{month:04b}{day:05b}"
```

Note storage order is **Year, Month, Day** even though RED MC captions list
Day, Month, Year. The absolute bit phase of the players table varies per file
(variable-length content earlier in the stream), so always anchor on content,
or on the slot stride once one anchor is known.

## Verified fields

| Bit offset (rel. anchor) | Width | Field | Evidence |
|---------|-------|-------|----------|
| −253 | 12–16 | **ID** (slot index; stored as 16 bits at record bit 16) | Values track record index exactly across 5 players (LeBron 121, Curry 380, Durant 338, Kobe 173, custom player 1131); pre-assigned in empty slots |
| −145 | 32 | **Height — IEEE-754 float32 (big-endian), centimetres** | LeBron 203.20 (6'8"), Curry 190.50 (6'3"), Durant 205.74 (6'9"), Kobe 198.12 (6'6") — exact real values; range across roster 160–221 cm |
| −113 | 32 | **Weight — IEEE-754 float32 (big-endian), pounds** | LeBron 250.0, Curry 185.0, Durant 230.0, Kobe 205.0, custom 178.0 |
| −76..−67 | ~10 | **Not a field:** the stamp half (`0x010A`) of the team reference at record bit 192 | 133 = `0x010A` bits 5–14; 0 = no team |
| −56..−50 | 6–7 | **Current team**: low bits of the `[010A][team]` reference at record bit 192 (Roster Lab `TeamID1`). Lakers=13, LeBron 9, Curry 28, Durant 25, Kobe 13 | new CAP assigned to Lakers got 13 |
| 0..10 | 11 | **BirthYear** (raw, e.g. 1985) | matched 5 known players |
| +11..+14 | 4 | **BirthMonth** (1–12) |〃 |
| +15..+19 | 5 | **BirthDay** (1–31) | 〃 |
| +28..+34 | 7 | **Number (jersey)**, record bit 301 | LeBron 6, Curry 30, Durant 35, Kobe 24, custom 19 — all correct |
| +45 | 1 | Inside **PeakAgeE** (record bit 314, 6 bits), not a flag | Roster Lab schema |
| +71..+78 | 8 | **CollegeID**: low bits of the `[010B][college]` reference at record bit 320 | Roster Lab `CollegeID` |
| +183..+185 | 3 | **Pos (primary position)** enum: PG=0, SG=1, SF=2, PF=3, C=4 | correct for all known players; distribution across 982 real players is near-uniform (217/177/199/189/200) |
| +186..+198 | 13 | **SecondPos** (459/3), **Personality** (463/2), **MinsAsg** (466/6) — not a portrait id | Roster Lab schema |
| +953..+1010 | ~57 | **Appearance block**: GenericF, Bodytype, Muscles, SkinTone, CAP_Hstl/Hcol, EyeColor, CAP_Eyebr, headband, facial hair, elbow gear (record bits 1226–1283) | Roster Lab schema |
| +1181..+1185 | 5 | **PlayStyle** (31-value enum, `Text/Enums.txt`) | LeBron 18 = "SF - All-Around", Kobe 11 = "SG - All-Around", Curry 1 = "PG - Scoring"; the enum's position group matches the Pos field for **98.5%** of 982 real players — no other offset in the record exceeds 55% |
| +1668..+1687 | 20 | **CYear1**, contract salary year 1 (record bit 1935, 26 bits): 532753 = $532,753 | Roster Lab schema |
| +1700..+1719 | 20 | **CYear2**, contract salary year 2 (record bit 1967, 26 bits): 556727 | 〃 |
| +2045..+2054 | ~10 | stamp half of the second team reference (see above) | 133 = `0x010A` |
| +2065..+2071 | 7 | **second team reference**, `[010A]` at record bit 2313; equals current team | 1351/1351 match |
| +2363 | 12–16 | **ID2** (record bit 2631, 16 bits), not ASA_ID (that is at 2425) | Roster Lab schema |
| +2571..+2906 | 42 × 8 | **Skill ratings array** — 42 consecutive 8-bit fields, `raw = 3 × (displayed − 25)`, i.e. `displayed = raw/3 + 25`, giving the documented 25–110 range | **Every** value of all 42 fields across all real players is an exact multiple of 3 — a run of precisely 42 such fields exists nowhere else in the record. Matches the caption file's `Skills:44` group minus its two non-rating entries (`Overall_I`, `SklBst`). |
| +2907..+3366 | — | tendencies / hot zones / gear / signature blob (unmapped) | rewritten on CAP creation |

Empty-slot template values worth knowing: birthdate region parses as
(1971, 8, 31); some fields hold alternating-bit filler (`0xAA`-style); ID
fields hold the slot index; template weight = 185 lbs (raw 114).

### Skill-rating ordering — RESOLVED (Roster Lab, verified 2026-09-26)

Storage order (record bits 2844..3179, 8 bits each, contiguous):

```
SShtCls SShtMed SBallHndl SSht3PT SShtFT SShtLoP SRunner SLayUpStnd SLayUp
SLayUpSpin SLayUpEuro SLayUpHop SStpThru SDunk SStdDunk SShtInT SShtOfD
SHustle SOffHDrib SBallSec SPass SDLowPost SOLowPost SBlock SHands SSteal
SSpeed SStamina SEmotion SVertical SOReb SDReb SDurab SDAwar SOAwar SConsis
SOnBallD SQuick SPOT SStrength SPstFdaway SPstHook
```

Independent check with this doc's own method (height correlation, 1375
rostered players in `FIBA 2017 SEABA.ROS`): SOReb +0.73, SDReb +0.71,
SBlock +0.68, SDLowPost +0.75, SStdDunk +0.78, versus SSpeed −0.75,
SQuick −0.77, SBallHndl −0.76, SSht3PT −0.62. That is physically consistent,
unlike caption order. Encoding: `displayed = (raw + 75) / 3`, the same as
`raw = 3 × (displayed − 25)`.

The original analysis follows. It is kept for the method, but its
conclusion is superseded.

The array location and encoding are proven, but which array position is
which named skill was not established, and it is *not* RED MC's caption
order. Correlating each of the 42 positions against height over 398 players
on real NBA teams gives physically impossible assignments under caption
order: the slots that caption order calls *Offense Rebound* (−0.83) and
*Vertical* (−0.84) are the most negatively height-correlated in the record,
while *Shoot In Traffic* (+0.86) and *Pass* (+0.78) are the most positive.
Rebounding cannot fall as players get taller — so storage order differs from
RED MC's display order.

To resolve: open a roster in RED MC, change **one named skill** on one
player, save, and `bitdiff` — the changed byte's index within the array names
that slot. 42 such edits (or a few, interpolating) fully labels the array.
Until then, treat the array as an ordered vector of ratings.

### Open items (from the height/weight/playstyle/ratings edit session)

Spans the in-game edit touched, now named via Roster Lab (anchor + 273 =
record bit):

- +1019 → GUndrshrt
- +1051..+1058 → sock, ankle, undershirt and elbow gear
- +1090..+1104 → GHdbndLg + **PlayType1–3** (the 535→4391 change is three
  4-bit play types)
- +1495 → AFreeT
- +1527 → AShtRlTim
- +2400..+2401 → GLeftArm

Note: an in-game roster re-save also sprinkles ~1-byte changes across many
unrelated tables (dirty counters/timestamps) — always anchor on the player
record, not the raw diff.

### Worked example (the sample CAP, slot 1131)

| Field | At creation | After the in-game edit |
|-------|-------------|------------------------|
| Height | 182.88 cm (6'0", CAP template default) | 207.66 cm (6'9¾") |
| Weight | 185.0 lb (template default) | 178.0 lb |
| PlayStyle | 5 = "PG - All-Around" | 1 = "PG - Scoring" |
| Position / Jersey / Team | PG / 19 / 13 (Lakers) | unchanged |

Height moved in ¼-inch steps (207.66 cm = 81.75 in), which is why the game
stores it as a float rather than an integer.

## What else changes when a player is created in-game

The full before/after diff touched 10 structures (all offsets file-specific):

| Region (this file) | Interpretation |
|--------------------|----------------|
| bytes 0x00–0x03 | CRC32 re-signed |
| bits 4999–5087 (bytes 0x270–0x27B) | two counter/bitmask words 64 bits apart, several bits 0→1 — bookkeeping (used-slot count / free-space accounting) **[HYPOTHESIS]** |
| bytes 0x1D0F0–0x1E2BB | one 2-bit + one 3-bit change, then 9 tiny changes spaced ≈3644±4 bits — quasi-regular records; team/rotation-related **[HYPOTHESIS]** |
| bytes 0xDCA19–0xDCAEA | scattered small-field changes ~33 bits apart incl. repeated binary **−1 decrements** (`100→011`) — ordered list updates (roster/free-agent ordering) **[HYPOTHESIS]** |
| bytes 0x87B1F–0x87CD5 | the player record itself (slot 1131) |
| bytes 0x266A5A–0x266A96 | CustomName strings written |

## Custom names (CAP players)

CAP first/last names are **not** added to the shared First_Names/Last_Names
tables. They are written into **reserved string slots in the heap**, padded
with `*` characters (empty slot = `**************`; 1413 such placeholders in
`FIBA 2017 SEABA.ROS`). Slots are null-terminated; leftover characters from a
previous longer occupant remain after the terminator (observed: a shorter name + "\0"
over a longer name leaving a `land` tail).

**Correction (verified):** *every* player, CAP or not, names his strings the
same way. `Last_Name` (record bit 32) and `First_Name` (bit 64) are 32-bit
heap handles (`[012F]`/`[0130]` + character offset; 02 § Strings), not
indices into the name tables. The 0102 CustomName section is a separate
5000-row table of 64-bit records.

## Reproducible methodology (what worked)

1. **Minimal pair diff**: create/change exactly one thing in-game or in RED
   MC; save; bit-diff (`ros_inspect.py bitdiff`). 233 changed bytes decompose
   cleanly into ~10 structures.
2. **Known-plaintext anchoring**: search for a distinctive multi-field value
   (birthdate y/m/d). Beware false positives: a per-season table matched
   `19,10,year` with year decrementing per row — always cross-check with a
   second player.
3. **Stride discovery**: autocorrelate the region (empty slots repeat) and
   check multiple known players share one residue mod stride.
4. **Vector matching**: for a candidate field offset/width, extract values
   for several known players and match against known attributes (jersey
   numbers confirmed this way in one shot).
5. **Population statistics beat star-matching.** Once one anchor is known,
   every slot is addressable, so validate candidates over ~1000 players:
   - *Distribution shape* — Pos was confirmed by a near-uniform 0–4 spread.
   - *Cross-field consistency* — PlayStyle was found by maximising agreement
     between its position group and the Pos field (98.5% vs <55% elsewhere).
   - *Encoding invariants* — the ratings array was delimited exactly by
     "every value is a multiple of 3".
   - *Physical correlation* — height/weight/big-man vs guard skills.
6. **Read the shipped spec first** (`ai-docs/08-official-field-spec.md`).
   Knowing Height is typed `Double` immediately explained why integer scans
   failed; the constant byte `134` before it is a float32 **exponent**
   (2^7 → 127+7), which is the tell for a float field in a bit-packed record.
