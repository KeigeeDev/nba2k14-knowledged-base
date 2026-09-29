"""rlapply - apply RED MC CSV exports to a 2K14 .ROS through Roster Lab, headless.

Roster Lab by Q2K (closed freeware, installed separately) does all the binary
work: this script imports its data layer (`document.RosterDocument`) at run
time, calls its `set()` for each cell and saves through its own `save_as()`,
so its save gates, face/name audits, roster-slot/PlNum bookkeeping and CRC
all apply. Nothing of Roster Lab is copied here.

Needs the same Python as the Roster Lab build (3.14):

    py -3.14 .ai/rosterlab/rlapply.py diff  "FIBA 2027 TEST 1" --csv "csv/FIBA 2026/v8"
    py -3.14 .ai/rosterlab/rlapply.py apply "FIBA 2027 TEST 1" --csv "csv/FIBA 2026/v8" --teams 2
    py -3.14 .ai/rosterlab/rlapply.py apply "FIBA 2027 TEST 1" --csv "csv/FIBA 2026/v8" --teams 2 --out "FIBA 2027 TEST 2"

`apply` without --out is a dry run. See README.md next to this file.
"""

import argparse
import collections
import json
import os
import re
import shutil
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
RED_MC = HERE.parent.parent
ROSTER_LAB = Path(os.environ.get("ROSTER_LAB", r"C:\Editing Tools\Roster Lab by Q2K"))
SAVES = Path(os.environ.get("APPDATA", "")) / "2K Sports" / "NBA 2K14" / "Saves"

# CSV table -> Roster Lab field prefix. Only these four are wired up.
TABLES = {"Players": "", "Teams": "team:", "Staff": "staff:", "Arenas": "arena:"}
ROSTER_COLS = [f"Ros_{p}" for p in ("PG", "SG", "SF", "PF", "C")] + \
              [f"Ros_S{i}" for i in range(6, 13)] + [f"Ros_R{i}" for i in range(13, 21)]
STAFF_COLS = ("Staff_HC", "Staff_AC", "Staff_SPr1", "Staff_SPr2", "Staff_SPr3",
              "Staff_Trn", "Staff_SNBA")
PASSES = 4  # later roster-slot writes can clear earlier situational picks


class Fail(Exception):
    pass


# -- setup --------------------------------------------------------------------

def load_engines():
    if sys.version_info[:2] != (3, 14):
        raise Fail(f"Roster Lab's modules are Python 3.14 bytecode; this is "
                   f"{sys.version.split()[0]}. Run with: py -3.14 {Path(__file__).name} ...")
    internal = ROSTER_LAB / "_internal"
    if not (internal / "document.pyc").exists():
        raise Fail(f"Roster Lab not found at {ROSTER_LAB} (set ROSTER_LAB to its folder)")
    sys.path.insert(0, str(internal))
    sys.path.insert(0, str(RED_MC / ".ai" / "csv"))
    global document, rmcsv
    import document  # noqa: E402  Roster Lab data layer
    import rmcsv     # noqa: E402  our CSV reader


def resolve_ros(name, must_exist=True):
    p = Path(name)
    if p.suffix.upper() != ".ROS":
        p = p.with_name(p.name + ".ROS")
    if not p.parent.parts or str(p.parent) == ".":
        if not p.exists() or not must_exist:
            p = SAVES / p.name
    if must_exist and not p.exists():
        raise Fail(f"roster not found: {p}")
    return p


def load_csvs(folder):
    folder = Path(folder)
    out = {}
    for t in TABLES:
        f = folder / f"{t}.csv"
        if f.exists():
            cf = rmcsv.CsvFile(f)
            rows = {}
            for _, vals in cf.data_rows():
                rows[int(vals[1])] = dict(zip(cf.header, vals))
            out[t] = (cf.header, rows)
    if not out:
        raise Fail(f"no Players/Teams/Staff/Arenas.csv in {folder}")
    return out


# -- comparison ---------------------------------------------------------------

def same(cur, want):
    if isinstance(cur, float):
        try:
            return abs(cur - float(want)) < 0.006
        except ValueError:
            return False
    if cur is None:
        return want in ("", "-1")
    if str(cur) == want:
        return True
    try:
        return float(cur) == float(want)
    except (TypeError, ValueError):
        return False


def conv(cur, want):
    if isinstance(cur, float):
        return float(want)
    if isinstance(cur, int) and not isinstance(cur, bool):
        return int(want)
    return want


def snapshot(doc, csvs):
    """{(table, id, col): (roster value, csv value)} for every mapped cell,
    plus {table: Counter(unmapped col)}."""
    snap, unmapped = {}, collections.defaultdict(collections.Counter)
    for t, (hdr, rows) in csvs.items():
        pfx = TABLES[t]
        for rid, row in rows.items():
            for col in hdr[2:]:
                try:
                    snap[(t, rid, col)] = (doc.get(rid, pfx + col), row[col])
                except Exception:
                    unmapped[t][col] += 1
    return snap, unmapped


def write_order(key):
    t, _, col = key
    if t == "Teams" and col.startswith("Ros_"):
        return 0
    if t == "Teams" and col.startswith("Sit_"):
        return 1
    if t == "Teams":
        return 2
    if t == "Players" and col == "TeamID1":
        return 4
    return 3


# -- scope --------------------------------------------------------------------

def parse_ids(spec):
    ids = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)-(\d+)", part)
        if m:
            ids.update(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            ids.add(int(part))
        else:
            raise Fail(f"bad id list {spec!r}")
    return ids


def build_scope(args, csvs, doc):
    scope = collections.defaultdict(set)
    notes = []
    if args.all:
        for t, (_, rows) in csvs.items():
            scope[t].update(rows)
    for spec in args.rows or []:
        m = re.fullmatch(r"(\w+):(.+)", spec)
        if not m or m.group(1) not in TABLES:
            raise Fail(f"--rows wants TABLE:IDS with TABLE in {list(TABLES)}, got {spec!r}")
        scope[m.group(1)].update(parse_ids(m.group(2)))
    for f in args.changes or []:
        f = Path(f)
        if f.is_dir():
            f = f / "changes.json"
        data = json.loads(f.read_text(encoding="utf-8"))
        for t, items in data.items():
            if t in TABLES:
                scope[t].update(int(x["id"]) for x in items)
    if args.teams:
        if "Teams" not in csvs:
            raise Fail("--teams needs Teams.csv in the CSV folder")
        trows = csvs["Teams"][1]
        for tid in parse_ids(args.teams):
            if tid not in trows:
                raise Fail(f"team {tid} is not in Teams.csv")
            row = trows[tid]
            scope["Teams"].add(tid)
            for c in ROSTER_COLS:
                if c in row and int(row[c]) >= 0:
                    scope["Players"].add(int(row[c]))
            for c in STAFF_COLS:
                if c in row and int(row[c]) >= 0:
                    scope["Staff"].add(int(row[c]))
            if "ArenaID" in row and int(row["ArenaID"]) >= 0:
                scope["Arenas"].add(int(row["ArenaID"]))
            notes.append(f"team {tid} {row.get('Name', '')}: team row, "
                         f"its CSV roster, staff and arena")
        # a player we rewrite who also sits on another team's roster
        chosen = parse_ids(args.teams)
        for other, row in trows.items():
            if other in chosen:
                continue
            for c in ROSTER_COLS:
                pid = int(row.get(c, -1))
                if pid in scope["Players"]:
                    notes.append(f"WARNING: player {pid} is also on team {other} "
                                 f"({row.get('Name', '')}); his edits show there too")
    if not any(scope.values()):
        raise Fail("nothing in scope: give --teams, --rows, --changes or --all")
    return {t: ids for t, ids in scope.items() if t in csvs}, notes


# -- commands -----------------------------------------------------------------

def cmd_diff(args):
    src = resolve_ros(args.roster)
    csvs = load_csvs(args.csv)
    doc = document.RosterDocument(str(src))
    snap, unmapped = snapshot(doc, csvs)
    print(f"{src.name} vs {Path(args.csv)}")
    teams = csvs.get("Teams", (None, {}))[1]
    for t in csvs:
        rows = collections.Counter(k[1] for k, (c, w) in snap.items()
                                   if k[0] == t and not same(c, w))
        print(f"\n== {t}: {sum(rows.values())} differing cells in {len(rows)} rows")
        for rid, n in sorted(rows.items()):
            label = ""
            if t == "Teams":
                label = teams[rid].get("Name", "")
            elif t == "Players":
                r = csvs[t][1][rid]
                label = f"{r.get('First_Name', '')} {r.get('Last_Name', '')}".strip()
            print(f"  {rid:>5}  {n:>4}  {label}")
            if args.verbose:
                for (tt, i, col), (c, w) in snap.items():
                    if tt == t and i == rid and not same(c, w):
                        print(f"           {col}: {c!r} -> {w!r}")
        if unmapped[t]:
            print(f"  (not writable by Roster Lab: {', '.join(sorted(unmapped[t]))})")
    return 0


def cmd_apply(args):
    src = resolve_ros(args.roster)
    csvs = load_csvs(args.csv)
    doc = document.RosterDocument(str(src))
    scope, notes = build_scope(args, csvs, doc)
    for n in notes:
        print(n)
    print("scope:", {t: len(ids) for t, ids in scope.items()}, "rows")
    missing = {t: sorted(i for i in ids if i not in csvs[t][1]) for t, ids in scope.items()}
    for t, ids in missing.items():
        if ids:
            raise Fail(f"{t} ids not in the CSV: {ids[:20]}")

    before, unmapped = snapshot(doc, csvs)
    in_scope = lambda k: k[1] in scope.get(k[0], ())  # noqa: E731
    errors, writes = [], 0
    for p in range(PASSES):
        cur = snapshot(doc, csvs)[0] if p else before
        todo = sorted((k for k in cur if in_scope(k) and not same(*cur[k])), key=write_order)
        if not todo:
            break
        print(f"pass {p + 1}: {len(todo)} cells")
        for k in todo:
            t, rid, col = k
            try:
                doc.set(rid, TABLES[t] + col, conv(cur[k][0], cur[k][1]))
                writes += 1
            except Exception as e:
                errors.append(f"{t} {rid} {col} -> {cur[k][1]!r}: {type(e).__name__}: {e}")
        if errors:
            break

    after, _ = snapshot(doc, csvs)
    left = [k for k in after if in_scope(k) and not same(*after[k])]
    spill = [(k, before[k][0], after[k][0]) for k in after
             if not in_scope(k) and before[k][0] != after[k][0]]

    print(f"\ncell writes: {writes}   errors: {len(errors)}   "
          f"in-scope cells still different: {len(left)}")
    for e in errors[:30]:
        print("  ERROR", e)
    for k in left[:30]:
        print("  LEFT ", k, after[k])
    if spill:
        print(f"cells changed OUTSIDE the scope by Roster Lab's own rules: {len(spill)}")
        for k, b, a in spill[:40]:
            print(f"  {k[0]} {k[1]} {k[2]}: {b!r} -> {a!r}")
    for t, cols in unmapped.items():
        if scope.get(t):
            print(f"not written ({t}, Roster Lab cannot write): {', '.join(sorted(cols))}")
    zf, nh = doc.zeroface_records(), doc.name_handle_problems()
    print(f"zero-face records: {len(zf)}   name-handle problems: {len(nh)}")
    for tid in sorted(scope.get("Teams", ())):
        probs = doc.team_problems(tid)
        print(f"team {tid} {doc.get(tid, 'team:Name')}: {doc.get(tid, 'team:PlNum')} players, "
              f"{len(probs)} problems" + "".join(f"\n    {x}" for x in probs[:10]))

    report = {"source": str(src), "csv": str(Path(args.csv)), "scope": {t: sorted(v) for t, v in scope.items()},
              "writes": writes, "errors": errors, "left": [list(map(str, k)) for k in left],
              "outside_scope": [[*map(str, k), repr(b), repr(a)] for k, b, a in spill]}
    if errors or left:
        print("\nNOT SAVED: fix the errors above first.")
        dump(args, report)
        return 1
    if not writes:
        print("\nAlready up to date: the roster matches the CSV for this scope.")
        dump(args, report)
        return 0
    if not args.out:
        print("\nDry run: nothing saved. Add --out NAME to write a roster.")
        dump(args, report)
        return 0

    dst = resolve_ros(args.out, must_exist=False)
    if dst.exists():
        if not args.overwrite:
            raise Fail(f"{dst} exists; pass --overwrite (a .bak copy is made first)")
        bak = dst.with_name(dst.name + ".bak")
        shutil.copy2(dst, bak)
        print(f"backed up {dst.name} -> {bak.name}")

    def confirm(*a, **k):
        print("Roster Lab asks:", " | ".join(str(x) for x in a[:3] if x))
        return bool(args.yes)
    try:
        doc.save_as(str(dst), confirm)
    except document.SaveCancelled as e:
        raise Fail(f"save cancelled at Roster Lab's question {e}. "
                   "Read it above, then rerun with --yes to accept")
    except Exception as e:
        raise Fail(f"Roster Lab refused to save: {e}")

    # verify what is on disk, independently of the in-memory document
    data = dst.read_bytes()
    if int.from_bytes(data[:4], "big") != zlib.crc32(data[4:]):
        raise Fail(f"CRC mismatch in {dst}")
    check = document.RosterDocument(str(dst))
    ondisk, _ = snapshot(check, csvs)
    bad = [k for k in ondisk if in_scope(k) and not same(*ondisk[k])]
    drift = [k for k in ondisk if ondisk[k][0] != after[k][0]]
    report.update(output=str(dst), crc="ok", reread_left=len(bad), reread_drift=len(drift))
    dump(args, report)
    if bad or drift:
        print(f"SAVED BUT VERIFY FAILED: {len(bad)} in-scope cells wrong, {len(drift)} drifted")
        return 1
    print(f"\nsaved {dst}\nCRC ok; reopened and every in-scope cell matches the CSV.")
    if src.resolve() != dst.resolve():
        print(f"source {src.name} left unmodified.")
    return 0


def dump(args, report):
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=1), encoding="utf-8")
        print("report:", args.report)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("diff", "apply"):
        p = sub.add_parser(name)
        p.add_argument("roster", help="source .ROS (a bare name is looked up in the 2K14 Saves folder)")
        p.add_argument("--csv", required=True, help="folder with Players/Teams/Staff/Arenas.csv")
        if name == "diff":
            p.add_argument("-v", "--verbose", action="store_true", help="list every differing cell")
        else:
            g = p.add_argument_group("scope (at least one; combined)")
            g.add_argument("--teams", help="team IDs, e.g. 2,5,15-16: team row + its CSV roster, staff, arena")
            g.add_argument("--rows", action="append", metavar="TABLE:IDS",
                           help="explicit rows, e.g. Players:1360-1361,1437 (repeatable)")
            g.add_argument("--changes", nargs="+", metavar="JSON|DIR",
                           help="checkpoint changes.json files (rows they touch)")
            g.add_argument("--all", action="store_true", help="every row that differs (careful)")
            p.add_argument("--out", help="save to this .ROS name; omit for a dry run")
            p.add_argument("--overwrite", action="store_true", help="allow --out to replace a file (backs it up)")
            p.add_argument("--yes", action="store_true", help="accept Roster Lab's save questions")
            p.add_argument("--report", help="write a JSON report here")
    args = ap.parse_args()
    try:
        load_engines()
        return {"diff": cmd_diff, "apply": cmd_apply}[args.cmd](args)
    except Fail as e:
        print("error:", e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
