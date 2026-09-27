"""Reusable Blender-side helpers for NBA 2K14 cyberface work via Blender MCP.

Load inside Blender (execute_blender_code):
    import sys, importlib
    p = r"C:\\2K Modding\\Cyberface\\scripts"
    sys.path.append(p) if p not in sys.path else None
    import cf_blender, dds_tools; importlib.reload(cf_blender); importlib.reload(dds_tools)

Conventions: model faces -Y, Z up, +X = character's left. Photos are handled as top-down float arrays.
See guides/ for when to use each function.
"""
import math
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler

VIEWS = {'FRONT': (90, 0, 0), 'RIGHT': (90, 0, 90), 'LEFT': (90, 0, -90), 'BACK': (90, 0, 180),
         'Q34': (90, 0, 35), 'Q34L': (90, 0, -35), 'TOP': (0, 0, 0)}


# ---- screenshots -------------------------------------------------------------------------------
def snap(path, view='FRONT', center=(0, 0, 30), ortho=60, W=600, H=600, shading='TEXTURE', xray=None):
    """Offscreen ortho render of the 3D viewport to PNG (then Read the PNG).

    shading: 'TEXTURE' | 'SINGLE' | 'MATERIAL' (MATERIAL shows alpha, e.g. hair).
    Needed because MCP get_viewport_screenshot uses a stale view matrix when Blender isn't redrawing.
    """
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    sp = area.spaces.active; reg = next(r for r in area.regions if r.type == 'WINDOW'); r3 = sp.region_3d
    if shading == 'MATERIAL':
        sp.shading.type = 'MATERIAL'
    else:
        sp.shading.type = 'SOLID'; sp.shading.color_type = shading
    if xray is not None:
        sp.shading.show_xray = bool(xray)
    q = Euler([math.radians(a) for a in VIEWS[view]]).to_quaternion()
    r3.view_perspective = 'ORTHO'; r3.view_rotation = q; r3.view_location = Vector(center); r3.view_distance = 150
    cam = Matrix.Translation(Vector(center) + (q.to_matrix() @ Vector((0, 0, 1))) * 150) @ q.to_matrix().to_4x4()
    vm = cam.inverted(); r3.view_matrix = vm
    h = ortho / 2; n, f = 1, 400; a = W / H
    pm = Matrix(((1 / (h * a if a > 1 else h), 0, 0, 0), (0, 1 / (h if a > 1 else h / a), 0, 0),
                 (0, 0, -2 / (f - n), -(f + n) / (f - n)), (0, 0, 0, 1)))
    bpy.context.view_layer.update()
    import gpu
    off = gpu.types.GPUOffScreen(W, H)
    try:
        off.draw_view3d(bpy.context.scene, bpy.context.view_layer, sp, reg, vm, pm, do_color_management=True)
        buf = off.texture_color.read()
    finally:
        off.free()
    buf.dimensions = W * H * 4
    im = bpy.data.images.new('_cf_snap', W, H, alpha=True)
    im.pixels.foreach_set((np.asarray(buf, dtype=np.float32) / 255.0).ravel())
    im.filepath_raw = path; im.file_format = 'PNG'; im.save(); bpy.data.images.remove(im)
    return path


# ---- images ------------------------------------------------------------------------------------
def image_array(name_or_image, rgb_only=True):
    """bpy image -> top-down float array (H,W,3|4)."""
    im = bpy.data.images[name_or_image] if isinstance(name_or_image, str) else name_or_image
    w, h = im.size
    a = np.array(im.pixels[:], np.float32).reshape(h, w, 4)[::-1].copy()
    return a[:, :, :3] if rgb_only else a


def bilinear(A, px, py):
    """Sample array A (H,W,C) at float pixel coords (top-down)."""
    h, w = A.shape[:2]
    px = np.clip(px, 0, w - 1.001); py = np.clip(py, 0, h - 1.001)
    x0 = px.astype(int); y0 = py.astype(int); fx = (px - x0)[..., None]; fy = (py - y0)[..., None]
    return (A[y0, x0] * (1 - fx) * (1 - fy) + A[y0, x0 + 1] * fx * (1 - fy)
            + A[y0 + 1, x0] * (1 - fx) * fy + A[y0 + 1, x0 + 1] * fx * fy)


def blur(m, n):
    """n passes of a 5-point box blur (feathering masks/weights)."""
    m = m.astype(np.float32)
    for _ in range(n):
        m = (m + np.roll(m, 1, 0) + np.roll(m, -1, 0) + np.roll(m, 1, 1) + np.roll(m, -1, 1)) / 5
    return m


def erode(m, n):
    for _ in range(n):
        m = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    return m


def person_mask(A, bg=None, thr=0.12, erode_px=4, exclude_blue=True):
    """Mask of subject pixels on a flat studio background (optionally drops blue shirt pixels)."""
    if bg is None:
        bg = np.median(np.concatenate([A[:40, :40].reshape(-1, 3), A[:40, -40:].reshape(-1, 3)]), axis=0)
    m = np.abs(A - bg).max(2) > thr
    if exclude_blue:
        shirt = blur((A[:, :, 2] > A[:, :, 0] + 0.04) & (A[:, :, 2] > A[:, :, 1]), 4) > 0.02
        m &= ~shirt
    return erode(m, erode_px)


# ---- landmark warp -----------------------------------------------------------------------------
def tps_fit(src, dst, reg=0.5):
    """Thin-plate spline 2D->2D. Returns f(points Nx2)->Nx2. Used for model (x,z)/(y,z) -> photo px."""
    src = np.asarray(src, float); dst = np.asarray(dst, float); n = len(src)
    d = np.linalg.norm(src[:, None] - src[None], axis=2)
    K = np.where(d > 0, d * d * np.log(d + 1e-12), 0) + reg * np.eye(n)
    P = np.hstack([np.ones((n, 1)), src])
    A = np.zeros((n + 3, n + 3)); A[:n, :n] = K; A[:n, n:] = P; A[n:, :n] = P.T
    b = np.zeros((n + 3, 2)); b[:n] = dst
    w = np.linalg.solve(A, b)

    def f(q):
        q = np.asarray(q, float); dd = np.linalg.norm(q[:, None] - src[None], axis=2)
        U = np.where(dd > 0, dd * dd * np.log(dd + 1e-12), 0)
        return U @ w[:n] + w[n] + q @ w[n + 1:]
    return f


# ---- geometry → texture ------------------------------------------------------------------------
def raster_uv(obj, size, component_filter=None, eps=0.02):
    """Map every texel of obj's UV layout to surface position + normal.

    Returns POS (S,S,3), NRM (S,S,3), COV (S,S bool); arrays are BOTTOM-UP rows (Blender pixel order).
    component_filter: optional callable(vertex_indices)->bool to keep only some triangles.
    """
    me = obj.data; me.calc_loop_triangles(); S = size
    co = np.array([v.co[:] for v in me.vertices]); vn = np.array([v.normal[:] for v in me.vertices])
    uvl = np.zeros((len(me.loops), 2)); me.uv_layers[0].data.foreach_get('uv', uvl.ravel())
    POS = np.zeros((S, S, 3), np.float32); NRM = np.zeros((S, S, 3), np.float32); COV = np.zeros((S, S), bool)
    for t in me.loop_triangles:
        vs = list(t.vertices)
        if component_filter and not component_filter(vs):
            continue
        p = uvl[list(t.loops)] * S - 0.5
        x0, y0 = np.floor(p.min(0)).astype(int); x1, y1 = np.ceil(p.max(0)).astype(int)
        X, Y = np.meshgrid(np.arange(max(x0, 0), min(x1, S - 1) + 1), np.arange(max(y0, 0), min(y1, S - 1) + 1))
        a, b, c = p; den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-12 or X.size == 0:
            continue
        l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / den
        l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / den
        l3 = 1 - l1 - l2
        m = (l1 >= -eps) & (l2 >= -eps) & (l3 >= -eps)
        if not m.any():
            continue
        L = np.stack([l1[m], l2[m], l3[m]], 1)
        POS[Y[m], X[m]] = L @ co[vs]; NRM[Y[m], X[m]] = L @ vn[vs]; COV[Y[m], X[m]] = True
    NRM /= np.maximum(np.linalg.norm(NRM, axis=2, keepdims=True), 1e-6)
    return POS, NRM, COV


def depth_map(obj, axes, depth_axis, nearest_is_min, res=0.1, rng=((-36, 36), (-12, 66))):
    """Rasterise obj into a 2D grid over `axes`, keeping the nearest depth along depth_axis.

    Front view: axes=(0,2), depth_axis=1, nearest_is_min=True (min y).
    +X side:   axes=(1,2), depth_axis=0, nearest_is_min=False; -X side: nearest_is_min=True.
    Returns (grid, (a0, b0, res)).
    """
    me = obj.data; me.calc_loop_triangles()
    co = np.array([v.co[:] for v in me.vertices])
    (a0, a1), (b0, b1) = rng; W = int((a1 - a0) / res) + 1; H = int((b1 - b0) / res) + 1
    D = np.full((H, W), np.inf if nearest_is_min else -np.inf, np.float32)
    for t in me.loop_triangles:
        P = co[list(t.vertices)]
        q = np.stack([(P[:, axes[0]] - a0) / res, (P[:, axes[1]] - b0) / res], 1); dep = P[:, depth_axis]
        x0, y0 = np.floor(q.min(0)).astype(int); x1, y1 = np.ceil(q.max(0)).astype(int)
        X, Y = np.meshgrid(np.arange(max(x0, 0), min(x1, W - 1) + 1), np.arange(max(y0, 0), min(y1, H - 1) + 1))
        a, b, c = q; den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-12 or X.size == 0:
            continue
        l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / den
        l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / den
        m = (l1 >= 0) & (l2 >= 0) & (1 - l1 - l2 >= 0)
        if not m.any():
            continue
        dd = l1[m] * dep[0] + l2[m] * dep[1] + (1 - l1[m] - l2[m]) * dep[2]
        (np.minimum if nearest_is_min else np.maximum).at(D, (Y[m], X[m]), dd)
    return D, (a0, b0, res)


def depth_lookup(dm, a, b):
    D, (a0, b0, res) = dm
    ia = np.clip(np.round((np.asarray(a) - a0) / res).astype(int), 0, D.shape[1] - 1)
    ib = np.clip(np.round((np.asarray(b) - b0) / res).astype(int), 0, D.shape[0] - 1)
    return D[ib, ia]


def dilate(img, cov, px=6):
    """Extend colours px texels past UV island borders (avoids seams at mip levels)."""
    m = cov.copy(); O = img.copy()
    for _ in range(px):
        acc = np.zeros_like(O); cnt = np.zeros(m.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            mm = np.roll(m, (dy, dx), (0, 1)); acc += np.roll(O, (dy, dx), (0, 1)) * mm[..., None]; cnt += mm
        new = (~m) & (cnt > 0); O[new] = acc[new] / cnt[new][:, None]; m |= new
    return O


def mesh_components(obj):
    """Connected-component id per vertex (hair cards in 0-12 are separate components)."""
    me = obj.data; n = len(me.vertices); parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for e in me.edges:
        a, b = find(e.vertices[0]), find(e.vertices[1])
        if a != b:
            parent[a] = b
    roots = {}
    return np.array([roots.setdefault(find(i), len(roots)) for i in range(n)])


# ---- validation --------------------------------------------------------------------------------
def validate_parts(edit_prefix='', default_prefix='DEF_'):
    """Assert every part keeps its default topology and has identity transforms. Returns report list."""
    rep = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.find('-') != 1:
            continue
        d = bpy.data.objects.get(default_prefix + o.name)
        m = o.data
        cnt = (len(m.vertices), len(m.edges), len(m.polygons))
        ok = True
        if d:
            ok = cnt == (len(d.data.vertices), len(d.data.edges), len(d.data.polygons))
        ok &= all(abs(x) < 1e-6 for x in o.location) and all(abs(x) < 1e-6 for x in o.rotation_euler) \
            and tuple(o.scale) == (1.0, 1.0, 1.0)
        rep.append((o.name, cnt, 'OK' if ok else 'FAIL'))
    return rep
