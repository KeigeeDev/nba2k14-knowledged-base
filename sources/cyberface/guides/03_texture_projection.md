# 03 — Face texture from photos (projection bake, numpy)

Bakes front + side photos straight into `0-1`'s UV layout. Output PNG (2048²) → convert to DXT5 like the original
`face_color.dds` (guide 05) → 3DM Tool.

## Steps
1. **Landmark warp** — plain projection misplaces features, so fit `cf_blender.tps_fit(model_pts, photo_px, reg=0.5)`:
   - Front `(x,z)→(px,py)`: eye-hole centres↔pupils, eye corners, mouth corners/centre, subnasale↔nostril base,
     chin bottom, jaw sides at mouth level, ear outer edges, neck sides, skull top.
   - Side `(y,z)→(px,py)`: eye, nose tip, subnasale, upper lip, mouth line, chin front, chin bottom, ear centre,
     brow ridge, back of head, front of neck.
   - Fit error should be < 1 px; sanity-check a few extrapolated points (hair edge, neck).
2. **Texel→surface**: `POS, NRM, COV = cf_blender.raster_uv(obj_0_1, 2048)` (~91% coverage; rows bottom-up).
3. **Occlusion**: `cf_blender.depth_map` — front (axes x,z; min y), +X side (max x), −X side (min x); drop texels
   more than ~0.35 behind the nearest surface (under the chin, behind ears).
4. **Weights**: front `max(0,−n_y)³`, side `max(0,|n_x|)³` (−X side reuses the side photo = mirror assumption),
   × `cf_blender.person_mask` (background removed, eroded 4 px, **blue shirt excluded**).
   Default texture weight: small baseline, ramping to dominant below z≈8 so the **neck seam keeps the default skin**.
5. **Colour match**: side→front gain in their overlap; both photos→default texture on the neck band z 6–13
   (per-channel gain, clamp 0.75–1.35).
6. **Feather**: blur weight maps (30 passes) and flood-fill colours into zero-weight texels before compositing —
   no hard edges where it falls back to default (ear backs, under chin).
7. **Pad**: `cf_blender.dilate(img, COV, 6)` past UV island borders.

## Ears (separate pass — the global TPS has only one ear point)
- After reshaping the ear (guide 02), give the ear texels their own **linear map** from the traced outline:
  `px = 276.5 + (y − off_y)/ks`, `py = 470.5 − (z − off_z)/ks`; check the ear bbox lands on the photo ear bbox (±5 px).
- Ear texels (triangles with ≥2 ear verts): photo where `n_x·sign(x) > ~0.05…0.45` and sample inside the (shrunk)
  photo ear outline; ear back / inner-facing → median ear skin ×0.9. Blend at the root with smoothstep(13.1,13.9,|x|).
- Head skin around the ear still shows the photo's ear rim (global map) → build an **ear-less photo**: cut the ear
  outline (scaled ~1.3×1.2) and diffusion-fill it **in photo space** (400–600 passes; reset known pixels AND weights
  each pass), then re-sample those head texels from it, weighted by a blurred hole mask × |n_x|.
- ✗ Don't inpaint in texture space with np.roll diffusion — it bleeds across unrelated UV islands (white/grey junk).
- Landmark pairs live in `projects/<PLAYER>_landmarks.json` (driver_namespace is lost when Blender restarts).

## Known limitations → fix in a follow-up pass
- **Back of head / nape**: no photo sees it → keeps the *default player's* hair → streaky patch + centre line in game.
  Fix: synthesise a short-hair fade for back-facing texels (`n_y > 0`) from side-hair colours, feathered in.
- **Baked lighting**: photo highlights (nose bridge, forehead, cheekbones) double with game lighting → shiny nose.
  Fix: de-light — compress luminance above the local low-frequency skin mean, keep hue and pore detail.
- Eyelid skin near eye holes picks up some eye colour; photo fringe gets painted on the forehead (fine when the
  hair cards cover it, otherwise clean in Photoshop).
- Eye colour is a game setting (RED MC / Edit Player), not texture.
