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
                # Real Render
                # print(f"  Rendering scene {scene.id} to {scene_out}")
                ffmpeg.output(video, audio_mix, scene_out, shortest=None, vcodec='libx264', acodec='aac').run(overwrite_output=True, quiet=True)
                scene_clips.append(scene_out)
            except ffmpeg.Error as e:
                print(f"FFmpeg error on scene {scene.id}: {e.stderr.decode('utf8') if e.stderr else str(e)}")

        # 3. Concatenate
        if not scene_clips:
            print("  [Error] No scenes to render.")
            return output_path
            
        try:
             # Real Concat
            # print(f"  Concatenating to {output_path}")
            inputs = [ffmpeg.input(clip) for clip in scene_clips]
            ffmpeg.concat(*inputs, v=1, a=1).output(str(output_path)).run(overwrite_output=True, quiet=True)
        except ffmpeg.Error as e:
            print(f"FFmpeg concat error: {e.stderr.decode('utf8') if e.stderr else str(e)}")

        # Cleanup temp clips
        for clip in scene_clips:
            Path(clip).unlink(missing_ok=True)

        return output_path