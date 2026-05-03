# Skill Evolution v5.0 — MiniMax API 集成笔记

> 记录 skill_developer 模块调用 MiniMax API 时发现的问题和解决方案。

## MiniMax API 配置

| 项目 | 正确值 | 错误值 |
|------|--------|--------|
| Base URL | `https://api.minimaxi.com/v1` | `https://api.minimaxi.com/anthropic/v1` |
| Model | `minimax-m2.7` (全小写) | `MiniMax-M2.7` (首字母大写 → 400 unknown model) |
| Model | `MiniMax-M2` (可用) | `MiniMax-Standard` (无效) |
| Thinking 格式 | `<AI_Thinking>...</AI_Thinking>` (普通文本标签) | `</think>` (MiniMax不用这个) |
| Thinking 格式 | `<thinking>...</thinking>` (部分模型) | — |
| API Key 环境变量 | `MINIMAX_API_KEY` | `OPENAI_API_KEY` |

## 模型名大小写（关键！）

MiniMax API 对模型名大小写敏感：

```
✅ minimax-m2.7    — 当前可用
✅ MiniMax-M2      — 可用
❌ MiniMax-M2.7    — 400 unknown model
❌ MiniMax-Standard — 400 unknown param
❌ minimax-Standard — 400 unknown param
```

验证方法（发现问题时快速自检）：
```python
import openai, httpx
client = openai.OpenAI(api_key=KEY, base_url="https://api.minimaxi.com/v1",
                         timeout=httpx.Timeout(60.0), http_client=httpx.Client())
# 快速测试模型是否有效
for model in ["minimax-m2.7", "MiniMax-M2"]:
    try:
        resp = client.chat.completions.create(model=model,
            messages=[{"role": "user", "content": "ok"}], max_tokens=10)
        print(f"✅ {model}")
    except Exception as e:
        print(f"❌ {model}: {e}")
```

## 思考标签去除（必须！）

MiniMax 模型返回时会在正文前插入 `<AI_Thinking>...</AI_Thinking>` 标签，
这些内容不是 JSON，会导致解析失败。**必须在解析前全部去除。**

```python
import re

def strip_thinking_tags(raw: str) -> str:
    """去除 MiniMax 思考标签，避免 JSON 解析失败"""
    for tag in [
        r'<AI_Thinking>.*?</AI_Thinking>',   # MiniMax 主要格式
        r'<thinking>.*?</thinking>',           # 部分模型
        r'<think>.*?</think>',                  # 标准 Anthropic 格式
        r'<refrain>.*?</refrain>',             # 极少量模型
    ]:
        raw = re.sub(tag, '', raw, flags=re.DOTALL)
    return raw.strip()
```

**验证方法：** 调用后检查是否还有 `<AI` 或 `Thinking>` 残留：
```python
raw = resp.choices[0].message.content.strip()
if '<AI_Thinking>' in raw or '<thinking>' in raw:
    print("⚠️ 思考标签未去除干净！")
```

## Thinking 标签与 max_tokens 的关系

思考标签会占用 `max_tokens` 预算！如果 max_tokens 设得太小，
正文还没说完就被截断，导致 JSON 截断或分隔符不完整。

| 场景 | 最小安全 max_tokens |
|------|-------------------|
| gap_detector.py（只返回 JSON） | 1024 |
| generator.py（SKILL.md + Python 脚本） | **4096** |

实测：
- `gap_detector` 清理后 ~300-500 chars → 1024 够用
- `generator` SKILL.md(约1000) + Python脚本(约3000) + 思考标签(可能数千) → 2048 不够，4096 够

**症状：** 生成结果只有 SKILL.md，没有 scripts/ 目录，或脚本被截断（缺 `if __name__` 块）

## JSON 解析失败分类处理

```python
try:
    result = json.loads(content)
    return result
except json.JSONDecodeError as e:
    # 独立处理：说明 LLM 返回了内容但格式不对，不是空响应
    return {"gaps": [], "summary": f"LLM 返回非 JSON 格式: {str(e)[:80]}"}
except Exception as e:
    # 其他错误（网络、超时、400 等）
    return {"gaps": [], "summary": f"LLM 调用失败: {str(e)[:100]}"}
```

## 分隔符格式（推荐）

比 JSON 更稳定（JSON mode 在 MiniMax 上有格式混乱问题）：

```
===SKILL_MD_START===
name: skill-name
description: "..."
category: research
===SKILL_MD_END===

===SCRIPT_START===
#!/usr/bin/env python3
# 功能: ...
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    print(f"Searching: {args.query}")

if __name__ == "__main__":
    sys.exit(main())
===SCRIPT_END===
```

正则提取：
```python
def _parse_delimiter(raw: str, skill_name: str) -> Optional[Dict]:
    files = {}
    idx_start = re.search(r'===SKILL_MD_START===', raw)
    if idx_start:
        idx_content = idx_start.end()
        idx_end = raw.find("===SKILL_MD_END===", idx_content)
        if idx_end >= idx_content:
            files["SKILL.md"] = raw[idx_content:idx_end].strip()

    script_name = skill_name.replace("-", "_") + ".py"
    idx_script = re.search(r'===SCRIPT_START===', raw)
    if idx_script:
        idx_content = idx_script.end()
        idx_end = raw.find("===SCRIPT_END===", idx_content)
        if idx_end >= idx_content:
            files[f"scripts/{script_name}"] = raw[idx_content:idx_end].strip()

    return {"files": files} if files else None
```

## 常见错误排查

| 错误信息 | 原因 | 解决 |
|---------|------|------|
| `unknown model 'MiniMax-M2.7'` | 模型名大小写错误 | 改用 `minimax-m2.7` |
| `Expecting value: line 1 column 1` | max_tokens 太小导致截断 → 空内容；或思考标签未去除 | 增大 max_tokens + strip_thinking_tags |
| `LLM 返回非 JSON 格式` | 内容被截断或思考标签混入 | 见上文 strip_thinking_tags + max_tokens |
| 只生成 SKILL.md，scripts/ 缺失 | generator max_tokens 不够 | 设为 4096 |
| 脚本内容缺少末尾 `if __name__` | 同上，截断 | 同上 |

## 扩展模块文件位置

```
extensions/
├── skill_developer/
│   ├── gap_detector.py   # LLMGapDetector — 分析对话识别技能缺口
│   ├── generator.py     # LLMSkillGenerator — LLM生成分隔符格式技能
│   └── registry.py       # HermesSkillLoader — 写入后触发Hermes重载
├── skill_explorer/
│   ├── gap_detector.py   # GapDetector — 缺口检测逻辑
│   └── learner.py        # SkillLearner — 自主学习
└── skill_evolution/
    ├── scorer.py         # SkillScorer — 技能评分
    ├── decay.py          # DecayEngine — 用进废退衰减
    └── registry.py       # SkillRegistry — 技能注册表
```

## 验证命令

```python
from pathlib import Path
import shutil, sys
sys.path.insert(0, '/home/luis/.hermes/skills/openclaw-imports/dream-selfimproving/extensions/skill_developer')
sys.path.insert(0, '/home/luis/.hermes/skills/openclaw-imports/dream-selfimproving/extensions/skill_evolution')

from generator import LLMSkillGenerator
from registry import HermesSkillLoader, SkillRegistry

key = "your-minimax-api-key"
gen = LLMSkillGenerator(api_key=key)

gap = {
    "skill_name": "test-skill",
    "skill_type": "research",
    "trigger_signal": "用户多次要求搜索",
    "reasoning": "可自动化",
    "priority": "high",
    "concrete_use_case": "用户说'帮我搜索XXX'时自动调用"
}

result = gen.generate_from_gap(gap)
print(f"success={result['success']}, quality={result['quality_score']}/100")

# 验证Hermes重载
loader = HermesSkillLoader()
loader.notify_new_skill("test-skill")
```
