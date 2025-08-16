from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class CoraiAgentState(TypedDict):
    messages: List[BaseMessage]
    summary: str
    code: str
    sandbox_response: Optional[dict]
    sandbox_response_err: Optional[dict]
    final_response: Optional[dict]
