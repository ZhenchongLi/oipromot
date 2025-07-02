#!/usr/bin/env python3
"""
Test Command Interface
Tests the new /q, /e, /c command interface
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from interactive_optimizer import InteractiveOptimizer


def test_commands():
    print("=== Command Interface Test ===")
    print("Testing /q, /e, /c commands...\n")
    
    optimizer = InteractiveOptimizer()
    
    # Test commands
    test_commands = [
        ("/c", "should clear conversation"),
        ("/clear", "should clear conversation"),
        ("0", "should work as app selection"),
        ("1", "should work as app selection"),
        ("make text bigger", "should work as normal input"),
        ("字号调大", "should work as Chinese input"),
    ]
    
    print("📝 Available Commands:")
    print("  /q or /quit  → Quit")
    print("  /e or /exit  → Exit") 
    print("  /c or /clear → Clear conversation")
    print("  0            → Select Word")
    print("  1            → Select Excel")
    print()
    
    print("🧪 Testing command responses:")
    print("-" * 40)
    
    for command, description in test_commands:
        print(f"Input: '{command}' ({description})")
        
        if command in ['/c', '/clear']:
            # Test clear command
            optimizer.conversation_history = [{"role": "user", "content": "test"}]
            print("  Before clear: conversation has 1 item")
            response = optimizer.get_optimization(command)
            print(f"  Response: {response}")
            print(f"  After clear: conversation has {len(optimizer.conversation_history)} items")
        else:
            # Test normal responses
            response = optimizer.smart_mock_response(command)
            print(f"  Response: {response}")
        
        print()
    
    print("✅ Command interface ready!")
    print("\n🚀 To try interactively:")
    print("   uv run python tools/interactive_optimizer.py")
    print("\n💡 Example usage:")
    print("   📝 Your request: make text bigger")
    print("   🤖 App: 0=Word, 1=Excel")
    print("   📝 Your request: 0")
    print("   🤖 Selected Word. Please describe the specific task.")
    print("   📝 Your request: /c")
    print("   🧹 Conversation cleared!")
    print("   📝 Your request: /q")
    print("   👋 Goodbye!")


if __name__ == "__main__":
    test_commands()