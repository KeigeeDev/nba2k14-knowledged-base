# Roster editing notes and tools (source material)

These are the repo owner's reverse-engineering notes and scripts for NBA 2K14 PC roster files (`.ROS`, `roster.iff`) and the editors around them (RED MC, Roster Lab by Q2K). They were pushed in commit `0dfcd75` (2026-09-27) under `docs/ai-docs/`, `docs/csv/` and `docs/rosterlab/`, and moved here unchanged so that `docs/` holds only reviewed, tagged entries. The compiled `__pycache__/*.pyc` files were deleted because they're build output.

On the owner's machine these folders live inside the RED MC install (`C:\Editing Tools\RED MC\ai-docs\` and `C:\Editing Tools\RED MC\.ai\{csv,rosterlab}\`). The scripts' import paths assume that layout (see "Running the scripts").

**Redaction:** at the owner's request, personal details about the test player and a local file path were removed from `ai-docs/06-player-record-map.md`, including from the repository history. No technical content changed.

Don't hand-edit these files otherwise. When the local notes change, replace them here in one commit, update the hashes, and re-review the docs entries that cite them.

| File | SHA-256 | What it is |
|---|---|---|
| `ai-docs/README.md` | `3acd7e982280b74f5f7eaf8cc65433398d09640de1b16c4185a3cffdc2b92627` | Index and key facts |
| `ai-docs/01-overview.md` | `c1c3d997bd7669e0366d825cd6fdc2b78c26d4324e331e7dd7585f27beb13db6` | RED MC 5.0: author, file types, install layout, versions |
| `ai-docs/02-ros-format.md` | `b184f1b9fb6a8ee4167c45bc3f821e05fd1894cd1e3e7c612acd31d67d3abf78` | `.ROS` container: header, CRC, directory, section map, bitstream, string heap |
| `ai-docs/03-data-dictionary.md` | `dd0a8b5e033a258317a0ed25de4073a01acc32dd6b76e53d92c250ce0577c593` | Parsing RED MC's `Text/` caption and enum files |
| `ai-docs/04-turk-scripting.md` | `4a3f4a0a9c4dc3c96a81770aa5dc8eb3a0263da5f7fc2040bbdaa45f7a125957` | TURK scripting language |
| `ai-docs/05-ai-integration.md` | `f9788b8f853bcc1859e1874e055be168eeb9ac328978b36e55c0b129b70a166f` | Ways to use AI tools with RED MC |
| `ai-docs/06-player-record-map.md` | `2487565179e679bbf78e3a93b47c2efef9173ba6c214d5b615613f46da1b463a` | Player record field map and mapping method. Personal details redacted at the owner's request (see below). |
| `ai-docs/07-roster-iff.md` | `35a9de5beef1785e37cc205c3060f33ca80c945f14cf8fcb69d2da393759b832` | `roster.iff` (the game's default roster) |
| `ai-docs/08-official-field-spec.md` | `ec79484357700e24ad2840decc377a11fbdec9f78ff4f40bdc604b75411e5b6b` | RED MC's shipped field spec (docx) and text-value table |
| `ai-docs/09-roster-lab.md` | `a0b1fb215c926d3a9a9e3959b800ae21a01ff08c1c966ef9bdb8c8a9e0cb4925` | Roster Lab by Q2K 1.7.0, reverse-engineered |
| `ai-docs/tools/ros_inspect.py` | `7e63bb8a01030dc02c4420764178df103201fa71e858215682299fad0e1b8f5d` | `.ROS` inspector: header, names, resign, bitdiff, player, dump |
| `ai-docs/tools/roster_lab_inspect.py` | `571f993fa4d27b6c7162bebe9af30d6822c99be8b578e6dc004361468fc70b12` | Reads Roster Lab's `.pyc` and schemas without running it |
| `csv/README.md` | `09d7573f6e3abe77047a67fa13daf8d950ddfd8e6a79f64c382daac38915bd76` | RED MC CSV round-trip pipeline |
| `csv/rmcsv.py` | `8976d7185bcf9e763c9129126a353c1c40a3b97346eb9dd943ddec5dd82fecda` | Format-preserving CSV inspect/validate/stats/edit/diff |
| `csv/test_rmcsv.py` | `b7e095c75dda3ba3b6d6ee5ac3b90684354a552e5e99c465d84fa7c086832614` | Test suite for `rmcsv.py` |
| `rosterlab/README.md` | `594c19471baea5544c8ac695e4679ce0feacd4ad11c8bc17e2598e64d7c9e6f8` | `rlapply`: headless CSV → `.ROS` through Roster Lab |
| `rosterlab/rlapply.py` | `f22deb3b295b6c5d5a596356475b674582e163e7443fc7d4603d921fb8234f61` | The `rlapply` script |
| `rosterlab/rlapply.cmd` | `ee068ec3c12328857a1c8e6781abaf41eb0a8867fb2877ded4b835ce4b93faae` | Windows launcher (`py -3.14`) |

## Running the scripts

- `ai-docs/tools/ros_inspect.py` is standalone (standard library only).
- `csv/rmcsv.py` and `csv/test_rmcsv.py` import `turk.py` from a sibling `turk/` folder (the owner's "TURK kit"). **That folder wasn't uploaded**, so they don't run from this repo as-is. They also read RED MC's `Text/` files.
- `rosterlab/rlapply.py` imports `rmcsv` from `../../.ai/csv` and Roster Lab from its install folder, and needs Python 3.14.
- `ai-docs/tools/roster_lab_inspect.py` needs a Roster Lab install and Python 3.14.

## Things to know when reading these

- The notes are written for AI sessions working in the owner's RED MC folder. Paths such as `C:\Editing Tools\RED MC`, `%APPDATA%\2K Sports\NBA 2K14\Saves` and `csv/FIBA 2026` refer to the owner's machine.
- None of the sample rosters, RED MC files or Roster Lab files mentioned in the notes are included. Roster Lab is all-rights-reserved freeware, and the notes say not to copy its schemas.
- Review findings (a script bug, stale sentences, missing files) are listed in the docs entries that cite these files.
