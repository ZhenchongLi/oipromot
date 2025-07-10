#!/usr/bin/env python3
"""
JWT utilities for authentication.
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from logger_config import get_logger

load_dotenv()

# Initialize logger
logger = get_logger(__name__)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def generate_jwt_token(user_id: str, username: str) -> str:
    """Generate JWT token for user."""
    logger.info(f"Generating JWT token for user: {username} (ID: {user_id})")
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.debug(f"JWT token generated successfully for user: {username}")
    return token


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload."""
    logger.debug("Verifying JWT token")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        logger.debug(f"JWT token verified successfully for user: {payload.get('username')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token verification failed: token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT token verification failed: invalid token - {str(e)}")
        return None


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token without verification (for debugging)."""
    logger.debug("Decoding JWT token without verification")
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        logger.debug(f"JWT token decoded successfully: {decoded.get('username')}")
        return decoded
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT token decode failed: {str(e)}")
        return None