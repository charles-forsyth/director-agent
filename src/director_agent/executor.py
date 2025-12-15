import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

from director_agent.config import settings
from director_agent.core import ProductionManifest, Scene

class Executor:
    def __init__(self):
        pass

    def produce_assets(self, manifest: ProductionManifest) -> Dict[int, Dict[str, Path]]:
        """
        Parallel execution of asset generation tools.
        """
        assets = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_scene = {
                executor.submit(self._produce_scene_assets, scene): scene.id 
                for scene in manifest.scenes
            }
            
            for future in as_completed(future_to_scene):
                scene_id = future_to_scene[future]
                try:
                    scene_assets = future.result()
                    assets[scene_id] = scene_assets
                except Exception as e:
                    print(f"Error producing scene {scene_id}: {e}")
                    # TODO: Implement retry or fallback logic
        return assets

    def _produce_scene_assets(self, scene: Scene) -> Dict[str, Path]:
        """
        Generates Video, Audio, and Music for a single scene.
        """
        print(f"🎬 Scene {scene.id}: Starting production...")
        scene_dir = settings.TEMP_DIR / f"scene_{scene.id}"
        scene_dir.mkdir(exist_ok=True)
        
        # 1. Video (Veo)
        video_path = scene_dir / "video.mp4"
        if not video_path.exists():
            self._run_veo(scene.visual_prompt, scene.duration, video_path)

        # 2. Audio (TTS)
        audio_path = scene_dir / "narration.mp3"
        if not audio_path.exists() and scene.narration_text:
            self._run_tts(scene.narration_text, scene.voice_id, audio_path)

        # 3. Music (Gen-Music)
        music_path = scene_dir / "score.mp3"
        if not music_path.exists() and scene.music_prompt:
            self._run_music(scene.music_prompt, scene.duration, music_path)
            
        return {
            "video": video_path,
            "audio": audio_path,
            "music": music_path
        }

    def _run_veo(self, prompt: str, duration: int, output_path: Path):
        cmd = [
            settings.VEO_CMD,
            prompt,
            "--duration", str(duration),
            "--aspect-ratio", "16:9",
            "--output-file", str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def _run_tts(self, text: str, voice: str, output_path: Path):
        cmd = [
            settings.TTS_CMD,
            text,
            "--voice-name", voice,
            "--output-file", str(output_path),
            "--audio-format", "MP3"
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def _run_music(self, prompt: str, duration: int, output_path: Path):
        cmd = [
            settings.MUSIC_CMD,
            prompt,
            "--duration", str(duration),
            "--output", str(output_path),
            "--format", "mp3"
        ]
        subprocess.run(cmd, check=True, capture_output=True)
