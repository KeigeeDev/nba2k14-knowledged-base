"""NBA 2K .n2km model helpers (format written by the io_n2km Blender add-on / 3DM Tool).

Format:
    b"2KM\\0"  int32 partCount  int32 20
    per part: char[8] name | int32 nVerts | nVerts x (f32 x, f32 y, f32 z, f32 u, f32 v)
              int32 nFaces | nFaces x (u16 a, u16 b, u16 c)
Stored axes = Blender (x, z, -y).

CLI (pure standard library):
    python n2km_tools.py info   model.n2km
    python n2km_tools.py compare original.n2km edited.n2km
compare = the pre-3DM-Tool safety check: same parts, same vert/face counts, identical faces & UVs.
"""
import struct
import sys


def parse(path):
    b = open(path, "rb").read()
    if b[:3] != b"2KM":
        raise ValueError(f"{path}: not an n2km file")
    n, _ = struct.unpack_from("<ii", b, 4)
    o = 12
    parts = {}
    for _ in range(n):
        name = b[o:o + 8].split(b"\0")[0].decode(); o += 8
        nv, = struct.unpack_from("<i", b, o); o += 4
        verts = [struct.unpack_from("<5f", b, o + 20 * i) for i in range(nv)]; o += 20 * nv
        nf, = struct.unpack_from("<i", b, o); o += 4
        faces = [struct.unpack_from("<3H", b, o + 6 * i) for i in range(nf)]; o += 6 * nf
        parts[name] = (verts, faces)
    return parts, len(b)


def _key(name):
    try:
        return int(name.split("-")[1])
    except (IndexError, ValueError):
        return 999


def info(path):
    parts, size = parse(path)
    print(f"{path}: {size} bytes, {len(parts)} parts")
    for k in sorted(parts, key=_key):
        v, f = parts[k]
        print(f"  {k:6s} verts={len(v):5d} faces={len(f):5d}")


def compare(orig, edit):
    """Return True if safe for the 3DM Tool (only positions differ)."""
    A, la = parse(orig)
    B, lb = parse(edit)
    ok = set(A) == set(B)
    print(f"size {la} vs {lb}; parts match: {ok}")
    for k in sorted(A, key=_key):
        if k not in B:
            print(f"  {k}: MISSING in edit"); ok = False; continue
        va, fa = A[k]; vb, fb = B[k]
        same_n = len(va) == len(vb) and len(fa) == len(fb)
        same_f = fa == fb
        mv = max((max(abs(x - y) for x, y in zip(p[:3], q[:3])) for p, q in zip(va, vb)), default=0)
        uv = max((max(abs(x - y) for x, y in zip(p[3:], q[3:])) for p, q in zip(va, vb)), default=0)
        flag = "OK" if (same_n and same_f and uv < 1e-4) else "FAIL"
        ok &= flag == "OK"
        print(f"  {k:6s} {flag}  verts {len(va)}/{len(vb)} faces {len(fa)}/{len(fb)} "
              f"faces_same={same_f} max_move={mv:.2f} uv_diff={uv:.6f}")
    print("RESULT:", "SAFE to import" if ok else "DO NOT IMPORT")
    return ok


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "info":
        info(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "compare":
        sys.exit(0 if compare(sys.argv[2], sys.argv[3]) else 1)
    else:
        print(__doc__); sys.exit(1)
