import os
from pathlib import Path
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration loading from environment variables and .env files.
    Prioritizes:
    1. Environment variables
    2. Local .env file
    3. XDG Config .env file (~/.config/director-agent/.env)
    """
    
    # Core API Keys
    GEMINI_API_KEY: SecretStr = Field(..., description="API Key for Gemini models")
    
    # Tool Paths (Optional override, defaults to PATH lookups)
    DEEP_RESEARCH_CMD: str = "deep-research"
    VEO_CMD: str = "generate-veo"
    TTS_CMD: str = "gen-tts"
    MUSIC_CMD: str = "gen-music"
    IMAGE_CMD: str = "generate-gemini-image"
    
    # Project Settings
    OUTPUT_DIR: Path = Field(default=Path.home() / "Movies", description="Default output directory for movies")
    TEMP_DIR: Path = Field(default=Path("/tmp/director_agent"), description="Temporary working directory")

    model_config = SettingsConfigDict(
        env_file=[
            os.path.expanduser("~/.config/director-agent/.env"),
            ".env"
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def ensure_dirs(self):
        """Ensure critical directories exist."""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Singleton instance
settings = Settings()
