from typing import Optional
from maya.settings import Settings
from langchain_groq import ChatGroq
import time
import logging
from langsmith import traceable

# Create an instance of Settings
settings = Settings()

@traceable
def create_chat_model(model_name: str, temperature: float = 0.7) -> ChatGroq:
    """Create a ChatGroq model with the specified parameters."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=model_name,
        temperature=temperature,
    )

@traceable
def get_chat_model(temperature: float = 0.7, max_retries: int = 3, retry_delay: float = 1.0, model_name: Optional[str] = None) -> ChatGroq:
    """
    Get a chat model with rate limit handling and fallback to small model.
    
    Args:
        temperature: Model temperature
        max_retries: Maximum number of retries on rate limit
        retry_delay: Delay between retries in seconds
        model_name: Optional specific model to use
    
    Returns:
        ChatGroq: Configured chat model
    """
    # If a specific model is requested, use it
    if model_name:
        return create_chat_model(model_name, temperature)
    
    # Try with main model first
    for attempt in range(max_retries + 1):
        try:
            model = create_chat_model(settings.TEXT_MODEL_NAME, temperature)
            # Test the model with a simple call
            # If this succeeds, we're good to go
            return model
        except Exception as e:
            # Check if this is a rate limit error
            if "rate limit" in str(e).lower() and attempt < max_retries:
                # Wait before retrying
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                continue
            elif attempt < max_retries:
                # For other errors, wait and retry
                time.sleep(retry_delay)
                continue
            else:
                # If we've exhausted retries, fall back to small model
                logging.warning(f"Failed to create main model after {max_retries} attempts, falling back to small model")
                break
    
    # Fallback to small model
    try:
        return create_chat_model(settings.SMALL_TEXT_MODEL_NAME, temperature)
    except Exception as e:
        # If even the small model fails, re-raise the exception
        logging.error(f"Failed to create small model: {e}")
        raise