# 01 — Blender MCP: connect, set up, see

## Start of every session
1. `get_addon_status` (Blender version; add-on protocol 9 vs server 11 still works — update with
   `uvx mcp-for-blender install-addon` if tools fail) → `get_scene_info`.
2. Load helpers:
   ```python
   import sys, importlib
   p = r"C:\2K Modding\Cyberface\scripts"
   if p not in sys.path: sys.path.append(p)
   import cf_blender, dds_tools; importlib.reload(cf_blender); importlib.reload(dds_tools)
   ```
3. Open the player's `.blend` (`bpy.ops.wm.open_mainfile`) or import: `bpy.ops.import_scene.n2km(filepath=...)`
   (operator lives in `import_scene`, not `import_mesh`).

## Scene setup (new player)
- Collections: `Edit_Head` (live parts), `Default_Head` (hidden, `hide_select`, `DEF_0-*` copies with **own mesh
  data** — position reference + validation baseline), `References` (image empties).
- Materials: face → `face_color` image on `0-1`; hair → hair texture with **Alpha linked** on `0-12`
  (DDS A8R8G8B8 must be loaded via `dds_tools`, see guide 05).
- Viewport `clip_end` ≥ 10000 (head is ~60+ units tall).
- Reference image empties (`empty_display_type='IMAGE'`, `empty_image_offset=(-0.5,-0.5)`, ortho + axis-aligned only):
  - `REF_front`: rot (90°,0,0) at y=+45 (behind head) → Front view.
  - `REF_side`: rot (90°,0,90°) at x=−45 → Right view. Side photo must show the face pointing LEFT
    (that is the character's left side, +X).
  - `empty_display_size` = image height px × k (units/px). Pixel→world: front `x=loc.x+(px−W/2)k`,
    `z=loc.z+(H/2−py)k`; side `y=loc.y+(px−W/2)k`. Choosing k → guide 02.

## Seeing the result (screenshots)
- **Don't trust `get_viewport_screenshot`** — it renders with the viewport's cached view matrix, which only updates
  when Blender redraws; with Blender in the background it returns the same stale image.
  `view3d.view_all` / `wm.redraw_timer` via `temp_override` do not fix it.
- Use `cf_blender.snap(path, view, center, ortho, W, H, shading)` then `Read` the PNG.
  - views: FRONT, RIGHT, LEFT, BACK, Q34, Q34L, TOP.
  - `shading='SINGLE'` + `xray=True` (alpha ≈0.35, flat orange) for model-vs-photo overlays.
  - `shading='TEXTURE'` for face texture checks; `'MATERIAL'` for alpha (hair). Material preview adds glossy/blue
    world reflections and can be cached between calls — judge hair looks in game.
- Hide objects for a snap with `obj.hide_viewport=True` (+ `view_layer.update()`). Objects hidden with the
  outliner eye icon (`hide_set(True)` → `hide_get()` True) are ALSO not drawn — the user may have toggled it.
  **Before judging a render, check `obj.visible_get()` for every part** (KQ: eyeballs were eye-icon-hidden, so the
  eye holes looked empty/grey and hiding them "changed nothing"). Restore visibility and delete temp PNGs afterwards.
- If two renders that should differ are byte-identical (`md5sum`), suspect visibility state first, not caching.

## Other MCP gotchas
- `bpy.data.images.pixels` → numpy: rows are bottom-up; photos are handled top-down (`cf_blender.image_array`).
- `Image.pixels.foreach_set` needs float32 (cast float64 results).
- `SequenceEditor.sequences` no longer exists in Blender 5 (it's `strips`); for a screen recording, ask for
  screenshots instead — no ffmpeg on this machine.
- Store per-session state in `bpy.app.driver_namespace[...]` (survives between MCP calls, **lost when Blender
  restarts** or the MCP reconnects) — persist anything reusable (landmarks, offsets) to `projects/<PLAYER>_*.json`.
- Blender's Python has numpy but **no matplotlib/scipy** — write small helpers (point-in-polygon, hull) yourself.
- Opening a .blend with `wm.open_mainfile` discards the current scene — check `bpy.data.filepath` and ask first.
- **One Blender, many sessions**: other Claude sessions (other players, e.g. JGDL) drive the same Blender and may
  switch the open file. At the start of each turn's Blender work, check `bpy.data.filepath` is this player's .blend;
  if not and the open file isn't dirty (`bpy.data.is_dirty`), reopen ours; reload helpers (driver_namespace is gone).
  Save after every step so a switch never loses work.
- Before a risky reshape: `bpy.ops.wm.save_as_mainfile(filepath=..._backup.blend, copy=True)`.
- Save with `bpy.ops.wm.save_mainfile()` after each milestone.
