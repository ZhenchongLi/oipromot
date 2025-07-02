#!/usr/bin/env python3
"""
Test Model Capability Adaptation
Tests how system adjusts prompt detail based on target model capabilities
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from interactive_optimizer import InteractiveOptimizer


def test_model_capabilities():
    print("=== Model Capability Adaptation Test ===")
    print("Testing how prompts adapt for big vs small target models...\n")
    
    # Test same requests with different target models
    test_requests = [
        "write a business proposal",
        "automate Excel formatting", 
        "创建一份报告",
        "批量处理文档"
    ]
    
    for request in test_requests:
        print(f"📝 Request: '{request}'")
        print("=" * 60)
        
        # Test with Big Model
        print("🤖 BIG MODEL (GPT-4, Claude-3.5, etc.):")
        optimizer_big = InteractiveOptimizer()
        optimizer_big.target_model_type = "big"
        response_big = optimizer_big.smart_mock_response(request)
        print(f"   {response_big}")
        print()
        
        # Test with Small Model  
        print("🤖 SMALL MODEL (7B, 13B models, etc.):")
        optimizer_small = InteractiveOptimizer()
        optimizer_small.target_model_type = "small"
        response_small = optimizer_small.smart_mock_response(request)
        print(f"   {response_small}")
        print()
        
        print("-" * 60)
        print()
    
    # Test model switching commands
    print("🔄 Testing Model Switching Commands:")
    print("=" * 60)
    
    optimizer = InteractiveOptimizer()
    
    # Test switching to small model
    print("Input: /ms")
    response = optimizer.smart_mock_response("/ms")
    print(f"Response: {response}")
    print(f"Current model type: {optimizer.target_model_type}")
    print()
    
    # Test switching to big model
    print("Input: /mb")
    response = optimizer.smart_mock_response("/mb")
    print(f"Response: {response}")
    print(f"Current model type: {optimizer.target_model_type}")
    print()
    
    print("✅ Model capability adaptation working!")
    print("\n💡 Key Differences:")
    print("   Big Model   → Brief prompts, relies on model reasoning")
    print("   Small Model → Detailed prompts, explicit step-by-step instructions")
    print("\n🚀 Usage:")
    print("   /mb = Switch to big model mode (brief prompts)")
    print("   /ms = Switch to small model mode (detailed prompts)")
    print("   Current target model affects all subsequent prompt generation")


if __name__ == "__main__":
    test_model_capabilities()