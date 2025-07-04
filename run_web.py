#!/usr/bin/env python3
"""
启动脚本for web应用
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Main entry point for web application."""
    # Get configuration from environment variables
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "8000"))
    reload = os.getenv("WEB_RELOAD", "true").lower() in ("true", "1", "yes", "on")
    
    print("🎯 启动交互式需求优化器 Web 应用")
    print(f"📱 访问地址: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"🔗 WebSocket 地址: ws://{host if host != '0.0.0.0' else 'localhost'}:{port}/ws/{{session_id}}")
    print("📝 按 Ctrl+C 停止服务器")
    print(f"🔧 配置: Host={host}, Port={port}, Reload={reload}")
    print("-" * 50)
    
    uvicorn.run(
        "web_app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()