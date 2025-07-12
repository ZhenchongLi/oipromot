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
from logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class User(SQLModel, table=True):
    """User model for authentication."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = Field(default=None)


class Conversation(SQLModel, table=True):
    """Conversation model for storing user chat sessions."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    session_id: str = Field(index=True)
    title: Optional[str] = Field(default=None)
    status: str = Field(default="active")  # active, completed, archived
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ConversationMessage(SQLModel, table=True):
    """Individual messages within a conversation."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: str = Field(index=True)  # user, assistant, system
    content: str
    message_metadata: Optional[str] = Field(default=None)  # JSON string for additional data
    created_at: datetime = Field(default_factory=datetime.now)


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
        logger.info("Initializing DatabaseManager")
        self.engine = create_engine(db_config.database_url)
        logger.info(f"Database connection established: {db_config.database_url}")
        self.create_tables()
    
    def create_tables(self):
        """Create database tables."""
        logger.info("Creating database tables")
        SQLModel.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
    
    def get_session(self) -> Session:
        """Get database session."""
        return Session(self.engine)
    
    def create_user(self, username: str, password: str) -> User:
        """Create a new user."""
        logger.info(f"Creating new user: {username}")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(username=username, hashed_password=hashed_password)
        
        with self.get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"User created successfully: {username} (ID: {user.id})")
            return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        logger.debug(f"Authenticating user: {username}")
        
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
                logger.info(f"User authenticated successfully: {username} (ID: {user.id})")
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
            logger.warning(f"Authentication failed for user: {username}")
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
        logger.info(f"Creating favorite command for user {user_id}: {command}")
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
            logger.info(f"Favorite command created successfully (ID: {favorite.id})")
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
        logger.info(f"Deleting favorite command {favorite_id} for user {user_id}")
        
        with self.get_session() as session:
            statement = select(FavoriteCommand).where(
                FavoriteCommand.id == favorite_id,
                FavoriteCommand.user_id == user_id
            )
            favorite = session.exec(statement).first()
            
            if favorite:
                session.delete(favorite)
                session.commit()
                logger.info(f"Favorite command deleted successfully: {favorite_id}")
                return True
            logger.warning(f"Favorite command not found for deletion: {favorite_id}")
            return False
    
    def check_favorite_exists(self, user_id: str, command: str) -> bool:
        """Check if a command is already favorited by user."""
        with self.get_session() as session:
            statement = select(FavoriteCommand).where(
                FavoriteCommand.user_id == user_id,
                FavoriteCommand.command == command
            )
            return session.exec(statement).first() is not None
    
    def create_conversation(self, user_id: str, session_id: str, title: Optional[str] = None) -> Conversation:
        """Create a new conversation."""
        logger.info(f"Creating conversation for user {user_id}, session {session_id}")
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            title=title
        )
        
        with self.get_session() as session:
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            logger.info(f"Conversation created successfully (ID: {conversation.id})")
            return conversation
    
    def get_conversation_by_session_id(self, user_id: str, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID for a specific user."""
        with self.get_session() as session:
            statement = select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.session_id == session_id
            )
            conversation = session.exec(statement).first()
            if conversation:
                return Conversation(
                    id=conversation.id,
                    user_id=conversation.user_id,
                    session_id=conversation.session_id,
                    title=conversation.title,
                    status=conversation.status,
                    created_at=conversation.created_at,
                    updated_at=conversation.updated_at
                )
            return None
    
    def save_message(self, conversation_id: str, role: str, content: str, message_metadata: Optional[str] = None) -> ConversationMessage:
        """Save a message to a conversation."""
        logger.debug(f"Saving {role} message to conversation {conversation_id}")
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_metadata=message_metadata
        )
        
        with self.get_session() as session:
            session.add(message)
            session.commit()
            session.refresh(message)
            return message
    
    def get_conversation_messages(self, conversation_id: str) -> List[ConversationMessage]:
        """Get all messages for a conversation."""
        with self.get_session() as session:
            statement = select(ConversationMessage).where(
                ConversationMessage.conversation_id == conversation_id
            ).order_by(ConversationMessage.created_at)
            messages = session.exec(statement).all()
            return [ConversationMessage(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                message_metadata=msg.message_metadata,
                created_at=msg.created_at
            ) for msg in messages]
    
    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user."""
        with self.get_session() as session:
            statement = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc()).limit(limit)
            conversations = session.exec(statement).all()
            return [Conversation(
                id=conv.id,
                user_id=conv.user_id,
                session_id=conv.session_id,
                title=conv.title,
                status=conv.status,
                created_at=conv.created_at,
                updated_at=conv.updated_at
            ) for conv in conversations]
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title."""
        with self.get_session() as session:
            statement = select(Conversation).where(Conversation.id == conversation_id)
            conversation = session.exec(statement).first()
            
            if conversation:
                conversation.title = title
                conversation.updated_at = datetime.now()
                session.add(conversation)
                session.commit()
                return True
            return False