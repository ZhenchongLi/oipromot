#!/usr/bin/env python3
"""
Simplified CLI for requirement optimization.
"""

import sys
import asyncio
from simple_cli import RequirementOptimizer


async def main():
    """Main CLI entry point."""
    optimizer = RequirementOptimizer()
    
    print("🎯 Requirement Optimizer")
    print("Transform user input into clear requirement descriptions")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("Enter your requirement: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("Processing...")
            optimized = await optimizer.optimize_requirement(user_input)
            
            print(f"\n📝 Optimized Requirement:")
            print(f"{optimized}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())