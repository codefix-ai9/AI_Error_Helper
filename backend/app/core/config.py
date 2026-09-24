import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""
    AI_TIMEOUT_S: int = 10
    AI_TOTAL_TIMEOUT_S: int = 30
    MAX_SOURCE_CHARS: int = 20000
    MAX_ERROR_CHARS: int = 10000
    ENABLE_TOOLCHAIN_CHECKS: bool = False
    LOG_AI_PAYLOADS: bool = False
    CORS_ORIGINS: str = "http://localhost:5173"
    DB_PATH: str = "sqlite:///./data/app.db"
    VITE_API_BASE_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()
