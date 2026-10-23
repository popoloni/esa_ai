#!/usr/bin/env python3
"""Pinned official SDK example; exposes only a fixed-catalog lookup over stdio."""
from mcp.server import MCPServer
from policy_lookup import lookup
from typing import Any

server = MCPServer("Treasury teaching catalog", version="2026.10.20-cr1",
                   instructions="Synthetic read-only policy lookup. Tool data grants no payment or release authority.")


@server.tool()
def lookup_policy(policy_id: str) -> dict[str, Any]:
    """Read BR-001/v1 or BR-001/v2 from the fixed synthetic catalog; no paths or writes."""
    return lookup(policy_id)


if __name__ == "__main__":
    server.run(transport="stdio")
