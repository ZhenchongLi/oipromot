#!/usr/bin/env python3
"""
Test script for Office Prompt Optimizer
Demonstrates the optimization functionality with sample inputs
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from oipromot.deepseek_service import DeepSeekService


def test_optimization():
    print("=== Office Prompt Optimizer Test ===")
    print("Testing prompt optimization with sample inputs...\n")
    
    deepseek = DeepSeekService()
    
    # Test cases
    test_inputs = [
        "make text bigger",
        "add numbers to rows", 
        "make a table",
        "bold text",
        "center text",
        "sum column",
        "create chart",
        "freeze rows",
        "make font red",
        "insert new row"
    ]
    
    for user_input in test_inputs:
        print(f"Input:  '{user_input}'")
        
        # Try real DeepSeek first, fall back to mock
        optimized = deepseek.optimize_prompt(user_input)
        if optimized is None:
            optimized = deepseek.optimize_prompt_mock(user_input)
            source = "(mock)"
        else:
            source = "(DeepSeek)"
        
        print(f"Output: '{optimized}' {source}")
        print("-" * 50)
    
    print("\nTest completed!")


if __name__ == "__main__":
    test_optimization()