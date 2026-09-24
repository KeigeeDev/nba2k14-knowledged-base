# Guidance for AI agents working in this repo

This repository is a knowledge base, not a codebase. Its purpose is to accumulate accurate, well-sourced information about modding NBA 2K14 (PC) and about using AI to help with that modding. Keep that goal in mind over any generic "software engineering task" instincts.

## Core rules

1. **Never present unverified claims as fact.** Every substantive entry must carry a confidence tag at the top: `[VERIFIED]`, `[COMMUNITY]`, or `[DRAFT]` (see README.md). If you are not confident about a specific technical detail (tool version, byte offset, file structure, download link), tag it `[DRAFT]` or `[COMMUNITY]` and say so explicitly rather than inventing specifics.
2. **Do not fabricate URLs, tool names, authors, or version numbers.** If the user hasn't given you a source and you aren't highly confident one exists, write `TODO: source needed` instead of guessing. A wrong link is worse than no link.
3. **Prefer citing what the user provides.** When the user pastes a forum post, tool README, Discord message, or file dump, extract and organize the knowledge from it rather than relying on training data.
4. **Keep entries atomic.** One tool, one file format, or one workflow per file under `docs/`. Don't create giant catch-all documents.
5. **Update the relevant index/README when adding a new doc file** so navigation doesn't silently rot.
6. **Use `templates/entry-template.md`** as the starting structure for new knowledge entries so the confidence tag and source fields aren't forgotten.

## Where things go

- `docs/game-mechanics/` — conceptual explanations of game systems (ratings, sliders, progression); link to `file-formats/` for byte-level detail
- `sources/` — raw evidence files (cheat tables, hex dumps) exactly as obtained, with provenance and SHA-256 in that folder's README. Never edit them. Don't copy in files whose license/authorship forbids redistribution — link instead
- `docs/tools/` — one file per tool (what it does, where to get it, known issues, usage notes)
- `docs/file-formats/` — one file per file type or format area (e.g. `.iff` containers, roster/draft-class files, texture formats)
- `docs/workflows/` — task-oriented guides (e.g. "swap a jersey texture", "edit a roster", "install a court mod")
- `docs/ai-workflows/` — how AI tools (LLMs, upscalers, script generation) are used to assist specific modding tasks
- `docs/glossary.md` — short definitions, keep alphabetized
- `docs/resources.md` — links to communities, archives, forums; note if a link is known dead

## Style

- Write for a modder who is competent with files/tools but may be new to NBA 2K14 specifically.
- Use short, direct sentences. Prefer numbered steps for workflows.
- Don't editorialize about the ethics of modding a single-player-friendly game feature — this repo assumes legitimate, personal-use modding of a game the user owns.
