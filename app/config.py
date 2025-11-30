from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # APP CONFIG
    APP_NAME: str = "Productivity Rule Engine + LLM"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment: dev, staging, prod")

    # REDIS CONFIG
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database index")
    REDIS_PASSWORD: str | None = Field(default=None, description="Password if Redis is secured")

    # Cache expiry for LLM responses (seconds)
    CACHE_EXPIRE_SECONDS: int = Field(default=3600, description="1 hour default LLM cache TTL")

    # LLM CONFIG
    LLM_API_KEY: str = Field(..., description="OpenAI or Groq API key")  # required
    LLM_MODEL: str = Field(default="gpt-4.1", description="Default model")
    LLM_TEMPERATURE: float = Field(default=0.0, description="Deterministic insights")
    LLM_MAX_TOKENS: int = Field(default=512)
    LLM_RETRIES: int = Field(default=2)
    LLM_TIMEOUT: int = Field(default=25)

    # RATE LIMITING
    RATE_LIMIT: str = Field(default="5/minute")

    # PRODUCTIVITY THRESHOLDS
    TARGET_DEEP_WORK: int = Field(default=90, description="Target deep work minutes per day")
    TARGET_SLEEP: float = Field(default=7.5, description="Target sleep hours per day")
    MAX_INTERRUPTION: int = Field(default=20, description="Maximum healthy interruptions per day")
    MAX_MEETINGS: int = Field(default=180, description="Maximum healthy meeting minutes per day")

    # Pydantic v2 config
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

# Cached settings instance
@lru_cache()
def get_settings() -> Settings:
    return Settings()
