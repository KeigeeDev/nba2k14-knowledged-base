# CSV pipeline

RED MC can **Export To CSV** and **Import From CSV** from its roster grids.
That is the one path where an AI can do real *data* work — rebalancing
ratings, bulk renames, generating rookie classes, auditing a roster — instead
of only writing TURK scripts.

This tool sits in the middle of that round trip:

```
RED MC  --Export To CSV-->  file.csv  --rmcsv.py-->  file.edited.csv  --Import From CSV-->  RED MC
```

## The important design constraint

**RED MC's CSV format is not documented and not discoverable.** The delimiter,
whether headers are field keys or display captions, the encoding — all of it
lives in compiled Delphi code. Searching `RED_MC.exe` turns up only the menu
action names (`ShowDialog_ExportToCSV`), no format strings.

So this tool never assumes a format. It **detects** one from the file it is
given and **re-emits every untouched cell as the original bytes**. An unedited
file round trips byte-identically; an edited one differs only in the cells you
changed. That is what makes the output safe to feed back to Import From CSV,
whatever RED MC's actual dialect turns out to be.

Verified against comma / semicolon / tab delimiters, cp1252 / utf-8 / utf-8-BOM
/ utf-16-le encodings, CRLF and LF, fully-quoted and minimally-quoted files,
and cells containing embedded commas, quotes and newlines. Run the suite:

```bash
python .ai/csv/test_rmcsv.py
```

## Commands

```bash
# What is this file, and which table did it come from?
python .ai/csv/rmcsv.py inspect roster.csv

# Check it against the field dictionary before importing
python .ai/csv/rmcsv.py validate roster.csv

# Understand a column before changing it
python .ai/csv/rmcsv.py stats roster.csv Loyalty

# Bulk edit -- always dry-run first
python .ai/csv/rmcsv.py edit roster.csv --set "Loyalty=clamp(Loyalty+10,0,100)" \
    --where "IsRegular == 1" --dry-run

# Audit exactly what changed before you import
python .ai/csv/rmcsv.py diff roster.csv roster.edited.csv
```

`edit` writes to `<name>.edited.csv` by default and never touches the input.
Add `--game NBA2K13` for 2K13 rosters, `--table Players` if auto-detection
picks wrong.

### Expressions

`--set FIELD=EXPR` and `--where COND` take small Python-like expressions where
every column is a variable, addressable by field key (`Loyalty`) or by display
caption with non-word characters replaced (`Years_Pro`). Numeric-looking cells
arrive as numbers.

Available functions: `int float str abs min max round len clamp lower upper`.
Anything else — attribute access, imports, calls to other functions — is
rejected by the parser before evaluation.

```bash
--set "Loyalty=clamp(Loyalty + 10, 0, 100)"
--set "NickName='Rookie'" --where "YearsPro == 0 and IsRegular == 1"
--set "PeakAgeE=PeakAgeS + 6"
```

## What validate checks

| Check | Basis |
|---|---|
| Duplicate `ASA_ID` | `03-data-dictionary.md`: must be unique or box scores glitch |
| Text in an otherwise-numeric column | typo detection |
| Row cell count vs header | truncated or malformed rows |
| Values outside a documented range | the `0..100` in a field's own description |
| Unrecognised columns | reported, then passed through untouched |

**Coverage limit worth knowing:** only **3 of 355** Player fields state a
numeric range in their caption description (`Loyalty`, `Play4Winner`,
`FinSecurity`), so the range check barely applies. The real ranges live in
`Tutorials\NBA 2K14\Fields & Values Tutorial - NBA 2K14.docx` — 1160 field rows
with storage types and ranges, per
[../../ai-docs/08-official-field-spec.md](../../ai-docs/08-official-field-spec.md).
Parsing that docx into the field dictionary is the highest-value upgrade to
this tool.

Enum-typed columns are **not** value-checked, for the same reason the TURK kit
does not: RED MC does not record which enum belongs to which field. Use
`python .ai/turk/turk.py enums "<label>"` to find an enum's integer value.

## Workflow

1. In RED MC, open the roster and **Export To CSV** (the dialog offers
   *Selected Tab* or *Whole File*).
2. `inspect` it — confirm the table was identified and the round trip is
   byte-identical. If it is not, **stop and do not edit**; send me the file.
3. `validate` it to get a baseline of pre-existing problems.
4. `edit --dry-run`, read the preview, then run for real.
5. `diff` the two files and read every change.
6. Back up the roster, then **Import From CSV** in RED MC.

## The quoting rule -- load-bearing, learned from a real import

**RED MC quotes a cell if and only if it contains a space.**

Verified across all 38 real exports in `csv/FIBA 2026`: 1677 cells contain a
space and every single one is quoted, zero exceptions -- while `-1`, `O.J.`,
`O'Neal` and `NO/OKC` all ship bare. So it is not RFC 4180's rule, and it is
not "quote anything with punctuation". It is the space, specifically.

This matters because it is **not symmetric**. Reading an unquoted
`Gomez de Liaño` is harmless; *writing* it unquoted is not. RED MC's importer
splits the value on whitespace, shifts every later column in that row, and you
get a dialog like `"Juan" is not a valid integer value` -- or worse, silent
corruption of a row that happens to still parse. `requote()` handles this, but
if you ever write these files by another route, match the rule.

A clean `validate` and a correct `diff` will **not** catch a violation: the
file is valid CSV by RFC rules, and `diff` compares parsed cells rather than
raw bytes. Scan for it directly before importing.

## Real exports: proven

No longer synthetic-only. Four tables -- `Teams`, `Staff`, `Players` and
`Arenas` -- have completed a full export -> edit -> import cycle through RED MC
against the `csv/FIBA 2026` set. Real exports are comma-delimited, **UTF-16 LE
with BOM**, CRLF, with an unnamed empty first column before `ID`.

Keep real exports as permanent fixtures:

```bash
python .ai/csv/test_rmcsv.py --extra "csv/FIBA 2026"
```
