#!/usr/bin/env python3
"""
Test Improved Office Prompt Optimizer
Tests 0/1 app selection and content vs VBA categorization
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from interactive_optimizer import InteractiveOptimizer


def test_improved_system():
    print("=== Improved Office Optimizer Test ===")
    print("Testing 0/1 app selection and content vs VBA categorization...\n")
    
    optimizer = InteractiveOptimizer()
    
    # Test conversation flows
    test_flows = [
        # Flow 1: Content generation (English)
        {
            "name": "Content Generation (English)",
            "conversation": [
                "write a business letter",
                "0",  # Word selection
                "formal complaint letter"
            ]
        },
        
        # Flow 2: Content generation (Chinese)
        {
            "name": "内容生成 (Chinese)",
            "conversation": [
                "写一份报告",
                "0",  # Word selection  
                "工作总结报告"
            ]
        },
        
        # Flow 3: VBA automation (English)
        {
            "name": "VBA Automation (English)", 
            "conversation": [
                "automate formatting for all documents",
                "0",  # Word selection
                "apply heading styles to all documents in folder"
            ]
        },
        
        # Flow 4: Excel operations (Chinese)
        {
            "name": "Excel操作 (Chinese)",
            "conversation": [
                "批量处理工作表",
                "1",  # Excel selection
                "合并多个工作表数据"
            ]
        },
        
        # Flow 5: Direct command (English)
        {
            "name": "Direct Command (English)",
            "conversation": [
                "make text bigger",
                "0",  # Word selection
                "14pt"
            ]
        }
    ]
    
    for flow in test_flows:
        print(f"🔄 {flow['name']}")
        print("=" * 50)
        
        # Reset conversation for each flow
        optimizer.conversation_history = []
        
        for i, user_input in enumerate(flow['conversation']):
            print(f"👤 User: {user_input}")
            
            response = optimizer.get_optimization(user_input)
            print(f"🤖 Assistant: {response}")
            print()
        
        print("-" * 50)
        print()
    
    # Test app selection responses
    print("🔢 Testing App Selection (0/1)")
    print("=" * 50)
    
    app_tests = ["0", "1"]
    for app_choice in app_tests:
        print(f"👤 User: {app_choice}")
        response = optimizer.smart_mock_response(app_choice)
        print(f"🤖 Assistant: {response}")
        print()
    
    print("Test completed! 🎉")


if __name__ == "__main__":
    test_improved_system()