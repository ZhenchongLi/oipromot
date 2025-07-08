#!/usr/bin/env python3
"""
User management script for creating and managing users.
"""

import argparse
import getpass
from models import DatabaseManager


def create_user(username: str, password: str = None):
    """Create a new user."""
    if not password:
        password = getpass.getpass("请输入密码: ")
        password_confirm = getpass.getpass("请确认密码: ")
        if password != password_confirm:
            print("密码不匹配，请重试")
            return False
    
    db_manager = DatabaseManager()
    
    # Check if user already exists
    if db_manager.get_user_by_username(username):
        print(f"用户 '{username}' 已存在")
        return False
    
    try:
        user = db_manager.create_user(username, password)
        print(f"用户 '{username}' 创建成功，ID: {user.id}")
        return True
    except Exception as e:
        print(f"创建用户失败: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="用户管理工具")
    parser.add_argument("action", choices=["create"], help="操作类型")
    parser.add_argument("username", help="用户名")
    parser.add_argument("--password", help="密码（不提供则交互式输入）")
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_user(args.username, args.password)


if __name__ == "__main__":
    main()