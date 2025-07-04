#!/usr/bin/env python3
"""
配置检查工具，帮助诊断常见的配置问题
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from typing import Dict, List, Tuple

load_dotenv()


class ConfigChecker:
    """配置检查器"""

    def __init__(self):
        self.issues = []
        self.suggestions = []

    async def check_all(self) -> Dict[str, any]:
        """检查所有配置项"""
        print("🔍 开始配置检查...")
        print("=" * 50)

        # 检查环境变量
        env_result = self.check_environment_variables()
        
        # 检查API连接
        api_result = await self.check_api_connection()
        
        # 检查模型可用性
        model_result = await self.check_model_availability()
        
        # 汇总结果
        all_passed = env_result and api_result and model_result
        
        self._print_summary(all_passed)
        
        return {
            "all_passed": all_passed,
            "environment": env_result,
            "api_connection": api_result,
            "model_availability": model_result,
            "issues": self.issues,
            "suggestions": self.suggestions
        }

    def check_environment_variables(self) -> bool:
        """检查环境变量配置"""
        print("\n📋 检查环境变量...")
        
        required_vars = {
            "API_BASE_URL": "API服务器地址",
            "AI_MODEL": "AI模型名称"
        }
        
        optional_vars = {
            "API_KEY": "API密钥（某些服务需要）",
            "WEB_HOST": "Web服务器地址",
            "WEB_PORT": "Web服务器端口"
        }
        
        all_good = True
        
        # 检查必需变量
        for var, desc in required_vars.items():
            value = os.getenv(var)
            if not value:
                print(f"❌ {var}: 未设置")
                self.issues.append(f"缺少必需的环境变量: {var}")
                self.suggestions.append(f"在.env文件中设置 {var}={desc}")
                all_good = False
            else:
                print(f"✅ {var}: {value}")
        
        # 检查可选变量
        for var, desc in optional_vars.items():
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: {value}")
            else:
                print(f"⚠️  {var}: 未设置 ({desc})")
        
        return all_good

    async def check_api_connection(self) -> bool:
        """检查API连接"""
        print("\n🌐 检查API连接...")
        
        api_url = os.getenv("API_BASE_URL")
        if not api_url:
            print("❌ API_BASE_URL 未设置，跳过连接检查")
            return False
        
        try:
            # 尝试连接API根路径和models端点
            async with aiohttp.ClientSession() as session:
                # 先尝试访问models端点，这通常是更好的健康检查方式
                models_url = f"{api_url.rstrip('/')}/models"
                
                api_key = os.getenv("API_KEY")
                headers = {}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                
                async with session.get(models_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        print(f"✅ API服务器可访问: {api_url}")
                        return True
                    elif response.status == 401:
                        print(f"⚠️  API需要认证，但可访问: {api_url}")
                        return True  # 服务器可访问，只是需要认证
                    elif response.status == 404:
                        # 如果models端点不存在，尝试根路径
                        async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as root_response:
                            if root_response.status in [200, 404]:  # 404也表示服务器可访问
                                print(f"✅ API服务器可访问: {api_url}")
                                return True
                            else:
                                print(f"⚠️  API服务器响应异常: HTTP {root_response.status}")
                                self.suggestions.append("检查API服务器是否正常运行")
                                return False
                    else:
                        print(f"⚠️  API服务器响应异常: HTTP {response.status}")
                        self.suggestions.append("检查API服务器是否正常运行")
                        return False
        
        except asyncio.TimeoutError:
            print(f"❌ API服务器连接超时: {api_url}")
            self.issues.append("API连接超时")
            self.suggestions.append("检查网络连接和API服务器地址")
            return False
        
        except Exception as e:
            print(f"❌ API连接失败: {str(e)}")
            self.issues.append(f"API连接错误: {str(e)}")
            self.suggestions.append("检查API_BASE_URL配置和网络连接")
            return False

    async def check_model_availability(self) -> bool:
        """检查模型可用性"""
        print("\n🤖 检查模型可用性...")
        
        api_url = os.getenv("API_BASE_URL")
        model_name = os.getenv("AI_MODEL")
        api_key = os.getenv("API_KEY")
        
        if not api_url or not model_name:
            print("❌ API配置不完整，跳过模型检查")
            return False
        
        try:
            # 构建请求
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # 尝试简单的模型调用
            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": "hello"}],
                "max_tokens": 10,
                "enable_thinking": False  # Required for some APIs like Qwen/Dashscope
            }
            
            async with aiohttp.ClientSession() as session:
                chat_url = f"{api_url.rstrip('/')}/chat/completions"
                async with session.post(
                    chat_url, 
                    json=data, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        print(f"✅ 模型可用: {model_name}")
                        return True
                    elif response.status == 401:
                        print(f"❌ 认证失败: 请检查API_KEY")
                        self.issues.append("API认证失败")
                        self.suggestions.append("检查API_KEY是否正确")
                        return False
                    elif response.status == 404:
                        print(f"❌ 模型不存在: {model_name}")
                        self.issues.append(f"模型 {model_name} 不可用")
                        self.suggestions.append("检查AI_MODEL配置，确保模型名称正确")
                        return False
                    else:
                        try:
                            response_text = await response.text()
                            print(f"❌ 模型调用失败: HTTP {response.status}")
                            
                            # 尝试解析错误信息
                            if response_text:
                                # 限制显示的响应长度
                                display_text = response_text[:300] + "..." if len(response_text) > 300 else response_text
                                print(f"响应: {display_text}")
                                
                                # 检查常见错误模式
                                if "enable_thinking" in response_text.lower():
                                    self.suggestions.append("API要求设置enable_thinking参数，这已在最新版本中修复")
                                elif "invalid_request_error" in response_text.lower():
                                    self.suggestions.append("请求参数有误，请检查模型名称和API兼容性")
                                elif "rate_limit" in response_text.lower():
                                    self.suggestions.append("API调用频率限制，请稍后重试")
                                else:
                                    self.suggestions.append("模型调用失败，请检查API服务器和模型配置")
                                    
                            self.issues.append(f"模型调用失败: HTTP {response.status}")
                            return False
                        except Exception:
                            print(f"❌ 模型调用失败: HTTP {response.status} (响应解析失败)")
                            self.issues.append(f"模型调用失败: HTTP {response.status}")
                            return False
        
        except asyncio.TimeoutError:
            print(f"❌ 模型调用超时")
            self.issues.append("模型调用超时")
            self.suggestions.append("模型响应较慢，可能是服务器负载高")
            return False
        
        except Exception as e:
            print(f"❌ 模型检查失败: {str(e)}")
            self.issues.append(f"模型检查错误: {str(e)}")
            return False

    def _print_summary(self, all_passed: bool):
        """打印检查总结"""
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 所有配置检查通过！")
            print("您的环境已正确配置，可以正常使用。")
        else:
            print("💥 发现配置问题")
            print("\n❌ 问题:")
            for issue in self.issues:
                print(f"  • {issue}")
            
            print("\n💡 建议:")
            for suggestion in self.suggestions:
                print(f"  • {suggestion}")
            
            print("\n📚 更多帮助:")
            print("  • 检查 .env.example 文件了解正确的配置格式")
            print("  • 确保API服务（如Ollama）正在运行")
            print("  • 验证网络连接和防火墙设置")

async def main():
    """主函数"""
    checker = ConfigChecker()
    await checker.check_all()

def config_main():
    """Entry point for the config check script."""
    asyncio.run(main())

if __name__ == "__main__":
    config_main()