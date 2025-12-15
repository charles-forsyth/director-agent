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
        """
        Orchestrates asset generation.
        """
        # 1. Pre-generate References
        # We scan for scenes that define a new reference_prompt
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
        """Generates and caches a reference image."""
        print(f"🎨 Generating Reference Asset: '{group_name}'...")
        ref_path = settings.TEMP_DIR / f"ref_{group_name}.png"
        
        if not ref_path.exists():
            cmd = [
                settings.IMAGE_CMD,
                "--prompt", prompt,
                "--output-dir", str(ref_path.parent),
                "--filename", ref_path.name,
                "--count", "1",
                "--style", "Cinematic",
                "--image-size", "4K",
                "--aspect-ratio", "16:9"
            ]
            print(f"  [MOCK] Running ImageGen (Ref): {' '.join(cmd)}")
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=green:s=3840x2160",
                "-frames:v", "1", str(ref_path)
            ], check=True, capture_output=True)
            
        self.reference_cache[group_name] = ref_path

    def _produce_scene_assets(self, scene: Scene) -> Dict[str, Path]:
        print(f"🎬 Scene {scene.id} ({scene.visual_type}): Starting...")
        scene_dir = settings.TEMP_DIR / f"scene_{scene.id}"
        scene_dir.mkdir(exist_ok=True, parents=True)
        
        assets = {"type": scene.visual_type}

        # --- Visuals ---
        if scene.visual_type == "video":
            assets["video"] = scene_dir / "video.mp4"
            ref_image = self.reference_cache.get(scene.reference_group) if scene.reference_group else None
            if not assets["video"].exists():
                self._run_veo(scene.visual_prompt, scene.duration, assets["video"], ref_image)
        else:
            assets["image"] = scene_dir / "image.png"
            if not assets["image"].exists():
                self._run_image_gen(scene.visual_prompt, assets["image"])

        # --- Audio ---
        if scene.audio_source == "generated":
            if scene.narration_text:
                assets["audio"] = scene_dir / "narration.mp3"
                if not assets["audio"].exists():
                    self._run_tts(scene.narration_text, scene.voice_id, assets["audio"])
            
            if scene.music_prompt:
                assets["music"] = scene_dir / "score.mp3"
                if not assets["music"].exists():
                    self._run_music(scene.music_prompt, scene.duration, assets["music"])
        
        # If audio_source is 'native' (Veo), we don't generate separate audio tracks
        # The Editor will use the audio inside the video.mp4

        return assets

    # --- Tool Wrappers (Mocked for safety/speed in this env) ---
    def _run_veo(self, prompt: str, duration: int, output_path: Path, ref_image: Optional[Path]):
        cmd = [settings.VEO_CMD, prompt, "--duration", str(duration), "--aspect-ratio", "16:9", "--output-file", str(output_path)]
        if ref_image: cmd.extend(["--ref-images", str(ref_image)])
        
        print(f"  [MOCK] Running Veo: {' '.join(cmd)}")
        # Generate 1080p video with sine wave audio (representing Native Veo Audio)
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"testsrc=duration={duration}:size=1920x1080:rate=30",
            "-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration}", 
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(output_path)
        ], check=True, capture_output=True)

    def _run_image_gen(self, prompt: str, output_path: Path):
        print(f"  [MOCK] Running ImageGen: {prompt[:20]}...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=3840x2160",
            "-frames:v", "1", str(output_path)
        ], check=True, capture_output=True)

    def _run_tts(self, text: str, voice: str, output_path: Path):
        print(f"  [MOCK] Running TTS...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=2", str(output_path)
        ], check=True, capture_output=True)

    def _run_music(self, prompt: str, duration: int, output_path: Path):
        print(f"  [MOCK] Running Music...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=220:duration={duration}", str(output_path)
        ], check=True, capture_output=True)