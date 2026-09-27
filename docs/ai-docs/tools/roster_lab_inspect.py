"""Inspect the Roster Lab by Q2K install without decompiling it.

Needs the same Python as the build (3.14) - its .pyc files are loaded with
`marshal`, which is version-locked.

    py -3.14 roster_lab_inspect.py modules [OUTDIR]     # one-line summary per module;
                                                        # with OUTDIR, a structure dump each
    py -3.14 roster_lab_inspect.py doc <module>         # full module docstring
    py -3.14 roster_lab_inspect.py consts <module> NAME [NAME ...]
    py -3.14 roster_lab_inspect.py grep <regex>         # search every string constant
    py -3.14 roster_lab_inspect.py schemas              # field counts per *_schema.json

`consts` imports the module, so only use it on data-layer modules (ros_*,
document, backups, fdc ...), never on UI modules.
"""

import dis
import glob
import json
import marshal
import os
import pprint
import re
import sys
import types

ROOT = os.environ.get("ROSTER_LAB", r"C:\Editing Tools\Roster Lab by Q2K")
SRC = os.path.join(ROOT, "_internal")


def app_modules():
    std = sys.stdlib_module_names
    return sorted(f[:-4] for f in os.listdir(SRC)
                  if f.endswith(".pyc") and f[:-4] not in std and not f.startswith("_"))


def load(mod):
    with open(os.path.join(SRC, mod + ".pyc"), "rb") as fh:
        fh.read(16)
        return marshal.load(fh)


def docstring(co):
    c = co.co_consts
    return c[0] if c and isinstance(c[0], str) else ""


def walk(co, depth=0):
    for c in co.co_consts:
        if isinstance(c, types.CodeType):
            args = c.co_varnames[:c.co_argcount + c.co_kwonlyargcount]
            yield depth, c, args
            yield from walk(c, depth + 1)


def imports(co):
    found = {i.argval for i in dis.get_instructions(co) if i.opname == "IMPORT_NAME"}
    for _, c, _ in walk(co):
        found |= {i.argval for i in dis.get_instructions(c) if i.opname == "IMPORT_NAME"}
    return found


def strings(co):
    out = [k for k in co.co_consts if isinstance(k, str)]
    for _, c, _ in walk(co):
        out += [k for k in c.co_consts if isinstance(k, str)]
    return out


def cmd_modules(outdir=None):
    mods = app_modules()
    for m in mods:
        co = load(m)
        first = docstring(co).strip().split("\n")[0][:110]
        deps = sorted(i for i in imports(co) if i.split(".")[0] in mods)
        print(f"{m:20s} {first}\n{'':20s} -> {deps}")
        if outdir:
            os.makedirs(outdir, exist_ok=True)
            lines = [f"# {m} ({co.co_filename})", "", docstring(co), ""]
            for depth, c, args in walk(co):
                lines.append("  " * depth + f"{c.co_qualname}({', '.join(args)})  L{c.co_firstlineno}")
            with open(os.path.join(outdir, m + ".txt"), "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))


def cmd_consts(mod, *names):
    sys.path.insert(0, SRC)
    sys.dont_write_bytecode = True
    m = __import__(mod)
    for n in names:
        print(f"--- {n}")
        pprint.pprint(getattr(m, n), width=120, compact=True)


def cmd_grep(pattern):
    pat = re.compile(pattern, re.I)
    for m in app_modules():
        hits = sorted({s for s in strings(load(m)) if pat.search(s)})
        if hits:
            print(m, "->", [h[:160] for h in hits][:12])


def cmd_schemas():
    for f in sorted(glob.glob(os.path.join(SRC, "*_schema.json"))):
        d = json.load(open(f, encoding="utf-8"))
        fields = d.get("fields", {})
        unc = sum(1 for v in fields.values() if {"bmin", "wmax", "wmin"} & set(v))
        print(f"{os.path.basename(f):28s} stamp={d.get('stamp')} bits={d.get('record_bits')} "
              f"fields={len(fields)} uncertain={unc} handles={len(d.get('handles', {}))}")


def main(argv):
    if not argv:
        print(__doc__)
        return
    cmd, rest = argv[0], argv[1:]
    if cmd == "modules":
        cmd_modules(*rest[:1])
    elif cmd == "doc":
        print(docstring(load(rest[0])))
    elif cmd == "consts":
        cmd_consts(*rest)
    elif cmd == "grep":
        cmd_grep(rest[0])
    elif cmd == "schemas":
        cmd_schemas()
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
