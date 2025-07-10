#!/usr/bin/env python3
"""
Web application version of the requirement optimizer using shared core logic.
"""

import orjson
import uuid
import time
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Form, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
from core_optimizer import RequirementOptimizer, SessionManager
from models import DatabaseManager, FavoriteCommand
from jwt_utils import generate_jwt_token, verify_jwt_token
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


class ConnectionManager:
    """Manages WebSocket connections and sessions using shared core logic."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, SessionManager] = {}
        self.optimizer = RequirementOptimizer()

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a new WebSocket session."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.sessions[session_id] = SessionManager(self.optimizer)
        logger.info(f"WebSocket connection established for session {session_id}")

    def disconnect(self, session_id: str):
        """Disconnect a WebSocket session."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.sessions:
            del self.sessions[session_id]
        logger.info(f"WebSocket connection closed for session {session_id}")

    async def send_message(self, session_id: str, message: dict):
        """Send message to specific session."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(orjson.dumps(message).decode())

    async def handle_message(self, session_id: str, message: dict):
        """Handle incoming messages from clients."""
        logger.debug(f"Handling message for session {session_id}: {message.get('type')}")
        
        if session_id not in self.sessions:
            logger.warning(f"Message received for non-existent session {session_id}")
            await self.send_message(session_id, {
                "type": "error",
                "content": "会话不存在"
            })
            return

        session = self.sessions[session_id]
        message_type = message.get("type")
        content = message.get("content", "")

        try:
            if message_type == "user_input":
                await self._handle_user_input(session_id, session, content)
            elif message_type == "new_conversation":
                await self._handle_new_conversation(session_id, session)
            else:
                logger.warning(f"Unknown message type: {message_type}")
        except Exception as e:
            logger.error(f"Error handling message for session {session_id}: {str(e)}")
            await self.send_message(session_id, {
                "type": "error",
                "content": f"处理消息时出错: {str(e)}"
            })

    async def _handle_user_input(self, session_id: str, session: SessionManager, user_input: str):
        """Handle user input (both new requirement and feedback)."""
        # Send processing message
        await self.send_message(session_id, {
            "type": "processing",
            "content": "处理中..."
        })

        # Check if this is a new conversation or feedback
        if session.get_status() == "IDLE":
            # New requirement
            result = await session.start_session(user_input)
        else:
            # Feedback
            result = await session.handle_feedback(user_input)

        await self.send_message(session_id, result)

    async def _handle_new_conversation(self, session_id: str, session: SessionManager):
        """Handle new conversation request."""
        result = session.reset_session()
        await self.send_message(session_id, result)


# FastAPI app setup
app = FastAPI(title="需求优化器", description="交互式需求优化web应用")

# Add proxy headers middleware (must be added before other middlewares)
app.add_middleware(ProxyHeadersMiddleware)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-this-in-production")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database manager
db_manager = DatabaseManager()


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

# Connection manager
manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serve the main page."""
    if not check_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    """Serve the login page."""
    if check_auth(request):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def post_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login form submission."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Login attempt from {client_ip} for user: {username}")
    
    user = db_manager.authenticate_user(username, password)
    if user:
        request.session["user_id"] = user.id
        logger.info(f"User {username} logged in successfully from {client_ip}")
        return RedirectResponse(url="/", status_code=302)
    else:
        logger.warning(f"Failed login attempt from {client_ip} for user: {username}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "用户名或密码错误"
        })


@app.post("/api/login")
async def api_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle API login and return JWT token."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"API login attempt from {client_ip} for user: {username}")
    
    user = db_manager.authenticate_user(username, password)
    if user:
        token = generate_jwt_token(user.id, user.username)
        logger.info(f"User {username} logged in via API successfully from {client_ip}")
        return JSONResponse({
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        })
    else:
        logger.warning(f"Failed API login attempt from {client_ip} for user: {username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")


@app.get("/logout")
async def logout(request: Request):
    """Handle logout."""
    user_id = request.session.get("user_id")
    if user_id:
        logger.info(f"User {user_id} logged out")
    request.session.pop("user_id", None)
    return RedirectResponse(url="/login", status_code=302)


@app.post("/api/logout")
async def api_logout():
    """Handle API logout (client should discard token)."""
    return JSONResponse({"message": "注销成功"})


@app.get("/api/me")
async def get_current_user_info(request: Request, user = Depends(get_current_user_jwt)):
    """Get current user information via JWT or session."""
    # 如果JWT认证失败，尝试session认证
    if not user:
        if check_auth(request):
            user = get_current_user(request)
        else:
            raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "user_id": user.id,
        "username": user.username,
        "created_at": user.created_at,
        "last_login": user.last_login
    }


@app.post("/api/get-token")
async def get_token_from_session(request: Request):
    """Get JWT token for session-authenticated user."""
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Session authentication required")
    
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    token = generate_jwt_token(user.id, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }


@app.post("/api/favorites")
async def create_favorite_command(
    command: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    user = Depends(require_auth_jwt)
):
    """Create a new favorite command."""
    logger.info(f"User {user.username} creating favorite command: {command}")
    
    if db_manager.check_favorite_exists(user.id, command):
        logger.warning(f"User {user.username} tried to create duplicate favorite: {command}")
        raise HTTPException(status_code=400, detail="命令已存在于收藏夹中")
    
    favorite = db_manager.create_favorite_command(user.id, command, description, category)
    logger.info(f"User {user.username} created favorite command successfully: {command}")
    return {
        "id": favorite.id,
        "command": favorite.command,
        "description": favorite.description,
        "category": favorite.category,
        "created_at": favorite.created_at,
        "updated_at": favorite.updated_at
    }


@app.get("/api/favorites")
async def get_favorite_commands(user = Depends(require_auth_jwt)):
    """Get all favorite commands for the current user."""
    favorites = db_manager.get_user_favorite_commands(user.id)
    return [{
        "id": fav.id,
        "command": fav.command,
        "description": fav.description,
        "category": fav.category,
        "created_at": fav.created_at,
        "updated_at": fav.updated_at
    } for fav in favorites]


@app.get("/api/favorites/{favorite_id}")
async def get_favorite_command(favorite_id: str, user = Depends(require_auth_jwt)):
    """Get a specific favorite command."""
    favorite = db_manager.get_favorite_command_by_id(favorite_id, user.id)
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏命令不存在")
    
    return {
        "id": favorite.id,
        "command": favorite.command,
        "description": favorite.description,
        "category": favorite.category,
        "created_at": favorite.created_at,
        "updated_at": favorite.updated_at
    }


@app.put("/api/favorites/{favorite_id}")
async def update_favorite_command(
    favorite_id: str,
    command: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    user = Depends(require_auth_jwt)
):
    """Update a favorite command."""
    favorite = db_manager.update_favorite_command(favorite_id, user.id, command, description, category)
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏命令不存在")
    
    return {
        "id": favorite.id,
        "command": favorite.command,
        "description": favorite.description,
        "category": favorite.category,
        "created_at": favorite.created_at,
        "updated_at": favorite.updated_at
    }


@app.delete("/api/favorites/{favorite_id}")
async def delete_favorite_command(favorite_id: str, user = Depends(require_auth_jwt)):
    """Delete a favorite command."""
    success = db_manager.delete_favorite_command(favorite_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="收藏命令不存在")
    
    return {"message": "收藏命令已删除"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication."""
    logger.info(f"WebSocket connection request for session {session_id}")
    
    # For WebSocket, we'll accept the connection and handle auth via message
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = orjson.loads(data)
                await manager.handle_message(session_id, message)
            except orjson.JSONDecodeError as e:
                logger.error(f"Invalid JSON received from session {session_id}: {str(e)}")
                await manager.send_message(session_id, {
                    "type": "error",
                    "content": "无效的消息格式"
                })
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
        manager.disconnect(session_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)