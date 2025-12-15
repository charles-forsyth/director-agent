import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

from director_agent.config import settings
from director_agent.models import ProductionManifest, Scene

class Executor:
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
        return assets

    def _produce_scene_assets(self, scene: Scene) -> Dict[str, Path]:
        """
        Generates Video/Image, Audio, and Music for a single scene.
        """
        print(f"🎬 Scene {scene.id}: Starting production...")
        scene_dir = settings.TEMP_DIR / f"scene_{scene.id}"
        scene_dir.mkdir(exist_ok=True, parents=True)
        
        # 1. Visual (Veo or Image)
        visual_path = scene_dir / ("video.mp4" if scene.visual_type == "video" else "image.png")
        if not visual_path.exists():
            if scene.visual_type == "video":
                self._run_veo(scene.visual_prompt, scene.duration, visual_path)
            else:
                self._run_image_gen(scene.visual_prompt, visual_path)

        # 2. Audio (TTS)
        audio_path = scene_dir / "narration.mp3"
        if not audio_path.exists() and scene.narration_text:
            self._run_tts(scene.narration_text, scene.voice_id, audio_path)

        # 3. Music (Gen-Music)
        music_path = scene_dir / "score.mp3"
        if not music_path.exists() and scene.music_prompt:
            self._run_music(scene.music_prompt, scene.duration, music_path)
            
        return {
            "video": visual_path, 
            "audio": audio_path,
            "music": music_path,
            "type": scene.visual_type
        }

    def _run_veo(self, prompt: str, duration: int, output_path: Path):
        cmd = [
            settings.VEO_CMD,
            prompt,
            "--duration", str(duration),
            "--aspect-ratio", "16:9",
            "--output-file", str(output_path)
        ]
        # Mock execution: Generate valid test video
        print(f"  [MOCK] Generating test video: {output_path.name}")
        # Generate 720p color bars
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", f"testsrc=duration={duration}:size=1280x720:rate=30",
            "-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration}", # Add silent audio track to match Veo output
            "-c:v", "libx264", "-c:a", "aac", "-shortest",
            str(output_path)
        ], check=True, capture_output=True)

    def _run_image_gen(self, prompt: str, output_path: Path):
        cmd = [
            settings.IMAGE_CMD,
            "--prompt", prompt,
            "--output-dir", str(output_path.parent),
            "--filename", output_path.name,
            "--count", "1",
            "--style", "Cinematic"
        ]
        print(f"  [MOCK] Generating test image: {output_path.name}")
        # Generate a solid color image
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=1280x720",
            "-frames:v", "1", str(output_path)
        ], check=True, capture_output=True)

    def _run_tts(self, text: str, voice: str, output_path: Path):
        cmd = [
            settings.TTS_CMD,
            text,
            "--voice-name", voice,
            "--output-file", str(output_path),
            "--audio-format", "MP3"
        ]
        print(f"  [MOCK] Generating test narration: {output_path.name}")
        # Generate a sine wave beep for 2 seconds
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
            str(output_path)
        ], check=True, capture_output=True)

    def _run_music(self, prompt: str, duration: int, output_path: Path):
        cmd = [
            settings.MUSIC_CMD,
            prompt,
            "--duration", str(duration),
            "--output", str(output_path),
            "--format", "mp3"
        ]
        print(f"  [MOCK] Generating test music: {output_path.name}")
        # Generate a lower tone for music
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", f"sine=frequency=220:duration={duration}",
            str(output_path)
        ], check=True, capture_output=True)
