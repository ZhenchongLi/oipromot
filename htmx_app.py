#!/usr/bin/env python3
"""
HTMX version of the web application with API endpoints for frontend-backend communication.
"""

import time
from typing import Dict, Optional
from fastapi import FastAPI, Request, HTTPException, Form, Depends, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
from core_optimizer import RequirementOptimizer, SessionManager
from models import DatabaseManager
from jwt_utils import verify_jwt_token
from logger_config import get_logger, log_performance

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)


class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to handle reverse proxy headers for correct URL generation."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Handle X-Forwarded-Proto and X-Forwarded-Host headers
        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        forwarded_host = request.headers.get("X-Forwarded-Host")
        forwarded_port = request.headers.get("X-Forwarded-Port")
        
        logger.debug(f"Request {request.method} {request.url.path} from {client_ip}")
        
        # Update request scope for correct URL generation
        if forwarded_proto:
            request.scope["scheme"] = forwarded_proto
        
        if forwarded_host:
            # Use the forwarded port if provided, otherwise use 8888 (nginx port)
            if forwarded_port:
                port = int(forwarded_port)
            else:
                # Default to 8888 for this specific nginx setup
                port = 8888
            request.scope["server"] = (forwarded_host, port)
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            log_performance(f"{request.method} {request.url.path}", duration)
            logger.info(f"Request {request.method} {request.url.path} completed with status {response.status_code} in {duration:.4f}s")
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request {request.method} {request.url.path} failed after {duration:.4f}s: {str(e)}")
            raise


class HTMXOptimizer:
    """Handles optimization requests for HTMX frontend."""
    
    def __init__(self):
        self.optimizer = RequirementOptimizer()
        self.sessions: Dict[str, SessionManager] = {}
    
    def get_session(self, session_id: str) -> SessionManager:
        """Get or create a session manager."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionManager(self.optimizer)
        return self.sessions[session_id]
    
    async def process_message(self, session_id: str, message: str) -> dict:
        """Process a user message and return the response."""
        session = self.get_session(session_id)
        
        try:
            # Check if this is a new conversation or feedback
            if session.get_status() == "IDLE":
                # New requirement
                result = await session.start_session(message)
            else:
                # Feedback
                result = await session.handle_feedback(message)
            
            return result
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {str(e)}")
            return {
                "type": "error",
                "content": f"处理消息时出错: {str(e)}",
                "response_time": 0,
                "error_type": "ProcessingError"
            }
    
    def new_conversation(self, session_id: str) -> dict:
        """Start a new conversation."""
        session = self.get_session(session_id)
        return session.reset_session()


# FastAPI app setup
app = FastAPI(title="需求优化器", description="交互式需求优化web应用")

# Add proxy headers middleware
app.add_middleware(ProxyHeadersMiddleware)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-this-in-production")

# Static files and templates for HTMX frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Add favicon route
@app.get("/favicon.ico")
async def get_favicon():
    """Return a simple favicon response to avoid 404 errors."""
    return HTMLResponse(content="", status_code=204)

# Database manager
db_manager = DatabaseManager()

# HTMX optimizer
htmx_optimizer = HTMXOptimizer()


def check_auth(request: Request):
    """Check if user is authenticated."""
    return request.session.get("user_id") is not None


def require_auth(request: Request):
    """Dependency to require authentication."""
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")


def get_current_user(request: Request):
    """Get current user from session."""
    user_id = request.session.get("user_id")
    if user_id:
        return db_manager.get_user_by_id(user_id)
    return None


def get_current_user_jwt(authorization: Optional[str] = Header(None)):
    """Get current user from JWT token."""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None
    
    payload = verify_jwt_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if user_id:
        return db_manager.get_user_by_id(user_id)
    return None


def require_auth_jwt(user = Depends(get_current_user_jwt)):
    """Dependency to require JWT authentication."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


# Routes
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serve the main HTMX page."""
    # Log warning if GET request contains login parameters
    if request.query_params.get("username") or request.query_params.get("password"):
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"GET request with login parameters from {client_ip} - login should use POST")
    
    if not check_auth(request):
        return templates.TemplateResponse("login.html", {"request": request})
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    """Serve the login page."""
    if check_auth(request):
        return templates.TemplateResponse("index.html", {"request": request})
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/login")
async def api_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle HTMX login."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"HTMX login attempt from {client_ip} for user: {username}")
    
    user = db_manager.authenticate_user(username, password)
    if user:
        request.session["user_id"] = user.id
        logger.info(f"User {username} logged in successfully from {client_ip}")
        
        # Redirect to main page after successful login
        return HTMLResponse(
            content="",
            status_code=200,
            headers={"HX-Redirect": "/"}
        )
    else:
        logger.warning(f"Failed login attempt from {client_ip} for user: {username}")
        return HTMLResponse(
            content=f"""
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                用户名或密码错误
            </div>
            <!-- Desktop Form -->
            <form hx-post="/api/login" hx-target="#login-form-container" hx-swap="innerHTML" class="d-none d-md-block">
                <div class="mb-3">
                    <label for="username" class="form-label fw-semibold">用户名</label>
                    <input type="text" class="form-control form-control-lg" id="username" name="username" placeholder="请输入用户名" required>
                </div>
                <div class="mb-4">
                    <label for="password" class="form-label fw-semibold">密码</label>
                    <input type="password" class="form-control form-control-lg" id="password" name="password" placeholder="请输入密码" required>
                </div>
                <button type="submit" class="btn btn-primary btn-lg w-100 py-3 mb-3">
                    <i class="fas fa-sign-in-alt me-2"></i>
                    登录
                </button>
            </form>
            <!-- Mobile Form -->
            <form hx-post="/api/login" hx-target="#mobile-login-form-container" hx-swap="innerHTML" class="d-md-none">
                <div class="mb-3">
                    <label for="mobile-username" class="form-label">用户名</label>
                    <input type="text" class="form-control form-control-lg" id="mobile-username" name="username" placeholder="请输入用户名" required>
                </div>
                <div class="mb-4">
                    <label for="mobile-password" class="form-label">密码</label>
                    <input type="password" class="form-control form-control-lg" id="mobile-password" name="password" placeholder="请输入密码" required>
                </div>
                <button type="submit" class="btn btn-primary btn-lg w-100 py-3">
                    <i class="fas fa-sign-in-alt me-2"></i>
                    登录
                </button>
            </form>
            """,
            status_code=400
        )


@app.post("/api/logout")
async def api_logout(request: Request):
    """Handle logout."""
    user_id = request.session.get("user_id")
    if user_id:
        logger.info(f"User {user_id} logged out")
    request.session.pop("user_id", None)
    
    # Redirect to login page after logout
    return HTMLResponse(
        content="",
        status_code=200,
        headers={"HX-Redirect": "/login"}
    )


@app.post("/api/send-message")
async def send_message(request: Request, message: str = Form(...)):
    """Handle message sending via HTMX."""
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get session ID from user session
    session_id = request.session.get("htmx_session_id")
    if not session_id:
        session_id = f"htmx_{user.id}_{int(time.time())}"
        request.session["htmx_session_id"] = session_id
    
    # Process the message
    response = await htmx_optimizer.process_message(session_id, message)
    
    # Create HTML response based on the response type
    if response["type"] == "ai_response" or response["type"] == "ai_response_refined":
        content = response["content"]
        response_time = response.get("response_time", 0)
        mode = response.get("mode", "")
        is_refined = response["type"] == "ai_response_refined"
        
        # Format content with basic HTML
        formatted_content = content.replace('\n', '<br>')
        formatted_content = formatted_content.replace('**', '<strong>')
        
        html = f"""
        <div class="message user-message">
            <div class="message-content">{message}</div>
        </div>
        <div class="message ai-message">
            <div class="message-content">{formatted_content}</div>
            <div class="message-meta">
                <div>
                    <i class="fas fa-robot"></i> {'AI调整后回复' if is_refined else 'AI回复'}
                </div>
                <div>
                    <span class="response-time">⏱️ {response_time:.2f}s</span>
                    <span class="thinking-mode">({mode})</span>
                    <button class="copy-button" data-content="{content}">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="favorite-button" data-content="{content}">
                        <i class="fas fa-star"></i>
                    </button>
                </div>
            </div>
        </div>
        """
        
    elif response["type"] == "error":
        content = response["content"]
        error_type = response.get("error_type", "")
        
        html = f"""
        <div class="message user-message">
            <div class="message-content">{message}</div>
        </div>
        <div class="message error-message">
            <div class="message-content">
                <i class="fas fa-exclamation-triangle"></i> {content}
                {f'<br><span class="badge bg-danger mt-2">{error_type}</span>' if error_type else ''}
                <div class="mt-3 small">
                    <strong>🔄 您可以:</strong>
                    <ul class="mb-0 mt-1">
                        <li>检查网络连接和配置</li>
                        <li>重新输入需求</li>
                        <li>点击"新对话"重新开始</li>
                    </ul>
                </div>
            </div>
        </div>
        """
    else:
        # Default response
        html = f"""
        <div class="message user-message">
            <div class="message-content">{message}</div>
        </div>
        <div class="message system-message">
            <div class="message-content">
                <i class="fas fa-info-circle"></i> 消息已收到
            </div>
        </div>
        """
    
    return HTMLResponse(content=html)


@app.post("/api/new-conversation")
async def new_conversation(request: Request):
    """Start a new conversation."""
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get session ID
    session_id = request.session.get("htmx_session_id")
    if not session_id:
        session_id = f"htmx_{user.id}_{int(time.time())}"
        request.session["htmx_session_id"] = session_id
    
    # Reset conversation
    htmx_optimizer.new_conversation(session_id)
    
    return HTMLResponse(content="""
        <div class="message system-message">
            <div class="message-content">
                <i class="fas fa-info-circle"></i>
                开始新对话。请输入您的需求，我会帮您转化为清晰的需求描述。
            </div>
        </div>
    """)


@app.get("/api/favorites-modal")
async def get_favorites_modal(request: Request):
    """Get favorites modal content."""
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get user's favorites
    favorites = db_manager.get_user_favorite_commands(user.id)
    
    # Generate favorites list HTML
    favorites_html = ""
    if favorites:
        for fav in favorites:
            favorites_html += f"""
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">
                        {fav.command}
                        {f'<span class="badge bg-secondary ms-2">{fav.category}</span>' if fav.category else ''}
                    </h6>
                    {f'<p class="card-text" style="max-height: 100px; overflow-y: auto; font-size: 0.9rem;">{fav.description.replace(chr(10), "<br>")}</p>' if fav.description else ''}
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-primary use-favorite" data-command="{fav.description or fav.command}">
                            <i class="fas fa-copy"></i> 复制
                        </button>
                        <button class="btn btn-outline-danger" 
                                hx-delete="/api/favorites/{fav.id}"
                                hx-confirm="确定要删除这个收藏命令吗？"
                                hx-target="closest .card"
                                hx-swap="outerHTML">
                            <i class="fas fa-trash"></i> 删除
                        </button>
                    </div>
                </div>
            </div>
            """
    else:
        favorites_html = '<div class="alert alert-info">还没有收藏的命令</div>'
    
    return HTMLResponse(content=f"""
    <div class="modal fade show" id="favoritesModal" tabindex="-1" style="display: block;">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-star"></i> 命令收藏夹
                    </h5>
                    <button type="button" class="btn-close" onclick="document.getElementById('modal-container').innerHTML = ''"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <button class="btn btn-success btn-sm" 
                                hx-get="/api/add-favorite-form"
                                hx-target="#favorites-list"
                                hx-swap="afterbegin">
                            <i class="fas fa-plus"></i> 添加命令
                        </button>
                    </div>
                    <div id="favorites-list">
                        {favorites_html}
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="modal-backdrop fade show"></div>
    """)


@app.get("/api/add-favorite-form")
async def get_add_favorite_form():
    """Get add favorite form."""
    return HTMLResponse(content="""
    <div class="card mb-3 border-primary">
        <div class="card-body">
            <h6 class="card-title text-primary">
                <i class="fas fa-plus"></i> 添加新命令
            </h6>
            <form hx-post="/api/favorites" hx-target="closest .card" hx-swap="outerHTML">
                <div class="mb-3">
                    <label class="form-label">命令 *</label>
                    <input type="text" class="form-control" name="command" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">描述</label>
                    <textarea class="form-control" name="description" rows="3"></textarea>
                </div>
                <div class="mb-3">
                    <label class="form-label">分类</label>
                    <input type="text" class="form-control" name="category">
                </div>
                <div class="btn-group btn-group-sm">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> 保存
                    </button>
                    <button type="button" class="btn btn-secondary" 
                            onclick="this.closest('.card').remove()">
                        取消
                    </button>
                </div>
            </form>
        </div>
    </div>
    """)


@app.post("/api/favorites")
async def create_favorite_command(
    request: Request,
    command: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None)
):
    """Create a new favorite command via HTMX."""
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    logger.info(f"User {user.username} creating favorite command: {command}")
    
    if db_manager.check_favorite_exists(user.id, command):
        return HTMLResponse(
            content='<div class="alert alert-warning">命令已存在于收藏夹中</div>',
            status_code=400
        )
    
    favorite = db_manager.create_favorite_command(user.id, command, description, category)
    
    return HTMLResponse(content=f"""
    <div class="card mb-3">
        <div class="card-body">
            <h6 class="card-title">
                {favorite.command}
                {f'<span class="badge bg-secondary ms-2">{favorite.category}</span>' if favorite.category else ''}
            </h6>
            {f'<p class="card-text" style="max-height: 100px; overflow-y: auto; font-size: 0.9rem;">{favorite.description.replace(chr(10), "<br>")}</p>' if favorite.description else ''}
            <div class="btn-group btn-group-sm">
                <button class="btn btn-primary use-favorite" data-command="{favorite.description or favorite.command}">
                    <i class="fas fa-copy"></i> 复制
                </button>
                <button class="btn btn-outline-danger" 
                        hx-delete="/api/favorites/{favorite.id}"
                        hx-confirm="确定要删除这个收藏命令吗？"
                        hx-target="closest .card"
                        hx-swap="outerHTML">
                    <i class="fas fa-trash"></i> 删除
                </button>
            </div>
        </div>
    </div>
    """)


@app.delete("/api/favorites/{favorite_id}")
async def delete_favorite_command(request: Request, favorite_id: str):
    """Delete a favorite command via HTMX."""
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    success = db_manager.delete_favorite_command(favorite_id, user.id)
    if not success:
        return HTMLResponse(
            content='<div class="alert alert-danger">删除失败</div>',
            status_code=404
        )
    
    return HTMLResponse(content="")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)