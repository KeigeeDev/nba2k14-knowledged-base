#!/usr/bin/env python3
"""Self-contained test suite for the CSV pipeline.

    python .ai/csv/test_rmcsv.py

Generates synthetic RED MC-style exports in every plausible format (we do not
know which one RED MC actually emits) and asserts the pipeline's core safety
property: an untouched file round trips byte-identically, and an edited file
differs ONLY in the cells that were edited.

When you have a real RED MC export, drop it in a folder and run:

    python .ai/csv/test_rmcsv.py --extra <folder-with-real-exports>

Every .csv there is added to the round-trip check. That is the single most
valuable thing you can do to harden this tool.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / ".ai" / "turk"))
import rmcsv  # noqa: E402
import turk as turklib  # noqa: E402

RMCSV = str(HERE / "rmcsv.py")
failures: list[str] = []


def check(cond: bool, label: str) -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")
    if not cond:
        failures.append(label)


def run(*args: str):
    return subprocess.run([sys.executable, RMCSV, *args],
                          capture_output=True, text=True)


ROWS = [
    ["Bryant", "Kobe", "Black Mamba", "24", "0", "0", "1", "0", "0", "0", "977", "0", "1", "1"],
    ["James", "LeBron", "King, James", "6", "0", "0", "1", "0", "0", "0", "978", "0", "3", "2"],
    ["Curry", "Stephen", "Chef", "30", "0", "0", "1", "0", "0", "0", "979", "0", "0", "0"],
    ["O'Neal", "Shaquille", 'The "Diesel"', "34", "0", "0", "1", "0", "0", "0", "980", "0", "4", "3"],
]


def build_fixtures(out: Path) -> list[Path]:
    schema = turklib.Schema("NBA2K14")
    cap = schema.load_caption("Player")
    fields = [cap["fields"][k.lower()] for k in cap["order"][:14]]
    keys = [f["key"] for f in fields]
    caps = [f["caption"] for f in fields]

    def write(name, header, rows, delim, term, enc, bom=b"", quote_all=False):
        def cell(v):
            need = quote_all or any(c in v for c in (delim, '"', "\r", "\n"))
            return '"' + v.replace('"', '""') + '"' if need else v
        body = term.join(delim.join(cell(c) for c in r)
                         for r in [header] + rows) + term
        p = out / name
        p.write_bytes(bom + body.encode(enc))
        return p

    made = [
        write("keys_comma_crlf.csv", keys, ROWS, ",", "\r\n", "cp1252"),
        write("caps_semicolon_crlf.csv", caps, ROWS, ";", "\r\n", "cp1252"),
        write("keys_tab_lf.csv", keys, ROWS, "\t", "\n", "utf-8"),
        write("keys_comma_bom_quoted.csv", keys, ROWS, ",", "\r\n", "utf-8",
              b"\xef\xbb\xbf", quote_all=True),
        write("keys_comma_utf16.csv", keys, ROWS, ",", "\r\n", "utf-16-le",
              b"\xff\xfe"),
    ]
    tricky = [r[:] for r in ROWS]
    tricky[0][2] = "Black\nMamba"
    made.append(write("embedded_newline.csv", keys, tricky, ",", "\r\n", "cp1252"))

    bad = [r[:] for r in ROWS]
    bad[1][10] = bad[0][10]      # duplicate ASA_ID
    bad[2][3] = "twenty"         # text in a numeric column
    made.append(write("bad_data.csv", keys, bad + [["Short", "Row"]], ",",
                      "\r\n", "cp1252"))
    return made


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", help="folder of real RED MC exports to include")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        fixtures = build_fixtures(tmp)
        extra = sorted(Path(args.extra).glob("*.csv")) if args.extra else []

        print("== 1. untouched round trip is byte-identical ==")
        for f in fixtures + extra:
            c = rmcsv.CsvFile(f)
            check(c.to_bytes() == f.read_bytes(), f"{f.name}: {c.describe()}")

        print("\n== 2. detection identifies the table from headers ==")
        for f in fixtures:
            c = rmcsv.CsvFile(f)
            m = rmcsv.Mapping(turklib.Schema("NBA2K14"), c.header)
            check(m.stem == "Player" and not m.unmapped,
                  f"{f.name}: {m.table} ({len(m.cols)}/{len(c.header)} columns)")

        print("\n== 3. edit touches only the targeted cells ==")
        cases = [
            ("keys_comma_crlf.csv", "ID2", "ID2+100", "Pos >= 3"),
            ("keys_comma_bom_quoted.csv", "NickName", "'X'", "IsRegular == 1"),
            ("keys_comma_utf16.csv", "ID2", "0", None),
            ("keys_tab_lf.csv", "ID2", "ID2*2", "Pos == 0"),
            ("caps_semicolon_crlf.csv", "ID2", "7", "Pos >= 1"),
            ("embedded_newline.csv", "ID2", "ID2+1", "Pos >= 3"),
        ]
        for name, field, expr, where in cases:
            src, out = tmp / name, tmp / f"edited_{name}"
            cmd = ["edit", str(src), "--set", f"{field}={expr}",
                   "--out", str(out), "--force"]
            if where:
                cmd += ["--where", where]
            r = run(*cmd)
            if r.returncode != 0:
                check(False, f"{name}: edit failed -- {r.stderr.strip()[:120]}")
                continue
            a, b = rmcsv.CsvFile(src), rmcsv.CsvFile(out)
            check(a.encoding == b.encoding and a.bom == b.bom
                  and a.delim == b.delim and a.terms == b.terms,
                  f"{name}: encoding/BOM/delimiter/line-endings preserved")
            check(a.header == b.header and len(a.rows) == len(b.rows),
                  f"{name}: header and row count preserved")
            col = next(i for i, h in enumerate(a.header)
                       if h.strip().lower() == field.lower()
                       or rmcsv._norm(h) == rmcsv._norm(field))
            stray = [(r_i, c_i)
                     for r_i in range(len(a.rows))
                     for c_i in range(len(a.rows[r_i]))
                     if c_i != col and a.rows[r_i][c_i] != b.rows[r_i][c_i]]
            check(not stray, f"{name}: no collateral change outside {field}"
                  + (f" -- {stray[:3]}" if stray else ""))

        print("\n== 4. validation catches known-bad data ==")
        r = run("validate", str(tmp / "bad_data.csv"))
        check(r.returncode == 1, "bad_data.csv fails validation")
        check("duplicate ASA_ID" in r.stdout, "duplicate ASA_ID reported")
        check("non-numeric" in r.stdout, "text in a numeric column reported")
        check("2 cells, header has 14" in r.stdout, "short row reported")
        r = run("validate", str(tmp / "keys_comma_crlf.csv"))
        check(r.returncode == 0 and "0 error(s)" in r.stdout,
              "clean file passes with no false positives")

        print("\n== 5. range guard (only 3 Player fields document a range) ==")
        ranged = tmp / "ranged.csv"
        ranged.write_bytes("Last_Name,First_Name,Loyalty\r\n"
                           "Bryant,Kobe,80\r\nJames,LeBron,60\r\n".encode("cp1252"))
        r = run("edit", str(ranged), "--set", "Loyalty=150", "--dry-run")
        check(r.returncode == 2 and "outside" in r.stderr,
              "out-of-range refused without --force")
        r = run("edit", str(ranged), "--set", "Loyalty=150", "--dry-run", "--force")
        check(r.returncode == 0 and "warning" in r.stdout,
              "--force allows it but warns")
        r = run("edit", str(ranged), "--set", "Loyalty=95", "--dry-run")
        check(r.returncode == 0, "in-range value accepted")

        print("\n== 6. expression sandbox ==")
        for expr, label in [
            ("__import__('os').system('echo pwned')", "dunder/import blocked"),
            ("open('x','w')", "open() blocked"),
            ("(1).__class__", "attribute access blocked"),
        ]:
            r = run("edit", str(ranged), "--set", f"Loyalty={expr}", "--dry-run")
            check(r.returncode != 0 and "pwned" not in r.stdout, label)

    print()
    if failures:
        print(f"{len(failures)} FAILURE(S):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
