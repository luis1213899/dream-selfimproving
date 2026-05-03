"""
GapDetector — 技能缺口检测器
分析当前技能与工作需求的差距，识别需要开发的新技能
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class GapDetector:
    """技能缺口检测器"""
    
    # 已有的技能类型
    SKILL_CATEGORIES = {
        'memory': '记忆管理',
        'code': '代码开发',
        'research': '研究搜索',
        'creative': '创意生成',
        'social': '社交媒体',
        'productivity': '效率工具',
        'data': '数据处理',
        'mlops': '机器学习运维',
        'devops': 'DevOps',
        'security': '安全相关',
        'communication': '通讯工具',
        'media': '媒体处理',
    }
    
    def __init__(self, work_analysis: Dict, skill_scores: Dict, skill_registry: Dict):
        """
        初始化缺口检测器
        work_analysis: WorkAnalyzer 的分析结果
        skill_scores: SkillScorer 的评分结果
        skill_registry: SkillRegistry 的技能注册表
        """
        self.work_analysis = work_analysis
        self.skill_scores = skill_scores
        self.skill_registry = skill_registry
    
    def detect_gaps(self) -> List[Dict]:
        """
        检测技能缺口
        返回需要开发的新技能列表
        """
        gaps = []
        
        # 1. 从未完成任务分析技能缺口
        task_gaps = self._detect_from_tasks()
        gaps.extend(task_gaps)
        
        # 2. 从技能活跃度分析缺口
        activity_gaps = self._detect_from_activity()
        gaps.extend(activity_gaps)
        
        # 3. 从工作类型分析缺口
        type_gaps = self._detect_from_work_type()
        gaps.extend(type_gaps)
        
        # 4. 去重并评估优先级
        gaps = self._deduplicate_gaps(gaps)
        
        return gaps
    
    def _detect_from_tasks(self) -> List[Dict]:
        """从未完成任务分析技能需求"""
        gaps = []
        incomplete = self.work_analysis.get('incomplete_tasks', [])
        
        for task in incomplete:
            content = task.get('content', '').lower()
            
            # 分析任务内容，识别所需技能
            if any(kw in content for kw in ['搜索', '查找', '查询', '搜索资料']):
                gaps.append({
                    'type': 'research',
                    'needed_for': task['content'][:50],
                    'priority': 'high',
                    'reason': '任务需要研究搜索能力'
                })
            
            if any(kw in content for kw in ['代码', '开发', '编程', '写代码']):
                gaps.append({
                    'type': 'code',
                    'needed_for': task['content'][:50],
                    'priority': 'high',
                    'reason': '任务需要编程开发能力'
                })
            
            if any(kw in content for kw in ['分析', '数据', '统计']):
                gaps.append({
                    'type': 'data',
                    'needed_for': task['content'][:50],
                    'priority': 'medium',
                    'reason': '任务需要数据分析能力'
                })
            
            if any(kw in content for kw in ['图片', '视频', '音频', '媒体']):
                gaps.append({
                    'type': 'media',
                    'needed_for': task['content'][:50],
                    'priority': 'medium',
                    'reason': '任务需要媒体处理能力'
                })
            
            if any(kw in content for kw in ['部署', '服务器', '运维']):
                gaps.append({
                    'type': 'devops',
                    'needed_for': task['content'][:50],
                    'priority': 'medium',
                    'reason': '任务需要DevOps能力'
                })
        
        return gaps
    
    def _detect_from_activity(self) -> List[Dict]:
        """从技能活跃度分析补充需求"""
        gaps = []
        
        # 找出极度低活跃的技能
        dormant_skills = [
            (name, data) for name, data in self.skill_scores.items()
            if data.get('tier') in ['🗄️', '⚰️']
        ]
        
        if len(dormant_skills) > 3:
            gaps.append({
                'type': 'review',
                'skill_names': [s[0] for s in dormant_skills[:3]],
                'priority': 'low',
                'reason': '多个技能长期未用，建议复习或归档'
            })
        
        # 技能覆盖检查
        active_categories = self._get_active_categories()
        for category, desc in self.SKILL_CATEGORIES.items():
            if category not in active_categories and category != 'review':
                gaps.append({
                    'type': 'missing_category',
                    'category': category,
                    'category_desc': desc,
                    'priority': 'low',
                    'reason': f'缺少{category}类技能覆盖'
                })
        
        return gaps
    
    def _detect_from_work_type(self) -> List[Dict]:
        """从工作类型分析潜在需求"""
        gaps = []
        
        # 分析今日工作类型
        entries = self.work_analysis.get('total_entries', 0)
        insights = len(self.work_analysis.get('insights', []))
        decisions = len(self.work_analysis.get('decisions', []))
        
        # 洞察多但决策少 → 需要更好的决策支持
        if insights > 5 and decisions < 2:
            gaps.append({
                'type': 'decision_support',
                'priority': 'medium',
                'reason': '工作产生大量洞察但决策少，可能需要更好的决策框架'
            })
        
        # 错误/纠正多 → 需要更好的错误预防
        corrections = len(self.work_analysis.get('corrections', []))
        if corrections > 3:
            gaps.append({
                'type': 'error_prevention',
                'priority': 'high',
                'reason': f'今日有{corrections}次纠正，需要错误预防机制'
            })
        
        return gaps
    
    def _get_active_categories(self) -> Set[str]:
        """获取当前活跃的技能类别"""
        active = set()
        for name, data in self.skill_scores.items():
            if data.get('tier') in ['🔥', '📈']:
                # 从技能名推断类别（简化版）
                name_lower = name.lower()
                if 'code' in name_lower or 'dev' in name_lower:
                    active.add('code')
                elif 'search' in name_lower or 'web' in name_lower:
                    active.add('research')
                elif 'media' in name_lower or 'audio' in name_lower:
                    active.add('media')
                elif 'data' in name_lower or 'analysis' in name_lower:
                    active.add('data')
                elif 'deploy' in name_lower or 'server' in name_lower:
                    active.add('devops')
        return active
    
    def _deduplicate_gaps(self, gaps: List[Dict]) -> List[Dict]:
        """去重并评估优先级"""
        seen = set()
        result = []
        
        for gap in gaps:
            key = gap.get('type', '') + gap.get('category', '')
            if key not in seen:
                seen.add(key)
                result.append(gap)
        
        # 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        result.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
        
        return result
    
    def suggest_skill_name(self, gap_type: str) -> str:
        """根据缺口类型建议技能名称"""
        suggestions = {
            'research': 'web-research',
            'code': 'code-assistant',
            'data': 'data-analysis',
            'media': 'media-processor',
            'devops': 'devops-automation',
            'decision_support': 'decision-helper',
            'error_prevention': 'error-checker',
        }
        return suggestions.get(gap_type, f'new-skill-{gap_type}')
