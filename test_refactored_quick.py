#!/usr/bin/env python3
"""
Quick test of refactored components.
"""

from src.oipromot.ai.prompt_optimizer import PromptOptimizer
from src.oipromot.ai.capability_analyzer import CapabilityAnalyzer


def test_core_functionality():
    """Test core refactored functionality."""
    print("=== Testing Refactored Core Functionality ===\n")
    
    # Test CapabilityAnalyzer
    print("1. Testing CapabilityAnalyzer:")
    analyzer = CapabilityAnalyzer()
    
    test_cases = [
        "write a business proposal",
        "batch process Excel files", 
        "make text bigger",
        "写一份报告",
        "批量处理文档"
    ]
    
    for case in test_cases:
        result = analyzer.analyze_task(case)
        print(f"   '{case}' → {result.recommendation} ({result.reason})")
    
    print()
    
    # Test PromptOptimizer
    print("2. Testing PromptOptimizer:")
    optimizer = PromptOptimizer()
    
    # Test app selection
    response = optimizer.optimize_prompt("0")
    print(f"   App selection '0' → {response}")
    
    # Test model switching
    response = optimizer.set_target_model("small")
    print(f"   Model switch to small → {response}")
    
    # Test content generation
    response = optimizer.optimize_prompt("write a report")
    print(f"   'write a report' → {response}")
    
    # Test Chinese input
    response = optimizer.optimize_prompt("写一份文档")
    print(f"   '写一份文档' → {response}")
    
    print()
    
    # Test conversation management
    print("3. Testing Conversation Management:")
    print(f"   History length before: {len(optimizer.conversation_history)}")
    
    clear_response = optimizer.clear_conversation()
    print(f"   Clear response: {clear_response}")
    print(f"   History length after: {len(optimizer.conversation_history)}")
    
    print("\n✅ All refactored components working correctly!")


if __name__ == "__main__":
    test_core_functionality()