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
        
        self.fuzzy_strengths = {
            # Tasks requiring AI's natural abilities beyond simple automation
            "complex_data_cleaning": ["fuzzy", "complex", "messy data", "inconsistent", "clean up", "normalize", "复杂", "模糊", "混乱数据", "不一致", "清理", "标准化"],
            "intelligent_extraction": ["understand", "interpret", "figure out", "smart extract", "detect pattern", "理解", "解释", "智能提取", "检测模式", "识别规律"],
            "contextual_processing": ["context", "meaning", "semantic", "understand content", "情境", "语义", "理解内容", "上下文"],
            "adaptive_tasks": ["flexible", "adapt", "case by case", "depends on", "灵活", "适应", "具体情况", "根据情况"],
            "reasoning_required": ["decide", "judge", "determine", "choose best", "reasoning", "判断", "决定", "推理", "选择最佳"]
        }
    
    def analyze_task(self, user_input: str) -> CapabilityRecommendation:
        """Determine if task is better suited for AI, VBA, or requires fuzzy AI processing."""
        user_lower = user_input.lower()
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
        
        ai_score = 0
        vba_score = 0
        fuzzy_score = 0
        ai_reasons = []
        vba_reasons = []
        fuzzy_reasons = []
        
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
        
        # Check fuzzy strengths (complex tasks requiring AI natural abilities)
        for category, keywords in self.fuzzy_strengths.items():
            if any(keyword in user_lower for keyword in keywords):
                fuzzy_score += 2  # Weight fuzzy tasks higher
                fuzzy_reasons.append(category)
        
        # Determine recommendation based on scores
        if fuzzy_score > 0:
            recommendation = "FUZZY_AI"
            primary_reason = fuzzy_reasons[0] if fuzzy_reasons else "complex_reasoning"
        elif ai_score > vba_score:
            recommendation = "AI"
            primary_reason = ai_reasons[0] if ai_reasons else "content_generation"
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
            fuzzy_score=fuzzy_score,
            is_chinese=is_chinese
        )