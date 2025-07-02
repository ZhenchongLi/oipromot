"""
Main prompt optimization service combining all AI capabilities.
"""

from typing import Optional, Dict, Any, List
from .capability_analyzer import CapabilityAnalyzer
from ..core.models import CapabilityRecommendation
from ..services.ai_service import AIService


class PromptOptimizer:
    """Main service for optimizing Office automation prompts."""
    
    def __init__(self, target_model_type: str = "big"):
        self.ai_service = AIService()
        self.analyzer = CapabilityAnalyzer()
        self.target_model_type = target_model_type
        self.conversation_history: List[Dict[str, str]] = []
        
        # Target model capabilities
        self.model_types = {
            "big": {
                "name": "Big Model (GPT-4, Claude-3.5, etc.)",
                "prompt_style": "brief, contextual, assumes good reasoning",
                "max_detail": "moderate"
            },
            "small": {
                "name": "Small Model (7B, 13B models, etc.)",
                "prompt_style": "detailed, step-by-step, explicit instructions", 
                "max_detail": "high"
            }
        }
    
    def set_target_model(self, model_type: str) -> str:
        """Set target model type and return confirmation message."""
        if model_type not in self.model_types:
            return "Invalid model type. Use 'big' or 'small'."
        
        self.target_model_type = model_type
        model_name = self.model_types[model_type]["name"]
        
        if model_type == "big":
            return f"🤖 Switched to big model mode: {model_name}\\nPrompts will be more brief, relying on model reasoning"
        else:
            return f"🤖 Switched to small model mode: {model_name}\\nPrompts will be more detailed with explicit steps"
    
    def clear_conversation(self) -> str:
        """Clear conversation history."""
        self.conversation_history = []
        return "🧹 Conversation cleared! Starting fresh with new memory."
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def get_capability_recommendation(self, user_input: str) -> CapabilityRecommendation:
        """Get AI vs VBA capability recommendation for the task."""
        return self.analyzer.analyze_task(user_input)
    
    async def optimize_prompt(self, user_input: str) -> str:
        """Main optimization method that returns the best response."""
        try:
            # Add user input to history
            self.add_to_history("user", user_input)
            
            # Create context-aware prompt for DeepSeek
            context = ""
            if len(self.conversation_history) > 1:
                context = "\\nPrevious conversation:\\n"
                for msg in self.conversation_history[-4:]:  # Last 4 messages for context
                    context += f"{msg['role']}: {msg['content']}\\n"
            
            target_model_info = self.model_types[self.target_model_type]
            full_prompt = f"""
You are an OfficeAI assistant for Word and Excel automation. Strategy:

Target Model: {target_model_info['name']}
Prompt Style: {target_model_info['prompt_style']}

1. App Selection: Use "0=Word, 1=Excel" format
2. Task Categories:
   - Content generation → Word + content details (adjust detail based on target model)
   - Function operations → Generate VBA prompt requirements (adjust detail based on target model)
   - Direct commands → Specific UI steps

Rules:
- CRITICAL: Respond in SAME LANGUAGE as current request (Chinese→Chinese, English→English)
- Keep responses very short (1-2 lines max)
- Adjust detail level for target model: {self.target_model_type} model needs {target_model_info['max_detail']} detail
- For content tasks → focus on Word + content prompts
- For functional tasks → create prompts for VBA generation (DO NOT write VBA code)

{context}
Current request: {user_input}

Response IN SAME LANGUAGE with appropriate detail level for {self.target_model_type} model:"""

            # Try configured AI service (OpenAI/DeepSeek/Ollama)
            if self.ai_service.is_available():
                try:
                    result = await self.ai_service.process_message(full_prompt)
                    if result:
                        self.add_to_history("assistant", result)
                        return result
                except Exception as ai_error:
                    # Log AI error but continue to fallback
                    print(f"⚠️  AI service error, using fallback: {ai_error}")
            
            # Fallback to smart mock if AI service unavailable or failed
            result = self._generate_smart_response(user_input)
            self.add_to_history("assistant", result)
            return result
            
        except Exception as e:
            return f"Error: {e}"
    
    def _generate_smart_response(self, user_input: str) -> str:
        """Generate smart mock response with capability-based recommendations."""
        user_lower = user_input.lower()
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
        
        # Handle model selection commands
        if user_input.lower() in ['/mb', '/model-big']:
            return self.set_target_model("big")
        
        if user_input.lower() in ['/ms', '/model-small']:
            return self.set_target_model("small")
        
        # Handle clear command
        if user_input.lower() in ['/c', '/clear']:
            return self.clear_conversation()
        
        # Handle app selection responses (0/1)
        if user_input.strip() in ['0', '1']:
            app_name = "Word" if user_input.strip() == '0' else "Excel"
            if is_chinese:
                return f"✅ 已选择{app_name}\\n\\n请详细描述你要完成的具体任务：\\n- 数据操作请描述具体步骤\\n- 内容创作请说明主题和要求\\n- 格式调整请明确目标样式"
            return f"✅ Selected {app_name}\\n\\nPlease describe your specific task in detail:\\n- For data operations: describe specific steps\\n- For content creation: specify topic and requirements\\n- For formatting: clarify target style"
        
        # Get capability recommendation for the task
        capability = self.get_capability_recommendation(user_input)
        
        # Generate response based on capability and task type
        return self._generate_capability_based_response(user_input, capability, is_chinese)
    
    def _generate_capability_based_response(self, user_input: str, capability: CapabilityRecommendation, is_chinese: bool) -> str:
        """Generate response based on capability analysis."""
        user_lower = user_input.lower()
        
        # Content generation tasks
        content_keywords = ["write", "generate", "create content", "draft", "letter", "report", "document", 
                           "写", "生成", "创建", "文档", "信件", "报告", "起草"]
        if any(word in user_lower for word in content_keywords):
            if is_chinese:
                if capability.recommendation == "AI":
                    base_msg = "应用选择：0=Word, 1=Excel\\n✅AI优势任务：内容创作"
                    if self.target_model_type == "small":
                        return f"{base_msg}\\n需要详细提示：具体主题、字数要求、格式规范、目标受众"
                    else:
                        return f"{base_msg}\\n简要描述主题和类型即可"
                else:
                    return "应用选择：0=Word, 1=Excel\\n内容生成→Word，请提供更多细节"
            else:
                if capability.recommendation == "AI":
                    base_msg = "App: 0=Word, 1=Excel\\n✅AI Strength: Content creation"
                    if self.target_model_type == "small":
                        return f"{base_msg}\\nNeed detailed prompt: specific topic, word count, format specs, target audience"
                    else:
                        return f"{base_msg}\\nBrief topic and type description sufficient"
                else:
                    return "App: 0=Word, 1=Excel\\nContent generation → Word. Provide more details"
        
        # Specific data processing tasks (ID card, birthday, age calculation, text splitting)
        data_keywords = ["身份证", "生日", "年龄", "提取", "计算", "出生", "拆分", "分离", "分割", "姓名", "电话", 
                         "ID card", "birthday", "age", "extract", "calculate", "split", "separate", "name", "phone"]
        if any(word in user_lower for word in data_keywords):
            if is_chinese:
                if "身份证" in user_lower and ("生日" in user_lower or "年龄" in user_lower):
                    return f"应用选择：1=Excel\\n🔧VBA解决方案：数据提取和计算\\n\\n使用MID函数提取身份证中的出生日期：\\n=MID(A2,7,8) 然后格式化为 年/月/日\\n计算年龄：=DATEDIF(生日列,TODAY(),\"Y\")\\n\\n适合Excel自动化处理，批量操作效率高"
                elif "拆分" in user_lower or "分离" in user_lower or "分割" in user_lower:
                    if "姓名" in user_lower or "电话" in user_lower:
                        return f"应用选择：1=Excel\\n🔧VBA解决方案：文本拆分\\n\\n使用Excel函数分离数据：\\n方法1：数据→分列→按分隔符分割\\n方法2：公式 =LEFT(B2,FIND(\" \",B2)-1) 提取姓名\\n方法3：公式 =RIGHT(B2,LEN(B2)-FIND(\" \",B2)) 提取电话\\n\\n批量操作效率高，适合大量数据处理"
                    else:
                        return f"应用选择：1=Excel\\n🔧VBA解决方案：文本拆分\\n\\n使用分列功能或文本函数进行数据分离\\n请明确分隔符类型（空格/逗号/其他）"
            else:
                if "id card" in user_lower and ("birthday" in user_lower or "age" in user_lower):
                    return f"App: 1=Excel\\n🔧VBA Solution: Data extraction and calculation\\n\\nUse MID function to extract birth date from ID card:\\n=MID(A2,7,8) then format as YYYY/MM/DD\\nCalculate age: =DATEDIF(birthday_column,TODAY(),\"Y\")\\n\\nSuitable for Excel automation, efficient for batch processing"
                elif "split" in user_lower or "separate" in user_lower:
                    return f"App: 1=Excel\\n🔧VBA Solution: Text splitting\\n\\nUse Excel functions to separate data:\\nMethod 1: Data→Text to Columns→Delimiter\\nMethod 2: Formula =LEFT(B2,FIND(\" \",B2)-1) for first part\\nMethod 3: Formula =RIGHT(B2,LEN(B2)-FIND(\" \",B2)) for second part\\n\\nEfficient for batch processing"
        
        # VBA/Automation tasks
        automation_keywords = ["automate", "macro", "vba", "batch", "format all", "process", "convert",
                              "自动化", "宏", "批处理", "处理", "转换", "格式化"]
        if any(word in user_lower for word in automation_keywords):
            if is_chinese:
                if capability.recommendation == "VBA":
                    base_msg = "应用选择：0=Word, 1=Excel\\n🔧VBA优势任务：精确操作/批量处理"
                    if self.target_model_type == "small":
                        return f"{base_msg}\\n需要详细需求：具体对象(文件/单元格)、操作条件、错误处理、预期结果"
                    else:
                        return f"{base_msg}\\n描述自动化目标和主要步骤即可"
                elif capability.recommendation == "AI":
                    return "应用选择：0=Word, 1=Excel\\n✅AI优势任务：文本处理\\n简要描述处理需求即可"
                else:  # HYBRID
                    return "应用选择：0=Word, 1=Excel\\n🔀混合方案：AI处理内容 + VBA执行操作\\n请描述具体任务以确定最佳方案"
            else:
                if capability.recommendation == "VBA":
                    base_msg = "App: 0=Word, 1=Excel\\n🔧VBA Strength: Precise operations/batch processing"
                    if self.target_model_type == "small":
                        return f"{base_msg}\\nNeed detailed requirements: specific objects (files/cells), conditions, error handling, expected results"
                    else:
                        return f"{base_msg}\\nDescribe automation goal and main steps"
                elif capability.recommendation == "AI":
                    return "App: 0=Word, 1=Excel\\n✅AI Strength: Text processing\\nBrief description of processing needs sufficient"
                else:  # HYBRID
                    return "App: 0=Word, 1=Excel\\n🔀Hybrid approach: AI for content + VBA for execution\\nDescribe specific task to determine best approach"
        
        # Default capability-based recommendation
        if capability.recommendation == "AI":
            if is_chinese:
                return f"应用选择：0=Word, 1=Excel\\n✅AI优势任务：{capability.reason}\\n任务：'{user_input}'"
            return f"App: 0=Word, 1=Excel\\n✅AI Strength: {capability.reason}\\nTask: '{user_input}'"
        elif capability.recommendation == "VBA":
            if is_chinese:
                return f"应用选择：0=Word, 1=Excel\\n🔧VBA优势任务：{capability.reason}\\n任务：'{user_input}'"
            return f"App: 0=Word, 1=Excel\\n🔧VBA Strength: {capability.reason}\\nTask: '{user_input}'"
        elif capability.recommendation == "HYBRID":
            if is_chinese:
                return f"应用选择：0=Word, 1=Excel\\n🔀混合方案：AI+VBA\\n任务：'{user_input}'\\n请提供更多细节以确定最佳方案"
            return f"App: 0=Word, 1=Excel\\n🔀Hybrid approach: AI+VBA\\nTask: '{user_input}'\\nProvide more details to determine best approach"
        
        # Default fallback
        if is_chinese:
            return f"应用选择：0=Word, 1=Excel\\n任务：'{user_input}'"
        return f"App: 0=Word, 1=Excel\\nTask: '{user_input}'"