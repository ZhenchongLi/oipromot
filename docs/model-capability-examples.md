# Target Model Capability Adaptation

## 🎯 Purpose

The system adapts prompt detail based on the **target AI model** that will receive the optimized prompts:

- **Big Models** (GPT-4, Claude-3.5, etc.) → Brief prompts (good reasoning capabilities)
- **Small Models** (7B, 13B models, etc.) → Detailed prompts (need explicit instructions)

## 🔄 Model Selection Commands

- `/mb` or `/model-big` → Switch to big model mode
- `/ms` or `/model-small` → Switch to small model mode

## 📝 Example Differences

### Content Generation Example

**User Request:** "write a business proposal"

**Big Model Response:**
```
App: 0=Word, 1=Excel
Content generation → Word. Brief topic and type description sufficient
```

**Small Model Response:**
```
App: 0=Word, 1=Excel
Content generation → Word. Need detailed prompt: specific topic, word count, format specs, target audience
```

### VBA Automation Example

**User Request:** "automate Excel formatting"

**Big Model Response:**
```
App: 0=Word, 1=Excel
VBA generation → Describe automation goal and main steps
```

**Small Model Response:**
```
App: 0=Word, 1=Excel
VBA generation → Need detailed requirements: specific objects (files/cells), conditions, error handling, expected results
```

### Chinese Example

**用户请求：** "创建一份报告"

**大模型响应：**
```
应用选择：0=Word, 1=Excel
内容生成→Word，简要描述主题和类型即可
```

**小模型响应：**
```
应用选择：0=Word, 1=Excel
内容生成→Word，需要详细提示：具体主题、字数要求、格式规范、目标受众
```

## 🎪 Sample Conversation

```
=== Interactive Office Optimizer ===
Target Model: Big Model (GPT-4, Claude-3.5, etc.)
Commands: /q=quit, /e=exit, /c=clear (fresh start), /mb=big model, /ms=small model

📝 Your request: write a report
🤖 App: 0=Word, 1=Excel
   Content generation → Word. Brief topic and type description sufficient

📝 Your request: /ms
🤖 Switched to small model mode: Small Model (7B, 13B models, etc.)
   Prompts will be more detailed with explicit steps

📝 Your request: write a report
🤖 App: 0=Word, 1=Excel
   Content generation → Word. Need detailed prompt: specific topic, word count, format specs, target audience

📝 Your request: 0
🤖 Selected Word. Please describe the specific task.

📝 Your request: quarterly sales report
🤖 VBA需求：报告主题(季度销售)，详细要求：包含具体数据源、图表类型、页面布局、字数范围(建议1500-2000字)、目标受众(管理层)
```

## 🔍 Key Benefits

1. **Optimized for Target Model**: Prompts match the receiving model's capabilities
2. **Efficiency**: Big models get concise prompts, small models get detailed guidance
3. **Flexibility**: Easy switching between model types during conversation
4. **Language Consistency**: Adaptation works for both English and Chinese
5. **Context Aware**: Model selection persists throughout the conversation

## 🚀 Usage

Start the interactive optimizer:
```bash
uv run python tools/interactive_optimizer.py
```

The interface shows your current target model and allows switching with simple commands.