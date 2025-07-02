#!/usr/bin/env python3
"""
Command-line interface entry points for OiPromot.
"""

import sys
import argparse
from src.oipromot.cli.interactive import InteractiveCLI
from src.oipromot.cli.simple import SimpleCLI


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OiPromot - Office AI Prompt Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py interactive    # Start interactive mode
  python cli.py simple         # Start simple mode
  python cli.py --help         # Show this help message
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['interactive', 'simple'],
        nargs='?',
        default='interactive',
        help='CLI mode to run (default: interactive)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'interactive':
            cli = InteractiveCLI()
            cli.run()
        elif args.mode == 'simple':
            cli = SimpleCLI()
            cli.run()
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()