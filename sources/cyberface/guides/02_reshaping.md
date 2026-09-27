# 02 — Reshaping the head to the references

## 1. Scale the references (the key decision)
Photo proportions never match the default head. Measure several ratios (model units / photo px):
IPD, ear-to-ear width, eye→chin, eye→mouth, mouth width, jaw width, eye→skull top — use the **median** k and
anchor on the eye line (x=0, z = eye line). Side photo gets its own k (different camera distance).
- Scaling by IPD alone → head ~14% too small; by mouth height alone → eyes misaligned (KQ).
- Eyes and mouth interior are bone-driven, so the photo is fitted *around* them, not vice versa.

## 2. Measure (numpy in Blender, flat studio background)
- Person mask: `max|rgb − bg| > 0.10` (bg = median of image corners). Per-row min/max x of the mask = silhouette.
- Pupils: centroid of pixels with L < 0.15 in a window around each eye.
- Mouth line / nostril base / chin shadow: darkest row in a narrow midline strip.
- Model landmarks: boundary loops of `0-1` (eye holes, mouth hole, neck), midline profile (|x|<0.4), ear verts
  (|x|>14, z 22–42).
- Compare photo vs model silhouettes per z-slice (front: x extents; side: y extents) in a table — more reliable
  than eyeballing overlays.

### Face width (the cheek/jaw outline)
- The plain photo mask can't see the face edge at cheek level (ears/hair are the silhouette there). Use a front
  image with a **drawn face contour** (e.g. KQ `front-wireframe-reference.webp`): align it to the front reference by
  pupils (scale + offset), **verify** nostrils/mouth/jaw coincide (KQ: ≤2 px) before trusting it.
- Extract contour pixels by colour (cyan/green lines), per row → half-width = (right−left)/2 (offset-free).
- Model side: exclude the ear by region-growing from verts with |x|>15.5 through |x|>13.2 (z 22–41, y −12…1);
  the widest remaining verts at ear level are the **ear root** — that's what the drawn line follows, so compare those.
  Also check the cheek front (max |x| for y<−12) and the ear rim separately: narrowing the root must not pull the rim in.
- Ignore rows where the drawn band curves along the hairline (not a width).

### Ears (size, tilt, protrusion)
- Trace the ear outline in the side photo (helix top, back, lobe, tragus, crus — ~10 px points from a 3× crop).
  Cross-check height with the front photo mask (ear rows). Default ears tend to be too small and lean forward;
  real ears lean back ~10–15°.
- Don't match single extreme points (duplicates → unstable). Match **moments**: fill the model ear's (y,z) convex
  hull and the traced polygon, compute centroid + principal axes + sd, build affine
  `M = Vt·diag(sd_t)·diag(1/sd_s)·Vsᵀ` (orient major axis up, minor axis +y), apply `yz' = c_t + M(yz − c_s)`.
- Ear verts = region-grown set (|x|>15.5 seed, grow through |x|>13.2). Blend with `w = smoothstep(13.0, 14.3, |x|)`
  so the root stays attached; optional protrusion `|x| = 13.2 + (|x|−13.2)(1+0.08w)`. Same target for both ears.
- Anything that sits over the ear (headband `0-0`) must clear the new ear top — restore it toward its `DEF_` shape near
  the ear if an earlier field dragged it down.

### Eye openings (lid shape)
- The eyeballs (`0-6`,`0-7`) are fixed — reshape only the `0-1` eye-hole boundary loops (18 verts each; find with
  `is_boundary`, z 31–37, |x|<9, y<−20; walk boundary edges to order the loop).
- Rebuild each loop as an almond: parameter u = 0 (outer corner) → 1 (inner corner); chord between corners;
  upper lid `chord + up·sin(πu)^0.85`, lower `chord − lo·sin(πu)^0.85` (KQ: up 0.95, lo 0.50, inner corner 0.3 in).
  Keep every lid vert **in front of the eyeball**: `y = min(y, eyeball_front_depth − 0.08)` (front depth map of the ball).
- Carry the surrounding skin + lash/socket parts `0-8…0-11` with a Gaussian-interpolated field of the loop
  displacements (σ 0.6, falloff by distance to loop σ 1.1, radius 4). Check 0-8…0-11 stay OK in validation.

### Nose
- Check in this order: **profile** (side-photo silhouette vs model edge-sampled min-y per z, drawn as dots on the
  photo), **width** (side-by-side front crop vs flat-shaded model at the same k — the ala's outer bulge, not the
  depth-step at the crease), then **form** (flat shading, front + 3/4).
- Ratios help decide scale: alar width vs IPD and vs mouth width (features) and vs face width (head). If features
  match but head doesn't, don't widen the nose alone.
- Default 2K noses are angular (flat ala slabs, pinched V columella). Round them without losing volume:
  **Taubin smoothing** (λ 0.5 / μ −0.53, 12 iters) masked to the lower nose (|x|<~4.2, z 23.6–31, y<−24.2; skip
  boundary verts), + 30 iters on the underside only (|x|<3.8, z 23.4–27.6, y<−25), + ala bulge along normals
  (0.3, Gaussian at (±2.9, −27.3, 26.4)). Verify the midline profile moved < ~0.2.
- Similarity-fit landmarks on the side photo can leave >1 unit residual (photo proportions ≠ model) — prefer local
  overlays over absolute numbers for small features.

## 3. Apply smooth displacement fields (topology-safe)
Move vertices with a field `D(p)` built from smoothstep falloffs, applied identically to every part that forms the
visible head (`0-1`, `0-12`, and `0-0` headband) so shared seams stay together. Skip `0-2…0-11`.
```python
def sstep(e0,e1,x): t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
# region = ellipsoid (centre, radii) → w = 1 - sstep(0.6, 1.35, normalised distance); D += w * move
# gate to the front with sstep over y; vertical ramps with sstep over z
```
Keep moves modest (KQ max 2.6 units) and never touch the neck boundary (z < ~8).

## 4. Validate and export
- `cf_blender.validate_parts()` → every part OK (counts = `DEF_` copy, identity transforms).
- Export to a NEW file (`<hash>_edit.n2km`, `_v2`, …), then:
  `python scripts/n2km_tools.py compare <PLAYER>/<hash>.N2KM <PLAYER>/<hash>_edit.n2km` → must print `SAFE to import`.
- Re-render front / side / 3/4 and compare to the references before the in-game test.
