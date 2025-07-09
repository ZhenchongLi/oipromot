#!/usr/bin/env python3
"""
Database models using SQLModel and DuckDB.
"""

import uuid
from typing import Optional
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime
import bcrypt
from database_config import db_config


class User(SQLModel, table=True):
    """User model for authentication."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = Field(default=None)


class DatabaseManager:
    """Database connection and operations manager."""
    
    def __init__(self):
        """Initialize database connection."""
        self.engine = create_engine(db_config.database_url)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables."""
        SQLModel.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get database session."""
        return Session(self.engine)
    
    def create_user(self, username: str, password: str) -> User:
        """Create a new user."""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(username=username, hashed_password=hashed_password)
        
        with self.get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        with self.get_session() as session:
            statement = select(User).where(User.username == username, User.is_active == True)
            user = session.exec(statement).first()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
                # Update last login and updated_at
                user.last_login = datetime.now()
                user.updated_at = datetime.now()
                session.add(user)
                session.commit()
                session.refresh(user)
                # Create a new detached User object with the data we need
                return User(
                    id=user.id,
                    username=user.username,
                    hashed_password=user.hashed_password,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                )
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        with self.get_session() as session:
            statement = select(User).where(User.username == username, User.is_active == True)
            user = session.exec(statement).first()
            if user:
                return User(
                    id=user.id,
                    username=user.username,
                    hashed_password=user.hashed_password,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                )
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        with self.get_session() as session:
            statement = select(User).where(User.id == user_id, User.is_active == True)
            user = session.exec(statement).first()
            if user:
                return User(
                    id=user.id,
                    username=user.username,
                    hashed_password=user.hashed_password,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                )
            return None