#!/usr/bin/env python3
"""
Test Language Matching in Office Prompt Optimizer
Tests that responses match input language (Chinese→Chinese, English→English)
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the InteractiveOptimizer from the tools directory
sys.path.insert(0, os.path.dirname(__file__))
from interactive_optimizer import InteractiveOptimizer


def test_language_matching():
    print("=== Language Matching Test ===")
    print("Testing that responses match input language...\n")
    
    optimizer = InteractiveOptimizer()
    
    test_cases = [
        # English inputs
        ("make text bigger", "English"),
        ("create a table", "English"), 
        ("sum column A", "English"),
        
        # Chinese inputs
        ("字号调大一点", "Chinese"),
        ("创建一个表格", "Chinese"),
        ("求和A列", "Chinese"),
        ("字体变红色", "Chinese"),
    ]
    
    for user_input, expected_lang in test_cases:
        print(f"Input ({expected_lang}): '{user_input}'")
        
        # Test the smart mock response
        response = optimizer.smart_mock_response(user_input)
        
        # Check if response language matches
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in response)
        response_lang = "Chinese" if has_chinese else "English"
        
        match_status = "✅" if response_lang == expected_lang else "❌"
        
        print(f"Response ({response_lang}): '{response}' {match_status}")
        print("-" * 60)
    
    print("Language matching test completed!")


if __name__ == "__main__":
    test_language_matching()