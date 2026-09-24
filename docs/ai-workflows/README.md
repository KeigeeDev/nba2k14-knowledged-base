# AI-Assisted Modding Workflows

Notes on using AI tools — LLMs (like Claude), image upscalers, etc. — to make NBA 2K14 modding faster or more accessible. This is the newer, more experimental section of the repo; entries here are more likely to start as `[DRAFT]`.

## Index

_No ai-workflow entries yet — add one using `templates/entry-template.md` and link it here._

<!-- Example lines once entries exist:
- [texture-upscaling.md](texture-upscaling.md) — using AI upscalers on low-res court/jersey textures
- [llm-script-generation.md](llm-script-generation.md) — using an LLM to write a batch roster-editing script
-->

## Ideas worth documenting as this grows

These are starting points, not verified guides — flesh each one out into its own file (tagged `[DRAFT]` until tested) as they're tried:

- **Format reverse-engineering assistance**: pasting hex dumps or partial format notes to an LLM to help spot patterns or generate a parser skeleton.
- **Texture upscaling/restoration**: using AI upscalers (e.g. ESRGAN-family models) on low-resolution jersey/court/cyberface textures before reinjecting them.
- **Script generation for batch edits**: using an LLM to write a Python/PowerShell script that automates repetitive tasks (renaming files to match a tool's expected format, batch-converting textures, bulk roster edits from a CSV).
- **Cyberface texture painting assistance**: using AI image tools to generate or touch up base textures, then hand-finishing in an image editor.
- **Documentation triage**: pointing an LLM at an old, messy forum thread and asking it to summarize into a clean entry for this repo (still needs human verification before tagging `[VERIFIED]`).

## Notes for contributors

- Always note which specific AI tool/model was used and roughly how (prompt structure, pipeline steps) — "I used AI" isn't reproducible, "I used <tool> with this prompt/pipeline" is.
- Flag anything where AI output needed significant manual correction, so future readers know how much to trust the automated part.
