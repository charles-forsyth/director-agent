import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# We need to configure settings before importing Director to ensure
# env vars are loaded or first-run check happens.
from director_agent.config import settings
from director_agent.core import Director

def main():
    parser = argparse.ArgumentParser(
        description="Lights, Camera, Action! Creates a complete movie from a single topic.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "topic",
        help="The topic or concept for the movie"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        help="Directory to save the movie",
        default=None
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    # 1. Check for First Run / Missing Config
    # This might exit if setup is needed
    settings.check_setup()

    if args.output_dir:
        settings.OUTPUT_DIR = args.output_dir

    director = Director()
    
    try:
        final_movie = director.create_movie(args.topic)
        # using print instead of typer.secho
        print(f"\n✨ Movie Premiere: {final_movie}")
    except Exception as e:
        print(f"\n💥 Production Failed: {e}", file=sys.stderr)
        if args.verbose:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()