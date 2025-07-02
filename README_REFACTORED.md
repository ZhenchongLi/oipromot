# OiPromot - Refactored OfficeAI Prompt Project

A refactored and improved Office AI Prompt optimization system with better architecture, error handling, and maintainability.

## 🏗️ Architecture Overview

The application has been refactored with a clean, layered architecture:

```
src/oipromot/
├── core/                    # Core application components
│   ├── config.py           # Configuration management
│   ├── database.py         # Database setup and session management
│   ├── exceptions.py       # Custom exception classes
│   ├── logging.py          # Logging configuration
│   ├── models.py           # Data models
│   └── repository.py       # Data access layer
├── services/               # Business logic layer
│   ├── ai_service.py       # AI model interactions
│   └── prompt_service.py   # Prompt business logic
├── routes/                 # API route handlers
│   └── prompts.py          # Prompt-related endpoints
├── cli/                    # Command-line interfaces
│   ├── base.py             # Base CLI class
│   ├── interactive.py      # Interactive CLI
│   └── simple.py           # Simple CLI
├── ai/                     # AI optimization logic
│   ├── prompt_optimizer.py # Main optimization service
│   ├── capability_analyzer.py # Task capability analysis
│   └── deepseek_client.py  # DeepSeek API client
└── app.py                  # FastAPI application setup
```

## 🚀 Key Improvements

### 1. **Layered Architecture**
- **Repository Pattern**: Separates data access from business logic
- **Service Layer**: Contains business logic and validation
- **Controller Layer**: Handles HTTP requests and responses
- **Clear separation of concerns** between layers

### 2. **Enhanced Error Handling**
- Custom exception hierarchy (`OiPromotException`, `DatabaseError`, `ValidationError`, etc.)
- Proper HTTP status codes and error messages
- Comprehensive logging throughout the application
- Graceful error recovery

### 3. **Configuration Management**
- Environment-based configuration using Pydantic Settings
- Validation of configuration values
- Support for `.env` files
- Type-safe configuration access

### 4. **Improved Logging**
- Centralized logging configuration
- Structured logging with proper levels
- Request/response logging
- Error tracking and debugging

### 5. **Better Testing**
- Comprehensive test suite with pytest
- Test fixtures for database and client setup
- Isolated test environment
- Coverage for all major functionality

### 6. **Dependency Injection**
- Proper dependency injection for services
- Testable components
- Clean separation of dependencies

### 7. **Input Validation**
- Pydantic models for request/response validation
- Custom validation rules
- Clear error messages for invalid input

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.13+
- pip or uv package manager

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd oipromot

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables
```bash
# Database
DATABASE_URL=duckdb:///oipromot.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# AI Services
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# CORS
CORS_ORIGINS=["*"]

# Logging
LOG_LEVEL=INFO
```

## 🚀 Usage

### API Server
```bash
# Start the API server
python main.py

# Or using uvicorn directly
uvicorn src.oipromot.app:app --host 0.0.0.0 --port 8000
```

### CLI Interface
```bash
# Interactive mode
python cli.py interactive

# Simple mode
python cli.py simple
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Prompts
```bash
# Create a prompt
POST /api/v1/prompts/
{
  "title": "My Prompt",
  "content": "Prompt content"
}

# Get all prompts
GET /api/v1/prompts/

# Get specific prompt
GET /api/v1/prompts/{prompt_id}

# Update prompt
PUT /api/v1/prompts/{prompt_id}

# Delete prompt
DELETE /api/v1/prompts/{prompt_id}
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/oipromot

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Test Structure
- `tests/conftest.py`: Test fixtures and configuration
- `tests/test_api.py`: API endpoint tests
- `tests/test_services.py`: Service layer tests
- `tests/test_repository.py`: Repository layer tests

## 🔧 Development

### Code Quality
The project uses several tools for code quality:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Adding New Features

1. **Models**: Add new models in `core/models.py`
2. **Repository**: Create repository methods in `core/repository.py`
3. **Service**: Add business logic in `services/`
4. **Routes**: Create API endpoints in `routes/`
5. **Tests**: Add corresponding tests in `tests/`

### Database Migrations
```bash
# Create new tables
python -c "from src.oipromot.core.database import create_db_and_tables; create_db_and_tables()"
```

## 📊 Monitoring & Logging

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General application information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Log Format
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🔒 Security

- Input validation on all endpoints
- SQL injection protection through SQLModel
- CORS configuration
- Environment variable management
- No sensitive data in logs

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "main.py"]
```

### Environment-Specific Configuration
- Development: Use `.env` file
- Production: Use environment variables
- Testing: Use test database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test examples

---

**Note**: This refactored version maintains backward compatibility while providing a much more robust and maintainable codebase.