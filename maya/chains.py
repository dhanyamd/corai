from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from .utils import get_chat_model
from .prompts import SUMMARY_PROMPT, SYSTEM_PROMPT, INSTRUCTIONS_PROMPT
from .settings import BaseSettings, Settings
from langsmith import traceable

# Create an instance of Settings
settings = Settings()

class SummaryResponse(BaseModel):
    """Response model for the summary generation chain.
    
    This model defines the structure of the output from the summary generation
    chain, which is used to create detailed summaries of user prompts for
    subsequent processing in later nodes of the application.
    """
    summary: str = Field(
        description="The summary should be detailed compared to the prompt given the original user. The summary must be generated from the prompt to feed into the later nodes"
    )

@traceable
def get_chain():
    """Create a chain for generating detailed summaries of user prompts.
    
    This function creates a processing chain that takes user messages and generates
    detailed summaries using a structured output model. The summaries are intended
    to be used as context for subsequent processing nodes.
    
    Returns:
        A LangChain chain that processes messages and returns a SummaryResponse.
    """
    model = get_chat_model(
       temperature=0.3,
       model_name=settings.SMALL_TEXT_MODEL_NAME
    )
    
    summary = ChatPromptTemplate.from_messages(
        [("system", SUMMARY_PROMPT), MessagesPlaceholder(variable_name="messages")]
    )

    return summary | model

@traceable
def get_code_response(summary: str = ""):
    """Create a chain for generating code responses based on a summary.
    
    This function creates a processing chain that generates code responses using
    a language model. If a summary is provided, it's included in the system
    message to provide context for the code generation.
    
    Args:
        summary (str, optional): A summary of the user's prompt or query to provide
            context for code generation. Defaults to "".
    
    Returns:
        A LangChain chain that generates code responses.
    """
    model = get_chat_model(
        temperature=0.5,
        model_name=settings.TEXT_MODEL_NAME
    )
    if summary:
        # Escape curly braces in the summary to avoid parsing errors
        # First, escape the SYSTEM_PROMPT's own template variables
        escaped_system_prompt = SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")
        # Then, escape the summary content
        escaped_summary = summary.replace("{", "{{").replace("}", "}}")
        system_message = escaped_system_prompt + f"\n\nThis is the summary of the user's prompt or query {escaped_summary}"
    else:
        system_message = SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")
    code_response = ChatPromptTemplate.from_messages([
        ("system", system_message)
    ])
    return code_response | model

@traceable
def get_instructions(code_gen: str = ""):
    """Create a chain for generating setup instructions based on generated code.
    
    This function creates a processing chain that generates instructions for
    installing dependencies and setting up environments based on previously
    generated code. If code_gen is provided, it's included in the system
    message to provide context for instruction generation.
    
    Args:
        code_gen (str, optional): Previously generated code to provide context
            for instruction generation. Defaults to "".
    
    Returns:
        A LangChain chain that generates setup instructions.
    """
    model = get_chat_model(
       temperature=0.5,
       model_name=settings.TEXT_MODEL_NAME
    )
    if code_gen:
        # Extract content from AIMessage object if needed
        if hasattr(code_gen, 'content'):
            code_gen_content = code_gen.content
        else:
            code_gen_content = str(code_gen)
            
        # Escape curly braces in the code_gen to avoid parsing errors
        # First, escape the INSTRUCTIONS_PROMPT's own template variables
        escaped_instructions_prompt = INSTRUCTIONS_PROMPT.replace("{", "{{").replace("}", "}}")
        # Then, escape the code_gen content
        escaped_code_gen = code_gen_content.replace("{", "{{").replace("}", "}}")
        system_message = escaped_instructions_prompt + f"\n\nThis is the code to be tested:\n{escaped_code_gen}"
    else:
        system_message = INSTRUCTIONS_PROMPT.replace("{", "{{").replace("}", "}}")
    instructions = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return instructions | model
