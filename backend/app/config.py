from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and environment configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = 8000
    host: str = "0.0.0.0"

    # Three configurable models for LiteLLM routing
    model_1: str = Field(
        default="groq/llama-3.3-70b-versatile",
        description="Primary model for general reasoning",
    )
    model_2: str = Field(
        default="gemini/gemini-1.5-flash",
        description="Secondary model for heavy research tasks",
    )
    model_3: str = Field(
        default="openai/gpt-4o-mini",
        description="Fallback model",
    )

    # Agent constraints
    max_tool_calls: int = Field(default=5, description="Maximum tool calls allowed per run")

    # Tool credentials (optional based on active tools)
    weather_api_key: str = Field(default="", description="Optional weather API key")
    tavily_api_key: str = Field(default="", description="Optional search API key")


settings = Settings()
