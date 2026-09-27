# TURK Scripting Language

TURK is RED MC's built-in batch-editing language — Pascal-like structure with
keywords from Chuvash. Scripts are plain text files with the `.TURK`
extension, written in any editor (or RED MC's Scripting Wizard) and executed
inside RED MC against the currently loaded roster.

**This is the only programmatic automation interface RED MC has** — there is
no CLI, no plugin API, no COM interface. Any AI-driven automation that wants
to stay inside RED MC's guarantees must generate TURK scripts (see
05-ai-integration.md).

## Language rules

- Everything is a string internally; ints/floats auto-convert. Types in
  declarations are decorative.
- **Not case sensitive.** Comments: `!!` to end of line, or `{ ... }`.
- **Postfix/RPN-flavored syntax**: the operator comes *after* its operands
  (`A B :=` means `A := B`).

## Keyword table

| TURK | Meaning |
|------|---------|
| `;` | statement separator |
| `A B :=` | assign B to A |
| `A B +=` / `A B -=` | compound add/subtract |
| `+ - * / = > < >= <= <>` | arithmetic / comparison |
| `//` | integer div |
| `%` | mod |
| `AN a` | NOT a (preferred negation) |
| `a E b` | a OR b |
| `a TATA b` (or `a TA b`) | a AND b |
| `PUSCHLA ... VESCHLE` | begin ... end |
| `a PULSAN b UNSARAN c` | IF a THEN b ELSE c |
| `i VALLI a RAN b TARAN TU` | FOR i := a TO b (step 1) |
| `ULSH` | var-declaration block (before first `puschla`) |
| `VAY YAPALI <Name>;` | script header ("program <Name>") |
| `"text"` | string literal |

## Data model

- Roster tables are arrays named after the tabs in
  `Text/NBA2K14/GridNames.txt`: `Players`, `Teams`, `Jerseys`, `Staff`, ...
- Field access: `Players[expr].FieldKey` where `FieldKey` is the internal
  name from the caption files (`Text/NBA2K14/Captions/Player.txt` etc.).
- Row counts: `<TabName>_Num` (e.g. `Players_Num`, `Teams_Num`).
- All variables must be declared in one `ulsh` block before the first
  `puschla`. The final `veschle` ends with a period: `veschle.`

## Annotated example (`Scripts/UnInjure All.TURK`)

```
vay yapali Uninjure;            !! program Uninjure
{Uninjures all the players}

ulsh
  i: int;                       !! declare loop variable

puschla                         !! begin
  i valli 0 ran Players_Num - 1 taran tu    !! for i := 0 to Players_Num-1
  puschla
    Players[i].InjType 0 := ;   !! Players[i].InjType := 0
    Players[i].InjDaysLeft 0 := !! Players[i].InjDaysLeft := 0
  veschle
veschle.                        !! end.  (note the final period)
```

## More patterns

Set all players' loyalty to 100, but only for regular players:

```
vay yapali MaxLoyalty;

ulsh
  i: int;

puschla
  i valli 0 ran Players_Num - 1 taran tu
  puschla
    Players[i].IsRegular 1 = pulsan
      Players[i].Loyalty 100 :=
  veschle
veschle.
```

Gotchas for generated scripts:

- Operator order is postfix: `Players[i].Height 200 + 4 :=` sets Height to
  204 (expression `200 + 4` evaluated, then assigned).
- Statement separator `;` between statements, none before `veschle`.
- Enum-typed fields take the **integer index** into the matching line of
  `Text/Enums.txt` (e.g. `InjType 0` = "Healthy").
