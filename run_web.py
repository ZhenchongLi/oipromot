#!/usr/bin/env python3
"""
启动脚本for web应用
"""

import uvicorn


def main():
    """Main entry point for web application."""
    print("🎯 启动交互式需求优化器 Web 应用")
    print("📱 访问地址: http://localhost:8000")
    print("🔗 WebSocket 地址: ws://localhost:8000/ws/{session_id}")
    print("📝 按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()