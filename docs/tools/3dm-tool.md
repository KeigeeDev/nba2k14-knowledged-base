# 3DM Tool

**Status:** [COMMUNITY]
**Category:** tool
**Last updated:** 2026-09-27

## Summary

The 3DM Tool opens NBA 2K `.iff` files. For cyberfaces it exports the head model as `.n2km` plus the textures as `.dds`, and imports edited versions back into the `.iff`. It's the standard way into and out of cyberface files in 2K14 tutorials.

## Details

- **Platform:** Windows. TODO: confirm the version and any runtime it needs.
- **Aliases:** forum threads also mention a "3DM Mod Tool" and an "NBA2KXMODTOOL". It's unconfirmed whether these are the same tool or versions of it.
- **Cyberface use:** open `png<ID>.iff`, then export the model (`<hash>.N2KM`) and the textures `face_color.dds`, `hair.dds` and `skin_colour.dds`. After editing, import the model and textures back. Full steps: [cyberface workflow](../workflows/cyberface-blender.md).

## Known issues

- **Import fails if topology changed.** According to the owner's notes, the tool fails if any part's vertex, edge or face count differs from the original. NLSC threads (seen only as search excerpts) report the same kind of error, for example a headband with 124 vertices instead of the expected 145, or an edited `0-1` that's larger than the original. Run `n2km_tools.py compare` before every import ([scripts](cyberface-scripts.md)).
- **Texture size limits** are unknown. See [cyberface textures](../file-formats/cyberface-textures.md#open-questions).

## Sources

- Owner's notes: [`sources/cyberface/CYBERFACE_MODDING_GUIDE.md`](../../sources/cyberface/CYBERFACE_MODDING_GUIDE.md).
- Listed as a required tool in icecr's NLSC tutorial (per search excerpts): https://forums.nba-live.com/viewtopic.php?f=154&t=113460
- Where to get it: TODO: source needed. Per search excerpts, the tutorial says most of the tools are in NLSC's NBA 2K14 downloads section.

## Open questions

- Who made it, and which version works with 2K14?
- What are the exact menu steps for export and import?
- Does it care about part order in the `.n2km`?
