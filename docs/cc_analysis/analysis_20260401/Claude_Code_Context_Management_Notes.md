# Claude Code 上下文管理算法学习笔记

> 来源：Claude Code 源码快照（2026-03-31）
> 核心文件：`src/query.ts`, `src/services/compact/`, `src/utils/toolResultStorage.ts`

---

## 架构总览：7 层递进式防御

每轮 query loop 按以下顺序执行，从便宜到昂贵，每一层减轻压力，可能阻止下一层触发：

```
1. Tool Result Budget    ← 单轮预算（同步，零 API 调用）
2. Snip Compact          ← 历史裁剪（零 API 调用）
3. Microcompact          ← 工具结果精细清理（零或极低 API 成本）
4. Context Collapse      ← 增量投影摘要（零 API 调用）
5. Auto-Compact          ← LLM 全量摘要（昂贵）
6. Blocking Limit        ← 硬停（所有自动措施关闭时）
7. Reactive Compact      ← 413 错误后紧急摘要（最后手段）
```

互斥门控防止昂贵操作竞争：Context Collapse 启用时抑制 Auto-Compact，Reactive Compact 实验模式抑制主动 Auto-Compact。

---

## 第 1 层：Tool Result Budget — 单轮聚合预算

**问题**：N 个并行工具可能在一轮中集体产生超大上下文。

**三分区算法**：

| 分区 | 含义 | 处理 |
|------|------|------|
| mustReapply | 之前已替换过的结果 | 直接重用缓存的替换字符串（零 I/O，字节级一致） |
| frozen | 之前见过但没替换 | 永不替换（保护 prompt cache） |
| fresh | 新结果 | 参与预算分配 |

**阈值**：
- 总预算：200K 字符/消息（远程可配置）
- 单工具上限：50K 字符（默认）
- 超出时：保留前 ~2KB 预览 + 持久化到磁盘，模型可用 Read 按需读取

**核心洞察**：frozen 分区 — 宁可浪费空间也不破坏缓存命中率。**Prompt cache 稳定性优先于空间效率**。

---

## 第 2 层：Snip Compact — 历史裁剪

**特点**：零 API 调用，直接删除旧消息。

**协调机制**：snipTokensFreed 传递给下游层，因为 tokenCountWithEstimation 读的是上一轮 API 返回的 input_tokens（反映 snip 前的数值），需要手动减去 snip 释放的量。

**双视图**：REPL 保留被 snip 的消息用于 UI 回滚，但投影层在发送 API 前过滤掉它们。

---

## 第 3 层：Microcompact — 三种精细清理路径

### 3a. 基于时间的清理

```
触发条件：距上次助手消息 > 60 分钟（= 服务端 cache TTL）
逻辑：cache 已过期 → 全量前缀会被重写 → 趁机清理旧工具结果
行为：替换为 "[Old tool result content cleared]"
保留：最近 5 个结果
```

**洞察**：利用缓存 TTL 过期的"免费窗口"搭车做清理。

### 3b. 缓存编辑（Cache Editing）— 最精妙的设计

```
触发条件：可压缩工具结果数超过阈值
关键创新：不修改本地消息！使用 API 的 cache_edits / cache_reference 机制
效果：服务端缓存被精确编辑，本地保持不变
确认：用 API 返回的 cache_deleted_input_tokens（非客户端估算）
范围：仅主线程，仅特定工具（FileRead, Bash, Grep, Glob 等）
```

**洞察**：读写分离 — 本地消息不变（保证重放一致性），服务端缓存被精确编辑（节省空间）。

### 3c. API 原生上下文管理

```
策略：clear_tool_uses + clear_thinking
触发：输入超 180K tokens
目标：保留最后 40K tokens
思考块：cache 冷（>1h）时仅保留最后一轮思考
```

---

## 第 4 层：Context Collapse — 增量投影式摘要（CQRS 思想）

**核心思想**：不破坏性替换消息，而是维护一个 commit log，每轮查询时 project 出压缩视图。

**阈值**：
- 90% 上下文窗口 → 开始提交 collapse
- 95% 上下文窗口 → 阻塞新 spawn
- ~93%（auto-compact 位置）→ 被抑制避免竞争

**关键 API**：
- `applyCollapsesIfNeeded()` — 投影压缩视图 + 可选提交新 collapse
- `recoverFromOverflow()` — 413 时排空所有暂存 collapse（第一道防线）
- `projectView()` — 每轮重放提交日志

**设计亮点**：
- Collapse 摘要存在 commit store 中，而非 REPL 消息数组 → 跨轮持久化
- REPL 保留完整历史（UI 回滚），API 调用看到投影视图（节省 tokens）
- 会话恢复时从 commits + snapshot 重建

---

## 第 5 层：Auto-Compact — 带熔断的 LLM 摘要

**触发**：`tokenCount > contextWindow - 13,000`

### 摘要 prompt 结构

```xml
<analysis>（内部草稿，生成后丢弃）</analysis>
<summary>
  1. Primary Request / Intent
  2. Key Technical Concepts
  3. Files / Code
  4. Errors / Fixes
  5. Problem Solving
  6. All User Messages（用户说过的每句话都保留）
  7. Pending Tasks
  8. Current Work
  9. Optional Next Step
</summary>
```

### Prompt Cache 共享优化

摘要子 agent 复用主对话的缓存前缀（通过 runForkedAgent）。
没有此优化：cache miss 率 98%，浪费全局 ~38B tok/天的 cache_creation。

### PTL（Prompt-Too-Long）重试

```
最多重试 3 次：
  → 按 API 轮次分组（groupMessagesByApiRound）
  → 丢弃最老的组以覆盖 token 缺口
  → 无法精确计算时 fallback 丢弃 20% 的组
图片：所有图片/文档块替换为 [image]/[document] 标记后再发送
```

### 熔断器

```
MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3
触发后：本会话剩余时间停止尝试
背景数据：~1,279 个会话曾出现 50+ 次连续失败（最高 3,272 次），
          每天浪费 ~250K API 调用
```

### Post-Compact 恢复清单

| 恢复项 | 预算 |
|--------|------|
| 最近读取的文件 | 最多 5 个，每个 5K tokens，总计 50K |
| Skill 附件 | 每个 5K，总计 25K |
| Plan 状态 | 完整恢复 |
| Deferred tools | 完整恢复 |
| Agent 列表 | 完整恢复 |
| MCP 指令 | 完整恢复 |

### Session Memory Compact（替代路径）

在 auto-compact 中**优先尝试**，失败回退到完整 LLM 摘要：
```
用预提取的 session memory 替代 LLM 摘要
保留范围：从最后摘要消息向后扩展
  满足 minTokens(10K) 且 minMessages(5)
  不超过 maxTokens(40K)
不变量：tool_use / tool_result 对永不拆分
```

---

## 第 6-7 层：Reactive Compact + 错误恢复级联

### 5 层错误恢复（从便宜到昂贵）

```
API 返回 prompt_too_long 或媒体尺寸被拒
  |
  v
Layer 1: Context Collapse drain（排空所有暂存 collapse，最便宜）
  |  失败
  v
Layer 2: Reactive Compact（完整 LLM 摘要）
  |  失败
  v
Layer 3: Max Output 升级（8K → 64K tokens）
  |  失败
  v
Layer 4: Multi-turn Recovery（注入 nudge 消息，最多 3 次）
  |  失败
  v
Layer 5: Model Fallback（切换到备用模型）
```

### 错误扣留（Error Withholding）模式

```
流式传输期间，可恢复错误不 yield 给调用者
  → 推入 assistantMessages 供恢复检查
  → 防止 SDK 消费者终止会话
  → 所有恢复手段都失败后才暴露给用户
```

防循环守卫：`hasAttemptedReactiveCompact` 防止同一轮无限重试。

---

## Token Budget Continuation — 输出预算跟踪（附加机制）

```
用途：长任务自动续跑（不是上下文管理，是输出预算控制）
完成阈值：输出 < 预算 90% → 继续
递减检测：连续 3+ 次续跑 且 最近两次增量 < 500 tokens → 停止
每次续跑注入 nudge 消息告知进度百分比
```

---

## 值得借鉴的设计原则

### 1. Prompt Cache 稳定性高于空间效率

- frozen 分区：进入 cache 的内容永不修改
- 字节级替换一致性：mustReapply 重用完全相同的替换字符串
- Tool pool 排序稳定：`assembleToolPool()` 排序防止 MCP 变化破坏缓存
- 缓存编辑不改本地消息：读写分离保证重放一致性

### 2. 分层防御，从便宜到昂贵

7 层递进，每层有可能阻止下一层触发。互斥门控防止昂贵操作竞争（collapse 抑制 autocompact）。snipTokensFreed 显式传递确保下游层看到真实 token 数。

### 3. 错误扣留 + 延迟恢复

流式传输中不立即暴露可恢复错误。给恢复机制留出空间后再决定是否暴露。这个模式可以推广到任何有多层 fallback 的系统。

### 4. CQRS 式双视图

REPL 保留完整历史（UI 回滚 + 会话恢复），API 看到投影视图（节省 tokens）。Context Collapse 的 commit log 和 projectView 就是这个思想的实现。

### 5. 熔断器模式

连续失败 3 次后停止重试。用真实数据驱动：1,279 个会话的失控循环 → 250K API 调用/天的浪费。

### 6. 利用缓存 TTL 做"免费清理"

cache 自然过期（60min）时搭车执行清理。既然前缀要重建，就把脏活一起干了。

### 7. Post-Compact 不从零开始

摘要后精心恢复关键上下文（最近文件、plan、skills）。有明确的 token 预算分配，不是全量恢复也不是什么都不恢复。

### 8. 不变量保护无处不在

- tool_use / tool_result 对永不拆分
- Compact 边界消息记录 pre-compact 状态供恢复重链
- Partial compact 的 "up_to" 变体清除旧边界防止级联剪枝 bug
- 子 agent compact 不重置主线程的模块级状态

---

## Query Loop 状态机一览

```typescript
State = {
  messages,
  toolUseContext,
  autoCompactTracking,          // 熔断计数
  maxOutputTokensRecoveryCount, // 输出恢复计数
  hasAttemptedReactiveCompact,  // 防循环守卫
  maxOutputTokensOverride,      // 8K → 64K 升级
  pendingToolUseSummary,
  stopHookActive,
  turnCount,
  transition                    // 状态转移原因
}

transition 类型：
  collapse_drain_retry
  reactive_compact_retry
  max_output_tokens_escalate
  max_output_tokens_recovery
  stop_hook_blocking
  token_budget_continuation
```

每轮不是递归而是 `while(true)` + 显式状态转移，避免长会话栈溢出。
