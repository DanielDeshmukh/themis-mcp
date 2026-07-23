# themis-mcp

[![PyPI version](https://img.shields.io/pypi/v/themis-mcp.svg)](https://pypi.org/project/themis-mcp/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://www.python.org/downloads/)

MCP server for [THEMIS](https://github.com/DanielDeshmukh/themis) — Indian statutory law Q&A via retrieval-grounded LLM.

*"Not retrieval. Not lookup. Baked into weights, grounded by retrieval."*

---

## What is this?

An MCP (Model Context Protocol) server that wraps the `themis-llm` SDK, making Indian legal knowledge available to any MCP-compatible client (Claude Desktop, opencode, Cursor, etc.).

**Supported laws:**
- Bharatiya Nyaya Sanhita (BNS) 2023 — 358 sections
- Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 — 531 sections
- Bharatiya Sakshya Adhiniyam (BSA) 2023 — 170 sections
- Indian Penal Code (IPC) 1860 — 511 sections
- Right to Information Act (RTI) 2005 — 31 sections
- Consumer Protection Act (CPA) 2019 — 107 sections

---

## Requirements

- Python 3.11+
- GPU with ~13GB VRAM (for local model inference)
- ~13GB disk space (for model weights)

---

## Quick Start

### Step 1: Install

```bash
pip install themis-mcp
```

Or with CLI extras:

```bash
pip install "themis-mcp[cli]"
```

### Step 2: Configure your MCP client

Add to your MCP client config:

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "themis": {
      "command": "themis-mcp"
    }
  }
}
```

**opencode** (`opencode.json`):
```json
{
  "mcpServers": {
    "themis": {
      "command": "themis-mcp"
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "themis": {
      "command": "themis-mcp"
    }
  }
}
```

### Step 3: Use it

Ask legal questions in natural language:

```
> What does Section 302 of the BNS say about murder?

> What is the punishment for theft under the Bharatiya Nyaya Sanhita?

> Compare IPC Section 302 with BNS Section 101.
```

---

## Tools

### `themis_ask`

Ask a legal question about Indian statutory law using the THEMIS retrieval-grounded model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `question` | string | **required** | Legal question about Indian law |
| `temperature` | float | `0.7` | Generation temperature (0.0-1.0). Lower = more deterministic |
| `max_tokens` | int | `512` | Maximum tokens to generate |

**Example response:**
```json
{
  "text": "Section 103 of the Bharatiya Nyaya Sanhita, 2023 defines murder as...",
  "grounded": true,
  "section": "103",
  "act": "The Bharatiya Nyaya Sanhita, 2023",
  "confidence": 0.95
}
```

### `themis_lookup`

Look up raw section text directly from anchor tables (no LLM inference — fast and deterministic).

| Parameter | Type | Description |
|-----------|------|-------------|
| `act` | string | One of: `bns`, `bnss`, `bsa`, `ipc`, `rti_2005`, `consumer_protection_2019` |
| `section` | string | Section number (e.g. `"302"`, `"63"`, `"Section 1"`) |

**Example:**
```
> Lookup BNS Section 103
```

Returns the exact statutory text without LLM interpretation.

---

## Resources

| URI | Description |
|-----|-------------|
| `themis://disclaimer` | Legal disclaimer (appended to all tool responses) |
| `themis://acts` | List of supported acts with section counts |

---

## Usage Examples

### Basic legal question

```
User: What is the punishment for robbery under BNS?

THEMIS: Section 309 of the Bharatiya Nyaya Sanhita, 2023 defines robbery 
as whoever commits robbery shall be punished with rigorous imprisonment 
for a term which may extend to ten years, and shall also be liable to fine.

---
Section: 309
Act: The Bharatiya Nyaya Sanhita, 2023
Grounded: Yes
Confidence: 0.92
---
This is not legal advice. THEMIS provides orientation on Indian statutory law. 
Consult a qualified lawyer for authoritative guidance.
```

### Direct section lookup

```
User: Look up IPC Section 302

THEMIS: Section 302 — IPC

302. Punishment for murder
Whoever commits murder shall be punished with death, or imprisonment 
for life, and shall also be liable to fine.
---
This is not legal advice. THEMIS provides orientation on Indian statutory law.
```

### IPC to BNS comparison

```
User: What section in BNS corresponds to IPC Section 302?

THEMIS: IPC Section 302 (Murder) corresponds to BNS Section 103.
Both provisions deal with the punishment for murder — death or life 
imprisonment, plus fine.
```

---

## Development

### Setup

```bash
git clone https://github.com/DanielDeshmukh/themis-mcp.git
cd themis-mcp
pip install -e ".[dev]"
```

### Run tests

```bash
pytest tests/ -v
```

### Linting

```bash
ruff format --check .
ruff check .
mypy src/themis_mcp/ --ignore-missing-imports
```

### Project structure

```
themis-mcp/
├── pyproject.toml
├── README.md
├── src/themis_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py          # FastMCP server, tool/resource registration
│   ├── tools.py            # themis_ask + themis_lookup
│   └── resources.py        # disclaimer + acts list
├── tests/
│   └── test_basic.py
└── .github/workflows/
    ├── test.yml            # Run tests on push/PR
    ├── lint.yml            # Format + lint + type check
    └── publish.yml         # Manual PyPI publish
```

---

## Publishing

### From GitHub Actions (recommended)

1. Go to [Actions → Publish to PyPI](https://github.com/DanielDeshmukh/themis-mcp/actions/workflows/publish.yml)
2. Click "Run workflow"
3. Enter the version number (e.g. `0.2.0`)
4. The workflow validates the version matches `pyproject.toml`, builds, and publishes

### From command line

```bash
# Build
python -m build

# Publish (requires PyPI token)
twine upload dist/* -u __token__ -p "pypi-YOUR_TOKEN"
```

---

## Relationship to THEMIS

| | themis-mcp | themis-llm |
|---|---|---|
| Interface | MCP tools | Python SDK + CLI |
| Use case | AI assistants (Claude, Cursor) | Scripts, notebooks, apps |
| Model loading | Local (GPU required) | Local (GPU required) |

---

## Disclaimer

THEMIS provides orientation on Indian statutory law. It is **not legal advice**. Consult a qualified lawyer for authoritative guidance.

---

## License

MIT

---

## Citation

```bibtex
@misc{themis-mcp2026,
  author = {Daniel Deshmukh},
  title = {themis-mcp: MCP Server for Indian Statutory Law Q\&A},
  year = {2026},
  url = {https://github.com/DanielDeshmukh/themis-mcp}
}
```

---

*THEMIS — Greek goddess of law, justice, and order. Because justice should not require a law degree to understand.*
