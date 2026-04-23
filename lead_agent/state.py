from typing import List, Literal, TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class AgentState(TypedDict):
    lead: dict
    intent: Literal["greeting", "inquiry", "high_intent"]
    rag_context: str
    messages: List[BaseMessage]


class RouterDecision(BaseModel):
    intent: Literal["greeting", "high_intent", "inquiry"]
