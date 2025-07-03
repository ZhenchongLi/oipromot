#!/usr/bin/env python3
"""
Interactive Office Prompt Optimizer

Conversational interface that asks clarifying questions to optimize Office automation requests.
"""

from oipromot.deepseek_service import DeepSeekService


class InteractiveOptimizer:
    def __init__(self):
        self.deepseek = DeepSeekService()
        self.conversation_history = []
        self.target_model_type = "big"  # Default to big model

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

        # AI vs VBA capability mapping
        self.ai_strengths = {
            # Tasks where AI excels
            "content_creation": ["write", "generate", "create content", "draft", "compose", "写", "生成", "创建", "起草"],
            "text_processing": ["summarize", "translate", "rewrite", "analyze text", "extract", "总结", "翻译", "改写", "分析"],
            "creative_tasks": ["brainstorm", "design", "creative", "ideas", "头脑风暴", "设计", "创意", "想法"],
            "analysis": ["analyze", "review", "compare", "evaluate", "分析", "评估", "比较", "审查"]
        }

        self.vba_strengths = {
            # Tasks where VBA/automation is more reliable
            "data_processing": ["batch", "bulk", "mass", "multiple files", "批量", "大量", "多个文件"],
            "precise_operations": ["format all", "apply styles", "exact formatting", "统一格式", "批量格式化"],
            "file_operations": ["save as", "convert", "export", "import", "保存为", "转换", "导出", "导入"],
            "repetitive_tasks": ["automate", "repeat", "loop", "每个", "重复", "自动化", "循环"]
        }

    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})

    def get_capability_recommendation(self, user_input: str) -> dict:
        """Determine if task is better suited for AI or VBA based on capabilities"""
        user_lower = user_input.lower()
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)

        ai_score = 0
        vba_score = 0
        ai_reasons = []
        vba_reasons = []

        # Check AI strengths
        for category, keywords in self.ai_strengths.items():
            if any(keyword in user_lower for keyword in keywords):
                ai_score += 1
                ai_reasons.append(category)

        # Check VBA strengths
        for category, keywords in self.vba_strengths.items():
            if any(keyword in user_lower for keyword in keywords):
                vba_score += 1
                vba_reasons.append(category)

        # Determine recommendation
        if ai_score > vba_score:
            recommendation = "AI"
            primary_reason = ai_reasons[0] if ai_reasons else "general"
        elif vba_score > ai_score:
            recommendation = "VBA"
            primary_reason = vba_reasons[0] if vba_reasons else "automation"
        else:
            recommendation = "HYBRID"  # Both or unclear
            primary_reason = "mixed_capabilities"

        return {
            "recommendation": recommendation,
            "reason": primary_reason,
            "ai_score": ai_score,
            "vba_score": vba_score,
            "is_chinese": is_chinese
        }

    def get_optimization(self, user_input: str) -> str:
        """Get optimization or clarifying question from DeepSeek"""
        try:
            # Add user input to history
            self.add_to_history("user", user_input)

            # Create context-aware prompt
            context = ""
            if len(self.conversation_history) > 1:
                context = "\nPrevious conversation:\n"
                for msg in self.conversation_history[-4:]:  # Last 4 messages for context
                    context += f"{msg['role']}: {msg['content']}\n"

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

            # Try DeepSeek API
            if self.deepseek.api_key:
                result = self.deepseek.optimize_prompt_with_context(full_prompt)
                if result:
                    self.add_to_history("assistant", result)
                    return result

            # Fallback to smart mock
            result = self.smart_mock_response(user_input)
            self.add_to_history("assistant", result)
            return result

        except Exception as e:
            return f"Error: {e}"

    def smart_mock_response(self, user_input: str) -> str:
        """Smart response with app selection (0/1) and task categorization"""
        user_lower = user_input.lower()

        # Detect if input contains Chinese characters
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)

        # Handle model selection commands
        if user_input.lower() in ['/mb', '/model-big']:
            self.target_model_type = "big"
            model_name = self.model_types["big"]["name"]
            if is_chinese:
                return f"🤖 已切换到大模型模式：{model_name}\n提示将更简洁，依赖模型推理能力"
            return f"🤖 Switched to big model mode: {model_name}\nPrompts will be more brief, relying on model reasoning"

        if user_input.lower() in ['/ms', '/model-small']:
            self.target_model_type = "small"
            model_name = self.model_types["small"]["name"]
            if is_chinese:
                return f"🤖 已切换到小模型模式：{model_name}\n提示将更详细，包含具体步骤"
            return f"🤖 Switched to small model mode: {model_name}\nPrompts will be more detailed with explicit steps"

        # Handle app selection responses (0/1)
        if user_input.strip() in ['0', '1']:
            app_name = "Word" if user_input.strip() == '0' else "Excel"
            if is_chinese:
                return f"已选择{app_name}。请继续描述具体任务。"
            return f"Selected {app_name}. Please describe the specific task."

        # Get capability recommendation for the task
        capability = self.get_capability_recommendation(user_input)

        # Content generation (Word focus)
        content_keywords = ["write", "generate", "create content", "draft", "letter", "report", "document",
                           "写", "生成", "创建", "文档", "信件", "报告", "起草"]
        if any(word in user_lower for word in content_keywords):
            if is_chinese:
                if capability["recommendation"] == "AI":
                    base_msg = "应用选择：0=Word, 1=Excel\n✅AI优势任务：内容创作"
                    if self.target_model_type == "small":
                        return f"{base_msg}\n需要详细提示：具体主题、字数要求、格式规范、目标受众"
                    else:
                        return f"{base_msg}\n简要描述主题和类型即可"
                else:
                    return "应用选择：0=Word, 1=Excel\n内容生成→Word，请提供更多细节"
            else:
                if capability["recommendation"] == "AI":
                    base_msg = "App: 0=Word, 1=Excel\n✅AI Strength: Content creation"
                    if self.target_model_type == "small":
                        return f"{base_msg}\nNeed detailed prompt: specific topic, word count, format specs, target audience"
                    else:
                        return f"{base_msg}\nBrief topic and type description sufficient"
                else:
                    return "App: 0=Word, 1=Excel\nContent generation → Word. Provide more details"

        # VBA/Automation tasks (functional operations)
        automation_keywords = ["automate", "macro", "vba", "batch", "format all", "process", "convert",
                              "自动化", "宏", "批处理", "处理", "转换", "格式化"]
        if any(word in user_lower for word in automation_keywords):
            if is_chinese:
                if capability["recommendation"] == "VBA":
                    base_msg = "应用选择：0=Word, 1=Excel\n🔧VBA优势任务：精确操作/批量处理"
                    if self.target_model_type == "small":
                        return f"{base_msg}\n需要详细需求：具体对象(文件/单元格)、操作条件、错误处理、预期结果"
                    else:
                        return f"{base_msg}\n描述自动化目标和主要步骤即可"
                elif capability["recommendation"] == "AI":
                    return "应用选择：0=Word, 1=Excel\n✅AI优势任务：文本处理\n简要描述处理需求即可"
                else:  # HYBRID
                    return "应用选择：0=Word, 1=Excel\n🔀混合方案：AI处理内容 + VBA执行操作\n请描述具体任务以确定最佳方案"
            else:
                if capability["recommendation"] == "VBA":
                    base_msg = "App: 0=Word, 1=Excel\n🔧VBA Strength: Precise operations/batch processing"
                    if self.target_model_type == "small":
                        return f"{base_msg}\nNeed detailed requirements: specific objects (files/cells), conditions, error handling, expected results"
                    else:
                        return f"{base_msg}\nDescribe automation goal and main steps"
                elif capability["recommendation"] == "AI":
                    return "App: 0=Word, 1=Excel\n✅AI Strength: Text processing\nBrief description of processing needs sufficient"
                else:  # HYBRID
                    return "App: 0=Word, 1=Excel\n🔀Hybrid approach: AI for content + VBA for execution\nDescribe specific task to determine best approach"

        # Text processing tasks (AI strengths)
        text_processing_keywords = ["summarize", "translate", "rewrite", "analyze text", "extract", "review",
                                   "总结", "翻译", "改写", "分析文本", "提取", "审查"]
        if any(word in user_lower for word in text_processing_keywords):
            if is_chinese:
                return "应用选择：0=Word, 1=Excel\n✅AI优势任务：文本处理\n描述具体文本处理需求（总结、翻译、分析等）"
            return "App: 0=Word, 1=Excel\n✅AI Strength: Text processing\nDescribe specific text processing needs (summarize, translate, analyze, etc.)"

        # Excel-specific patterns
        excel_keywords = ["sum", "formula", "chart", "pivot", "cell", "column", "row", "worksheet",
                         "求和", "公式", "图表", "透视表", "单元格", "列", "行", "工作表"]
        if any(word in user_lower for word in excel_keywords):
            if is_chinese:
                if capability["recommendation"] == "VBA":
                    return "应用选择：0=Word, 1=Excel\n🔧VBA优势：Excel精确操作\n请描述具体数据处理需求"
                elif capability["recommendation"] == "AI":
                    return "应用选择：0=Word, 1=Excel\n✅AI优势：数据分析\n描述分析目标和预期结果"
                else:
                    return "应用选择：0=Word, 1=Excel\nExcel任务，请描述具体操作"
            else:
                if capability["recommendation"] == "VBA":
                    return "App: 0=Word, 1=Excel\n🔧VBA Strength: Precise Excel operations\nDescribe specific data processing needs"
                elif capability["recommendation"] == "AI":
                    return "App: 0=Word, 1=Excel\n✅AI Strength: Data analysis\nDescribe analysis goals and expected results"
                else:
                    return "App: 0=Word, 1=Excel\nExcel task. Describe the specific operation"

        # Word-specific patterns
        word_keywords = ["font", "paragraph", "page", "header", "footer", "style", "align",
                        "字体", "段落", "页面", "页眉", "页脚", "样式", "对齐"]
        if any(word in user_lower for word in word_keywords):
            if is_chinese:
                return "应用选择：0=Word, 1=Excel\n看起来是Word任务，请描述具体操作"
            return "App: 0=Word, 1=Excel\nSeems like Word task. Describe the specific operation"

        # Specific operation responses (when app is known)
        if "font" in user_lower or "字号" in user_lower or "字体" in user_lower:
            if "size" not in user_lower and "pt" not in user_lower and "磅" not in user_lower:
                if is_chinese:
                    return "字号调整为多少？（12磅、14磅、16磅等）"
                return "What font size? (12pt, 14pt, 16pt, etc.)"
            if is_chinese:
                return "Word操作：选择文字 → 开始 → 字号 → 14磅"
            return "Word: Select text → Home → Font Size → 14pt"

        # General capability-based recommendation
        if capability["recommendation"] == "AI":
            if is_chinese:
                return f"应用选择：0=Word, 1=Excel\n✅AI优势任务：{capability['reason']}\n任务：'{user_input}'"
            return f"App: 0=Word, 1=Excel\n✅AI Strength: {capability['reason']}\nTask: '{user_input}'"
        elif capability["recommendation"] == "VBA":
            if is_chinese:
                return f"应用选择：0=Word, 1=Excel\n🔧VBA优势任务：{capability['reason']}\n任务：'{user_input}'"
            return f"App: 0=Word, 1=Excel\n🔧VBA Strength: {capability['reason']}\nTask: '{user_input}'"
        elif capability["recommendation"] == "HYBRID":
            if is_chinese:
                return f"应用选择：0=Word, 1=Excel\n🔀混合方案：AI+VBA\n任务：'{user_input}'\n请提供更多细节以确定最佳方案"
            return f"App: 0=Word, 1=Excel\n🔀Hybrid approach: AI+VBA\nTask: '{user_input}'\nProvide more details to determine best approach"

        # Default - ask for app selection
        if is_chinese:
            return f"应用选择：0=Word, 1=Excel\n任务：'{user_input}'"
        return f"App: 0=Word, 1=Excel\nTask: '{user_input}'"

    def run(self):
        """Main interactive loop"""
        current_model = self.model_types[self.target_model_type]["name"]
        print("=== Interactive Office Optimizer ===")
        print("I'll help optimize your Word/Excel requests through conversation!")
        print(f"Target Model: {current_model}")
        print("Commands: /q=quit, /e=exit, /c=clear (fresh start), /mb=big model, /ms=small model\n")

        while True:
            try:
                user_input = input("📝 Your request: ").strip()

                if user_input.lower() in ['/q', '/quit']:
                    print("👋 Goodbye!")
                    break

                if user_input.lower() in ['/e', '/exit']:
                    print("👋 Goodbye!")
                    break

                if user_input.lower() in ['/c', '/clear']:
                    self.conversation_history = []
                    print("🧹 Conversation cleared! Starting fresh with new memory.")
                    continue

                if not user_input:
                    continue

                print("🤔 Processing...")
                response = self.get_optimization(user_input)
                print(f"🤖 {response}\n")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    optimizer = InteractiveOptimizer()
    optimizer.run()