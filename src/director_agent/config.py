import os
import sys
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel

APP_NAME = "director-agent"
APP_CONFIG_DIR = Path.home() / ".config" / APP_NAME
APP_CONFIG_FILE = APP_CONFIG_DIR / ".env"

console = Console()

class Settings(BaseSettings):
    """
    Application configuration.
    """
    
    # Core API Keys (Optional to allow app to start and run setup wizard)
    GEMINI_API_KEY: Optional[SecretStr] = Field(None, description="API Key for Gemini models")
    
    # Tool Paths
    DEEP_RESEARCH_CMD: str = "deep-research"
    VEO_CMD: str = "generate-veo"
    TTS_CMD: str = "gen-tts"
    MUSIC_CMD: str = "gen-music"
    IMAGE_CMD: str = "generate-gemini-image"
    
    # Project Settings
    OUTPUT_DIR: Path = Field(default=Path.home() / "Movies", description="Default output directory for movies")
    
    # We define a base temp dir, but individual runs will create subdirs
    BASE_TEMP_DIR: Path = Field(default=Path(f"/tmp/{APP_NAME}"), description="Base temporary directory")
    
    # This will be set dynamically per run
    RUN_TEMP_DIR: Optional[Path] = None

    model_config = SettingsConfigDict(
        env_file=[
            APP_CONFIG_FILE,
            ".env"
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def init_run(self):
        """
        Initializes a unique temporary directory for this specific execution context.
        Call this at the start of the CLI.
        """
        run_id = f"run_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}_{{uuid.uuid4().hex[:6]}}"
        self.RUN_TEMP_DIR = self.BASE_TEMP_DIR / run_id
        self.RUN_TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return self.RUN_TEMP_DIR

    def check_setup(self):
        """
        Checks if the API key is set. If not, performs first-run setup.
        """
        if self.GEMINI_API_KEY is None:
            self._run_first_setup()
            sys.exit(0) # Stop execution so user can edit file

    def _run_first_setup(self):
        """Creates the config directory and a template .env file."""
        APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        if not APP_CONFIG_FILE.exists():
            content = (
                f"# {APP_NAME} Configuration\n"
                f"# Get your Gemini API key from: https://aistudio.google.com/app/apikey\n"
                f"GEMINI_API_KEY=your_api_key_here\n\n"
                f"# Optional Overrides\n"
                f"# OUTPUT_DIR={{Path.home()}}/Movies\n"
            )
            APP_CONFIG_FILE.write_text(content)
            # Set permissions to 600 (read/write only by owner)
            APP_CONFIG_FILE.chmod(0o600)
            
            console.print(Panel(
                f"[bold green]✨ Welcome to {APP_NAME}![/bold green]\n\n"
                f"I have created a configuration file for you at:\n"
                f"[bold cyan]{APP_CONFIG_FILE}[/bold cyan]\n\n"
                f"[yellow]Action Required:[/yellow] Please open this file and paste your GEMINI_API_KEY.",
                title="First Run Setup",
                expand=False
            ))
        else:
            # File exists but key is missing/null in the loaded settings
            console.print(Panel(
                f"[bold red]❌ Configuration Error[/bold red]\n\n"
                f"The GEMINI_API_KEY is missing or invalid.\n"
                f"Please check your config file:\n"
                f"[bold cyan]{APP_CONFIG_FILE}[/bold cyan]",
                expand=False
            ))

# Singleton instance
settings = Settings()