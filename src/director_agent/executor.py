import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

from director_agent.config import settings
from director_agent.models import ProductionManifest, Scene

class Executor:
    def __init__(self):
        self.reference_cache: Dict[str, Path] = {}

    def produce_assets(self, manifest: ProductionManifest) -> Dict[int, Dict[str, Path]]:
        # 1. Pre-generate References (if any)
        for scene in manifest.scenes:
            if scene.reference_group and scene.reference_prompt and scene.reference_group not in self.reference_cache:
                self._generate_reference(scene.reference_group, scene.reference_prompt)
        
        # 2. Produce Scenes
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
        return assets

    def _generate_reference(self, group_name: str, prompt: str):
        print(f"🎨 Generating Reference Asset: '{group_name}'...")
        ref_path = settings.RUN_TEMP_DIR / f"ref_{group_name}.png"
        
        if not ref_path.exists():
            cmd = [
                settings.IMAGE_CMD,
                "--prompt", prompt,
                "--output-dir", str(ref_path.parent),
                "--filename", ref_path.name,
                "--count", "1",
                "--style", "Cinematic", # References usually default to Cinematic unless specified
                "--image-size", "4K",
                "--aspect-ratio", "16:9"
            ]
            self._run_tool(cmd, ref_path)
            
        self.reference_cache[group_name] = ref_path

    def _produce_scene_assets(self, scene: Scene) -> Dict[str, Path]:
        print(f"🎬 Scene {scene.id} ({scene.image_style}): Starting...")
        scene_dir = settings.RUN_TEMP_DIR / f"scene_{scene.id}"
        scene_dir.mkdir(exist_ok=True, parents=True)
        
        assets = {"type": scene.visual_type}

        # --- Visuals ---
        assets["image"] = scene_dir / "image.png"
        if not assets["image"].exists():
            # Use the specific style requested by the Planner
            self._run_image_gen(scene.visual_prompt, assets["image"], scene.image_style)

        # --- Audio ---
        if scene.narration_text:
            assets["audio"] = scene_dir / "narration.mp3"
            if not assets["audio"].exists():
                self._run_tts(scene.narration_text, scene.voice_id, assets["audio"])
        
        if scene.music_prompt:
            assets["music"] = scene_dir / "score.mp3"
            if not assets["music"].exists():
                self._run_music(scene.music_prompt, scene.duration, assets["music"])
        
        return assets

    # --- Tool Wrappers ---
    def _run_tool(self, cmd: list, output_path: Path):
        print(f"  Running: {' '.join(cmd)}")
        try:
            # capture_output=True captures both stdout and stderr
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ❌ Tool Failed (Exit Code {result.returncode})")
                print(f"  STDOUT: {result.stdout}")
                print(f"  STDERR: {result.stderr}")
                raise RuntimeError(f"Tool execution failed: {cmd[0]}")
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                print(f"  ❌ Tool finished (Exit 0) but output missing: {output_path}")
                print(f"  STDOUT: {result.stdout}")
                print(f"  STDERR: {result.stderr}")
                raise RuntimeError(f"Tool produced no output: {cmd[0]}")
                
        except Exception as e:
            print(f"  ❌ Execution Error: {e}")
            raise

    def _run_image_gen(self, prompt: str, output_path: Path, style: str):
        cmd = [
            settings.IMAGE_CMD,
            "--prompt", prompt,
            "--output-dir", str(output_path.parent),
            "--filename", output_path.name,
            "--count", "1",
            "--style", style,  # Dynamic Style!
            "--image-size", "4K",
            "--aspect-ratio", "16:9"
        ]
        self._run_tool(cmd, output_path)

    def _run_tts(self, text: str, voice: str, output_path: Path):
        cmd = [
            settings.TTS_CMD,
            text,
            "--voice-name", voice,
            "--output-file", str(output_path),
            "--audio-format", "MP3"
        ]
        self._run_tool(cmd, output_path)

    def _run_music(self, prompt: str, duration: int, output_path: Path):
        cmd = [
            settings.MUSIC_CMD,
            prompt,
            "--duration", str(duration),
            "--output", str(output_path),
            "--format", "mp3"
        ]
        self._run_tool(cmd, output_path)
