# Claude Code 是否偷换模型？源码级逆向分析

> 基于 Claude Code 源码（2026-03-31 快照，512K 行 TypeScript）逆向分析
> 核心文件：`src/utils/model/model.ts`、`src/services/api/withRetry.ts`、`src/query.ts`、`src/services/api/claude.ts`

---

## 结论先行

**不存在"偷换模型"。你的主对话模型完全由你控制，不会被偷偷降级。**

但 Claude Code 确实在后台使用 Haiku（弱模型）执行辅助任务（配额检查、摘要生成等），这些 Haiku 调用不会出现在你的对话中，也不会替代你与 Opus 的交互。

唯一可能改变主对话模型的场景是 **529 连续过载回退**（Opus → Sonnet），此时会显示明确的系统消息通知用户。

---

## 1. 主对话模型选择：完全由用户控制

### 模型选择优先级（源码确认）

```typescript
// src/utils/model/model.ts:92
function getMainLoopModel(): ModelName {
  const model = getUserSpecifiedModelSetting()
  if (model !== undefined && model !== null) {
    return parseUserSpecifiedModel(model)
  }
  return getDefaultMainLoopModel()
}

// src/utils/model/model.ts:61
function getUserSpecifiedModelSetting(): ModelSetting | undefined {
  // 优先级从高到低：
  // 1. /model 命令（会话内切换）— 最高优先级
  const modelOverride = getMainLoopModelOverride()
  if (modelOverride !== undefined) return modelOverride

  // 2. --model 启动参数 / ANTHROPIC_MODEL 环境变量 / settings.json
  return process.env.ANTHROPIC_MODEL || settings.model || undefined
}
```

**你设了 Opus，主对话就用 Opus。没有任何代码在你不知情的情况下把它换掉。**

### 默认模型

```typescript
// src/utils/model/model.ts:105
function getDefaultOpusModel(): ModelName {
  // 支持环境变量覆盖
  if (process.env.ANTHROPIC_DEFAULT_OPUS_MODEL) {
    return process.env.ANTHROPIC_DEFAULT_OPUS_MODEL
  }
  return getModelStrings().opus46  // 默认 Opus 4.6
}

function getDefaultSonnetModel(): ModelName {
  if (process.env.ANTHROPIC_DEFAULT_SONNET_MODEL) {
    return process.env.ANTHROPIC_DEFAULT_SONNET_MODEL
  }
  // 3P 提供商默认 Sonnet 4.5（可能尚未支持 4.6）
  if (getAPIProvider() !== 'firstParty') return getModelStrings().sonnet45
  return getModelStrings().sonnet46
}

function getDefaultHaikuModel(): ModelName {
  if (process.env.ANTHROPIC_DEFAULT_HAIKU_MODEL) {
    return process.env.ANTHROPIC_DEFAULT_HAIKU_MODEL
  }
  return getModelStrings().haiku45  // Haiku 4.5（所有平台通用）
}
```

---

## 2. 唯一会改变主对话模型的场景：529 过载回退

### 触发条件（极其严格）

```typescript
// src/services/api/withRetry.ts:326-350

// 必须同时满足以下所有条件：
// 1. 收到 529 错误（服务器过载）
// 2. 连续 529 次数 >= MAX_529_RETRIES
// 3. 配置了 fallbackModel
// 4. 以下二选一：
//    a. 设置了 FALLBACK_FOR_ALL_PRIMARY_MODELS 环境变量
//    b. 非 Claude.ai 订阅用户 且 使用非自定义 Opus 模型

if (is529Error(error) &&
    (process.env.FALLBACK_FOR_ALL_PRIMARY_MODELS ||
     (!isClaudeAISubscriber() && isNonCustomOpusModel(options.model)))) {
  consecutive529Errors++
  if (consecutive529Errors >= MAX_529_RETRIES) {
    if (options.fallbackModel) {
      // 触发回退
      throw new FallbackTriggeredError(options.model, options.fallbackModel)
    }
  }
}
```

**关键限制：**

| 条件 | 说明 |
|------|------|
| `!isClaudeAISubscriber()` | **Claude.ai 订阅用户默认不触发回退** |
| `isNonCustomOpusModel()` | 仅对标准 Opus 模型生效（自定义模型 ID 不触发） |
| `MAX_529_RETRIES` | 需要连续多次 529 才触发 |

### 回退执行过程（透明可见）

```typescript
// src/query.ts:894-946

if (innerError instanceof FallbackTriggeredError && fallbackModel) {
  // 1. 切换模型
  currentModel = fallbackModel  // Opus → Sonnet（不是 Haiku）

  // 2. 清理孤立的 assistant 消息
  yield* yieldMissingToolResultBlocks(assistantMessages, 'Model fallback triggered')
  assistantMessages.length = 0

  // 3. 剥离 thinking 签名块（签名绑定原模型，发给回退模型会导致 400）
  // 源码注释：
  // "Strip before retry so the fallback model gets clean history."

  // 4. 更新工具上下文中的模型引用
  toolUseContext.options.mainLoopModel = fallbackModel

  // 5. 记录分析事件
  logEvent('tengu_api_opus_fallback_triggered', {
    original_model: options.model,
    fallback_model: options.fallbackModel,
  })

  // 6. 显示系统消息通知用户（在 UI 中可见）
  `Switched to ${renderModelName(fallbackModel)} due to high demand
   for ${renderModelName(originalModel)}`
}
```

### 回退目标

```typescript
// src/main.tsx:1336-1337
// 回退模型必须与主模型不同
if (fallbackModel && options.model && fallbackModel === options.model) {
  // 验证失败，不设置回退
}

// 回退目标是 Sonnet（不是 Haiku）
// 通过 getDefaultSonnetModel() 获取
```

### 用户如何知道发生了回退

回退时，UI 中会显示一条系统消息：

```
Switched to Claude Sonnet 4.6 due to high demand for Claude Opus 4.6
```

同时在 `AssistantTextMessage.tsx:178` 中提供操作建议：

```
To continue immediately, use /model to switch to Sonnet and continue coding.
```

---

## 3. 后台辅助任务使用 Haiku — 不影响主对话

Claude Code 在后台使用 Haiku（`getSmallFastModel()`）执行多种轻量辅助任务。这些调用**完全独立于你的对话**，不会出现在消息流中。

### 所有 Haiku 使用场景（逐一列出）

#### 3.1 配额检查

```typescript
// src/services/claudeAiLimits.ts:199-218
async function makeTestQuery() {
  const model = getSmallFastModel()  // → Haiku
  const anthropic = await getAnthropicClient({ maxRetries: 0, model, source: 'quota_check' })
  // 发送 max_tokens: 1 的最小请求，仅读取响应头的配额信息
  return anthropic.beta.messages.create({
    model,
    max_tokens: 1,
    messages: [{ role: 'user', content: 'quota' }],
  }).asResponse()
}
```

**用途：** 检测用户是否已达配额限制。只读取 HTTP 响应头，不使用模型输出。

#### 3.2 离开摘要（Away Summary）

```typescript
// src/services/awaySummary.ts:44-52
// 当用户长时间离开后返回时，生成一个简短摘要
{
  thinkingConfig: { type: 'disabled' },  // 关闭思考
  tools: [],                              // 不给工具
  model: getSmallFastModel(),             // → Haiku
}
```

**用途：** 用户长时间不操作后返回时，快速生成"你离开期间发生了什么"的简要摘要。

#### 3.3 Token 计数

```typescript
// src/services/api/claude.ts:540-543
// WARNING: if you change this to use a non-Haiku model,
// this request will fail in 1P unless it uses getCLISyspromptPrefix.
const model = getSmallFastModel()  // → Haiku
// 调用 countTokens API 获取精确 token 数
```

**用途：** 调用 Anthropic 的 `countTokens` 端点获取精确 token 计数，用于自动压缩阈值判断。

#### 3.4 工具使用摘要

```typescript
// src/services/api/claude.ts:3273-3280
// 在主模型流式输出期间，并行用 Haiku 生成工具调用的简短描述
{
  model: getSmallFastModel(),             // → Haiku
  enablePromptCaching: false,
}
```

**用途：** 当模型连续调用多个工具时，生成简短的工具使用描述（如"读取了 config.ts 并修改了第 42 行"）。

源码注释明确说明了并行关系：
```typescript
// src/query.ts:1054
// Yield tool use summary from previous turn —
// haiku (~1s) resolved during model streaming (5-30s)
```
Haiku 在后台 1 秒内完成摘要，同时 Opus 还在处理你的主对话。

#### 3.5 记忆相关性评分

```typescript
// src/memdir/findRelevantMemories.ts
// 用 Sonnet（非 Haiku）评估记忆文件的相关性
// 从标题中选择最多 5 条与当前查询相关的记忆
```

#### 3.6 Web 搜索预处理

```typescript
// src/tools/WebSearchTool/WebSearchTool.ts:280
model: useHaiku ? getSmallFastModel() : context.options.mainLoopModel,
toolChoice: useHaiku ? { type: 'tool', name: 'web_search' } : undefined,
```

**用途：** 当条件满足时（`useHaiku` 标志），用 Haiku 预处理搜索查询。

#### 3.7 其他辅助调用

| 调用者 | 模型 | 用途 |
|--------|------|------|
| `tokenEstimation.ts` | Haiku | Vertex 全局区域 token 计数回退 |
| `analyzeContext.ts` | Haiku | 上下文分析的 countTokens 回退 |
| `claudeAiLimits.ts` | Haiku | 配额状态检查 |
| Bedrock `client.ts` | Haiku | 小模型可指定不同 AWS 区域 |

### 辅助任务 vs 主对话的隔离

```
你的对话：
  用户 → [Opus 4.6] → 助手响应 → [Opus 4.6] → 助手响应 → ...

后台并行：
  [Haiku] → 配额检查（1 token）
  [Haiku] → 工具使用摘要（~1s）
  [Haiku] → token 计数

两条线完全隔离，Haiku 的输出不进入你的对话消息流。
```

---

## 4. Fast Mode：同模型加速，不换模型

这是一个常见误解，源码中有明确声明：

```typescript
// src/constants/prompts.ts:702
`Fast mode for Claude Code uses the same ${FRONTIER_MODEL_NAME} model
 with faster output. It does NOT switch to a different model.
 It can be toggled with /fast.`
```

Fast Mode 通过 API 的 speed 参数请求更快的输出，模型不变。如果 API 拒绝 fast mode（如组织未启用），会自动降回标准速度：

```typescript
// src/services/api/withRetry.ts:310-313
if (wasFastModeActive && isFastModeNotEnabledError(error)) {
  handleFastModeRejectedByAPI()
  retryContext.fastMode = false
  continue  // 重试，同一模型，标准速度
}
```

---

## 5. Plan Mode 临时模型切换 — 透明可见

```typescript
// src/commands/model/model.tsx:214
// Do not update fast mode in settings since this is an automatic downgrade

// src/commands/model/model.tsx:256
onDone(`Current model: ${chalk.bold(renderModelLabel(mainLoopModelForSession))}
  (session override from plan mode)\nBase model: ${displayModel}`)
```

Plan Mode 可能临时使用 Sonnet 执行实现步骤，但：
- UI 显示 "session override from plan mode"
- 显示 Base model 让你知道原始模型
- 不修改 settings 中的模型设置

---

## 6. Effort 降级 — 不换模型，换参数

```typescript
// src/utils/effort.ts:162
// API rejects 'max' on non-Opus-4.6 models — downgrade to 'high'.
```

如果设置了 `effort: max` 但模型不支持，会降级 effort 参数（max → high），不换模型。

---

## 7. 全局搜索：不存在的场景

通过对 512K 行源码的全局搜索，以下场景**被确认不存在**：

| 假设的偷换场景 | 搜索结果 | 证据 |
|----------------|----------|------|
| 根据订阅层级偷换弱模型 | **不存在** | `getMainLoopModel()` 不检查订阅类型 |
| 根据额度用量偷换弱模型 | **不存在** | 额度用完返回 429 错误，不换模型 |
| 随机/概率性降级到弱模型 | **不存在** | 无 `Math.random()` 与模型选择相关的代码 |
| A/B 测试使用弱模型回答 | **不存在** | GrowthBook 控制功能开关，不控制模型 |
| 静默替换后不通知用户 | **不存在** | 529 回退有系统消息，其他场景不换主模型 |
| 把 Opus 对话路由到 Haiku | **不存在** | Haiku 仅用于辅助任务 |
| 根据问题复杂度选择弱模型 | **不存在** | 主循环始终使用用户指定的模型 |
| 根据时间段降级（如高峰期） | **不存在** | 无时间相关的模型选择逻辑 |
| 首次用户用弱模型 | **不存在** | 默认模型是 Opus 4.6 |

---

## 8. 模型使用全景图

```
┌─────────────────────────────────────────────────────────┐
│                   你的主对话                              │
│                                                         │
│  模型：你指定的（默认 Opus 4.6）                          │
│  控制：/model 命令 > --model 参数 > 环境变量 > 设置       │
│  唯一例外：529 连续过载 → Sonnet 回退（有通知）            │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                   后台辅助任务（Haiku）                    │
│                                                         │
│  配额检查      → 1 token 请求，只读响应头                 │
│  Token 计数    → countTokens API 调用                    │
│  工具摘要      → 并行于主对话，~1s 完成                    │
│  离开摘要      → 用户回来时显示简要信息                    │
│  Web 搜索      → 搜索查询预处理（条件触发）                │
│                                                         │
│  这些不进入你的对话消息流                                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                   Fork Agent 任务                        │
│                                                         │
│  上下文压缩    → 使用你的主模型（共享 prompt cache）       │
│  记忆提取      → 使用你的主模型                           │
│  权限分类器    → Haiku（auto 模式下的命令安全分类）        │
│                                                         │
│  压缩结果进入上下文，但不替代你的对话                      │
└─────────────────────────────────────────────────────────┘
```

---

## 9. 如何验证你正在使用的模型

### 方法 1：查看 API 响应

每条助手消息的内部结构中包含模型信息：

```typescript
// AssistantMessage.message.model 字段包含实际使用的模型 ID
// 例如："claude-opus-4-6-20260301"
```

### 方法 2：使用 /cost 命令

`/cost` 命令显示按模型分类的 token 使用量，你可以看到每个模型消耗了多少 token。

### 方法 3：检查 status line

状态栏显示当前模型名称。如果发生回退，会更新为回退后的模型。

### 方法 4：环境变量调试

```bash
# 查看所有 API 调用的模型信息
export CLAUDE_CODE_DEBUG=1

# 强制禁用回退
unset FALLBACK_FOR_ALL_PRIMARY_MODELS
```

---

## 10. 总结

| 问题 | 答案 | 依据 |
|------|------|------|
| Opus 会被偷偷换成 Haiku 吗？ | **不会** | Haiku 仅用于辅助任务，不进入主对话 |
| Opus 会被偷偷换成 Sonnet 吗？ | **仅在 529 连续过载时，且会通知** | `withRetry.ts:347` + `query.ts:946` |
| Claude.ai 订阅用户会被降级吗？ | **默认不会** | `!isClaudeAISubscriber()` 条件排除 |
| 后台有 Haiku 调用吗？ | **有，但不影响你的对话** | 6 种辅助任务，全部隔离 |
| Fast Mode 换模型吗？ | **不换** | 源码明确声明 "does NOT switch to a different model" |
| 有没有根据问题难度选模型？ | **没有** | 主循环始终使用用户指定模型 |

**一句话：你付费用 Opus，对话就用 Opus。Haiku 只在幕后干杂活。**

---

*来自：AI超元域 | B站频道：https://space.bilibili.com/3493277319825652*

*基于 Claude Code 源码逆向分析，2026-03-31*
