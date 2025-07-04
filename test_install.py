#!/usr/bin/env python3
"""
测试安装脚本
"""

import sys
import importlib.util

def test_imports():
    """测试所有必要的导入."""
    required_modules = [
        'openai',
        'dotenv',
        'fastapi',
        'uvicorn',
        'jinja2'
    ]
    
    print("🧪 测试模块导入...")
    failed = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ 导入失败的模块: {', '.join(failed)}")
        print("请运行: uv sync")
        return False
    else:
        print("\n✅ 所有模块导入成功!")
        return True

def test_cli_main():
    """测试 CLI 主函数存在."""
    try:
        from simple_cli import main
        print("✅ CLI main 函数可用")
        return True
    except ImportError as e:
        print(f"❌ CLI main 函数导入失败: {e}")
        return False

def test_web_main():
    """测试 Web 主函数存在."""
    try:
        from run_web import main
        print("✅ Web main 函数可用")
        return True
    except ImportError as e:
        print(f"❌ Web main 函数导入失败: {e}")
        return False

def main():
    """运行所有测试."""
    print("🎯 测试 OiPromot 安装")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_cli_main,
        test_web_main
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 所有测试通过! 项目已正确安装。")
        print("\n🚀 启动命令:")
        print("  CLI 版本: uv run simple-cli")
        print("  Web 版本: uv run web-app")
        return 0
    else:
        print("💥 某些测试失败。请检查安装。")
        return 1

if __name__ == "__main__":
    sys.exit(main())