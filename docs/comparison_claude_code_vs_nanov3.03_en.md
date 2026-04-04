# Claude Code vs Nano Claude Code v3.03: Comparative Analysis

## Overview

| Dimension | Claude Code (TypeScript) | Nano Claude Code (Python) |
|-----------|--------------------------|---------------------------|
| **Language** | TypeScript + React/Ink | Python 3.8+ |
| **File Count** | 1,332 TS/TSX files | 51 Python files |
| **Code Size** | ~283K lines | ~10.2K lines |
| **Tool Count** | 44+ tools | 21 tools |
| **Slash Commands** | 88 | 17 |
| **Model Providers** | Anthropic only | 7+ providers |

---

## Architecture Comparison

### Agent Loop (Core)

**Claude Code** — `QueryEngine.ts` (~47KB)
- Complex message stream management with extended thinking support
- Multi-layer permission system (MDM, team management, per-tool gates)
- Built-in context compaction scheduler

**Nano Claude Code** — `agent.py` (174 lines)
- Generator-based event stream (`yield TextChunk | ToolStart | ToolEnd`)
- Clean event flow, highly readable code
- Cooperative cancellation support for sub-agents

### Tool System

**Claude Code**
- Each tool in its own directory with full schema, permission docs, and tests
- Complex inter-tool dependencies (EnterWorktree → isolated env → ExitWorktree)
- Advanced tools: `SyntheticOutputTool`, `RemoteTriggerTool`, etc.

**Nano Claude Code**
- `ToolDef` registry pattern — any module can dynamically inject via `register_tool()`
- `read_only` / `concurrent_safe` flags drive automatic permission decisions
- Output truncation (32KB cap) prevents context bloat

### UI Rendering

**Claude Code**: React + Ink, full component tree, diff visualization, dialogs, progress bars, streaming rendering

**Nano Claude Code**: `rich` library, Markdown syntax highlighting — simple but sufficient

---

## Strengths and Weaknesses

### Claude Code Strengths
1. **Engineering completeness** — 88 slash commands, 44 tools, enterprise-grade permission management (MDM/team config)
2. **UI quality** — React/Ink component tree, high-quality streaming rendering, fine-grained diff visualization
3. **Service layer depth** — LSP integration, Analytics/Telemetry, OAuth, GrowthBook feature flags
4. **Session memory** — AI-driven memory extraction (`extractMemories` service)
5. **Production reliability** — Single bundled `cli.js` (12MB), comprehensive test coverage, version-locked

### Claude Code Weaknesses
1. **Single provider** — Anthropic API only, no OpenAI/Gemini/local model support
2. **Poor code readability** — 1,332 files + decompiled code, scattered logic, hard to modify
3. **Heavy build dependency** — Bun + esbuild + TypeScript; changes require a full build chain
4. **Closed extensibility** — Feature flags (`internal-only modules`) dead-code-eliminated at compile time, no external extension

### Nano Claude Code Strengths
1. **Multi-provider** — Anthropic/OpenAI/Gemini/Kimi/Qwen/DeepSeek/Ollama with auto-detection
2. **Highly readable** — 51 files, 10K lines, architecture immediately apparent, great for learning and research
3. **Zero build** — Pure Python, `pip install` ready, changes take effect immediately
4. **Dynamic extensibility** — Runtime injection via `register_tool()`, Plugin system supports git URL installation
5. **Markdown Skills** — Custom skills via `~/.nano_claude/skills/*.md` without touching source code
6. **Task dependency graph** — `task/store.py` has `blocks/blocked_by` dependency tracking (absent in Claude Code)

### Nano Claude Code Weaknesses
1. **Thin UI** — No diff visualization, no dialog system, no progress bar components
2. **Tool coverage gaps** — Missing `WebSearch` (needs API key), `NotebookEdit`, `LSP Diagnostics`
3. **Weak security posture** — No MDM control, no team permission sync, no keychain integration
4. **Performance** — Slower Python startup, large file handling slower than Node.js
5. **Immature sub-agents** — `subagent.py` still has stubs; multi-agent coordination less stable than the original

---

## Key Design Differences

### Context Compaction Strategy

| | Claude Code | Nano Claude Code |
|-|-------------|-----------------|
| Trigger | Exact token counting | `len/3.5` estimate at 70% threshold |
| Compression layers | Single-layer AI summarization | Two layers: Snip (rule-based) + AI summary |
| Retention policy | System-level scheduler | `preserve_last_n_turns` parameter |

### Memory System

Claude Code's `extractMemories` service uses AI to proactively extract knowledge from conversations. Nano's `memory/` module is tool-driven explicit storage (`MemorySave` tool calls) — more controllable but requires the model to actively use it.

### Module Structure

**Claude Code** (services layer):
```
services/
├── api/          # Claude API, OAuth, analytics
├── mcp/          # Model Context Protocol client
├── plugins/      # Plugin installation/execution
├── SessionMemory/# Persistent session state
├── compact/      # Context compression
├── lsp/          # Language Server Protocol
├── extractMemories/ # AI-driven memory extraction
└── MagicDocs/    # Documentation generation
```

**Nano Claude Code** (flat packages):
```
mcp/          # MCP client (stdio/SSE/HTTP)
memory/       # Persistent dual-scope memory
task/         # Task management with dependency graph
skill/        # Markdown-based skill loader
multi_agent/  # Sub-agent lifecycle + git worktrees
plugin/       # Plugin loader/recommend system
```

---

## Supported Models

**Claude Code**: Anthropic only (`claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`)

**Nano Claude Code**:

| Provider | Models |
|----------|--------|
| Anthropic | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 |
| OpenAI | gpt-4o, gpt-4o-mini, o1, o3-mini |
| Google | gemini-2.5-pro, gemini-2.0-flash, gemini-1.5-pro |
| Moonshot | kimi-latest |
| Alibaba | qwen-max, qwen-plus |
| Zhipu | glm-4 |
| DeepSeek | deepseek-chat, deepseek-reasoner |
| Ollama (local) | llama3.3, qwen2.5-coder, deepseek-r1, mistral, phi4, codellama |

---

## Summary

Nano Claude Code is a **minimal reimplementation** of Claude Code's core philosophy. It surpasses the original in multi-provider support and code readability, making it ideal as a research foundation or personal tool. Claude Code is a complete engineering product with unmatched UI, security, and enterprise features. The most valuable gaps to bridge are: **WebSearch tool**, **more robust sub-agent coordination**, and **diff visualization rendering**.

| Gap | Priority | Notes |
|-----|----------|-------|
| WebSearch tool | High | Needs a search API backend |
| Diff visualization | Medium | Rich has diff support |
| Sub-agent stability | Medium | `subagent.py` stubs need fleshing out |
| LSP diagnostics | Low | Requires language server per language |
| Keychain integration | Low | `keyring` library available for Python |
