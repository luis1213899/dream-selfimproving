# 🌙 Dream Self-improving

> **让 AI 每晚进化一次，越用越聪明，用进废退自主进化**

AI 夜间记忆蒸馏与自我进化技能。基于 OpenClaw / Hermes Agent 环境运行，每天自动复盘对话、提取洞察、更新记忆，并根据使用情况自动学习新技能、淘汰低频技能。

[![ClawHub](https://img.shields.io/badge/ClawHub-dream--selfimproving-blue?style=flat-square)](https://clawhub.dev/skills/dream-selfimproving)
[![Version](https://img.shields.io/badge/version-5.0.1-green?style=flat-square)](#)

---

## ✨ 核心能力

### 🧠 夜间记忆蒸馏

每天早 7 点、晚 10 点自动执行：
- 实时监听对话，提取高价值记忆条目
- M-FLOW 四层知识图谱构建（Entity → FacetPoint → Facet → Episode）
- Bundle Search 语义检索 + Long-Term RAG 长记忆层
- AI Auditor 自动检测"AI 味"内容，保持记忆真实性

### 🛠️ 技能用进废退（v5.0 新增）

| 等级 | 标识 | 分值 | 说明 |
|------|------|------|------|
| 高度活跃 | 🔥 | ≥80 | 调用频繁，持续进化 |
| 正常 | 📈 | 60-79 | 稳定使用 |
| 低活跃 | 💤 | 40-59 | 使用较少，建议复习 |
| 休眠 | 🗄️ | 20-39 | 长期未用，待激活 |
| 已归档 | ⚰️ | <20 | 彻底停用 |

**评分公式**：`活跃度 = 调用次数 × 质量系数 × 时间衰减`

### 📊 完整每日汇报（v5.0 新增）

每天自动生成六大模块汇报：
1. **📝 今日总结** — 工作完成情况、未完成原因、阻碍因素
2. **📋 明日计划** — 继续任务、新任务、技能开发计划
3. **🛠️ 技能开发** — 新技能生成、技能改进
4. **📈 技能评分** — Top 10 活跃度排行
5. **🎯 精进点** — 学到的新东西、改进方向
6. **💭 个人感想** — AI 自我反思

---

## 📁 目录结构

```
dream-selfimproving/
├── SKILL.md                     # 技能完整文档
├── _meta.json                   # ClawHub 元数据
├── extensions/                  # v5.0 扩展模块
│   ├── skill_evolution/         # 技能评分 + 用进废退
│   │   ├── scorer.py            # 技能评分器
│   │   ├── decay.py            # 用进废退引擎
│   │   └── registry.py         # 技能注册表
│   ├── work_review/            # 工作复盘
│   │   ├── analyzer.py         # 工作分析器
│   │   └── planner.py         # 明日计划生成器
│   ├── skill_explorer/         # 技能探索
│   │   ├── gap_detector.py     # 缺口检测器
│   │   └── learner.py          # 技能学习器
│   ├── skill_developer/        # 技能开发
│   │   ├── generator.py        # 技能生成器
│   │   ├── quality.py          # 质量评估器
│   │   └── templates.py        # 技能模板库
│   └── reporter/               # 每日汇报
│       ├── daily_report.py     # 日报生成器
│       └── skill_report.py     # 技能报告
├── scripts/
│   ├── dream.py                # 主蒸馏脚本（v5.0）
│   ├── longterm_rag.py         # 长记忆 RAG 管理
│   ├── bundle-search.py        # Bundle Search 实现
│   ├── graph-builder.py        # M-FLOW 图构建
│   └── update-cron-date.py     # Cron 日期更新
├── references/                 # 参考文档
│   ├── skill-evolution-v50.md  # v5.0 设计文档
│   └── ...
└── analyze.py, debug_*.py      # 调试工具
```

---

## 🚀 快速开始

### 安装

```bash
# 通过 ClawHub 安装
clawhub install dream-selfimproving

# 或通过 OpenClaw CLI
openclaw skills install dream-selfimproving
```

### 配置 Cron 任务

```bash
# 早 7 点蒸馏
openclaw cron add "0 7 * * *" "dream" --agent <your-agent-id>

# 晚 10 点蒸馏
openclaw cron add "0 22 * * *" "dream" --agent <your-agent-id>
```

### 手动触发

```bash
cd ~/.hermes/skills/openclaw-imports/dream-selfimproving
python3 scripts/dream.py
```

---

## 📖 详细文档

- [SKILL.md](SKILL.md) — 完整技能文档（部署、配置、故障排查）
- [references/skill-evolution-v50.md](references/skill-evolution-v50.md) — v5.0 用进废退设计详解

---

## 🏗️ 架构设计

### M-FLOW 知识图谱

```
倒锥结构：
锥尖(L3) FacetPoint — 精准锚点
    ↓ 语义边传播
锥底(L1) Episode   — 返回完整记忆
```

### v5.0 技能进化流程

```
每日蒸馏 → 工作复盘 → 技能评分 → 用进废退 → 缺口检测 → 技能开发 → 汇报生成
    ↓           ↓           ↓           ↓           ↓           ↓         ↓
 洞察提取   完成分析    活跃度排名   状态变化    新技能需求   AI全自动生成   六大模块
```

---

## 📌 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 5.0.1 | 2026-05-03 | 更新描述，体现用进废退能力 |
| 5.0.0 | 2026-05-03 | v5.0 技能进化插件：用进废退 + 全自动技能开发 + 完整每日汇报 |
| 4.2.1 | 2026-04-30 | 上一稳定版本 |

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT-0 — Free to use, modify, and redistribute. No attribution required.
