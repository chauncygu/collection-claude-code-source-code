# Claude Code 隐藏高级功能全景图

> 基于 Claude Code 源码（2026-03-31 快照，512K 行 TypeScript）逆向分析
> 发现 55+ 个特性开关、20+ 个隐藏命令、以及多个未公开系统

---

## 目录

1. [你现在就能用的隐藏功能](#1-你现在就能用的隐藏功能)
2. [55+ 个编译时特性开关完整清单](#2-55-个编译时特性开关完整清单)
3. [KAIROS — AI 助手守护进程](#3-kairos--ai-助手守护进程)
4. [CHICAGO_MCP — Computer Use 电脑控制](#4-chicago_mcp--computer-use-电脑控制)
5. [投机执行系统（Speculation）](#5-投机执行系统speculation)
6. [Undercover 隐身模式](#6-undercover-隐身模式)
7. [Dream Mode 记忆梦境整合](#7-dream-mode-记忆梦境整合)
8. [Voice Mode 语音输入](#8-voice-mode-语音输入)
9. [Proactive 自主代理模式](#9-proactive-自主代理模式)
10. [伴侣精灵系统（Buddy）](#10-伴侣精灵系统buddy)
11. [多代理团队/Swarm 系统](#11-多代理团队swarm-系统)
12. [Anthropic 内部专用命令](#12-anthropic-内部专用命令)
13. [隐藏键盘快捷键](#13-隐藏键盘快捷键)
14. [隐藏环境变量](#14-隐藏环境变量)
15. [其他彩蛋与冷知识](#15-其他彩蛋与冷知识)

---

## 1. 你现在就能用的隐藏功能

这些功能在当前公开版本中存在，但很少被提及：

| 功能 | 触发方式 | 说明 |
|------|----------|------|
| 实体贴纸 | `/stickers` | 打开 Claude Code 实体贴纸购买页 |
| 堆转储 | `/heapdump` | 把 JS 堆转储到 `~/Desktop`（隐藏命令，不在 /help 中） |
| 裸模式 | `--bare` 或 `CLAUDE_CODE_SIMPLE=1` | 极简模式：只保留 Bash、Read、Edit 三个工具 |
| 自定义加载词 | `settings.json` → `spinnerVerbs` | 替换或追加 200+ 个花式加载词（"Clauding"、"Flibbertigibbeting"…） |
| 输出风格切换 | `/config` → output style | **Explanatory**（教学模式，附 Insight 解说）或 **Learning**（动手练习，含 TODO(human) 标记） |
| Vim 模式 | `/vim` | 完整状态机：d/c/y 操作符、h/l/w/b/e/$ 移动、f/t 查找、文本对象、dot-repeat |
| 消息动作选择器 | `shift+up` | 进入消息导航：j/k 上下移动，c 复制消息，p 固定消息 |
| 年度回顾 | `/think-back` | "Your 2025 Claude Code Year in Review" 动画回顾 |
| 转储系统提示 | `--dump-system-prompt` | 打印完整系统提示词后退出（需特性开关） |
| 多代理团队 | `--agent-teams` 或 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | 多 Claude 实例在 tmux/iTerm 分屏中并行工作 |
| 后台任务 | `ctrl+b` | 把当前运行中的任务转入后台 |
| 历史搜索 | `ctrl+r` | 反向搜索命令历史 |
| Transcript 模式 | `ctrl+o` | 查看完整对话记录，支持搜索 |
| Todo 面板 | `ctrl+t` | 任务追踪面板 |
| 速率限制选项 | `/rate-limit-options` | 隐藏命令，速率限制时显示选项 |
| 使用洞察 | `/insights` | 分析你的 Claude Code 使用历史（113KB 延迟加载模块） |
| 全局文件搜索 | `ctrl+shift+f` | 跨文件搜索（需 QUICK_SEARCH 开关） |
| 快速打开 | `ctrl+shift+p` | 快速打开文件 |

---

## 2. 55+ 个编译时特性开关完整清单

所有开关通过 `feature('FLAG')` 在 Bun 编译时评估。外部构建中为 `false` 的分支会被彻底删除（死代码消除）。

### 核心功能开关

| 开关 | 功能 | 状态 |
|------|------|:----:|
| `VOICE_MODE` | 语音输入（push-to-talk） | 内部 |
| `KAIROS` | AI 助手守护进程模式 | 内部 |
| `KAIROS_DREAM` | 梦境记忆整合 | 内部 |
| `KAIROS_BRIEF` | Brief 摘要工具 | 内部 |
| `KAIROS_CHANNELS` | 频道通知系统 | 内部 |
| `KAIROS_PUSH_NOTIFICATION` | 推送通知工具 | 内部 |
| `KAIROS_GITHUB_WEBHOOKS` | GitHub PR 订阅 | 内部 |
| `CHICAGO_MCP` | Computer Use 电脑控制 | 付费用户 |
| `PROACTIVE` | 自主代理模式（Sleep + 自动唤醒） | 内部 |
| `BRIDGE_MODE` | Remote Control 桥接 | 公开 |
| `DAEMON` | 后台守护进程 | 内部 |

### 上下文管理开关

| 开关 | 功能 |
|------|------|
| `CONTEXT_COLLAPSE` | 智能上下文折叠（替代暴力压缩） |
| `REACTIVE_COMPACT` | 响应式压缩（API 报 prompt-too-long 时触发） |
| `CACHED_MICROCOMPACT` | 缓存感知微压缩（不破坏 prompt cache） |
| `HISTORY_SNIP` | 历史裁剪（SnipTool + /force-snip） |
| `TOKEN_BUDGET` | Token 预算追踪和递减收益检测 |
| `EXTRACT_MEMORIES` | 自动记忆提取 |
| `TEAMMEM` | 团队记忆同步 |

### 工具和代理开关

| 开关 | 功能 |
|------|------|
| `COORDINATOR_MODE` | 多代理协调者模式 |
| `AGENT_TRIGGERS` | 定时触发器（Cron） |
| `AGENT_TRIGGERS_REMOTE` | 远程触发器 |
| `MONITOR_TOOL` | 监控工具和任务 |
| `WEB_BROWSER_TOOL` | 网页浏览器自动化工具 |
| `TERMINAL_PANEL` | 终端面板（meta+j） |
| `WORKFLOW_SCRIPTS` | 工作流脚本系统 |
| `BG_SESSIONS` | 后台会话（claude ps/logs/attach/kill） |
| `OVERFLOW_TEST_TOOL` | 上下文溢出测试工具 |
| `BUDDY` | 伴侣精灵系统 |

### UI 和体验开关

| 开关 | 功能 |
|------|------|
| `MESSAGE_ACTIONS` | 消息动作选择器（shift+up） |
| `QUICK_SEARCH` | 全局搜索和快速打开 |
| `AUTO_THEME` | 自动主题检测 |
| `STREAMLINED_OUTPUT` | 流式 JSON 模式优化输出 |
| `CONNECTOR_TEXT` | 连接器文本摘要 beta |

### 安全和调试开关

| 开关 | 功能 |
|------|------|
| `BASH_CLASSIFIER` | Bash 命令 ML 安全分类器 |
| `TRANSCRIPT_CLASSIFIER` | 基于 transcript 的权限模式分类 |
| `NATIVE_CLIENT_ATTESTATION` | 客户端证明头（cch=） |
| `HARD_FAIL` | 硬失败模式（任何错误都崩溃） |
| `DUMP_SYSTEM_PROMPT` | --dump-system-prompt 隐藏 CLI 标志 |
| `ABLATION_BASELINE` | A/B 测试消融基线 |
| `PROMPT_CACHE_BREAK_DETECTION` | Prompt 缓存失效检测 |

### 基础设施开关

| 开关 | 功能 |
|------|------|
| `LODESTONE` | `cc://` 深度链接协议注册 |
| `DIRECT_CONNECT` | 通过 cc:// 深度链接直连 |
| `SSH_REMOTE` | SSH 远程会话 |
| `BYOC_ENVIRONMENT_RUNNER` | 自带计算环境运行器 |
| `SELF_HOSTED_RUNNER` | 自托管运行器 |
| `CCR_REMOTE_SETUP` | /remote-setup 命令 |
| `FORK_SUBAGENT` | /fork 子代理分叉命令 |
| `MCP_SKILLS` | MCP 提供的技能 |
| `EXPERIMENTAL_SKILL_SEARCH` | 实验性技能模糊搜索 |
| `REVIEW_ARTIFACT` | 审查工件工具 |
| `BUILDING_CLAUDE_APPS` | /claude-api 技能 |
| `RUN_SKILL_GENERATOR` | 技能生成器 |
| `ULTRAPLAN` | 超级计划模式 |
| `TORCH` | /torch 命令 |
| `TEMPLATES` | 任务分类器/模板系统 |
| `VERIFICATION_AGENT` | 验证代理 |
| `COMMIT_ATTRIBUTION` | 提交归属（Co-Authored-By） |
| `AWAY_SUMMARY` | 离开摘要生成 |
| `FILE_PERSISTENCE` | 跨轮次文件持久化追踪 |
| `MEMORY_SHAPE_TELEMETRY` | 记忆文件形状遥测 |
| `COWORKER_TYPE_TELEMETRY` | Coworker 类型遥测 |
| `DOWNLOAD_USER_SETTINGS` | 设置下载同步 |
| `UPLOAD_USER_SETTINGS` | 设置上传同步 |
| `BREAK_CACHE_COMMAND` | /break-cache 命令 |

---

## 3. KAIROS — AI 助手守护进程

**代号含义：** KAIROS（希腊语，"决定性时刻"）

### 架构

```
claude assistant                    ← 启动入口
  ↓
永驻守护进程
  ├── 每日日志: logs/YYYY/MM/YYYY-MM-DD.md（仅追加）
  ├── SleepTool: 休眠 → 定时自主唤醒
  ├── PushNotificationTool: 向用户推送通知
  ├── SendUserFileTool: 发送文件给用户
  ├── SubscribePRTool: 订阅 GitHub PR webhook
  ├── BriefTool: 简短状态报告（ctrl+shift+b）
  ├── 频道通知: 通过 MCP 接收外部消息
  └── /dream: 夜间记忆蒸馏
```

### 关键特性

- **记忆范式不同**：不写独立记忆文件，而是追加到每日日志
- **夜间梦境**：`/dream` 技能自动将日志蒸馏为主题文件
- **自主循环**：SleepTool + 自动唤醒 = 完全自主的工作循环
- **压缩后行为**：提示词包含 "你正在自主模式中运行，这不是首次唤醒——继续工作循环"
- **涉及 6 个子特性开关**：KAIROS + KAIROS_DREAM + KAIROS_BRIEF + KAIROS_CHANNELS + KAIROS_PUSH_NOTIFICATION + KAIROS_GITHUB_WEBHOOKS

---

## 4. CHICAGO_MCP — Computer Use 电脑控制

**代号：** Chicago（子门控以芝加哥地标命名：`tengu_malort_pedway`）

### 功能

- 创建**进程内 MCP 服务器**控制屏幕
- macOS 上使用**原生 Swift 执行器**
- 支持 `pixels` 和 `normalized` 两种坐标模式
- 自动列出已安装应用供模型参考
- **ESC 热键**紧急中断电脑控制
- 可通过 `--computer-use-mcp` 独立启动 MCP 服务器

### 子功能门控

| 子门控 | 功能 |
|--------|------|
| `pixelValidation` | 像素坐标验证 |
| `clipboardPasteMultiline` | 多行剪贴板粘贴 |
| `mouseAnimation` | 鼠标移动动画 |
| `hideBeforeAction` | 操作前隐藏 UI |
| `autoTargetDisplay` | 自动目标显示器选择 |
| `clipboardGuard` | 剪贴板保护 |

### 访问控制

- 需要 **Max 或 Pro 订阅**（外部用户）
- Anthropic 员工可直接使用（绕过订阅检查）
- 有专用权限 UI（`ComputerUseApproval.tsx`）

---

## 5. 投机执行系统（Speculation）

**仅 Anthropic 内部**（`USER_TYPE === 'ant'`）

### 工作原理

```
1. 系统生成"下一步建议"提示词
   ↓
2. 用户看到建议的同时，后台 Fork Agent 已开始执行
   ↓
3. 文件写入到 overlay 目录（copy-on-write 隔离）
   ~/.claude/tmp/speculation/<pid>/<id>/
   ↓
4. 用户接受建议 → 投机结果注入对话 + overlay 文件复制到真实文件系统
   用户拒绝/修改 → 丢弃投机结果
```

### 安全约束

| 工具类型 | 投机执行中的权限 |
|----------|:----------------:|
| 只读工具（Read, Glob, Grep） | 允许 |
| 写入工具（Edit, Write） | 仅在权限模式允许自动接受时 |
| Bash 命令 | 必须通过只读验证 |
| 未知工具 | 遇到即暂停（boundary） |

### 限制

- 最多 **20 轮**、**100 条消息**
- 可以**流水线化**：当前投机完成后预生成下一步建议

### 用户反馈（内部可见）

```
Speculated 5 tool uses — +12s saved (47s this session)
```

---

## 6. Undercover 隐身模式

**仅 Anthropic 员工**，自动激活条件：在公开/开源仓库工作。

### 激活后的行为

| 行为 | 说明 |
|------|------|
| 剥除归属 | 所有 `Co-Authored-By` 行被移除 |
| 禁止提及内部代号 | Capybara、Tengu 等动物代号 |
| 禁止提及版本号 | 未发布的模型版本 |
| 禁止提及内部仓库 | Anthropic 内部仓库名 |
| 禁止提及 Slack 频道 | 内部 Slack 频道名 |
| 禁止提及 "Claude Code" | commit 消息必须看起来像人类写的 |

### 控制

- 自动检测：仓库 remote 不在内部白名单 → 自动开启
- 强制开启：`CLAUDE_CODE_UNDERCOVER=1`
- 无强制关闭选项
- 首次激活有说明对话框

---

## 7. Dream Mode 记忆梦境整合

### 自动触发条件

同时满足：
- 距上次整合 ≥ **24 小时**（`minHours`，可配置）
- 且触及 ≥ **5 个会话**（`minSessions`，可配置）
- 无其他进程正在整合（锁机制）

### 四阶段执行

```
阶段 1 — 定向
  读取记忆目录和 MEMORY.md 索引

阶段 2 — 收集
  从每日日志和会话 transcript 中提取新信号

阶段 3 — 整合
  将新信息合并到已有主题文件
  转换相对日期为绝对日期
  删除被新事实矛盾的旧事实

阶段 4 — 修剪
  保持索引在 25KB 以内
  清理过时条目
```

### 工具限制

Dream 运行期间，Bash 被限制为只读命令。

### 手动触发

`/dream` 技能在前台执行同样的整合流程（需 KAIROS 或 KAIROS_DREAM 开关）。

---

## 8. Voice Mode 语音输入

### 激活方式

**按住空格键说话**（push-to-talk），通过 `/voice` 命令开启。

### 技术栈

```
原生音频捕获
  macOS → CoreAudio (audio-capture-napi / cpal)
  Linux → ALSA
  回退 → SoX rec / arecord

录音参数
  采样率: 16kHz
  声道: 单声道
  静音检测: 2.0秒，3% 阈值（SoX 回退路径）

STT 流式传输
  → claude.ai voice_stream 端点
  → 需要 Anthropic OAuth（API key/Bedrock/Vertex 不支持）
```

### UI 元素

- 音频电平指示器
- 语音状态显示
- 语言选择器（`LanguagePicker.tsx`）
- 自定义关键词词汇表（`voiceKeyterms.ts`）

### 控制

- GrowthBook 杀开关：`tengu_amber_quartz_disabled`
- 默认 fail-open（新安装时启用）

---

## 9. Proactive 自主代理模式

### 核心工具：SleepTool

```typescript
// 代理可以休眠指定时间后自主唤醒
SleepTool.call({ duration: '5m' })
// 5 分钟后自动恢复执行
```

### 与 KAIROS 结合

```
claude assistant
  ↓
[工作] → [SleepTool 5m] → [自动唤醒] → [继续工作] → [SleepTool 10m] → ...
  ↑                                                                      |
  └──────────────────────────── 无限循环 ────────────────────────────────┘
```

### 压缩后的特殊行为

普通模式压缩后：提示用户是否有问题

自主模式压缩后：
```
你正在自主/主动模式中运行。这不是首次唤醒——你在压缩前已经在自主工作。
继续你的工作循环：根据上面的摘要从离开的地方接续。不要问候用户或询问要做什么。
```

---

## 10. 伴侣精灵系统（Buddy）

`feature('BUDDY')` — 一个完整的收藏型宠物系统。

### 物种（18种）

duck、goose、blob、cat、dragon、octopus、owl、penguin、turtle、snail、ghost、axolotl、capybara、cactus、robot、rabbit、mushroom、chonk

### 外观组合

```
18 种物种 × 6 种眼睛 × 8 种帽子 = 864 种外观组合
× 5 种稀有度 = 4,320 种可能的精灵
```

### 稀有度

| 等级 | 概率 | 显示 | 属性底值 |
|------|:----:|------|:--------:|
| Common | 60% | 1星 | 低 |
| Uncommon | 25% | 2星 | 略高 |
| Rare | 10% | 3星 | 中等 |
| Epic | 4% | 4星 | 高 |
| Legendary | 1% | 5星 | 最高 |

### 5种属性

- **DEBUGGING** — 调试力
- **PATIENCE** — 耐心
- **CHAOS** — 混沌
- **WISDOM** — 智慧
- **SNARK** — 吐槽力

每只精灵有一个巅峰属性和一个低谷属性。

### 确定性生成

```typescript
// 种子 = hash(userId + 'friend-2026-401')
// PRNG = Mulberry32
// 无论何时重新生成，同一用户始终得到同一只精灵
// 编辑配置文件无法伪造稀有度——bones 从 hash 重新计算
```

### ASCII 动画

```
每种物种 3 帧动画，5行×12字符
500ms tick 的闲置动画
包含眨眼帧和特殊效果（烟雾、天线发光、墨水泡泡等）
```

### 互动

```
/buddy pet → 触发 2.5 秒心形粒子特效（❤ 字符向上飘浮）
模型可以让精灵"说话"（通过 speech bubble 系统）
用户对精灵说话时，模型会自动退让
```

### 反作弊

```
物种名中某些与模型代号冲突的名称用 String.fromCharCode 十六进制编码
配置文件编辑不影响生成结果（bones 从 hash 重算）
```

### 启动引导

首次未孵化时显示彩虹色 `/buddy` 提示文本。

---

## 11. 多代理团队/Swarm 系统

### 激活方式

```bash
# 外部用户
claude --agent-teams
# 或
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

### 三种后端

| 后端 | 实现 | 特点 |
|------|------|------|
| **TmuxBackend** | 隔离 tmux socket `claude-swarm-<PID>` | 彩色边框，不影响用户的 tmux |
| **ITermBackend** | iTerm2 的 `it2` CLI + Python API | 原生分屏 |
| **InProcessBackend** | 进程内运行 | 无终端 UI |

自动检测选择最佳可用后端。

### Tmux 隔离

```typescript
// Claude 创建自己的 tmux socket，防止命令影响用户会话
const SWARM_SESSION_NAME = 'claude-swarm'
const HIDDEN_SESSION_NAME = 'claude-hidden'
// socket 名: claude-<PID>
```

### Coordinator 模式

```bash
export CLAUDE_CODE_COORDINATOR_MODE=1
```

Claude 变为协调者，通过 `AgentTool`、`SendMessageTool`、`TaskStopTool` 编排 worker 代理。Worker 拥有独立工具访问权限。

### 团队工具

| 工具 | 功能 |
|------|------|
| `TeamCreateTool` | 创建代理团队 |
| `TeamDeleteTool` | 删除代理团队 |
| `SendMessageTool` | 代理间消息传递 |
| `TaskStopTool` | 停止子任务 |
| `TungstenTool`（内部） | tmux 会话管理 |

### 共享便签本

当 `tengu_scratch` 门控开启时，worker 获得共享 scratchpad 目录，跨 worker 知识交换绕过权限提示。

---

## 12. Anthropic 内部专用命令（20+个）

全部在外部构建中被替换为 `{ isEnabled: false, isHidden: true }` 存根。

### 调试和诊断

| 命令 | 用途 |
|------|------|
| `/bridge-kick` | 注入 bridge 故障（close/poll/register/heartbeat 等 10+ 子命令） |
| `/mock-limits` | 模拟各种速率限制场景 |
| `/reset-limits` | 重置速率限制状态 |
| `/ctx-viz` | 上下文窗口可视化 |
| `/debug-tool-call` | 工具调用调试 |
| `/ant-trace` | Anthropic 内部追踪 |
| `/perf-issue` | 性能问题报告 |
| `/env` | 显示环境变量 |
| `/stuck` | 诊断冻结/慢会话（扫描 CPU、进程状态、内存泄漏） |
| `/force-snip` | 强制历史裁剪 |
| `/break-cache` | 使 prompt cache 失效 |

### 工作流和自动化

| 命令 | 用途 |
|------|------|
| `/autofix-pr` | 自动修复 PR 问题 |
| `/bughunter` | 远程审查的 bug 猎人模式 |
| `/teleport` | 远程传送到其他环境 |
| `/backfill-sessions` | 回填会话数据 |
| `/agents-platform` | 代理平台管理 |
| `/ultraplan` | 超级计划模式 |
| `/share` | 分享对话 |

### 开发辅助

| 命令 | 用途 |
|------|------|
| `/lorem-ipsum` | 精确 token 计数的填充文本生成（用 1-token 词汇实现精确计数） |
| `/oauth-refresh` | OAuth token 手动刷新 |
| `/good-claude` | （已存根化） |
| `/onboarding` | 引导流程 |
| `/init-verifiers` | 初始化验证器 |

### 内部专用工具

| 工具 | 用途 |
|------|------|
| `ConfigTool` | 直接修改配置 |
| `TungstenTool` | tmux 会话管理 |
| `REPLTool` | 沙盒 REPL VM |
| `SuggestBackgroundPRTool` | 建议后台 PR |
| `CtxInspectTool` | 上下文检查 |
| `OverflowTestTool` | 溢出测试 |
| `SnipTool` | 历史裁剪 |
| `MonitorTool` | 监控 |

### Bridge Kick 详细子命令

```
/bridge-kick close <code>           — 触发 WebSocket close
/bridge-kick poll 404 [type]        — 下次轮询 404
/bridge-kick poll transient         — 下次轮询 5xx
/bridge-kick register fail [N]      — 下 N 次注册失败
/bridge-kick register fatal         — 注册 403（终端失败）
/bridge-kick reconnect-session fail — 重连失败
/bridge-kick heartbeat <status>     — 心跳致命错误
/bridge-kick reconnect              — 直接触发重连
/bridge-kick status                 — 打印 bridge 状态
```

支持**组合故障序列**，复现真实生产故障链。

---

## 13. 隐藏键盘快捷键

### 全局快捷键

| 快捷键 | 动作 |
|--------|------|
| `ctrl+t` | 切换 Todo 面板 |
| `ctrl+o` | 切换 Transcript 查看器 |
| `ctrl+r` | 历史反向搜索 |
| `ctrl+l` | 重绘屏幕 |
| `ctrl+b` | 后台运行当前任务 |
| `shift+tab` | 循环切换权限模式 |
| `meta+p` | 模型选择器 |
| `meta+o` | Fast Mode 切换 |
| `meta+t` | Thinking 模式切换 |

### Chord 快捷键（两步组合）

| 快捷键 | 动作 |
|--------|------|
| `ctrl+x ctrl+k` | 终止所有代理 |
| `ctrl+x ctrl+e` 或 `ctrl+g` | 打开外部编辑器 |

### 编辑快捷键

| 快捷键 | 动作 |
|--------|------|
| `ctrl+_` / `ctrl+shift+-` | 撤销文本输入 |
| `ctrl+s` | 暂存当前输入 |
| `ctrl+v` / `alt+v`(Win) | 粘贴图片 |

### 特性门控快捷键

| 快捷键 | 动作 | 需要 |
|--------|------|------|
| `shift+up` | 消息动作选择器 | `MESSAGE_ACTIONS` |
| `ctrl+shift+f` / `cmd+shift+f` | 全局文件搜索 | `QUICK_SEARCH` |
| `ctrl+shift+p` / `cmd+shift+p` | 快速打开 | `QUICK_SEARCH` |
| `meta+j` | 终端面板 | `TERMINAL_PANEL` |
| `ctrl+shift+b` | Brief 模式切换 | `KAIROS` |
| `ctrl+shift+o` | 队友预览切换 | 团队模式 |
| `space`（按住） | Push-to-talk 语音 | `VOICE_MODE` |

### 滚动快捷键

| 快捷键 | 动作 |
|--------|------|
| `pageup` / `pagedown` | 翻页滚动 |
| `wheelup` / `wheeldown` | 鼠标滚轮滚动 |
| `ctrl+shift+c` / `cmd+c` | 复制选中内容（滚动模式中） |

### 保留快捷键（不可重绑定）

- `ctrl+c` — 中断
- `ctrl+d` — 退出

---

## 14. 隐藏环境变量

### 核心配置

| 变量 | 效果 |
|------|------|
| `CLAUDE_CODE_SIMPLE=1` | 极简模式（3个工具） |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | 禁用自动记忆提取 |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` | 禁用所有非必要网络流量 |
| `CLAUDE_CODE_DISABLE_THINKING=1` | 禁用 thinking 模式 |
| `CLAUDE_CODE_DISABLE_FAST_MODE=1` | 禁用 fast mode |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` | 禁用 CLAUDE.md 加载 |
| `CLAUDE_CODE_DISABLE_COMMAND_INJECTION_CHECK=1` | 禁用命令注入检查 |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` | 禁用后台任务 |

### 性能调优

| 变量 | 效果 |
|------|------|
| `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY=N` | 最大并发工具数（默认10） |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW=N` | 覆盖自动压缩窗口 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS=N` | 覆盖最大输出 token |
| `CLAUDE_CODE_MAX_RETRIES=N` | 覆盖最大重试次数 |
| `CLAUDE_CODE_BLOCKING_LIMIT_OVERRIDE=N` | 覆盖阻塞限制 |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80` | 在 80% 上下文时触发压缩 |

### API 控制

| 变量 | 效果 |
|------|------|
| `ANTHROPIC_MODEL=model-id` | 覆盖默认模型 |
| `ANTHROPIC_SMALL_FAST_MODEL=model-id` | 覆盖后台辅助任务模型 |
| `ANTHROPIC_BASE_URL=url` | 自定义 API 基础 URL |
| `ANTHROPIC_CUSTOM_HEADERS='{"k":"v"}'` | 注入自定义 HTTP 头 |
| `CLAUDE_CODE_EXTRA_BODY='{"k":"v"}'` | 注入额外 API 请求体 |
| `CLAUDE_CODE_EXTRA_METADATA='{"k":"v"}'` | 注入额外元数据 |
| `CLAUDE_CODE_USE_BEDROCK=1` | 使用 AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX=1` | 使用 Google Vertex |
| `CLAUDE_CODE_USE_FOUNDRY=1` | 使用 Azure Foundry |
| `CLAUDE_CODE_UNATTENDED_RETRY=1` | 无人值守无限重试 |

### 调试

| 变量 | 效果 |
|------|------|
| `CLAUDE_CODE_DEBUG=1` | 启用调试日志 |
| `CLAUDE_CODE_FRAME_TIMING_LOG=/path` | 记录帧渲染时间 |
| `CLAUDE_CODE_BASH_SANDBOX_SHOW_INDICATOR=1` | 显示沙盒指示器 |
| `CLAUDE_CODE_SYNTAX_HIGHLIGHT=1` | 启用语法高亮 |
| `OTEL_LOG_TOOL_DETAILS=1` | 遥测中记录工具详情 |
| `OTEL_LOG_USER_PROMPTS=1` | 遥测中记录用户提示词（默认 REDACTED） |
| `DISABLE_COMPACT=1` | 完全禁用压缩 |
| `DISABLE_AUTO_COMPACT=1` | 仅禁用自动压缩 |

### 代理团队

| 变量 | 效果 |
|------|------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | 启用多代理团队 |
| `CLAUDE_CODE_COORDINATOR_MODE=1` | 协调者模式 |
| `CLAUDE_CODE_TEAMMATE_COMMAND=cmd` | 队友启动命令 |
| `CLAUDE_CODE_AGENT_COLOR=color` | 代理颜色 |
| `CLAUDE_CODE_PLAN_MODE_REQUIRED=1` | 强制 plan 模式 |

---

## 15. 其他彩蛋与冷知识

### 200+ 花式加载词

`spinnerVerbs.ts` 中的精选：

```
Clauding, Boondoggling, Canoodling, Flibbertigibbeting,
Hullaballooing, Moonwalking, Prestidigitating, Razzmatazzing,
Shenaniganing, Tomfoolering, Whatchamacalliting, Beboppin'
```

完成时的过去式：
```
Baked for 5s, Cogitated for 12s, Noodled for 8s
```

### VCR 录制/回放模式

`FORCE_VCR=1`（内部）：录制和回放 API 交互，用于测试。

### Lorem Ipsum 精确 token 生成

`/lorem-ipsum 50000`（内部）：使用经过验证的 1-token 单词生成精确 token 数的填充文本。

### Fennec 代号

内部模型迁移中有 `migrateFennecToOpus.ts`：将 `fennec-latest` 映射到 `opus`，`fennec-fast-latest` 映射到 `opus[1m]` + fast mode。

### 消融基线模式

`CLAUDE_CODE_ABLATION_BASELINE`：降级功能用于 A/B 测试，验证各功能的实际贡献。

### 深度链接协议

`feature('LODESTONE')`：注册 `cc://` URL 协议处理器，其他应用可直接打开 Claude Code 会话。

### 物种名编码

```typescript
// 伴侣精灵的某个物种名与内部模型代号冲突
// 用 String.fromCharCode 十六进制编码避免 excluded-strings 检查
```

### 权限模式循环

`shift+tab` 在以下模式间循环：
```
default → acceptEdits → plan → auto → default → ...
```

### Anthropic API Key 自检回避

```typescript
// 秘密扫描器中 Anthropic API key 前缀在运行时拼接
// 避免匹配自身源码的 excluded-strings 检查
const prefix = ['sk', 'ant', 'api'].join('-')
```

---

## 总结：冰山模型

```
                    ╭───────────────╮
         公开版本   │  CLI + 43工具  │  ← 你看到的
                    │  /命令 + UI   │
                    ╰───────┬───────╯
                            │
            ╭───────────────┼───────────────╮
  编译时剥离 │  KAIROS守护进程 │ Computer Use  │  ← 源码中存在
            │  Voice Mode   │ Speculation   │     但外部构建被删除
            │  Dream Mode   │ Undercover    │
            │  Buddy Pet    │ Swarm/Teams   │
            │  Workflows    │ BG Sessions   │
            │  Deep Links   │ Cron Triggers │
            ╰───────────────┴───────────────╯
                            │
            ╭───────────────┼───────────────╮
  内部专用   │ 20+ 调试命令   │ bridge-kick   │  ← 仅 Anthropic 员工
            │ mock-limits   │ VCR 录放      │
            │ lorem-ipsum   │ 消融基线      │
            │ stuck 诊断    │ ctx-viz       │
            ╰───────────────┴───────────────╯
```

**Claude Code 不只是一个 CLI 工具——它的源码中隐藏着一个完整的 AI 助手操作系统的雏形。** 守护进程、语音输入、电脑控制、投机执行、梦境记忆整合、多代理协作、隐身模式——当前公开版本只暴露了冰山一角。

---

*来自：AI超元域 | B站频道：https://space.bilibili.com/3493277319825652*

*基于 Claude Code 源码逆向分析，2026-03-31*
