"""
DeepSeek API MCP Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
95% cheaper AI inference for any MCP-compatible AI agent.

Usage:
  deepseek-mcp              # Start server (reads DEEPSEEK_API_KEY from env)
  deepseek-mcp --api-key sk-xxx  # Or pass key directly

Configure in your AI agent (Claude Code / Cursor / Windsurf / Hermes):
  mcp_servers:
    deepseek:
      command: "deepseek-mcp"
      env:
        DEEPSEEK_API_KEY: "sk-xxx"

Pricing: $9/month unlimited (via MCPize marketplace)
         Free tier: 100 requests/day
"""

import os
import sys
import json
import logging
from typing import Any

import mcp.server.stdio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities

from openai import OpenAI

# ── Config ─────────────────────────────────────────────────
DEFAULT_MODEL = "deepseek-chat"  # V4-Flash (cheap, fast)
PRO_MODEL = "deepseek-reasoner"  # V4-Pro (powerful, reasoning)
BASE_URL = "https://api.deepseek.com"

# Rate limiting (simple in-memory — for MVP)
_request_count = 0
FREE_LIMIT = 100  # free tier: 100 requests/day

# ── Logger ─────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="[deepseek-mcp] %(message)s")
logger = logging.getLogger(__name__)

# ── Client ─────────────────────────────────────────────────
_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not _api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not set. Get your key at https://platform.deepseek.com/api_keys\n"
                "Then set: export DEEPSEEK_API_KEY=sk-xxx\n"
                "Or pass via MCP server env config."
            )
        _client = OpenAI(api_key=_api_key, base_url=BASE_URL)
    return _client


# ── MCP Server ─────────────────────────────────────────────
server = Server("deepseek-mcp")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Register available tools."""
    return [
        Tool(
            name="deepseek_chat",
            description="Chat with DeepSeek V4-Flash — the cheapest frontier AI model. $0.14/M input, $0.28/M output tokens. 95% cheaper than GPT-4. Best for: general Q&A, content generation, summarization, translation, classification.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Your message or question to DeepSeek",
                    },
                    "system": {
                        "type": "string",
                        "description": "Optional system prompt to set behavior/role",
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Creativity level (0-2). Default: 0.7",
                        "default": 0.7,
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Max tokens in response. Default: 4096",
                        "default": 4096,
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="deepseek_reason",
            description="Deep reasoning with DeepSeek V4-Pro (R1-style chain-of-thought). Best for: complex math, logic puzzles, multi-step reasoning, code architecture decisions. Shows reasoning steps before final answer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Complex problem requiring deep reasoning",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Max tokens (includes reasoning). Default: 8192",
                        "default": 8192,
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="deepseek_code",
            description="Generate code with DeepSeek V4-Flash, optimized for programming tasks. Best for: writing functions, debugging, refactoring, explaining code, generating tests.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Coding task description. Be specific about language, framework, and requirements.",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (python, javascript, typescript, rust, go, etc.)",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Max tokens. Default: 4096",
                        "default": 4096,
                    },
                },
                "required": ["prompt"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    global _request_count

    try:
        client = get_client()

        if name == "deepseek_chat":
            result = await _do_chat(client, arguments)
        elif name == "deepseek_reason":
            result = await _do_reason(client, arguments)
        elif name == "deepseek_code":
            result = await _do_code(client, arguments)
        else:
            result = f"❌ Unknown tool: {name}"

        _request_count += 1
        if _request_count > FREE_LIMIT:
            result += (
                f"\n\n⚠️  Free tier limit reached ({FREE_LIMIT} requests/day). "
                "Upgrade to Pro at https://mcpize.com/deepseek-mcp ($9/month unlimited)"
            )

        return [TextContent(type="text", text=result)]

    except ValueError as e:
        return [TextContent(type="text", text=f"🔑 Configuration Error: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ DeepSeek API Error: {e}")]


async def _do_chat(client: OpenAI, args: dict) -> str:
    """Standard chat completion."""
    messages = []
    if args.get("system"):
        messages.append({"role": "system", "content": args["system"]})
    messages.append({"role": "user", "content": args["prompt"]})

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=args.get("temperature", 0.7),
        max_tokens=args.get("max_tokens", 4096),
    )

    content = response.choices[0].message.content
    usage = response.usage

    cost = (usage.prompt_tokens * 0.14 + usage.completion_tokens * 0.28) / 1_000_000
    return (
        f"{content}\n\n"
        f"---\n"
        f"📊 Tokens: {usage.prompt_tokens} in + {usage.completion_tokens} out | "
        f"💰 Cost: ${cost:.6f} | "
        f"⚡ Model: DeepSeek V4-Flash"
    )


async def _do_reason(client: OpenAI, args: dict) -> str:
    """Deep reasoning with V4-Pro."""
    response = client.chat.completions.create(
        model=PRO_MODEL,
        messages=[{"role": "user", "content": args["prompt"]}],
        max_tokens=args.get("max_tokens", 8192),
    )

    content = response.choices[0].message.content
    usage = response.usage

    # Extract reasoning if available
    reasoning = ""
    if hasattr(response.choices[0].message, "reasoning_content"):
        reasoning = response.choices[0].message.reasoning_content

    cost = (usage.prompt_tokens * 0.435 + usage.completion_tokens * 0.87) / 1_000_000

    result = ""
    if reasoning:
        result += f"🧠 Reasoning:\n{reasoning}\n\n━━━ Answer ━━━\n\n"
    result += (
        f"{content}\n\n"
        f"---\n"
        f"📊 Tokens: {usage.prompt_tokens} in + {usage.completion_tokens} out | "
        f"💰 Cost: ${cost:.6f} | "
        f"⚡ Model: DeepSeek V4-Pro (reasoning)"
    )
    return result


async def _do_code(client: OpenAI, args: dict) -> str:
    """Code generation optimized."""
    lang = args.get("language", "")
    lang_hint = f" in {lang}" if lang else ""
    system = (
        f"You are an expert{lang_hint} programmer. "
        "Write clean, well-documented, production-ready code. "
        "Include error handling, type hints (where applicable), and brief comments. "
        "Output ONLY the code with minimal explanation."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": args["prompt"]},
    ]

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=0.3,  # Lower temp for code
        max_tokens=args.get("max_tokens", 4096),
    )

    content = response.choices[0].message.content
    usage = response.usage
    cost = (usage.prompt_tokens * 0.14 + usage.completion_tokens * 0.28) / 1_000_000

    return (
        f"{content}\n\n"
        f"---\n"
        f"📊 Tokens: {usage.prompt_tokens} in + {usage.completion_tokens} out | "
        f"💰 Cost: ${cost:.6f} | "
        f"⚡ Model: DeepSeek V4-Flash (code)"
    )


# ── Entry Point ────────────────────────────────────────────
def main():
    """Start the MCP server."""
    global _api_key

    # Parse CLI args for API key
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--api-key" and i + 1 < len(args):
            _api_key = args[i + 1]
        elif arg.startswith("--api-key="):
            _api_key = arg.split("=", 1)[1]

    if not _api_key:
        _api_key = os.environ.get("DEEPSEEK_API_KEY", "")

    logger.info("DeepSeek MCP Server starting...")
    if _api_key:
        masked = _api_key[:8] + "..." + _api_key[-4:]
        logger.info(f"API Key: {masked}")
    else:
        logger.warning("No API key found — server will error on first request")

    async def run():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="deepseek-mcp",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(),
                ),
            )

    import asyncio
    asyncio.run(run())


if __name__ == "__main__":
    main()
