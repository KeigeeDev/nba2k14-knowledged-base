# Baking reference photos into the face texture

**Status:** [DRAFT]. The method comes from one project ("KQ") in the owner's notes. The TPS warp was checked in isolation (see Sources); the rest wasn't.
**Category:** ai-workflow
**Last updated:** 2026-09-27

## Summary

Front and side photos are projected straight into the UV layout of `0-1`, using numpy inside Blender. A landmark warp keeps features in place, normal-based weights blend the two views, and the default texture fills in where no photo sees the head. The result is a 2048² PNG, which gets downsized and saved as `face_color.dds` ([textures](../file-formats/cyberface-textures.md)). Full parameters are in the [source guide](../../sources/cyberface/guides/03_texture_projection.md).

## Steps

1. **Landmark warp.** Plain projection puts features in the wrong place, so fit a thin-plate spline from model coordinates to photo pixels (`cf_blender.tps_fit(model_pts, photo_px, reg=0.5)`):
   - Front `(x, z)`: eye centres ↔ pupils, eye corners, mouth corners and centre, nostril base, chin, jaw sides, ear edges, neck sides, skull top.
   - Side `(y, z)`: eye, nose tip, nostril base, upper lip, mouth line, chin front and bottom, ear centre, brow ridge, back of head, front of neck.
   - Aim for under 1 px fit error, and spot-check a few extrapolated points (hair edge, neck).
2. **Texel → surface:** `cf_blender.raster_uv(obj_0_1, 2048)` gives each texel a position and normal. It covers about 91% of the texture.
3. **Occlusion:** build depth maps (front, +X, −X). Drop texels that sit more than about 0.35 units behind the nearest surface, such as under the chin or behind the ears.
4. **Weights:**
   - Front photo `max(0, −n_y)³`, side photo `max(0, |n_x|)³`. The −X side reuses the side photo, which assumes the face is symmetric.
   - Multiply by the person mask (background removed, blue shirt excluded).
   - Let the default texture take over below z ≈ 8, so the neck seam keeps the default skin.
5. **Colour match:** match the side photo to the front one where they overlap. Then match both to the default texture on the neck band, with gains clamped to 0.75–1.35.
6. **Feather:** blur the weight maps, and flood-fill colours into zero-weight texels so there are no hard edges.
7. **Pad:** `cf_blender.dilate(img, COV, 6)` extends colours past the UV island borders.

## Ears (separate pass)

The global warp has only one ear point, so ears get their own linear map from the traced ear outline. The skin around the ear still shows the photo's ear rim. The fix is an "ear-less" photo, inpainted **in photo space**, which then gets re-sampled. Don't inpaint in texture space with `np.roll` diffusion: it bleeds across unrelated UV islands.

## Known limitations

- **Back of head / nape:** no photo sees it, so it keeps the default player's hair, which shows up as a streaky patch in game. Planned fix: fill back-facing texels with a short-hair fade made from the side hair's colours.
- **Baked lighting:** photo highlights double up with game lighting and make the nose look shiny. Planned fix: reduce highlights while keeping hue and pore detail.
- Eyelid skin near the eye holes picks up some eye colour. The photo's fringe gets painted onto the forehead, which is fine if hair cards cover it.
- Eye colour is a roster setting ([RED MC](../tools/red-mc.md)), not part of the texture.

## Sources

- [`sources/cyberface/guides/03_texture_projection.md`](../../sources/cyberface/guides/03_texture_projection.md)
- `tps_fit` behaviour was tested during review; see [scripts: what was tested](../tools/cyberface-scripts.md#what-was-tested-2026-09-27).

## Open questions

- Were the planned fixes for the back of the head and baked lighting ever tried?
- Does step 6's texture-space blur cause visible bleeding between UV islands? ([scripts known issue 3](../tools/cyberface-scripts.md#known-issues))
