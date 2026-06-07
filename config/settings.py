from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING     = "staging"      
    PRODUCTION  = "production"   


class Settings(BaseSettings):
 
    env: str = Environment.DEVELOPMENT
 
    log_level: str = "DEBUG"
 
    api_timeout:       int = 10
    api_retry_count:   int = 3
    api_retry_backoff: int = 2
 
    postgres_host:     str
    postgres_port:     int
    postgres_db:       str
    postgres_user:     str
    postgres_password: str = Field(repr=False)   

    class Config:
        env_file          = ".env"
        env_file_encoding = "utf-8"
        case_sensitive    = False

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_production(self) -> bool:
        """Convenience check — use this to guard destructive operations."""
        return self.env == Environment.PRODUCTION


@lru_cache()
def get_settings() -> Settings:
    return Settings()