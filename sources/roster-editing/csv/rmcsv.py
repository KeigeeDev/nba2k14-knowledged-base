#!/usr/bin/env python3
"""CSV pipeline for RED MC roster exports.

RED MC's Export To CSV / Import From CSV is a GUI-only round trip, and its
exact output format (delimiter, header style, encoding) is compiled into the
exe -- it is not documented and not discoverable from Text/. So this tool
never *assumes* a format: it detects one from the file it is given, and
re-emits every untouched cell as the original bytes. An unedited file round
trips byte-identically; an edited one differs only in the cells you changed.
That is what makes the result safe to feed back into Import From CSV.

Subcommands:
  inspect   Detect format + identify which roster table the CSV came from.
  validate  Check values against the field dictionary (types, ranges, ids).
  stats     Summarise a column (min/max/mean/distribution).
  edit      Bulk --set / --where edits, preserving format exactly.
  diff      Cell-level diff of two CSVs, to audit before importing.

See .ai/csv/README.md for the workflow and .ai/turk/turk.py for the field
dictionary these checks are built on.
"""
from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "turk"))
import turk as turklib  # noqa: E402  (field dictionary, shared with the TURK kit)

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_DELIMS = [",", ";", "\t", "|"]


# ---------------------------------------------------------------------------
# Format detection + format-preserving CSV parsing
# ---------------------------------------------------------------------------
class CsvFile:
    """A parsed CSV that remembers exactly how it was written.

    Cells are kept as their original raw text; only cells that are actually
    edited get re-serialised. `to_bytes()` on an unedited file reproduces the
    input byte for byte.
    """

    def __init__(self, path: Path):
        self.path = path
        raw = path.read_bytes()
        self.encoding, self.bom, text = _decode(raw)
        self.delim = _sniff_delim(text)
        self.rows: list[list[str]] = []      # raw cell text, quotes included
        self.terms: list[str] = []           # line terminator per row
        for cells, term in _parse(text, self.delim):
            self.rows.append(cells)
            self.terms.append(term)
        self.dirty: set[tuple[int, int]] = set()

    # -- access ---------------------------------------------------------
    @property
    def header(self) -> list[str]:
        return [unquote(c) for c in self.rows[0]] if self.rows else []

    def data_rows(self):
        """Yield (row_index, [values]) for every non-header row."""
        for r in range(1, len(self.rows)):
            if len(self.rows[r]) == 1 and unquote(self.rows[r][0]).strip() == "":
                continue  # trailing blank line
            yield r, [unquote(c) for c in self.rows[r]]

    def get(self, r: int, c: int) -> str:
        return unquote(self.rows[r][c]) if c < len(self.rows[r]) else ""

    def set(self, r: int, c: int, value: str) -> None:
        if c >= len(self.rows[r]):
            return
        if unquote(self.rows[r][c]) == value:
            return
        self.rows[r][c] = requote(value, self.delim)
        self.dirty.add((r, c))

    def to_bytes(self) -> bytes:
        out = []
        for cells, term in zip(self.rows, self.terms):
            out.append(self.delim.join(cells) + term)
        return self.bom + "".join(out).encode(self.encoding)

    def describe(self) -> str:
        d = {",": "comma", ";": "semicolon", "\t": "tab", "|": "pipe"}[self.delim]
        terms = {t for t in self.terms if t}
        nl = "/".join(sorted({"\\r\\n" if t == "\r\n" else "\\n" if t == "\n"
                              else "\\r" for t in terms})) or "none"
        return (f"{d}-delimited, {self.encoding}"
                f"{' with BOM' if self.bom else ''}, line endings {nl}, "
                f"{len(self.rows)} rows x {len(self.header)} columns")


def _decode(raw: bytes) -> tuple[str, bytes, str]:
    for bom, enc in ((b"\xef\xbb\xbf", "utf-8"), (b"\xff\xfe", "utf-16-le"),
                     (b"\xfe\xff", "utf-16-be")):
        if raw.startswith(bom):
            return enc, bom, raw[len(bom):].decode(enc)
    for enc in ("utf-8", "cp1252"):
        try:
            return enc, b"", raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return "cp1252", b"", raw.decode("cp1252", errors="replace")


def _sniff_delim(text: str) -> str:
    """Pick the delimiter that yields the most consistent column count."""
    sample = text.split("\n")[:30]
    best, best_score = ",", (-1.0, 0)
    for d in CANDIDATE_DELIMS:
        counts = [len(_parse(ln, d)[0][0]) for ln in sample if ln.strip()]
        if not counts:
            continue
        mode = max(set(counts), key=counts.count)
        if mode < 2:
            continue
        score = (counts.count(mode) / len(counts), mode)
        if score > best_score:
            best, best_score = d, score
    return best


def _parse(text: str, delim: str, quote: str = '"'):
    """Stream-parse CSV, preserving each cell's raw text and each row's
    terminator. Handles quoted cells containing delimiters and newlines."""
    rows, row, i, n = [], [], 0, len(text)
    while i < n:
        start = i
        if text[i] == quote:
            i += 1
            while i < n:
                if text[i] == quote:
                    if i + 1 < n and text[i + 1] == quote:
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
        else:
            while i < n and text[i] != delim and text[i] not in "\r\n":
                i += 1
        row.append(text[start:i])
        if i < n and text[i] == delim:
            i += 1
            continue
        term = ""
        if i < n:
            if text.startswith("\r\n", i):
                term, i = "\r\n", i + 2
            elif text[i] in "\r\n":
                term, i = text[i], i + 1
        rows.append((row, term))
        row = []
        if i >= n:
            break
    if row:
        rows.append((row, ""))
    return rows or [([""], "")]


def unquote(cell: str) -> str:
    c = cell.strip()
    if len(c) >= 2 and c[0] == '"' and c[-1] == '"':
        return c[1:-1].replace('""', '"')
    return cell


def requote(value: str, delim: str) -> str:
    # RED MC quotes a cell if and only if it contains a space -- verified across
    # all 38 real exports in csv/FIBA 2026: 1677 space-bearing cells, every one
    # quoted, zero exceptions, while "-1", "O.J.", "O'Neal" and "NO/OKC" ship
    # bare. Omitting the quotes makes its importer split the value on
    # whitespace and shift every later column in the row, so " " belongs in
    # this set even though RFC 4180 does not require it.
    if any(ch in value for ch in (delim, '"', "\r", "\n", " ")):
        return '"' + value.replace('"', '""') + '"'
    return value


# ---------------------------------------------------------------------------
# Mapping CSV columns onto the field dictionary
# ---------------------------------------------------------------------------
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


class Mapping:
    """Maps CSV header columns to fields of one roster table."""

    def __init__(self, schema, header: list[str], table: str | None = None):
        self.schema = schema
        self.header = header
        self.table, self.stem, self.score = self._identify(table)
        self.cols: dict[int, dict] = {}     # column index -> field info
        self.unmapped: list[int] = []
        if self.stem:
            cap = schema.load_caption(self.stem)
            by_key = {k: v for k, v in cap["fields"].items()}
            by_norm = {}
            for f in cap["fields"].values():
                by_norm.setdefault(_norm(f["key"]), f)
                by_norm.setdefault(_norm(f["caption"]), f)
            for i, h in enumerate(header):
                f = by_key.get(h.strip().lower()) or by_norm.get(_norm(h))
                if f:
                    self.cols[i] = f
                else:
                    self.unmapped.append(i)

    def _identify(self, forced):
        """Score every caption file by how many headers it explains."""
        if forced:
            stem, _ = self.schema.caption_for(forced)
            if not stem:
                raise SystemExit(f"error: unknown table {forced!r}; "
                                 f"try `python .ai/turk/turk.py tables`")
            return forced, stem, 1.0
        best = (None, None, 0.0)
        stems = {v[0] for v in turklib.GRID_TO_CAPTION.values()}
        norm_header = [_norm(h) for h in self.header]
        for stem in sorted(stems):
            cap = self.schema.load_caption(stem)
            if not cap["order"]:
                continue
            keys = set()
            for f in cap["fields"].values():
                keys.add(_norm(f["key"]))
                keys.add(_norm(f["caption"]))
            hit = sum(1 for h in norm_header if h in keys)
            frac = hit / max(1, len(norm_header))
            if frac > best[2]:
                keys = [t for t, (s, _) in turklib.GRID_TO_CAPTION.items()
                        if s == stem]
                # report the properly-cased name from GridNames.txt
                proper = next((g for g in self.schema.tables
                               if g.lower() in keys), keys[0] if keys else stem)
                best = (proper, stem, frac)
        return best

    def field_col(self, name: str) -> int | None:
        n = _norm(name)
        for i, f in self.cols.items():
            if _norm(f["key"]) == n or _norm(f["caption"]) == n:
                return i
        return None


RANGE_RE = re.compile(r"(-?\d+)\s*\.\.\s*(-?\d+)")


def declared_range(field: dict):
    m = RANGE_RE.search(field.get("desc", ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def as_number(s: str):
    t = s.strip()
    if not t:
        return None
    try:
        return int(t)
    except ValueError:
        try:
            return float(t)
        except ValueError:
            return None


# ---------------------------------------------------------------------------
# Safe expression evaluation for --set / --where
# ---------------------------------------------------------------------------
import ast  # noqa: E402

_ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not,
    ast.USub, ast.UAdd, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div,
    ast.FloorDiv, ast.Mod, ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE,
    ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Name, ast.Load, ast.Constant,
    ast.Call, ast.IfExp, ast.List, ast.Tuple,
)
_FUNCS = {
    "int": int, "float": float, "str": str, "abs": abs, "min": min,
    "max": max, "round": round, "len": len,
    "clamp": lambda v, lo, hi: max(lo, min(hi, v)),
    "lower": lambda s: str(s).lower(), "upper": lambda s: str(s).upper(),
}


def safe_eval(expr: str, env: dict):
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"expression uses unsupported syntax: "
                             f"{type(node).__name__}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _FUNCS:
                raise ValueError("only these functions are allowed: "
                                 + ", ".join(sorted(_FUNCS)))
    return eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}},
                {**_FUNCS, **env})


def row_env(mapping: Mapping, values: list[str]) -> dict:
    """Column values addressable by field key and by caption, numeric where
    they look numeric."""
    env = {}
    for i, f in mapping.cols.items():
        if i >= len(values):
            continue
        raw = values[i]
        num = as_number(raw)
        val = num if num is not None else raw
        env[f["key"]] = val
        ident = re.sub(r"\W", "_", f["caption"])
        if ident and not ident[0].isdigit():
            env.setdefault(ident, val)
    return env


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def _load(args):
    path = Path(args.file)
    if not path.is_file():
        raise SystemExit(f"error: {path}: not found")
    csvf = CsvFile(path)
    schema = turklib.Schema(args.game)
    mapping = Mapping(schema, csvf.header, getattr(args, "table", None))
    return csvf, schema, mapping


def cmd_inspect(args) -> int:
    csvf, schema, m = _load(args)
    print(f"{csvf.path}")
    print(f"  format : {csvf.describe()}")
    # A byte-identical round trip proves the parser understood the file.
    ok = csvf.to_bytes() == csvf.path.read_bytes()
    print(f"  round trip: {'byte-identical' if ok else 'MISMATCH -- do not edit this file'}")
    if m.stem:
        print(f"  table  : {m.table} (Captions/{m.stem}.txt), "
              f"{len(m.cols)}/{len(csvf.header)} columns recognised "
              f"({m.score:.0%} header match)")
    else:
        print("  table  : could not identify")
    if m.unmapped:
        names = ", ".join(csvf.header[i] or f"<col {i}>" for i in m.unmapped[:12])
        print(f"  unrecognised columns ({len(m.unmapped)}): {names}"
              + (" ..." if len(m.unmapped) > 12 else ""))
    n = sum(1 for _ in csvf.data_rows())
    print(f"  data rows: {n}")
    if not ok:
        return 1
    return 0


def cmd_validate(args) -> int:
    csvf, schema, m = _load(args)
    problems, warnings = [], []

    if not m.stem:
        print("error: could not identify which roster table this CSV is from; "
              "pass --table", file=sys.stderr)
        return 2

    ncols = len(csvf.header)
    numericish: dict[int, int] = {}      # column -> count of numeric cells
    present: dict[int, int] = {}         # column -> count of non-blank cells
    total = 0
    seen_ids: dict[str, dict[str, int]] = {}

    for r, values in csvf.data_rows():
        total += 1
        if len(values) != ncols:
            problems.append(f"row {r + 1}: {len(values)} cells, header has {ncols}")
        for i, f in m.cols.items():
            if i >= len(values):
                continue
            raw = values[i].strip()
            if raw == "":
                continue
            present[i] = present.get(i, 0) + 1
            num = as_number(raw)
            if num is not None:
                numericish[i] = numericish.get(i, 0) + 1
                rng = declared_range(f)
                if rng and not (rng[0] <= num <= rng[1]):
                    warnings.append(f"row {r + 1} {f['key']}={raw} outside "
                                    f"documented range {rng[0]}..{rng[1]}")
            # uniqueness checks the docs call out explicitly
            if f["key"].lower() in ("asa_id",):
                bucket = seen_ids.setdefault(f["key"], {})
                if raw in bucket:
                    problems.append(f"row {r + 1}: duplicate {f['key']}={raw} "
                                    f"(first seen row {bucket[raw] + 1}) -- "
                                    f"duplicates glitch box scores")
                else:
                    bucket[raw] = r

    # Stray text in a numeric column is almost always a typo. Judge by the
    # absolute number of outliers so this works on small files too.
    for i, hits in numericish.items():
        seen = present.get(i, 0)
        outliers = seen - hits
        if hits >= 2 and 0 < outliers <= max(1, round(0.05 * seen)):
            f = m.cols[i]
            for r, values in csvf.data_rows():
                if i < len(values):
                    v = values[i].strip()
                    if v and as_number(v) is None:
                        problems.append(f"row {r + 1} {f['key']}: non-numeric "
                                        f"{v!r} in an otherwise numeric column")

    print(f"{csvf.path}")
    print(f"  {m.table} ({m.stem}.txt), {total} rows, "
          f"{len(m.cols)}/{ncols} columns recognised")
    for p in problems[:args.limit]:
        print(f"  error   {p}")
    for w in warnings[:args.limit]:
        print(f"  warning {w}")
    extra = max(0, len(problems) - args.limit) + max(0, len(warnings) - args.limit)
    if extra:
        print(f"  ... {extra} more (raise --limit to see them)")
    if m.unmapped:
        print(f"  note: {len(m.unmapped)} column(s) not in the field "
              f"dictionary; they are passed through untouched")
    print(f"  {len(problems)} error(s), {len(warnings)} warning(s)")
    return 1 if problems else 0


def cmd_stats(args) -> int:
    csvf, schema, m = _load(args)
    col = m.field_col(args.field)
    if col is None:
        print(f"error: no column for field {args.field!r}; "
              f"try `python .ai/turk/turk.py fields {m.table} {args.field}`",
              file=sys.stderr)
        return 2
    f = m.cols[col]
    nums, blanks, texts = [], 0, {}
    for _, values in csvf.data_rows():
        raw = values[col].strip() if col < len(values) else ""
        if not raw:
            blanks += 1
            continue
        n = as_number(raw)
        if n is None:
            texts[raw] = texts.get(raw, 0) + 1
        else:
            nums.append(n)
    print(f"{f['key']} ({f['caption']}) -- {m.table}")
    if f.get("desc"):
        print(f"  {f['desc'][:110]}")
    rng = declared_range(f)
    if rng:
        print(f"  documented range: {rng[0]}..{rng[1]}")
    if nums:
        print(f"  n={len(nums)} min={min(nums)} max={max(nums)} "
              f"mean={statistics.mean(nums):.2f} median={statistics.median(nums)}")
        buckets: dict = {}
        for v in nums:
            buckets[v] = buckets.get(v, 0) + 1
        if len(buckets) <= 15:
            for v in sorted(buckets):
                bar = "#" * max(1, round(40 * buckets[v] / len(nums)))
                print(f"    {v:>6} {buckets[v]:>5}  {bar}")
    if texts:
        print(f"  {len(texts)} distinct non-numeric value(s):")
        for v, c in sorted(texts.items(), key=lambda kv: -kv[1])[:10]:
            print(f"    {c:>5}  {v}")
    if blanks:
        print(f"  {blanks} blank")
    return 0


def cmd_edit(args) -> int:
    csvf, schema, m = _load(args)
    if not m.stem:
        print("error: could not identify the table; pass --table", file=sys.stderr)
        return 2

    assignments = []
    for spec in args.set:
        if "=" not in spec:
            print(f"error: --set expects FIELD=EXPR, got {spec!r}", file=sys.stderr)
            return 2
        name, _, expr = spec.partition("=")
        col = m.field_col(name.strip())
        if col is None:
            print(f"error: no column for field {name.strip()!r}", file=sys.stderr)
            return 2
        assignments.append((col, m.cols[col], expr.strip()))

    changed_rows = 0
    changed_cells = 0
    preview = []
    for r, values in csvf.data_rows():
        env = row_env(m, values)
        try:
            if args.where and not safe_eval(args.where, env):
                continue
        except Exception as e:
            print(f"error: --where failed on row {r + 1}: {e}", file=sys.stderr)
            return 2
        row_hit = False
        for col, f, expr in assignments:
            try:
                new = safe_eval(expr, env)
            except Exception as e:
                print(f"error: --set {f['key']} failed on row {r + 1}: {e}",
                      file=sys.stderr)
                return 2
            if isinstance(new, float) and new.is_integer():
                new = int(new)
            new_s = str(new)
            old_s = values[col] if col < len(values) else ""
            if new_s != old_s:
                rng = declared_range(f)
                n = as_number(new_s)
                if rng and n is not None and not (rng[0] <= n <= rng[1]):
                    if not args.force:
                        print(f"error: row {r + 1} {f['key']}={new_s} is outside "
                              f"the documented range {rng[0]}..{rng[1]}; "
                              f"use --force to allow", file=sys.stderr)
                        return 2
                    print(f"  warning: row {r + 1} {f['key']}={new_s} outside "
                          f"documented range {rng[0]}..{rng[1]}")
                csvf.set(r, col, new_s)
                changed_cells += 1
                row_hit = True
                if len(preview) < 10:
                    preview.append(f"    row {r + 1} {f['key']}: {old_s} -> {new_s}")
        changed_rows += 1 if row_hit else 0

    print(f"{csvf.path}")
    print(f"  {changed_cells} cell(s) in {changed_rows} row(s) would change")
    for line in preview:
        print(line)
    if changed_cells > len(preview):
        print(f"    ... {changed_cells - len(preview)} more")

    if args.dry_run:
        print("  dry run -- nothing written (drop --dry-run to write)")
        return 0
    if not changed_cells:
        print("  nothing to write")
        return 0

    out = Path(args.out) if args.out else csvf.path.with_suffix(".edited.csv")
    if out.exists() and not args.force:
        print(f"error: {out} exists; pass --force to overwrite", file=sys.stderr)
        return 2
    out.write_bytes(csvf.to_bytes())
    print(f"  wrote {out}")
    print(f"  next: `diff` it against the original, then Import From CSV in RED MC")
    return 0


def cmd_diff(args) -> int:
    a, b = CsvFile(Path(args.file)), CsvFile(Path(args.other))
    if a.header != b.header:
        print("headers differ:")
        for h in set(a.header) ^ set(b.header):
            print(f"  only in one file: {h}")
        return 1
    ra = {r: v for r, v in a.data_rows()}
    rb = {r: v for r, v in b.data_rows()}
    if len(ra) != len(rb):
        print(f"row count differs: {len(ra)} vs {len(rb)}")
    shown = 0
    total = 0
    for r in sorted(set(ra) & set(rb)):
        for i, h in enumerate(a.header):
            va = ra[r][i] if i < len(ra[r]) else ""
            vb = rb[r][i] if i < len(rb[r]) else ""
            if va != vb:
                total += 1
                if shown < args.limit:
                    print(f"  row {r + 1} {h}: {va!r} -> {vb!r}")
                    shown += 1
    print(f"{total} cell difference(s)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="rmcsv.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=turklib.DEFAULT_GAME,
                    help="NBA2K14 (default) or NBA2K13")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, table=True):
        p.add_argument("file")
        if table:
            p.add_argument("--table", help="force the roster table "
                                           "(default: auto-detect from headers)")

    p = sub.add_parser("inspect", help="detect format and table")
    common(p)
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("validate", help="check values against the field dictionary")
    common(p)
    p.add_argument("--limit", type=int, default=25)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("stats", help="summarise one column")
    common(p)
    p.add_argument("field")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("edit", help="bulk edit, preserving format")
    common(p)
    p.add_argument("--set", action="append", default=[], required=True,
                   metavar="FIELD=EXPR")
    p.add_argument("--where", metavar="COND")
    p.add_argument("--out", help="output path (default: <name>.edited.csv)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="allow out-of-range values and overwrite the output")
    p.set_defaults(func=cmd_edit)

    p = sub.add_parser("diff", help="cell-level diff of two CSVs")
    common(p, table=False)
    p.add_argument("other")
    p.add_argument("--limit", type=int, default=40)
    p.set_defaults(func=cmd_diff)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
