"""
Main prompt optimization service combining all AI capabilities.
"""

from typing import Optional, Dict, Any, List
from .capability_analyzer import CapabilityAnalyzer
from ..core.models import CapabilityRecommendation
from ..services.ai_service import AIService


class PromptOptimizer:
    """Main service for optimizing Office automation prompts."""
    
    def __init__(self, target_model_type: str = "big", trust_mode: bool = False):
        self.ai_service = AIService()
        self.analyzer = CapabilityAnalyzer()
        self.target_model_type = target_model_type
        self.trust_mode = trust_mode  # When True, trust big models and minimize optimization
        self.conversation_history: List[Dict[str, str]] = []
        
        # Pre-planned templates for different task types
        self.task_templates = self._initialize_task_templates()
        
        # Target model capabilities
        self.model_types = {
            "big": {
                "name": "Big Model (GPT-4, Claude-3.5, etc.)",
                "prompt_style": "comprehensive, detailed, information-preserving",
                "max_detail": "maximum",
                "context_preservation": "full",
                "information_loss_tolerance": "zero"
            },
            "small": {
                "name": "Small Model (7B, 13B models, etc.)",
                "prompt_style": "detailed, step-by-step, explicit instructions", 
                "max_detail": "high",
                "context_preservation": "essential",
                "information_loss_tolerance": "minimal"
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
    
    def _analyze_hybrid_task(self, user_input: str, capability: 'CapabilityRecommendation', is_chinese: bool) -> str:
        """Provide intelligent analysis for hybrid tasks instead of asking for more details."""
        user_lower = user_input.lower()
        user_task_prefix = f"Task: '{user_input}'\\n\\n" if len(user_input) < 100 else f"Task: '{user_input[:97]}...'\\n\\n"
        
        # Analyze task complexity and provide specific recommendations
        data_volume_indicators = ["批量", "多个", "所有", "全部", "batch", "multiple", "all", "bulk"]
        has_volume = any(indicator in user_lower for indicator in data_volume_indicators)
        
        precision_indicators = ["精确", "准确", "一致", "标准化", "precise", "accurate", "consistent", "standardize"]
        needs_precision = any(indicator in user_lower for indicator in precision_indicators)
        
        content_indicators = ["内容", "文本", "信息", "描述", "content", "text", "information", "description"]
        has_content_work = any(indicator in user_lower for indicator in content_indicators)
        
        extraction_indicators = ["提取", "抽取", "获取", "分离", "extract", "parse", "separate", "split"]
        needs_extraction = any(indicator in user_lower for indicator in extraction_indicators)
        
        # Make intelligent decision based on task characteristics
        if has_volume and needs_precision:
            # High volume + precision = VBA preferred
            recommendation = "VBA"
            reason = "批量精确处理" if is_chinese else "batch precision processing"
        elif has_content_work and not needs_extraction:
            # Content work without extraction = AI preferred  
            recommendation = "AI"
            reason = "内容理解处理" if is_chinese else "content understanding processing"
        elif needs_extraction and has_volume:
            # Extraction + volume = Hybrid approach
            recommendation = "HYBRID_STRUCTURED"
            reason = "结构化提取处理" if is_chinese else "structured extraction processing"
        else:
            # Default to AI for ambiguous cases
            recommendation = "AI"
            reason = "智能分析处理" if is_chinese else "intelligent analysis processing"
        
        if is_chinese:
            if recommendation == "VBA":
                return f"""{user_task_prefix}应用选择：0=Word, 1=Excel
🔧 推荐方案：VBA自动化处理
📊 分析结果：{reason}

💡 理由分析：
- 任务涉及大量数据或需要精确操作
- VBA能提供可靠的批量处理能力
- 适合标准化、重复性操作

🎯 实施建议：
1. 使用VBA宏进行批量自动化
2. 设计错误处理和验证机制
3. 确保数据一致性和准确性

具体实现：基于任务特点设计VBA解决方案"""
            
            elif recommendation == "AI":
                return f"""{user_task_prefix}应用选择：0=Word, 1=Excel
✅ 推荐方案：AI智能处理
🧠 分析结果：{reason}

💡 理由分析：
- 任务需要内容理解或上下文分析
- AI能处理复杂的语义和逻辑关系
- 适合灵活性和适应性要求高的场景

🎯 实施建议：
1. 利用AI的自然语言理解能力
2. 结合上下文进行智能判断
3. 处理不规则或变化的数据格式

具体实现：设计AI辅助的智能处理流程"""
            
            else:  # HYBRID_STRUCTURED
                return f"""{user_task_prefix}应用选择：0=Word, 1=Excel
🔀 推荐方案：AI+VBA混合处理
⚙️ 分析结果：{reason}

💡 理由分析：
- 任务同时需要智能理解和批量处理
- AI负责复杂分析，VBA负责执行操作
- 结合两者优势实现最佳效果

🎯 实施建议：
1. AI部分：理解内容、识别模式、处理异常
2. VBA部分：批量操作、数据转换、格式化
3. 协同工作：AI分析结果指导VBA执行

具体实现：设计AI分析+VBA执行的协同方案"""
        
        else:  # English
            if recommendation == "VBA":
                return f"""{user_task_prefix}App: 0=Word, 1=Excel
🔧 Recommended Solution: VBA Automation
📊 Analysis Result: {reason}

💡 Reasoning:
- Task involves high volume or requires precise operations
- VBA provides reliable batch processing capabilities
- Suitable for standardized, repetitive operations

🎯 Implementation Approach:
1. Use VBA macros for batch automation
2. Design error handling and validation mechanisms
3. Ensure data consistency and accuracy

Specific Implementation: Design VBA solution based on task characteristics"""
            
            elif recommendation == "AI":
                return f"""{user_task_prefix}App: 0=Word, 1=Excel
✅ Recommended Solution: AI Intelligence Processing
🧠 Analysis Result: {reason}

💡 Reasoning:
- Task requires content understanding or contextual analysis
- AI can handle complex semantic and logical relationships
- Suitable for scenarios requiring high flexibility and adaptability

🎯 Implementation Approach:
1. Leverage AI's natural language understanding capabilities
2. Combine context for intelligent judgment
3. Handle irregular or variable data formats

Specific Implementation: Design AI-assisted intelligent processing workflow"""
            
            else:  # HYBRID_STRUCTURED
                return f"""{user_task_prefix}App: 0=Word, 1=Excel
🔀 Recommended Solution: AI+VBA Hybrid Processing
⚙️ Analysis Result: {reason}

💡 Reasoning:
- Task requires both intelligent understanding and batch processing
- AI handles complex analysis, VBA handles execution
- Combines advantages of both approaches for optimal results

🎯 Implementation Approach:
1. AI Component: Understand content, identify patterns, handle exceptions
2. VBA Component: Batch operations, data transformation, formatting
3. Collaborative Work: AI analysis guides VBA execution

Specific Implementation: Design collaborative AI analysis + VBA execution solution"""
    
    def _evaluate_trust_mode(self, user_input: str) -> Dict[str, str]:
        """Evaluate whether to trust big model, pass through, or ask clarifying questions."""
        user_lower = user_input.lower()
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
        
        # Check if request is clear and complete
        completeness_indicators = {
            "has_clear_action": any(word in user_lower for word in [
                "create", "generate", "extract", "format", "calculate", "convert", "analyze",
                "创建", "生成", "提取", "格式化", "计算", "转换", "分析", "制作", "处理"
            ]),
            "has_target_object": any(word in user_lower for word in [
                "table", "document", "file", "data", "report", "chart", "list",
                "表格", "文档", "文件", "数据", "报告", "图表", "列表", "内容"
            ]),
            "has_specific_details": len(user_input.split()) > 5,  # More than 5 words suggests detail
            "has_context": len(self.conversation_history) > 2  # Has conversation context
        }
        
        completeness_score = sum(completeness_indicators.values())
        
        # Check for ambiguity indicators
        ambiguity_indicators = [
            "help", "assist", "什么", "如何", "怎么", "帮助", "协助",
            "best way", "最好的", "最佳", "建议", "recommend", "suggest"
        ]
        has_ambiguity = any(indicator in user_lower for indicator in ambiguity_indicators)
        
        # Check for missing critical information
        missing_info_patterns = {
            "vague_object": any(word in user_lower for word in ["this", "that", "它", "这个", "那个"]) and not completeness_indicators["has_target_object"],
            "unclear_scope": any(word in user_lower for word in ["some", "few", "several", "一些", "几个", "部分"]),
            "missing_format": "format" in user_lower or "格式" in user_lower and not any(fmt in user_lower for fmt in ["xlsx", "docx", "pdf", "csv", "txt"]),
            "missing_location": any(word in user_lower for word in ["where", "哪里", "位置"]) and not any(loc in user_lower for loc in ["column", "row", "cell", "列", "行", "单元格"])
        }
        
        has_missing_info = any(missing_info_patterns.values())
        
        # Decision logic
        if completeness_score >= 3 and not has_ambiguity and not has_missing_info:
            # Clear, complete request - trust the big model
            return {"action": "pass_through"}
        
        elif has_ambiguity or has_missing_info:
            # Generate intelligent clarifying questions
            questions = self._generate_clarifying_questions(user_input, missing_info_patterns, is_chinese)
            return {"action": "clarify", "response": questions}
        
        else:
            # Moderate clarity - trust big model but with context
            return {"action": "pass_through"}
    
    def _generate_clarifying_questions(self, user_input: str, missing_patterns: Dict[str, bool], is_chinese: bool) -> str:
        """Generate intelligent clarifying questions to improve the prompt."""
        questions = []
        
        if missing_patterns.get("vague_object"):
            if is_chinese:
                questions.append("🎯 请明确具体的操作对象（如：哪个表格、文档或数据集）")
            else:
                questions.append("🎯 Please specify the exact object (e.g., which table, document, or dataset)")
        
        if missing_patterns.get("unclear_scope"):
            if is_chinese:
                questions.append("📊 请说明处理范围（如：所有数据、特定条件的数据、还是样例数据）")
            else:
                questions.append("📊 Please clarify the scope (e.g., all data, data meeting specific conditions, or sample data)")
        
        if missing_patterns.get("missing_format"):
            if is_chinese:
                questions.append("📄 请指定输出格式或文件类型（如：Excel、Word、PDF等）")
            else:
                questions.append("📄 Please specify output format or file type (e.g., Excel, Word, PDF, etc.)")
        
        if missing_patterns.get("missing_location"):
            if is_chinese:
                questions.append("📍 请明确数据位置或目标位置（如：具体列名、行号、单元格范围）")
            else:
                questions.append("📍 Please specify data location or target location (e.g., specific column names, row numbers, cell ranges)")
        
        # If no specific missing patterns detected, ask general clarifying questions
        if not questions:
            if is_chinese:
                questions.append("💡 为了提供最准确的解决方案，请补充：\n- 具体的操作目标和期望结果\n- 数据的来源和格式\n- 任何特殊要求或限制条件")
            else:
                questions.append("💡 To provide the most accurate solution, please add:\n- Specific operation goals and expected results\n- Data source and format\n- Any special requirements or constraints")
        
        # Format the response
        task_summary = f"Task: '{user_input}'\n\n" if len(user_input) < 100 else f"Task: '{user_input[:97]}...'\n\n"
        
        if is_chinese:
            header = f"{task_summary}🤔 为了更好地协助您，需要澄清以下信息：\n\n"
            footer = "\n\n✨ 提供这些细节后，我可以为您设计最优的解决方案！"
        else:
            header = f"{task_summary}🤔 To better assist you, I need to clarify the following:\n\n"
            footer = "\n\n✨ Once you provide these details, I can design the optimal solution for you!"
        
        return header + "\n".join(questions) + footer
    
    def _initialize_task_templates(self) -> Dict[str, Dict]:
        """Initialize pre-planned templates for different task types."""
        return {
            "data_extraction": {
                "chinese": {
                    "title": "数据提取任务模板",
                    "structure": """
应用选择：{app_selection}

📋 数据提取执行计划：

🎯 任务目标：
- 源数据：{source_data}
- 目标字段：{target_fields}
- 提取条件：{extraction_conditions}

⚙️ 执行步骤：
1. 数据识别和验证
   - 检查源数据格式和完整性
   - 确认字段位置和数据类型
   
2. 提取逻辑实现
   - {extraction_method}
   - 处理边界情况和异常值
   
3. 结果验证和输出
   - 验证提取结果的准确性
   - 格式化并保存到目标位置

💡 技术实现：
{technical_implementation}

✅ 验证检查：
- 提取数量是否正确
- 数据格式是否一致
- 是否有遗漏或错误
""",
                    "placeholders": {
                        "app_selection": "0=Word, 1=Excel",
                        "source_data": "[请填写源数据位置和格式]",
                        "target_fields": "[请填写目标字段名称]", 
                        "extraction_conditions": "[请填写提取条件]",
                        "extraction_method": "[请填写具体提取方法]",
                        "technical_implementation": "[请填写技术实现方案]"
                    }
                },
                "english": {
                    "title": "Data Extraction Task Template",
                    "structure": """
App Selection: {app_selection}

📋 Data Extraction Execution Plan:

🎯 Task Objective:
- Source Data: {source_data}
- Target Fields: {target_fields}
- Extraction Conditions: {extraction_conditions}

⚙️ Execution Steps:
1. Data Identification and Validation
   - Check source data format and completeness
   - Confirm field positions and data types
   
2. Extraction Logic Implementation
   - {extraction_method}
   - Handle edge cases and outliers
   
3. Result Validation and Output
   - Validate extraction accuracy
   - Format and save to target location

💡 Technical Implementation:
{technical_implementation}

✅ Validation Checks:
- Is extraction count correct?
- Is data format consistent?
- Any missing or erroneous data?
"""
                }
            },
            
            "content_generation": {
                "chinese": {
                    "title": "内容生成任务模板",
                    "structure": """
应用选择：{app_selection}

📋 内容生成执行计划：

🎯 内容要求：
- 内容类型：{content_type}
- 目标受众：{target_audience}
- 字数要求：{word_count}
- 风格要求：{style_requirements}

⚙️ 生成结构：
1. 内容框架设计
   - 主要章节：{main_sections}
   - 逻辑顺序：{logical_order}
   
2. 内容创作执行
   - {content_creation_method}
   - 确保信息准确性和连贯性
   
3. 格式化和美化
   - 应用适当的格式和样式
   - 添加必要的图表或视觉元素

💡 创作指导：
{creation_guidance}

✅ 质量检查：
- 内容是否符合要求
- 逻辑是否清晰连贯
- 格式是否规范美观
""",
                    "placeholders": {
                        "app_selection": "0=Word, 1=Excel",
                        "content_type": "[请填写内容类型]",
                        "target_audience": "[请填写目标受众]",
                        "word_count": "[请填写字数要求]",
                        "style_requirements": "[请填写风格要求]",
                        "main_sections": "[请填写主要章节]",
                        "logical_order": "[请填写逻辑顺序]",
                        "content_creation_method": "[请填写创作方法]",
                        "creation_guidance": "[请填写创作指导]"
                    }
                }
            },
            
            "data_processing": {
                "chinese": {
                    "title": "数据处理任务模板", 
                    "structure": """
应用选择：{app_selection}

📋 数据处理执行计划：

🎯 处理目标：
- 输入数据：{input_data}
- 处理操作：{processing_operations}
- 输出要求：{output_requirements}

⚙️ 处理流程：
1. 数据预处理
   - 数据清洗：{data_cleaning}
   - 格式标准化：{format_standardization}
   
2. 核心处理逻辑
   - {core_processing_logic}
   - 错误处理和异常情况
   
3. 结果整理和验证
   - 数据验证和质量检查
   - 格式化输出结果

💡 技术方案：
{technical_solution}

✅ 验证标准：
- 数据完整性检查
- 处理结果准确性
- 输出格式符合要求
""",
                    "placeholders": {
                        "app_selection": "0=Word, 1=Excel",
                        "input_data": "[请填写输入数据描述]",
                        "processing_operations": "[请填写处理操作]",
                        "output_requirements": "[请填写输出要求]",
                        "data_cleaning": "[请填写数据清洗方法]",
                        "format_standardization": "[请填写格式标准化]",
                        "core_processing_logic": "[请填写核心处理逻辑]",
                        "technical_solution": "[请填写技术方案]"
                    }
                }
            },
            
            "automation_task": {
                "chinese": {
                    "title": "自动化任务模板",
                    "structure": """
应用选择：{app_selection}

📋 自动化执行计划：

🎯 自动化目标：
- 重复操作：{repetitive_operations}
- 触发条件：{trigger_conditions}
- 执行频率：{execution_frequency}

⚙️ 自动化流程：
1. 触发条件检测
   - 条件监控：{condition_monitoring}
   - 触发判断逻辑：{trigger_logic}
   
2. 自动化执行
   - {automation_execution}
   - 错误处理和重试机制
   
3. 结果反馈和日志
   - 执行状态记录
   - 结果通知和报告

💡 实现方案：
{implementation_plan}

✅ 监控指标：
- 执行成功率
- 处理时间效率
- 错误类型和频率
""",
                    "placeholders": {
                        "app_selection": "0=Word, 1=Excel",
                        "repetitive_operations": "[请填写重复操作内容]",
                        "trigger_conditions": "[请填写触发条件]",
                        "execution_frequency": "[请填写执行频率]",
                        "condition_monitoring": "[请填写条件监控方法]",
                        "trigger_logic": "[请填写触发判断逻辑]",
                        "automation_execution": "[请填写自动化执行步骤]",
                        "implementation_plan": "[请填写实现方案]"
                    }
                }
            }
        }
    
    def _select_and_fill_template(self, user_input: str, task_type: str, is_chinese: bool) -> str:
        """Select appropriate template and guide AI to fill in the content."""
        lang = "chinese" if is_chinese else "english"
        template_data = self.task_templates.get(task_type, {}).get(lang, {})
        
        if not template_data:
            # Fallback to generic template
            return self._generate_generic_template(user_input, is_chinese)
        
        # Create a prompt that guides AI to fill the template with strict adherence to original text
        if is_chinese:
            fill_prompt = f"""
你是一个Office自动化专家。

📋 原始用户请求（这是绝对准确的依据）：
"{user_input}"

📋 预设模板结构：
{template_data['title']}

{template_data['structure']}

🚨 重要指示：
1. 原始用户请求是唯一权威依据，所有内容必须严格基于原文
2. 如果模板内容与原文发生任何冲突，必须以原文为准
3. 填写模板时，直接使用原文中的确切用词和表述
4. 保持原文中的所有技术术语、字段名、表名等不变
5. 不要添加原文中没有的信息，不要修改原文的表达方式

⚙️ 填写要求：
- 将模板中的占位符 {{变量}} 替换为基于原文的具体内容
- 如果原文信息不足以填写某个占位符，标注"[原文未明确指定]"
- 保持模板的整体结构和格式
- 确保与原文完全一致

请严格按照原文内容填写模板：
"""
        else:
            fill_prompt = f"""
You are an Office automation expert.

📋 Original User Request (This is the absolute authoritative source):
"{user_input}"

📋 Predefined Template Structure:
{template_data['title']}

{template_data['structure']}

🚨 Critical Instructions:
1. The original user request is the only authoritative source - all content must strictly follow the original text
2. If there's any conflict between template content and original text, the original text takes precedence
3. When filling the template, use exact wording and expressions from the original text
4. Keep all technical terms, field names, table names, etc. unchanged from the original
5. Do not add information not present in the original text, do not modify the original expressions

⚙️ Filling Requirements:
- Replace template placeholders {{variables}} with specific content based on the original text
- If original text lacks information for a placeholder, mark as "[Not specified in original]"
- Maintain the overall template structure and format
- Ensure complete consistency with the original text

Please fill the template strictly according to the original text content:
"""
        
        return fill_prompt
    
    def _generate_generic_template(self, user_input: str, is_chinese: bool) -> str:
        """Generate a generic template when no specific template matches."""
        if is_chinese:
            return f"""
📋 原始用户请求（绝对权威依据）：
"{user_input}"

应用选择：0=Word, 1=Excel

📋 任务执行计划：

🚨 重要：严格按照原文内容填写，不得偏离原文表述

🎯 目标分析（基于原文）：
- 具体需求：[直接引用原文中的需求描述，保持原文用词]
- 期望结果：[基于原文推断的预期结果，使用原文术语]

⚙️ 执行步骤（按原文逻辑）：
1. 准备阶段
   - [基于原文确定的准备工作，保持原文中的对象名称]
   
2. 执行阶段  
   - [严格按照原文描述的操作步骤，使用原文的确切表述]
   
3. 验证阶段
   - [基于原文要求的验证方法]

💡 实现建议（忠于原文）：
[提供与原文完全一致的实现方案，保持所有技术术语不变]

✅ 成功标准（原文标准）：
- [根据原文定义的完成标准，不添加额外要求]

⚠️ 填写原则：
1. 所有内容必须基于原文
2. 保持原文中的确切用词
3. 不添加原文未提及的信息
4. 如信息不足，标注"[原文未明确]"
"""
        else:
            return f"""
📋 Original User Request (Absolute Authority):
"{user_input}"

App Selection: 0=Word, 1=Excel

📋 Task Execution Plan:

🚨 Important: Fill strictly according to original text, no deviation from original expressions

🎯 Objective Analysis (Based on Original):
- Specific Requirements: [Quote requirement descriptions directly from original text, maintain original wording]
- Expected Results: [Expected outcomes inferred from original text, using original terminology]

⚙️ Execution Steps (Following Original Logic):
1. Preparation Phase
   - [Preparation work determined from original text, maintain object names from original]
   
2. Execution Phase
   - [Strictly follow operation steps described in original text, use exact original expressions]
   
3. Validation Phase
   - [Validation methods based on original requirements]

💡 Implementation Suggestions (Faithful to Original):
[Provide implementation plans completely consistent with original text, maintain all technical terms unchanged]

✅ Success Criteria (Original Standards):
- [Completion standards defined according to original text, no additional requirements]

⚠️ Filling Principles:
1. All content must be based on original text
2. Maintain exact wording from original
3. Do not add information not mentioned in original
4. If information insufficient, mark "[Not specified in original]"
"""
    
    def _classify_task_type(self, user_input: str) -> str:
        """Classify user input into predefined task types for template selection."""
        user_lower = user_input.lower()
        
        # Data extraction patterns
        extraction_patterns = [
            "提取", "抽取", "获取", "分离", "extract", "parse", "get", "retrieve", 
            "split", "separate", "pull out", "拆分", "分解"
        ]
        
        # Content generation patterns  
        content_patterns = [
            "写", "创建", "生成", "制作", "编写", "起草", "write", "create", "generate", 
            "draft", "compose", "produce", "文档", "报告", "信件", "document", "report", "letter"
        ]
        
        # Data processing patterns
        processing_patterns = [
            "处理", "转换", "格式化", "清洗", "标准化", "process", "convert", "format", 
            "clean", "normalize", "transform", "计算", "统计", "分析", "calculate", "analyze"
        ]
        
        # Automation patterns
        automation_patterns = [
            "自动化", "批量", "重复", "定时", "automate", "batch", "bulk", "repeat", 
            "schedule", "macro", "宏", "脚本", "script"
        ]
        
        # Score each category
        scores = {
            "data_extraction": sum(1 for pattern in extraction_patterns if pattern in user_lower),
            "content_generation": sum(1 for pattern in content_patterns if pattern in user_lower), 
            "data_processing": sum(1 for pattern in processing_patterns if pattern in user_lower),
            "automation_task": sum(1 for pattern in automation_patterns if pattern in user_lower)
        }
        
        # Return highest scoring category, or None if no clear match
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return "generic"  # Fallback to generic template
    
    async def _handle_app_selection(self, app_selection: str) -> str:
        """Handle app selection (0/1) with template processing."""
        app_name = "Word" if app_selection == '0' else "Excel"
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in '\u4e00')  # Default check
        
        # Extract previous task from conversation history
        previous_task = self._extract_previous_task_context()
        if not previous_task:
            # No previous context, fall back to generic response
            if is_chinese:
                return f"✅ 已选择{app_name}\n\n请详细描述你要完成的具体任务：\n- 数据操作请描述具体步骤\n- 内容创作请说明主题和要求\n- 格式调整请明确目标样式"
            return f"✅ Selected {app_name}\n\nPlease describe your specific task in detail:\n- For data operations: describe specific steps\n- For content creation: specify topic and requirements\n- For formatting: clarify target style"
        
        # Determine if previous task was in Chinese
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in previous_task)
        
        # Create AI prompt to generate complete solution directly
        ai_prompt = self._create_solution_prompt(previous_task, app_name, is_chinese)
        
        # Try to have AI generate the complete solution
        try:
            if self.ai_service.is_available():
                ai_solution = await self.ai_service.process_message(ai_prompt)
                if ai_solution and len(ai_solution.strip()) > 50:  # Ensure we got a substantial response
                    return f"✅ 已选择{app_name}\n\n{ai_solution}" if is_chinese else f"✅ Selected {app_name}\n\n{ai_solution}"
        except Exception as e:
            print(f"AI solution generation error: {e}")
        
        # Fallback to template-based approach if AI fails
        task_type = self._classify_task_type(previous_task)
        if task_type in self.task_templates:
            template_response = self._select_and_fill_template_with_app(previous_task, task_type, app_selection, is_chinese)
            return f"✅ 已选择{app_name}\n\n{template_response}" if is_chinese else f"✅ Selected {app_name}\n\n{template_response}"
        else:
            generic_template = self._generate_generic_template_with_app(previous_task, app_selection, is_chinese)
            return f"✅ 已选择{app_name}\n\n{generic_template}" if is_chinese else f"✅ Selected {app_name}\n\n{generic_template}"
    
    def _create_solution_prompt(self, user_task: str, app_name: str, is_chinese: bool) -> str:
        """Create a focused AI prompt to generate complete solution directly."""
        if is_chinese:
            return f"""用户任务：{user_task}
目标应用：{app_name}

请直接生成完整的可执行解决方案，包括：
1. 具体的操作步骤（详细说明每一步如何在{app_name}中执行）
2. 需要的公式或代码（如果涉及数据处理，提供完整的Excel公式或VBA代码）
3. 实际示例（基于用户任务的具体示例）
4. 注意事项和验证方法

要求：
- 直接提供可操作的解决方案，不要只是框架或模板
- 保持原文中的所有关键信息（表名、字段名、术语等）
- 提供具体的实现细节，不要抽象描述
- 如果是数据处理任务，必须包含具体的Excel公式

请现在就生成完整的解决方案："""
        else:
            return f"""User Task: {user_task}
Target Application: {app_name}

Please generate a complete executable solution directly, including:
1. Specific operational steps (detailed instructions for each step in {app_name})
2. Required formulas or code (if data processing is involved, provide complete Excel formulas or VBA code)
3. Practical examples (specific examples based on the user's task)
4. Important notes and validation methods

Requirements:
- Provide directly actionable solutions, not just frameworks or templates
- Preserve all key information from the original text (table names, field names, terminology, etc.)
- Include specific implementation details, not abstract descriptions
- If it's a data processing task, must include specific Excel formulas

Please generate the complete solution now:"""
    
    def _extract_previous_task_context(self) -> str:
        """Extract the original task from conversation history when user selects app."""
        if len(self.conversation_history) < 2:
            return ""
        
        # Look for the most recent substantive user request (not app selection)
        for msg in reversed(self.conversation_history):
            if msg['role'] == 'user' and msg['content'].strip() not in ['0', '1', '/c', '/clear', '/mb', '/ms', '/model-big', '/model-small']:
                return msg['content']
        
        return ""
    
    def _select_and_fill_template_with_app(self, user_input: str, task_type: str, app_selection: str, is_chinese: bool) -> str:
        """Create template with app selection already filled in."""
        lang = "chinese" if is_chinese else "english"
        template_data = self.task_templates.get(task_type, {}).get(lang, {})
        
        if not template_data:
            return self._generate_generic_template_with_app(user_input, app_selection, is_chinese)
        
        # Fill the app_selection in the template structure
        filled_structure = template_data['structure'].replace('{app_selection}', f"{app_selection}={'Word' if app_selection == '0' else 'Excel'}")
        
        if is_chinese:
            return f"""基于您的原始需求，已为您准备执行模板：

📋 原始需求（权威依据）："{user_input}"

📋 {template_data['title']}

{filled_structure}

🚨 智能填写指示：
- 基于原始需求，运用AI能力智能推断和补充细节
- 保持原文中的确切用词和技术术语不变
- 对于原文未明确的信息，提供合理的业务逻辑推断
- 生成可直接执行的完整方案，包括具体的公式和步骤

💡 AI处理方式：
- 理解业务场景：客户管理系统的财务汇总需求
- 推断数据结构：基于常见的客户、合同、收款表结构
- 生成实用方案：提供Excel公式或VBA代码实现
- 包含完整说明：从准备到验证的全过程

请运用AI的自然语言理解能力，直接生成完整可执行的解决方案："""
        else:
            return f"""Based on your original request, execution template prepared:

📋 Original Request (Authoritative Source): "{user_input}"

📋 {template_data['title']}

{filled_structure}

🚨 Intelligent Processing Instructions:
- Based on original request, use AI capabilities to intelligently infer and supplement details
- Maintain exact wording and technical terms from original unchanged
- For information not explicitly stated, provide reasonable business logic inferences
- Generate directly executable complete solution including specific formulas and steps

💡 AI Processing Approach:
- Understand business scenario: Customer management system financial summary requirements
- Infer data structures: Based on common customer, contract, payment table structures
- Generate practical solution: Provide Excel formulas or VBA code implementation
- Include complete instructions: Full process from preparation to validation

Please use AI's natural language understanding capabilities to directly generate a complete executable solution:"""
    
    def _generate_generic_template_with_app(self, user_input: str, app_selection: str, is_chinese: bool) -> str:
        """Generate generic template with app already selected."""
        app_name = "Word" if app_selection == "0" else "Excel"
        
        if is_chinese:
            return f"""基于您的原始需求："{user_input}"

📋 任务执行计划（{app_name}）

🎯 目标分析（基于原文）：
- 具体需求：[直接引用原文需求，保持原文用词]
- 期望结果：[基于原文的预期结果]

⚙️ 执行步骤：
1. 准备阶段
   - [基于原文的准备工作]
   
2. 执行阶段
   - [严格按原文的操作步骤]
   
3. 验证阶段
   - [原文要求的验证方法]

💡 AI智能实现方案：
请基于业务常识和Excel最佳实践，生成包含以下内容的完整方案：
- 具体的Excel公式（如SUMIF、VLOOKUP等）
- 详细的操作步骤说明
- 数据验证和测试方法
- 可能遇到的问题及解决方案

🎯 期望输出：直接可用的Excel解决方案，无需用户再次提供技术细节"""
        else:
            return f"""Based on your original request: "{user_input}"

📋 Task Execution Plan ({app_name})

🎯 Objective Analysis (Based on Original):
- Specific Requirements: [Quote directly from original, maintain original wording]
- Expected Results: [Expected outcomes from original]

⚙️ Execution Steps:
1. Preparation Phase
   - [Preparation work based on original]
   
2. Execution Phase
   - [Operation steps strictly from original]
   
3. Validation Phase
   - [Validation methods required by original]

💡 AI Intelligent Implementation Plan:
Please generate a complete solution based on business common sense and Excel best practices, including:
- Specific Excel formulas (such as SUMIF, VLOOKUP, etc.)
- Detailed operational step-by-step instructions  
- Data validation and testing methods
- Potential issues and solutions

🎯 Expected Output: Directly usable Excel solution without requiring users to provide additional technical details"""
    
    async def _pass_through_to_ai(self, user_input: str) -> str:
        """Pass user input directly to AI with minimal optimization, trusting big model capabilities."""
        # Create minimal context
        context = ""
        if len(self.conversation_history) > 1:
            context = "\nPrevious conversation:\n"
            # Only use last 3 messages to keep it minimal
            for msg in self.conversation_history[-3:]:
                context += f"{msg['role']}: {msg['content']}\n"
        
        # Minimal prompt for big model
        minimal_prompt = f"""You are an expert Office automation assistant.

User Request: {user_input}
{context}
App Selection: Use "0=Word, 1=Excel" format

Provide a comprehensive, practical solution. Use your full capabilities to understand the request and deliver the best approach."""
        
        # Try AI service
        if self.ai_service.is_available():
            try:
                result = await self.ai_service.process_message(minimal_prompt)
                if result:
                    self.add_to_history("assistant", result)
                    return result
            except Exception as ai_error:
                print(f"⚠️  AI service error in trust mode: {ai_error}")
        
        # Fallback with trust mode acknowledgment
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
        if is_chinese:
            return f"Task: '{user_input}'\n\n🤖 AI服务暂时不可用，但您的请求已记录。\n应用选择：0=Word, 1=Excel\n\n请选择应用程序继续操作。"
        else:
            return f"Task: '{user_input}'\n\n🤖 AI service temporarily unavailable, but your request is recorded.\nApp: 0=Word, 1=Excel\n\nPlease select the application to continue."
    
    def _validate_information_preservation(self, original_input: str, optimized_response: str) -> bool:
        """Validate that optimized response preserves core information from original input."""
        original_lower = original_input.lower()
        response_lower = optimized_response.lower()
        
        # Extract key elements from original input with enhanced detection
        key_elements = []
        
        # Check for specific tools/applications mentioned
        apps = ["word", "excel", "powerpoint", "office", "文档", "表格", "演示"]
        mentioned_apps = [app for app in apps if app in original_lower]
        key_elements.extend(mentioned_apps)
        
        # Check for action verbs (what user wants to do)
        actions = ["create", "generate", "write", "format", "calculate", "extract", "split", "convert", 
                  "automate", "batch", "process", "analyze", "add", "增加", "创建", "生成", "写", "格式", "计算", "提取", 
                  "拆分", "转换", "自动化", "批处理", "处理", "分析", "填入", "填充"]
        mentioned_actions = [action for action in actions if action in original_lower]
        key_elements.extend(mentioned_actions)
        
        # Check for specific data types or objects
        objects = ["table", "chart", "document", "file", "data", "text", "number", "date", "image", 
                  "表格", "图表", "文档", "文件", "数据", "文本", "数字", "日期", "图片", "字段", "列", "行"]
        mentioned_objects = [obj for obj in objects if obj in original_lower]
        key_elements.extend(mentioned_objects)
        
        # Enhanced detection for business-specific terms
        business_terms = ["客户", "customer", "省", "市", "province", "city", "地址", "address", "详细", "detailed"]
        mentioned_business = [term for term in business_terms if term in original_lower]
        key_elements.extend(mentioned_business)
        
        # Check for field names and technical specifications (quoted strings)
        import re
        quoted_terms = re.findall(r'[""\'](.*?)[""\'"]', original_input)
        key_elements.extend([term.lower() for term in quoted_terms])
        
        # Check for specific database/table terminology
        db_terms = ["表", "table", "字段", "field", "列", "column", "行", "row", "数据库", "database"]
        mentioned_db = [term for term in db_terms if term in original_lower]
        key_elements.extend(mentioned_db)
        
        # Check preservation rate with different thresholds for different model types
        if not key_elements:
            return True  # No specific elements to validate
            
        preserved_count = sum(1 for element in key_elements if element in response_lower)
        preservation_rate = preserved_count / len(key_elements)
        
        # Big models require much higher preservation rate (95%), small models require 70%
        if self.target_model_type == "big":
            required_rate = 0.95  # 95% preservation for big models
        else:
            required_rate = 0.70  # 70% preservation for small models
        
        return preservation_rate >= required_rate
    
    def _validate_template_fidelity(self, original_input: str, template_response: str) -> bool:
        """Validate that template response maintains fidelity to original user input."""
        original_lower = original_input.lower()
        response_lower = template_response.lower()
        
        # Extract quoted strings and technical terms from original
        import re
        quoted_terms = re.findall(r'[""\'](.*?)[""\'"]', original_input)
        
        # Check if all quoted terms are preserved
        for term in quoted_terms:
            if term.lower() not in response_lower:
                return False
        
        # Check for critical business terms preservation
        critical_terms = []
        
        # Extract table/object names (Chinese patterns)
        table_patterns = re.findall(r'(\w*表\w*)', original_input)
        critical_terms.extend(table_patterns)
        
        # Extract field/column names (Chinese patterns)
        field_patterns = re.findall(r'(\w*字段\w*)', original_input)
        critical_terms.extend(field_patterns)
        
        # Check preservation of critical terms
        for term in critical_terms:
            if term and term.lower() not in response_lower:
                return False
        
        # For template responses, require higher fidelity (90%)
        return self._validate_information_preservation(original_input, template_response)
    
    def _add_original_text_reminder(self, original_input: str, ai_response: str, is_chinese: bool) -> str:
        """Add original text reminder when template response may have deviated."""
        if is_chinese:
            reminder = f"""
{ai_response}

🚨 重要提醒：请严格参考原始需求
原始需求："{original_input}"

如果上述回复与您的原始需求有任何不符，请以您的原始需求为准。所有表名、字段名、操作步骤都应该严格按照您提供的原始描述执行。
"""
        else:
            reminder = f"""
{ai_response}

🚨 Important Reminder: Please strictly refer to original requirements
Original Request: "{original_input}"

If the above response has any inconsistency with your original requirements, please follow your original requirements. All table names, field names, and operation steps should strictly follow your original description.
"""
        
        return reminder
    
    def get_capability_recommendation(self, user_input: str) -> CapabilityRecommendation:
        """Get AI vs VBA capability recommendation for the task."""
        return self.analyzer.analyze_task(user_input)
    
    async def optimize_prompt(self, user_input: str) -> str:
        """Main optimization method that returns the best response."""
        try:
            # Add user input to history
            self.add_to_history("user", user_input)
            
            # For big models in trust mode, check if we should pass through or ask clarifying questions
            if self.target_model_type == "big" and self.trust_mode:
                trust_decision = self._evaluate_trust_mode(user_input)
                if trust_decision["action"] == "pass_through":
                    # Trust the big model - pass through with minimal context
                    return await self._pass_through_to_ai(user_input)
                elif trust_decision["action"] == "clarify":
                    # Ask intelligent clarifying questions
                    return trust_decision["response"]
            
            # Handle app selection responses (0/1) FIRST before any other processing
            if user_input.strip() in ['0', '1']:
                return await self._handle_app_selection(user_input.strip())
            
            # Analyze task capability to determine if it's a fuzzy AI task
            capability = self.get_capability_recommendation(user_input)
            
            # Determine task type and use appropriate template
            task_type = self._classify_task_type(user_input)
            is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
            
            # Use template-driven approach for clear task types
            if task_type in self.task_templates:
                template_prompt = self._select_and_fill_template(user_input, task_type, is_chinese)
                # Pass template to AI for content filling
                if self.ai_service.is_available():
                    try:
                        result = await self.ai_service.process_message(template_prompt)
                        if result:
                            # Enhanced validation specifically for template-based responses
                            if self._validate_template_fidelity(user_input, result):
                                self.add_to_history("assistant", result)
                                return result
                            else:
                                # Original text fidelity failed, enhance with warning
                                print(f"⚠️  Template response may have deviated from original text")
                                enhanced_result = self._add_original_text_reminder(user_input, result, is_chinese)
                                self.add_to_history("assistant", enhanced_result)
                                return enhanced_result
                    except Exception as e:
                        print(f"Template processing error: {e}")
            
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
                # Enhanced prompts for big models with maximum detail preservation
                if self.target_model_type == "big":
                    full_prompt = f"""
You are an advanced OfficeAI assistant with sophisticated analytical capabilities for complex data processing tasks.

🧠 STRUCTURED DATA ANALYSIS FRAMEWORK (SDAF) MODE ACTIVATED - BIG MODEL ENHANCED
Task Type: {capability.reason}
Target Model: {target_model_info['name']}
Information Preservation: {target_model_info['information_loss_tolerance']} loss tolerance
Context Preservation: {target_model_info['context_preservation']} detail level

⚠️ CRITICAL INFORMATION PRESERVATION REQUIREMENTS:
- PRESERVE ALL original terminology, field names, table names, and technical specifications
- MAINTAIN ALL contextual details from user request
- RETAIN ALL conditional logic and processing requirements
- PRESERVE ALL specific data examples and formats mentioned
- KEEP ALL language-specific terms and cultural context
- MAINTAIN ALL business logic and workflow requirements

📋 COMPREHENSIVE SDAF FRAMEWORK FOR BIG MODELS:

🔍 PHASE 1: COMPREHENSIVE DATA DISCOVERY & ASSESSMENT
STEP 1: Detailed Data Structure Analysis
- Examine ALL data formats mentioned: Excel tables, CSV files, text documents, mixed sources
- Identify ALL data types: text fields, numeric columns, date formats, mixed content
- Detect ALL patterns: delimiters, separators, formatting conventions, encoding
- Note ALL inconsistencies: missing values, special characters, formatting variations, edge cases
- Map ALL relationships: primary keys, foreign keys, dependent fields, calculated columns

STEP 2: Multi-Dimensional Complexity Assessment
- SIMPLE: Consistent structure, clean data, standard formats → Direct automation sufficient
- MEDIUM: Some inconsistencies, multiple formats, minor variations → Guided processing needed
- COMPLEX: Mixed structures, messy text, significant variations → AI reasoning required
- FUZZY: Requires interpretation, context understanding, cultural knowledge → Full AI capabilities essential

🎯 PHASE 2: COMPREHENSIVE PROCESSING STRATEGY DESIGN
STEP 3: Multi-Modal Processing Approach Selection
- Direct automation (VBA/formulas/built-in functions) for consistent, structured data
- AI-powered reasoning for inconsistent, contextual, or culturally-dependent data
- Hybrid approach combining automation efficiency with AI intelligence for mixed scenarios
- Custom algorithm development for unique or specialized processing requirements

STEP 4: Advanced Text Processing Strategy Design
COMPREHENSIVE TEXT STRUCTURE HANDLING:
- Structured text → Advanced pattern matching, regex with validation, template-based extraction
- Semi-structured → AI interpretation with rule validation, confidence scoring, exception handling
- Unstructured → Full natural language processing, semantic analysis, contextual understanding
- Mixed formats → Dynamic format detection, adaptive processing pipeline, progressive refinement

⚙️ PHASE 3: DETAILED IMPLEMENTATION GUIDANCE
STEP 5: Systematic Processing Methodology
A. COMPREHENSIVE READ & PARSE:
   1. Sample diverse data sets to understand complete pattern spectrum and edge cases
   2. Identify ALL exception scenarios, outliers, and boundary conditions
   3. Plan comprehensive error handling, logging, and recovery strategies
   4. Design validation checkpoints and quality assurance measures

B. INTELLIGENT PROCESS & TRANSFORM:
   1. Apply consistent automation rules where data structure permits reliable processing
   2. Use advanced AI reasoning for ambiguous, contextual, or culturally-dependent cases
   3. Implement continuous validation with confidence scoring and uncertainty flagging
   4. Handle exceptions gracefully with fallback strategies and manual review workflows

C. COMPREHENSIVE OUTPUT & VERIFY:
   1. Format results with consistent structure while preserving source data integrity
   2. Perform multi-level data integrity checks: syntax, semantics, business logic
   3. Provide detailed processing summary with statistics, confidence levels, and quality metrics
   4. Generate comprehensive audit trail for accountability and debugging

📝 PHASE 4: SPECIALIZED TEXT HANDLING EXPERTISE

FOR NAME/CONTACT DATA (Enhanced for Cultural Sensitivity):
- Handle ALL formats: "姓, 名", "名 姓", "称谓 名 姓, 后缀", international variations
- Process titles, suffixes, special characters, diacritical marks, cultural naming conventions
- Normalize spacing, capitalization, punctuation while preserving cultural authenticity
- Handle multi-language names, transliterations, and phonetic variations

FOR ADDRESS DATA (Enhanced for Geographic Complexity):
- Parse ALL formats: "省市区街道号", "Street, City, State ZIP", international formats
- Handle abbreviations: "省/Province", "市/City", "区/District", "街/Street", "号/Number"
- Extract ALL components: country, province/state, city, district, street, building, unit, postal code
- Manage address hierarchies, administrative divisions, and geographic relationships

FOR MIXED CONTENT (Enhanced for Complex Scenarios):
- Identify ALL content types within single text fields: structured data, free text, codes, references
- Separate structured from unstructured information with precision and context preservation
- Apply appropriate processing methodology to each component while maintaining relationships
- Handle nested structures, embedded formats, and multi-layer encoding

FOR INCONSISTENT DATA (Enhanced AI-Powered Resolution):
- Use advanced contextual clues, semantic analysis, and cultural knowledge to interpret intent
- Apply sophisticated fuzzy matching algorithms with confidence scoring and similarity metrics
- Flag uncertain cases with detailed explanations and suggested manual review priorities
- Provide alternative interpretations and processing options for ambiguous scenarios

🎯 ENHANCED CRITICAL EXECUTION RULES FOR BIG MODELS:
- LANGUAGE: Respond in SAME LANGUAGE as request with full linguistic and cultural preservation
- METHODOLOGY: Follow SDAF phases systematically with comprehensive documentation
- REASONING: Provide detailed analytical process explanation with decision rationale
- PRESERVATION: Maintain ALL original information with {target_model_info['information_loss_tolerance']} loss tolerance
- ADAPTATION: Utilize full big model capabilities for {target_model_info['max_detail']} detail processing
- VALIDATION: Implement multi-level verification with confidence assessment and quality metrics

App Selection Format: "0=Word, 1=Excel"

ORIGINAL USER REQUEST (PRESERVE ALL DETAILS): {user_input}

{context}

{self._get_domain_specific_guidance(capability.reason, any('\u4e00' <= char <= '\u9fff' for char in user_input))}

RESPOND using full SDAF methodology with MAXIMUM detail preservation IN SAME LANGUAGE:"""
                else:
                    # Standard prompt for small models
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
        
        # App selection (0/1) is now handled earlier in optimize_prompt, so this should not be reached
        
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
            # Enhanced HYBRID handling - provide intelligent recommendations instead of asking for more details
            hybrid_analysis = self._analyze_hybrid_task(user_input, capability, is_chinese)
            return hybrid_analysis
        
        # Default fallback
        if is_chinese:
            return f"应用选择：0=Word, 1=Excel\\n任务：'{user_input}'"
        return f"App: 0=Word, 1=Excel\\nTask: '{user_input}'"