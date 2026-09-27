# MCP for Blender

**Status:** [VERIFIED] for the package name, maintainer and install command (checked on PyPI 2026-09-27). [DRAFT] for the notes on how it behaves, which come from one project.
**Category:** tool
**Last updated:** 2026-09-27

## Summary

MCP for Blender is an MCP server plus a Blender add-on. Together they let an AI assistant such as Claude run Python inside a live Blender session. The owner uses it to reshape heads, bake textures and render check images for cyberfaces.

## Details

- **Package:** `mcp-for-blender` on PyPI, maintained by Siddharth Ahuja (`ahujasid`). The old PyPI name `blender-mcp` now points to it. Latest version when checked: 2.1.1.
- **Requirements:** Blender 3.0 or newer, Python 3.10+.
- **Install:** install `uv`, point your MCP client at the server, then install the Blender add-on:
  ```
  uvx mcp-for-blender install-addon
  ```
  In Blender, enable (or disable and re-enable) the add-on "Interface: MCP for Blender" and click **Start MCP Server**. This step comes from the project README as quoted in search results; it wasn't opened directly.
- **Owner's observations (Blender 5.2):**
  - An add-on on protocol 9 still worked with server protocol 11. Reinstall the add-on if tools start failing.
  - `get_viewport_screenshot` can return a stale image while Blender isn't redrawing. Render offscreen instead (`cf_blender.snap`).
  - Several assistant sessions can drive the same Blender and may switch the open file.

How the owner runs cyberface sessions through it: [Blender MCP setup for cyberfaces](../ai-workflows/cyberface-blender-mcp-setup.md).

## Sources

- PyPI: https://pypi.org/project/mcp-for-blender/ (`live`, checked 2026-09-27)
- GitHub: https://github.com/ahujasid/mcp-for-blender (repo named on the PyPI page)
- Owner's notes: [`sources/cyberface/guides/01_blender_mcp_setup.md`](../../sources/cyberface/guides/01_blender_mcp_setup.md)

## Open questions

- Is there a documented fix for the stale viewport screenshot?
