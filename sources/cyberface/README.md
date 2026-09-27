# Cyberface guides and scripts (source material)

These are the repo owner's working notes and helper scripts for making NBA 2K14 cyberfaces in Blender through the Blender MCP. They were copied from the owner's local `C:\2K Modding\Cyberface` folder and pushed in commit `383a040` (2026-09-27). The files are stored exactly as uploaded. They were moved here from `docs/` so that `docs/` holds only reviewed, tagged entries. The compiled `__pycache__/*.pyc` files from the upload were deleted because they're build output, not evidence.

Don't hand-edit these files. When the local notes change, replace them here in one commit, update the hashes below, and re-review the docs entries that cite them. Git history keeps the old versions.

| File | SHA-256 | What it is | Reviewed in |
|---|---|---|---|
| `CYBERFACE_MODDING_GUIDE.md` | `f00a1ce5b0aa4853d4a93b83846cc17ec504052669f9737d0ba0bbf470b141f5` | Index: toolchain, workflow, hard rules, part map | [workflow](../../docs/workflows/cyberface-blender.md), [parts](../../docs/file-formats/cyberface-parts.md) |
| `guides/01_blender_mcp_setup.md` | `4bd652ce26efe59b033cd3ed52046a46060eab806e86cf388e62e3213c4d19f7` | Blender MCP session setup, screenshots, gotchas | [MCP setup](../../docs/ai-workflows/cyberface-blender-mcp-setup.md) |
| `guides/02_reshaping.md` | `649dddbb9ad64ae908ee68add363e6adc51bf6e82e4afdd9211063c06b100a3d` | Fitting the head to reference photos | [reshaping](../../docs/ai-workflows/cyberface-reshaping.md) |
| `guides/03_texture_projection.md` | `1097e95cc8102d8889e400e7c1dc0a17fe2a9bb198128833550b0dbd90155595` | Baking photos into the face texture | [texture projection](../../docs/ai-workflows/cyberface-texture-projection.md) |
| `guides/04_hair.md` | `ddce98eb71e25317a48b678d994e3aae9ee181d7b8f4d57090a3110c098e4936` | Hair part `0-12` and `hair.dds` | [hair](../../docs/ai-workflows/cyberface-hair.md) |
| `guides/05_file_formats.md` | `d1d5589585b38a0691a89ff86e892e2c95f2855bdaad28ee3bc70e98ec2b9b2f` | `.n2km` and `.dds` layouts | [n2km](../../docs/file-formats/n2km.md), [textures](../../docs/file-formats/cyberface-textures.md) |
| `scripts/cf_blender.py` | `281eba7bdbd16da59dff265b450c04270789663bf45c8c8a59d2dcd2c05ffe7f` | Blender-side helpers (render, TPS warp, UV raster, validation) | [scripts](../../docs/tools/cyberface-scripts.md) |
| `scripts/dds_tools.py` | `5fe967a6ae4714818391b7532290443a3c5377b131ebd0b18a0fd84aad49fcc0` | Read/write uncompressed A8R8G8B8 DDS; DDS header info | [scripts](../../docs/tools/cyberface-scripts.md) |
| `scripts/n2km_tools.py` | `3680086f613cdfcffea0940325e0f39eac720f6f1571220f133819241a6ffa62` | `.n2km` info and pre-import safety compare | [scripts](../../docs/tools/cyberface-scripts.md) |
| `compare-47F01028-v7.txt` | `84fea19b46a057a9eaa7efadfc295f77477f8c5b7ab1ccde324ef33fa30cf099` | Output of `n2km_tools.py compare` on the real KQ head (`47F01028.N2KM`) vs the owner's edit `v7`, run on the owner's machine and pasted in chat on 2026-09-27 | [n2km](../../docs/file-formats/n2km.md), [parts](../../docs/file-formats/cyberface-parts.md) |

## Things to know when reading these

- The notes were written during one cyberface project, "KQ" (head model `47F01028.N2KM`). Coordinates, thresholds and falloff radii come from that model and may not carry over to other heads.
- Parts of the notes are addressed to Claude (for example "rule for Claude", and the warnings about several sessions sharing one Blender). They are working notes, not a polished tutorial.
- Paths like `C:\2K Modding\...` and `C:\Editing Tools\RED MC` are the owner's local install paths. In this repo the scripts are in `sources/cyberface/scripts/`.
- The notes refer to files that were **not** uploaded: `projects/<PLAYER>.md` logs, `projects/*_landmarks.json`, per-player folders, and the game files themselves.
- Review found a few script limitations and contradictions between the notes. They're listed in the linked docs entries.
