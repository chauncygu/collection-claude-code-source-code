# Claude Code 值得借鉴的算法与设计模式

> 来源：Claude Code 源码快照（2026-03-31）
> 上下文管理部分见另一份笔记 `Claude_Code_Context_Management_Notes.md`

---

## 目录

1. [权限系统：多层安全级联](#1-权限系统多层安全级联)
2. [流式工具执行：模型推理与工具执行重叠](#2-流式工具执行模型推理与工具执行重叠)
3. [并发控制与重试策略](#3-并发控制与重试策略)
4. [终端渲染引擎：双缓冲 + Diff 写入](#4-终端渲染引擎双缓冲--diff-写入)
5. [纯 TypeScript 原生模块移植](#5-纯-typescript-原生模块移植)
6. [FileEditTool：12 步验证链](#6-filedittool12-步验证链)
7. [记忆系统：提取与召回](#7-记忆系统提取与召回)
8. [多 Agent 协调：Swarm 架构](#8-多-agent-协调swarm-架构)
9. [启动优化：并行预取](#9-启动优化并行预取)
10. [其他精巧设计](#10-其他精巧设计)

---

## 1. 权限系统：多层安全级联

### 1.1 Bash 命令权限解析（8 步级联）

文件：`src/tools/BashTool/bashPermissions.ts`

```
Step 0: Tree-sitter AST 解析
  → simple（干净命令）/ too-complex（无法静态分析）/ parse-unavailable（降级正则）
  + Shadow 模式：Tree-sitter 观察性运行，记录与 legacy 路径的分歧

Step 1: 沙盒自动放行
  → sandboxing 启用 + autoAllowBashIfSandboxed → 允许
  → 复合命令拆分，逐子命令检查 deny 规则

Step 2: 精确匹配权限检查
  → 优先级：deny > ask > allow > passthrough

Step 3: LLM 分类器 deny/ask 规则
  → Haiku 模型并行分类 deny 和 ask 描述列表
  → 仅高置信度结果触发

Step 4: 命令操作符拆分
  → 对 |, &&, ||, ; 递归调用权限检查
  → 即使管道段被允许，原始命令仍重新验证

Step 5: Legacy 误解析门控
  → 仅当 Tree-sitter 不可用时运行

Step 6: 逐子命令检查
  → splitCommand → 过滤 cd ${cwd} → checkCommandAndSuggestRules

Step 7: 8 步子级联
  → 精确匹配 → 前缀 deny → ask 规则 → 路径约束
  → 精确 allow → 前缀/通配符 allow → sed 约束
  → 模式权限 → 只读检查 → passthrough
```

### 1.2 规则匹配中的安全技巧

**复合命令防护**：前缀和通配符规则拒绝匹配复合命令。防止 `cd /path && python3 evil.py` 被 `cd:*` 规则放行。

**环境变量剥离的不对称设计**：
- Deny 规则：使用激进的 `stripAllLeadingEnvVars`（固定点循环剥离所有环境变量），防止 `FOO=bar denied_cmd` 绕过
- Allow 规则：使用保守的 `stripSafeWrappers`，只接受白名单中的 ~60 个安全环境变量

**安全环境变量白名单**（SAFE_ENV_VARS）：
- 包含：`NODE_ENV`, `RUST_LOG`, `CGO_ENABLED` 等
- 排除：`PATH`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, `DYLD_*`, `PYTHONPATH`, `NODE_OPTIONS`, `BASH_ENV`

### 1.3 Shell 安全分析（23 个验证器）

文件：`src/tools/BashTool/bashSecurity.ts`

按安全优先级排序的验证链：

| 验证器 | 检测内容 |
|--------|---------|
| `validateJqCommand` | `system()`, `-f`, `--from-file`, `-L` |
| `validateObfuscatedFlags` | 引号内隐藏的标志（如 `"-rf"`） |
| `validateShellMetacharacters` | 参数中的 `;`, `\|`, `&` |
| `validateDangerousVariables` | `BASH_ENV`, `PROMPT_COMMAND`, `PS1`, `BASH_FUNC_*` |
| `validateCommentQuoteDesync` | 引号内的 `#`（注释跟踪混淆） |
| `validateCarriageReturn` | CR 字符（shell-quote/bash 分词差异） |
| `validateIFSInjection` | `IFS=` 赋值 |
| `validateDangerousPatterns` | 反引号, `$()`, `${}`, zsh 扩展 (`=cmd`, `~[`, `(e:`) |
| `validateUnicodeWhitespace` | 非 ASCII 空白字符 |
| `validateBraceExpansion` | `{...,...}` 模式 |
| `validateZshDangerousCommands` | 20+ 个 zsh 内建命令（`zmodload`, `syswrite`, `ztcp` 等） |

**关键排序技巧**：非误解析验证器的 `ask` 结果被延迟返回。循环继续运行误解析验证器；只有没有误解析验证器触发时，延迟的非误解析结果才被返回。防止非误解析的 `ask` 掩盖应该设置 `isBashSecurityCheckForMisparsing` 的误解析 `ask`。

### 1.4 只读命令分类（双层判定）

文件：`src/tools/BashTool/readOnlyValidation.ts`

**Tier 1 — Flag 级别白名单**：每个命令的每个 flag 都有类型标注（`none`, `number`, `string`, 特定字面量）。特例：
- `xargs` 的 `-i`/`-e` 被移除（GNU `getopt_long` 可选参数语义漏洞）
- `tree` 的 `-R` 被移除（它会写文件）
- `fd`/`fdfind` 的 `-x`/`--exec` 被排除

**Tier 2 — 正则匹配**：`cat`, `head`, `tail`, `wc`, `jq`, `echo`, `pwd` 等简单命令。

**复合命令安全**：`cd && git` 组合被阻止（沙盒逃逸 — 通过恶意 git hooks）。检测写入 `.git/hooks/`、`objects/`、`refs/` 后运行 git 的命令链。

### 1.5 Auto-Mode (YOLO) 分类器

文件：`src/utils/permissions/yoloClassifier.ts`

**不是传统 ML — 是 LLM 即分类器**。

**两阶段 XML 分类**：
```
Stage 1（快速判定）：
  max_tokens=64, stop_sequences=['</block>']
  → "no"（允许）：立即返回
  → "yes" 或无法解析：升级到 Stage 2

Stage 2（深度推理）：
  max_tokens=4096, 启用 chain-of-thought
  → 用 <thinking> 标签推理后再决定
  → 解析时先剥离 <thinking> 块再匹配 <block> 标签
```

**200ms 竞赛模式**（interactiveHandler.ts）：
```
5 个参赛者同时启动：
  1. 用户权限对话框
  2. Hooks 异步执行
  3. Bash 分类器异步执行
  4. Bridge 权限响应（claude.ai）
  5. Channel 权限中继（Telegram 等）

createResolveOnce 原子 claim() — 第一个到达的赢，其他 no-op

200ms 宽限期：
  前 200ms 内忽略用户交互（防止意外按键取消分类器）
  200ms 后任何用户交互都会杀死分类器的自动批准机会
```

**投机性分类器检查**：在权限对话框出现之前就启动分类器（`startSpeculativeClassifierCheck`），与 deny/ask 分类器、hooks、对话框设置并行运行。

---

## 2. 流式工具执行：模型推理与工具执行重叠

文件：`src/services/tools/StreamingToolExecutor.ts`

### 核心思想

工具在模型**还在生成 token 时就开始执行**，而非等完整响应结束。

### 并发控制算法

```typescript
canExecuteTool(isConcurrencySafe: boolean): boolean {
  const executing = this.tools.filter(t => t.status === 'executing')
  return (
    executing.length === 0 ||
    (isConcurrencySafe && executing.every(t => t.isConcurrencySafe))
  )
}
```

- 没有正在执行的工具 → 可以执行
- 自身并发安全 且 所有正在执行的也并发安全 → 可以执行
- 否则 → 等待

### 工具状态机

```
queued → executing → completed → yielded
```

队列有序处理。非并发工具遇到无法执行时直接 break（保持严格顺序）；并发工具可跳过。

### 错误级联

**只有 Bash 错误才取消兄弟工具**。原因：Bash 命令有隐式依赖链（mkdir 失败 → 后续命令无意义）。Read/WebFetch 等独立工具不取消。

`siblingAbortController` 是 parent 的子控制器 — 兄弟子进程立即死亡，但父 query loop 不中断。

### 进度流式传输

使用 Promise 信号机制（`progressAvailableResolve`）。`getRemainingResults()` async generator 用 `Promise.race` 在工具完成和新进度到达之间等待，确保进度消息实时传递而非缓冲。

### 与 query.ts 的集成

```
流式循环中：
  API content_block_stop 事件
    → 立即 yield AssistantMessage
    → query.ts 喂给 StreamingToolExecutor.addTool()
  
  事件间隙：
    → getCompletedResults() 收割已完成的工具
  
  流式结束后：
    → getRemainingResults() 排空所有待处理工具
```

---

## 3. 并发控制与重试策略

### 3.1 并发 Generator 合并（all 函数）

文件：`src/utils/generators.ts`

```
维护 waiting 队列 + active Promise 集合
1. 初始填充 concurrencyCap 个 generator
2. Promise.race 所有活跃 generator
3. 某个 yield → 立即 .next() 推进它
4. 某个完成 → waiting 中取一个填补
5. 公平交错 + 有界并行（默认上限 10）
```

### 3.2 工具并发安全分类

| 分类 | 工具 | 依据 |
|------|------|------|
| 始终安全 | FileRead, LSP, TaskCreate, TaskGet, Brief | 返回 `true` |
| 输入依赖 | BashTool | 委托给 `isReadOnly(input)`，只读命令并发，写命令独占 |
| 默认不安全 | FileEdit, FileWrite 等 | 使用默认 `false`（fail-closed） |

### 3.3 指数退避 + 抖动重试

文件：`src/services/api/withRetry.ts`

```
baseDelay = min(500ms * 2^(attempt-1), 32s)
jitter = random(0, 25% * baseDelay)       // 加性抖动，非乘性
finalDelay = baseDelay + jitter
// server retry-after header 存在时覆盖
```

**529（过载）处理 — 级联放大防护**：
```
非前台查询（摘要、标题、分类器）→ 收到 529 立即放弃（不重试）
前台查询 → 重试最多 3 次
3 次 529 后 → FallbackTriggeredError → 切换备用模型
```

**Fast Mode 降级**：
```
429/529 + fast mode 激活：
  retry-after < 20s → 继续 fast mode 重试（保持 prompt cache）
  retry-after ≥ 20s → 冷却（最少 10min）切换标准速度
```

**无人值守模式**（`CLAUDE_CODE_UNATTENDED_RETRY`）：
```
429/529 无限重试，最大退避 5 分钟
长休眠拆为 30s 心跳间隔（防止主机标记会话空闲）
6 小时硬上限重置
```

### 3.4 流式看门狗

文件：`src/services/api/claude.ts`

```
空闲超时默认 90s（可配置）
50% 时间 → 警告
100% 时间 → 硬中止挂起的流
每个 chunk 重置计时器
```

---

## 4. 终端渲染引擎：双缓冲 + Diff 写入

### 4.1 双缓冲帧交换

文件：`src/ink/ink.tsx`, `src/ink/output.ts`, `src/ink/screen.ts`

```
每次渲染后：
  backFrame = frontFrame
  frontFrame = newFrame
```

**Screen 缓冲区**：packed `Int32Array`，每个单元格 2 个 word（8 bytes）。
- Word 0: char pool ID
- Word 1: style ID + hyperlink ID + cell width（位打包）
- `resetScreen()` 复用同一 buffer（只增不缩），用 `BigInt64Array` 视图批量清零

**charCache**（16384 上限）：跨帧缓存 grapheme 聚类结果，大多数行不变时直接命中。

### 4.2 Diff 算法

文件：`src/ink/screen.ts` (diffEach), `src/ink/log-update.ts`

```
1. 计算两帧 damage rectangle 的并集
2. 仅在 damage 区域内逐 word 比较 Int32Array
3. findNextDiff() 是纯函数，设计为 JIT 内联
4. VirtualScreen 跟踪光标位置，只在目标不一致时发移动指令
```

**关键优化**：
- **DECSTBM 硬件滚动**：ScrollBox 的 scrollTop 变化时用终端硬件滚动（`CSI top;bot r + CSI n S/T`），而非重写整个区域。先对 prev.screen 执行 `shiftRows()` 模拟硬件位移，后续 diff 自然只找到新滚入的行。
- **StylePool.transition()**：按 (fromId, toId) 对缓存 ANSI 样式转换字符串 — 预热后零分配
- **fg-only 空格跳过**：只有前景色的空格单元格视为不可见，跳过写入

### 4.3 Blit 优化

文件：`src/ink/render-node-to-output.ts`

```
节点干净（not dirty）且布局位置不变
  → 直接从 prevScreen 复制单元格（blit）
  → blitRegion() 使用 TypedArray.set() 批量内存拷贝
  → 每行一次调用，连续全宽区域只需一次
  → 跳过整个子树的重新渲染
```

### 4.4 渲染器 Peephole 优化

文件：`src/ink/optimizer.ts`

单趟扫描 Diff 数组：
- 合并连续 `cursorMove`（加 dx/dy）
- 折叠连续 `cursorTo`（只保留最后一个）
- 拼接相邻 `styleStr`
- 取消 cursor hide/show 对
- 去重相同 URI 的 hyperlink patch
- 移除 count=0 的 clear patch

---

## 5. 纯 TypeScript 原生模块移植

### 5.1 Yoga 布局引擎（C++ → TypeScript）

文件：`src/native-ts/yoga-layout/index.ts`（~2400 行）

完整的 Flexbox 布局实现，消除了 native binary 依赖。

**多层缓存策略**：
| 缓存 | 机制 | 效果 |
|------|------|------|
| Dirty-flag | 干净子树 + 匹配输入 → 跳过 | 最基本的剪枝 |
| 双槽缓存 | 分别缓存 layout 和 measure 结果 | 同一节点两种调用模式 |
| 4 槽环形缓存 | packed Float64Array | 500 消息 scrollbox: 76k→4k layoutNode 调用 |
| flex-basis 缓存 | generation-stamped | 短路递归 computeFlexBasis |
| 快速路径标志 | `_hasAutoMargin` 等 | 全零情况单分支跳过 |

**`resolveEdges4Into()`**：一次遍历解析全部 4 条物理边到预分配元组，提升共享 fallback 查找。

### 5.2 模糊搜索（Rust nucleo/fzf → TypeScript）

文件：`src/native-ts/file-index/index.ts`

**逐步过滤架构**：
```
Step 1: 字符位图过滤（O(1) 拒绝）
  → 每个路径一个 26-bit charBits 掩码
  → (charBits & needleBitmap) !== needleBitmap → 跳过

Step 2: 融合 indexOf 扫描
  → String.indexOf()（V8/JSC 中 SIMD 加速）
  → 同时找到匹配位置 + 累积 gap/consecutive 分数
  → 无需第二次评分遍历

Step 3: Gap-bound 拒绝
  → 计算分数上限（所有边界奖励）减去已知 gap 惩罚
  → 无法超过当前 top-k 阈值 → 跳过昂贵的边界评分

Step 4: 边界/驼峰评分
  → 路径分隔符 (/\-_.) 匹配奖励
  → 驼峰转换匹配奖励
  → 首字符匹配奖励
  → 常数近似 nucleo/fzf-v2 权重

Top-k 维护：升序数组 + 二分插入（避免全量 O(n log n) 排序）
```

**其他特性**：
- 异步构建：每 ~4ms yield 事件循环，`readyCount` 支持构建中的部分索引搜索
- 智能大小写：全小写查询 = 大小写不敏感；有大写 = 敏感
- 测试文件惩罚：路径包含 "test" → 1.05x 分数惩罚

### 5.3 语法高亮 + Word-Level Diff（Rust syntect/bat → TypeScript）

文件：`src/native-ts/color-diff/index.ts`

- highlight.js 延迟加载（避免 ~200ms 的 190+ 语法注册启动成本）
- `diff` npm 包的 `diffArrays` 做词级 diff
- RGB → ANSI-256 颜色近似：移植 `ansi_colours` Rust crate 的立方体 vs 灰阶感知最近索引算法
- Monokai Extended / GitHub-light 作用域到颜色映射
- Storage 关键字重分割（highlight.js 把 `const`/`function`/`class` 归为 "keyword"；端口重分割以匹配 syntect 的 cyan storage 颜色）

---

## 6. FileEditTool：12 步验证链

文件：`src/tools/FileEditTool/FileEditTool.ts`

```
 1. 密钥检测 → 阻止向 team memory 文件写入密钥
 2. 空操作检测 → old_string === new_string 直接拒绝
 3. Deny 规则检查 → 文件路径匹配 deny 权限规则
 4. UNC 路径安全 → 跳过 \\server\share（防止 NTLM 凭证泄露）
 5. 文件大小守卫 → > 1 GiB 拒绝
 6. 编码检测 → UTF-16LE BOM (0xFF 0xFE) / UTF-8, \r\n → \n
 7. 文件存在检查 → 不存在时建议相似文件（findSimilarFile）
 8. 空 old_string → 仅在文件为空时允许（创建文件场景）
 9. Notebook 重定向 → .ipynb 必须使用 NotebookEditTool
10. 陈旧性检测 → mtime 比较，失败时回退到内容比较（避免云同步/杀毒软件时间戳干扰的误报）
11. 引号规范化 → 弯引号→直引号搜索；写入时用启发式恢复弯引号样式
12. 歧义匹配 → 多处匹配 + 非 replace_all → 拒绝并要求更多上下文
```

### 引号规范化算法（utils.ts）

```
搜索阶段：
  1. 精确匹配 old_string → 找到则使用
  2. normalizeQuotes(old_string) → 弯引号转直引号
  3. 在 normalizeQuotes(fileContent) 中搜索
  4. 返回 fileContent 中的原始子串（保留弯引号）

写入阶段（preserveQuoteStyle）：
  检测到规范化被应用时：
  → 将 new_string 中的直引号转回弯引号
  → 启发式：空白/行首/开括号后 = 开引号；字母间 = 撇号
```

### 反序列化映射（desanitizeMatchString）

模型不会看到某些 XML 标签（发送给 API 前被清理）。当模型在编辑中输出清理后的形式时，反向映射：
- `<fnr>` → `<function_results>`
- `\n\nH:` → `\n\nHuman:`

### call() 写入路径中的双重陈旧性检查

```
validateInput 时检查一次陈旧性
  → 通过
    → call() 中重新同步读取文件，再次检查
    → 防止 validate 和 call 之间的 TOCTOU 竞态
```

---

## 7. 记忆系统：提取与召回

### 7.1 记忆提取（extractMemories）

文件：`src/services/extractMemories/`

**架构**：每个完整 query loop 结束时，fork 一个子 agent（共享父级 prompt cache）执行提取。

```
提取流程：
1. 门控：仅主 agent，非子 agent，非远程模式
2. 重叠守卫：已有提取在运行 → 暂存当前上下文（最新覆盖旧的）
3. 轮次节流：合格轮次未达阈值 → 跳过
4. 互斥：主 agent 已手动写入记忆 → 跳过并推进游标
5. 注入记忆清单：扫描目录 + 读 frontmatter → 预格式化
6. Fork agent 执行：最多 5 轮，受限工具访问
7. 游标推进：仅在成功后；失败时留在原位以重新考虑
8. 尾随运行：完成后检查暂存的待处理上下文
```

**工具限制**：Read/Grep/Glob 无限制；只读 Bash；Edit/Write 仅限记忆目录内。

### 7.2 记忆召回（findRelevantMemories）

文件：`src/memdir/findRelevantMemories.ts`

**不是启发式评分 — 是 LLM 评分**：

```
Phase 1: 扫描
  → 读取记忆目录所有 .md 文件（排除 MEMORY.md）
  → 每个文件读前 30 行提取 frontmatter（name, description, type）
  → 按 mtime 降序排列，上限 200 个文件
  → 单遍设计：读取后排序（而非 stat-排序-读取），syscall 减半

Phase 2: LLM 选择
  → 发送查询 + 格式化清单 + 最近使用工具列表给 Sonnet
  → 结构化 JSON 输出
  → "只包含你确定有帮助的记忆。不确定就不包含。最多 5 个。"
  → 最近使用工具列表防止为已活跃使用的工具推荐 API 文档
  → 但关于这些工具的警告/陷阱仍然会被选中

Phase 3: 新鲜度处理
  → 超过 1 天的记忆注入 <system-reminder> 告警
  → "此记忆已 N 天。关于代码行为的声明可能过时。"
```

**already-surfaced 过滤**：过滤掉之前轮次已展示的路径，5 个名额全部花在新候选上。

---

## 8. 多 Agent 协调：Swarm 架构

### 8.1 协调者模式（Coordinator）

文件：`src/coordinator/coordinatorMode.ts`

```
任务工作流阶段：
  Research（并行 workers）→ Synthesis（协调者）→ Implementation（workers）→ Verification（workers）

并发规则：
  只读任务 → 自由并行
  写密集任务 → 按文件区域串行
  验证可与不同文件的实现重叠

Worker prompt 必须自包含：
  Worker 看不到协调者对话 → 每个 prompt 需要完整上下文（文件路径、行号等）

Continue vs Spawn 决策：
  高上下文重叠 → continue（复用已加载上下文）
  低上下文重叠 → spawn 新 worker
```

### 8.2 两种后端策略

| 后端 | 隔离方式 | 通信 | 特点 |
|------|---------|------|------|
| In-Process | `AsyncLocalStorage` 上下文隔离 | 基于文件的 mailbox | 共享 API client + MCP 连接；独立 AbortController（leader 中断不杀 worker） |
| Pane-Based (tmux/iTerm2) | 独立 OS 进程 | 基于文件的 mailbox | CLI flag 传播（`--agent-id`, `--agent-name`, `--team-name`, `--agent-color`）；leader 的模型/权限/环境变量全部传播 |

### 8.3 权限桥接

In-process teammate 通过 `leaderPermissionBridge` 路由权限提示到 leader 的 UI（复用 BashPermissionRequest、FileEditToolDiff 等对话框）。Bridge 不可用时回退到 mailbox 权限同步。

### 8.4 Fork Subagent

文件：`src/tools/AgentTool/forkSubagent.ts`

```
子进程继承父级完整对话上下文 + system prompt

递归 fork 防护：
  isInForkChild() 检查对话历史中的 <fork_boilerplate> 标签

Cache 共享设计：
  保留完整父级 assistant 消息（所有 tool_use 块）
  构建 tool_result 块（占位文本："Fork started -- processing in background"）
  只有最后的 text 块不同 → 最大化 prompt cache 命中

子进程 10 条严格规则：
  不生成子 agent、不评论、只用工具、提交变更、
  结构化输出（Scope/Result/Key files/Files changed/Issues）、最多 500 字
```

---

## 9. 启动优化：并行预取

文件：`src/main.tsx` 前 20 行

```typescript
// 这些副作用必须在所有其他 import 之前运行：
profileCheckpoint('main_tsx_entry')     // 标记入口（在 ~135ms import 之前）
startMdmRawRead()                       // 并行：MDM 子进程读取（plutil/reg query）
startKeychainPrefetch()                 // 并行：macOS 钥匙串双读取
                                        // 无此优化：~65ms 同步阻塞（每次 macOS 启动）
```

**启动分析器**（`startupProfiler.ts`）：
- 采样日志：内部 100%，外部 0.5%。记录 import_time, init_time, settings_time, total_time
- 详细分析：`CLAUDE_CODE_PROFILE_STARTUP=1`，带 `process.memoryUsage()` 快照的完整时间线
- 非采样用户零开销（`profileCheckpoint` 立即返回）

---

## 10. 其他精巧设计

### 10.1 35 行状态管理

文件：`src/state/store.ts`

```typescript
createStore<T>(initialState, onChange?) => {
  getState()          // 返回当前状态
  setState(updater)   // updater: (prev) => next
                      // Object.is() 相等检查（引用相同则跳过）
                      // 触发 onChange + 通知 Set<Listener>
  subscribe(listener) // 返回 unsubscribe
}
```

无中间件，无选择器，无 devtools。配合 `useSyncExternalStore` 实现最小化重渲染。

### 10.2 ToolSearchTool — 延迟工具发现

文件：`src/tools/ToolSearchTool/ToolSearchTool.ts`

**两种查询模式**：

直接选择（`select:ToolA,ToolB`）：精确查找，返回 `tool_reference` 块。

关键词搜索评分：
| 匹配类型 | 分数 |
|---------|------|
| 名称部分精确匹配 | +10（MCP: +12） |
| 名称部分子串匹配 | +5（MCP: +6） |
| 全名回退 | +3 |
| searchHint 词边界匹配 | +4 |
| 描述词边界匹配 | +2 |

`+` 前缀标记必需词（全部必须匹配才入围）。

工具名解析：MCP 工具去 `mcp__` 前缀后按 `__` 和 `_` 分割；普通工具按驼峰转换和 `_` 分割。

### 10.3 Token 估算（无 API 调用）

文件：`src/utils/tokens.ts`

```
粗略估算：content.length / bytesPerToken

文件类型感知：
  JSON/JSONL/JSONC: 2 bytes/token（密集单字符 token）
  其他: 4 bytes/token

区块级估算：
  text/thinking: length / 4
  image/document: 固定 2000 tokens
  tool_use: (name + JSON.stringify(input)).length / 4

上下文窗口估算（tokenCountWithEstimation）：
  1. 从后向前找到最后一条有 API usage 数据的消息
  2. 处理并行工具调用：跨越共享 message.id 的兄弟记录
  3. 返回 usage.input_tokens + 粗略估算(后续消息)
  4. 无 usage 数据时全量粗略估算
```

### 10.4 错误扣留模式（Error Withholding）

```
流式传输中可恢复错误不暴露给调用者：
  → prompt_too_long, media_size, max_output_tokens
  → 推入 assistantMessages 供恢复检查
  → 所有恢复失败后才 yield 给用户
  → 防止 SDK 消费者在中间错误时终止会话
```

### 10.5 Prompt Cache 稳定性设计集锦

| 技术 | 位置 | 效果 |
|------|------|------|
| 工具池排序 | `assembleToolPool()` | 防止 MCP 变更破坏缓存前缀 |
| 系统 prompt 分界标记 | `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` | 静态部分 `scope: global` 跨组织缓存 |
| Agent 列表附件注入 | AgentTool prompt.ts | 从工具描述中移出动态列表（减少 10.2% cache_creation） |
| Fork 消息构造 | forkSubagent.ts | 所有子进程共享相同 tool_result 占位符，仅最后文本块不同 |
| Tool result 替换一致性 | toolResultStorage.ts | mustReapply 重用完全相同的替换字符串（字节级一致） |
| frozen 分区 | toolResultStorage.ts | 进入 cache 的内容永不修改 |

### 10.6 文本选择算法

文件：`src/ink/selection.ts`

- anchor + focus 点用屏幕缓冲区坐标（col, row）
- 双击/三击选词/行模式：`anchorSpan` 启用拖拽时按词/行扩展
- 滚动捕获：`scrolledOffAbove`/`scrolledOffBelow` 累加器捕获拖拽滚动时离开视口的行
- 词边界检测匹配 iTerm2 默认行为（路径字符 `/-+\~_.` 视为词字符）
- `getSelectedText()` 合并离屏和在屏行，尊重软换行标记重建逻辑行

### 10.7 鼠标 Hit Testing

文件：`src/ink/hit-test.ts`

递归深度优先遍历 DOM 树。**子节点逆序遍历**（后绘制的在上层），确保正确 z-order。
- `dispatchClick()`：从最深命中节点沿 parentNode 冒泡
- `dispatchHover()`：类 DOM mouseEnter/mouseLeave（非冒泡），diff hovered-node 集合

### 10.8 GrepTool 分页

```
默认限制：250 条（未指定时）
head_limit=0：无限制（谨慎使用）
offset 参数：跳过前 N 条
分页在 ripgrep 返回后、路径相对化之前应用（节省 CPU）
appliedLimit 仅在实际截断时报告（让模型知道有更多结果）
```

### 10.9 Partial Compact 方向性

```
from（默认）：
  摘要 pivot 之后的消息，保留之前的
  → prompt cache 保留（保留的消息在前）

up_to：
  摘要 pivot 之前的消息，保留之后的
  → prompt cache 失效（摘要在保留消息之前）
  → 剥离旧 compact 边界和摘要（防止陈旧边界混淆扫描器）
```

### 10.10 API 消息轮次分组

文件：`src/services/compact/grouping.ts`

```
groupMessagesByApiRound：
  按 API 轮次边界分组（不同 message.id 标记新轮次）
  比之前的 human-turn 分组更细粒度
  → 支持单 human turn 的 SDK/CCR/eval 会话中的精确 compact
  流式 chunk 共享 id → 同一响应内的交错 tool_result 保持正确分组
```
