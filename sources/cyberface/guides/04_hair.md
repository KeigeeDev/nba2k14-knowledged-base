# 04 — Hair (part 0-12 + hair.dds)

Reference method: Unnamed2K, "HAIR TUTORIAL FOR NBA2K14 MODDING!" (youtu.be/ctm6OQivh14, silent, Blender 2.7x +
Photoshop): reshape the existing hair part (count fixed), project source hair images onto it with extra UV maps
(front/side/top views), bake into the original UV layout, build the alpha (white = hair) in Photoshop, save DDS,
3DM Tool. His source hair came from 2K23 textures ("copy the alpha to make it white").

## Anatomy of 0-12 (457 verts, 34 separate mesh components — none connected)
Find them with `cf_blender.mesh_components(obj)`; each card can be transformed freely without tearing.
| Piece | Size | UV region (0–1) | Role |
|---|---|---|---|
| scalp cap | 176 verts | centre island 0.16–0.84 | shell over skull; front lip overhangs forehead (~3 units) |
| front fringe cards | 11 × 9–12 verts | 0.74–1.0 × 0–0.37 | default: stick forward like a visor |
| fringe underlayer | 20 verts | 0.27–0.73 × 0.09–0.26 | band under the fringe |
| top fins | ~18 × 4–12 verts | 0.84–1.0 × 0.54–0.99 | spiky top silhouette |
| nape cards | 2 × 8 verts | 0.04–0.16 × 0.34–0.76 | tufts at the back |
(Numbers from KQ's model `47F01028`; re-check per model.)

## Reshaping cards (KQ fringe example)
- Drape forward cards over the forehead: for card vertices in front of the hairline (y < y0≈−26),
  `t = distance beyond hairline / card max`, `s = smoothstep(t)`, `z_new = z − (z − z_floor)·s` with
  `z_floor = 40.5 + 0.035·x²` (brows at centre, higher at temples), `y_new = skin_y(x, z_new) − (0.7 + 2.6·(1−s))`
  where `skin_y` comes from the face depth map (`cf_blender.depth_map` of `0-1`, front view).
- Always compute from the ORIGINAL positions (store them) so re-runs don't compound.
- Check silhouettes against the photo (front/side) like guide 02.

## Hair texture
- `hair.dds` = **256² A8R8G8B8** (uncompressed) — Blender can't open it; use `dds_tools.read_argb` (guide 05).
- Base = the default strand texture (`hair copy.png` = `hair.dds` RGB), desaturated and tinted to the player's
  hair colour (sample dark photo pixels, L < 0.2, in the hair region).
- Cap island: `cf_blender.raster_uv(obj_0_12, 512, component_filter=lambda vs: comp[vs[0]] == cap_id)`, project front/side photos with the face TPS
  maps (they extrapolate fine to the hair region); **alpha = photo "hairness"** `clip((0.32 − L)/0.2, 0, 1)`
  (dark = opaque, skin/fade = transparent) where photos see it; top/back keep recoloured default strands + alpha.
  Cap alpha capped by the default rim alpha so strand edges stay soft.
- Cards keep their default alpha, recoloured.
- Write with `dds_tools.write_argb(path, w, h, rgba, template_header=hair.dds header)`: 256² drop-in and 512².
  Unknown yet whether the 3DM Tool accepts 512² for hair → log the result.
- The face texture shows through transparent hair: keep the face texture's scalp/fade consistent with the hair.
