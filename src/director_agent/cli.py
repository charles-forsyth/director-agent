import typer
import logging
from typing import Optional
from pathlib import Path
from director_agent.core import Director
from director_agent.config import settings

app = typer.Typer(help="🎬 Director Agent: Autonomous Movie Studio")

@app.command()
def action(
    topic: str = typer.Argument(..., help="The topic or concept for the movie"),
    output_dir: Optional[Path] = typer.Option(None, help="Directory to save the movie"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """
    Lights, Camera, Action! Creates a complete movie from a single topic.
    """
    if verbose:
        logging.basicConfig(level=logging.INFO)
    
    if output_dir:
        settings.OUTPUT_DIR = output_dir

    director = Director()
    try:
        final_movie = director.create_movie(topic)
        typer.secho(f"\n✨ Movie Premiere: {final_movie}", fg=typer.colors.GREEN, bold=True)
    except Exception as e:
        typer.secho(f"\n💥 Production Failed: {e}", fg=typer.colors.RED)
        if verbose:
            raise

if __name__ == "__main__":
    app()
