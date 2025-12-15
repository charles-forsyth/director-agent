import logging
from pathlib import Path
from typing import Dict
from director_agent.config import settings
from director_agent.planner import Planner
from director_agent.executor import Executor
from director_agent.editor import Editor
from director_agent.core import ProductionManifest # Import definition

# --- Core Director Class ---

class Director:
    def __init__(self):
        self.logger = logging.getLogger("director_agent")
        settings.ensure_dirs()
        self.planner = Planner()
        self.executor = Executor()
        self.editor = Editor()

    def create_movie(self, topic: str) -> Path:
        """
        Orchestrates the entire movie creation process.
        """
        self.logger.info(f"🎬 Starting production for topic: {topic}")

        # 1. Plan
        manifest = self.plan(topic)
        self.logger.info(f"📝 Plan created: {manifest.title} ({len(manifest.scenes)} scenes)")

        # 2. Execute (Generate Assets)
        assets = self.execute(manifest)
        
        # 3. Assemble (Edit)
        movie_path = self.assemble(manifest, assets)
        
        self.logger.info(f"✅ Production complete: {movie_path}")
        return movie_path

    def plan(self, topic: str) -> ProductionManifest:
        return self.planner.generate_manifest(topic)

    def execute(self, manifest: ProductionManifest) -> Dict[int, Dict[str, Path]]:
        return self.executor.produce_assets(manifest)

    def assemble(self, manifest: ProductionManifest, assets: Dict[int, Dict[str, Path]]) -> Path:
        output_file = settings.OUTPUT_DIR / f"{manifest.title.replace(' ', '_')}.mp4"
        return self.editor.assemble(manifest, assets, output_file)