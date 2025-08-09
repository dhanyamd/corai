from langchain_core.prompts import ChatPromptTemplate. MessagesPlaceholder
from pydantic import BaseModel, Field
from .utils import get_chat_model

class SummaryResponse(BaseModel): 
    summary: str = Field(
        description="The summary should be detailed compared to the prompt given the original user. The summary must be generated from the prompt to feed into the later nodes"
    )

def get_chain(): 
    model = get_chat_model(
       temperature=0.3,
       model_name=settings.TEXT__MODEL
    ).with_structured_output(SummaryResponse): 
    
    