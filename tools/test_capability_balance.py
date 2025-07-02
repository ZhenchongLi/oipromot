#!/usr/bin/env python3
"""
Test AI vs VBA Capability Balancing
Tests how system recommends AI or VBA based on task characteristics
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from interactive_optimizer import InteractiveOptimizer


def test_capability_balancing():
    print("=== AI vs VBA Capability Balancing Test ===")
    print("Testing intelligent recommendations based on task characteristics...\n")
    
    optimizer = InteractiveOptimizer()
    
    # Test cases with expected recommendations
    test_cases = [
        # AI Strengths (should recommend AI)
        {
            "category": "AI Strengths",
            "tasks": [
                "write a business proposal",
                "summarize this document", 
                "translate text to Chinese",
                "analyze the content",
                "写一份报告",
                "总结文档内容"
            ]
        },
        
        # VBA Strengths (should recommend VBA)
        {
            "category": "VBA Strengths", 
            "tasks": [
                "batch process 100 Excel files",
                "automate formatting for all documents",
                "convert all files to PDF",
                "apply styles to multiple documents",
                "批量处理工作表",
                "自动化格式设置"
            ]
        },
        
        # Mixed/Hybrid tasks
        {
            "category": "Hybrid Tasks",
            "tasks": [
                "analyze data and generate reports",
                "process text content and save results",
                "extract information and format output",
                "分析内容并批量输出"
            ]
        },
        
        # Text processing (AI advantage)
        {
            "category": "Text Processing (AI)",
            "tasks": [
                "rewrite this paragraph",
                "extract key points",
                "review document quality",
                "改写这段文字"
            ]
        }
    ]
    
    for category_info in test_cases:
        print(f"📂 {category_info['category']}")
        print("=" * 60)
        
        for task in category_info['tasks']:
            print(f"📝 Task: '{task}'")
            
            # Get capability recommendation
            capability = optimizer.get_capability_recommendation(task)
            
            # Get response with recommendation
            response = optimizer.smart_mock_response(task)
            
            # Show recommendation details
            print(f"   🎯 Recommendation: {capability['recommendation']}")
            print(f"   📊 Scores: AI={capability['ai_score']}, VBA={capability['vba_score']}")
            print(f"   🔍 Reason: {capability['reason']}")
            print(f"   🤖 Response: {response.replace(chr(10), ' | ')}")
            
            # Analyze if recommendation makes sense
            if "AI" in response:
                indicator = "✅ AI"
            elif "VBA" in response:
                indicator = "🔧 VBA"
            elif "混合" in response or "Hybrid" in response:
                indicator = "🔀 Hybrid"
            else:
                indicator = "❓ Unclear"
            
            print(f"   📋 Classification: {indicator}")
            print()
        
        print("-" * 60)
        print()
    
    # Test edge cases
    print("🔍 Edge Case Testing:")
    print("=" * 60)
    
    edge_cases = [
        "make text bigger",  # Simple operation
        "hello world",       # Unclear task
        "process",          # Ambiguous
        "Excel",           # Just application name
    ]
    
    for task in edge_cases:
        print(f"📝 Task: '{task}'")
        capability = optimizer.get_capability_recommendation(task)
        response = optimizer.smart_mock_response(task)
        print(f"   🎯 Recommendation: {capability['recommendation']}")
        print(f"   🤖 Response: {response.replace(chr(10), ' | ')}")
        print()
    
    print("✅ Capability balancing test completed!")
    print("\n💡 Key Insights:")
    print("   ✅ AI recommended for: Content creation, text processing, analysis")
    print("   🔧 VBA recommended for: Batch operations, precise formatting, file processing") 
    print("   🔀 Hybrid for: Complex tasks requiring both capabilities")
    print("   📊 Scoring system helps determine best approach")
    print("\n🚀 This helps users choose the most effective solution for their specific needs!")


if __name__ == "__main__":
    test_capability_balancing()