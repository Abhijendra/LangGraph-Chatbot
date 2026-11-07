from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator, SecretStr
from typing import Literal
from pathlib import Path
from enum import Enum

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings(BaseSettings):

    # ==========================================
    # 1. Project & Environment Configuration
    # ==========================================
    PROJECT_NAME: str = "LangGraph FastAPI Chatbot"
    VERSION: str = "0.1.0"
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    DEBUG: bool = False

    # CORS Origins (Decoded from a comma-separated string)
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return []

    # ==========================================
    # 2. Database & Checkpointer Configuration
    # ==========================================
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    
    # Controls which checkpointer backend to use for LangGraph memory
    CHECKPOINTER_TYPE: Literal["memory", "sqlite", "postgres"] = "sqlite"


    # ==========================================
    # 3. LLM Provider API Keys & Settings
    # ==========================================
    # SecretStr masks keys in logs/exceptions to prevent accidental leakage
    OPENAI_API_KEY: SecretStr | None = None
    GOOGLE_API_KEY: SecretStr | None = None
    
    DEFAULT_MODEL_NAME: str = "gpt-5-nano"
    MODEL_TEMPERATURE: float = 0.0


    # ==========================================
    # 4. Pydantic Settings Rules
    # ==========================================
    model_config = SettingsConfigDict(
        # Tells pydantic to load from a .env file if it exists
        env_file=BASE_DIR / ".env", 
        # Extra environments variables are ignored rather than raising errors
        extra="ignore",
        # Allows nested configuration parsing if needed
        case_sensitive=True
    )

# Pydantic will read from the environment first, then fallback to .env, then defaults
settings = Settings()