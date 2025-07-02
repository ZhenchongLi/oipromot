#!/usr/bin/env python3
"""
Test VBA Prompt Generation 
Shows how system generates prompts for VBA code generation (not VBA code itself)
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from interactive_optimizer import InteractiveOptimizer


def test_vba_prompt_generation():
    print("=== VBA Prompt Generation Test ===")
    print("Testing that system generates VBA prompts, not VBA code...\n")
    
    optimizer = InteractiveOptimizer()
    
    # Test cases for VBA prompt generation
    test_cases = [
        # English VBA automation requests
        {
            "name": "English VBA Automation",
            "conversation": [
                "automate formatting for all Word documents in folder",
                "0",  # Word selection
                "apply Heading 1 style to first line, Normal style to body, save as PDF"
            ]
        },
        
        # Chinese VBA automation requests  
        {
            "name": "中文VBA自动化",
            "conversation": [
                "批量处理Excel工作表",
                "1",  # Excel selection
                "遍历所有工作表，删除空行，统一格式，汇总到新表"
            ]
        },
        
        # Content generation (should give content prompts, not VBA)
        {
            "name": "Content Generation",
            "conversation": [
                "write a business proposal",
                "0",  # Word selection
                "technology partnership proposal for AI integration"
            ]
        }
    ]
    
    for test_case in test_cases:
        print(f"🔄 {test_case['name']}")
        print("=" * 60)
        
        # Reset conversation
        optimizer.conversation_history = []
        
        for i, user_input in enumerate(test_case['conversation']):
            print(f"👤 User: {user_input}")
            
            response = optimizer.get_optimization(user_input)
            print(f"🤖 Assistant: {response}")
            
            # Analyze response type
            if i == len(test_case['conversation']) - 1:  # Final response
                if any(word in response.lower() for word in ["vba", "code", "loop", "for each", "function"]):
                    print("❌ ERROR: Generated VBA code instead of VBA prompt!")
                elif any(word in response.lower() for word in ["prompt", "requirement", "describe", "objects", "conditions"]):
                    print("✅ GOOD: Generated VBA prompt requirements")
                elif any(word in response.lower() for word in ["content", "topic", "format", "details"]):
                    print("✅ GOOD: Generated content prompt")
                else:
                    print("ℹ️  INFO: Generated direct command/response")
            
            print()
        
        print("-" * 60)
        print()
    
    print("Example of correct VBA prompt generation:")
    print("=" * 60)
    print("❌ WRONG (generates VBA code):")
    print("   For Each ws In Worksheets: ws.Range('A1').Delete")
    print()
    print("✅ CORRECT (generates VBA prompt):")
    print("   VBA需求：遍历所有工作表(对象)，删除空行(条件：行为空)，预期结果：清理后的工作表")
    print("   VBA requirement: Loop through worksheets (objects), delete empty rows (condition: row is empty), expected: cleaned worksheets")
    
    print("\nVBA prompt generation test completed! 🎉")


if __name__ == "__main__":
    test_vba_prompt_generation()