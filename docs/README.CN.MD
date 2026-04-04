[English](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/README.md) | 中文 |[한국어](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.KO.MD) | [日本語](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.JP.MD) | [Deutsch](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.DE.MD) | [Português](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/README.ES.MD)

<div align="center">
  <a href="https://github.com/SafeRL-Lab/nano-claude-code">
    <img src="https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/logo-v1.png" alt="Logo" width="280"> 
  </a>

<h1 align="center" style="font-size: 30px;"><strong><em>Nano Claude Code</em></strong>：一个快速、易用、支持任意模型的 Claude Code Python 复现版本</h1>
<p align="center">
    <a href="https://github.com/chauncygu/collection-claude-code-source-code">最新的 Claude Code 相关源码资源</a>
    ·
    <a href="https://github.com/SafeRL-Lab/nano-claude-code/issues">Issue</a>
    ·
    <a href="https://deepwiki.com/SafeRL-Lab/nano-claude-code">简要介绍</a>
</p>
</div>

<div align="center">
 <img src="https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/demo.gif" width="850"/> 
</div>
<div align="center">
<center style="color:#000000;text-decoration:underline"> </center>
</div>

---

## 🔥🔥🔥 更新动态（太平洋时间）
- 2026 年 4 月 3 日 06:00 PM：**v3.03** —— 任务管理系统（`task/` 包）：提供 `TaskCreate` / `TaskUpdate` / `TaskGet` / `TaskList` 工具，支持顺序 ID、依赖边（`blocks` / `blocked_by`）、元数据、持久化到 `.nano_claude/tasks.json`、线程安全存储、`/tasks` REPL 命令，以及 37 个新测试（**约 9500 行** Python 代码）。
- 2026 年 4 月 3 日 02:50 PM：**v3.02** —— 插件系统（`plugin/` 包）：支持通过 `/plugin` CLI 进行安装 / 卸载 / 启用 / 禁用 / 更新；包含推荐引擎（关键词 + 标签匹配）、多作用域（用户 / 项目）、基于 git 的插件市场。新增 `AskUserQuestion` 工具：任务中途可交互式向用户提问，支持编号选项和自由文本输入（**约 8500 行** Python 代码）。
- 2026 年 4 月 3 日 10:00 AM：**v3.01** —— 支持 MCP（Model Context Protocol，模型上下文协议）：新增 `mcp/` 包，支持 stdio + SSE + HTTP 传输、自动工具发现、`/mcp` 命令，以及 34 个新测试（**约 7000 行** Python 代码）。
- 2026 年 4 月 2 日 12:20 PM：**v3.0** —— 多智能体包（`multi_agent/`）、记忆包（`memory/`）、技能包（`skill/`），内置技能、参数替换、fork/inline 执行、AI 记忆搜索、git worktree 隔离、智能体类型定义（**约 5000 行** Python 代码），详见 [更新说明](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/update_readme_v3.0.md)。
- 2026 年 4 月 2 日 10:00 AM：**v2.0** —— 上下文压缩、记忆、子智能体、技能、diff 视图、工具插件系统（**约 3400 行** Python 代码）。
- 2026 年 4 月 1 日 01:47 PM：支持 VLLM 推理（**约 2000 行** Python 代码）。
- 2026 年 4 月 1 日 11:30 AM：支持更多**闭源模型**和**开源模型**：Claude、GPT、Gemini、Kimi、Qwen、Zhipu、DeepSeek，以及通过 Ollama 或任意 OpenAI 兼容端点接入的本地开源模型（**约 1700 行** Python 代码）。
- 2026 年 4 月 1 日 09:50 AM：支持更多**闭源模型**：Claude、GPT、Gemini（**约 1300 行** Python 代码）。
- 2026 年 4 月 1 日 08:23 AM：发布 Nano Claude Code 初始版本（**约 900 行** Python 代码）。

---

# Nano Claude Code

Nano Claude Code：一个**轻量级**、**易于使用**的 Claude Code Python 复现版本，**支持任意模型**，例如 Claude、GPT、Gemini、Kimi、Qwen、Zhipu、DeepSeek，以及通过 Ollama 或任意 OpenAI 兼容端点接入的本地开源模型。

---

## 目录
  * [为什么选择 Nano Claude Code](#为什么选择-nano-claude-code)
  * [功能特性](#功能特性)
  * [支持的模型](#支持的模型)
  * [安装](#安装)
  * [使用方式：闭源 API 模型](#使用方式闭源-api-模型)
  * [使用方式：开源模型（本地）](#使用方式开源模型本地)
  * [模型名称格式](#模型名称格式)
  * [CLI 参考](#cli-参考)
  * [Slash 命令（REPL）](#slash-命令repl)
  * [配置 API Key](#配置-api-key)
  * [权限系统](#权限系统)
  * [内置工具](#内置工具)
  * [记忆](#记忆)
  * [技能](#技能)
  * [子智能体](#子智能体)
  * [MCP（模型上下文协议）](#mcp模型上下文协议)
  * [插件系统](#插件系统)
  * [AskUserQuestion 工具](#askuserquestion-工具)
  * [任务管理](#任务管理)
  * [上下文压缩](#上下文压缩)
  * [Diff 视图](#diff-视图)
  * [CLAUDE.md 支持](#claudemd-支持)
  * [会话管理](#会话管理)
  * [项目结构](#项目结构)
  * [FAQ](#faq)

## 为什么选择 Nano Claude Code

Claude Code 是一个强大、面向生产环境的 AI 编码助手——但它的源码是一个编译后的 12 MB TypeScript/Node.js bundle（约 1300 个文件，约 28.3 万行代码）。它与 Anthropic API 强绑定，难以修改，也无法运行在本地模型或其他模型之上。

**Nano Claude Code** 用约 1 万行可读的 Python 重写了相同的核心循环：保留真正需要的部分，去掉不必要的复杂性。更多详细分析可见（Nano Claude Code v3.03）：[英文版](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/comparison_claude_code_vs_nano_v3.03_en.md) 与 [中文版](https://github.com/SafeRL-Lab/nano-claude-code/blob/main/docs/comparison_claude_code_vs_nano_v3.03_cn.md)。

### 一图速览

| 维度 | Claude Code（TypeScript） | Nano Claude Code（Python） |
|-----------|--------------------------|---------------------------|
| 语言 | TypeScript + React/Ink | Python 3.8+ |
| 源文件数量 | ~1,332 个 TS/TSX 文件 | 51 个 Python 文件 |
| 代码行数 | ~283K | ~10.2K |
| 内置工具 | 44+ | 21 |
| Slash 命令 | 88 | 17 |
| 模型提供方 | 仅 Anthropic | 7+（Anthropic · OpenAI · Gemini · Kimi · Qwen · DeepSeek · Ollama · …） |
| 本地模型 | 不支持 | 支持 —— Ollama、LM Studio、vLLM、任意 OpenAI 兼容端点 |
| 是否需要构建步骤 | 需要（Bun + esbuild） | 不需要 —— 直接运行 `python nano_claude.py` |
| 运行时扩展性 | 封闭（编译期） | 开放 —— 可在运行时 `register_tool()`，支持 Markdown 技能与 git 插件 |
| 任务依赖图 | 不支持 | 支持 —— `task/` 包中的 `blocks` / `blocked_by` 边 |

### Claude Code 的优势

- **UI 质量** —— 基于 React/Ink 的组件树，支持流式渲染、细粒度 diff 可视化和对话系统。
- **工具广度** —— 44 个工具，包括 `NotebookEdit`、`LSP Diagnostics`、`RemoteTrigger`、`EnterWorktree` 等。
- **企业级特性** —— MDM 管理配置、团队权限同步、OAuth、钥匙串存储、GrowthBook 功能开关。
- **AI 驱动的记忆提取** —— `extractMemories` 服务无需显式工具调用即可主动从对话中抽取知识。
- **生产可靠性** —— 单文件分发 `cli.js`、完整测试覆盖、版本锁定发布。

### Nano Claude Code 的优势

- **多提供方支持** —— 通过 `--model` 或 `/model` 可在 Claude、GPT-4o、Gemini 2.5 Pro、DeepSeek、Qwen 或本地 Llama 模型之间切换——无需重新编译。
- **本地模型支持** —— 可通过 Ollama、LM Studio 或任何 vLLM 托管模型完全离线运行。
- **源码可读性高** —— 整个智能体核心循环仅 174 行（`agent.py`）。任何 Python 开发者都能在几分钟内看懂、fork 和扩展。
- **零构建** —— `pip install -r requirements.txt` 即可运行。改动立即生效。
- **动态可扩展性** —— 可在运行时通过 `register_tool(ToolDef(...))` 注册新工具，从 git URL 安装技能包，或接入任意 MCP 服务器。
- **任务依赖图** —— `TaskCreate` / `TaskUpdate` 支持 `blocks` / `blocked_by` 依赖边，可进行结构化多步规划（Claude Code 暂不支持）。
- **双层上下文压缩** —— 基于规则的裁剪 + AI 摘要，可通过 `preserve_last_n_turns` 配置。

### 关键设计差异

**智能体循环（Agent loop）** —— Nano 使用 Python 生成器，`yield` 出类型化事件（`TextChunk`、`ToolStart`、`ToolEnd`、`TurnDone`）。整个循环都在一个文件中，便于添加 hook、自定义渲染器或日志。

**工具注册** —— 每个工具都是一个 `ToolDef(name, schema, func, read_only, concurrent_safe)` 数据类。任何模块都可以在导入时调用 `register_tool()`；MCP 服务器、插件和技能都使用同一机制。

**上下文压缩**

| | Claude Code | Nano Claude Code |
|-|-------------|-----------------|
| 触发方式 | 精确 token 计数 | 用 `len / 3.5` 估算，在 70% 时触发 |
| 第一层 | — | Snip：截断旧工具输出（无 API 成本） |
| 第二层 | AI 摘要 | 对旧轮次进行 AI 摘要 |
| 控制方式 | 系统内部管理 | `preserve_last_n_turns` 参数 |

**记忆** —— Claude Code 的 `extractMemories` 服务让模型主动暴露事实。Nano 的 `memory/` 包是工具驱动的：模型显式调用 `MemorySave`，因此行为更可预测、更可审计。

### 谁适合使用 Nano Claude Code

- 想把**本地模型或非 Anthropic 模型**用作编码助手的开发者。
- 研究**智能体编码助手如何工作**的研究者——整个系统一屏可看完。
- 需要一个**可 hack、可扩展的基线系统**的团队，用来添加专有工具、自定义权限策略或专用智能体类型。
- 想获得 Claude Code 风格生产力、但**不想引入 Node.js 构建链**的用户。

---

## 功能特性

| 功能 | 说明 |
|---|---|
| 多提供方 | Anthropic · OpenAI · Gemini · Kimi · Qwen · Zhipu · DeepSeek · Ollama · LM Studio · 自定义端点 |
| 交互式 REPL | readline 历史记录、Tab 自动补全 slash 命令 |
| 智能体循环 | 流式 API + 自动工具调用循环 |
| 21 个内置工具 | Read · Write · Edit · Bash · Glob · Grep · WebFetch · WebSearch · MemorySave · MemoryDelete · MemorySearch · MemoryList · Agent · SendMessage · CheckAgentResult · ListAgentTasks · ListAgentTypes · Skill · SkillList · AskUserQuestion · *（MCP + 插件工具启动时自动加入）* |
| MCP 集成 | 可连接任意 MCP 服务器（stdio/SSE/HTTP），工具自动注册并可由 Claude 调用 |
| 插件系统 | 支持从 git URL 或本地路径安装 / 卸载 / 启用 / 禁用 / 更新插件；支持多作用域（用户 / 项目）和推荐引擎 |
| AskUserQuestion | Claude 可以在任务中途暂停并向用户提出澄清问题，支持可选编号选项 |
| 任务管理 | TaskCreate/Update/Get/List 工具；顺序 ID；依赖边；元数据；持久化到 `.nano_claude/tasks.json`；`/tasks` REPL 命令 |
| Diff 视图 | 对 Edit 和 Write 显示 git 风格红绿 diff |
| 上下文压缩 | 自动压缩长对话，避免超出模型上下文限制 |
| 持久记忆 | 双作用域记忆（用户 + 项目），4 种类型，AI 搜索，过期提醒 |
| 多智能体 | 可启动类型化子智能体（coder/reviewer/researcher/...），支持 git worktree 隔离与后台模式 |
| 技能 | 内置 `/commit` · `/review`，支持自定义 Markdown 技能，带参数替换和 fork/inline 执行 |
| 插件工具 | 通过 `tool_registry.py` 注册自定义工具 |
| 权限系统 | `auto` / `accept-all` / `manual` 三种模式 |
| 17 个 slash 命令 | `/model` · `/config` · `/save` · `/cost` · `/memory` · `/skills` · `/agents` · … |
| 上下文注入 | 自动加载 `CLAUDE.md`、git 状态、当前工作目录、持久记忆 |
| 会话持久化 | 将对话保存 / 加载到 `~/.nano_claude/sessions/` |
| Extended Thinking | 可开启 / 关闭（仅限 Claude 模型） |
| 成本跟踪 | Token 使用量 + 预估美元成本 |
| 非交互模式 | `--print` 标志，适合脚本 / CI |

---

## 支持的模型

### 闭源模型（API）

| 提供方 | 模型 | 上下文 | 优势 | API Key 环境变量 |
|---|---|---|---|---|
| **Anthropic** | `claude-opus-4-6` | 200k | 能力最强，适合复杂推理 | `ANTHROPIC_API_KEY` |
| **Anthropic** | `claude-sonnet-4-6` | 200k | 速度与质量平衡 | `ANTHROPIC_API_KEY` |
| **Anthropic** | `claude-haiku-4-5-20251001` | 200k | 快速、成本低 | `ANTHROPIC_API_KEY` |
| **OpenAI** | `gpt-4o` | 128k | 强多模态与编码能力 | `OPENAI_API_KEY` |
| **OpenAI** | `gpt-4o-mini` | 128k | 快、便宜 | `OPENAI_API_KEY` |
| **OpenAI** | `o3-mini` | 200k | 推理能力强 | `OPENAI_API_KEY` |
| **OpenAI** | `o1` | 200k | 高级推理 | `OPENAI_API_KEY` |
| **Google** | `gemini-2.5-pro-preview-03-25` | 1M | 长上下文、多模态 | `GEMINI_API_KEY` |
| **Google** | `gemini-2.0-flash` | 1M | 快速、大上下文 | `GEMINI_API_KEY` |
| **Google** | `gemini-1.5-pro` | 2M | 最大上下文窗口 | `GEMINI_API_KEY` |
| **Moonshot (Kimi)** | `moonshot-v1-8k` | 8k | 中英文能力 | `MOONSHOT_API_KEY` |
| **Moonshot (Kimi)** | `moonshot-v1-32k` | 32k | 中英文能力 | `MOONSHOT_API_KEY` |
| **Moonshot (Kimi)** | `moonshot-v1-128k` | 128k | 长上下文 | `MOONSHOT_API_KEY` |
| **Alibaba (Qwen)** | `qwen-max` | 32k | 最强 Qwen 质量 | `DASHSCOPE_API_KEY` |
| **Alibaba (Qwen)** | `qwen-plus` | 128k | 平衡型 | `DASHSCOPE_API_KEY` |
| **Alibaba (Qwen)** | `qwen-turbo` | 1M | 快速、便宜 | `DASHSCOPE_API_KEY` |
| **Alibaba (Qwen)** | `qwq-32b` | 32k | 强推理 | `DASHSCOPE_API_KEY` |
| **Zhipu (GLM)** | `glm-4-plus` | 128k | 最强 GLM 质量 | `ZHIPU_API_KEY` |
| **Zhipu (GLM)** | `glm-4` | 128k | 通用用途 | `ZHIPU_API_KEY` |
| **Zhipu (GLM)** | `glm-4-flash` | 128k | 提供免费档位 | `ZHIPU_API_KEY` |
| **DeepSeek** | `deepseek-chat` | 64k | 编码能力强 | `DEEPSEEK_API_KEY` |
| **DeepSeek** | `deepseek-reasoner` | 64k | 思维链推理 | `DEEPSEEK_API_KEY` |

### 开源模型（本地，通过 Ollama）

| 模型 | 参数规模 | 优势 | 拉取命令 |
|---|---|---|---|
| `llama3.3` | 70B | 通用、推理强 | `ollama pull llama3.3` |
| `llama3.2` | 3B / 11B | 轻量 | `ollama pull llama3.2` |
| `qwen2.5-coder` | 7B / 32B | **最适合编码任务** | `ollama pull qwen2.5-coder` |
| `qwen2.5` | 7B / 72B | 中英文能力 | `ollama pull qwen2.5` |
| `deepseek-r1` | 7B–70B | 推理、数学 | `ollama pull deepseek-r1` |
| `deepseek-coder-v2` | 16B | 编码 | `ollama pull deepseek-coder-v2` |
| `mistral` | 7B | 快速、高效 | `ollama pull mistral` |
| `mixtral` | 8x7B | 强大的 MoE 模型 | `ollama pull mixtral` |
| `phi4` | 14B | 微软模型，推理强 | `ollama pull phi4` |
| `gemma3` | 4B / 12B / 27B | Google 开源模型 | `ollama pull gemma3` |
| `codellama` | 7B / 34B | 代码生成 | `ollama pull codellama` |

> **注意：** 工具调用要求模型支持函数调用。推荐的本地模型：`qwen2.5-coder`、`llama3.3`、`mistral`、`phi4`。

---

## 安装

```bash
git clone <repo-url>
cd nano_claude_code

pip install -r requirements.txt
# 或手动安装：
pip install anthropic openai httpx rich
```

---

## 使用方式：闭源 API 模型

### Anthropic Claude

在 [console.anthropic.com](https://console.anthropic.com) 获取 API Key。

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-...

# 默认模型（claude-opus-4-6）
python nano_claude.py

# 选择特定模型
python nano_claude.py --model claude-sonnet-4-6
python nano_claude.py --model claude-haiku-4-5-20251001

# 启用 Extended Thinking
python nano_claude.py --model claude-opus-4-6 --thinking --verbose
```

### OpenAI GPT

在 [platform.openai.com](https://platform.openai.com) 获取 API Key。

```bash
export OPENAI_API_KEY=sk-...

python nano_claude.py --model gpt-4o
python nano_claude.py --model gpt-4o-mini
python nano_claude.py --model gpt-4.1-mini
python nano_claude.py --model o3-mini
```

### Google Gemini

在 [aistudio.google.com](https://aistudio.google.com) 获取 API Key。

```bash
export GEMINI_API_KEY=AIza...

python nano_claude.py --model gemini/gemini-2.0-flash
python nano_claude.py --model gemini/gemini-1.5-pro
python nano_claude.py --model gemini/gemini-2.5-pro-preview-03-25
```

### Kimi（Moonshot AI）

在 [platform.moonshot.cn](https://platform.moonshot.cn) 获取 API Key。

```bash
export MOONSHOT_API_KEY=sk-...

python nano_claude.py --model kimi/moonshot-v1-32k
python nano_claude.py --model kimi/moonshot-v1-128k
```

### Qwen（Alibaba DashScope）

在 [dashscope.aliyun.com](https://dashscope.aliyun.com) 获取 API Key。

```bash
export DASHSCOPE_API_KEY=sk-...

python nano_claude.py --model qwen/Qwen3.5-Plus
python nano_claude.py --model qwen/Qwen3-MAX
python nano_claude.py --model qwen/Qwen3.5-Flash
```

### Zhipu GLM

在 [open.bigmodel.cn](https://open.bigmodel.cn) 获取 API Key。

```bash
export ZHIPU_API_KEY=...

python nano_claude.py --model zhipu/glm-4-plus
python nano_claude.py --model zhipu/glm-4-flash   # 免费档
```

### DeepSeek

在 [platform.deepseek.com](https://platform.deepseek.com) 获取 API Key。

```bash
export DEEPSEEK_API_KEY=sk-...

python nano_claude.py --model deepseek/deepseek-chat
python nano_claude.py --model deepseek/deepseek-reasoner
```

---

## 使用方式：开源模型（本地）

### 方案 A —— Ollama（推荐）

Ollama 可以零配置地在本地运行模型，不需要 API Key。

**第 1 步：安装 Ollama**

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# 或从 https://ollama.com/download 下载
```

**第 2 步：拉取模型**

```bash
# 最适合编码（推荐）
ollama pull qwen2.5-coder          # 4.7 GB (7B)
ollama pull qwen2.5-coder:32b      # 19 GB (32B)

# 通用模型
ollama pull llama3.3               # 42 GB (70B)
ollama pull llama3.2               # 2.0 GB (3B)

# 推理模型
ollama pull deepseek-r1            # 4.7 GB (7B)
ollama pull deepseek-r1:32b        # 19 GB (32B)

# 其他模型
ollama pull phi4                   # 9.1 GB (14B)
ollama pull mistral                # 4.1 GB (7B)
```

**第 3 步：启动 Ollama 服务**（macOS 会自动运行；Linux 需手动启动）

```bash
ollama serve     # 启动在 http://localhost:11434
```

**第 4 步：运行 nano claude**

```bash
python nano_claude.py --model ollama/qwen2.5-coder
python nano_claude.py --model ollama/llama3.3
python nano_claude.py --model ollama/deepseek-r1
```

**查看本地可用模型列表：**

```bash
ollama list
```

然后可使用列表中的任意模型：

```bash
python nano_claude.py --model ollama/<model-name>
```

---

### 方案 B —— LM Studio

LM Studio 提供图形界面来下载和运行模型，并带有内置的 OpenAI 兼容服务器。

**第 1 步：** 下载并安装 [LM Studio](https://lmstudio.ai)。

**第 2 步：** 在 LM Studio 内搜索并下载模型（GGUF 格式）。

**第 3 步：** 打开 **Local Server** 标签页 → 点击 **Start Server**（默认端口：1234）。

**第 4 步：**

```bash
python nano_claude.py --model lmstudio/<model-name>
# 例如：
python nano_claude.py --model lmstudio/phi-4-GGUF
python nano_claude.py --model lmstudio/qwen2.5-coder-7b
```

模型名称应与 LM Studio 服务器状态栏显示的名称一致。

---

### 方案 C —— vLLM / 自托管 OpenAI 兼容服务器

适用于自托管推理服务器（vLLM、TGI、llama.cpp server 等），只要它暴露的是 OpenAI 兼容 API：

方案 C 快速开始：
第 1 步：启动 vLLM：
```bash
CUDA_VISIBLE_DEVICES=7 python -m vllm.entrypoints.openai.api_server \
      --model Qwen/Qwen2.5-Coder-7B-Instruct \
      --host 0.0.0.0 \
      --port 8000 \
      --enable-auto-tool-choice \
      --tool-call-parser hermes
```

第 2 步：启动 nano claude：
```bash
export CUSTOM_BASE_URL=http://localhost:8000/v1
export CUSTOM_API_KEY=none
python nano_claude.py --model custom/Qwen/Qwen2.5-Coder-7B-Instruct
```

```bash
# 示例：vLLM 部署 Qwen2.5-Coder-32B
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-Coder-32B-Instruct \
    --port 8000

# 然后运行 nano claude 并指向你的服务器：
python nano_claude.py
```

在 REPL 中：

```text
/config custom_base_url=http://localhost:8000/v1
/config custom_api_key=token-abc123    # 如无鉴权可跳过
/model custom/Qwen2.5-Coder-32B-Instruct
```

或通过环境变量设置：

```bash
export CUSTOM_BASE_URL=http://localhost:8000/v1
export CUSTOM_API_KEY=token-abc123

python nano_claude.py --model custom/Qwen2.5-Coder-32B-Instruct
```

对于远程 GPU 服务器：

```text
/config custom_base_url=http://192.168.1.100:8000/v1
/model custom/your-model-name
```

---

## 模型名称格式

支持三种等价格式：

```bash
# 1. 根据前缀自动识别（适用于常见模型）
python nano_claude.py --model gpt-4o
python nano_claude.py --model gemini-2.0-flash
python nano_claude.py --model deepseek-chat

# 2. 使用斜杠显式指定提供方
python nano_claude.py --model ollama/qwen2.5-coder
python nano_claude.py --model kimi/moonshot-v1-128k

# 3. 使用冒号显式指定提供方（也支持）
python nano_claude.py --model kimi:moonshot-v1-32k
python nano_claude.py --model qwen:qwen-max
```

**自动识别规则：**

| 模型前缀 | 识别出的提供方 |
|---|---|
| `claude-` | anthropic |
| `gpt-`, `o1`, `o3` | openai |
| `gemini-` | gemini |
| `moonshot-`, `kimi-` | kimi |
| `qwen`, `qwq-` | qwen |
| `glm-` | zhipu |
| `deepseek-` | deepseek |
| `llama`, `mistral`, `phi`, `gemma`, `mixtral`, `codellama` | ollama |

---

## CLI 参考

```text
python nano_claude.py [OPTIONS] [PROMPT]

选项：
  -p, --print          非交互模式：执行 prompt 后退出
  -m, --model MODEL    覆盖默认模型（例如 gpt-4o, ollama/llama3.3）
  --accept-all         自动批准所有操作（不弹权限确认）
  --verbose            显示 thinking 块和每轮 token 计数
  --thinking           启用 Extended Thinking（仅 Claude）
  --version            打印版本并退出
  -h, --help           显示帮助
```

**示例：**

```bash
# 使用默认模型启动交互式 REPL
python nano_claude.py

# 启动时切换模型
python nano_claude.py --model gpt-4o
python nano_claude.py -m ollama/deepseek-r1:32b

# 非交互 / 脚本模式
python nano_claude.py --print "Write a Python fibonacci function"
python nano_claude.py -p "Explain the Rust borrow checker in 3 sentences" -m gemini/gemini-2.0-flash

# CI / 自动化（无权限确认）
python nano_claude.py --accept-all --print "Initialize a Python project with pyproject.toml"

# 调试模式（查看 token + thinking）
python nano_claude.py --thinking --verbose
```

---

## Slash 命令（REPL）

输入 `/` 并按 **Tab** 可自动补全。

| 命令 | 描述 |
|---|---|
| `/help` | 显示所有命令 |
| `/clear` | 清空对话历史 |
| `/model` | 显示当前模型并列出所有可用模型 |
| `/model <name>` | 切换模型（立即生效） |
| `/config` | 显示当前所有配置值 |
| `/config key=value` | 设置配置值（持久化到磁盘） |
| `/save` | 保存会话（默认按时间戳命名） |
| `/save <filename>` | 保存会话到指定文件 |
| `/load` | 列出所有已保存会话 |
| `/load <filename>` | 加载一个已保存会话 |
| `/history` | 打印完整对话历史 |
| `/context` | 显示消息数量和 token 估算 |
| `/cost` | 显示 token 用量和预估美元成本 |
| `/verbose` | 切换 verbose 模式（token + thinking） |
| `/thinking` | 切换 Extended Thinking（仅 Claude） |
| `/permissions` | 显示当前权限模式 |
| `/permissions <mode>` | 设置权限模式：`auto` / `accept-all` / `manual` |
| `/cwd` | 显示当前工作目录 |
| `/cwd <path>` | 切换当前工作目录 |
| `/memory` | 列出所有持久记忆 |
| `/memory <query>` | 按关键词搜索记忆 |
| `/skills` | 列出可用技能 |
| `/agents` | 显示子智能体任务状态 |
| `/mcp` | 列出配置的 MCP 服务器及其工具 |
| `/mcp reload` | 重新连接所有 MCP 服务器并刷新工具 |
| `/mcp reload <name>` | 重新连接单个 MCP 服务器 |
| `/mcp add <name> <cmd> [args]` | 向用户配置中添加一个 stdio MCP 服务器 |
| `/mcp remove <name>` | 从用户配置中移除一个服务器 |
| `/exit` / `/quit` | 退出 |

**在会话中切换模型：**

```text
[myproject] ❯ /model
  Current model: claude-opus-4-6  (provider: anthropic)

  Available models by provider:
    anthropic     claude-opus-4-6, claude-sonnet-4-6, ...
    openai        gpt-4o, gpt-4o-mini, o3-mini, ...
    ollama        llama3.3, llama3.2, phi4, mistral, ...
    ...

[myproject] ❯ /model gpt-4o
  Model set to gpt-4o  (provider: openai)

[myproject] ❯ /model ollama/qwen2.5-coder
  Model set to ollama/qwen2.5-coder  (provider: ollama)
```

---

## 配置 API Key

### 方法 1：环境变量（推荐）

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=AIza...
export MOONSHOT_API_KEY=sk-...       # Kimi
export DASHSCOPE_API_KEY=sk-...      # Qwen
export ZHIPU_API_KEY=...             # Zhipu GLM
export DEEPSEEK_API_KEY=sk-...       # DeepSeek
```

### 方法 2：在 REPL 中设置（会持久化）

```text
/config anthropic_api_key=sk-ant-...
/config openai_api_key=sk-...
/config gemini_api_key=AIza...
/config kimi_api_key=sk-...
/config qwen_api_key=sk-...
/config zhipu_api_key=...
/config deepseek_api_key=sk-...
```

这些 key 会保存到 `~/.nano_claude/config.json`，下次启动时自动加载。

### 方法 3：直接编辑配置文件

```json
// ~/.nano_claude/config.json
{
  "model": "qwen/qwen-max",
  "max_tokens": 8192,
  "permission_mode": "auto",
  "verbose": false,
  "thinking": false,
  "qwen_api_key": "sk-...",
  "kimi_api_key": "sk-...",
  "deepseek_api_key": "sk-..."
}
```

---

## 权限系统

| 模式 | 行为 |
|---|---|
| `auto`（默认） | 只读操作始终允许；执行 Bash 命令和写文件前会提示确认。 |
| `accept-all` | 从不提示；所有操作自动执行。 |
| `manual` | 每个操作都提示确认，包括读取操作。 |

**提示示例：**

```text
  Allow: Run: git commit -am "fix bug"  [y/N/a(ccept-all)]
```

- `y` —— 只批准这一次操作
- `n` 或回车 —— 拒绝
- `a` —— 批准并将本次会话切换为 `accept-all`

**在 `auto` 模式下始终自动批准的命令：**
`ls`、`cat`、`head`、`tail`、`wc`、`pwd`、`echo`、`git status`、`git log`、`git diff`、`git show`、`find`、`grep`、`rg`、`python`、`node`、`pip show`、`npm list` 以及其他只读 shell 命令。

---

## 内置工具

### 核心工具

| 工具 | 描述 | 关键参数 |
|---|---|---|
| `Read` | 带行号读取文件 | `file_path`, `limit`, `offset` |
| `Write` | 创建或覆盖文件（显示 diff） | `file_path`, `content` |
| `Edit` | 精确字符串替换（显示 diff） | `file_path`, `old_string`, `new_string`, `replace_all` |
| `Bash` | 执行 shell 命令 | `command`, `timeout`（默认 30s） |
| `Glob` | 按 glob 模式查找文件 | `pattern`（例如 `**/*.py`）, `path` |
| `Grep` | 在文件中正则搜索（若可用则使用 ripgrep） | `pattern`, `path`, `glob`, `output_mode` |
| `WebFetch` | 获取 URL 并提取文本 | `url`, `prompt` |
| `WebSearch` | 通过 DuckDuckGo 搜索网页 | `query` |

### 记忆工具

| 工具 | 描述 | 关键参数 |
|---|---|---|
| `MemorySave` | 保存或更新持久记忆 | `name`, `type`, `description`, `content`, `scope` |
| `MemoryDelete` | 按名称删除记忆 | `name`, `scope` |
| `MemorySearch` | 按关键词搜索记忆（或使用 AI 排序） | `query`, `scope`, `use_ai`, `max_results` |
| `MemoryList` | 列出所有记忆及其年龄和元数据 | `scope` |

### 子智能体工具

| 工具 | 描述 | 关键参数 |
|---|---|---|
| `Agent` | 为任务启动一个子智能体 | `prompt`, `subagent_type`, `isolation`, `name`, `model`, `wait` |
| `SendMessage` | 向指定后台智能体发送消息 | `name`, `message` |
| `CheckAgentResult` | 检查后台智能体的状态 / 结果 | `task_id` |
| `ListAgentTasks` | 列出所有进行中和已完成的智能体任务 | — |
| `ListAgentTypes` | 列出可用的智能体类型定义 | — |

### 技能工具

| 工具 | 描述 | 关键参数 |
|---|---|---|
| `Skill` | 在对话中按名称调用一个技能 | `name`, `args` |
| `SkillList` | 列出所有可用技能及其触发器和元数据 | — |

### MCP 工具

MCP 工具会从已配置服务器中自动发现，并以 `mcp__<server>__<tool>` 形式注册。Claude 可以像使用内置工具一样使用它们。

| 示例工具名 | 来源 |
|---|---|
| `mcp__git__git_status` | `git` 服务器的 `git_status` 工具 |
| `mcp__filesystem__read_file` | `filesystem` 服务器的 `read_file` 工具 |
| `mcp__myserver__my_action` | 你配置的自定义服务器 |

> **添加自定义工具：** 参见 [Architecture Guide](docs/architecture.md#tool-registry) 了解如何注册自己的工具。

---

## 记忆

模型可以使用内置记忆系统跨会话记住信息。

**工作方式：** 记忆以 Markdown 文件形式存储，共有两个作用域：
- **用户作用域**（`~/.nano_claude/memory/`）—— 跨所有项目共享
- **项目作用域**（当前目录中的 `.nano_claude/memory/`）—— 仅针对当前仓库

每次保存或删除记忆时，系统都会自动重建一个 `MEMORY.md` 索引（≤ 200 行 / 25 KB），并将其注入系统提示词中，因此 Claude 始终拥有一个总览。

**记忆类型：**

| 类型 | 用途 |
|---|---|
| `user` | 你的角色、偏好、背景 |
| `feedback` | 你希望模型如何表现 |
| `project` | 正在进行的工作、截止日期、决策 |
| `reference` | 外部资源链接 |

**记忆文件格式**（`~/.nano_claude/memory/coding_style.md`）：
```markdown
---
name: coding style
description: Python formatting preferences
type: feedback
created: 2026-04-02
---
Prefer 4-space indentation and full type hints in all Python code.
**Why:** user explicitly stated this preference.
**How to apply:** apply to every Python file written or edited.
```

**示例交互：**

```text
You: Remember that I prefer 4-space indentation and type hints in all Python code.
AI: [calls MemorySave] Memory saved: coding_style [feedback/user]

You: /memory
  [feedback/user] coding_style (today): Python formatting preferences

You: /memory python
  [feedback/user] coding_style: Prefers 4-space indent and type hints in Python
```

**过期提醒：** 超过 1 天的记忆会在 `/memory` 输出中带有新鲜度提醒，方便你及时复查或更新。

**AI 排序搜索：** `MemorySearch(query="...", use_ai=true)` 会让模型基于相关性进行排序，而不是只做简单关键词匹配。

---

## 技能

技能是可复用的提示模板，可赋予模型专门能力。系统开箱自带两个内置技能——无需额外设置。

**内置技能：**

| 触发器 | 描述 |
|---|---|
| `/commit` | 审查已暂存修改并生成结构良好的 git commit |
| `/review [PR]` | 对代码或 PR diff 进行结构化审查 |

**快速开始 —— 自定义技能：**

```bash
mkdir -p ~/.nano_claude/skills
```

创建 `~/.nano_claude/skills/deploy.md`：

```markdown
---
name: deploy
description: Deploy to an environment
triggers: [/deploy]
allowed-tools: [Bash, Read]
when_to_use: Use when the user wants to deploy a version to an environment.
argument-hint: [env] [version]
arguments: [env, version]
context: inline
---

Deploy $VERSION to the $ENV environment.
Full args: $ARGUMENTS
```

然后这样使用：

```text
You: /deploy staging 2.1.0
AI: [deploys version 2.1.0 to staging]
```

**参数替换：**
- `$ARGUMENTS` —— 原始完整参数字符串
- `$ARG_NAME` —— 按命名参数进行位置替换（第一个词 → 第一个参数名）
- 缺失参数将变为空字符串

**执行模式：**
- `context: inline`（默认）—— 在当前会话历史中执行
- `context: fork` —— 以隔离的子智能体执行，使用全新历史；支持 `model` 覆盖

**优先级**（越高越优先）：项目级 > 用户级 > 内置

**列出技能：** `/skills` —— 显示触发器、参数提示、来源和 `when_to_use`

**技能搜索路径：**

```text
./.nano_claude/skills/     # 项目级（覆盖用户级）
~/.nano_claude/skills/     # 用户级
```

---

## 子智能体

模型可以启动独立子智能体并行处理任务。

**内置的专用智能体类型：**

| 类型 | 优化方向 |
|---|---|
| `general-purpose` | 研究、探索、多步任务 |
| `coder` | 编写、阅读和修改代码 |
| `reviewer` | 安全性、正确性和代码质量分析 |
| `researcher` | 网页搜索与文档查询 |
| `tester` | 编写并运行测试 |

**基本用法：**
```text
You: Search this codebase for all TODO comments and summarize them.
AI: [calls Agent(prompt="...", subagent_type="researcher")]
    Sub-agent reads files, greps for TODOs...
    Result: Found 12 TODOs across 5 files...
```

**后台模式** —— 启动后不等待，稍后再获取结果：
```text
AI: [calls Agent(prompt="run all tests", name="test-runner", wait=false)]
AI: [continues other work...]
AI: [calls CheckAgentResult / SendMessage to follow up]
```

**Git worktree 隔离** —— 智能体在隔离分支中工作，避免冲突：
```text
Agent(prompt="refactor auth module", isolation="worktree")
```
如果未产生改动，worktree 会自动清理；否则会报告分支名称。

**自定义智能体类型** —— 创建 `~/.nano_claude/agents/myagent.md`：
```markdown
---
name: myagent
description: Specialized for X
model: claude-haiku-4-5-20251001
tools: [Read, Grep, Bash]
---
Extra system prompt for this agent type.
```

**列出运行中的智能体：** `/agents`

子智能体拥有独立对话历史，共享文件系统，并限制为最多 3 层嵌套。

---

## MCP（模型上下文协议）

MCP 让你可以接入任意外部工具服务器——无论是本地子进程还是远程 HTTP——Claude 都能自动使用它们的工具。这也是 Claude Code 用来扩展能力的同一协议。

### 支持的传输方式

| 传输方式 | 配置中的 `type` | 说明 |
|---|---|---|
| **stdio** | `"stdio"` | 启动一个本地子进程（最常见） |
| **SSE** | `"sse"` | HTTP Server-Sent Events 流 |
| **HTTP** | `"http"` | 可流式的 HTTP POST（新型服务器） |

### 配置方式

可在项目目录中放置 `.mcp.json`，或编辑 `~/.nano_claude/mcp.json` 作为全局用户配置。

```json
{
  "mcpServers": {
    "git": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-git"]
    },
    "filesystem": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-filesystem", "/tmp"]
    },
    "my-remote": {
      "type": "sse",
      "url": "http://localhost:8080/sse",
      "headers": {"Authorization": "Bearer my-token"}
    }
  }
}
```

配置优先级：按服务器名称，`.mcp.json`（项目级）会覆盖 `~/.nano_claude/mcp.json`（用户级）。

### 快速开始

```bash
# 安装一个常用的 MCP 服务器
pip install uv        # uv 内含 uvx
uvx mcp-server-git --help   # 验证可正常运行

# 通过 REPL 添加到用户配置
/mcp add git uvx mcp-server-git

# 或在项目目录创建 .mcp.json，然后：
/mcp reload
```

### REPL 命令

```text
/mcp                          # 列出服务器 + 工具 + 连接状态
/mcp reload                   # 重新连接所有服务器并刷新工具列表
/mcp reload git               # 重新连接某个服务器
/mcp add myserver uvx mcp-server-x   # 添加 stdio 服务器
/mcp remove myserver          # 从用户配置中移除
```

### Claude 如何使用 MCP 工具

一旦连接成功，Claude 就可以直接调用 MCP 工具：

```text
You: What files changed in the last git commit?
AI: [calls mcp__git__git_diff_staged()]
    → shows diff output from the git MCP server
```

工具命名遵循 `mcp__<server_name>__<tool_name>` 模式。所有非字母数字或 `_` 的字符都会自动替换为 `_`。

### 常见 MCP 服务器

| 服务器 | 安装方式 | 提供功能 |
|---|---|---|
| `mcp-server-git` | `uvx mcp-server-git` | git 操作（status、diff、log、commit） |
| `mcp-server-filesystem` | `uvx mcp-server-filesystem <path>` | 文件读 / 写 / 列表 |
| `mcp-server-fetch` | `uvx mcp-server-fetch` | HTTP 抓取工具 |
| `mcp-server-postgres` | `uvx mcp-server-postgres <conn-str>` | PostgreSQL 查询 |
| `mcp-server-sqlite` | `uvx mcp-server-sqlite --db-path x.db` | SQLite 查询 |
| `mcp-server-brave-search` | `uvx mcp-server-brave-search` | Brave 网页搜索 |

> 完整服务器注册表可见 [modelcontextprotocol.io/servers](https://modelcontextprotocol.io/servers)

---

## 插件系统

`plugin/` 包允许你通过 git 仓库或本地目录，为 nano-claude-code 扩展额外工具、技能和 MCP 服务器。

### 安装插件

```bash
/plugin install my-plugin@https://github.com/user/my-plugin
/plugin install local-plugin@/path/to/local/plugin
```

### 管理插件

```bash
/plugin                   # 列出已安装插件
/plugin enable my-plugin  # 启用一个已禁用插件
/plugin disable my-plugin # 禁用但不卸载
/plugin disable-all       # 禁用所有插件
/plugin update my-plugin  # 从 git 拉取最新版本
/plugin uninstall my-plugin
/plugin info my-plugin    # 显示 manifest 详情
```

### 插件推荐引擎

```bash
/plugin recommend                    # 根据项目文件自动检测
/plugin recommend "docker database"  # 按关键词上下文推荐
```

推荐引擎会根据标签和关键词打分，将你的上下文与一个精心维护的插件市场进行匹配（如 git-tools、python-linter、docker-tools、sql-tools、test-runner、diagram-tools、aws-tools、web-scraper）。

### 插件清单（plugin.json）

```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "description": "Does something useful",
  "author": "you",
  "tags": ["git", "python"],
  "tools": ["tools"],
  "skills": ["skills/my.md"],
  "mcp_servers": {},
  "dependencies": ["httpx"]
}
```

也可使用 `PLUGIN.md` 中的 YAML frontmatter。

### 作用域

| 作用域 | 位置 | 配置 |
|-------|----------|--------|
| user（默认） | `~/.nano_claude/plugins/` | `~/.nano_claude/plugins.json` |
| project | `.nano_claude/plugins/` | `.nano_claude/plugins.json` |

使用 `--project` 标志：`/plugin install name@url --project`

---

## AskUserQuestion 工具

Claude 可以在任务中途暂停，并在继续之前交互式向你提出问题。

**Claude 的调用示例：**
```json
{
  "tool": "AskUserQuestion",
  "question": "Which database should I use?",
  "options": [
    {"label": "SQLite", "description": "Simple, file-based"},
    {"label": "PostgreSQL", "description": "Full-featured, requires server"}
  ],
  "allow_freetext": true
}
```

**你在终端中看到的是：**
```text
❓ Question from assistant:
   Which database should I use?

  [1] SQLite — Simple, file-based
  [2] PostgreSQL — Full-featured, requires server
  [0] Type a custom answer

Your choice (number or text):
```

- 可通过编号选择，也可直接输入自由文本
- Claude 收到你的回答后会继续任务
- 5 分钟超时（若未回答则返回 `"(no answer — timeout)"`）

---

## 任务管理

`task/` 包为 Claude（以及你自己）提供了一个结构化任务列表，用于在单个会话中追踪多步工作。

### 提供给 Claude 的工具

| 工具 | 参数 | 功能 |
|------|-----------|--------------|
| `TaskCreate` | `subject`, `description`, `active_form?`, `metadata?` | 创建任务；返回 `#id created: subject` |
| `TaskUpdate` | `task_id`, `subject?`, `description?`, `status?`, `owner?`, `add_blocks?`, `add_blocked_by?`, `metadata?` | 更新任意字段；`status='deleted'` 会删除任务 |
| `TaskGet` | `task_id` | 返回单个任务的完整详情 |
| `TaskList` | _(none)_ | 列出所有任务，带状态图标和待解决阻塞项 |

**有效状态：** `pending` → `in_progress` → `completed` / `cancelled` / `deleted`

### 依赖边

```text
TaskUpdate(task_id="3", add_blocked_by=["1","2"])
# 任务 3 现在被任务 1 和 2 阻塞。
# 反向边会自动设置：任务 1 和 2 的 "blocks" 列表中都会加入任务 3。
```

已完成的任务会被视为已解决，因此 `TaskList` 不会再把它们的阻塞作用显示在依赖任务上。

### 持久化

任务在每次变更后都会保存到当前工作目录下的 `.nano_claude/tasks.json`，并在首次访问时自动重新加载。

### REPL 命令

```text
/tasks                    列出所有任务
/tasks create <subject>   快速创建任务
/tasks start <id>         标记为 in_progress
/tasks done <id>          标记为 completed
/tasks cancel <id>        标记为 cancelled
/tasks delete <id>        删除任务
/tasks get <id>           显示完整详情
/tasks clear              删除所有任务
```

### Claude 的典型工作流

```text
User: implement the login feature

Claude:
  TaskCreate(subject="Design auth schema", description="JWT vs session")  → #1
  TaskCreate(subject="Write login endpoint", description="POST /auth/login") → #2
  TaskCreate(subject="Write tests", description="Unit + integration") → #3
  TaskUpdate(task_id="2", add_blocked_by=["1"])
  TaskUpdate(task_id="3", add_blocked_by=["2"])

  TaskUpdate(task_id="1", status="in_progress", active_form="Designing schema")
  ... (does the work) ...
  TaskUpdate(task_id="1", status="completed")
  TaskList()  → task 2 is now unblocked
  ...
```

---

## 上下文压缩

长对话会被自动压缩，以保持在模型上下文窗口之内。

**两层机制：**

1. **Snip** —— 若干轮之后，旧工具输出（文件读取、bash 结果）会被截断。速度快，无 API 成本。
2. **Auto-compact** —— 当 token 使用量超过上下文上限的 70% 时，模型会把较早消息总结成简明回顾。

这一过程是透明进行的，你无需手动操作。

---

## Diff 视图

当模型编辑或覆盖文件时，你会看到 git 风格的 diff：

```diff
  Changes applied to config.py:

--- a/config.py
+++ b/config.py
@@ -12,7 +12,7 @@
     "model": "claude-opus-4-6",
-    "max_tokens": 8192,
+    "max_tokens": 16384,
     "permission_mode": "auto",
```

绿色行表示新增，红色行表示删除。若是新建文件，则会显示摘要而非 diff。

---

## CLAUDE.md 支持

你可以在项目中放一个 `CLAUDE.md` 文件，为模型提供有关代码库的持久上下文。Nano Claude 会自动查找并注入到系统提示词中。

```text
~/.claude/CLAUDE.md          # 全局级 —— 应用于所有项目
/your/project/CLAUDE.md      # 项目级 —— 从 cwd 向上查找
```

**示例 `CLAUDE.md`：**

```markdown
# Project: FastAPI Backend

## Stack
- Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic
- Tests: pytest, coverage target 90%

## Conventions
- Format with black, lint with ruff
- Full type annotations required
- New endpoints must have corresponding tests

## Important Notes
- Never hard-code credentials — use environment variables
- Do not modify existing Alembic migration files
- The `staging` branch deploys automatically to staging on push
```

---

## 会话管理

```bash
# 在 REPL 中：
/save                          # 自动命名：session_20260401_143022.json
/save debug_auth_bug           # 指定名称保存

/load                          # 列出所有已保存会话
/load debug_auth_bug           # 恢复一个会话
/load session_20260401_143022.json
```

会话会以 JSON 格式保存在 `~/.nano_claude/sessions/` 中。

---

## 项目结构

```text
nano_claude_code/
├── nano_claude.py        # 入口：REPL + slash 命令 + diff 渲染
├── agent.py              # 智能体循环：流式处理、工具调度、压缩
├── providers.py          # 多提供方：Anthropic、OpenAI 兼容流式接口
├── tools.py              # 核心工具（Read/Write/Edit/Bash/Glob/Grep/Web）+ registry 接线
├── tool_registry.py      # 工具插件注册表：注册、查找、执行
├── compaction.py         # 上下文压缩：snip + 自动摘要
├── context.py            # 系统提示构建器：CLAUDE.md + git + memory
├── config.py             # 配置加载 / 保存 / 默认值
│
├── multi_agent/          # 多智能体包
│   ├── __init__.py       # 重新导出
│   ├── subagent.py       # AgentDefinition, SubAgentManager, worktree 辅助函数
│   └── tools.py          # Agent, SendMessage, CheckAgentResult, ListAgentTasks, ListAgentTypes
├── subagent.py           # 向后兼容 shim → multi_agent/
│
├── memory/               # 记忆包
│   ├── __init__.py       # 重新导出
│   ├── types.py          # MEMORY_TYPES 和格式说明
│   ├── store.py          # save/load/delete/search, MEMORY.md 索引重建
│   ├── scan.py           # MemoryHeader, age/freshness 辅助函数
│   ├── context.py        # get_memory_context(), truncation, AI search
│   └── tools.py          # MemorySave, MemoryDelete, MemorySearch, MemoryList
├── memory.py             # 向后兼容 shim → memory/
│
├── skill/                # 技能包
│   ├── __init__.py       # 重新导出；导入 builtin 以注册内置技能
│   ├── loader.py         # SkillDef, parse, load_skills, find_skill, substitute_arguments
│   ├── builtin.py        # 内置技能：/commit, /review
│   ├── executor.py       # execute_skill()：inline 或 fork 子智能体
│   └── tools.py          # Skill, SkillList
├── skills.py             # 向后兼容 shim → skill/
│
├── mcp/                  # MCP（模型上下文协议）包
│   ├── __init__.py       # 重新导出
│   ├── types.py          # MCPServerConfig, MCPTool, MCPServerState, JSON-RPC 辅助函数
│   ├── client.py         # StdioTransport, HttpTransport, MCPClient, MCPManager
│   ├── config.py         # 加载 .mcp.json（项目）+ ~/.nano_claude/mcp.json（用户）
│   └── tools.py          # 自动发现 + 将 MCP 工具注册到 tool_registry
│
└── tests/                # 135 个单元测试
    ├── test_mcp.py
    ├── test_memory.py
    ├── test_skills.py
    ├── test_subagent.py
    ├── test_tool_registry.py
    ├── test_compaction.py
    └── test_diff_view.py
```

> **给开发者：** 每个功能包（`multi_agent/`、`memory/`、`skill/`、`mcp/`）都是自包含的。你可以在任何由 `tools.py` 导入的模块中调用 `register_tool(ToolDef(...))` 来添加自定义工具。

---

## FAQ

**问：如何添加一个 MCP 服务器？**

方式 1 —— 通过 REPL（stdio 服务器）：
```text
/mcp add git uvx mcp-server-git
```

方式 2 —— 在项目中创建 `.mcp.json`：
```json
{
  "mcpServers": {
    "git": {"type": "stdio", "command": "uvx", "args": ["mcp-server-git"]}
  }
}
```

然后运行 `/mcp reload` 或重启。可使用 `/mcp` 查看连接状态。

**问：某个 MCP 服务器报错了，如何调试？**

```text
/mcp                    # 显示每个服务器的错误信息
/mcp reload git         # 尝试重新连接
```

如果服务器使用 stdio，请确认命令在你的 `$PATH` 中：
```bash
which uvx               # 应输出一个路径
uvx mcp-server-git      # 手动运行以查看错误
```

**问：可以使用需要认证的 MCP 服务器吗？**

对于带 Bearer token 的 HTTP/SSE 服务器：
```json
{
  "mcpServers": {
    "my-api": {
      "type": "sse",
      "url": "https://myserver.example.com/sse",
      "headers": {"Authorization": "Bearer sk-my-token"}
    }
  }
}
```

对于使用环境变量认证的 stdio 服务器：
```json
{
  "mcpServers": {
    "brave": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-brave-search"],
      "env": {"BRAVE_API_KEY": "your-key"}
    }
  }
}
```

**问：我的本地 Ollama 模型无法进行工具调用。**

并不是所有模型都支持函数调用。请使用推荐的工具调用模型之一：`qwen2.5-coder`、`llama3.3`、`mistral` 或 `phi4`。

```bash
ollama pull qwen2.5-coder
python nano_claude.py --model ollama/qwen2.5-coder
```

**问：如何连接运行 vLLM 的远程 GPU 服务器？**

```text
/config custom_base_url=http://your-server-ip:8000/v1
/config custom_api_key=your-token
/model custom/your-model-name
```

**问：如何查看 API 成本？**

```text
/cost

  Input tokens:  3,421
  Output tokens:   892
  Est. cost:     $0.0648 USD
```

**问：同一个会话里可以用多个 API Key 吗？**

可以。提前设置好所需的全部 key（通过环境变量或 `/config`），之后即可自由切换模型——每次调用都会使用当前活跃提供方对应的 key。

**问：如何让某个模型在所有项目中都可用？**

把 key 写入 `~/.bashrc` 或 `~/.zshrc`。默认模型可在 `~/.nano_claude/config.json` 中设置：

```json
{ "model": "claude-sonnet-4-6" }
```

**问：Qwen / Zhipu 输出乱码。**

请确认 `DASHSCOPE_API_KEY` / `ZHIPU_API_KEY` 正确，并确保账户有足够额度。这两个提供方都使用 UTF-8，并且对中文支持良好。

**问：可以通过管道把输入传给 nano claude 吗？**

```bash
echo "Explain this file" | python nano_claude.py --print --accept-all
cat error.log | python nano_claude.py -p "What is causing this error?"
```

**问：如何把它当作一个全局 CLI 工具使用？**

```bash
# 把别名加入 ~/.bashrc 或 ~/.zshrc
alias nc='python /path/to/nano_claude_code/nano_claude.py'

# 或作为脚本安装
pip install -e .   # 如果存在 setup.py
```
