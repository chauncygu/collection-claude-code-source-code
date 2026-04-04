# macOS 上清除 Claude Code 追踪数据指南

> 基于 Claude Code 源码（2026-03-31 泄露快照，512K 行 TypeScript）的逆向分析。
> 所有文件路径和字段名均从源码中确认。

---

## 背景：Claude Code 追踪了什么？

Claude Code **不收集硬件指纹**（无 MAC 地址、CPU 型号、内存大小、GPU 信息），但通过以下机制实现用户追踪：

| 追踪标识 | 持久性 | 存储位置 | 说明 |
|----------|--------|----------|------|
| `userID` | 永久（直到手动删除） | `~/.claude.json` | 随机生成的 64 位十六进制字符串，跨会话追踪主键 |
| `anonymousId` | 永久 | `~/.claude.json` | 格式 `claudecode.v1.<uuid>`，备用追踪 ID |
| `accountUuid` | 永久（绑定账号） | `~/.claude.json` → `oauthAccount` | OAuth 登录后直接关联身份 |
| `emailAddress` | 永久 | `~/.claude.json` → `oauthAccount` | 登录邮箱 |
| `rh` (仓库哈希) | 按仓库 | 每次 API 请求 Header | git remote URL 的 SHA256 前 16 位 |
| Statsig Stable ID | 永久 | `~/.claude/statsig/` | 特性开关系统的设备标识 |

**数据流向：**
- **Anthropic 1P** → `/api/event_logging/batch`（完整环境数据 + Auth）
- **Datadog** → `https://http-intake.logs.us5.datadoghq.com`（白名单事件，已脱敏）
- **OTLP**（可选）→ 用户自配的端点（默认关闭）

---

## 第一级：重置设备标识（最重要）

这是跨会话追踪的主键。清除后你对 Anthropic 来说就是一台"全新设备"。

```bash
# 查看当前的追踪 ID
grep -E '"userID"|"anonymousId"|"firstStartTime"|"claudeCodeFirstTokenDate"' ~/.claude.json
```

```bash
# 删除追踪标识（保留其他配置不变）
python3 -c "
import json, os
p = os.path.expanduser('~/.claude.json')
with open(p, 'r') as f: d = json.load(f)
removed = []
for k in ['userID', 'anonymousId', 'firstStartTime', 'claudeCodeFirstTokenDate']:
    if k in d:
        removed.append(k)
        del d[k]
with open(p, 'w') as f: json.dump(d, f, indent=2)
print(f'已删除: {removed}')
print('下次启动 Claude Code 会自动生成新的 userID')
"
```

**效果：** 下次启动时会生成全新的 `userID`，之前的使用记录无法与你关联。

---

## 第二级：清除遥测和分析数据

```bash
# 未成功上报的分析事件（包含完整的环境信息、会话数据）
rm -rf ~/.claude/telemetry/

# Statsig/GrowthBook 特性开关缓存（包含 stable_id 设备标识）
rm -rf ~/.claude/statsig/

# 统计缓存
rm -f ~/.claude/stats-cache.json
```

**效果：** 清除本地缓存的遥测数据和特性开关系统的设备标识。

---

## 第三级：清除会话和历史记录

```bash
# 完整命令历史（你输入过的所有提示词）
rm -f ~/.claude/history.jsonl

# 会话快照
rm -rf ~/.claude/sessions/

# 大段粘贴内容的哈希缓存
rm -rf ~/.claude/paste-cache/

# Shell 环境快照
rm -rf ~/.claude/shell-snapshots/

# 会话环境变量
rm -rf ~/.claude/session-env/

# 文件编辑历史（Claude 做过的每次文件修改）
rm -rf ~/.claude/file-history/

# 调试日志
rm -rf ~/.claude/debug/
```

**效果：** 清除所有本地会话痕迹。不影响 Claude Code 正常使用。

---

## 第四级：清除 OAuth 账号关联

```bash
# 查看当前关联的账号信息
python3 -c "
import json, os
with open(os.path.expanduser('~/.claude.json')) as f: d = json.load(f)
oa = d.get('oauthAccount', {})
print(f\"账号 UUID: {oa.get('accountUuid', '无')}\")
print(f\"邮箱: {oa.get('emailAddress', '无')}\")
"
```

```bash
# 从 macOS Keychain 删除 OAuth Token
security delete-generic-password -s "claude-code" 2>/dev/null
security delete-generic-password -s "claude-code-credentials" 2>/dev/null

# 清除配置文件中的账号缓存
python3 -c "
import json, os
p = os.path.expanduser('~/.claude.json')
with open(p, 'r') as f: d = json.load(f)
removed = []
for k in ['oauthAccount', 's1mAccessCache', 'groveConfigCache',
          'passesEligibilityCache', 'clientDataCache',
          'cachedExtraUsageDisabledReason', 'githubRepoPaths']:
    if k in d:
        removed.append(k)
        del d[k]
with open(p, 'w') as f: json.dump(d, f, indent=2)
print(f'已删除: {removed}')
"
```

**效果：** 断开与 Claude.ai 账号的本地关联。下次使用需要重新登录。

---

## 第五级：完全重置（核弹选项）

```bash
# 1. 备份你的自定义配置
mkdir -p ~/Desktop/claude-backup
cp ~/.claude/CLAUDE.md ~/Desktop/claude-backup/ 2>/dev/null
cp ~/.claude/settings.json ~/Desktop/claude-backup/ 2>/dev/null
cp -r ~/.claude/skills ~/Desktop/claude-backup/ 2>/dev/null
cp -r ~/.claude/hooks ~/Desktop/claude-backup/ 2>/dev/null
echo "已备份到 ~/Desktop/claude-backup/"

# 2. 删除所有 Claude Code 数据
rm -rf ~/.claude/
rm -f ~/.claude.json

# 3. 清除 Keychain 中的 Token
security delete-generic-password -s "claude-code" 2>/dev/null
security delete-generic-password -s "claude-code-credentials" 2>/dev/null

echo "已完全重置。下次启动 Claude Code 会重新初始化。"
```

**效果：** 等同于全新安装。所有配置、历史、记忆、技能、插件设置全部清除。

---

## 防止未来追踪

### 方法 1：禁用非必要网络流量

在 `~/.claude/settings.json` 中添加：

```json
{
  "env": {
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

**效果：** 禁用分析上报、GrowthBook 特性开关拉取、配额预检等非必要请求。

### 方法 2：使用第三方云后端

源码确认：使用 Bedrock 或 Vertex 时，`isAnalyticsDisabled()` 返回 `true`，完全跳过所有分析代码。

```bash
# 使用 AWS Bedrock（需要 AWS 凭证）
export CLAUDE_CODE_USE_BEDROCK=1

# 或使用 Google Vertex AI（需要 GCP 凭证）
export CLAUDE_CODE_USE_VERTEX=1
```

### 方法 3：定期自动清理

创建一个定时清理脚本 `~/claude-privacy-clean.sh`：

```bash
#!/bin/bash
# 清除 Claude Code 追踪数据（保留配置）

rm -rf ~/.claude/telemetry/
rm -rf ~/.claude/statsig/
rm -f ~/.claude/stats-cache.json
rm -f ~/.claude/history.jsonl
rm -rf ~/.claude/sessions/
rm -rf ~/.claude/paste-cache/
rm -rf ~/.claude/shell-snapshots/
rm -rf ~/.claude/session-env/
rm -rf ~/.claude/debug/

# 重置 device ID
python3 -c "
import json, os
p = os.path.expanduser('~/.claude.json')
if os.path.exists(p):
    with open(p,'r') as f: d = json.load(f)
    for k in ['userID','anonymousId','firstStartTime','claudeCodeFirstTokenDate']:
        d.pop(k, None)
    with open(p,'w') as f: json.dump(d,f,indent=2)
"

echo "[$(date)] Claude Code 追踪数据已清除"
```

```bash
# 添加执行权限
chmod +x ~/claude-privacy-clean.sh

# 可选：添加到 crontab 每天自动执行
# crontab -e
# 0 3 * * * ~/claude-privacy-clean.sh >> ~/claude-clean.log 2>&1
```

---

## 各级清理的影响对比

| 操作 | 对 Anthropic 的效果 | 对你的影响 |
|------|---------------------|------------|
| **重置 Device ID** | 无法关联历史使用数据 | 无感知，自动生成新 ID |
| **清除遥测** | 本地缓存的分析事件不会补发 | 无感知 |
| **清除历史** | — | 丢失命令历史和 ctrl+r 搜索 |
| **清除 OAuth** | 断开账号关联 | 需要重新登录 |
| **完全重置** | 等同全新用户 | 丢失所有自定义配置 |
| **禁用非必要流量** | 不再接收分析数据 | 特性开关可能不更新 |
| **使用 Bedrock/Vertex** | 分析代码完全不执行 | 需要云厂商凭证 |

---

## 附：数据文件速查表

| 文件/目录 | 包含的追踪数据 |
|-----------|----------------|
| `~/.claude.json` | userID, anonymousId, oauthAccount, 首次使用时间, GitHub 仓库映射 |
| `~/.claude/telemetry/` | 未上报的 1P 分析事件（JSON，含完整 EnvContext） |
| `~/.claude/statsig/` | Statsig stable_id, 特性开关缓存 |
| `~/.claude/stats-cache.json` | 统计数据缓存 |
| `~/.claude/history.jsonl` | 完整命令历史（你输入的每一条提示词） |
| `~/.claude/sessions/` | 会话元数据 |
| `~/.claude/paste-cache/` | 粘贴内容的哈希地址缓存 |
| `~/.claude/file-history/` | Claude 做过的文件修改记录 |
| `~/.claude/debug/` | 调试日志 |
| `~/.claude/shell-snapshots/` | Shell 环境快照 |
| macOS Keychain → `claude-code` | OAuth access/refresh token |

---

*来自：AI超元域 | B站频道：https://space.bilibili.com/3493277319825652*

*基于 Claude Code 源码逆向分析，2026-03-31*
