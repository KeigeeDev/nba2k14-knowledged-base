# Blender MCP setup for cyberface work

**Status:** [DRAFT]. These are the owner's observations from one project on Blender 5.2. One Blender API claim was partly checked against release notes (see Sources).
**Category:** ai-workflow
**Last updated:** 2026-09-27

## Summary

This page covers how the owner sets up an AI-driven Blender session for cyberface editing: load the helpers, set up the scene and reference images, and get renders the assistant can trust. It also collects the traps that cost time.

## Start of each session

1. Check the connection (the MCP add-on status and scene info). If tools fail, reinstall the add-on: `uvx mcp-for-blender install-addon` ([tool page](../tools/mcp-for-blender.md)).
2. Load the helper scripts ([`cf_blender`, `dds_tools`](../tools/cyberface-scripts.md)) by adding their folder to `sys.path` and calling `importlib.reload`.
3. Check `bpy.data.filepath` is the right player's `.blend` before changing anything. Other sessions may have switched files. Opening a file discards the current scene, so check `bpy.data.is_dirty` and ask first.
4. Open the `.blend`, or import the model with `bpy.ops.import_scene.n2km(filepath=...)`.

## Scene setup for a new player

- **Collections:**
  - `Edit_Head`: the live parts.
  - `Default_Head`: hidden, not selectable. It holds `DEF_0-*` copies with their own mesh data, used as position reference and validation baseline.
  - `References`: the image empties.
- **Materials:** `face_color` on `0-1`. On `0-12`, the hair texture with alpha linked. `hair.dds` has to be loaded through `dds_tools`, because Blender can't read it.
- **Clipping:** set the viewport clip end to ≥ 10000. The head is 60+ units tall.
- **Reference images** are image empties with `empty_image_offset=(-0.5,-0.5)`, viewed only in ortho, axis-aligned views:
  - `REF_front`: rotation (90°, 0, 0) at y = +45, behind the head. Seen in Front view.
  - `REF_side`: rotation (90°, 0, 90°) at x = −45. Seen in Right view. The side photo must show the face pointing **left**, which is the character's left side (+X).
  - Size = image height in px × k, where k is units per pixel. [Reshaping](cyberface-reshaping.md#1-scale-the-references) covers how to choose k.

## Getting renders the assistant can trust

- **Don't trust `get_viewport_screenshot`.** It uses a cached view matrix, which only updates when Blender redraws. With Blender in the background it keeps returning the same stale image.
- Use `cf_blender.snap(path, view, center, ortho, W, H, shading)` instead, which renders offscreen, and have the assistant read the PNG.
  - Views: `FRONT`, `RIGHT`, `LEFT`, `BACK`, `Q34`, `Q34L`, `TOP`.
  - For model-vs-photo overlays, use `shading='SINGLE'` + `xray=True`.
  - `'TEXTURE'` checks the face texture. `'MATERIAL'` shows alpha (hair), but its reflections make hair look glossy, so judge hair in game.
- **Before judging a render, check `obj.visible_get()` for every part.** Parts hidden with the outliner eye icon don't render either. In the KQ project the eyeballs were eye-icon-hidden, so the eye holes looked empty.
- If two renders that should differ are byte-identical, suspect visibility first, not caching.

## Other traps

- `Image.pixels` rows are bottom-up; photos are handled top-down (`cf_blender.image_array`). `pixels.foreach_set` needs float32.
- Blender's bundled Python has numpy but not scipy or matplotlib, so write small helpers yourself.
- State kept in `bpy.app.driver_namespace` survives between MCP calls but is lost when Blender restarts or the MCP reconnects. Save landmarks and offsets to JSON.
- Save a backup copy before risky reshapes (`save_as_mainfile(..., copy=True)`), and save after every step.
- `SequenceEditor.sequences` is gone in Blender 5 (it's `strips`). The owner's machine has no ffmpeg, so ask the user for screenshots rather than a screen recording.

## Sources

- [`sources/cyberface/guides/01_blender_mcp_setup.md`](../../sources/cyberface/guides/01_blender_mcp_setup.md)
- Blender 4.4 Python API release notes (found through search, 2026-09-27): `bpy.types.Sequence` was renamed `Strip`, and properties named "sequence" were deprecated in favour of "strip" names. https://developer.blender.org/docs/release_notes/4.4/python_api/. Removal in 5.0 wasn't confirmed.

## Open questions

- Does the stale screenshot also happen with Blender in the foreground, or only in the background?
