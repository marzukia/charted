"""Headless MCP handshake smoke test for the charted-mcp server.

Launches `charted-mcp` over stdio, performs the MCP initialize handshake,
lists the tools, and calls `create_chart` with PNG output. Exits non-zero
(raising) if the tool list is missing `create_chart` or the PNG call does
not return image content.
"""

from __future__ import annotations

import asyncio
import base64
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import ImageContent


async def main() -> None:
    params = StdioServerParameters(command="charted-mcp", args=[])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            print(f"tools: {sorted(names)}")
            required = {
                "create_chart",
                "chart_from_csv",
                "list_chart_types",
                "list_themes",
            }
            missing = required - names
            if missing:
                raise SystemExit(f"missing tools: {sorted(missing)}")

            result = await session.call_tool(
                "create_chart",
                {
                    "chart_type": "bar",
                    "data": [3, 1, 4, 1, 5],
                    "labels": ["a", "b", "c", "d", "e"],
                    "title": "smoke",
                    "output_format": "png",
                },
            )

            images = [c for c in result.content if isinstance(c, ImageContent)]
            if not images:
                kinds = [type(c).__name__ for c in result.content]
                raise SystemExit(f"no image content returned, got: {kinds}")

            img = images[0]
            if img.mimeType != "image/png":
                raise SystemExit(f"unexpected mime type: {img.mimeType}")

            raw = base64.b64decode(img.data)
            if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
                raise SystemExit("image content is not a valid PNG")

            print(f"png ok: {len(raw)} bytes, mime={img.mimeType}")

    print("MCP handshake smoke test passed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit as exc:
        print(f"SMOKE FAIL: {exc}", file=sys.stderr)
        raise
