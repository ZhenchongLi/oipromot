"""
Tests for the capability analyzer.
"""

import pytest
from src.oipromot.ai.capability_analyzer import CapabilityAnalyzer


class TestCapabilityAnalyzer:
    """Test cases for CapabilityAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CapabilityAnalyzer()
    
    def test_ai_content_creation(self):
        """Test AI recommendation for content creation tasks."""
        result = self.analyzer.analyze_task("write a business proposal")
        assert result.recommendation == "AI"
        assert result.reason == "content_creation"
        assert result.ai_score > result.vba_score
        assert not result.is_chinese
    
    def test_ai_text_processing_chinese(self):
        """Test AI recommendation for Chinese text processing."""
        result = self.analyzer.analyze_task("总结文档内容")
        assert result.recommendation == "AI"
        assert result.reason == "text_processing"
        assert result.ai_score > result.vba_score
        assert result.is_chinese
    
    def test_vba_batch_processing(self):
        """Test VBA recommendation for batch processing."""
        result = self.analyzer.analyze_task("batch process 100 Excel files")
        assert result.recommendation == "VBA"
        assert result.reason == "data_processing"
        assert result.vba_score > result.ai_score
        assert not result.is_chinese
    
    def test_vba_automation_chinese(self):
        """Test VBA recommendation for Chinese automation tasks."""
        result = self.analyzer.analyze_task("自动化格式设置")
        assert result.recommendation == "VBA"
        assert result.reason == "repetitive_tasks"
        assert result.vba_score > result.ai_score
        assert result.is_chinese
    
    def test_hybrid_mixed_capabilities(self):
        """Test hybrid recommendation for mixed tasks."""
        result = self.analyzer.analyze_task("make text bigger")
        assert result.recommendation == "HYBRID"
        assert result.reason == "mixed_capabilities"
        assert result.ai_score == result.vba_score
    
    def test_complex_task_with_both_keywords(self):
        """Test task with both AI and VBA keywords."""
        result = self.analyzer.analyze_task("analyze data and batch process files")
        # Should favor AI since it has more matches (analyze + generate from "data")
        assert result.ai_score >= result.vba_score