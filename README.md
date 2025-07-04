# Simple CLI - 交互式需求优化器

一个基于 AI 的交互式需求优化工具，帮助用户将模糊的需求转化为清晰、准确的需求描述。

## 🏗️ 项目结构

```
oipromot/
├── cli.py                  # 原始CLI入口
├── simple_cli.py           # 交互式需求优化器（主要功能）
├── .env.example            # 配置模板
└── pyproject.toml          # uv项目配置
```

## 🚀 功能特性

### 1. **交互式需求优化**
- 将用户的原始输入转化为清晰、准确的需求描述
- 支持 Excel 和 Word 相关功能的专业术语理解
- 自动去除冗余信息，保持需求核心意图
- 以列表形式输出，每个需求点用数字编号

### 2. **反馈调整机制**
- 初始需求优化后，用户可以提供反馈进行调整
- 支持多轮反馈迭代，直到满意为止
- 实时显示 AI 调整后的结果

### 3. **思考模式控制**
- **无思考模式**（默认）：快速响应，直接输出结果
- **思考模式**：通过 `/t` 激活，提供更深入的分析

### 4. **技术特性**
- 支持 OpenAI 兼容的 API（包括 Ollama）
- 异步处理，响应时间显示
- 自动语言检测（中文/英文）
- 优雅的错误处理和回退机制

## 🛠️ 安装要求

### 快速开始

1. **安装依赖**
   ```bash
   # 使用 uv 安装项目依赖
   uv sync
   ```

2. **测试安装**
   ```bash
   # 验证所有模块正确安装
   uv run test-install
   ```

3. **配置环境**
   ```bash
   # 复制环境配置模板
   cp .env.example .env
   # 编辑 .env 配置你的 API 设置
   ```

4. **启动应用**
   ```bash
   # CLI 版本
   uv run simple-cli
   
   # Web 版本
   uv run web-app
   ```

### 依赖管理
项目使用 uv 进行现代化 Python 依赖管理：
```bash
# 添加新依赖
uv add package-name

# 开发依赖
uv sync --group dev

# 更新依赖
uv lock --upgrade
```

### 环境配置
创建 `.env` 文件：
```env
# API 配置
API_BASE_URL=http://localhost:11434/v1  # Ollama 默认地址
API_KEY=your_api_key_here               # OpenAI API key（Ollama 可省略）
AI_MODEL=qwen3:1.7b                     # 模型名称

# Web 应用配置
WEB_HOST=0.0.0.0                        # 服务器监听地址
WEB_PORT=8000                           # 服务器端口
WEB_RELOAD=true                         # 开发模式自动重载
```

## 🚀 使用方法

### 启动程序
```bash
# 使用 uv 运行
uv run python simple_cli.py
# 或者使用脚本命令
uv run simple-cli
```

### 交互命令
| 命令 | 功能 |
|------|------|
| `quit`, `exit`, `q` | 退出程序 |
| `/n`, `n` | 开始新对话 |
| `/t` | 启用思考模式（在输入中包含） |
| `Ctrl+C` | 快速退出 |

### 使用流程

1. **启动程序**
   ```
   🎯 交互式需求优化器
   通过确认流程转换用户输入
   命令: 'quit' 退出, '/n' 或 'n' 开始新对话, '/t' 启用思考模式, Ctrl+C 快速退出
   
   请输入您的需求: 
   ```

2. **输入需求**
   ```
   请输入您的需求: 我想要一个Excel表格来跟踪项目进度
   ```

3. **查看 AI 优化结果**
   ```
   处理中...
   ⏱️ 响应时间: 1.23s (无思考模式)
   
   🤖 AI回复: 1. 创建Excel工作表用于项目进度跟踪
   2. 包含项目名称、负责人、开始日期、截止日期、完成状态等字段
   3. 支持进度百分比显示和状态更新功能
   
   请选择:
   1. 输入反馈意见进行调整
   2. 输入 '/n' 或 'n' 开始新对话
   ```

4. **提供反馈调整**
   ```
   您的反馈: 还需要添加风险评估和预算跟踪功能
   
   🤖 AI调整后回复: 1. 创建Excel工作表用于项目进度跟踪
   2. 包含项目名称、负责人、开始日期、截止日期、完成状态等字段
   3. 支持进度百分比显示和状态更新功能
   4. 添加风险评估等级和风险描述字段
   5. 包含预算跟踪功能，显示预算金额和实际支出
   
   请选择:
   1. 输入反馈意见继续调整
   2. 输入 '/n' 或 'n' 开始新对话
   ```

### 思考模式使用

在输入中包含 `/t` 来启用思考模式：
```
请输入您的需求: /t 设计一个复杂的数据分析系统
```

思考模式特点：
- 使用更高的温度参数（0.3 vs 0.1）
- 分配更多 token 限制（3000 vs 1500）
- 提供更深入的分析和思考过程

## 🔧 代码结构

### 主要类和方法

```python
class RequirementOptimizer:
    def __init__(self)                                              # 初始化优化器
    async def start_session(self, user_input: str) -> str          # 开始新会话
    async def handle_feedback(self, feedback: str) -> str          # 处理用户反馈
    async def optimize_requirement(self, user_input: str) -> str   # 优化需求
    async def refine_requirement(self, initial_result: str, feedback: str) -> str  # 细化需求
    async def _call_api(self, system_prompt: str, user_input: str) -> Optional[str]  # API调用
```

### 配置参数

#### 思考模式控制
- **检测机制**：检测用户输入中是否包含 `/t`
- **无思考模式**（默认）：
  - `temperature=0.1`
  - `max_tokens=1500`
  - `enable_thinking=False`
- **思考模式**：
  - `temperature=0.3`
  - `max_tokens=3000`
  - `enable_thinking=True`

#### 会话状态
- `WAITING_FEEDBACK`: 等待用户反馈
- `NEW_CONVERSATION`: 开始新对话

## 🧪 测试示例

### 基本使用
```bash
$ python simple_cli.py
🎯 交互式需求优化器
请输入您的需求: 创建一个客户管理系统

🤖 AI回复: 1. 创建客户信息管理系统
2. 包含客户基本信息录入和编辑功能
3. 支持客户信息查询和筛选
4. 提供客户联系记录管理
```

### 思考模式
```bash
请输入您的需求: /t 设计一个复杂的财务报表系统
⏱️ 响应时间: 2.45s (思考模式)

🤖 AI回复: 1. 设计综合财务报表系统
2. 包含损益表、资产负债表、现金流量表等核心报表
3. 支持多期间对比分析和趋势分析
4. 提供财务指标计算和可视化展示
5. 集成预算管理和成本控制模块
```

## 🛠️ 支持的API提供商

支持所有 OpenAI 兼容的 API：
- **Ollama**（默认）- 本地模型如 Qwen、Llama 等
- **OpenAI** - GPT 模型
- **DeepSeek** - DeepSeek Chat
- **Groq** - 快速推理
- **任何其他 OpenAI 兼容的提供商**

## 🔍 常见问题

### API 连接问题
1. 确保 Ollama 服务正在运行
2. 检查 `API_BASE_URL` 配置
3. 验证模型名称是否正确

### 响应质量问题
1. 尝试使用思考模式（`/t`）
2. 提供更具体的需求描述
3. 通过反馈机制进行迭代优化

### 性能优化
1. 使用无思考模式获得更快响应
2. 选择合适的模型大小
3. 调整 `max_tokens` 限制

## 🌐 Web 应用版本

除了命令行版本，我们还提供了基于 FastAPI 和 WebSocket 的 Web 应用版本。

### 启动 Web 应用

```bash
# 安装依赖
uv sync

# 启动 Web 服务器
uv run python run_web.py
# 或者使用脚本命令
uv run web-app
```

### 访问应用
- **Web 界面**: http://localhost:8000 (默认，可通过 WEB_PORT 配置)
- **API 文档**: http://localhost:8000/docs

### 配置选项

#### Web 应用配置
| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `WEB_HOST` | `0.0.0.0` | 服务器监听地址，`0.0.0.0` 允许外部访问 |
| `WEB_PORT` | `8000` | 服务器端口号 |
| `WEB_RELOAD` | `true` | 开发模式自动重载，生产环境建议设为 `false` |

#### 使用示例
```bash
# 更改端口为 3000
echo "WEB_PORT=3000" >> .env

# 仅本地访问
echo "WEB_HOST=127.0.0.1" >> .env

# 关闭自动重载（生产环境）
echo "WEB_RELOAD=false" >> .env
```

### Web 版本特性

1. **现代化界面**
   - 响应式设计，支持桌面和移动设备
   - 实时聊天界面
   - 美观的消息气泡和动画效果

2. **实时通信**
   - WebSocket 连接，实时消息传递
   - 自动重连机制
   - 连接状态显示

3. **会话管理**
   - 独立的会话ID管理
   - 会话状态跟踪
   - 支持多用户同时使用

4. **增强功能**
   - 思考模式开关
   - 字符计数显示
   - 响应时间监控
   - 错误处理和重试

### 技术栈
- **后端**: FastAPI + WebSocket
- **前端**: HTML5 + CSS3 + JavaScript (ES6+)
- **模板引擎**: Jinja2
- **UI 框架**: Bootstrap 5
- **图标**: Font Awesome

### 项目结构（Web 版本）

```
oipromot/
├── web_app.py              # Web 应用主文件
├── run_web.py              # 启动脚本
├── simple_cli.py           # 原始 CLI 版本
├── pyproject.toml          # uv 项目配置和依赖
├── templates/
│   └── index.html         # 主页模板
├── static/
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       └── app.js         # 前端逻辑
└── .env                   # 环境配置
```

## 📝 开发说明

### 核心特点
- 异步处理提高响应性能
- 统一的思考模式控制
- 完整的会话状态管理
- 优雅的错误处理和回退机制
- 响应时间监控
- WebSocket 实时通信
- 现代化 Web 界面

### 扩展点
- 支持更多 AI 模型提供商
- 添加更多专业领域的需求模板
- 集成更多输出格式选项
- 添加历史记录和会话管理
- 用户认证和权限管理
- 多语言国际化支持

## 📝 许可证

MIT License