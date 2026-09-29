# TURK (RED MC scripting)

**Status:** [VERIFIED] for the syntax and the example, which come from RED MC's own TURK tutorial and sample scripts (owner's notes).
**Category:** tool
**Last updated:** 2026-09-27

## Summary

TURK is RED MC's built-in batch-editing language, and the only programmatic way to drive RED MC itself. Scripts are plain `.TURK` text files that run inside RED MC against the loaded roster, so RED MC handles all the bit packing, strings and checksums. That makes TURK a safe target for AI-generated edits.

## Language rules

- The syntax is postfix: operators come after their operands. `A B :=` means `A := B`.
- Keywords come from Chuvash. It isn't case-sensitive.
- Everything is a string internally; numbers auto-convert.
- Comments are `!!` to end of line, or `{ ... }`.
- Declare all variables in one `ulsh` block before the first `puschla`. The script ends with `veschle.` (with a period).

| TURK | Meaning |
|---|---|
| `VAY YAPALI <Name>;` | Script header ("program") |
| `ULSH` | Variable declaration block |
| `PUSCHLA ... VESCHLE` | begin ... end |
| `A B :=` / `A B +=` / `A B -=` | Assign / add / subtract |
| `+ - * / // %` | Arithmetic (`//` integer division) |
| `= > < >= <= <>` | Comparison |
| `AN a` / `a E b` / `a TATA b` | NOT / OR / AND |
| `a PULSAN b UNSARAN c` | IF a THEN b ELSE c |
| `i VALLI a RAN b TARAN TU` | FOR i := a TO b |

**Data model:**
- Tables are arrays named after RED MC's tabs (`Players`, `Teams`, ...). `<Table>_Num` is the row count.
- Fields use the internal keys from `Text\NBA2K14\Captions\*.txt`, e.g. `Players[i].InjType`.
- Enum fields take the integer index from the matching list in `Text\Enums.txt`.

## Example (ships with RED MC as `Scripts\UnInjure All.TURK`)

```
vay yapali Uninjure;
{Uninjures all the players}
ulsh
  i: int;
puschla
  i valli 0 ran Players_Num - 1 taran tu
  puschla
    Players[i].InjType 0 := ;
    Players[i].InjDaysLeft 0 :=
  veschle
veschle.
```

Separate statements with `;`, but don't put one before `veschle`.

## Sources

- [`sources/roster-editing/ai-docs/04-turk-scripting.md`](../../sources/roster-editing/ai-docs/04-turk-scripting.md) (owner's notes from RED MC's TURK docs and samples).
- Using AI to write TURK: [RED MC and AI tools](../ai-workflows/red-mc-ai-integration.md).

## Open questions

- Operator precedence inside longer postfix expressions (`Players[i].Height 200 + 4 :=` is documented to set 204).
- Can TURK add or delete records, or only edit existing ones?
