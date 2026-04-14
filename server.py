#!/usr/bin/env python3
"""MEOK AI Labs — churn-predictor-ai-mcp MCP Server. Predict customer churn risk from behavioral signals."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent)
import mcp.types as types

# In-memory store (replace with DB in production)
_store = {}

server = Server("churn-predictor-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="predict_churn", description="Predict churn risk", inputSchema={"type":"object","properties":{"last_login_days":{"type":"number"},"support_tickets":{"type":"number"}},"required":["last_login_days","support_tickets"]}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "predict_churn":
            risk = (args["last_login_days"] * 2) + (args["support_tickets"] * 10)
            return [TextContent(type="text", text=json.dumps({"churn_risk_score": risk, "at_risk": risk > 60}, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="churn-predictor-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(main())
