# Claude Code 默认 Effort Level 设置为 Max

## 问题

`/effort max` 命令只对当前会话生效，重启 Claude Code 后会恢复为默认的 `medium`。

## 解决方案

在 `~/.zshrc` 中添加环境变量：

```bash
export CLAUDE_CODE_EFFORT_LEVEL=max
```

新开终端窗口后自动生效。

## 为什么不能用 settings.json

Claude Code 的 `~/.claude/settings.json` 支持 `effortLevel` 字段，但只接受 `low`、`medium`、`high` 三个值。`max` 是 Opus 4.6 专属的深度推理模式，只能通过环境变量持久化。

## Effort Level 一览

| 级别 | 说明 |
|------|------|
| `low` | 快速响应，适合简单问答 |
| `medium` | 默认级别 |
| `high` | 更深入的推理 |
| `max` | 最深度推理，无 token 限制（仅 Opus 4.6） |

## 其他设置方式

- **启动参数**（单次）：`claude --effort max`
- **会话内**（单次）：`/effort max`
- **环境变量**（永久）：`export CLAUDE_CODE_EFFORT_LEVEL=max` ← 推荐

---

*记录于 2026-03-30*
