# Claude Code 上下文压缩算法深度分析

> 基于 Claude Code 源码（2026-03-31 快照，512K 行 TypeScript）逆向分析
> 核心文件：`src/services/compact/` 目录下 11 个文件

---

## 目录

1. [架构总览](#1-架构总览)
2. [第1层：微压缩（Microcompact）](#2-第1层微压缩microcompact)
3. [第2层：自动压缩（Auto-Compact）](#3-第2层自动压缩auto-compact)
4. [第3层：传统压缩（Full Compact）](#4-第3层传统压缩full-compact)
5. [第4层：Session Memory 压缩](#5-第4层session-memory-压缩)
6. [消息分组算法](#6-消息分组算法)
7. [Token 估算算法](#7-token-估算算法)
8. [压缩提示词工程](#8-压缩提示词工程)
9. [5层错误恢复中的压缩角色](#9-5层错误恢复中的压缩角色)
10. [各层对比与设计哲学](#10-各层对比与设计哲学)

---

## 1. 架构总览

Claude Code 的上下文压缩不是单一算法，而是一个 **4层递进的压缩体系**，每层解决不同层面的问题：

```
用户消息 → [第1层：微压缩] → [第2层：自动压缩] → API 调用
              ↓                    ↓
         细粒度清理旧工具输出    上下文即将超限时触发
         (不丢语义，<1ms)       (调用 LLM 或 Session Memory)
                                   ↓
                    ┌──────────────┴──────────────┐
              [第4层：SM压缩]              [第3层：传统压缩]
              (用已有摘要，<10ms)          (Fork Agent 生成摘要，5-30s)
```

**核心原则：** 尽可能用廉价的规则操作延迟昂贵的 LLM 调用，只在不得已时丢弃信息。

### 涉及的源文件

| 文件 | 行数 | 职责 |
|------|------|------|
| `microCompact.ts` | ~400 | 微压缩：规则清理旧工具结果 |
| `apiMicrocompact.ts` | — | API 层缓存编辑集成 |
| `timeBasedMCConfig.ts` | — | 时间触发微压缩配置 |
| `autoCompact.ts` | ~350 | 自动压缩：阈值判断 + 断路器 |
| `compact.ts` | ~600+ | 传统压缩：Fork Agent 摘要 |
| `prompt.ts` | ~375 | 压缩提示词模板 |
| `sessionMemoryCompact.ts` | ~630 | Session Memory 压缩路径 |
| `grouping.ts` | ~63 | 消息按 API 轮次分组 |
| `postCompactCleanup.ts` | — | 压缩后清理 |
| `compactWarningHook.ts` | — | 压缩警告钩子 |
| `compactWarningState.ts` | — | 压缩警告状态 |

---

## 2. 第1层：微压缩（Microcompact）

**源文件：** `microCompact.ts`

### 核心思想

不调用 LLM，纯规则操作——清理旧的、大块的工具输出结果，保留语义信息。这是每轮查询前都会执行的最轻量操作。

### 可压缩工具白名单

```typescript
const COMPACTABLE_TOOLS = new Set([
  'Read',      // 文件读取结果可能很大
  'Bash',      // Shell 输出可能很长
  'Grep',      // 搜索结果
  'Glob',      // 文件列表
  'WebSearch', // 网页搜索结果
  'WebFetch',  // 网页抓取结果
  'Edit',      // 文件编辑的 diff
  'Write',     // 文件写入确认
])
```

不在白名单中的工具（如 Agent、Skill、MCP 等）的结果不会被微压缩。

### 两个子路径

#### 子路径 A：时间触发微压缩

```
触发条件：距上次助手消息的时间间隔超过阈值（API 缓存已过期）

执行逻辑：
1. 收集所有可压缩工具的 tool_use ID
2. 保留最近 N 个工具结果
3. 将更早的 tool_result 内容替换为：
   "[Old tool result content cleared]"
4. 不修改 tool_use 块（保持 API 配对完整性）

特点：
- 缓存已过期，所以无需保护缓存
- 直接修改本地消息内容
- 减少重传时的 token 消耗
```

#### 子路径 B：缓存编辑微压缩（Cached MC）

这是更精巧的路径——在缓存仍然有效时工作：

```
触发条件：
- 特性开关 CACHED_MICROCOMPACT 开启
- 模型支持缓存编辑 API
- 当前是主线程查询（非 fork agent）

执行逻辑：
1. collectCompactableToolIds(): 收集所有可压缩的 tool_use ID
2. registerToolResult(): 注册每个工具结果（按用户消息分组）
3. registerToolMessage(): 记录工具消息组
4. getToolResultsToDelete(): 根据 count/keep 阈值决定删除哪些
5. createCacheEditsBlock(): 生成 cache_edits API 块

关键区别：
- 不修改本地消息内容！
- 通过 API 的 cache_edits 字段告诉服务端删除特定工具结果的缓存
- 保持 prompt cache 命中率
- 状态通过 pendingCacheEdits / pinnedCacheEdits 管理
```

**缓存编辑的状态管理：**

```typescript
// 全局状态
let cachedMCState: CachedMCState | null = null
let pendingCacheEdits: CacheEditsBlock | null = null

// consumePendingCacheEdits():
//   返回待插入的缓存编辑块，然后清空 pending 状态
//   调用者在 API 请求后必须调用 pinCacheEdits() 固定它们

// getPinnedCacheEdits():
//   返回之前已固定的缓存编辑，需要在后续请求中重新发送

// markToolsSentToAPIState():
//   标记工具已发送给 API（成功响应后调用）
```

### Token 估算辅助

```typescript
function calculateToolResultTokens(block: ToolResultBlockParam): number {
  if (typeof block.content === 'string') {
    return roughTokenCountEstimation(block.content)  // 字符数 / 4
  }
  // 数组：逐项计算
  return block.content.reduce((sum, item) => {
    if (item.type === 'text') return sum + roughTokenCountEstimation(item.text)
    if (item.type === 'image' || item.type === 'document') return sum + 2000
    return sum
  }, 0)
}

function estimateMessageTokens(messages: Message[]): number {
  let totalTokens = 0
  for (const message of messages) {
    for (const block of message.message.content) {
      switch (block.type) {
        case 'text': totalTokens += roughTokenCountEstimation(block.text); break
        case 'tool_result': totalTokens += calculateToolResultTokens(block); break
        case 'image':
        case 'document': totalTokens += 2000; break  // 固定估算
        case 'thinking': totalTokens += roughTokenCountEstimation(block.thinking); break
        case 'redacted_thinking': totalTokens += roughTokenCountEstimation(block.data); break
        case 'tool_use': totalTokens += roughTokenCountEstimation(block.name + JSON.stringify(block.input ?? {})); break
        default: totalTokens += roughTokenCountEstimation(JSON.stringify(block)); break
      }
    }
  }
  return Math.ceil(totalTokens * (4 / 3))  // × 4/3 保守填充
}
```

---

## 3. 第2层：自动压缩（Auto-Compact）

**源文件：** `autoCompact.ts`

### 阈值计算

```typescript
// 有效上下文窗口 = 模型上下文窗口 - 摘要输出预留
const MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000  // p99.99 的摘要输出是 17,387 tokens

function getEffectiveContextWindowSize(model: string): number {
  const reservedTokensForSummary = Math.min(
    getMaxOutputTokensForModel(model),
    MAX_OUTPUT_TOKENS_FOR_SUMMARY,
  )
  let contextWindow = getContextWindowForModel(model)
  // 支持环境变量覆盖（用于测试）
  if (process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW) {
    contextWindow = Math.min(contextWindow, parsed)
  }
  return contextWindow - reservedTokensForSummary
}

// 自动压缩阈值 = 有效上下文窗口 - 13K 缓冲
const AUTOCOMPACT_BUFFER_TOKENS = 13_000

function getAutoCompactThreshold(model: string): number {
  return getEffectiveContextWindowSize(model) - AUTOCOMPACT_BUFFER_TOKENS
}

// 举例（Opus 200K 上下文）：
// 有效窗口 = 200,000 - 20,000 = 180,000
// 自动压缩阈值 = 180,000 - 13,000 = 167,000 tokens
```

### 其他阈值

```typescript
const WARNING_THRESHOLD_BUFFER_TOKENS = 20_000   // 警告阈值
const ERROR_THRESHOLD_BUFFER_TOKENS = 20_000     // 错误阈值
const MANUAL_COMPACT_BUFFER_TOKENS = 3_000       // 手动 /compact 的阻塞限制
```

### 断路器机制

```typescript
const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3

// BQ 数据分析发现：1,279 个会话连续失败 50+ 次（最多 3,272 次），
// 每天浪费约 250K 次 API 调用。所以加了断路器。

if (tracking.consecutiveFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
  return { wasCompacted: false }  // 直接跳过，不再尝试
}
```

### shouldAutoCompact 决策树

```
shouldAutoCompact(messages, model, querySource):

1. querySource 是 'session_memory' 或 'compact'？
   → 返回 false（防止递归死锁——压缩代理自己不能触发压缩）

2. querySource 是 'marble_origami'（上下文折叠代理）？
   → 返回 false（防止破坏主线程的已提交日志）

3. isAutoCompactEnabled() 返回 false？
   → 返回 false
   （检查 DISABLE_COMPACT、DISABLE_AUTO_COMPACT 环境变量和用户配置）

4. 响应式压缩模式开启？（tengu_cobalt_raccoon gate）
   → 返回 false（让 API 的 prompt-too-long 错误触发响应式压缩）

5. 上下文折叠模式开启？
   → 返回 false（上下文折叠是 90%/95% 流程，自动压缩在 93% 会干扰它）

6. tokenCountWithEstimation(messages) - snipTokensFreed >= threshold？
   → 返回 true
```

### autoCompactIfNeeded 执行流程

```
autoCompactIfNeeded(messages, context, ...):

1. DISABLE_COMPACT 环境变量？→ 跳过

2. 断路器检查：consecutiveFailures >= 3？→ 跳过

3. shouldAutoCompact() 返回 true？
   ↓ 是
4. 优先尝试 Session Memory 压缩
   ↓ 成功 → 返回结果
   ↓ 失败

5. 回退到传统压缩（compactConversation）
   ↓ 成功 → 重置 consecutiveFailures = 0，返回结果
   ↓ 失败

6. consecutiveFailures++
   ↓ 达到 3 次
7. 日志：断路器触发，本次会话不再尝试自动压缩
```

---

## 4. 第3层：传统压缩（Full Compact）

**源文件：** `compact.ts` + `prompt.ts`

### 核心机制：Fork Agent

传统压缩使用一个 **Fork Agent**——创建当前会话的一个分支，让它生成摘要。关键优势是**共享主会话的 prompt cache**。

```
主会话消息: [user1, assistant1, user2, assistant2, ...]
                ↓ 全部传入
Fork Agent（共享 prompt cache）
                ↓ 单轮回复
生成结构化摘要（<analysis> + <summary>）
                ↓
后处理 → 替换原消息
```

### 预处理管线

```
原始消息
  ↓
stripImagesFromMessages()    ← 图片 → "[image]"，文档 → "[document]"
  ↓                            （防止压缩请求自身超过上下文限制）
stripReinjectedAttachments() ← 删除技能发现/列表附件
  ↓                            （压缩后会自动重新注入）
normalizeMessagesForAPI()    ← 规范化消息格式
  ↓
发送给 Fork Agent
```

### 摘要输出格式

Fork Agent 被要求生成两个 XML 块：

```xml
<analysis>
[思考草稿——用于提高摘要质量的中间推理过程]
[这部分最终会被删除，不会进入压缩后的上下文]
</analysis>

<summary>
1. Primary Request and Intent:
   [详细描述用户的所有请求和意图]

2. Key Technical Concepts:
   - [概念1]
   - [概念2]

3. Files and Code Sections:
   - [文件名1]
     - [为什么这个文件重要]
     - [代码片段]
   - [文件名2]
     - [代码片段]

4. Errors and fixes:
   - [错误描述]:
     - [修复方式]
     - [用户反馈]

5. Problem Solving:
   [问题解决过程]

6. All user messages:
   - [逐条列出所有非工具结果的用户消息]

7. Pending Tasks:
   - [待办事项1]
   - [待办事项2]

8. Current Work:
   [精确描述当前工作内容，包含文件名和代码片段]

9. Optional Next Step:
   [下一步计划，包含最近对话的直接引用]
</summary>
```

### 防止工具调用的强力前导词

```typescript
const NO_TOOLS_PREAMBLE = `CRITICAL: Respond with TEXT ONLY. Do NOT call any tools.

- Do NOT use Read, Bash, Grep, Glob, Edit, Write, or ANY other tool.
- You already have all the context you need in the conversation above.
- Tool calls will be REJECTED and will waste your only turn — you will fail the task.
- Your entire response must be plain text: an <analysis> block followed by a <summary> block.
`
```

为什么需要这么强力？注释解释了：

```
// Sonnet 4.6+ 自适应思考模型有时会忽略较弱的尾部指令并尝试调用工具。
// 在 maxTurns: 1 的情况下，被拒绝的工具调用意味着没有文本输出
// → 回退到流式备用路径（4.6 上 2.79% vs 4.5 上 0.01%）。
// 把这个放在最前面并明确说明拒绝后果，可以防止浪费轮次。
```

### 后处理（formatCompactSummary）

```typescript
function formatCompactSummary(summary: string): string {
  // 1. 删除 <analysis> 块（草稿，已无价值）
  summary = summary.replace(/<analysis>[\s\S]*?<\/analysis>/, '')

  // 2. 提取 <summary> 内容，替换为可读标题
  const match = summary.match(/<summary>([\s\S]*?)<\/summary>/)
  if (match) {
    summary = summary.replace(/<summary>[\s\S]*?<\/summary>/,
      `Summary:\n${match[1].trim()}`)
  }

  // 3. 清理多余空行
  summary = summary.replace(/\n\n+/g, '\n\n')
  return summary.trim()
}
```

### 压缩后消息序列

```
[CompactBoundaryMessage]     ← 标记压缩边界（含 token 统计、trigger 类型）
[SummaryUserMessage]         ← 格式化后的摘要
[messagesToKeep]             ← 保留的最近消息（如果有）
[Attachments]                ← 重新注入的附件
  - 最近读取的文件（前 5 个，每个 ≤ 5K tokens，总预算 50K）
  - Plan 文件（如果有活跃计划）
  - MCP 指令增量
  - 技能发现增量
  - 代理列表增量
[HookResults]                ← PreCompact/PostCompact 钩子结果
```

### Prompt-Too-Long 重试机制

当压缩请求本身超过上下文限制时：

```typescript
const MAX_PTL_RETRIES = 3

function truncateHeadForPTLRetry(messages, ptlResponse): Message[] | null {
  // 1. 移除上一次重试的标记消息（防止重试停滞）
  // 2. 按 API 轮次分组
  const groups = groupMessagesByApiRound(messages)
  if (groups.length < 2) return null  // 无法再裁剪

  // 3. 决定删除多少组
  const tokenGap = getPromptTooLongTokenGap(ptlResponse)
  if (tokenGap !== undefined) {
    // 能解析出 token 缺口 → 精确删除
    let acc = 0, dropCount = 0
    for (const g of groups) {
      acc += roughTokenCountEstimationForMessages(g)
      dropCount++
      if (acc >= tokenGap) break
    }
  } else {
    // 不能解析 → 删除 20% 最旧的组
    dropCount = Math.max(1, Math.floor(groups.length * 0.2))
  }

  // 4. 保证至少保留 1 组
  dropCount = Math.min(dropCount, groups.length - 1)

  // 5. 如果裁剪后第一条是 assistant 消息，补一个 user marker
  //    （API 要求第一条消息必须是 user）
  const sliced = groups.slice(dropCount).flat()
  if (sliced[0]?.type === 'assistant') {
    return [createUserMessage({ content: PTL_RETRY_MARKER, isMeta: true }), ...sliced]
  }
  return sliced
}
```

### 部分压缩（Partial Compact）

支持两个方向：

| 方向 | 提示词 | 用途 |
|------|--------|------|
| `from`（默认） | `PARTIAL_COMPACT_PROMPT` | 保留旧消息，仅摘要"最近的消息" |
| `up_to` | `PARTIAL_COMPACT_UP_TO_PROMPT` | 摘要旧消息，保留新消息。摘要会放在开头，后续消息跟在后面 |

`up_to` 模式的摘要包含一个特殊的第 9 章节 "Context for Continuing Work"，专门为后续消息提供上下文。

---

## 5. 第4层：Session Memory 压缩

**源文件：** `sessionMemoryCompact.ts`

### 核心思想

不调用 LLM 生成新摘要，而是直接使用已经通过后台记忆提取（`extractMemories`）积累的 Session Memory 作为"摘要"。

### 优势

- **速度快**：不需要 API 调用，<10ms
- **质量可预测**：Session Memory 是在每轮查询后渐进更新的，不是一次性压缩
- **保留近期消息**：不像传统压缩那样替换所有消息

### 配置参数

```typescript
const DEFAULT_SM_COMPACT_CONFIG = {
  minTokens: 10_000,           // 至少保留 10K tokens 的最近消息
  minTextBlockMessages: 5,      // 至少保留 5 条含文本的消息
  maxTokens: 40_000,           // 最多保留 40K tokens（硬上限）
}
// 这些值通过 GrowthBook 远程配置，可动态调整
```

### calculateMessagesToKeepIndex 算法

这是 Session Memory 压缩的核心算法——决定保留哪些最近的消息：

```
输入：messages[], lastSummarizedIndex（Session Memory 已覆盖到哪条消息）

算法：
1. startIndex = lastSummarizedIndex + 1
   （即：从 Session Memory 尚未覆盖的消息开始）

2. 计算当前 [startIndex, end] 范围的 token 总量和含文本消息数

3. 如果已经超过 maxTokens (40K) → 直接返回（不再扩展）

4. 如果同时满足 ≥ minTokens (10K) AND ≥ minTextBlockMessages (5)
   → 直接返回（已足够）

5. 否则，从 startIndex 往前逐条扩展：
   - 每加入一条消息，更新 token 和消息计数
   - 停止条件：
     a. 达到 maxTokens (40K)
     b. 同时满足 minTokens 和 minTextBlockMessages
     c. 到达上一个 CompactBoundary（不跨越旧的压缩边界）

6. adjustIndexToPreserveAPIInvariants(messages, startIndex)
   → 确保不切断 tool_use/tool_result 配对
   → 确保不分离共享 message.id 的 thinking 块
```

### adjustIndexToPreserveAPIInvariants 算法

这个算法解决一个棘手的问题——流式传输时，一个 API 响应会产生多条消息（thinking、tool_use 等），它们共享同一个 `message.id`。如果在中间切断，`normalizeMessagesForAPI` 合并时会丢失 thinking 块。

```
输入：messages[], startIndex

步骤 1：修复 tool_use/tool_result 配对
  1a. 收集 [startIndex, end] 范围内所有 tool_result 的 tool_use_id
  1b. 收集范围内已有的 tool_use_id
  1c. 找出缺失的 tool_use_id（在范围外）
  1d. 向前搜索，把包含缺失 tool_use 的 assistant 消息纳入范围

步骤 2：修复 thinking 块分离
  2a. 收集范围内所有 assistant 消息的 message.id
  2b. 向前搜索，把共享同一 message.id 的 assistant 消息纳入范围

返回：调整后的 startIndex
```

**源码注释中的真实 bug 场景：**

```
Session 存储（压缩前）：
  Index N:   assistant, message.id: X, content: [thinking]
  Index N+1: assistant, message.id: X, content: [tool_use: ORPHAN_ID]
  Index N+2: assistant, message.id: X, content: [tool_use: VALID_ID]
  Index N+3: user, content: [tool_result: ORPHAN_ID, tool_result: VALID_ID]

如果 startIndex = N+2：
  旧代码：只检查 N+2 的 tool_results，找不到，返回 N+2
  normalizeMessagesForAPI 合并后：
    msg[1]: assistant with [tool_use: VALID_ID]  ← ORPHAN tool_use 被排除！
    msg[2]: user with [tool_result: ORPHAN_ID, tool_result: VALID_ID]
  API 报错：孤立的 tool_result 引用了不存在的 tool_use
```

### trySessionMemoryCompaction 完整流程

```
trySessionMemoryCompaction(messages, agentId, autoCompactThreshold):

1. shouldUseSessionMemoryCompaction()？
   → 检查 tengu_session_memory AND tengu_sm_compact 特性开关
   → 支持 ENABLE_CLAUDE_CODE_SM_COMPACT / DISABLE_CLAUDE_CODE_SM_COMPACT 环境变量

2. 初始化远程配置（仅首次）

3. 等待正在进行的 Session Memory 提取完成（带超时）

4. 获取 lastSummarizedMessageId 和 sessionMemory 内容

5. Session Memory 文件不存在？→ 返回 null
6. Session Memory 是空模板？→ 返回 null

7. 确定 lastSummarizedIndex：
   a. 正常情况：在 messages 中查找 lastSummarizedMessageId 的索引
   b. 恢复的会话：设为 messages.length - 1（从末尾开始）

8. calculateMessagesToKeepIndex() → startIndex
9. 过滤掉 messagesToKeep 中的旧 CompactBoundary

10. 执行 SessionStart 钩子（恢复 CLAUDE.md 等上下文）

11. 创建压缩结果：
    - 截断过大的 Session Memory 章节
    - 生成摘要用户消息
    - 附加 Plan 文件（如果有）

12. 检查压缩后 token 是否仍超过阈值
    → 是：返回 null（回退到传统压缩）
    → 否：返回 CompactionResult
```

---

## 6. 消息分组算法

**源文件：** `grouping.ts`

```typescript
function groupMessagesByApiRound(messages: Message[]): Message[][] {
  const groups: Message[][] = []
  let current: Message[] = []
  let lastAssistantId: string | undefined

  for (const msg of messages) {
    // 当出现新的 assistant message.id 时，开始新的一组
    if (
      msg.type === 'assistant' &&
      msg.message.id !== lastAssistantId &&
      current.length > 0
    ) {
      groups.push(current)
      current = [msg]
    } else {
      current.push(msg)
    }
    if (msg.type === 'assistant') {
      lastAssistantId = msg.message.id
    }
  }

  if (current.length > 0) {
    groups.push(current)
  }
  return groups
}
```

**设计细节：**

- 同一 API 请求的流式块共享同一个 `message.id`
- `StreamingToolExecutor` 在流式输出期间交错插入 `tool_result`，但它们属于同一轮次
- 只要 `message.id` 不变，所有消息都在同一组内
- 不跟踪未解决的 `tool_use` ID——让分组边界自然形成，由 `ensureToolResultPairing` 在 API 层修复残留的配对问题

---

## 7. Token 估算算法

贯穿所有压缩路径的核心辅助：

### 粗略估算

```typescript
function roughTokenCountEstimation(text: string): number {
  return text.length / 4  // 经验法则：4 字符 ≈ 1 token
}
```

### 消息级估算

```typescript
function estimateMessageTokens(messages: Message[]): number {
  let totalTokens = 0
  for (const message of messages) {
    if (message.type !== 'user' && message.type !== 'assistant') continue
    for (const block of message.message.content) {
      switch (block.type) {
        case 'text':
          totalTokens += roughTokenCountEstimation(block.text)
          break
        case 'tool_result':
          totalTokens += calculateToolResultTokens(block)
          break
        case 'image':
        case 'document':
          totalTokens += 2000  // 固定值，不论实际大小
          break
        case 'thinking':
          totalTokens += roughTokenCountEstimation(block.thinking)
          // 注意：不计算签名（signature 是元数据，不被模型 tokenize）
          break
        case 'redacted_thinking':
          totalTokens += roughTokenCountEstimation(block.data)
          break
        case 'tool_use':
          totalTokens += roughTokenCountEstimation(
            block.name + JSON.stringify(block.input ?? {})
          )
          // 不计算 JSON wrapper 和 id 字段
          break
        default:
          totalTokens += roughTokenCountEstimation(JSON.stringify(block))
          break
      }
    }
  }
  return Math.ceil(totalTokens * (4 / 3))  // 保守填充 33%
}
```

### 精确计算

```typescript
// 当有 API 响应的 usage 数据时，使用精确值
function tokenCountFromLastAPIResponse(messages: Message[]): number | undefined {
  // 从最后一条 assistant 消息的 usage 字段读取
  // usage.input_tokens 包含了 API 看到的实际 token 数
}

// 混合策略
function tokenCountWithEstimation(messages: Message[]): number {
  // 优先使用 API 返回的精确值
  // 不可用时回退到估算
}
```

---

## 8. 压缩提示词工程

**源文件：** `prompt.ts`

### 三种提示词模板

| 模板 | 变量名 | 用途 |
|------|--------|------|
| 完整压缩 | `BASE_COMPACT_PROMPT` | 摘要整个对话 |
| 部分压缩（from） | `PARTIAL_COMPACT_PROMPT` | 只摘要最近的消息 |
| 部分压缩（up_to） | `PARTIAL_COMPACT_UP_TO_PROMPT` | 摘要旧消息，作为后续消息的前导 |

### 提示词结构

```
[NO_TOOLS_PREAMBLE]        ← 强力禁止工具调用
[DETAILED_ANALYSIS_INSTRUCTION]  ← 要求 <analysis> 思考草稿
[MAIN_PROMPT]              ← 9 章节结构化摘要要求 + 示例
[Custom Instructions]      ← 用户自定义指令（如果有）
[NO_TOOLS_TRAILER]         ← 再次强调不要调用工具
```

### <analysis> 块的作用

```
提示词要求模型先在 <analysis> 中"打草稿"：
1. 按时间顺序分析每条消息
2. 识别用户意图、技术决策、代码模式
3. 特别关注用户反馈（"用户让你做不同的事情"）
4. 双重检查技术准确性和完整性

这类似于 Chain-of-Thought，但最终会被 formatCompactSummary() 删除，
只保留 <summary> 部分进入压缩后的上下文。
```

### 压缩后的摘要消息

```typescript
function getCompactUserSummaryMessage(summary, suppressFollowUp, transcriptPath, recentPreserved): string {
  let msg = `This session is being continued from a previous conversation that ran out of context.
The summary below covers the earlier portion of the conversation.

${formatCompactSummary(summary)}`

  // 如果有 transcript 路径，提供回溯指引
  if (transcriptPath) {
    msg += `\n\nIf you need specific details from before compaction
(like exact code snippets, error messages, or content you generated),
read the full transcript at: ${transcriptPath}`
  }

  // 如果保留了最近消息
  if (recentMessagesPreserved) {
    msg += `\n\nRecent messages are preserved verbatim.`
  }

  // 如果是自动压缩（suppressFollowUp = true）
  if (suppressFollowUpQuestions) {
    msg += `\nContinue the conversation from where it left off
without asking the user any further questions.
Resume directly — do not acknowledge the summary,
do not recap what was happening,
do not preface with "I'll continue" or similar.
Pick up the last task as if the break never happened.`
  }

  // 如果是 Proactive/KAIROS 模式
  if (proactiveModule?.isProactiveActive()) {
    msg += `\n\nYou are running in autonomous/proactive mode.
This is NOT a first wake-up — you were already working autonomously before compaction.
Continue your work loop: pick up where you left off based on the summary above.
Do not greet the user or ask what to work on.`
  }

  return msg
}
```

---

## 9. 5层错误恢复中的压缩角色

在 `query.ts` 的 5 层错误恢复机制中，压缩系统承担了前 2 层：

```
API 调用失败
  ↓
第1层：上下文折叠排水（Context Collapse Drain）
  ↓ 失败
第2层：响应式压缩（Reactive Compact）  ← 使用 compact.ts
  ↓ 失败
第3层：最大输出升级（8K → 64K tokens）
  ↓ 失败
第4层：多轮恢复（注入"请继续"消息，最多 3 次）
  ↓ 失败
第5层：模型回退（切换到备用模型，剥离 thinking 签名块）
  ↓ 失败
暴露错误给用户
```

**响应式压缩** vs **主动压缩**：

| 属性 | 主动压缩（Auto-Compact） | 响应式压缩（Reactive Compact） |
|------|--------------------------|-------------------------------|
| 触发 | token 数超过阈值 | API 返回 prompt-too-long 错误 |
| 时机 | API 调用前 | API 调用失败后 |
| 路径 | `autoCompact.ts` → `compact.ts` | `query.ts` 错误恢复层 |
| 回退 | SM → 传统压缩 → 放弃 | 传统压缩 → 裁剪最旧消息 |

---

## 10. 各层对比与设计哲学

### 横向对比

| 属性 | 微压缩 | Session Memory | 传统压缩 | PTL Recovery |
|------|--------|---------------|----------|-------------|
| **调用 LLM** | 否 | 否 | 是（Fork Agent） | 否 |
| **信息损失** | 最小（仅删工具输出） | 中等（靠已有摘要） | 中等（9章摘要） | 高（丢弃最旧消息） |
| **延迟** | <1ms | <10ms | 5-30s | ~0 |
| **触发** | 每轮自动 | 自动压缩优先路径 | 自动/手动 | 压缩自身超限 |
| **prompt cache** | 保留（缓存编辑） | 破坏 | 共享（Fork） | 破坏 |
| **最大输出** | — | — | 20K tokens | — |
| **断路器** | 无 | 无 | 有（3次） | 有（3次） |
| **token 预算** | — | 40K 最大保留 | 50K 文件重注入 | 按组裁剪 |

### 设计哲学总结

1. **渐进式降级**：从无损操作（微压缩）到有损操作（传统压缩）到丢弃操作（PTL Recovery），每一层都比上一层代价更高

2. **缓存优先**：微压缩的缓存编辑路径专门设计为不破坏 prompt cache，传统压缩通过 Fork Agent 共享 cache

3. **安全性保证**：
   - 永远不切断 tool_use/tool_result 配对
   - 永远不分离共享 message.id 的消息块
   - 断路器防止失败时无限重试
   - 递归保护防止压缩代理触发自身压缩

4. **可观测性**：每个压缩操作都记录 `logEvent`（如 `tengu_compact`, `tengu_cached_microcompact`），包含压缩前后的 token 数、触发原因、重试次数等

5. **可配置性**：几乎所有阈值都支持环境变量覆盖（用于测试）或 GrowthBook 远程配置（用于动态调整）

---

*来自：AI超元域 | B站频道：https://space.bilibili.com/3493277319825652*

*基于 Claude Code 源码逆向分析，2026-03-31*
