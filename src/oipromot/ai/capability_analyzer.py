"""
Capability analyzer for determining AI vs VBA recommendations.
"""

from typing import Dict, List
from ..core.models import CapabilityRecommendation


class CapabilityAnalyzer:
    """Analyzes tasks to recommend AI vs VBA approaches."""
    
    def __init__(self):
        # AI vs VBA capability mapping
        self.ai_strengths = {
            # Tasks where AI excels
            "content_creation": ["write", "generate", "create content", "draft", "compose", "写", "生成", "创建", "起草"],
            "text_processing": ["summarize", "translate", "rewrite", "analyze text", "extract", "总结", "翻译", "改写", "分析"],
            "creative_tasks": ["brainstorm", "design", "creative", "ideas", "头脑风暴", "设计", "创意", "想法"],
            "analysis": ["analyze", "review", "compare", "evaluate", "分析", "评估", "比较", "审查"]
        }
        
        self.vba_strengths = {
            # Tasks where VBA/automation is more reliable
            "data_processing": ["batch", "bulk", "mass", "multiple files", "批量", "大量", "多个文件"],
            "precise_operations": ["format all", "apply styles", "exact formatting", "统一格式", "批量格式化"],
            "file_operations": ["save as", "convert", "export", "import", "保存为", "转换", "导出", "导入"],
            "repetitive_tasks": ["automate", "repeat", "loop", "每个", "重复", "自动化", "循环"]
        }
    
    def analyze_task(self, user_input: str) -> CapabilityRecommendation:
        """Determine if task is better suited for AI or VBA based on capabilities."""
        user_lower = user_input.lower()
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
        
        ai_score = 0
        vba_score = 0
        ai_reasons = []
        vba_reasons = []
        
        # Check AI strengths
        for category, keywords in self.ai_strengths.items():
            if any(keyword in user_lower for keyword in keywords):
                ai_score += 1
                ai_reasons.append(category)
        
        # Check VBA strengths
        for category, keywords in self.vba_strengths.items():
            if any(keyword in user_lower for keyword in keywords):
                vba_score += 1
                vba_reasons.append(category)
        
        # Determine recommendation
        if ai_score > vba_score:
            recommendation = "AI"
            primary_reason = ai_reasons[0] if ai_reasons else "general"
        elif vba_score > ai_score:
            recommendation = "VBA"
            primary_reason = vba_reasons[0] if vba_reasons else "automation"
        else:
            recommendation = "HYBRID"  # Both or unclear
            primary_reason = "mixed_capabilities"
        
        return CapabilityRecommendation(
            recommendation=recommendation,
            reason=primary_reason,
            ai_score=ai_score,
            vba_score=vba_score,
            is_chinese=is_chinese
        )