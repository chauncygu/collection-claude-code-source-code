
# A collection of the newest Claude Code open source

> Source archive of Claude Code and a clean-room Python rewrite research repository

## 🔥🔥🔥 News (Pacific Time)
- 19:45 PM · Mar 31, 2026: [Claude Code Technical Report](https://github.com/chauncygu/collection-claude-code-source-code/blob/main/docs/claude-code-deep-dive-xelatex.pdf)
- 17:13 PM · Mar 31, 2026: [Architecture Analysis of Claude Code (In Chinese)](https://mp.weixin.qq.com/s?__biz=MzI0ODk2NDIyMQ==&mid=2247502519&idx=1&sn=1072dd7a822a78709bc7cc3bf0e1dcc2&chksm=e8de6705e2bacc854211663aa02903738560f9e858eb6ce72b94c32fdbf67917badfab2d6536&mpshare=1&scene=1&srcid=0401KpkqfaXFBReRof6AwJ74&sharer_shareinfo=30fa54f1602d1d8bb1a65e7008074e08&sharer_shareinfo_first=30fa54f1602d1d8bb1a65e7008074e08#rd)
 - 16:43 PM · Mar 31, 2026: [An Overview of Claude Code Features (In Chinese)](https://mp.weixin.qq.com/s?__biz=MzAxODI5ODMwOA==&mid=2666572944&idx=1&sn=c54e34711e67a2e961acb341f51d2190&chksm=81ca164af949bdfe90a616c8ef8d7e729116a4a12a480cd9d012f42f5b8d7ecd6d05e284db09&mpshare=1&scene=1&srcid=04017JkKs9qrCh4AHcfZq7qL&sharer_shareinfo=95eb268167dd1b3d98271b8b26e7553e&sharer_shareinfo_first=95eb268167dd1b3d98271b8b26e7553e#rd)
- 15:00 PM · Mar 31, 2026: [Hacker News Community Discussion about Claude Code Leak](https://news.ycombinator.com/item?id=47586778)
- 9:50 AM · Mar 31, 2026: [Claude code memory analysis](https://x.com/henryl_ai/status/2039022608310808965)
- 9:48 AM · Mar 31, 2026: [Claude Code's source code appears to have leaked: here's what we know](https://venturebeat.com/technology/claude-codes-source-code-appears-to-have-leaked-heres-what-we-know)
- 9:04 AM · Mar 31, 2026: [Deconstructing the Claude Code Architecture (In Chinese)](https://mp.weixin.qq.com/s?__biz=MzA3NzUxMzM5MQ==&mid=2453898430&idx=1&sn=1c4051fb17a15b17e449b7eb85d3e1c5&chksm=897cc501d472cdd6916679a0766ab146b5347bc78e48171d9da97de282a05c10eea8d22c3605&mpshare=1&scene=1&srcid=0401oXuLa2VmhvrcRZk7VHfH&sharer_shareinfo=e7ff02258e887208db510104bc343079&sharer_shareinfo_first=6c39c564855be1e2372289b5c09b6247#rd)
- 7:07 AM · Mar 31, 2026: [A Walkthrough of Claude Code's Source Code (In Chinese)](https://mp.weixin.qq.com/s?__biz=MjM5ODI5Njc2MA==&mid=2655937729&idx=1&sn=0afb97062ef5f229910e3e54dd36abb6&chksm=bc66bca5b0f4171b56075506f208efea18381031c5ffa33070701ee1200bef7e411ea10188e9&mpshare=1&scene=1&srcid=0331PBEUSD8CVryQYEluyZbc&sharer_shareinfo=c5a329d2cc3ec432238f5fc1d9d70723&sharer_shareinfo_first=c5a329d2cc3ec432238f5fc1d9d70723#rd)
- 5:41 AM · Mar 31, 2026: [Why Claude Code Outperforms Other Tools: An Analysis](https://x.com/YukerX/status/2038959908968919297)
- 5:03 AM · Mar 31, 2026: [Anthropic's AI Coding Tool Leaks Its Own Source Code](https://www.ndtv.com/science/anthropics-ai-coding-tool-leaks-its-own-source-code-for-the-second-time-in-a-year-11291517)
- 3:28 AM · Mar 31, 2026: [Claude Code Source Code Unveiled: Prompts, Self-Healing Mechanisms, and Multi-Agent Architecture (In Chinese)](https://mp.weixin.qq.com/s?__biz=MzI3ODY3ODg2Nw==&mid=2247484425&idx=1&sn=f77d3b97e88cb8019f014ca2eb95db65&chksm=ea98ee5bb2249e1c637520cf02b525b98b434671f2cc23ec554e5faa868e890deeead939c578&mpshare=1&scene=1&srcid=0401kVgDQ41tx7AECPzvch3W&sharer_shareinfo=5d97c04d957d52383c9b59245e421c5a&sharer_shareinfo_first=5d97c04d957d52383c9b59245e421c5a#rd)
- 3:02 AM · Mar 31, 2026: [Community Reaction to the Claude Code Source Exposure](https://x.com/hank_aibtc/status/2038919948370616330)
- 2:57 AM · Mar 31, 2026: [The code behind Claude Code](https://x.com/mal_shaik/status/2038918662489510273)
- 1:23 AM · Mar 31, 2026: [A Viral Post on the Claude Code Source Leak](https://x.com/Fried_rice/status/2038894956459290963?s=20)

This repository contains two subprojects that study Claude Code (Anthropic’s official CLI tool) from two different angles:

| Subproject                                            | Language   | Nature                              | File Count  |
| ----------------------------------------------------- | ---------- | ----------------------------------- | ----------- |
| [claude-code-source-code](#1-claude-code-source-code) | TypeScript | Decompiled source archive (v2.1.88) | 1,884 files |
| [claw-code](#2-claw-code)                             | Python     | Clean-room architectural rewrite    | 66 files    |

---



## 1. claude-code-source-code

A decompiled/unpacked source archive of Claude Code v2.1.88, reconstructed from the npm package `@anthropic-ai/claude-code@2.1.88`, containing approximately 163,318 lines of TypeScript code.

### Overall Architecture

```text
claude-code-source-code/
├── src/
│   ├── main.tsx              # CLI entry and REPL bootstrap (4,683 lines)
│   ├── query.ts              # Core main agent loop (largest single file, 785KB)
│   ├── QueryEngine.ts        # SDK/Headless query lifecycle engine
│   ├── Tool.ts               # Tool interface definitions + buildTool factory
│   ├── commands.ts           # Slash command definitions (~25K lines)
│   ├── tools.ts              # Tool registration and presets
│   ├── context.ts            # User input context handling
│   ├── history.ts            # Session history management
│   ├── cost-tracker.ts       # API cost tracking
│   ├── setup.ts              # First-run initialization
│   │
│   ├── cli/                  # CLI infrastructure (stdio, structured transports)
│   ├── commands/             # ~87 slash command implementations
│   ├── components/           # React/Ink terminal UI (33 subdirectories)
│   ├── tools/                # 40+ tool implementations (44 subdirectories)
│   ├── services/             # Business logic layer (22 subdirectories)
│   ├── utils/                # Utility function library
│   ├── state/                # Application state management
│   ├── types/                # TypeScript type definitions
│   ├── hooks/                # React Hooks
│   ├── bridge/               # Claude Desktop remote bridge
│   ├── remote/               # Remote mode
│   ├── coordinator/          # Multi-agent coordination
│   ├── tasks/                # Task management
│   ├── assistant/            # KAIROS assistant mode
│   ├── memdir/               # Long-term memory management
│   ├── plugins/              # Plugin system
│   ├── voice/                # Voice mode
│   └── vim/                  # Vim mode
│
├── docs/                     # In-depth analysis docs (bilingual: Chinese/English)
│   ├── en/                   # English analysis
│   └── zh/                   # Chinese analysis
├── vendor/                   # Third-party dependencies
├── stubs/                    # Module stubs
├── types/                    # Global type definitions
├── utils/                    # Top-level utility functions
├── scripts/                  # Build scripts
└── package.json
```

### Core Execution Flow

```text
User Input
  ↓
processUserInput()         # Parse /slash commands
  ↓
query()                    # Main agent loop (query.ts)
  ├── fetchSystemPromptParts()    # Assemble system prompt
  ├── StreamingToolExecutor       # Parallel tool execution
  ├── autoCompact()               # Automatic context compression
  └── runTools()                  # Tool orchestration and scheduling
  ↓
yield SDKMessage           # Stream results back to the consumer
```

### Tech Stack

| Component       | Technology                               |
| --------------- | ---------------------------------------- |
| Language        | TypeScript 6.0+                          |
| Runtime         | Bun (compiled into Node.js >= 18 bundle) |
| Claude API      | Anthropic SDK                            |
| Terminal UI     | React + Ink                              |
| Code Bundling   | esbuild                                  |
| Data Validation | Zod                                      |
| Tool Protocol   | MCP (Model Context Protocol)             |

### Main Module Descriptions

#### Tool System (40+ tools)

| Category                    | Tools                                                     |
| --------------------------- | --------------------------------------------------------- |
| File Operations             | FileReadTool, FileEditTool, FileWriteTool                 |
| Code Search                 | GlobTool, GrepTool                                        |
| System Execution            | BashTool                                                  |
| Web Access                  | WebFetchTool, WebSearchTool                               |
| Task Management             | TaskCreateTool, TaskUpdateTool, TaskGetTool, TaskListTool |
| Sub-agents                  | AgentTool                                                 |
| Code Environments           | NotebookEditTool, REPLTool, LSPTool                       |
| Git Workflow                | EnterWorktreeTool, ExitWorktreeTool                       |
| Configuration & Permissions | ConfigTool, AskUserQuestionTool                           |
| Memory & Planning           | TodoWriteTool, EnterPlanModeTool, ExitPlanModeTool        |
| Automation                  | ScheduleCronTool, RemoteTriggerTool, SleepTool            |
| MCP Integration             | MCPTool                                                   |

#### Slash Commands (~87)

`/commit` `/commit-push-pr` `/review` `/resume` `/session` `/memory` `/config` `/skills` `/help` `/voice` `/desktop` `/mcp` `/permissions` `/theme` `/vim` `/copy` and more

#### Permission System

* Three modes: `default` (ask user) / `bypass` (auto-allow) / `strict` (auto-deny)
* Tool-level fine-grained control
* ML-based automated permission inference classifier
* Persistent storage of permission rules

#### Context Management

* Automatic compression strategies (`autoCompact`): reactive compression, micro-compression, trimmed compression
* Context collapsing (`CONTEXT_COLLAPSE`)
* Token counting and estimation
* Session transcript persistence

#### Analysis Documents (`docs/`)

| Document                                   | Content                                                                           |
| ------------------------------------------ | --------------------------------------------------------------------------------- |
| 01 - Telemetry and Privacy                 | Dual-layer analysis pipeline (Anthropic + Datadog), with no opt-out switch        |
| 02 - Hidden Features and Model Codenames   | Internal codenames such as Capybara, Tengu, Fennec, Numbat                        |
| 03 - Undercover Mode                       | Anthropic employees automatically entering undercover mode in public repositories |
| 04 - Remote Control and Emergency Switches | Hourly polling, 6+ killswitches, dangerous-change popups                          |
| 05 - Future Roadmap                        | KAIROS autonomous agent, voice mode, 17 unreleased tools                          |

---

## 2. claw-code

A clean-room Python rewrite of Claude Code (without including original source copies), focused on architectural mirroring and research. Built by [@instructkr](https://github.com/instructkr) (Sigrid Jin), and became one of the fastest GitHub repositories in the world to reach 30K stars.

### Overall Architecture

```text
claw-code/
├── src/
│   ├── __init__.py               # Package export interface
│   ├── main.py                   # CLI entry (~200 lines)
│   ├── query_engine.py           # Core query engine
│   ├── runtime.py                # Runtime session management
│   ├── models.py                 # Shared data classes
│   ├── commands.py               # Command metadata and execution framework
│   ├── tools.py                  # Tool metadata and execution framework
│   ├── permissions.py            # Permission context management
│   ├── context.py                # Ported context layer
│   ├── setup.py                  # Workspace initialization
│   ├── session_store.py          # Session persistence
│   ├── transcript.py             # Session transcript storage
│   ├── port_manifest.py          # Workspace manifest generation
│   ├── execution_registry.py     # Execution registry
│   ├── history.py                # History logs
│   ├── parity_audit.py           # Parity audit against TypeScript source
│   ├── remote_runtime.py         # Remote mode simulation
│   ├── bootstrap_graph.py        # Bootstrap graph generation
│   ├── command_graph.py          # Command graph partitioning
│   ├── tool_pool.py              # Tool pool assembly
│   │
│   ├── reference_data/           # JSON snapshot data (drives command/tool metadata)
│   │   ├── commands_snapshot.json
│   │   └── tools_snapshot.json
│   │
│   ├── commands/                 # Command implementation subdirectory
│   ├── tools/                    # Tool implementation subdirectory
│   ├── services/                 # Business logic services
│   ├── components/               # Terminal UI components (Python version)
│   ├── state/                    # State management
│   ├── types/                    # Type definitions
│   ├── utils/                    # Utility functions
│   ├── remote/                   # Remote mode
│   ├── bridge/                   # Bridge modules
│   ├── hooks/                    # Hook system
│   ├── memdir/                   # Memory management
│   ├── vim/                      # Vim mode
│   ├── voice/                    # Voice mode
│   └── plugins/                  # Plugin system
│
└── tests/                        # Validation tests
```

### Core Classes

| Class / Module          | Responsibility                                                                      |
| ----------------------- | ----------------------------------------------------------------------------------- |
| `QueryEnginePort`       | Query engine handling message submission, streaming output, and session compression |
| `PortRuntime`           | Runtime manager responsible for routing, session startup, and turn-loop execution   |
| `PortManifest`          | Workspace manifest that generates Markdown overviews                                |
| `ToolPermissionContext` | Tool permission context (`allow` / `deny` / `ask`)                                  |
| `WorkspaceSetup`        | Environment detection and initialization reporting                                  |
| `TranscriptStore`       | Session transcript storage with append, compaction, and replay support              |

### CLI Commands

```bash
python3 -m src.main [COMMAND]

# Overview
summary              # Markdown workspace overview
manifest             # Print manifest
subsystems           # List Python modules

# Routing and indexing
commands             # List all commands
tools                # List all tools
route [PROMPT]       # Route prompt to corresponding command/tool

# Execution
bootstrap [PROMPT]   # Start runtime session
turn-loop [PROMPT]   # Run turn loop (--max-turns)
exec-command NAME    # Execute command
exec-tool NAME       # Execute tool

# Session management
flush-transcript     # Persist session transcript
load-session ID      # Load saved session

# Remote mode
remote-mode TARGET   # Simulate remote control
ssh-mode TARGET      # Simulate SSH branch
teleport-mode TARGET # Simulate Teleport branch

# Audit and config
parity-audit         # Compare consistency with TypeScript source
setup-report         # Startup configuration report
bootstrap-graph      # Bootstrap phase graph
command-graph        # Command graph partition view
tool-pool            # Tool pool assembly view
```

### Design Features

* **Snapshot-driven**: command/tool metadata is loaded through JSON snapshots without requiring full logical implementations
* **Clean-room rewrite**: does not include original TypeScript code; independently implemented
* **Parity audit**: built-in `parity_audit.py` tracks gaps from the original implementation
* **Lightweight architecture**: core framework implemented in 66 files, suitable for learning and extension

---

## Comparison of the Two Projects

| Dimension               | claude-code-source-code                   | claw-code                                        |
| ----------------------- | ----------------------------------------- | ------------------------------------------------ |
| Language                | TypeScript                                | Python                                           |
| Code Size               | ~163,000 lines                            | ~5,000 lines                                     |
| Nature                  | Decompiled source archive                 | Clean-room architectural rewrite                 |
| Functional Completeness | Complete (100%)                           | Architectural framework (~20%)                   |
| Core Loop               | `query.ts` (785KB)                        | `QueryEnginePort` (~200 lines)                   |
| Tool System             | 40+ fully implemented tools               | Snapshot metadata + execution framework          |
| Command System          | ~87 fully implemented commands            | Snapshot metadata + execution framework          |
| Main Use Case           | Deep study of full implementation details | Architectural understanding and porting research |

---

## License and Disclaimer

This repository is for academic research and educational purposes only. Both subprojects are built from publicly accessible information. Users are responsible for complying with applicable laws, regulations, and service terms.

