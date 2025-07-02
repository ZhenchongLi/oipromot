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
    
    def _extract_key_information(self, messages: List[Dict[str, str]]) -> str:
        """Extract key information from earlier messages to preserve important context."""
        key_info = []
        
        for msg in messages:
            content = msg['content'].lower()
            role = msg['role']
            
            # Extract important keywords and patterns
            if role == 'user':
                # Look for task requirements, constraints, specific needs
                if any(keyword in content for keyword in ['requirement', 'need', 'must', 'should', 'requirement']):
                    key_info.append(f"Requirement: {msg['content'][:100]}...")
                elif any(keyword in content for keyword in ['error', 'problem', 'issue', 'bug']):
                    key_info.append(f"Issue: {msg['content'][:100]}...")
                elif any(keyword in content for keyword in ['target', 'goal', 'objective', 'purpose']):
                    key_info.append(f"Goal: {msg['content'][:100]}...")
            elif role == 'assistant':
                # Look for important decisions or recommendations
                if any(keyword in content for keyword in ['recommend', 'suggest', 'solution', 'approach']):
                    key_info.append(f"Recommendation: {msg['content'][:100]}...")
        
        return "; ".join(key_info) if key_info else ""
    
    def _get_domain_specific_guidance(self, capability_reason: str, is_chinese: bool) -> str:
        """Generate domain-specific guidance based on the type of fuzzy task."""
        guidance_templates = {
            "complex_data_cleaning": {
                "chinese": """
🔧 数据清理专项指导：
• 数据标准化：统一格式、编码、命名约定
• 重复项处理：识别并合并相似记录
• 缺失值策略：填充、插值或标记处理
• 异常值检测：识别并处理超出正常范围的数据
• 一致性检查：确保跨字段的数据逻辑一致性""",
                "english": """
🔧 Data Cleaning Specialized Guidance:
• Data Standardization: Unify formats, encoding, naming conventions
• Duplicate Handling: Identify and merge similar records
• Missing Value Strategy: Fill, interpolate, or flag for processing
• Outlier Detection: Identify and handle data outside normal ranges
• Consistency Checks: Ensure logical consistency across fields"""
            },
            "intelligent_extraction": {
                "chinese": """
🔍 智能提取专项指导：
• 模式识别：识别数据中的隐藏模式和结构
• 实体抽取：从文本中提取人名、地址、日期等
• 关系映射：建立数据元素之间的逻辑关系
• 上下文理解：基于语境推断缺失或模糊信息
• 语义分析：理解文本内容的深层含义""",
                "english": """
🔍 Intelligent Extraction Specialized Guidance:
• Pattern Recognition: Identify hidden patterns and structures in data
• Entity Extraction: Extract names, addresses, dates from text
• Relationship Mapping: Establish logical relationships between data elements
• Context Understanding: Infer missing or ambiguous information from context
• Semantic Analysis: Understand deeper meaning of text content"""
            },
            "contextual_processing": {
                "chinese": """
🧠 上下文处理专项指导：
• 语境分析：理解数据在特定环境中的含义
• 歧义消解：基于上下文确定多义词的正确含义
• 推理补全：根据已知信息推断缺失部分
• 文化适应：处理不同文化背景下的数据差异
• 动态适应：根据数据特点调整处理策略""",
                "english": """
🧠 Contextual Processing Specialized Guidance:
• Context Analysis: Understand data meaning in specific environments
• Ambiguity Resolution: Determine correct meaning based on context
• Inference Completion: Infer missing parts from known information
• Cultural Adaptation: Handle data differences across cultural backgrounds
• Dynamic Adaptation: Adjust processing strategy based on data characteristics"""
            },
            "adaptive_tasks": {
                "chinese": """
🔄 自适应处理专项指导：
• 灵活规则：根据数据特点动态调整处理规则
• 例外处理：为特殊情况设计专门的处理逻辑
• 学习适应：从处理结果中学习并优化策略
• 渐进处理：分步骤处理复杂任务，逐步完善
• 反馈循环：基于验证结果调整处理方法""",
                "english": """
🔄 Adaptive Processing Specialized Guidance:
• Flexible Rules: Dynamically adjust processing rules based on data characteristics
• Exception Handling: Design specialized logic for special cases
• Learning Adaptation: Learn from processing results and optimize strategy
• Progressive Processing: Handle complex tasks step-by-step, gradually refine
• Feedback Loop: Adjust processing methods based on validation results"""
            },
            "reasoning_required": {
                "chinese": """
🤔 推理决策专项指导：
• 逻辑推理：基于已知事实进行逻辑推导
• 权重评估：为不同判断标准分配合理权重
• 决策树：构建系统化的决策流程
• 不确定性处理：在信息不完整时做出最佳判断
• 置信度评估：为每个决策提供可信度评分""",
                "english": """
🤔 Reasoning & Decision Specialized Guidance:
• Logical Reasoning: Perform logical deduction based on known facts
• Weight Assessment: Assign reasonable weights to different judgment criteria
• Decision Tree: Build systematic decision-making processes
• Uncertainty Handling: Make optimal judgments with incomplete information
• Confidence Assessment: Provide confidence scores for each decision"""
            }
        }
        
        template = guidance_templates.get(capability_reason, {})
        return template.get("chinese" if is_chinese else "english", "")
    
    def _validate_information_preservation(self, original_input: str, optimized_response: str) -> bool:
        """Validate that optimized response preserves core information from original input."""
        original_lower = original_input.lower()
        response_lower = optimized_response.lower()
        
        # Extract key elements from original input
        key_elements = []
        
        # Check for specific tools/applications mentioned
        apps = ["word", "excel", "powerpoint", "office", "文档", "表格", "演示"]
        mentioned_apps = [app for app in apps if app in original_lower]
        key_elements.extend(mentioned_apps)
        
        # Check for action verbs (what user wants to do)
        actions = ["create", "generate", "write", "format", "calculate", "extract", "split", "convert", 
                  "automate", "batch", "process", "analyze", "创建", "生成", "写", "格式", "计算", "提取", 
                  "拆分", "转换", "自动化", "批处理", "处理", "分析"]
        mentioned_actions = [action for action in actions if action in original_lower]
        key_elements.extend(mentioned_actions)
        
        # Check for specific data types or objects
        objects = ["table", "chart", "document", "file", "data", "text", "number", "date", "image", 
                  "表格", "图表", "文档", "文件", "数据", "文本", "数字", "日期", "图片"]
        mentioned_objects = [obj for obj in objects if obj in original_lower]
        key_elements.extend(mentioned_objects)
        
        # Check preservation rate
        if not key_elements:
            return True  # No specific elements to validate
            
        preserved_count = sum(1 for element in key_elements if element in response_lower)
        preservation_rate = preserved_count / len(key_elements)
        
        # Consider it valid if at least 70% of key elements are preserved
        return preservation_rate >= 0.7
    
    def get_capability_recommendation(self, user_input: str) -> CapabilityRecommendation:
        """Get AI vs VBA capability recommendation for the task."""
        return self.analyzer.analyze_task(user_input)
    
    async def optimize_prompt(self, user_input: str) -> str:
        """Main optimization method that returns the best response."""
        try:
            # Add user input to history
            self.add_to_history("user", user_input)
            
            # Analyze task capability to determine if it's a fuzzy AI task
            capability = self.get_capability_recommendation(user_input)
            
            # Create context-aware prompt with enhanced context preservation
            context = ""
            if len(self.conversation_history) > 1:
                context = "\\nPrevious conversation:\\n"
                # Use last 10 messages for better context preservation
                recent_messages = self.conversation_history[-10:]
                
                # If conversation is very long, include a summary of earlier context
                if len(self.conversation_history) > 10:
                    earlier_messages = self.conversation_history[:-10]
                    # Extract key information from earlier messages
                    key_info = self._extract_key_information(earlier_messages)
                    if key_info:
                        context += f"Earlier context summary: {key_info}\\n\\n"
                
                # Add recent messages with full detail
                for msg in recent_messages:
                    context += f"{msg['role']}: {msg['content']}\\n"
            
            target_model_info = self.model_types[self.target_model_type]
            
            # Special handling for fuzzy AI tasks using Structured Data Analysis Framework
            if capability.recommendation == "FUZZY_AI":
                full_prompt = f"""
You are an OfficeAI assistant with advanced analytical capabilities for complex data processing tasks.

🧠 STRUCTURED DATA ANALYSIS FRAMEWORK (SDAF) MODE ACTIVATED
Task Type: {capability.reason}
Target Model: {target_model_info['name']}

📋 FOLLOW THIS SYSTEMATIC FRAMEWORK:

🔍 PHASE 1: DATA DISCOVERY & ASSESSMENT
STEP 1: Data Structure Analysis
- Examine input data format (Excel, CSV, text, mixed)
- Identify data types (text, numbers, dates, mixed)
- Detect patterns, delimiters, and structure inconsistencies
- Note missing values, special characters, edge cases

STEP 2: Complexity Assessment
- SIMPLE: Consistent structure, clean data → Use direct automation
- MEDIUM: Some inconsistencies, multiple formats → Use guided processing
- COMPLEX: Mixed structures, messy text → Use AI reasoning
- FUZZY: Requires interpretation and context → Use full AI capabilities

🎯 PHASE 2: PROCESSING STRATEGY DESIGN
STEP 3: Choose Processing Approach
- Direct automation (VBA/formulas) for consistent data
- AI reasoning for inconsistent/contextual data
- Hybrid approach for mixed complexity scenarios

STEP 4: Text Processing Strategy
TEXT STRUCTURE HANDLING:
- Structured text → Pattern matching/regex approach
- Semi-structured → AI interpretation + validation rules
- Unstructured → Full natural language processing
- Mixed formats → Adaptive processing per data case

⚙️ PHASE 3: IMPLEMENTATION GUIDANCE
STEP 5: Systematic Processing
A. READ & PARSE:
   1. Sample data to understand patterns and variations
   2. Identify edge cases and exception scenarios
   3. Plan comprehensive error handling strategy

B. PROCESS & TRANSFORM:
   1. Apply consistent rules where data allows
   2. Use AI reasoning for ambiguous/contextual cases
   3. Validate results continuously and handle exceptions

C. OUTPUT & VERIFY:
   1. Format results with consistent structure
   2. Perform data integrity checks
   3. Provide detailed processing summary

📝 PHASE 4: SPECIALIZED TEXT HANDLING GUIDES

FOR NAME/CONTACT DATA:
- Handle formats: "Last, First" vs "First Last" vs "Title First Last, Suffix"
- Process titles, suffixes, special characters, cultural variations
- Normalize spacing, capitalization, and punctuation

FOR ADDRESS DATA:
- Parse: "123 Main St, City, State ZIP" vs "Street\\nCity State ZIP"
- Handle abbreviations: "St/Street", "Ave/Avenue", "Rd/Road"
- Extract components: street number, name, unit, city, state, postal code

FOR MIXED CONTENT:
- Identify content types within single text fields
- Separate structured from unstructured information
- Apply appropriate processing methodology to each part

FOR INCONSISTENT DATA:
- Use contextual clues to interpret user intent
- Apply fuzzy matching algorithms for similar entries
- Flag uncertain cases for manual review/verification

🎯 CRITICAL EXECUTION RULES:
- LANGUAGE: Respond in SAME LANGUAGE as request (Chinese→Chinese, English→English)
- METHODOLOGY: Follow SDAF phases systematically
- REASONING: Explain your analytical process and decisions
- ADAPTATION: Adjust complexity based on target model: {self.target_model_type} needs {target_model_info['max_detail']} detail
- VALIDATION: Always verify results and provide confidence levels

App Selection Format: "0=Word, 1=Excel"

{context}
Current complex data task: {user_input}

{self._get_domain_specific_guidance(capability.reason, any('\u4e00' <= char <= '\u9fff' for char in user_input))}

RESPOND using SDAF methodology IN SAME LANGUAGE with systematic analysis:"""
            else:
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
                        # Validate information preservation
                        if self._validate_information_preservation(user_input, result):
                            self.add_to_history("assistant", result)
                            return result
                        else:
                            # Information loss detected, enhance with fallback
                            print(f"⚠️  Information loss detected in AI response, enhancing...")
                            fallback_result = self._generate_smart_response(user_input)
                            enhanced_result = f"{result}\\n\\n📝 Enhanced context: {fallback_result}"
                            self.add_to_history("assistant", enhanced_result)
                            return enhanced_result
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
        """Generate smart mock response with enhanced context preservation."""
        user_lower = user_input.lower()
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
        
        # Preserve user intent by including their exact request in the response
        # This ensures no information is lost even in fallback mode
        
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
        """Generate response based on capability analysis with preserved user context."""
        user_lower = user_input.lower()
        
        # Create a prefix that includes the user's original request to preserve context
        user_task_prefix = f"Task: '{user_input}'\\n\\n" if len(user_input) < 100 else f"Task: '{user_input[:97]}...'\\n\\n"
        
        # Content generation tasks
        content_keywords = ["write", "generate", "create content", "draft", "letter", "report", "document", 
                           "写", "生成", "创建", "文档", "信件", "报告", "起草"]
        if any(word in user_lower for word in content_keywords):
            if is_chinese:
                if capability.recommendation == "AI":
                    base_msg = "应用选择：0=Word, 1=Excel\\n✅AI优势任务：内容创作"
                    if self.target_model_type == "small":
                        return f"{user_task_prefix}{base_msg}\\n需要详细提示：具体主题、字数要求、格式规范、目标受众"
                    else:
                        return f"{user_task_prefix}{base_msg}\\n简要描述主题和类型即可"
                else:
                    return f"{user_task_prefix}应用选择：0=Word, 1=Excel\\n内容生成→Word，请提供更多细节"
            else:
                if capability.recommendation == "AI":
                    base_msg = "App: 0=Word, 1=Excel\\n✅AI Strength: Content creation"
                    if self.target_model_type == "small":
                        return f"{user_task_prefix}{base_msg}\\nNeed detailed prompt: specific topic, word count, format specs, target audience"
                    else:
                        return f"{user_task_prefix}{base_msg}\\nBrief topic and type description sufficient"
                else:
                    return f"{user_task_prefix}App: 0=Word, 1=Excel\\nContent generation → Word. Provide more details"
        
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
        
        # Default capability-based recommendation with Structured Data Analysis Framework
        if capability.recommendation == "FUZZY_AI":
            if is_chinese:
                return f"""{user_task_prefix}应用选择：0=Word, 1=Excel
🧠 结构化数据分析框架(SDAF)模式：{capability.reason}

📋 请按以下系统化流程进行：

🔍 阶段1：数据发现与评估
- 分析数据格式和结构（Excel、CSV、文本、混合）
- 识别数据类型和不一致性
- 评估复杂程度（简单/中等/复杂/模糊）

🎯 阶段2：处理策略设计  
- 选择处理方法（直接自动化/AI推理/混合方式）
- 制定文本处理策略（结构化/半结构化/非结构化）

⚙️ 阶段3：实施指导
- 读取解析：样本数据，识别边界情况
- 处理转换：应用规则，AI推理处理歧义
- 输出验证：格式化结果，数据完整性检查

📝 阶段4：专门文本处理
- 姓名/联系人：处理各种格式和文化差异
- 地址数据：解析不同格式，处理缩写
- 混合内容：分离结构化和非结构化部分
- 不一致数据：使用上下文线索，模糊匹配

💡 请详细描述：
1. 数据的具体特点和结构
2. 期望的处理结果
3. 遇到的具体问题或挑战

{self._get_domain_specific_guidance(capability.reason, True)}"""
            
            domain_guidance = self._get_domain_specific_guidance(capability.reason, False)
            return f"""{user_task_prefix}App: 0=Word, 1=Excel
🧠 Structured Data Analysis Framework (SDAF) Mode: {capability.reason}

📋 Follow this systematic workflow:

🔍 PHASE 1: Data Discovery & Assessment
- Analyze data format and structure (Excel, CSV, text, mixed)
- Identify data types and inconsistencies
- Assess complexity level (simple/medium/complex/fuzzy)

🎯 PHASE 2: Processing Strategy Design
- Choose processing approach (direct automation/AI reasoning/hybrid)
- Develop text processing strategy (structured/semi-structured/unstructured)

⚙️ PHASE 3: Implementation Guidance  
- Read & Parse: Sample data, identify edge cases
- Process & Transform: Apply rules, use AI reasoning for ambiguity
- Output & Verify: Format results, check data integrity

📝 PHASE 4: Specialized Text Handling
- Name/Contact: Handle various formats and cultural variations
- Address Data: Parse different formats, handle abbreviations  
- Mixed Content: Separate structured and unstructured parts
- Inconsistent Data: Use context clues, fuzzy matching

💡 Please describe in detail:
1. Specific data characteristics and structure
2. Expected processing outcomes
3. Specific problems or challenges encountered

{domain_guidance}"""
        elif capability.recommendation == "AI":
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