import ffmpeg
from pathlib import Path
from typing import Dict
from director_agent.core import ProductionManifest

class Editor:
    def assemble(self, manifest: ProductionManifest, assets: Dict[int, Dict[str, Path]], output_path: Path) -> Path:
        """
        Assembles the final movie from scene assets.
        """
        print("✂️  Assembling final cut...")
        
        # List of temporary scene clips
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
                music = ffmpeg.input(music_path).audio.filter('volume', 0.3)  # Background level
                # Mix narration and music
                audio_mix = ffmpeg.filter([narration, music], 'amix', inputs=2, duration='first')
            else:
                audio_mix = narration
                
            # Create a temporary file for this scene (simplifies concat)
            scene_out = str(output_path.parent / f"temp_scene_{scene.id}.mp4")
            
            try:
                ffmpeg.output(video, audio_mix, scene_out, shortest=None, vcodec='libx264', acodec='aac').run(overwrite_output=True, quiet=True)
                scene_clips.append(scene_out)
            except ffmpeg.Error as e:
                print(f"FFmpeg error on scene {scene.id}: {e.stderr.decode('utf8')}")

        # 3. Concatenate all scenes
        if not scene_clips:
            raise RuntimeError("No scenes were successfully rendered.")
            
        inputs = [ffmpeg.input(clip) for clip in scene_clips]
        
        try:
            # Safe concat
            ffmpeg.concat(*inputs, v=1, a=1).output(str(output_path)).run(overwrite_output=True)
        except ffmpeg.Error as e:
            print(f"FFmpeg concat error: {e.stderr.decode('utf8')}")
            raise

        # Cleanup temp clips
        for clip in scene_clips:
            Path(clip).unlink(missing_ok=True)
            
        return output_path
