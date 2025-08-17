from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from .utils import get_chat_model
from .prompts import SUMMARY_PROMPT, SYSTEM_PROMPT, INSTRUCTIONS_PROMPT
from .settings import BaseSettings, Settings
from langsmith import traceable

# Create an instance of Settings
settings = Settings()

class SummaryResponse(BaseModel):
    summary: str = Field(description="Brief summary of user request")

@traceable
def get_chain():
    model = get_chat_model(temperature=0.3, model_name=settings.SMALL_TEXT_MODEL_NAME)
    summary = ChatPromptTemplate.from_messages([
        ("system", SUMMARY_PROMPT), 
        MessagesPlaceholder(variable_name="messages")
    ])
    return summary | model

@traceable
def get_code_response(summary: str = ""):
    model = get_chat_model(temperature=0.5, model_name=settings.TEXT_MODEL_NAME)
    code_response = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return code_response | model

@traceable
def get_fixer_chain():
    model = get_chat_model(temperature=0.5, model_name=settings.TEXT_MODEL_NAME)
    fixer_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a code-fixing AI. You will be given a piece of code, a failing test, and an error message. Your task is to fix the code so that it passes the test. You must return only the corrected code, enclosed in a markdown block. Do not include any other text, explanations, or apologies."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return fixer_prompt | model

@traceable
def get_instructions(code_gen: str = ""):
    model = get_chat_model(temperature=0.5, model_name=settings.TEXT_MODEL_NAME)
    instructions = ChatPromptTemplate.from_messages([
        ("system", INSTRUCTIONS_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return instructions | model
