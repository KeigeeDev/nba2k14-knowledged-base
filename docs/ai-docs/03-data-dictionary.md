# Data Dictionary — Parsing RED MC's `Text/` Resources

RED MC ships its entire field dictionary as plain text under
`C:\Editing Tools\RED MC\Text\`. These files are the authoritative,
machine-readable source for **every editable field of every roster table** —
parse them instead of duplicating their content.

## `Text/NBA2K14/GridNames.txt` — table list

One internal table (tab) name per line, in order. 38 tables for 2K14:

```
Players, Rookie_Templates, CAP_Templates, MP_Templates, My_Legend, Arenas,
Teams, Colleges, ScheduleBase_82, ScheduleBase_58, ScheduleBase_29,
ScheduleBase_14, ScheduleBase_PreSeason, Staff, Old_Coach_Stats,
Playbooks_actual, Playbooks_default, Player_Stats, Team_Stats, First_Names,
Last_Names, City_Names, Jerseys, Headshapes, Overriding_Rotations,
Player_Ratings0..4, Records, Awards, Draft_Projection, Trades, Matchups,
Hall_Of_Fame, OnLine_TeamUp, Skills Boosts
```

These names are also the array names used by TURK scripts
(`Players[i].Height`), and each has a `<Name>_Num` count variable.

## `Text/NBA2K14/Captions/*.txt` — per-table field dictionaries

One file per logical table/tab: `Player.txt`, `Team.txt`, `Jersey.txt`,
`Staff.txt`, `Headshape.txt`, `Arena.txt`, `College.txt`, `Schedule.txt`,
`Rotation.txt`, `Playbook.txt`, `PlayerStat.txt`, `TeamStat.txt`,
`CoachStat.txt`, `NameData.txt`, `CustomName.txt`, `Award.txt`,
`GameRecord.txt`, `HallOfFamer.txt`, `Matchup.txt`, `DraftData.txt`,
`Draftees.txt`, `Transaction.txt`, `SkillsBoost.txt`, `PlayerRating.txt`,
`FreeAgentsList.txt`, `OnlineTeamup.txt`, `Struct44.txt`,
`Struct735767AE.txt`.

`Struct<HASH>.txt` files are keyed by the same struct-type hash that appears
in the `.ROS` table directory (see 02-ros-format.md).

### File grammar

```
Line 1:            <GroupName>:<fieldCount>;<GroupName>:<fieldCount>;...
Lines starting #:  either a sub-group header  "#<GroupName>;Sub:count;..."
                   or a bare "#" acting as a visual separator between fields
Field lines:       <FieldKey>;<Display Caption>;<Description>[;<flag>]
```

- `FieldKey` is the internal field name — the same identifier TURK scripts
  use (`Players[i].InjType` ↔ line `InjType;...` in `Player.txt`).
- Group counts on line 1 partition the field lines in order into UI tabs
  (e.g. `Player.txt`: `Names:3;General:9;Bio:22;Appearance:28;Play Style:7;
  Status:14;Stats:21;Game Highs:28;Skills:44;Signature Skills:5;
  Tendencies:58;Hot Zones:14;Animations:40;Contract:14;Gear:48` — **355**
  fields total, verified by summing the counts; Roster Lab's player layout
  also has 355 keys).
- Optional 4th token: short flag (e.g. `H` on Height, `W` on Weight).

### Notable Player fields (from `Player.txt`)

- Identity: `Last_Name`, `First_Name` (32-bit **string-heap handles**, not
  indices into the name tables — see 02 § Strings), `NickName`,
  `ID2` (keep equal to row ID), `ASA_ID` (second global player id; **must be
  unique** or box scores glitch).
- Slots/status: `IsUnused`, `SlotType`, `IsRegular`, `IsGener` (game
  generated), `IsDraftee`, `IsDrafted`.
- Bio: `Pos`, `SecondPos`, `Height` (cm), `Weight` (lbs), `BirthDay/Month/
  Year`, `YearsPro`, `CollegeID`, `DraftedBy`, `DraftYear/Round/Pos`.
- Visuals: `PortrID` (portrait id in portraits.iff), `GenericF` (generic vs
  cyberface), `CF_ID` (cyberface id), `HS_ID` (headshape row), `SkinTone`,
  full CAP face/tattoo/gear field sets.
- Skills/tendencies/hot zones/animations/contract — enumerated per group.
- Injuries: `InjType`, `InjDaysLeft` (used by the sample TURK script).

## `Text/Enums.txt` — combo-box value lists

One enum per line, **129 lists** (the file has no trailing newline, so
`wc -l` shows 128). The token before `;` is a **kind flag**, not a default
index (verified against Roster Lab's parsed `enums.json`: 115 kind-0, 14
kind-1):

- `0;<label0>,<label1>,...` — positional: the stored value is the position.
- `1;<value>,<label>,<value>,<label>,...` — explicit pairs, e.g.
  `1;-1,Not Rucker Park,0,Rucker Day,1,Rucker Night`. Values can be negative
  or sparse. Five playbook/jersey/logo lists use 8-digit hex hashes as
  values.

A list is identified by its 1-based line number. Lines ~1–95 are 2K13 lists
and ~96–129 are 2K14 lists, often in pairs; prefer the later list. **No file
maps fields to lists.** RED MC keeps that mapping internally. Roster Lab
hand-built one (`enums.MAP`/`TABLE_MAP`, with evidence per entry); it is
useful as a reference.

## `Text/IFF/Contents.txt`

Column captions for the IFF browser: `Name`, `FileID` (derived from file
name; the game addresses inner files by ID), `Type`, `Size`.

## `Text/NBA2K13/`

Parallel caption set for NBA 2K13 rosters (slightly different tables — no
`Draftees`/`SkillsBoost`/`PlayerRating` files, which were 2K14 additions).
