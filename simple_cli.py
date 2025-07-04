#!/usr/bin/env python3
"""
Simple CLI for requirement optimization using shared core logic.
"""

import asyncio
import argparse
import signal
import sys
from core_optimizer import RequirementOptimizer, SessionManager


class CLIInterface:
    """CLI interface for the requirement optimizer."""

    def __init__(self):
        """Initialize CLI with core optimizer."""
        self.optimizer = RequirementOptimizer()
        self.session = SessionManager(self.optimizer)

    async def start_session(self, user_input: str):
        """Start a new optimization session and display results."""
        result = await self.session.start_session(user_input)
        self._display_result(result)
        return result["type"]

    async def handle_feedback(self, feedback: str):
        """Handle user feedback and display results."""
        result = await self.session.handle_feedback(feedback)
        self._display_result(result)
        return result["type"]

    def _display_result(self, result: dict):
        """Display result to user in CLI format."""
        result_type = result["type"]
        content = result["content"]

        if result_type == "error":
            print(f"\n❌ {content}")
            if "response_time" in result:
                print(f"⏱️ 响应时间: {result['response_time']:.2f}s")

            # Show additional error details if available
            if "error_type" in result:
                print(f"🔍 错误类型: {result['error_type']}")

            # Show retry suggestion
            print("\n🔄 您可以:")
            print("  1. 检查网络连接和配置")
            print("  2. 重新输入需求")
            print("  3. 输入 '/n' 开始新对话")

        elif result_type == "ai_response":
            print(f"\n🤖 AI回复: {content}")
            self._display_metadata(result)
            self._display_options()

        elif result_type == "ai_response_refined":
            print(f"\n🤖 AI调整后回复: {content}")
            self._display_metadata(result)
            self._display_options()

        elif result_type == "new_conversation":
            print(f"\n✨ {content}")

    def _display_metadata(self, result: dict):
        """Display response metadata."""
        if "response_time" in result:
            mode_text = f" ({result.get('mode', '')})" if result.get('mode') else ""
            print(f"⏱️ 响应时间: {result['response_time']:.2f}s{mode_text}")

    def _display_options(self):
        """Display user options."""
        print("\n请选择:")
        print("1. 输入反馈意见进行调整")
        print("2. 输入 '/n' 或 'n' 开始新对话")


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n👋 再见!")
    sys.exit(0)


async def main():
    """CLI interface for the requirement optimizer with interactive flow."""
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Interactive Requirement Optimizer")
    args = parser.parse_args()

    cli = CLIInterface()
    session_active = False

    print("🎯 交互式需求优化器")
    print("通过确认流程转换用户输入")
    print("命令: 'quit' 退出, '/n' 或 'n' 开始新对话, Ctrl+C 快速退出\n")

    while True:
        try:
            try:
                if not session_active:
                    user_input = input("请输入您的需求: ").strip()
                else:
                    user_input = input("您的反馈: ").strip()
            except KeyboardInterrupt:
                print("\n再见!")
                break

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见!")
                break

            if user_input.lower() in ['/n', 'n']:
                cli.session.reset_session()
                session_active = False
                print("✨ 开始新对话\n")
                continue

            if not user_input:
                continue

            try:
                if not session_active:
                    # Start new session
                    print("处理中...")
                    result_type = await cli.start_session(user_input)
                    if result_type in ["ai_response", "ai_response_refined"]:
                        session_active = True
                else:
                    # Handle feedback in current session
                    result_type = await cli.handle_feedback(user_input)

                    if result_type == "new_conversation":
                        session_active = False
                        continue

            except KeyboardInterrupt:
                print("\n操作已取消。")
                continue

        except KeyboardInterrupt:
            print("\n再见!")
            break
        except Exception as e:
            print(f"错误: {e}")


def cli_main():
    """Entry point for the CLI script."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()