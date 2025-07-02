from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from .database import get_session
from .models import Prompt, PromptCreate, PromptResponse
from .services import LangChainService

router = APIRouter()


@router.post("/prompts", response_model=PromptResponse)
async def create_prompt(
    prompt: PromptCreate,
    session: Session = Depends(get_session)
):
    db_prompt = Prompt.model_validate(prompt)
    session.add(db_prompt)
    session.commit()
    session.refresh(db_prompt)
    return db_prompt


@router.get("/prompts", response_model=List[PromptResponse])
async def get_prompts(session: Session = Depends(get_session)):
    prompts = session.exec(select(Prompt)).all()
    return prompts


@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: str, session: Session = Depends(get_session)):
    prompt = session.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.post("/chat")
async def chat_with_langchain(
    message: str,
    langchain_service: LangChainService = Depends()
):
    response = await langchain_service.process_message(message)
    return {"response": response}