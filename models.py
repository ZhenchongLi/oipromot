#!/usr/bin/env python3
"""
Database models using SQLModel and DuckDB.
"""

import uuid
from typing import Optional, List
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


class FavoriteCommand(SQLModel, table=True):
    """Favorite command model for users."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    command: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


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
    
    def create_favorite_command(self, user_id: str, command: str, description: Optional[str] = None, category: Optional[str] = None) -> FavoriteCommand:
        """Create a new favorite command."""
        favorite = FavoriteCommand(
            user_id=user_id,
            command=command,
            description=description,
            category=category
        )
        
        with self.get_session() as session:
            session.add(favorite)
            session.commit()
            session.refresh(favorite)
            return favorite
    
    def get_user_favorite_commands(self, user_id: str) -> List[FavoriteCommand]:
        """Get all favorite commands for a user."""
        with self.get_session() as session:
            statement = select(FavoriteCommand).where(FavoriteCommand.user_id == user_id).order_by(FavoriteCommand.created_at.desc())
            favorites = session.exec(statement).all()
            return [FavoriteCommand(
                id=fav.id,
                user_id=fav.user_id,
                command=fav.command,
                description=fav.description,
                category=fav.category,
                created_at=fav.created_at,
                updated_at=fav.updated_at
            ) for fav in favorites]
    
    def get_favorite_command_by_id(self, favorite_id: str, user_id: str) -> Optional[FavoriteCommand]:
        """Get favorite command by ID for a specific user."""
        with self.get_session() as session:
            statement = select(FavoriteCommand).where(
                FavoriteCommand.id == favorite_id,
                FavoriteCommand.user_id == user_id
            )
            favorite = session.exec(statement).first()
            if favorite:
                return FavoriteCommand(
                    id=favorite.id,
                    user_id=favorite.user_id,
                    command=favorite.command,
                    description=favorite.description,
                    category=favorite.category,
                    created_at=favorite.created_at,
                    updated_at=favorite.updated_at
                )
            return None
    
    def update_favorite_command(self, favorite_id: str, user_id: str, command: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None) -> Optional[FavoriteCommand]:
        """Update a favorite command."""
        with self.get_session() as session:
            statement = select(FavoriteCommand).where(
                FavoriteCommand.id == favorite_id,
                FavoriteCommand.user_id == user_id
            )
            favorite = session.exec(statement).first()
            
            if favorite:
                if command is not None:
                    favorite.command = command
                if description is not None:
                    favorite.description = description
                if category is not None:
                    favorite.category = category
                favorite.updated_at = datetime.now()
                
                session.add(favorite)
                session.commit()
                session.refresh(favorite)
                return FavoriteCommand(
                    id=favorite.id,
                    user_id=favorite.user_id,
                    command=favorite.command,
                    description=favorite.description,
                    category=favorite.category,
                    created_at=favorite.created_at,
                    updated_at=favorite.updated_at
                )
            return None
    
    def delete_favorite_command(self, favorite_id: str, user_id: str) -> bool:
        """Delete a favorite command."""
        with self.get_session() as session:
            statement = select(FavoriteCommand).where(
                FavoriteCommand.id == favorite_id,
                FavoriteCommand.user_id == user_id
            )
            favorite = session.exec(statement).first()
            
            if favorite:
                session.delete(favorite)
                session.commit()
                return True
            return False
    
    def check_favorite_exists(self, user_id: str, command: str) -> bool:
        """Check if a command is already favorited by user."""
        with self.get_session() as session:
            statement = select(FavoriteCommand).where(
                FavoriteCommand.user_id == user_id,
                FavoriteCommand.command == command
            )
            return session.exec(statement).first() is not None