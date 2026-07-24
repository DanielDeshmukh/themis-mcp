# INTERVIEW_PREP.md

## 1. THE 30-SECOND PITCH

"themis-mcp is an MCP server that wraps a fine-tuned Mistral 7B model trained on Indian statutory law. It lets any AI assistant—Claude Desktop, Cursor, opencode—ask legal questions about Indian laws (BNS, IPC, BNSS, BSA, RTI) and get answers grounded in actual statute text, not hallucinated recall. Think of it as a legal copilot for the Indian legal system that connects to your existing AI tools through a standard protocol. It runs locally on a GPU, loads once at startup, and exposes two main tools: one for interpretive Q&A via the LLM, and one for fast deterministic section lookup from anchor tables."

---

## 2. THE ARCHITECTURE, WHITEBOARD-READY

```
[MCP Client]          [themis-mcp Server]         [THEMIS Model]
(Claude/Cursor/       │                            (Mistral 7B + LoRA)
 opencode)            │                            ~13GB, loaded once
     │                │                            at startup via lifespan
     │  stdio /       │
     │  HTTP          │
     ▼                ▼
  MCP Protocol ──► FastMCP (server.py)
                     │
            ┌────────┼────────┐
            ▼        ▼        ▼
       themis_ask  themis_lookup  themis_map_section
       (LLM)       (anchor table) (IPC↔BNS mapper)
            │        │
            ▼        ▼
       tools.py ──► cache.py ──► metrics.py ──► ratelimit.py
            │
            ▼
       Model.generate() → GenerationResult
```

**On a typical request:**
1. Client sends MCP tool call over stdio or HTTP
2. `server.py` routes to `themis_ask` or `themis_lookup`
3. `tools.py` checks rate limiter, then cache (for deterministic queries)
4. Cache miss → calls `_model.generate(question)` on the loaded THEMIS inference engine
5. Returns `ToolResult` with text + error metadata
6. `server.py` appends legal disclaimer, returns formatted string to client
7. `metrics.py` records latency, `cache.py` stores result if temperature ≤ 0.1

---

## 3. TECH STACK + WHY, ONE LINE EACH

| Tech | Why |
|------|-----|
| **Python 3.11+** | Match Python version requirements of themis-llm SDK |
| **FastMCP (MCP Python SDK v1.x)** | Official MCP SDK, handles stdio/HTTP transport, tool/resource/prompt registration |
| **themis-llm SDK** | Pre-trained Mistral 7B LoRA on Indian law, already fine-tuned and published on HuggingFace |
| **Mistral 7B** | Best open-source 7B model for legal domain; LoRA fine-tuning gives legal accuracy without full fine-tune cost |
| **Hatchling** | Modern, fast Python build backend; lighter than setuptools for simple packages |
| **Ruff** | Faster than flake8+isort+black combined; single tool for lint+format |
| **Pytest** | Industry standard, works with hatchling's test config |
| **OpenTelemetry (optional)** | Production tracing without vendor lock-in |
| **Prometheus metrics** | Custom implementation to avoid heavy dependencies; just counters/histograms in text format |
| **Streamable HTTP** | Modern MCP transport for remote deployments, chosen over SSE for simplicity |
| **LRU cache with TTL** | Deterministic queries (temp ≤ 0.1) cached 5 min to avoid redundant GPU inference |

---

## 4. THE THREE HARDEST DECISIONS

**Decision 1: Removing fabricated metadata from tool responses.**
The original code returned `grounded`, `confidence`, `section`, `act`, `warning` fields on every response. When I audited the actual `GenerationResult` dataclass from the SDK, it only has `response`, `input_tokens`, `output_tokens`, `device`—no grounding detection exists. I had to choose: fabricate plausible-sounding values (which would be dishonest), or strip the fields entirely. I stripped them. The tradeoff was losing impressive-looking output metadata, but the alternative was shipping lies. The honest approach means the tool now returns just the text response with a disclaimer.

**Decision 2: The IPC↔BNS mapping table data integrity crisis.**
The original AI-generated mapping table had 182 entries. I verified 27 against official sources (NCRB, LawSikho) and found 12 were actively wrong (44%) and 8 were missing entirely. The hardest part was deciding how to handle the remaining 180 unverified entries. I chose to keep them with severe warnings rather than delete the feature entirely—users might find partial mappings useful as long as they know the limitations. But this means the tool is marked EXPERIMENTAL with explicit disclaimers on every response. The tradeoff: the mapper works but can't be trusted without external verification.

**Decision 3: Model loading in async lifespan vs. blocking startup.**
The MCP SDK's `lifespan` handler is async, but model loading (`inference.load_model()`) is synchronous and blocks for minutes while downloading ~13GB. I chose to load the model synchronously inside the async context manager, accepting that the server will block during startup. The alternative was background loading with a ready flag, but that adds complexity and race conditions. The pragmatic choice: block on startup, fail fast with clear error messages (GPU not found, OOM, network issues), and let the `/health` endpoint report 503 until ready.

---

## 5. ONE REAL FAILURE STORY

The IPC↔BNS mapper was the most embarrassing discovery. I had built a `themis_map_section` tool with 182 entries, confidently labeled it "Source: Ministry of Law and Justice, Government of India," and shipped it. When I actually fetched the NCRB official comparison table and spot-checked 27 entries, I found that IPC 420 (the most famous IPC section—"420" is Indian slang for fraudster) was mapped to BNS 345, when it should be BNS 318. IPC 379 (theft) was mapped to 304 instead of 303. Four entries were mapping to `bnss:` (the procedural code) instead of `bns:` (the penal code)—a category-level error, not just a wrong number.

How I diagnosed it: I fetched the official NCRB table, the LawSikho verified conversion table, and cross-referenced. The pattern was clear—the original table was a sequential mapping (IPC 302→BNS 103, IPC 303→BNS 104, etc.), which is fundamentally wrong because BNS sections aren't sequentially numbered from IPC.

What I changed: Rewrote the entire mapping table, keeping only verified entries, adding explicit warnings, and documenting the exact verification status (27 verified, 180 unverified). What I'd do differently now: never ship AI-generated legal reference data without external verification first. The lesson: in a legal tool, an unverified answer is worse than no answer.

---

## 6. LIKELY GOTCHA QUESTIONS

**Q: Why use a local LLM instead of calling an API like OpenAI?**
A: Indian law is a niche domain. General models hallucinate Indian statute references. The fine-tuned Mistral 7B is trained specifically on BNS/IPC/BNSS text, so it actually knows the section numbers and wording. Also, legal data is sensitive—local inference avoids sending client questions to third-party APIs.

**Q: How does the cache work, and why only for temperature ≤ 0.1?**
A: LRU cache with 128 entries and 5-minute TTL. Only caches when temperature ≤ 0.1 because higher temperatures produce non-deterministic outputs—caching a random answer would be wrong. The key is SHA-256 of (tool_name + all arguments).

**Q: What happens if the model isn't loaded yet when a request comes in?**
A: `tools.py` checks `_model is None` at the start of `ask()`. Returns a `ToolResult` with `error=True, error_class="SERVER_ERROR"`. The `/health` endpoint returns 503 with `model_loaded: false` until the lifespan handler completes.

**Q: How does the rate limiter work?**
A: Token bucket algorithm in `ratelimit.py`. Default: 30 requests per minute per tool. If exceeded, returns `RATE_LIMITED` error with seconds until reset. Checked before cache lookup, so rate-limited requests don't hit cache.

**Q: The mapper has 180 unverified entries. Isn't that worse than not having them?**
A: It's a documented tradeoff. The warnings are explicit: "UNVERIFIED and AI-generated. Do NOT treat as authoritative legal references." The alternative was either deleting the feature entirely (losing useful mappings for people who know to verify) or only shipping 27 verified entries (which would be incomplete). The choice was transparency over completeness.

**Q: Why is the `themis_ask` tool async but `themis_lookup` is sync?**
A: `themis_ask` needs `ctx.report_progress()` which is an async MCP SDK call. `themis_lookup` is pure dictionary lookup—no I/O, no model call, so sync is fine and faster. FastMCP handles the sync/async mismatch automatically.

**Q: What's the deployment model? Who runs this?**
A: Designed for individual developers running locally with a GPU. stdio transport for local use with Claude Desktop/opencode. Streamable HTTP for shared/team deployments. No cloud hosting required—the model runs on the user's machine.

---

## 7. NUMBERS TO HAVE READY

- **16 Python source files**, ~1,800 lines of code total
- **12 tests**, all passing
- **207 IPC↔BNS mappings** (27 verified, 180 unverified)
- **6 supported laws**: BNS (358 sections), BNSS (531), BSA (170), IPC (511), RTI (31), CPA (107)
- **~13GB GPU VRAM** required for model inference
- **~13GB disk** for model weights (Mistral 7B + LoRA adapter)
- **30 requests/minute** rate limit default
- **128 cache entries**, 5-minute TTL
- **6 MCP prompts** for common legal queries
- **4 resources** (disclaimer, acts list, law PDFs)
- **3 CI workflows**: test, lint, publish
- **Published to PyPI** as `themis-mcp` v1.0.0
- **MIT licensed**
- **Python 3.11+** required
