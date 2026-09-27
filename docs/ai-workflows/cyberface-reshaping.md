# Reshaping a cyberface head to reference photos

**Status:** [DRAFT]. The method comes from one project ("KQ") in the owner's notes. The numbers are that head's and may not carry over.
**Category:** ai-workflow
**Last updated:** 2026-09-27

## Summary

An AI assistant, working through the Blender MCP, measures front and side photos with numpy, compares them with the model slice by slice, and moves vertices with smooth displacement fields. Vertex counts never change, so the result stays importable. The full recipes, with KQ's exact coordinates and thresholds, are in the [source guide](../../sources/cyberface/guides/02_reshaping.md).

## 1. Scale the references

- Photo proportions never match the default head, so measure several ratios (model units ÷ photo pixels): eye spacing (IPD), ear-to-ear width, eye → chin, eye → mouth, mouth width, jaw width, eye → skull top.
- Use the **median** ratio, anchored on the eye line. Give the side photo its own ratio, because the camera distance differs.
- On KQ, scaling by IPD alone made the head about 14% too small. Scaling by mouth height alone misaligned the eyes.
- The eyes and mouth interior are bone-driven, so fit the photo around them, not the other way round. Don't make the head bigger with a uniform scale of every part: that would move them too.

## 2. Measure

- **Person mask:** pixels that differ from the background (the median of the image corners) by more than about 0.10. The mask's left and right edges per row give the silhouette.
- **Features:** pupils are the centroid of dark pixels near each eye. The mouth line, nostril base and chin shadow are the darkest rows in a narrow midline strip.
- **Model landmarks:** the boundary loops of `0-1` (eye holes, mouth, neck), the midline profile, and the ear vertices.
- **Compare in a table** of photo vs model extents for each height slice. That's more reliable than eyeballing overlays.

## 3. Feature-specific methods

These are summaries; the source guide has the parameters.

- **Face width:** the photo mask can't see the cheek edge (ears and hair form the silhouette there). Use a front image with a drawn face contour, and first check it lines up at the pupils, nostrils, mouth and jaw. Compare it with the **ear root** of the model, not the ear rim.
- **Ears:** trace the ear outline in the side photo. Match the model ear to it by moments (centroid, principal axes, spread) rather than single extreme points. Blend with a smoothstep so the root stays attached. Default ears tend to be too small and lean forward; real ears lean back about 10–15°. Afterwards, check the headband (`0-0`) still clears the ear.
- **Eye openings:** leave the eyeballs alone. Rebuild each 18-vertex eye-hole loop of `0-1` as an almond shape, keep every lid vertex in front of the eyeball, and carry the nearby skin and lash parts with a smooth field. This moves `0-8`–`0-11` slightly. On KQ that was up to 0.64 units, and it looked right in game ([rules](../workflows/cyberface-blender.md#how-the-eye-and-mouth-rules-were-settled)).
- **Nose:** check the profile first, then the width, then the form. Default 2K noses are angular. Round them with masked Taubin smoothing plus a small bulge at the nostril wings, and check that the midline profile moves less than about 0.2 units.

## 4. Apply smooth displacement fields

- Build a field from smoothstep falloffs (ellipsoid regions, gated front/back and by height). Apply it **identically** to every part that forms the visible head (`0-1`, `0-12`, `0-0`) so seams stay together.
- Skip `0-2`–`0-11`, and don't touch the neck boundary (z below about 8).
- Keep moves modest. KQ's maximum was 2.6 units.
- Always compute from the original positions, so re-runs don't compound.

## 5. Validate and export

1. `cf_blender.validate_parts()` → every part `OK`. Mind [its gaps](../tools/cyberface-scripts.md#known-issues).
2. Export to a new file, then run `n2km_tools.py compare original edited`. It must say `SAFE to import`.
3. Render front, side and 3/4 views and compare them with the references before testing in game.

## Sources

- [`sources/cyberface/guides/02_reshaping.md`](../../sources/cyberface/guides/02_reshaping.md)

## Open questions

- Which of KQ's numbers (ear thresholds, nose masks, eye-loop z range) hold for other heads with the same topology?
- How were the results judged in game? Were any of these steps changed after in-game testing? The project log `projects/KQ.md` wasn't uploaded.
