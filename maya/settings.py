from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    # Required API Keys
    GROQ_API_KEY: str = Field(..., description="Groq API key for language models")
    LANGSMITH_API_KEY: str = Field(default="", description="LangSmith API key for tracing")
    LANGSMITH_TRACING: bool = Field(default=True, description="Enable LangSmith tracing")
    LANGSMITH_PROJECT: str = Field(default="maya", description="LangSmith project name")
    E2B_API_KEY: str = Field(default="", description="E2B API key for sandbox execution")
    TEXT_MODEL_NAME: str = Field(default="llama3-70b-8192", description="Main text model")
    SMALL_TEXT_MODEL_NAME: str = Field(default="llama3-8b-8192", description="Smaller text model")

    def configure_langsmith(self):
        """Configure LangSmith environment variables."""
        if self.LANGSMITH_API_KEY:
            os.environ["LANGSMITH_API_KEY"] = self.LANGSMITH_API_KEY
        os.environ["LANGSMITH_TRACING"] = str(self.LANGSMITH_TRACING).lower()
        os.environ["LANGSMITH_PROJECT"] = self.LANGSMITH_PROJECT