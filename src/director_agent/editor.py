import ffmpeg
from pathlib import Path
from typing import Dict
from director_agent.models import ProductionManifest

class Editor:
    def assemble(self, manifest: ProductionManifest, assets: Dict[int, Dict[str, Path]], output_path: Path) -> Path:
        """
        Assembles the final movie from scene assets.
        """
        print("✂️  Assembling final cut...")
        
        scene_clips = []
        
        for scene in manifest.scenes:
            scene_assets = assets.get(scene.id)
            if not scene_assets:
                continue
                
            video_path = str(scene_assets['video'])
            audio_path = str(scene_assets['audio']) if scene_assets.get('audio') else None
            music_path = str(scene_assets['music']) if scene_assets.get('music') else None
            
            # 1. Video Stream
            video = ffmpeg.input(video_path).video
            
            # 2. Audio Stream (Narration + Music)
            if audio_path:
                narration = ffmpeg.input(audio_path).audio
            else:
                narration = ffmpeg.input('anullsrc', f='lavfi', t=scene.duration).audio

            if music_path:
                music = ffmpeg.input(music_path).audio.filter('volume', 0.3)
                audio_mix = ffmpeg.filter([narration, music], 'amix', inputs=2, duration='first')
            else:
                audio_mix = narration
                
            scene_out = str(output_path.parent / f"temp_scene_{scene.id}.mp4")
            
            try:
                # Mocking ffmpeg execution for now since we are in a dev environment without real assets
                print(f"  [MOCK] Rendering scene {scene.id} to {scene_out}")
                Path(scene_out).touch()
                scene_clips.append(scene_out)
            except Exception as e:
                print(f"FFmpeg error on scene {scene.id}: {e}")

        # 3. Concatenate
        if not scene_clips:
            print("  [MOCK] No scenes to render.")
            output_path.touch()
            return output_path
            
        try:
             # Mock concat
            print(f"  [MOCK] Concatenating to {output_path}")
            output_path.touch()
        except Exception as e:
            print(f"FFmpeg concat error: {e}")

        return output_path