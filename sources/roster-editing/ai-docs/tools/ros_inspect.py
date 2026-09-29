#!/usr/bin/env python3
"""
ros_inspect.py - Inspector for NBA 2K14 PC roster (.ROS) files.

Verified against RED MC 5.0-compatible rosters (all files 2,672,672 bytes).

Capabilities:
  * Verify / recompute the header CRC32 (allows re-signing externally modified files)
  * Dump the table directory (table id, struct-type hash, value)
  * Scan the bit-packed data area for UTF-16BE string pools (player first/last
    names, city names) and dump them
  * Bit-level diff of two .ROS files (for differential reverse engineering:
    change ONE field in RED MC, save, then diff to locate the field's bit offset)

Usage:
  python ros_inspect.py header  <file.ros>
  python ros_inspect.py names   <file.ros>
  python ros_inspect.py resign  <file.ros>            (fix CRC in place)
  python ros_inspect.py bitdiff <a.ros> <b.ros>       (list differing bit runs)
  python ros_inspect.py player  <file.ros> <year> <month> <day>
        Find player record(s) by birthdate; prints slot id, jersey number,
        team ref (offsets per ai-docs/06-player-record-map.md)
  python ros_inspect.py dump    <file.ros> <year> <month> <day>
        Full decode of a player: height/weight (float32), position,
        play style, jersey, team, and the 42 skill ratings

All multi-byte integers in the file are BIG-ENDIAN (console heritage).
"""
import struct
import sys
import zlib

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MAGIC = 0x501551AE  # bytes 0x04..0x07 of every known .ROS


def load(path):
    with open(path, "rb") as f:
        return f.read()


def crc_of(data):
    """Header CRC = CRC32 (zlib polynomial) of bytes 4..EOF, stored big-endian at 0x00."""
    return zlib.crc32(data[4:]) & 0xFFFFFFFF


def cmd_header(path):
    d = load(path)
    stored_crc, magic, version, fsize = struct.unpack_from(">IIII", d, 0)
    used = struct.unpack_from(">I", d, 0x18)[0]
    print(f"file            : {path} ({len(d)} bytes)")
    print(f"crc32 stored    : {stored_crc:08X}  computed: {crc_of(d):08X}  "
          f"{'OK' if stored_crc == crc_of(d) else 'MISMATCH'}")
    print(f"magic           : {magic:08X}  {'OK' if magic == MAGIC else 'UNEXPECTED'}")
    print(f"version         : {version}")
    print(f"file size field : {fsize} ({'OK' if fsize == len(d) else 'MISMATCH'})")
    print(f"used size @0x18 : {used}")
    # 45 entries {id, hash, value} at 0x24..0x240. The hash belongs to the
    # entry's own section, but `value` is the record count of the NEXT
    # section; section 0x0101's count is the word at 0x20. The stamp comes
    # from the position: the id word is wrong for the empty 0x0129/0x012A.
    # See ai-docs/02-ros-format.md.
    print("\nsections (stamp by position; hash from own entry, count from previous):")
    count = struct.unpack_from(">I", d, 0x20)[0]
    for k in range((0x240 - 0x24) // 12 + 1):
        off = 0x24 + 12 * k
        a, h, v = struct.unpack_from(">III", d, off)
        stamp = 0x0101 + k
        note = "" if a >> 16 == stamp else f"  (id word reads 0x{a >> 16:04X})"
        print(f"  0x{off:04X}  stamp=0x{stamp:04X}  struct=0x{h:08X}  count={count}{note}")
        count = v
    wm_a, wm_b = struct.unpack_from(">II", d, 0x250)
    print(f"heap next-free handles: [012F] 0x{wm_a:04X}  [0130] 0x{wm_b:04X}")
    print("bitstream starts at byte 0x26C (bit 4960) with section 0x0102")


def bitstream(d):
    return "".join(f"{b:08b}" for b in d)


def cmd_names(path):
    """Extract UTF-16BE null-terminated string pools from the bit-packed tail."""
    d = load(path)
    bits = bitstream(d)
    # Pools observed in the last ~15% of the file at a constant bit phase.
    # Heuristic: slide 16-bit windows at each of 8 phases; collect runs of
    # printable UTF-16BE chars terminated by 0x0000.
    start_byte = int(len(d) * 0.80)
    found = []
    for phase in range(8):
        pos = start_byte * 8 + phase
        run = []
        while pos + 16 <= len(bits):
            v = int(bits[pos:pos + 16], 2)
            if 0x20 <= v < 0x180 and v != 0x7F:  # Latin-1 + Latin Extended-A
                run.append(chr(v))
            elif v == 0 and run:
                s = "".join(run)
                if 2 <= len(s) <= 24 and any(c.isalpha() for c in s):
                    found.append((pos // 8, phase, s))
                run = []
            else:
                run = []
            pos += 16
    for byte_off, phase, s in found:
        print(f"0x{byte_off:06X} +{phase}  {s}")
    print(f"# {len(found)} strings", file=sys.stderr)


def cmd_resign(path):
    d = bytearray(load(path))
    old = struct.unpack_from(">I", d, 0)[0]
    new = crc_of(bytes(d))
    struct.pack_into(">I", d, 0, new)
    with open(path, "wb") as f:
        f.write(d)
    print(f"crc {old:08X} -> {new:08X} written")


def cmd_bitdiff(pa, pb):
    a, b = load(pa), load(pb)
    if len(a) != len(b):
        print(f"sizes differ: {len(a)} vs {len(b)}")
        return
    ba, bb = bitstream(a), bitstream(b)
    run_start = None
    runs = 0
    for i in range(len(ba)):
        if ba[i] != bb[i]:
            if run_start is None:
                run_start = i
        elif run_start is not None:
            print(f"bits {run_start}..{i - 1}  (byte 0x{run_start // 8:06X}+{run_start % 8}, "
                  f"len {i - run_start})")
            run_start = None
            runs += 1
            if runs > 500:
                print("... (truncated, >500 runs)")
                return
    if run_start is not None:
        print(f"bits {run_start}..{len(ba) - 1}")


PLAYER_STRIDE = 3644  # bits per player record (verified)

# Field offsets relative to the BirthYear anchor (see ai-docs/06-player-record-map.md)
FLD = {
    "slot_id":   (-253, 12, "uint"),
    "height_cm": (-145, 32, "f32"),
    "weight_lb": (-113, 32, "f32"),
    "team_ref":   (-56,  7, "uint"),
    "birth_year":   (0, 11, "uint"),
    "birth_month": (11,  4, "uint"),
    "birth_day":   (15,  5, "uint"),
    "jersey":      (28,  7, "uint"),   # record bit 301
    "position":   (183,  3, "uint"),
    "play_style":(1181,  5, "uint"),
}
RATINGS_OFF, RATINGS_N = 2571, 42   # 8-bit each, raw = 3 * (displayed - 25)
POSITIONS = ["PG", "SG", "SF", "PF", "C"]


def _bitval(bits, pos, width, kind):
    raw = int(bits[pos:pos + width], 2)
    if kind == "f32":
        return struct.unpack(">f", raw.to_bytes(4, "big"))[0]
    return raw


def player_anchor(bits, slot, ref_anchor, ref_slot):
    return ref_anchor + (slot - ref_slot) * PLAYER_STRIDE


def find_anchor_by_birthdate(bits, year, month, day):
    """Return every bit position whose y/m/d field matches."""
    pat = f"{year:011b}{month:04b}{day:05b}"
    out, p = [], bits.find(pat)
    while p >= 0:
        out.append(p)
        p = bits.find(pat, p + 1)
    return out


def decode_player(bits, anchor):
    rec = {}
    for name, (off, w, kind) in FLD.items():
        rec[name] = _bitval(bits, anchor + off, w, kind)
    rec["ratings"] = [
        int(bits[anchor + RATINGS_OFF + 8 * i: anchor + RATINGS_OFF + 8 * i + 8], 2) // 3 + 25
        for i in range(RATINGS_N)
    ]
    return rec


def cmd_dump(path, year, month, day):
    """Decode every verified field of the player(s) with this birthdate."""
    bits = bitstream(load(path))
    hits = find_anchor_by_birthdate(bits, year, month, day)
    if not hits:
        print("no player with that birthdate")
        return
    for anchor in hits:
        r = decode_player(bits, anchor)
        # sanity gate: reject coincidental matches in non-player tables
        if not (150.0 <= r["height_cm"] <= 240.0 and 100.0 <= r["weight_lb"] <= 400.0):
            continue
        inches = r["height_cm"] / 2.54
        pos = POSITIONS[r["position"]] if r["position"] < 5 else r["position"]
        print(f"--- anchor bit {anchor} (byte 0x{anchor // 8:06X}+{anchor % 8})")
        print(f"  slot id    : {r['slot_id']}")
        print(f"  born       : {r['birth_year']}-{r['birth_month']:02d}-{r['birth_day']:02d}")
        print(f"  height     : {r['height_cm']:.2f} cm "
              f"({int(inches // 12)}'{inches - 12 * (inches // 12):.2f}\")")
        print(f"  weight     : {r['weight_lb']:.1f} lb")
        print(f"  position   : {pos}   jersey: {r['jersey']}   team ref: {r['team_ref']}")
        print(f"  play style : {r['play_style']} (index into the PlayStyle enum)")
        print(f"  ratings    : {r['ratings']}")


def cmd_player(path, year, month, day):
    """Find player record(s) by birthdate; decode verified nearby fields.

    Anchor = first bit of the 11-bit BirthYear field (storage order y,m,d).
    Verified relative offsets (ai-docs/06-player-record-map.md):
      ID/slot index @ anchor-253 (12 bits), jersey @ anchor+28 (7 bits),
      team ref @ anchor-56 (7 bits).
    """
    d = load(path)
    bits = bitstream(d)
    pat = f"{year:011b}{month:04b}{day:05b}"
    p = bits.find(pat)
    found = 0
    while p >= 0:
        slot   = int(bits[p - 253:p - 241], 2)
        jersey = int(bits[p + 27:p + 35], 2)
        team   = int(bits[p - 56:p - 49], 2)
        print(f"anchor bit {p} (byte 0x{p // 8:06X}+{p % 8})  "
              f"slot_id={slot}  jersey={jersey}  team_ref={team}")
        found += 1
        p = bits.find(pat, p + 1)
    if not found:
        print("no record with that birthdate (note: only checks y/m/d "
              "storage order; verify values)")
    else:
        print("# caution: birthdate patterns can also match non-player "
              "tables; trust hits that come with sane slot/jersey values",
              file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "header":
        cmd_header(sys.argv[2])
    elif cmd == "names":
        cmd_names(sys.argv[2])
    elif cmd == "resign":
        cmd_resign(sys.argv[2])
    elif cmd == "bitdiff":
        cmd_bitdiff(sys.argv[2], sys.argv[3])
    elif cmd == "player":
        cmd_player(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    elif cmd == "dump":
        cmd_dump(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    else:
        print(__doc__)
        sys.exit(1)
