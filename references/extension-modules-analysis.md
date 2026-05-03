# Dream Self-Improving — Extension Modules Architecture Review

**Date:** 2026-05-03  
**Purpose:** Document what each module actually does vs. what it claims to do.

---

## Executive Summary

The v5.0 extension modules are **structurally complete** but the "AI generation" steps are all **template-based**, not LLM-powered. The pipeline is:

```
gap_detector  →  hardcoded keyword matching
learner       →  template filling from gap_specs dict
generator     →  writes SKILL.md from string templates
quality.py    → 事后评分，不参与生成过程
registry      → 写入 JSON，不触发 Hermes 重载
```

**Critical gap:** Hermes never learns about newly created skills. The registry writes a JSON file but never calls `hermes skills reload` or any mechanism to make new skills discoverable.

---

## Module-by-Module Analysis

### skill_evolution/
| File | What it does | What's missing |
|------|-------------|---------------|
| `scorer.py` | Scores skills using call frequency × recency × success_rate × decay | Relies entirely on skill-scoreboard data. No scoreboard = no data |
| `decay.py` | Changes skill status based on days unused | Only changes status; doesn't trigger re-learning or replacement |
| `registry.py` | Central JSON registry at `memory/skill_registry.json` | **Doesn't trigger Hermes skill reload.** New skills are invisible to Hermes |

### skill_explorer/
| File | What it does | What's missing |
|------|-------------|---------------|
| `gap_detector.py` | Keyword matching against hardcoded `SKILL_CATEGORIES` dict | Not LLM-powered. Uses `if any(kw in content for kw in ['搜索','查找'...])` pattern |
| `learner.py` | Template fills `gap_specs` dict for known gap types | Hardcoded specs for: research, code, data, media, devops. Unknown types fall through |

### skill_developer/
| File | What it does | What's missing |
|------|-------------|---------------|
| `generator.py` | `_generate_files()` calls `templates.py` to build SKILL.md strings | **Pure string formatting. No LLM call. No actual script generation.** |
| `templates.py` | `SkillTemplates.generate_skill_md()` returns formatted markdown | Outputs `(待定义)` placeholders for undefined fields |
| `quality.py` | Post-generation scoring via regex checks on file contents | Doesn't run during generation; only rates existing files |

### reporter/
| File | What it does | What's missing |
|------|-------------|---------------|
| `daily_report.py` | String template substitution into 6-section markdown | No real data sources connected for most sections |

---

## The Three Broken Loops

### Loop 1: Skill Creation (BROKEN at Hermes reload)
```
gap_detector.detect_gaps()
  → GapDetector returns gap dicts
    → learner.generate_skill_requirements()
      → Hardcoded template fill
        → generator.generate_skill()
          → SKILL.md written to SharedSkills/
            → registry.add_skill()
              → skill_registry.json updated
                → ❌ Hermes never notified
```
**Fix needed:** After `registry.add_skill()`, call `hermes skills reload` or equivalent.

### Loop 2: Skill Call Tracking (PARTIAL)
```
hermes uses skill
  → skill-scoreboard logs call
    → scorer.score_all_skills() reads scores.json
      → New skills don't appear until they ARE called (chicken-egg)
```
**Fix needed:** Auto-call mechanism for newly created skills, or initial seed score.

### Loop 3: Archive/Replace (BROKEN)
```
decay.process_all_skills_decay()
  → Skill tier drops to ⚰️ archived
    → ❌ No check: "is there a newer skill that covers this?"
    → ❌ No replacement suggestion
    → ❌ Deprecated skill name stays blocked from re-creation
```
**Fix needed:** On archive, check registry for replacement candidates. Unblock name if genuinely superseded.

---

## What's Actually Working

- ✅ **Scoring math** — decay nodes, tier thresholds, weights are all sound
- ✅ **M-FLOW knowledge graph** — Bundle Search, RAG layer, graph connectivity
- ✅ **Thalamus/Amygdala/Hippocampus** tagging — real signal detection
- ✅ **Daily report template** — comprehensive structure
- ✅ **Registry JSON** — correct schema, good history tracking

---

## Priority Fixes for True Autonomy

1. **P0:** Make `registry.add_skill()` trigger Hermes skill reload
2. **P1:** Replace `gap_detector` keyword matching with LLM analysis of raw对话
3. **P1:** Replace `generator` template fill with LLM skill generation
4. **P2:** Add deprecated-name unblocking logic on archive
5. **P2:** Seed new skills with initial scoreboard entry to break chicken-egg
