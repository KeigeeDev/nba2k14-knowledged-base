# Glossary

Short definitions of terms and acronyms used across NBA 2K14 modding references. Keep alphabetized. Add a `[DRAFT]`/`[COMMUNITY]`/`[VERIFIED]` tag inline if a definition itself needs scrutiny.

- **Cheat table (`.CT`)**: an XML file for Cheat Engine that lists named memory addresses along with their data types. See [tools/cheat-engine.md](tools/cheat-engine.md).
- **Court mod**: a mod that replaces the textures or geometry of an in-game arena floor and its surroundings.
- **Cyberface**: the in-game 3D face/head model and texture used to represent a specific player. See [workflows/cyberface-blender.md](workflows/cyberface-blender.md).
- **CyberFace ID**: the number in a player's roster entry that selects their cyberface file. ID 326 means `png0326.iff`. Look it up with [RED MC](tools/red-mc.md).
- **DDS**: the texture file format used for cyberface textures. It can be block-compressed (DXT1, DXT5) or uncompressed (A8R8G8B8). See [file-formats/cyberface-textures.md](file-formats/cyberface-textures.md).
- **Draft class**: a generated or custom set of incoming rookie players, stored in its own save file format.
- **DXT1 / DXT5**: block-compressed DDS formats. DXT5 keeps a full alpha channel. `face_color.dds` is DXT5 and `skin_colour.dds` is DXT1. They need a real encoder (NVIDIA tools, Photoshop).
- **`.iff`**: the game's container file for assets such as cyberfaces (`png<ID>.iff`). Opened with the [3DM Tool](tools/3dm-tool.md).
- **MCP (Model Context Protocol)**: a protocol that lets an AI assistant call tools, for example running Python in Blender via [MCP for Blender](tools/mcp-for-blender.md).
- **Module-relative address / RVA**: an address written as an offset from where the exe is loaded (`nba2k14.exe+11DD6A0`). It stays valid between game sessions, as long as the exe build is the same.
- **MyTeam**: the card-collecting game mode. On PC it's modded less often than franchise and roster content.
- **`.n2km`**: the model format for cyberface heads, exported and imported by the 3DM Tool. See [file-formats/n2km.md](file-formats/n2km.md).
- **Rating / attribute**: one of about 40 per-player skill values (3PT Shot, Speed, Block, ...), each stored as a single byte. See [game-mechanics/player-ratings.md](game-mechanics/player-ratings.md).
- **Roster file**: the save file that holds player attributes, ratings, and team assignments. It can be edited outside the game with the right tool.
- **Slider**: a global gameplay tuning value with separate User and CPU settings. Sliders scale success rates and how much each rating counts. Each is stored as a float. See [file-formats/gameplay-sliders-memory-map.md](file-formats/gameplay-sliders-memory-map.md).

<!-- Add new terms alphabetically. -->
