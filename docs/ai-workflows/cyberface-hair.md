# Cyberface hair: part `0-12` and `hair.dds`

**Status:** [DRAFT]. The method comes from one project ("KQ", model `47F01028`) in the owner's notes. The video tutorial it's based on couldn't be checked.
**Category:** ai-workflow
**Last updated:** 2026-09-27

## Summary

Hair is the model part `0-12` (a scalp cap plus separate hair cards) and the uncompressed `hair.dds` texture. Its alpha channel decides what's hair and what's see-through. You reshape the existing cards (never add or remove any), then build the texture and alpha from photos plus the default strand texture. Full details are in the [source guide](../../sources/cyberface/guides/04_hair.md).

## Anatomy of `0-12`

On KQ, `0-12` has 457 vertices in 34 separate, unconnected pieces, so each card can be moved freely without tearing anything. Find them with `cf_blender.mesh_components(obj)`.

| Piece | Size | UV region (0–1) | Role |
|---|---|---|---|
| Scalp cap | 176 verts | Centre, 0.16–0.84 | Shell over the skull. Its front lip overhangs the forehead by about 3 units. |
| Front fringe cards | 11 × 9–12 verts | 0.74–1.0 × 0–0.37 | By default they stick forward like a visor |
| Fringe underlayer | 20 verts | 0.27–0.73 × 0.09–0.26 | Band under the fringe |
| Top fins | ~18 × 4–12 verts | 0.84–1.0 × 0.54–0.99 | Spiky top silhouette |
| Nape cards | 2 × 8 verts | 0.04–0.16 × 0.34–0.76 | Tufts at the back |

Re-check these per model. The "34 pieces" count is consistent with the part's vertex/edge/face counts ([cyberface parts](../file-formats/cyberface-parts.md#consistency-checks)).

## Reshaping cards

- Drape the forward cards over the forehead with a smoothstep: the further a vertex sits past the hairline, the more it's pulled down to a brow-height floor and back onto the skin. The skin surface comes from a depth map of `0-1`.
- Always compute from the original positions, so re-runs don't compound.
- Check silhouettes against the photos, the same way as in [reshaping](cyberface-reshaping.md).

## Hair texture

- `hair.dds` is 256² A8R8G8B8. Read and write it with `dds_tools.read_argb` / `write_argb`, using the original header as the template ([textures](../file-formats/cyberface-textures.md)).
- **Base:** the default strand texture, desaturated and tinted to the player's hair colour. Sample the colour from dark photo pixels in the hair region.
- **Scalp cap:**
  - Project the front and side photos with the face warp, which extends well into the hair region.
  - Set alpha to the photo's "hairness", `clip((0.32 − L)/0.2, 0, 1)`: dark pixels are opaque, skin and fade are transparent.
  - Where no photo sees the head, keep the recoloured default strands.
  - Cap the alpha at the default rim alpha so edges stay soft.
- **Cards:** keep their default alpha, recoloured.
- The face texture shows through transparent hair, so keep the scalp and fade in the face texture consistent with the hair.
- A 512² `hair.dds` was written, but whether the 3DM Tool accepts it is unknown.

## Sources

- [`sources/cyberface/guides/04_hair.md`](../../sources/cyberface/guides/04_hair.md)
- The notes base the method on Unnamed2K, "HAIR TUTORIAL FOR NBA2K14 MODDING!" (silent video, Blender 2.7x + Photoshop), linked there as `youtu.be/ctm6OQivh14`. It couldn't be opened from the review environment (YouTube is blocked there) or found through web search, so it's unverified.
- NLSC also has an older hair and beard tutorial: "Tutorial: Importing 3D BEARD AND HAIR", https://forums.nba-live.com/viewtopic.php?f=154&t=96047 (found through search 2026-09-27; not opened).

## Open questions

- Does the 3DM Tool accept a 512² `hair.dds`?
- How did the draped fringe look in game compared to the Blender render?
