# Claude Code 多 Agent 架构深度分析

> 基于源码约 **13,700 行、37+ 文件**的深度探索，涵盖 `src/utils/swarm/`、`src/tools/AgentTool/`、`src/coordinator/` 等核心模块。

---

## 一、整体架构

系统采用 **Leader-Worker 模型**，核心有三种执行后端和两种编排模式：

```
                        ┌─────────────────────────────┐
                        │     用户请求 (REPL/CLI)       │
                        └──────────┬──────────────────┘
                                   │
                        ┌──────────▼──────────────────┐
                        │     Leader Agent (team-lead)  │
                        │     QueryEngine → query()     │
                        └──┬────────┬────────┬────────┘
                           │        │        │
              ┌────────────▼┐  ┌────▼─────┐  ┌▼────────────┐
              │  InProcess   │  │  Tmux    │  │  iTerm2     │
              │  (同进程)     │  │ (分屏)   │  │  (分屏)     │
              └──────────────┘  └──────────┘  └─────────────┘
                     │               │              │
              AsyncLocalStorage   独立进程         独立进程
              隔离上下文          文件邮箱通信      文件邮箱通信
```

**两种编排模式：**

- **Team Mode** — 通过 `TeamCreate` 创建团队，手动管理 Worker
- **Coordinator Mode** — 自动化编排，Coordinator 只能用 Agent/TaskStop/SendMessage 三个工具

---

## 二、Agent Tool — 统一入口

`src/tools/AgentTool/AgentTool.tsx` 是所有子 Agent 的统一入口。

### 2.1 输入参数

| 参数 | 类型 | 作用 |
|------|------|------|
| `prompt` | string | 任务描述 |
| `subagent_type` | string | Agent 类型 (Explore, Plan, 自定义等) |
| `model` | `'sonnet'\|'opus'\|'haiku'` | 模型覆盖 |
| `run_in_background` | boolean | 后台异步执行 |
| `name` | string | 命名，使其可通过 SendMessage 寻址 |
| `team_name` | string | 团队名 |
| `mode` | string | 权限模式 (plan, acceptEdits 等) |
| `isolation` | `'worktree'` | Git worktree 隔离 |

### 2.2 路由决策树

```
call() 入口 (AgentTool.tsx:284)
  ├── team_name + name → spawnTeammate() → 生成持久化队友
  ├── isolation === 'remote' → Cloud Code Runner
  ├── run_in_background === true → runAsyncAgentLifecycle() (fire-and-forget)
  └── 默认 → runAgent() 同步执行，阻塞父 Agent
```

### 2.3 关键常量

```typescript
// src/tools/AgentTool/constants.ts
AGENT_TOOL_NAME = 'Agent'
LEGACY_AGENT_TOOL_NAME = 'Task'  // 向后兼容
ONE_SHOT_BUILTIN_AGENT_TYPES = {'Explore', 'Plan'}
```

---

## 三、Agent 定义系统

`src/tools/AgentTool/loadAgentsDir.ts` (755行) 负责从多来源加载 Agent 定义。

### 3.1 AgentDefinition 类型

```typescript
type AgentDefinition = {
  agentType: string           // 唯一标识
  whenToUse: string           // 何时使用的描述
  tools: string[]             // 可用工具列表，['*'] 表示全部
  disallowedTools: string[]   // 禁用工具
  model: string               // 模型选择
  permissionMode: string      // 权限模式
  maxTurns: number            // 最大对话轮次
  background: boolean         // 是否后台运行
  isolation: 'worktree'       // 隔离方式
  getSystemPrompt()           // 系统提示词生成函数
}
```

### 3.2 三种来源

- `BuiltInAgentDefinition` — 内置 Agent (source: 'built-in')
- `CustomAgentDefinition` — 用户自定义 `.claude/agents/*.md` 文件
- `PluginAgentDefinition` — 插件提供的 Agent

### 3.3 内置 Agent 类型

| Agent | 模型 | 工具 | 特点 |
|-------|------|------|------|
| `general-purpose` | 默认 | `['*']` | 全能通用 |
| `Explore` | haiku | 只读工具 | 代码探索，禁止编辑/写入/嵌套 Agent |
| `Plan` | inherit | 只读工具 | 架构规划，禁止编辑 |
| `verification` | inherit | 只读 | 后台对抗性测试，红色标识 |
| `statusline-setup` | sonnet | Read, Edit | 状态栏配置专用 |
| `fork` (合成) | inherit | `['*']` | 继承父上下文，权限冒泡 |
| `claude-code-guide` | — | 有限工具 | Claude Code 使用指南 |

### 3.4 加载优先级

```
built-in < plugin < userSettings < projectSettings < flagSettings < policySettings
```

后加载的同名 Agent 覆盖先加载的。

---

## 四、三大执行后端

### 4.1 InProcess 后端 (同进程)

**文件**: `src/utils/swarm/backends/InProcessBackend.ts` (339行)

最轻量的方式——所有 Worker 运行在**同一个 Node.js 进程**中：

```
Leader 进程
  ├── AsyncLocalStorage<TeammateContext> #1 → Worker A
  ├── AsyncLocalStorage<TeammateContext> #2 → Worker B
  └── AsyncLocalStorage<TeammateContext> #3 → Worker C
```

**核心流程：**

1. `spawn()` → `spawnInProcessTeammate()` 注册到 AppState
2. `startInProcessTeammate()` fire-and-forget 启动 Agent 循环
3. 通过 `runWithTeammateContext(context, fn)` 包裹执行，实现上下文隔离
4. 权限请求直接使用 Leader 的 `ToolUseConfirm` 对话框（通过 `leaderPermissionBridge.ts`）

**上下文隔离** (`src/utils/teammateContext.ts`, 96行)：

```typescript
// AsyncLocalStorage 实现进程内隔离
const teammateContextStorage = new AsyncLocalStorage<TeammateContext>()

function runWithTeammateContext(context: TeammateContext, fn: () => T): T {
  return teammateContextStorage.run(context, fn)
}

function isInProcessTeammate(): boolean {
  return teammateContextStorage.getStore() !== undefined
}
```

### 4.2 Tmux 后端 (终端分屏)

**文件**: `src/utils/swarm/backends/TmuxBackend.ts` (764行)

每个 Worker 是一个**独立的 Claude CLI 进程**，运行在 tmux 分屏中。

**两种模式：**

**Leader 在 tmux 内：**
```
┌─────────────────┬──────────────────┐
│                 │    Worker A      │
│    Leader       ├──────────────────┤
│    (30%)        │    Worker B      │
│                 ├──────────────────┤
│                 │    Worker C      │
└─────────────────┴──────────────────┘
         main-vertical 布局
```

**Leader 在 tmux 外：** 创建 `claude-swarm-{pid}` 独立 session，tiled 布局。

**关键细节：**
- `acquirePaneCreationLock()` 序列化并行 spawn，防止竞态
- 200ms shell 初始化延迟等待 rc 文件加载
- 通过 `tmux send-keys` 向 pane 发送命令
- 支持 `hidePane()` (break-pane) / `showPane()` (join-pane)

### 4.3 iTerm2 后端

**文件**: `src/utils/swarm/backends/ITermBackend.ts` (370行)

通过 `it2` CLI (Python 自动化工具) 控制 iTerm2：

- 首个 Worker 垂直分割，后续水平分割
- 死会话恢复：split 失败时验证 session list 并重试
- `setPaneBorderColor`/`rebalancePanes` 为 no-op（避免频繁启动 Python 进程）
- `supportsHideShow = false`（无等效的 tmux break-pane）

### 4.4 后端选择逻辑

`src/utils/swarm/backends/registry.ts` 的 `detectAndGetBackend()` (line 136)：

```
优先级瀑布:
1. 在 tmux 内？ → TmuxBackend (原生)
2. 在 iTerm2 且有 it2 CLI？ → ITermBackend
3. 在 iTerm2 无 it2？ → 回退 tmux，提示安装 it2
4. 有 tmux？ → TmuxBackend (外部 session)
5. 非交互模式 (-p)？ → InProcessBackend
6. teammateMode 配置为 'in-process'？ → InProcessBackend
7. 都没有 → 报错并给出平台特定安装指引
```

---

## 五、核心通信机制 — 文件邮箱

### 5.1 邮箱结构

`src/utils/teammateMailbox.ts` (1,183行)

每个 Agent 拥有一个 JSON 文件邮箱：

```
~/.claude/teams/{team_name}/inboxes/{agent_name}.json
```

```typescript
type TeammateMessage = {
  from: string       // 发送者名称
  text: string       // 消息内容
  timestamp: string  // 时间戳
  read: boolean      // 是否已读
  color?: string     // 发送者 UI 颜色
  summary?: string   // 5-10 字摘要
}
```

### 5.2 核心操作

| 函数 | 作用 |
|------|------|
| `writeToMailbox()` | 原子写入 + `proper-lockfile` 文件锁（10次重试，5-100ms 退避） |
| `readMailbox()` | 读取所有消息 |
| `readUnreadMessages()` | 过滤未读消息 |
| `markMessagesAsRead()` | 标记已读 |

### 5.3 结构化消息类型

邮箱不仅传递文本，还定义了一套协议消息：

- `createShutdownRequestMessage` / `createShutdownApprovedMessage` — 关闭协议
- `createPermissionRequestMessage` / `createPermissionResponseMessage` — 权限请求/响应
- `createSandboxPermissionRequestMessage` / `createSandboxPermissionResponseMessage` — 沙箱网络权限
- `createIdleNotification` — Worker 空闲通知

### 5.4 轮询机制

| Agent 类型 | 轮询方式 |
|------------|----------|
| Pane 类 Worker | `useInboxPoller` React hook 定期轮询 |
| InProcess Worker | `waitForNextPromptOrShutdown()` 直接读邮箱 |
| Leader | `useInboxPoller` 处理权限请求、空闲通知等 |

---

## 六、SendMessage Tool — Agent 间通信

`src/tools/SendMessageTool/SendMessageTool.ts` (917行)

### 6.1 输入参数

```typescript
{
  to: string      // 收件人名称、"*" 广播、"uds:<socket>"、"bridge:<session-id>"
  summary: string // 5-10 字摘要
  message: string | ShutdownRequest | ShutdownResponse | PlanApprovalResponse
}
```

### 6.2 路由逻辑

```
SendMessage.call() (line 741)
  ├── to: "bridge:<session-id>" → postInterClaudeMessage (跨机器 Remote Control)
  ├── to: "uds:<socket>"        → sendToUdsSocket (Unix Domain Socket 本地通信)
  ├── to: "*"                   → 广播到所有团队成员邮箱
  ├── to: "<name>"              → 查 agentNameRegistry:
  │     ├── InProcess Agent running → queuePendingMessage (内存队列)
  │     ├── InProcess Agent stopped → resumeAgentBackground (自动唤醒!)
  │     └── Pane Agent → writeToMailbox (文件邮箱)
  └── 结构化消息 → 分发到对应处理器
```

**关键设计：Agent 的纯文本输出对其他 Agent 不可见，必须通过 SendMessage 通信。**

---

## 七、权限委托系统

### 7.1 完整流程

`src/utils/swarm/permissionSync.ts` (928行)

```
Worker 遇到需要权限的操作
    ↓
检查 bash classifier 能否自动批准 (swarmWorkerHandler.ts:52)
    ↓ 不能
创建 PermissionRequest 对象 (line 71)
    ↓
注册回调 BEFORE 发送请求 (避免竞态, line 79)
    ↓
发送 permission_request 到 Leader 邮箱 (line 123)
    ↓
显示 "waiting for leader" 状态 (line 126)
    ↓
Leader 轮询检测到请求
    ↓
在 Leader UI 展示权限对话框（带 worker badge）
    ↓
用户批准/拒绝
    ↓
Leader 发送 permission_response 到 Worker 邮箱
    ↓
Worker 轮询获取响应（每 500ms），继续执行
```

### 7.2 InProcess 优化路径

通过 `leaderPermissionBridge.ts` (54行)，InProcess Worker 直接使用 Leader 的 `ToolUseConfirm` 队列：

```typescript
// REPL 注册权限 UI
registerLeaderPermissionQueue(setToolUseConfirmQueue, setToolPermissionContext)

// Worker 推送权限请求到 Leader UI，带 worker badge
pushToLeaderPermissionQueue(request, workerBadge)
```

跳过文件邮箱的 I/O 开销，提供与 Leader 自身工具相同的 UI 体验。

### 7.3 SwarmPermissionRequest 结构

```typescript
type SwarmPermissionRequest = {
  id: string
  workerId: string
  workerName: string
  toolName: string
  toolUseId: string
  description: string
  input: any
  permissionSuggestions: any
  status: 'pending' | 'approved' | 'rejected'
  resolvedBy?: string
  feedback?: string
  updatedInput?: any
  permissionUpdates?: any
}
```

### 7.4 权限模式继承

当 Leader 批准 Worker 的 plan 时：

```typescript
const modeToInherit = leaderMode === 'plan' ? 'default' : leaderMode
```

团队文件中每个成员有独立的 `mode` 字段，支持通过 `setMemberMode()` / `setMultipleMemberModes()` 动态调整。

---

## 八、Agent 执行引擎

### 8.1 runAgent() — 子 Agent 核心驱动

`src/tools/AgentTool/runAgent.ts` (973行)

`runAgent()` 是一个 `AsyncGenerator<Message, void>`：

```
runAgent() (line 248)
  1. 解析模型 → getAgentModel()
  2. 创建隔离上下文 → createSubagentContext()
     - fork 父消息到独立上下文
     - 隔离的文件状态缓存
  3. 初始化 Agent 专属 MCP servers → initializeAgentMcpServers()
  4. 解析工具集 → resolveAgentTools()
  5. 构建系统提示词 (Agent 自身 + 环境信息)
  6. 注册 Perfetto 追踪, hooks
  7. 调用 query() — 与主 REPL 完全相同的 agentic 循环
  8. yield 每条消息回父 Agent
  9. 清理 MCP servers, shell tasks, agent tracking
```

**核心设计：子 Agent 复用完全相同的 `query()` 循环**，递归地拥有完整的工具执行能力。

### 8.2 异步 Agent 生命周期

`agentToolUtils.ts` 的 `runAsyncAgentLifecycle()` (line 508)：

```
registerAsyncAgent() → 创建 task entry
    ↓
注册 name 到 agentNameRegistry (用于 SendMessage 路由)
    ↓
void runWithAgentContext(...) → fire-and-forget
    ↓
迭代 runAgent() 的消息流
    ↓
ProgressTracker 追踪:
  - tool use 次数
  - token 消耗
  - 最近活动
    ↓
完成时 finalizeAgentTool():
  - 提取最终文本内容
  - 计算 totalDurationMs, totalTokens, totalToolUseCount
    ↓
completeAsyncAgent() → 标记 task 完成
    ↓
发送 <task-notification> XML 通知父 Agent
```

**多个异步 Agent 是真正并行的**——每个都是独立的 async 操作。

### 8.3 工具过滤

`agentToolUtils.ts` 的 `filterToolsForAgent()` (line 70) 使用多层禁用列表：

| 禁用列表 | 适用范围 | 禁用的工具 |
|----------|----------|-----------|
| `ALL_AGENT_DISALLOWED_TOOLS` | 所有 Agent | TaskOutput, ExitPlanMode, EnterPlanMode, AskUserQuestion, TaskStop |
| `CUSTOM_AGENT_DISALLOWED_TOOLS` | 非内置 Agent | 同上 + AgentTool |
| `ASYNC_AGENT_ALLOWED_TOOLS` | 后台 Agent | 白名单制：Read, Grep, Glob, Edit, Write, WebSearch 等 |
| `COORDINATOR_MODE_ALLOWED_TOOLS` | Coordinator | 仅 Agent, TaskStop, SendMessage, SyntheticOutput |

---

## 九、Coordinator Mode — 自动化编排

`src/coordinator/coordinatorMode.ts` (369行)

### 9.1 激活条件

```typescript
function isCoordinatorMode(): boolean {
  return feature('COORDINATOR_MODE') && process.env.CLAUDE_CODE_COORDINATOR_MODE === '1'
}
```

### 9.2 工作流程

```
Coordinator (只能用 Agent + TaskStop + SendMessage)
    │
    ├── Research Phase → 并行派出多个 Worker 调研
    │       ├── Worker A: 搜索代码
    │       ├── Worker B: 读取文档
    │       └── Worker C: 分析依赖
    │
    ├── Synthesis Phase → Coordinator 综合分析研究结果
    │
    ├── Implementation Phase → Worker 执行代码实现
    │
    └── Verification Phase → Worker 验证实现结果
```

### 9.3 Coordinator 系统提示词要点

`getCoordinatorSystemPrompt()` (line 111) 的 369 行提示词规定：

- Coordinator 通过 `Agent` 工具派出 Worker，通过 `SendMessage` 继续对话，通过 `TaskStop` 终止
- Worker 完成时发送 `<task-notification>` XML
- 明确的 spawn vs continue 决策指导
- 并发管理策略

---

## 十、Team Mode — 持久化协作

### 10.1 团队文件结构

`~/.claude/teams/{team-name}/config.json`：

```typescript
type TeamFile = {
  name: string
  description: string
  createdAt: string
  leadAgentId: string
  leadSessionId: string
  hiddenPaneIds: string[]
  teamAllowedPaths: string[]
  members: [{
    agentId: string          // 格式: name@teamName
    name: string
    agentType: string
    model: string
    color: string
    planModeRequired: boolean
    joinedAt: string
    tmuxPaneId?: string
    cwd: string
    worktreePath?: string
    sessionId: string
    subscriptions: string[]
    backendType: 'tmux' | 'iterm2' | 'in-process'
    isActive: boolean
    mode: string
  }]
}
```

### 10.2 团队工作流

```
1. TeamCreate → 创建 config.json + tasks 目录
2. TaskCreate → 在 ~/.claude/tasks/{team-name}/ 创建任务
3. Agent tool (team_name + name) → 派出 teammate
4. TaskUpdate → 分配任务 owner
5. Teammate 工作 → 完成后自动发送 idle notification
6. SendMessage(shutdown_request) → 优雅关闭 teammate
```

### 10.3 Teammate 系统提示词附加

`src/utils/swarm/teammatePromptAddendum.ts`：

> "You are running as an agent in a team. To communicate with anyone on your team, use the SendMessage tool. Just writing a response in text is not visible to others."

---

## 十一、Worktree 隔离

`src/utils/worktree.ts` 的 `createAgentWorktree()` (line 902)

### 11.1 创建流程

```
Agent spawn 时 isolation='worktree'
  → 生成 slug: agent-{agentId前8字符}
  → validateWorktreeSlug() — 拒绝路径穿越，限制64字符
  → 路径: .claude/worktrees/<slug>
  → 分支: worktree-<slug>
  → git worktree add -B worktree-<slug>
  → performPostCreationSetup():
      - 复制 settings.local.json
      - 配置 git hooks
      - 符号链接目录
      - 复制 .worktreeinclude 文件
```

### 11.2 清理流程

```
Agent 完成时:
  → hasWorktreeChanges()?
      ├── 有改动 → 保留 worktree，在 <task-notification> 中报告路径和分支
      └── 无改动 → removeAgentWorktree() 自动清理
```

---

## 十二、Worker 完整生命周期

### 12.1 诞生

```
Leader 调用 Agent tool
  ├── InProcess: spawnInProcessTeammate()
  │     1. 生成 agentId = name@teamName
  │     2. 创建独立 AbortController（不链接到 Leader）
  │     3. 创建 TeammateContext for AsyncLocalStorage
  │     4. 注册 InProcessTeammateTaskState 到 AppState
  │     5. startInProcessTeammate() → runWithTeammateContext() → runAgent()
  │
  └── Pane: PaneBackendExecutor.spawn()
        1. assignTeammateColor() 分配颜色
        2. createTeammatePaneInSwarmView() 创建分屏
        3. 构建 CLI 命令:
           claude --agent-id X --agent-name Y --team-name Z
                  --agent-color C --parent-session-id P
        4. sendCommandToPane() 发送命令
        5. writeToMailbox() 写入初始 prompt
```

### 12.2 执行

```
InProcess Runner (inProcessRunner.ts, 1552行):
  runWithTeammateContext() 包裹:
    → runAgent() → query() 循环
    → 轮询邮箱获取新消息（注入为 user-turn messages）
    → 权限请求转发到 Leader UI
    → ProgressTracker 追踪工具使用和 token
    → 支持 auto-compact（上下文过大时自动压缩）
```

### 12.3 通信

```
Worker → Leader: writeToMailbox() 或 queuePendingMessage (InProcess)
Leader → Worker: writeToMailbox() 或 SendMessage
Worker → Worker: SendMessage tool → writeToMailbox()
广播: SendMessage(to: "*") → 写入所有成员邮箱
```

### 12.4 终止

三条终止路径：

| 方式 | 触发 | 流程 |
|------|------|------|
| 优雅关闭 | `shutdown_request` via mailbox | Worker 处理请求 → 退出 → idle notification |
| 强制终止 (InProcess) | `killInProcessTeammate()` | abort AbortController → 更新 task 状态为 'killed' → 移出团队文件 |
| 强制终止 (Pane) | `backend.killPane(paneId)` | 杀死 tmux/iTerm2 pane |

### 12.5 会话清理

`cleanupSessionTeams()` 在 Leader 退出时运行：
- 杀死所有孤立 pane
- 移除团队和任务目录
- 销毁 git worktree

---

## 十三、Feature Gates 汇总

| Feature Flag | 控制内容 | 激活方式 |
|-------------|---------|---------|
| `COORDINATOR_MODE` | Coordinator 自动编排 | 编译时 + `CLAUDE_CODE_COORDINATOR_MODE=1` |
| `FORK_SUBAGENT` | Fork 模式子 Agent | 编译时 feature gate |
| `BUILTIN_EXPLORE_PLAN_AGENTS` | Explore/Plan 内置 Agent | 编译时 + A/B test `tengu_amber_stoat` |
| `VERIFICATION_AGENT` | 验证 Agent | 编译时 + gate `tengu_hive_evidence` |
| Agent Teams (Swarm) | 团队协作模式 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` + GrowthBook gate |

---

## 十四、通信协议总览

| 通道 | 机制 | 方向 | 用途 |
|------|------|------|------|
| 文件邮箱 `inboxes/{name}.json` | JSON + 文件锁 | 任意 Agent → 任意 Agent | 所有 teammate 消息、权限、关闭协议 |
| 内存队列 `pendingUserMessages` | AppState | 父 → InProcess 子 | 运行中 Agent 的即时消息 |
| Leader Permission Bridge | 模块级函数注册 | InProcess Worker → Leader UI | 权限弹窗 |
| UDS Socket | Unix Domain Socket | Session → Session (本地) | 跨 session 消息 |
| Bridge (Remote Control) | HTTP via Anthropic | Session → Session (跨机器) | 远程控制消息 |
| Task 系统 | 文件 `~/.claude/tasks/` | 所有团队成员 | 工作项追踪、状态更新 |
| `<task-notification>` XML | 注入对话 | 后台 Agent → 父 Agent | 完成/失败通知 |

---

## 十五、架构规模统计

| 层次 | 核心组件 | 代码规模 |
|------|---------|---------|
| 入口 | AgentTool | ~800行 |
| 执行引擎 | runAgent + query() 循环 | ~2,700行 |
| Agent 定义 | loadAgentsDir + builtInAgents | ~850行 |
| 后端管理 | registry + 3个后端实现 | ~1,800行 |
| 通信 | teammateMailbox + SendMessageTool | ~2,100行 |
| 权限委托 | permissionSync + leaderPermissionBridge | ~1,000行 |
| 团队管理 | teamHelpers + spawnMultiAgent | ~1,800行 |
| 上下文隔离 | agentContext + teammateContext | ~300行 |
| Coordinator | coordinatorMode + workerAgent | ~400行 |
| InProcess Runner | inProcessRunner | ~1,550行 |
| **总计** | **37+ 文件** | **~13,700行** |

---

## 十六、核心设计理念

1. **query() 循环复用** — 子 Agent 使用与主 REPL 完全相同的 agentic 循环，天然具备完整工具能力
2. **AsyncLocalStorage 隔离** — InProcess 模式下零 IPC 开销，通过 Node.js 原生机制隔离上下文
3. **文件邮箱统一通信** — 跨进程、跨后端的统一消息协议，用文件锁保证并发安全
4. **权限始终由人类把控** — 无论多少层 Agent 嵌套，危险操作最终都路由到 Leader 的 UI 由用户决定
5. **优雅降级** — 从 iTerm2 → tmux → InProcess，自动选择最佳可用后端
6. **Fire-and-forget 异步** — 后台 Agent 通过 `<task-notification>` XML 非侵入式通知父 Agent
