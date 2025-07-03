
"""
Main prompt optimization service combining all AI capabilities.
"""

from typing import Optional, Dict, Any, List
from ..services.ai_service import AIService


class PromptOptimizer:
    """Main service for optimizing Office automation prompts."""
    
    def __init__(self, target_model_type: str = "big", trust_mode: bool = False):
        self.ai_service = AIService()
        self.target_model_type = target_model_type
        self.trust_mode = trust_mode  # When True, trust big models and minimize optimization
        self.conversation_history: List[Dict[str, str]] = []
        
        # Pre-planned templates for different task types
        self.user_templates = self._initialize_user_templates()
        
        # Target model capabilities
        self.model_types = {
            "big": {
                "name": "Big Model (GPT-4, Claude-3.5, etc.)",
            },
            "small": {
                "name": "Small Model (7B, 13B models, etc.)",
            }
        }
    
    def set_target_model(self, model_type: str) -> str:
        """Set target model type and return confirmation message."""
        if model_type not in self.model_types:
            return "Invalid model type. Use 'big' or 'small'."
        
        self.target_model_type = model_type
        model_name = self.model_types[model_type]["name"]
        
        if model_type == "big":
            return f"🤖 Switched to big model mode: {model_name}\nPrompts will be more brief, relying on model reasoning"
        else:
            return f"🤖 Switched to small model mode: {model_name}\nPrompts will be more detailed with explicit steps"
    
    def clear_conversation(self) -> str:
        """Clear conversation history."""
        self.conversation_history = []
        return "🧹 Conversation cleared! Starting fresh with new memory."
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def _initialize_user_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize user-facing, pre-defined templates."""
        return {
            "report": {
                "description": "Generate a structured report with a title and sections.",
                "template": "Report Title: {title}\n\nSection 1: {section1_title}\n{section1_content}\n\nSection 2: {section2_title}\n{section2_content}",
            },
            "summary": {
                "description": "Summarize a long text into key points.",
                "template": "Original Text: {text}\n\nKey Points Summary:\n- {point1}\n- {point2}\n- {point3}",
            },
            "email": {
                "description": "Draft a professional email.",
                "template": "Subject: {subject}\n\nDear {recipient},\n\n{body}\n\nBest regards,\n{sender}",
            },
        }

    def list_templates(self) -> str:
        """Return a formatted string of available templates."""
        if not self.user_templates:
            return "No templates available."
        
        output = "Available templates:\n"
        for name, data in self.user_templates.items():
            output += f"- {name}: {data['description']}\n"
        return output

    async def process_with_template(self, user_input: str, template_name: str) -> str:
        """Process user input with a pre-defined template."""
        try:
            template_data = self.user_templates.get(template_name.lower())
            if not template_data:
                return f"Template '{template_name}' not found. Use /list to see available templates."

            template = template_data["template"]
            
            # Add user input to history
            self.add_to_history("user", f"Input: {user_input}\nTemplate: {template_name}")

            is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)

            if is_chinese:
                prompt = f"""
                你是一个Office自动化专家。

                📋 原始用户请求:
                "{user_input}"

                📋 使用此模板:
                "{template}"

                请根据用户请求和模板，生成一个完整的、可执行的解决方案。将模板中的占位符（例如 {{placeholder}}）替换为从用户请求中提取的相关信息。
                """
            else:
                prompt = f"""
                You are an Office automation expert.

                📋 Original User Request:
                "{user_input}"

                📋 Use this template:
                "{template}"

                Please generate a complete, executable solution based on the user request and the provided template. Replace the placeholders in the template (e.g., {{placeholder}}) with the relevant information from the user request.
                """

            if self.ai_service.is_available():
                try:
                    result = await self.ai_service.process_message(prompt)
                    if result:
                        self.add_to_history("assistant", result)
                        return result
                except Exception as e:
                    print(f"Error processing with template: {e}")
                    return "Error processing with template."

            return "AI service is not available."
        except Exception as e:
            return f"Error: {e}"
    
    async def optimize_prompt(self, user_input: str) -> str:
        """Main optimization method that returns the best response."""
        try:
            # Add user input to history
            self.add_to_history("user", user_input)
            
            is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
            
            if is_chinese:
                prompt = f"""
                你是一个Office自动化专家。

                请根据以下用户请求，生成一个完整的、可执行的解决方案。
                
                用户请求: "{user_input}"
                """
            else:
                prompt = f"""
                You are an Office automation expert.

                Please generate a complete, executable solution based on the following user request.
                
                User request: "{user_input}"
                """

            # Try configured AI service (OpenAI/DeepSeek/Ollama)
            if self.ai_service.is_available():
                try:
                    result = await self.ai_service.process_message(prompt)
                    if result:
                        self.add_to_history("assistant", result)
                        return result
                except Exception as ai_error:
                    # Log AI error but continue to fallback
                    print(f"⚠️  AI service error, using fallback: {ai_error}")
            
            # Fallback to smart mock if AI service unavailable or failed
            if is_chinese:
                return "AI服务当前不可用，请稍后再试。"
            else:
                return "The AI service is currently unavailable. Please try again later."
            
        except Exception as e:
            return f"Error: {e}"
