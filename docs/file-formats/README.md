# File Formats

Reverse-engineered notes on NBA 2K14's file formats. This is the highest-value, hardest-to-recover kind of knowledge in this repo — old forum threads with format breakdowns disappear constantly, so anything confirmed here is worth preserving carefully.

## Index

### Runtime memory

- [mycareer-ratings-memory-map.md](mycareer-ratings-memory-map.md): the MyCareer player's 42-byte rating block, plus height, weight, and birth year
- [gameplay-sliders-memory-map.md](gameplay-sliders-memory-map.md): the User/CPU slider float array and fixed-address game clock values

### On-disk files

- [n2km.md](n2km.md): `.n2km` model layout (header, parts, vertices, triangles)
- [cyberface-parts.md](cyberface-parts.md): what parts `0-0` to `0-12` of a cyberface head are, with their vertex counts
- [cyberface-textures.md](cyberface-textures.md): `face_color` / `skin_colour` / `hair` DDS formats, and the A8R8G8B8 byte layout

- [ros-roster.md](ros-roster.md): `.ROS` roster saves: header, CRC, table directory, section map, bitstream, string heap
- [ros-player-record.md](ros-player-record.md): the 3,644-bit player record: mapped fields and the 42 skill ratings
- [roster-iff.md](roster-iff.md): `roster.iff`, the game's default roster (IFF + zlib, little-endian)

_Still missing: general `.iff` containers, `.FXG`/`.CMG` save tails._

## Notes for contributors

- Where possible, back format claims with a hex dump excerpt, a parsing script, or a link to a tool's source code that reads the format — not just "someone on a forum said."
- If a format is only partially understood, document what's known and explicitly list the unknown parts under "Open questions" in the entry.
