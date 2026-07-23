# themis-mcp

[![PyPI version](https://img.shields.io/pypi/v/themis-mcp.svg)](https://pypi.org/project/themis-mcp/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://www.python.org/downloads/)
[![Test](https://github.com/DanielDeshmukh/themis-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/DanielDeshmukh/themis-mcp/actions/workflows/test.yml)
[![Lint](https://github.com/DanielDeshmukh/themis-mcp/actions/workflows/lint.yml/badge.svg)](https://github.com/DanielDeshmukh/themis-mcp/actions/workflows/lint.yml)

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

### Step 4: Configure transport (optional)

By default, the server uses stdio transport (for local use with Claude Desktop, opencode, etc.).

For remote/shared deployments, use Streamable HTTP:

```bash
# Set transport to Streamable HTTP
export THEMIS_MCP_TRANSPORT=streamable-http
export THEMIS_MCP_HOST=0.0.0.0
export THEMIS_MCP_PORT=8000

# Start the server
themis-mcp
```

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `THEMIS_MCP_TRANSPORT` | `stdio` | `stdio` or `streamable-http` |
| `THEMIS_MCP_HOST` | `0.0.0.0` | Host to bind to (HTTP mode) |
| `THEMIS_MCP_PORT` | `8000` | Port to listen on (HTTP mode) |
| `THEMIS_MCP_TOOLS` | `ask,lookup` | Comma-separated list of tools to enable |

---

## Tools

### `themis_ask`

Answer a question about Indian statutory law (BNS, IPC, BNSS, BSA, RTI, CPA).

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

Retrieve the exact text of a legal section from anchor tables. Fast, deterministic, no LLM inference.

| Parameter | Type | Description |
|-----------|------|-------------|
| `act` | string | One of: `bns`, `bnss`, `bsa`, `ipc`, `rti_2005`, `consumer_protection_2019` |
| `section` | string | Section number (e.g. `"302"`, `"63"`) |

### `themis_map_section`

Map an IPC section to its BNS equivalent (or vice versa).

| Parameter | Type | Description |
|-----------|------|-------------|
| `source_act` | string | `"ipc"` or `"bns"` |
| `section` | string | Section number (e.g. `"302"`, `"103"`) |
| `target_act` | string | `"bns"` or `"ipc"` (optional, auto-detected) |

**Example:**
```
> Map IPC Section 302 to BNS

IPC Section 302 corresponds to BNS Section 103.
```

---

## Health Check

When running in Streamable HTTP mode, a `/health` endpoint is available:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "themis-mcp",
  "model_loaded": true
}
```

Returns `503` if the model is still loading.

---

## Resources

| URI | Description |
|-----|-------------|
| `themis://disclaimer` | Legal disclaimer (appended to all tool responses) |
| `themis://acts` | List of supported acts with section counts |
| `themis://laws/pdf` | Official PDF links for all supported statutes |
| `themis://laws/{act}/pdf` | Official PDF link for a specific statute |

---

## Prompts

Pre-built legal query templates for common tasks:

| Prompt | Description | Args |
|--------|-------------|------|
| `compare_ipc_bns` | Compare IPC section with BNS equivalent | `section` (e.g. "302") |
| `explain_section` | Explain a section in plain language | `act`, `section` |
| `punishment_for` | Find punishment for an offense | `act`, `offense` |
| `rti_rights` | RTI citizen rights query | `section` (default: "6") |
| `consumer_complaint` | Consumer complaint filing guide | — |
| `section_summary` | Quick section lookup with significance | `act`, `section` |

**Usage in MCP clients:**
```
Use the themis prompt "compare_ipc_bns" with section "302"
```

---

## Caching

Deterministic queries (temperature ≤ 0.1) are cached for 5 minutes (128 entries max).

Cache stats are included in the `/health` endpoint response:
```json
{
  "cache": {
    "size": 12,
    "max_size": 128,
    "hits": 45,
    "misses": 23,
    "hit_rate": "66.2%"
  }
}
```

---

## Sampling

When the client supports MCP sampling, the server can request AI-assisted clarification for ambiguous questions. This is opt-in and gracefully degrades if the client doesn't support it.

---

## IPC ↔ BNS Mapper

Cross-reference sections between old (IPC) and new (BNS) criminal laws:

```bash
# Via tool
> Map IPC 302 to BNS

# Via prompt
Use the themis prompt "compare_ipc_bns" with section "302"
```

200+ known mappings from the Ministry of Law and Justice are included.

---

## Legal Citations

Format citations in multiple styles:

```python
from themis_mcp.citation import format_citation, format_inline_citation, format_footnote

format_citation("bns", "103")
# 'Section 103, The Bharatiya Nyaya Sanhita, 2023'

format_citation("ipc", "302", short=True)
# 'IPC s. 302'

format_inline_citation("bns", "103")
# '(BNS, s. 103)'

format_footnote("bns", "103")
# 'Bharatiya Nyaya Sanhita, 2023, s. 103.'
```

---

## Prometheus Metrics

When running in HTTP mode, metrics are available at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

**Available metrics:**
- `themis_tool_calls_total` — Total tool calls (labels: `tool`)
- `themis_tool_errors_total` — Tool errors (labels: `tool`, `error`)
- `themis_tool_duration_seconds` — Tool call duration histogram
- `themis_cache_hits_total` — Cache hits
- `themis_uptime_seconds` — Server uptime

---

## Session Management

HTTP mode tracks active sessions with automatic timeout (1 hour default).

Session stats are included in `/health`:
```json
{
  "sessions": {
    "active_sessions": 3,
    "timeout_seconds": 3600
  }
}
```

---

## Dynamic Tool Loading

Control which tools are exposed to the MCP client via environment variable:

```bash
# Only expose the ask tool (no lookup)
export THEMIS_MCP_TOOLS=ask

# Only expose the lookup tool (no LLM inference)
export THEMIS_MCP_TOOLS=lookup

# Both tools (default)
export THEMIS_MCP_TOOLS=ask,lookup
```

---

## Rate Limiting

The `themis_ask` tool is rate-limited to prevent abuse:

- **Limit:** 30 calls per minute
- **Response:** `Error (RATE_LIMITED): Rate limit exceeded. Try again in X seconds.`

Configure via the `RateLimitConfig` in `ratelimit.py` if needed.

---

## Error Handling

Errors are classified into three categories:

| Class | Meaning | LLM Action |
|-------|---------|------------|
| `CLIENT_ERROR` | Bad input, missing params | Self-correct the request |
| `SERVER_ERROR` | Internal failure (GPU, model) | Abort and notify user |
| `EXTERNAL_ERROR` | Network, download failure | Retry with backoff |

Example error response:
```
Error (SERVER_ERROR): Insufficient GPU memory
Details: THEMIS requires ~13GB VRAM. Close other GPU applications.
```

---

## OpenTelemetry Tracing

Optional tracing for production monitoring. Install with:

```bash
pip install "themis-mcp[otel]"
```

Traces are emitted for every tool call with:
- `mcp.tool.name` — tool being called
- `mcp.tool.question` — input (truncated to 100 chars)
- Latency and error status

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

### IPC to BNS mapping

```
User: Map IPC Section 302 to BNS

THEMIS: IPC Section 302 corresponds to BNS Section 103.
```

### Using prompts

```
User: Use the themis prompt "punishment_for" with act "BNS" and offense "theft"

THEMIS: Section 303 of the Bharatiya Nyaya Sanhita, 2023 defines theft...
```

### Law PDF resources

```
User: Get the PDF link for BNS

THEMIS: {
  "title": "Bharatiya Nyaya Sanhita, 2023",
  "pdf_url": "https://www.indiacode.nic.in/bitstream/...",
  "date_enacted": "2023-12-25",
  "effective_date": "2024-07-01"
}
```

---

## Troubleshooting

### "No GPU available or CUDA not configured"

THEMIS requires a CUDA-capable GPU with ~13GB VRAM.

1. Verify CUDA is installed: `nvidia-smi`
2. Install CUDA: https://developer.nvidia.com/cuda-downloads
3. Ensure PyTorch sees CUDA: `python -c "import torch; print(torch.cuda.is_available())"`

### "Insufficient GPU memory"

Close other GPU-intensive applications (browser tabs with hardware acceleration, other ML models, etc.).

### "Failed to download model weights"

Check your internet connection. The model weights (~13GB) are downloaded from HuggingFace on first run.

### "THEMIS model not loaded"

The server may still be starting up. Wait a few seconds and try again. If the error persists, check the server logs.

### Model loads slowly on first run

First run downloads ~13GB of model weights from HuggingFace. Subsequent runs use the cached weights.

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
