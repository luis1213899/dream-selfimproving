# 🌙 Dream Self-improving

> **让 AI 每晚进化一次，越用越聪明，用进废退自主进化**

AI 夜间记忆蒸馏与自我进化技能。基于 OpenClaw / Hermes Agent 环境运行，每天自动复盘对话、提取洞察、更新记忆，并根据使用情况自动学习新技能、淘汰低频技能。

[![ClawHub](https://img.shields.io/badge/ClawHub-dream--selfimproving-blue?style=flat-square)](https://clawhub.dev/skills/dream-selfimproving)
[![Version](https://img.shields.io/badge/version-5.1.0-green?style=flat-square)](#)

---

## ✨ 核心能力

### 🧠 夜间记忆蒸馏

每天早 7 点、晚 10 点自动执行：
- 实时监听对话，提取高价值记忆条目
- M-FLOW 四层知识图谱构建（Entity → FacetPoint → Facet → Episode）
- Bundle Search 语义检索 + Long-Term RAG 长记忆层
- AI Auditor 自动检测"AI 味"内容，保持记忆真实性

### 🛠️ 技能用进废退（v5.0 新增，v5.1 增强）

| 等级 | 标识 | 分值 | 说明 |
|------|------|------|------|
| 高度活跃 | 🔥 | ≥80 | 调用频繁，持续进化 |
| 正常 | 📈 | 60-79 | 稳定使用 |
| 低活跃 | 💤 | 40-59 | 使用较少，建议复习 |
| 休眠 | 🗄️ | 20-39 | 长期未用，待激活 |
| 已归档 | ⚰️ | <20 | 彻底停用 |

**评分公式**：`活跃度 = 调用次数 × 质量系数 × 时间衰减`

**v5.1 增强**：与 skill-evolver 共用 `~/.skill_scoreboard/scores.json` 数据源，缺口检测与技能生成无缝衔接。

### 🤖 自主技能生成（v5.1 新增）

GapDetector v2.0 内置 11 种能力模板，自动检测缺口后直接生成完整 SKILL.md 草稿：

| 能力类型 | 触发场景 |
|----------|----------|
| deep-researcher | 搜索论文、深度调研、竞品分析 |
| image-generator | AI 绘图、封面设计、插画生成 |
| web-scraper | 网页内容抓取、数据采集 |
| shell-automation | 批量处理、定时任务、系统管理 |
| git-assistant | 代码管理、分支操作、冲突解决 |
| feishu-integration | 飞书消息、文档、知识库 |
| video-generator | 视频生成、字幕处理 |
| doc-summarizer | 长文档摘要、要点提取 |
| data-analyst | 数据分析、可视化、报表生成 |
| ppt-generator | PPT 制作、幻灯片生成 |
| translator | 多语言翻译、本地化 |

生成的草稿写入 `~/SharedSkills/{skill_name}/SKILL.md`，可立即被 OpenClaw / Hermes 发现和触发。

### 📊 完整每日汇报（v5.0 新增）

每天自动生成六大模块汇报：
1. **📝 今日总结** — 工作完成情况、未完成原因、阻碍因素
2. **📋 明日计划** — 继续任务、新任务、技能开发计划
3. **🛠️ 技能开发** — 新技能生成（SKILL.md 草稿）、技能改进
4. **📈 技能评分** — Top 10 活跃度排行
5. **🎯 精进点** — 学到的新东西、改进方向
6. **💭 个人感想** — AI 自我反思

---

## 📁 目录结构

```
dream-selfimproving/
├── SKILL.md                     # 技能完整文档
├── _meta.json                   # ClawHub 元数据
├── README.md                    # 本文档
├── extensions/                  # v5.0+ 扩展模块
│   ├── skill_evolution/         # 技能评分 + 用进废退
│   │   ├── scorer.py            # 技能评分器
│   │   ├── decay.py            # 用进废退引擎
│   │   └── registry.py         # 技能注册表
│   ├── work_review/            # 工作复盘
│   │   ├── analyzer.py         # 工作分析器
│   │   └── planner.py         # 明日计划生成器
│   ├── skill_explorer/         # 技能探索（v5.1 大幅增强）
│   │   ├── gap_detector.py     # 缺口检测器 v2.0（含 SKILL.md 草稿生成）
│   │   └── learner.py          # 技能学习器
│   ├── skill_developer/        # 技能开发
│   │   ├── generator.py        # 技能生成器
│   │   ├── quality.py          # 质量评估器
│   │   └── templates.py        # 技能模板库
│   └── reporter/               # 每日汇报
│       ├── daily_report.py     # 日报生成器
│       └── skill_report.py     # 技能报告
├── scripts/
│   ├── dream.py                # 主蒸馏脚本（v5.1）
│   ├── longterm_rag.py         # 长记忆 RAG 管理
│   └── update-cron-date.py     # Cron 日期更新
└── references/                 # 参考文档
    ├── skill-evolution-v50.md  # v5.0 设计文档
    ├── extension-modules-analysis.md
    ├── minimax-api-notes.md
    └── system-architecture.md
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

### Cron 任务（自动调度）

| 时间 | 平台 | 任务 |
|------|------|------|
| 07:00 | Hermes | 梦境早间蒸馏 |
| 21:00 | Hermes | 技能衰减 + 每日报告 |
| 22:00 | OpenClaw | 梦境晚间蒸馏（600s 超时） |
| 09:00 Mon | Hermes | 技能缺口检测 |
| every 2h | Hermes | 技能使用追踪（日志解析） |

### 手动触发

```bash
cd ~/SharedSkills/dream-selfimproving
python3 scripts/dream.py
```

---

## 📖 详细文档

- [SKILL.md](SKILL.md) — 完整技能文档（部署、配置、Cron、故障排查）
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

### v5.1 技能进化完整流程

```
每日蒸馏 → 工作复盘 → 技能评分 → 用进废退 → 缺口检测 → 技能开发 → 汇报生成
    ↓           ↓           ↓           ↓           ↓           ↓         ↓
 洞察提取   完成分析    活跃度排名   状态变化    新技能需求   AI全自动生成   六大模块
                                    ↓
                        GapDetector v2.0
                        detect_and_generate()
                        ↓
              检测缺口 → 生成 SKILL.md 草稿
                        ↓
              写入 ~/SharedSkills/{skill_name}/
                        ↓
              OpenClaw/Hermes 自动发现
```

**与 skill-evolver 共用数据源**：`~/.skill_scoreboard/scores.json`

---

## 📌 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 5.1.0 | 2026-05-03 | GapDetector v2.0：detect_and_generate() 同时返回缺口 + SKILL.md 草稿；11种能力模板；E6/E8 流程整合；deep-researcher、image-generator 草稿 |
| 5.0.1 | 2026-05-03 | 更新描述，体现用进废退能力 |
| 5.0.0 | 2026-05-03 | v5.0 技能进化插件：用进废退 + 全自动技能开发 + 完整每日汇报 |
| 4.2.1 | 2026-04-30 | 上一稳定版本 |

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT-0 — Free to use, modify, and redistribute. No attribution required.
