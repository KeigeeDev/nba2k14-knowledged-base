"""DDS helpers for NBA 2K14 cyberface textures.

Handles UNCOMPRESSED 32-bit A8R8G8B8 DDS (e.g. hair.dds) read + write, and prints the header of any DDS.
DXT1/DXT5 (face_color, skin_colour) are only identified, not encoded — convert those with NVIDIA tools/Photoshop.
Blender can *read* DXT files itself (bpy.data.images.load) but NOT uncompressed A8R8G8B8 — use read_argb() for those.

Pure standard library. numpy helpers (to_numpy / from_numpy) only work where numpy exists (inside Blender).

CLI:
    python dds_tools.py info file.dds [...]
"""
import struct
import sys

HEADER_SIZE = 128  # "DDS " magic (4) + DDS_HEADER (124)


def info(path):
    """Return a dict describing a DDS file's header."""
    b = open(path, "rb").read(HEADER_SIZE)
    if b[:4] != b"DDS ":
        raise ValueError(f"{path}: not a DDS file")
    h, w = struct.unpack_from("<II", b, 12)
    pitch, = struct.unpack_from("<I", b, 20)
    mips, = struct.unpack_from("<I", b, 28)
    pf_flags, = struct.unpack_from("<I", b, 80)
    fourcc = b[84:88]
    bits, = struct.unpack_from("<I", b, 88)
    masks = struct.unpack_from("<4I", b, 92)
    if pf_flags & 0x4:
        fmt = fourcc.decode("ascii", "replace")
    elif bits == 32 and masks == (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000):
        fmt = "A8R8G8B8"
    else:
        fmt = f"uncompressed {bits}bpp masks={tuple(hex(m) for m in masks)}"
    return {"width": w, "height": h, "pitch": pitch, "mips": mips, "format": fmt}


def read_argb(path):
    """Read an A8R8G8B8 DDS. Returns (width, height, header_bytes, rgba_bytes).

    rgba_bytes: top row first, 4 bytes per pixel in R,G,B,A order.
    """
    d = info(path)
    if d["format"] != "A8R8G8B8":
        raise ValueError(f"{path}: format {d['format']} — only A8R8G8B8 supported")
    data = open(path, "rb").read()
    w, h = d["width"], d["height"]
    bgra = data[HEADER_SIZE:HEADER_SIZE + w * h * 4]
    rgba = bytearray(len(bgra))
    rgba[0::4] = bgra[2::4]; rgba[1::4] = bgra[1::4]; rgba[2::4] = bgra[0::4]; rgba[3::4] = bgra[3::4]
    return w, h, data[:HEADER_SIZE], bytes(rgba)


def write_argb(path, width, height, rgba_bytes, template_header):
    """Write an A8R8G8B8 DDS.

    rgba_bytes: top row first, R,G,B,A bytes. template_header: the 128-byte header of the ORIGINAL game file
    (keeps flags/masks exactly as the game expects); only size + pitch are patched. No mipmaps (as in 2K14 hair).
    """
    hd = bytearray(template_header[:HEADER_SIZE])
    struct.pack_into("<II", hd, 12, height, width)
    # 2K14's own files leave pitch = 0; only fill it in if the template did
    if struct.unpack_from("<I", hd, 20)[0] != 0:
        struct.pack_into("<I", hd, 20, width * 4)
    rgba = bytes(rgba_bytes)
    if len(rgba) != width * height * 4:
        raise ValueError("pixel data size mismatch")
    bgra = bytearray(len(rgba))
    bgra[0::4] = rgba[2::4]; bgra[1::4] = rgba[1::4]; bgra[2::4] = rgba[0::4]; bgra[3::4] = rgba[3::4]
    with open(path, "wb") as f:
        f.write(bytes(hd) + bytes(bgra))


# ---- numpy helpers (Blender) -------------------------------------------------------------------
def to_numpy(rgba_bytes, width, height):
    """-> float32 array (H, W, 4), top-down, 0..1."""
    import numpy as np
    return np.frombuffer(rgba_bytes, np.uint8).reshape(height, width, 4).astype(np.float32) / 255.0


def from_numpy(arr):
    """float array (H, W, 4) top-down 0..1 -> rgba bytes."""
    import numpy as np
    return (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()


def to_blender_image(arr, name):
    """Top-down float RGBA array -> packed bpy image (Blender stores rows bottom-up)."""
    import bpy
    import numpy as np
    h, w, _ = arr.shape
    im = bpy.data.images.get(name) or bpy.data.images.new(name, w, h, alpha=True)
    if tuple(im.size) != (w, h):
        im.scale(w, h)
    im.pixels.foreach_set(np.ascontiguousarray(arr[::-1]).astype(np.float32).ravel())
    return im


def from_blender_image(im):
    """bpy image -> top-down float RGBA array."""
    import numpy as np
    w, h = im.size
    return np.array(im.pixels[:], np.float32).reshape(h, w, 4)[::-1].copy()


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "info":
        print(__doc__); sys.exit(1)
    for p in sys.argv[2:]:
        d = info(p)
        print(f"{p}: {d['width']}x{d['height']} {d['format']} mips={d['mips']} pitch={d['pitch']}")
