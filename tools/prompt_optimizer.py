#!/usr/bin/env python3
"""
Office Prompt Optimizer Tool

Simple terminal interface for optimizing user prompts for Office automation.
Run this script and input your requests to get optimized Office commands.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from oipromot.deepseek_service import DeepSeekService


def main():
    print("=== Office Prompt Optimizer ===")
    print("Enter your Office requests and get optimized commands!")
    print("Commands: /q=quit, /e=exit\n")
    
    deepseek = DeepSeekService()
    
    while True:
        try:
            # Get user input
            user_input = input("Your request: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['/q', '/quit', '/e', '/exit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("Processing...")
            
            # Try real DeepSeek first, fall back to mock
            optimized = deepseek.optimize_prompt(user_input)
            if optimized is None:
                print("DeepSeek not available, using mock responses...")
                optimized = deepseek.optimize_prompt_mock(user_input)
            
            # Display result
            print(f"Optimized: {optimized}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()