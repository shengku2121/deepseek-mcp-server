# 🐋 DeepSeek MCP Server

**95% cheaper AI inference for any MCP-compatible AI agent.**

Give Claude Code, Cursor, Windsurf, and any MCP agent access to DeepSeek V4 — the frontier AI model that costs **$0.14/M tokens** vs GPT-4's $15/M tokens. That's 99% cheaper.

## 🔥 Why This Exists

| Model | Input $/M tokens | Output $/M tokens |
|-------|-----------------|-------------------|
| GPT-4 Turbo | $10.00 | $30.00 |
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| **DeepSeek V4-Flash** | **$0.14** | **$0.28** |
| DeepSeek V4-Pro | $0.435* | $0.87* |

*\*75% promo through 2026-05-31, list price $1.74/$3.48*

Your AI agent shouldn't burn credits on simple tasks. Use DeepSeek for everything except the hardest problems.

## 📦 Installation

```bash
pip install deepseek-mcp-server
```

Or from source:
```bash
git clone https://github.com/silicon-legion/deepseek-mcp-server
cd deepseek-mcp-server
pip install -e .
```

Get your API key at [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)

## 🚀 Quick Start

### Claude Code
```yaml
# ~/.claude/claude.yaml
mcp_servers:
  deepseek:
    command: "deepseek-mcp"
    env:
      DEEPSEEK_API_KEY: "sk-your-key"
```

### Cursor / Windsurf
```json
{
  "mcpServers": {
    "deepseek": {
      "command": "deepseek-mcp",
      "env": {
        "DEEPSEEK_API_KEY": "sk-your-key"
      }
    }
  }
}
```

### Hermes Agent
```yaml
# ~/.hermes/config.yaml
mcp_servers:
  deepseek:
    command: "deepseek-mcp"
    env:
      DEEPSEEK_API_KEY: "sk-your-key"
```

## 🛠️ Tools

### `deepseek_chat`
General chat. Best for Q&A, content, translation, classification.

```
"Summarize this RFC in 3 bullet points"
"What's the capital of Mongolia?"
"Translate this to Japanese: Hello world"
```

### `deepseek_reason`
Deep chain-of-thought reasoning with V4-Pro. Best for math, logic, architecture.

```
"Prove that sqrt(2) is irrational"
"Design a database schema for a multi-tenant SaaS"
"What's wrong with this distributed lock implementation?"
```

### `deepseek_code`
Code generation optimized. Best for writing functions, debugging, tests.

```
"Write a Python decorator that retries on exception with exponential backoff"
"Find the bug in this React useEffect hook"
"Generate pytest fixtures for this FastAPI endpoint"
```

## 💰 Pricing

| Tier | Price | Limits |
|------|-------|--------|
| **Free** | $0 | 100 requests/day |
| **Pro** | $9/month | Unlimited requests |
| **Enterprise** | Custom | SLA, priority support, on-prem |

➡️ **[Upgrade to Pro on MCPize](https://mcpize.com/deepseek-mcp)**

## 🏗️ Architecture

```
AI Agent (Claude Code/Cursor/Hermes)
    │
    │ MCP Protocol (stdio)
    ▼
DeepSeek MCP Server
    │
    │ OpenAI-compatible API
    ▼
DeepSeek API (api.deepseek.com)
    │
    ├── deepseek-chat    → V4-Flash ($0.14/M in)
    └── deepseek-reasoner → V4-Pro  ($0.435/M in*)
```

## 🔒 Security

- Your API key stays local — never sent anywhere except DeepSeek's API
- All traffic goes directly to `api.deepseek.com`
- No telemetry, no tracking, no analytics

## 🧪 Development

```bash
# Clone and install
git clone https://github.com/silicon-legion/deepseek-mcp-server
cd deepseek-mcp-server
pip install -e ".[dev]"

# Run tests
pytest

# Test manually with MCP Inspector
npx @modelcontextprotocol/inspector deepseek-mcp
```

## 📄 License

MIT © 2026 Silicon Legion (硅基军团)

---

Built with ❤️ by [Silicon Legion](https://github.com/silicon-legion) — autonomous AI company.
