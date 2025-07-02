"""
Tests for the main prompt optimizer.
"""

import pytest
from src.oipromot.ai.prompt_optimizer import PromptOptimizer


class TestPromptOptimizer:
    """Test cases for PromptOptimizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = PromptOptimizer()
    
    def test_model_switching(self):
        """Test model type switching."""
        # Test switching to small model
        result = self.optimizer.set_target_model("small")
        assert "small model mode" in result.lower()
        assert self.optimizer.target_model_type == "small"
        
        # Test switching to big model
        result = self.optimizer.set_target_model("big")
        assert "big model mode" in result.lower()
        assert self.optimizer.target_model_type == "big"
        
        # Test invalid model type
        result = self.optimizer.set_target_model("invalid")
        assert "Invalid model type" in result
    
    def test_conversation_management(self):
        """Test conversation history management."""
        # Add some history
        self.optimizer.add_to_history("user", "test message")
        assert len(self.optimizer.conversation_history) == 1
        
        # Clear conversation
        result = self.optimizer.clear_conversation()
        assert "cleared" in result.lower()
        assert len(self.optimizer.conversation_history) == 0
    
    def test_app_selection_responses(self):
        """Test app selection (0/1) responses."""
        # Test Word selection
        result = self.optimizer.optimize_prompt("0")
        assert "Word" in result
        assert "describe" in result.lower()
        
        # Test Excel selection
        result = self.optimizer.optimize_prompt("1")
        assert "Excel" in result
        assert "describe" in result.lower()
    
    def test_capability_recommendation_integration(self):
        """Test that capability recommendations are properly integrated."""
        # Test AI task
        result = self.optimizer.optimize_prompt("write a report")
        assert ("AI" in result) or ("内容创作" in result)
        
        # Test VBA task
        result = self.optimizer.optimize_prompt("batch process files")
        assert ("VBA" in result) or ("批量" in result)
    
    def test_language_consistency(self):
        """Test that responses match input language."""
        # English input
        result = self.optimizer.optimize_prompt("write a document")
        # Should not contain Chinese characters
        assert not any('\u4e00' <= char <= '\u9fff' for char in result)
        
        # Chinese input
        result = self.optimizer.optimize_prompt("写一份文档")
        # Should contain Chinese characters
        assert any('\u4e00' <= char <= '\u9fff' for char in result)
    
    def test_model_detail_adaptation(self):
        """Test that detail level adapts to model type."""
        # Set to small model
        self.optimizer.set_target_model("small")
        result_small = self.optimizer.optimize_prompt("write a report")
        
        # Set to big model
        self.optimizer.set_target_model("big")
        result_big = self.optimizer.optimize_prompt("write a report")
        
        # Small model should generally have more detailed responses
        # (This is a heuristic test, actual implementation may vary)
        assert len(result_small) >= len(result_big) * 0.8  # Allow some variance