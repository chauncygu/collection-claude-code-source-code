# Claude Code Memory 记忆系统深度分析

> 基于 Claude Code 源码（2026-03-31 快照，512K 行 TypeScript）逆向分析
> 核心文件：`src/memdir/`（8个文件）、`src/services/extractMemories/`（2个）、`src/services/SessionMemory/`（3个）、`src/services/teamMemorySync/`（5个）

---

## 1. 三层记忆架构总览

Claude Code 的记忆系统不是一个简单的文件存储，而是一个**三层递进的知识管理体系**：

```
┌─────────────────────────────────────────────────────────────┐
│  第3层：团队记忆（Team Memory）                               │
│  跨用户、按仓库   │ 服务端同步 │ REST API + 乐观锁           │
│  秘密扫描保护     │ 文件监听器 │ 30种凭证检测规则             │
├─────────────────────────────────────────────────────────────┤
│  第2层：持久记忆（Persistent Memory / extractMemories）       │
│  跨会话、按项目   │ 本地文件   │ 后台 Fork Agent 自动提取     │
│  4种类型分类      │ MEMORY.md 索引 │ AI 相关性召回            │
├─────────────────────────────────────────────────────────────┤
│  第1层：会话记忆（Session Memory）                             │
│  仅当前会话      │ 单个文件   │ 10个固定章节 │ 服务于压缩     │
└─────────────────────────────────────────────────────────────┘
```

| 层级 | 范围 | 持久性 | 触发方式 | 存储位置 |
|------|------|--------|----------|----------|
| 会话记忆 | 当前会话 | 临时（会话结束即停用） | 后采样钩子（token+工具调用阈值） | 会话目录下单文件 |
| 持久记忆 | 跨会话、按项目 | 永久（直到手动删除） | 每轮查询结束时（Stop Hook） | `~/.claude/projects/<项目>/memory/` |
| 团队记忆 | 跨用户、按仓库 | 远程服务器 + 本地镜像 | 文件监听器（2秒去抖） | `memory/team/` + Anthropic API |

---

## 2. 持久记忆系统（核心）

### 2.1 记忆文件格式

每条记忆是一个独立的 Markdown 文件，带 YAML frontmatter：

```markdown
---
name: 用户偏好-简洁回复
description: 用户不希望在每次回复末尾加总结
type: feedback
---

不要在回复末尾总结刚做了什么，用户能看到 diff。

**Why:** 用户明确要求过"stop summarizing what you just did"
**How to apply:** 所有回复结束时，直接结束，不加回顾性总结。
```

### 2.2 四种记忆类型

```typescript
const MEMORY_TYPES = ['user', 'feedback', 'project', 'reference'] as const
```

| 类型 | 用途 | 保存时机 | 作用域（团队模式） |
|------|------|----------|:------------------:|
| **user** | 用户角色、目标、知识背景 | 了解到用户的身份信息时 | 始终私有 |
| **feedback** | 用户对工作方式的指导 | 用户纠正或确认做法时 | 默认私有 |
| **project** | 项目进展、目标、事件 | 了解到工作计划、截止日期时 | 偏向团队 |
| **reference** | 外部系统指针 | 了解到 Linear/Grafana/Slack 等资源时 | 通常团队 |

**每种类型要求的结构：**
- feedback 和 project 类型必须包含 `**Why:**` 和 `**How to apply:**` 行
- 相对日期必须转换为绝对日期（如"周四"→"2026-03-05"）
- user 类型的示例："深度 Go 经验，React 新手——用后端类比解释前端概念"

### 2.3 明确不保存的内容

源码中硬编码了 6 类排除项（即使用户明确要求也不保存）：

1. 代码模式、架构、文件路径、项目结构——可从代码推导
2. Git 历史、最近变更——`git log`/`git blame` 是权威来源
3. 调试方案或修复步骤——修复在代码中，commit message 有上下文
4. CLAUDE.md 中已有的内容——不重复
5. 临时任务细节：进行中的工作、当前对话上下文
6. 如果用户要求保存 PR 列表或活动摘要，要追问"什么是令人意外的或不明显的？"——只保存那部分

### 2.4 MEMORY.md 索引机制

```
MEMORY.md 是索引，不是记忆本身
```

**格式：** 纯 Markdown，无 frontmatter。每条一行，约 150 字符以内：
```markdown
- [用户偏好-简洁回复](feedback_concise.md) — 不在回复末尾加总结
- [项目-合并冻结](project_freeze.md) — 3月5日起移动端发布冻结
```

**限制：**
- 最大 200 行（`MAX_ENTRYPOINT_LINES`）
- 最大 25,000 字节（`MAX_ENTRYPOINT_BYTES`）
- 超出时在末尾追加截断警告
- 截断按行边界执行（不会切断一行的中间）

**两步保存流程：**
1. 写入记忆文件（如 `feedback_concise.md`）
2. 在 MEMORY.md 中添加索引行

可选的 `skipIndex` 模式（通过 `tengu_moth_copse` 特性开关）可跳过第2步。

### 2.5 存储目录结构

```
~/.claude/
  projects/
    -Users-charlesqin-Desktop-myproject/   ← sanitizePath(项目根目录)
      memory/                               ← AUTO_MEM_DIRNAME
        MEMORY.md                           ← 索引文件
        user_role.md                        ← 私有记忆文件
        feedback_testing.md
        project_deadline.md
        reference_linear.md
        team/                               ← 团队记忆子目录
          MEMORY.md                         ← 团队索引
          project_api_migration.md
          reference_oncall_board.md
        logs/                               ← KAIROS 每日日志
          2026/
            03/
              2026-03-31.md
```

### 2.6 路径安全机制

`paths.ts` 包含多层安全验证：

| 安全层 | 检查内容 | 防御目标 |
|--------|----------|----------|
| 绝对路径检查 | 拒绝相对路径 | 路径遍历 |
| 根路径检查 | 拒绝长度 < 3 的路径 | 写入系统根目录 |
| UNC 路径检查 | 拒绝 `\\server\share` 和 `//server/share` | NTLM 凭证泄露 |
| Null 字节检查 | 拒绝包含 `\0` 的路径 | 路径截断攻击 |
| Tilde 展开限制 | 拒绝 `~`、`~/`、`~/.`、`~/..` | 匹配整个 HOME |
| **项目设置排除** | `.claude/settings.json` 不能设 `autoMemoryDirectory` | **恶意仓库重定向写入到 `~/.ssh`** |
| NFC 规范化 | Unicode NFC 标准化 | macOS 路径不一致 |
| Git 根规范化 | worktree 共享主仓库的记忆 | 避免重复记忆目录 |

**关键安全设计：** `projectSettings`（提交到仓库的 `.claude/settings.json`）被有意排除在 `autoMemoryDirectory` 的信任来源之外。源码注释明确说明原因：

```typescript
// SECURITY: projectSettings is intentionally excluded —
// a malicious repo could set autoMemoryDirectory: "~/.ssh"
// and gain write access to sensitive directories
```

---

## 3. 自动记忆提取（extractMemories）

### 3.1 触发时机

```
用户输入 → 模型响应 → 工具执行 → 循环... → 模型最终响应（无工具调用）
                                                    ↓
                                              Stop Hooks 执行
                                                    ↓
                                        executeExtractMemories()  ← 即发即忘
```

**前置条件（全部满足才执行）：**
1. `EXTRACT_MEMORIES` 编译时特性开关开启
2. `isExtractModeActive()` = true（`tengu_passport_quail` GrowthBook 开关）
3. `isAutoMemoryEnabled()` = true
4. 非子代理（`!toolUseContext.agentId`）
5. 非 bare 模式
6. 自上次提取以来有新的模型可见消息

### 3.2 互斥机制

```typescript
// 如果主代理在对话中已经直接写了记忆文件，跳过自动提取
if (hasMemoryWritesSince(lastMemoryMessageUuid)) {
  // 推进游标但不执行提取——避免覆盖用户显式保存的记忆
  lastMemoryMessageUuid = messages[messages.length - 1].uuid
  return
}
```

这防止了自动提取和用户手动保存之间的冲突。

### 3.3 Fork Agent 执行

```typescript
const result = await runForkedAgent({
  messages: conversationMessages,
  system: extractionPrompt,
  maxTurns: 5,           // 硬上限：5轮（读1轮 + 写1-4轮）
  canUseTool: createAutoMemCanUseTool(autoMemPath),
  // ... 共享主会话的 prompt cache
})
```

**工具权限白名单：**

| 工具 | 权限 |
|------|------|
| FileRead | 允许（无限制） |
| Grep | 允许（无限制） |
| Glob | 允许（无限制） |
| Bash | 仅只读命令（ls, find, grep, cat, stat, wc, head, tail） |
| FileEdit | 仅限 `autoMemPath` 内 |
| FileWrite | 仅限 `autoMemPath` 内 |
| MCP / Agent / 写入型 Bash | **全部禁止** |

### 3.4 提取节流

```typescript
let turnsSinceLastExtraction = 0
const turnsBeforeExtraction = getFeatureValue('tengu_bramble_lintel', 1)

// 每 N 轮查询才执行一次提取（默认每轮都执行）
if (turnsSinceLastExtraction < turnsBeforeExtraction) {
  turnsSinceLastExtraction++
  return
}
```

### 3.5 提取后通知

成功提取后，将写入的文件路径列表作为 `SystemMemorySavedMessage` 追加到主对话中，这样主代理知道记忆已更新。

---

## 4. AI 驱动的记忆召回（findRelevantMemories）

### 4.1 召回流程

```
用户发送消息
  ↓
scanMemoryFiles(memoryDir)
  ↓ 递归读取所有 .md 文件（排除 MEMORY.md）
  ↓ 解析前 30 行 frontmatter（description + type）
  ↓ 按 mtime 降序排序，上限 200 个文件
  ↓
过滤掉 alreadySurfaced（之前轮次已展示的路径）
  ↓
selectRelevantMemories(query, memories, signal, recentTools)
  ↓ 构建文本清单：每行 "- [type] filename (timestamp): description"
  ↓ 附加 "Recently used tools: ..." 部分
  ↓
sideQuery → Sonnet 模型
  ↓ 系统提示：SELECT_MEMORIES_SYSTEM_PROMPT
  ↓ 用户消息：Query + Available memories
  ↓ 结构化输出：{ selected_memories: string[] }
  ↓ max_tokens: 256
  ↓
返回最多 5 条 RelevantMemory（路径 + mtime）
```

### 4.2 选择提示词的关键规则

```
- 返回最多 5 个文件名
- 要有选择性和辨别力；如果不确定，不要包含
- 如果提供了最近使用的工具列表：
  ✗ 不要选择这些工具的使用参考/API 文档（已经在用了）
  ✓ 仍然选择这些工具的警告/陷阱/已知问题
```

### 4.3 记忆新鲜度标注

```typescript
function memoryAge(mtimeMs: number): string {
  const days = memoryAgeDays(mtimeMs)
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  return `${days} days ago`
}

function memoryFreshnessText(mtimeMs: number): string {
  if (memoryAgeDays(mtimeMs) <= 1) return ''  // 新鲜记忆不加警告
  return `This memory is ${days} days old.
Memories are point-in-time observations, not live state —
claims about code behavior or file:line citations may be outdated.
Verify against current code before asserting as fact.`
}
```

**设计动机（源码注释）：** 用户报告过过期的记忆被模型当作事实断言。"47 days ago" 比 ISO 时间戳更能触发模型的过期推理。

### 4.4 召回前的验证要求

源码中注入的系统提示明确要求模型在使用记忆前验证：

```
- 如果记忆提到一个文件路径 → 检查文件是否存在
- 如果记忆提到一个函数或标志 → grep 搜索它
- 如果用户即将根据你的建议行动 → 先验证
- "记忆说 X 存在"不等于"X 现在存在"
- 活动日志、架构快照是冻结在某个时间点的，优先使用 git log
```

---

## 5. 会话记忆（Session Memory）

### 5.1 与持久记忆的关键区别

| 维度 | 会话记忆 | 持久记忆 |
|------|----------|----------|
| 生命周期 | 当前会话 | 跨会话永久 |
| 文件数量 | 1 个 | 多个 |
| 触发频率 | 每次后采样（需满足阈值） | 每轮查询结束 |
| 主要用途 | **服务于上下文压缩** | 跨会话知识保留 |
| 记忆提取者 | Fork Agent（仅 FileEdit） | Fork Agent（Read/Write/Edit/Grep） |
| 格式 | 10个固定章节 | 自由格式 + frontmatter |

### 5.2 触发阈值

```typescript
// 默认配置（可通过 GrowthBook tengu_sm_config 远程调整）
const defaults = {
  minimumMessageTokensToInit: 10_000,   // 上下文达到 10K tokens 才激活
  minimumTokensBetweenUpdate: 5_000,    // 每增长 5K tokens 更新一次
  toolCallsBetweenUpdates: 3,           // 且至少 3 次工具调用
}

// 触发条件：
// (token 阈值满足 AND 工具调用阈值满足)
// OR (token 阈值满足 AND 最后一轮助手消息无工具调用)
```

### 5.3 会话记忆模板（10 个固定章节）

```markdown
# Session Memory

## Session Title
_Brief description of what this session is about_

## Current State
_What is the current status of the work_

## Task specification
_Detailed description of the current task requirements_

## Files and Functions
_Key files and functions being worked on_

## Workflow
_Steps being followed or processes in use_

## Errors & Corrections
_Errors encountered and how they were resolved_

## Codebase and System Documentation
_Important codebase patterns, conventions, and system behavior_

## Learnings
_Insights gained during this session_

## Key results
_Important outputs, measurements, or achievements_

## Worklog
_Chronological log of actions taken_
```

### 5.4 大小限制

```typescript
const MAX_SECTION_LENGTH = 2_000      // 每个章节最大 2K tokens
const MAX_TOTAL_SESSION_MEMORY_TOKENS = 12_000  // 整个文件最大 12K tokens
```

### 5.5 与压缩的集成

Session Memory 是上下文压缩的优先路径（参见 `sessionMemoryCompact.ts`）：
- 自动压缩触发时，优先尝试用 Session Memory 作为摘要
- 保留最近 10K-40K tokens 的消息
- 比传统压缩快得多（不调用 LLM），且摘要质量更可预测

### 5.6 自定义

用户可以自定义模板和提示词：
- 模板：`~/.claude/session-memory/config/template.md`
- 提示词：`~/.claude/session-memory/config/prompt.md`（支持 `{{variableName}}` 替换）

---

## 6. 团队记忆同步

### 6.1 前置条件

同时满足才启用：
1. `TEAMMEM` 编译时特性开关开启
2. `isTeamMemoryEnabled()` = true（`tengu_herring_clock` GrowthBook 开关）
3. 第一方 OAuth + 同时拥有 `INFERENCE_SCOPE` 和 `PROFILE_SCOPE`
4. Git remote 是 github.com（非 GitHub 仓库不同步）

### 6.2 API 端点

```
基础 URL: {baseUrl}/api/claude_code/team_memory?repo={owner/repo}
```

| 方法 | 参数 | 用途 | 关键状态码 |
|------|------|------|:----------:|
| GET | `repo={slug}` | 拉取全部团队记忆 | 200 / 304 / 404 |
| GET | `repo={slug}&view=hashes` | 仅拉取哈希（轻量探测） | 200 / 404 |
| PUT | `repo={slug}` | 上传记忆条目（upsert） | 200 / 412 / 413 |

**认证头：** `Authorization: Bearer {oauthToken}`

### 6.3 同步协议

#### 拉取（Pull）

```
1. GET 请求，携带 ETag（条件请求）
2. 304 = 未变化，跳过
3. 200 = 有更新：
   a. 对每个条目验证路径（防遍历攻击）
   b. 跳过 >250KB 的文件
   c. 跳过本地内容已匹配的文件
   d. 并行写入本地文件系统
   e. 刷新 serverChecksums
```

#### 推送（Push — Delta 上传 + 乐观锁）

```
1. readLocalTeamMemory(): 遍历 team/ 目录
   → 每个文件扫描秘密（30种规则）
   → 跳过 >250KB 的文件
   → 计算 SHA-256 哈希

2. 计算 delta：仅本地哈希与 serverChecksums 不同的 key

3. 分批上传：贪心装箱，每批 ≤ 200KB (MAX_PUT_BODY_BYTES)

4. 每批携带 If-Match 头（乐观锁）

5. 冲突处理：
   412 Conflict → 探测 ?view=hashes → 刷新 serverChecksums → 重算 delta → 重试（最多 2 次）
   413 Too Many → 学习 serverMaxEntries 上限，截断后重试

6. 冲突策略：本地优先（local-wins）
   → 当前用户正在编辑的内容覆盖服务端
```

### 6.4 文件监听器

```typescript
// watcher.ts
fs.watch(teamMemDir, { recursive: true })
// macOS: FSEvents（O(1) 文件描述符）
// Linux: inotify（O(子目录数)）

// 2 秒去抖：最后一次变更后 2 秒才触发推送
```

**推送抑制：** 永久失败（no_oauth、no_repo、4xx 非 409/429）后，抑制后续推送，直到发生文件删除（恢复动作）或会话重启。

### 6.5 团队 vs 私有的作用域划分

源码注入的系统提示中，每种记忆类型都带有 XML 作用域标签：

```xml
<type>
  <name>user</name>
  <scope>always private</scope>
  ...
</type>

<type>
  <name>project</name>
  <scope>strongly bias toward team</scope>
  ...
</type>
```

额外安全要求：
```
MUST avoid saving sensitive data within shared team memories
```

---

## 7. 秘密扫描保护

### 7.1 双层防护

| 层 | 时机 | 文件 | 行为 |
|----|------|------|------|
| 写入时拦截 | FileWrite/FileEdit 调用 | `teamMemSecretGuard.ts` | 阻止写入，返回错误 |
| 上传前扫描 | pushTeamMemory 读取本地文件 | `secretScanner.ts` | 跳过该文件，不上传 |

### 7.2 检测的 30 种秘密模式

**云服务商：**
- AWS Access Token（A3T/AKIA/ASIA/ABIA/ACCA 前缀）
- GCP API Key（AIza 前缀）
- Azure AD Client Secret
- DigitalOcean PAT / Access Token

**AI API：**
- Anthropic API Key（`sk-ant-api03-` 前缀，运行时拼接避免自身匹配）
- Anthropic Admin API Key（`sk-ant-admin01-`）
- OpenAI API Key（`sk-proj`/`svcacct`/`admin` + `T3BlbkFJ` 标记）
- HuggingFace Access Token（`hf_`）

**版本控制：**
- GitHub PAT / Fine-grained PAT / App Token / OAuth / Refresh Token
- GitLab PAT / Deploy Token

**通信平台：**
- Slack Bot/User/App Token（`xoxb-`/`xoxp-`/`xapp-`）
- Twilio API Key
- SendGrid API Token

**开发工具：**
- npm Access Token
- PyPI Upload Token
- Databricks API Token
- HashiCorp Terraform API Token
- Pulumi API Token
- Postman API Token

**可观测性：**
- Grafana API Key / Cloud API Token / Service Account Token
- Sentry User/Org Token

**支付：**
- Stripe Access Token（`sk_test`/`live`/`prod` 或 `rk_`）
- Shopify Access Token / Shared Secret

**密码学：**
- PEM 格式私钥（`BEGIN/END PRIVATE KEY` 块）

### 7.3 设计原则

```typescript
// 匹配到的秘密值永远不被记录或返回——只返回规则 ID 和人类可读标签
// Anthropic API key 前缀在运行时拼接，避免匹配自身的 excluded-strings 检查：
const prefix = ['sk', 'ant', 'api'].join('-')
```

---

## 8. KAIROS 模式的记忆（每日日志）

当 KAIROS（AI 助手模式）激活时，记忆范式完全改变：

```
普通模式：写独立文件 + 更新 MEMORY.md 索引
KAIROS 模式：追加到 logs/YYYY/MM/YYYY-MM-DD.md 日志文件
```

- 只追加，不编辑已有内容
- 每日一个文件，按日期路径组织
- 由单独的 `/dream` 技能在夜间蒸馏日志为主题文件和 MEMORY.md
- 提示词中使用 `YYYY-MM-DD` 占位符而非实际日期（因为提示词被缓存，日期变化不会触发失效）

---

## 9. 记忆系统注入的完整系统提示词

### 9.1 个人模式（auto memory）

```
# auto memory

You have a persistent, file-based memory system at `<memoryDir>`.
This directory already exists — write to it directly with the Write tool.

You should build up this memory system over time so that future conversations
can have a complete picture of who the user is, how they'd like to collaborate
with you, what behaviors to avoid or repeat, and the context behind the work.

[如果用户要求记住 → 立即保存]
[如果用户要求忘记 → 找到并删除]

## Types of memory
[4种类型，每种含 description/when_to_save/how_to_use/examples]

## What NOT to save in memory
[6类排除项]

## How to save memories
Step 1: 写入文件（带 frontmatter）
Step 2: 在 MEMORY.md 中添加索引行

## When to access memories
- 看起来相关时
- 用户明确要求时（必须访问）
- 用户说"忽略记忆"时，假装 MEMORY.md 为空

## Before recommending from memory
- 提到文件路径 → 检查文件是否存在
- 提到函数/标志 → grep 搜索
- 用户要行动 → 先验证

## Memory and other forms of persistence
- 实施方案 → 用 Plan，不用记忆
- 当前对话步骤 → 用 Tasks，不用记忆

## Searching past context
[grep 记忆文件，或搜索会话 transcript]

## MEMORY.md
[实际的 MEMORY.md 内容，或"当前为空"]
```

### 9.2 团队模式额外内容

在个人模式基础上增加：

```
## Memory scope
- 私有记忆：<privateDir> — 你的个人偏好、反馈
- 团队记忆：<teamDir> — 项目上下文、外部引用

[类型定义中增加 <scope> XML 标签]

额外安全规则：不得在团队记忆中保存敏感数据
```

---

## 10. 团队记忆的路径安全（深度防御）

`teamMemPaths.ts` 是整个记忆系统中安全措施最密集的文件：

### 10.1 自定义错误类

```typescript
class PathTraversalError extends Error {
  name = 'PathTraversalError'
}
```

### 10.2 sanitizePathKey — 服务端提供的相对路径清理

```typescript
function sanitizePathKey(key: string): string {
  // 1. 拒绝 null 字节
  // 2. URL 编码遍历检测：解码 %2e%2e%2f 等
  // 3. Unicode 规范化攻击：全角字符 \uFF0E\uFF0E\uFF0F → ../
  // 4. 拒绝反斜杠（Windows 路径遍历）
  // 5. 拒绝绝对路径
}
```

### 10.3 realpathDeepestExisting — 符号链接解析

```typescript
async function realpathDeepestExisting(path: string): Promise<string> {
  // 逐级向上 realpath() 直到成功
  // 检测悬挂符号链接（link 存在但 target 不存在）
  //   → 安全威胁：writeFile 会跟随链接在 team 目录外创建文件
  // 检测符号链接循环（ELOOP）→ PathTraversalError
  // 不可恢复的错误（EACCES, EIO）→ fail-closed
}
```

### 10.4 validateTeamMemWritePath — 双重验证

```
写入团队记忆文件前的完整验证链：

第1遍：字符串级
  1. Null 字节检查
  2. path.resolve() 解析
  3. startsWith(teamDir) 验证

第2遍：符号链接级
  4. realpathDeepestExisting() 解析实际路径
  5. isRealPathWithinTeamDir() 验证实际路径在团队目录内

通过 → 返回解析后的路径
失败 → 抛出 PathTraversalError
```

### 10.5 前缀攻击防护

```typescript
// 团队目录路径以分隔符结尾：/foo/team/
// 这样 /foo/team-evil/ 不会通过 startsWith 检查
```

---

## 11. 记忆的生命周期全景

```
会话开始
  │
  ├─ loadMemoryPrompt()
  │   → 读取 MEMORY.md → 注入系统提示
  │
  ├─ initSessionMemory()
  │   → 注册后采样钩子
  │
  ├─ startTeamMemoryWatcher()
  │   → 拉取服务端 → 启动文件监听
  │
  ▼
每轮对话
  │
  ├─ findRelevantMemories(query)
  │   → 扫描文件 → Sonnet 选择 → 返回最多 5 条
  │   → 新鲜度标注（>1天 → 加过期警告）
  │
  ├─ [模型可能直接读/写记忆文件]
  │   → 写入团队记忆 → checkTeamMemSecrets() 拦截秘密
  │   → 文件监听触发 → 2秒后推送到服务端
  │
  ├─ Session Memory 后采样钩子
  │   → 检查阈值 → Fork Agent 更新单文件
  │
  ├─ 模型最终响应（无工具调用）
  │   → Stop Hooks → executeExtractMemories()
  │   → 互斥检查 → Fork Agent 提取 → 更新持久记忆文件
  │
  ▼
自动压缩触发时
  │
  ├─ trySessionMemoryCompaction()（优先路径）
  │   → 用 Session Memory 内容作为摘要
  │   → 保留最近 10K-40K tokens 的消息
  │
  ├─ compactConversation()（回退路径）
  │   → Fork Agent 生成 9 章节结构化摘要
  │
  ▼
会话结束
  │
  ├─ drainPendingExtraction()
  │   → 等待进行中的记忆提取完成
  │
  └─ 团队记忆推送最后一批变更
```

---

## 12. 关键设计决策总结

| 决策 | 原因 |
|------|------|
| 记忆文件是独立的 .md 文件，不是数据库 | 用户可以直接编辑、Git 追踪、跨工具使用 |
| MEMORY.md 是索引不是记忆 | 防止单文件膨胀，支持截断不丢核心内容 |
| 自动提取在 Stop Hook 中即发即忘 | 不阻塞主对话循环 |
| 互斥检查（主代理 vs 自动提取） | 防止覆盖用户显式保存的内容 |
| 召回用 Sonnet 不用 Haiku | 需要理解语义相关性，Haiku 不够准确 |
| 新鲜度用"X days ago"不用 ISO 时间 | 模型对相对时间的推理比绝对时间好 |
| 项目设置排除 autoMemoryDirectory | 防止恶意仓库劫持写入路径 |
| 团队记忆双重路径验证 | 符号链接攻击需要在文件系统层面检查 |
| 秘密模式在运行时拼接 | 避免自身的 excluded-strings 检查 |
| 本地优先的冲突策略 | 用户正在编辑 = 最新意图 |
| 断路器（MAX_CONFLICT_RETRIES = 2） | 防止推送冲突的无限重试 |

---

*来自：AI超元域 | B站频道：https://space.bilibili.com/3493277319825652*

*基于 Claude Code 源码逆向分析，2026-03-31*
