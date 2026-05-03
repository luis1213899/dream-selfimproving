# 梦境技能系统架构 — 关键上下文

> 本文档澄清 dream-selfimproving 与 Hermes Curator / skill-evolver 的关系，以及 cron 调度系统。
> **最后更新：2026-05-03**

---

## 调度系统：OpenClaw cron ≠ Hermes cron

梦境技能的 cron 跑在 **OpenClaw 平台端**，不是 Hermes 本地 cron。这是两套独立的调度系统：

| | OpenClaw cron | Hermes cron |
|--|--|--|
| 配置位置 | `~/.openclaw/cron/jobs.json` | `~/.hermes/` 或 Hermes Cloud |
| 查看命令 | `curl localhost:3011/api/...` 或直接读 `~/.openclaw/cron/jobs.json` | `hermes cron list` |
| 梦境技能 | ✅ 早间蒸馏、晚间蒸馏在此 | ❌ |
| skill-evolver | ❌ | ✅ 追踪、衰减、缺口检测 |

**判断方法：** 如果 `hermes cron list` 为空但记忆里记录了 cron 任务，配置在 OpenClaw 平台端，不在本地 Hermes。

---

## Cron 任务清单（OpenClaw 端）

| 任务名 | Job ID（前8位） | Cron | 作用 |
|--------|----------------|------|------|
| 梦境技能-早间蒸馏 | `eeb00ae0` | `0 7 * * *` (Asia/Shanghai) | `dream.py` → 飞书汇报 |
| 梦境技能-晚间蒸馏 | `fc30089a` | `0 22 * * *` (Asia/Shanghai) | `dream.py` → 飞书汇报 |
| 每日技能积分榜快照 | `b00b50fc` | `0 23 * * *` (Asia/Shanghai) | `parse_gateway_logs.py` + `score_tracker.py` → 飞书 |
| AI Agent技能评测 | `d89dd954` | `0 */2 * * *` (Asia/Shanghai) | GitHub 搜索 → 微信文章 |

---

## 晚间蒸馏超时问题

**症状：** 晚间蒸馏偶尔报 `model idle timeout`（300秒内模型没完整响应）

```
status: error
error: "The model did not produce a response before the model idle timeout"
durationMs: ~160000  （160秒时模型停止输出）
output_tokens: 65     （只生成了65个token就卡住）
```

**原因：** 模型/网络问题，不是代码问题。`dream.py` 本身执行正常，模型响应在160秒时卡死。

**解法：** OpenClaw cron `fc30089a` 的 `timeoutSeconds` 当前是 300，可考虑调大。但这不是关键任务，偶尔超时影响有限。

---

## 与 Hermes Curator / skill-evolver 的关系

dream-selfimproving 有**自己独立的**技能进化系统（v5.0 内置），不依赖 skill-evolver：

```
dream.py v5.0 内部：
├── skill_evolution  → 自己的评分/衰减引擎
├── work_review      → 工作复盘
├── skill_explorer   → 缺口检测
├── skill_developer  → 全自动技能生成
└── reporter         → 每日汇报

skill-evolver（ Hermes 增强层）：
├── bump_use() hook  → 双通道写入 .usage.json + scores.json
├── quality_tracker.py → 质量分析
└── gap_detector.py  → 缺口检测

Hermes Curator（官方生命周期）：
├── .usage.json      → 官方追踪（use_count/view_count）
├── 30天不用 → stale
└── 90天不用 → archived
```

**三者关系：**
- dream-selfimproving 负责**记忆蒸馏**（每晚复盘对话）
- Hermes Curator 负责**技能生命周期**（stale/archived）
- skill-evolver 负责**技能质量分析**（衰减模拟、缺口检测）

它们各自独立运行，数据共享点在 `bump_use()` 钩子写入 `scores.json`。

---

## 查看 cron 运行记录

```bash
# OpenClaw cron 运行日志
cat ~/.openclaw/cron/runs/<job-id>.jsonl | tail

# Hermes cron 状态
hermes cron list

# OpenClaw cron 作业配置
cat ~/.openclaw/cron/jobs.json | python3 -c "
import json,sys
data=json.load(sys.stdin)
for j in data['jobs']:
    print(j['id'][:8], '|', j['name'])
"
```
