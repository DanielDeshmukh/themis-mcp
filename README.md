# themis-mcp

MCP server for [THEMIS](https://github.com/DanielDeshmukh/themis) — Indian statutory law Q&A via retrieval-grounded LLM.

## What is this?

An MCP (Model Context Protocol) server that wraps the `themis-llm` SDK, making Indian legal knowledge available to any MCP-compatible client (Claude Desktop, opencode, etc.).

## Requirements

- Python 3.11+
- GPU with ~13GB VRAM (for local model inference)
- `themis-llm` SDK

## Install

```bash
pip install -e .
```

## Usage

### Run directly

```bash
python -m themis_mcp
```

### Via entry point

```bash
themis-mcp
```

## MCP Configuration

Add to your MCP client config (e.g. Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "themis": {
      "command": "themis-mcp"
    }
  }
}
```

Or for development:

```json
{
  "mcpServers": {
    "themis": {
      "command": "python",
      "args": ["-m", "themis_mcp"]
    }
  }
}
```

## Tools

### `themis_ask`

Ask a legal question about Indian statutory law.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `question` | string | required | Legal question about Indian law |
| `temperature` | float | 0.7 | Generation temperature (0.0-1.0) |
| `max_tokens` | int | 512 | Maximum tokens to generate |

**Supported domains:** BNS, IPC, BNSS, BSA, RTI Act, Consumer Protection Act, Constitution

### `themis_lookup`

Look up raw section text from anchor tables (no LLM inference).

| Parameter | Type | Description |
|-----------|------|-------------|
| `act` | string | Act identifier: `bns`, `bnss`, `bsa`, `ipc`, `rti_2005`, `consumer_protection_2019` |
| `section` | string | Section number (e.g. `"302"`, `"Section 63"`) |

## Resources

| URI | Description |
|-----|-------------|
| `themis://disclaimer` | Legal disclaimer |
| `themis://acts` | List of supported acts with section counts |

## Disclaimer

THEMIS provides orientation on Indian statutory law. It is not legal advice. Consult a qualified lawyer for authoritative guidance.

## License

MIT
