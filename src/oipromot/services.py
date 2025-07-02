from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from .config import settings


class LangChainService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.7
        )
    
    async def process_message(self, message: str) -> str:
        messages = [HumanMessage(content=message)]
        response = await self.llm.ainvoke(messages)
        return response.content