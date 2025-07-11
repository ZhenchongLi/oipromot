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

### 4. **用户认证系统**
- JWT 基础的安全认证机制
- 用户注册和登录功能
- 会话管理和状态保持
- 用户专属的个性化体验

### 5. **收藏功能**
- 保存常用的需求优化命令
- 快速重用历史成功的需求模板
- 个人收藏夹管理
- 跨会话的历史记录访问

### 6. **数据持久化**
- DuckDB 数据库支持
- 用户数据安全存储
- 高性能的数据访问
- 轻量级的部署方案

### 7. **技术特性**
- 支持 OpenAI 兼容的 API（包括 Ollama）
- 异步处理，响应时间显示
- 自动语言检测（中文/英文）
- 优雅的错误处理和回退机制
- 反向代理支持（Nginx 等）

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

   # 配置检查（如有问题）
   uv run config-check
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

### 主要依赖包
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `sqlmodel` - 数据库 ORM
- `duckdb` - 嵌入式数据库
- `bcrypt` - 密码加密
- `pyjwt` - JWT 认证
- `orjson` - 高性能 JSON 处理
- `openai` - AI API 客户端

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

# 数据库配置
DATABASE_URL=duckdb:///data/app.db      # DuckDB 数据库路径

# 安全配置
SECRET_KEY=your_secret_key_here         # JWT 密钥（请更换为随机字符串）
JWT_EXPIRE_HOURS=24                     # JWT 过期时间（小时）
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

#### CLI 版本流程

1. **启动程序**
   ```
   🎯 交互式需求优化器
   通过确认流程转换用户输入
   命令: 'quit' 退出, '/n' 或 'n' 开始新对话, '/t' 启用思考模式, Ctrl+C 快速退出

   请输入您的需求:
   ```

#### Web 版本流程

1. **访问应用**
   - 打开浏览器，访问 `http://localhost:8000`
   - 系统将自动重定向到登录页面

2. **用户登录**
   - 输入用户名和密码
   - 系统将自动创建用户账户（如果不存在）
   - 成功登录后进入主界面

3. **使用功能**
   - 输入需求并获得 AI 优化建议
   - 使用收藏功能保存常用命令
   - 快速重用收藏的需求模板

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

#### 收藏功能使用

1. **添加收藏**
   - 在 Web 界面中，当 AI 返回优化结果后
   - 点击“添加收藏”按钮
   - 输入收藏名称并保存

2. **使用收藏**
   - 在收藏列表中查看所有保存的命令
   - 点击“使用”按钮将收藏内容自动填入输入框
   - 支持删除不需要的收藏项目

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
- **Qwen** - 通义千问模型，支持动态思考模式控制
- **OpenAI** - GPT 模型
- **DeepSeek** - DeepSeek Chat
- **Groq** - 快速推理
- **DashScope** - 阿里云通义千问
- **任何其他 OpenAI 兼容的提供商**

### 思考模式支持

不同 API 提供商对思考模式的支持方式：

| 提供商 | 支持方式 | 配置说明 |
|-------|---------|---------|
| **Ollama** | `extra_body={"enable_thinking": true/false}` | 完全支持动态控制 |
| **Qwen** | `extra_body={"enable_thinking": true/false}` | 完全支持动态控制 |
| **DashScope** | 仅流式模式支持 | 需要启用 `stream=True` |
| **其他** | 文本标签控制 | 使用 `/t` 和 `/no_think` 标签 |

## 🔍 故障排除

### 自动配置检查

如果遇到问题，首先运行配置检查工具：

```bash
uv run config-check
```

该工具将检查：
- ✅ 环境变量配置
- 🌐 API 服务器连接
- 🤖 模型可用性
- 💡 针对性的修复建议

### 增强错误提示

应用现在提供详细的错误信息：

- **错误类型识别**: 连接错误、认证错误、模型错误等
- **具体错误描述**: 清晰说明问题所在
- **修复建议**: 提供针对性的解决方案
- **重试选项**: 指导用户下一步操作

### 常见问题解决

| 错误类型 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 连接错误 | 网络问题/服务器未运行 | 检查网络连接和API服务器状态 |
| 认证错误 | API密钥无效 | 验证 `.env` 中的 `API_KEY` |
| 模型错误 | 模型名称错误 | 检查 `AI_MODEL` 配置 |
| 频率限制 | API调用过于频繁 | 稍后重试或检查API配额 |

### 响应质量优化
1. 尝试使用思考模式（`/t`）
2. 提供更具体的需求描述
3. 通过反馈机制进行迭代优化

## 🌐 Web 应用版本

除了命令行版本，我们还提供了两个Web应用版本：

### 1. 原版 Web 应用（WebSocket 版本）

基于 FastAPI 和 WebSocket 的实时通信版本：

```bash
# 安装依赖
uv sync

# 启动 Web 服务器
uv run python run_web.py
# 或者使用脚本命令
uv run web-app
```

### 2. HTMX 版本（推荐）

基于 HTMX 的现代化前端版本，更简洁、更高效：

```bash
# 启动 HTMX 版本
uv run python run_htmx.py
# 或者使用脚本命令
uv run htmx-app
```

### 访问应用
- **原版 Web 界面**: http://localhost:8000 (WebSocket 版本)
- **HTMX 版本界面**: http://localhost:8001 (HTMX 版本)
- **API 文档**: http://localhost:8000/docs 或 http://localhost:8001/docs

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

#### 共同特性
1. **现代化界面**
   - 响应式设计，支持桌面和移动设备
   - 美观的消息气泡和动画效果
   - 用户友好的登录界面

2. **用户认证系统**
   - 简洁的登录界面
   - JWT 令牌管理
   - 自动会话保持
   - 安全的密码加密

3. **收藏功能**
   - 保存常用的需求优化命令
   - 快速重用收藏的需求模板
   - 个人收藏夹管理
   - 一键复制到输入框

4. **增强功能**
   - 思考模式开关
   - 字符计数显示
   - 响应时间监控
   - 错误处理和重试

#### WebSocket 版本特性
- **实时通信**: WebSocket 连接，实时消息传递
- **自动重连**: 自动重连机制和连接状态显示
- **复杂交互**: 支持更复杂的实时交互模式

#### HTMX 版本特性（推荐）
- **轻量级**: 无需复杂的 JavaScript 框架
- **服务器驱动**: 服务器端渲染，更快的页面加载
- **渐进式增强**: 基于标准 HTML 表单，功能渐进增强
- **简洁架构**: 更简单的前后端交互模式
- **高性能**: 最小化的 JavaScript 代码和网络请求

### 技术栈

#### WebSocket 版本
- **后端**: FastAPI + WebSocket
- **前端**: HTML5 + CSS3 + JavaScript (ES6+)
- **实时通信**: WebSocket

#### HTMX 版本
- **后端**: FastAPI + REST API
- **前端**: HTMX + HTML5 + CSS3 + 最小化 JavaScript
- **交互模式**: HTMX 驱动的服务器端渲染

#### 共同技术
- **模板引擎**: Jinja2
- **UI 框架**: Bootstrap 5
- **图标**: Font Awesome
- **数据库**: DuckDB + SQLModel

### 项目架构

```
oipromot/
├── core_optimizer.py       # 🧠 核心逻辑（共享）
│   ├── RequirementOptimizer # AI 优化器
│   └── SessionManager      # 会话管理
├── simple_cli.py           # 🖥️ CLI 界面层
├── web_app.py              # 🌐 WebSocket 版本界面层
├── htmx_app.py             # 🚀 HTMX 版本界面层（推荐）
├── run_web.py              # 🚀 WebSocket 版本启动脚本
├── run_htmx.py             # 🚀 HTMX 版本启动脚本
├── models.py               # 📊 数据库模型
├── jwt_utils.py            # 🔐 JWT 工具
├── database_config.py      # 💾 数据库配置
├── test_install.py         # 🧪 安装测试
├── config_check.py         # 🔧 配置检查
├── pyproject.toml          # 📦 项目配置和依赖
├── templates/              # 🎨 WebSocket 版本模板
│   ├── index.html         # 主页面模板
│   └── login.html         # 登录页面模板
├── frontend/               # 🎨 HTMX 版本前端
│   ├── templates/
│   │   ├── index.html     # HTMX 主页面模板
│   │   └── login.html     # HTMX 登录页面模板
│   └── static/
│       ├── css/
│       │   └── style.css  # HTMX 样式文件
│       └── js/
│           └── app.js     # HTMX 前端逻辑
├── static/                 # 🎨 WebSocket 版本静态文件
│   ├── css/
│   │   └── style.css      # 💄 样式文件
│   └── js/
│       └── app.js         # ⚡ 前端逻辑
├── data/
│   └── app.db             # 📊 DuckDB 数据库文件
├── tools/
│   ├── __init__.py
│   └── user_manager.py    # 👥 用户管理工具
└── .env                   # ⚙️ 环境配置
```

#### 架构说明

- **`core_optimizer.py`**: 包含所有核心业务逻辑
  - `RequirementOptimizer`: 处理 AI API 调用和需求优化
  - `SessionManager`: 管理会话状态和交互流程
- **`simple_cli.py`**: CLI 界面层，使用核心逻辑
- **`web_app.py`**: WebSocket 版本界面层，使用相同的核心逻辑
- **`htmx_app.py`**: HTMX 版本界面层（推荐），更简洁的前后端分离
- **共享特性**: 三个界面共享完全相同的优化逻辑和功能

#### 版本选择建议

- **CLI 版本**: 适合命令行环境和自动化脚本
- **WebSocket 版本**: 适合需要实时交互的复杂应用
- **HTMX 版本**: 推荐用于大多数 Web 应用场景，更简洁高效

## 📝 开发说明

### 核心特点
- 异步处理提高响应性能
- 统一的思考模式控制
- 完整的会话状态管理
- 优雅的错误处理和回退机制
- 响应时间监控
- WebSocket 实时通信
- 现代化 Web 界面
- JWT 安全认证
- DuckDB 轻量级数据库
- 用户收藏系统

### 扩展点
- 支持更多 AI 模型提供商
- 添加更多专业领域的需求模板
- 集成更多输出格式选项
- 增强收藏系统（标签、分类、搜索）
- 会话历史和导出功能
- 用户权限管理
- 多语言国际化支持
- 批量操作和 API 集成

### 数据库设计

系统使用 DuckDB 作为主数据库，包含以下数据表：

- **User 表**: 用户认证信息
- **FavoriteCommand 表**: 用户收藏的命令

### 安全特性

- **密码加密**: 使用 bcrypt 进行密码哈希
- **JWT 认证**: 无状态的令牌认证机制
- **会话管理**: 自动过期和更新机制
- **数据隔离**: 用户数据严格隔离
- **反向代理支持**: 支持 X-Forwarded-* 头部

## 🕰 更新日志

### v0.2.0 (2024-12-XX)
- ✨ 新增用户认证系统（JWT 支持）
- ✨ 新增收藏功能，保存常用命令
- ✨ 集成 DuckDB 数据库支持
- ✨ 增强 Web 界面，支持用户个性化体验
- ✨ 添加反向代理支持
- 🔒 增强安全性，密码加密存储
- 📦 更新依赖包，添加 orjson, bcrypt, pyjwt 等

### v0.1.0 (2024-11-XX)
- ✨ 初始发布
- ✨ CLI 和 Web 两种界面
- ✨ 交互式需求优化
- ✨ 思考模式支持
- ✨ 多 API 提供商支持

## 📝 许可证

MIT License