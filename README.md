# OiPromot - Simple Requirement Optimizer

A simple CLI tool that optimizes user input to clearly describe requirements without extra guidance.

## 🏗️ Simple Structure

Ultra-simple structure with just the essentials:

```
oipromot/
├── cli.py                  # Main CLI entry point
├── simple_cli.py           # Core requirement optimizer
├── .env.example            # Configuration template
└── pyproject.toml          # uv project config
```

## 🚀 Key Features

### 1. **Single Purpose**
- Focuses only on optimizing user input for clear requirement descriptions
- No extra guidance or implementation suggestions
- Clean, professional language output

### 2. **OpenAI-Compatible API Support**
- Works with any OpenAI-compatible API (Ollama, OpenAI, DeepSeek, Groq, etc.)
- Default configuration for Ollama (local)
- Simple environment variable configuration
- Automatic fallback to simple text cleaning when APIs unavailable

### 3. **Language Support**
- Automatic Chinese/English detection
- Appropriate prompts for each language
- Maintains cultural context in optimization

### 4. **Simple Configuration**
- Environment variable based configuration
- No complex setup required
- Clear API key management

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.13+
- uv package manager
- For default setup: [Ollama](https://ollama.ai) with a model like `qwen2.5:3b`

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd oipromot

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API configuration (defaults to Ollama)

# For Ollama setup (default):
# 1. Install Ollama: https://ollama.ai
# 2. Pull a model: ollama pull qwen2.5:3b
# 3. Run: uv run python cli.py (uses default Ollama config)
```

### Environment Variables
```bash
# OpenAI-compatible API Configuration
# Default: Ollama (local)
API_BASE_URL=http://localhost:11434/v1
# API_KEY=  # Leave empty for Ollama (no key required)
MODEL=qwen2.5:3b

# Examples for different providers:
# OpenAI: API_BASE_URL=https://api.openai.com/v1, API_KEY=sk-..., MODEL=gpt-3.5-turbo
# DeepSeek: API_BASE_URL=https://api.deepseek.com/v1, API_KEY=sk-..., MODEL=deepseek-chat
```

## 🚀 Usage

### CLI Interface
```bash
# Run the requirement optimizer
uv run python cli.py
```

### Example Usage
```bash
$ uv run python cli.py
🎯 Requirement Optimizer
Transform user input into clear requirement descriptions
Type 'quit' to exit

Enter your requirement: I want to help me create a spreadsheet that can track my expenses

Processing...

📝 Optimized Requirement:
Create a spreadsheet for expense tracking

--------------------------------------------------
Enter your requirement: 请帮我做一个能够管理客户信息的表格

Processing...

📝 Optimized Requirement:
创建一个客户信息管理表格

--------------------------------------------------
```

## 🧪 Testing

You can test the optimizer with various inputs:

```bash
# Test with verbose input
"I want to help me create a spreadsheet that can track my expenses"
→ "Create a spreadsheet for expense tracking"

# Test with Chinese input
"请帮我做一个能够管理客户信息的表格"
→ "创建一个客户信息管理表格"

# Test with simple input
"make a report"
→ "Make a report"
```

## 🔧 How It Works

1. **Input Analysis**: Detects language (Chinese/English) and removes filler words
2. **AI Processing**: Uses any OpenAI-compatible API (default: Ollama) to optimize the requirement description
3. **Fallback**: Simple text cleaning when APIs are unavailable
4. **Output**: Clear, professional requirement description

## 🛠️ Supported Providers

The tool works with any OpenAI-compatible API:
- **Ollama** (default) - Local models like Qwen, Llama, etc.
- **OpenAI** - GPT models
- **DeepSeek** - DeepSeek Chat
- **Groq** - Fast inference
- **Any other OpenAI-compatible provider**

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the configuration in `.env.example`

---

**Note**: This simplified version focuses purely on requirement optimization without extra guidance.