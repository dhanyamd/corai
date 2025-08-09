from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    # Required API Keys
    GROQ_API_KEY: str = Field(..., description="Groq API key for language models")
    TEXT_MODEL_NAME: str = Field(default="llama2-70b-4096", description="Main text model")
    SMALL_TEXT_MODEL_NAME: str = Field(default="llama2-13b-4096", description="Smaller text model")