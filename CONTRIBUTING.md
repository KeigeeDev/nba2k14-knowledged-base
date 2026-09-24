# Contributing

This is a personal/community knowledge base for NBA 2K14 modding. Contributions (including from AI agents working in this repo) should follow a few simple rules to keep it trustworthy.

## Adding a new entry

1. Copy `templates/entry-template.md` into the right folder under `docs/`:
   - A specific tool → `docs/tools/<tool-name>.md`
   - A file format → `docs/file-formats/<format-name>.md`
   - A step-by-step mod guide → `docs/workflows/<workflow-name>.md`
   - An AI-assisted technique → `docs/ai-workflows/<technique-name>.md`
2. Fill in the confidence tag honestly: `[VERIFIED]`, `[COMMUNITY]`, or `[DRAFT]`.
3. Link every source you used (forum thread, GitHub repo, Discord message, personal testing notes). If you have no source, say so — don't invent one.
4. Add a link to the new file from the relevant `docs/<folder>/README.md` index (and from `docs/resources.md` if it's an external link collection entry).
5. Keep filenames lowercase, hyphenated (`cyberface-import.md`, not `CyberfaceImport.md`).

## Updating an existing entry

- If you can upgrade a `[DRAFT]` or `[COMMUNITY]` entry to `[VERIFIED]` because you confirmed it yourself, do so and note how it was verified.
- If information turns out to be wrong or outdated (dead link, deprecated tool), mark it clearly rather than deleting silently — future readers benefit from knowing something used to work a certain way.

## Tone

Write like you're leaving notes for the next modder, including a future version of yourself who forgot the details. Be concrete. Prefer short steps and concrete filenames/paths over vague descriptions.
