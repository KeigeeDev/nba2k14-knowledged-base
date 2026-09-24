# NBA 2K14 Modding Knowledge Base

A curated collection of knowledge, references, tools, and workflows for modding **NBA 2K14** (PC), plus notes on using AI to speed up modding work.

This repo is meant to grow over time as entries get added, corrected, and expanded. It is **not** a finished reference — treat every entry as a starting point to verify, not a guaranteed-accurate fact, unless it links to a primary source.

## Why this exists

NBA 2K14's PC modding knowledge is scattered across old forum posts, dead links, Discord servers, and tool READMEs that have since disappeared. This repo's goal is to centralize:

- What tools exist, what they do, and where to (still) get them
- What the game's file formats look like and how they've been reverse-engineered
- Step-by-step workflows for common mods (rosters, cyberfaces, courts, jerseys, etc.)
- How to use AI (LLMs, upscalers, etc.) to make modding faster and more accessible

## Structure

```
docs/
  game-mechanics/   How game systems work (ratings, sliders, progression)
  tools/            Modding tools: what they do, install notes, known issues
  file-formats/     Reverse-engineered layouts (memory maps, .iff, rosters, etc.)
  workflows/        Step-by-step guides for specific mod types
  ai-workflows/     How to use AI assistants/models to help with modding tasks
  glossary.md       Terms and acronyms used across the modding community
  resources.md      Links to communities, forums, Discords, archives
sources/            Raw source material (cheat tables, dumps) that docs cite
templates/
  entry-template.md Template to copy when adding a new knowledge entry
```

## Start here

- [How player ratings work](docs/game-mechanics/player-ratings.md)

## Contribution status legend

Entries use one of these tags at the top so readers know how much to trust them:

- `[VERIFIED]` — confirmed against a primary source or hands-on testing
- `[COMMUNITY]` — widely reported/used by modders but not independently verified here
- `[DRAFT]` — placeholder or best-effort notes, needs review

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: copy `templates/entry-template.md`, fill it in, tag its confidence level, and link sources whenever possible.

## AI assistants working in this repo

See [CLAUDE.md](CLAUDE.md) for how AI agents (like Claude Code) should read and add to this knowledge base.
