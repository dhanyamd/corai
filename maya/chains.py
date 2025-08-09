from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from .utils import get_chat_model
from .prompts import SUMMARY_PROMPT, SYSTEM_PROMPT
from .settings import BaseSettings, Settings
class SummaryResponse(BaseModel): 
    summary: str = Field(
        description="The summary should be detailed compared to the prompt given the original user. The summary must be generated from the prompt to feed into the later nodes"
    )

def get_chain(): 
    """
    
    """
    model = get_chat_model(
       temperature=0.3,
       model_name=Settings.SMALL_TEXT_MODEL_NAME
    ).with_structured_output(SummaryResponse)
    
    summary = ChatPromptTemplate.from_messages(
        [("system", SUMMARY_PROMPT), MessagesPlaceholder(variable_name="messages")]
    ) 

    return summary | model

def get_code_response(summary: str = ""): 
   """
   
   """
   model = get_chat_model(
       temperature=0.5,
       model_name=Settings.TEXT_MODEL_NAME
   )
   code_response = ChatPromptTemplate.from_messages([
       "system", SYSTEM_PROMPT
   ])
   return code_response | model 