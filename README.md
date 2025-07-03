# OiPromot - Simple Requirement Optimizer

A simple tool that optimizes user input to clearly describe requirements without extra guidance.

## 🏗️ Simple Structure

This tool has been simplified to focus on a single purpose:

```
oipromot/
├── cli.py                  # Main CLI entry point
├── simple_cli.py           # Core requirement optimizer
├── simple_optimizer.py     # Alternative standalone version
└── .env.example            # Configuration template
```

## 🚀 Key Features

### 1. **Single Purpose**
- Focuses only on optimizing user input for clear requirement descriptions
- No extra guidance or implementation suggestions
- Clean, professional language output

### 2. **Multi-Provider Support**
- OpenAI API integration
- DeepSeek API integration
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

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd oipromot

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## 🚀 Usage

### CLI Interface
```bash
# Run the requirement optimizer
python cli.py

# Or run the standalone version
python simple_optimizer.py
```

### Example Usage
```bash
$ python cli.py
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
2. **AI Processing**: Uses OpenAI or DeepSeek API to optimize the requirement description
3. **Fallback**: Simple text cleaning when APIs are unavailable
4. **Output**: Clear, professional requirement description

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the configuration in `.env.example`

---

**Note**: This simplified version focuses purely on requirement optimization without extra guidance.