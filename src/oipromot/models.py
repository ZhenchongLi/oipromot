from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class PromptBase(SQLModel):
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Prompt(PromptBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)


class PromptCreate(PromptBase):
    pass


class PromptResponse(PromptBase):
    id: str