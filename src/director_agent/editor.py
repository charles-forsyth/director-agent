import ffmpeg
from pathlib import Path
from typing import Dict
from director_agent.models import ProductionManifest

class Editor:
    def assemble(self, manifest: ProductionManifest, assets: Dict[int, Dict[str, Path]], output_path: Path) -> Path:
        print("✂️  Assembling final cut (Presentation Mode)...")
        scene_clips = []
        
        for scene in manifest.scenes:
            scene_data = assets.get(scene.id)
            if not scene_data: continue
            
            scene_out = str(output_path.parent / f"temp_scene_{scene.id}.mp4")
            
            try:
                # --- IMAGE SCENE (with Ken Burns Effect) ---
                # Zoom in 10% over the duration (z=zoom+0.0015)
                # pattern_type='none' is crucial to prevent ffmpeg from looking for sequences
                image_in = ffmpeg.input(str(scene_data['image']), loop=1, t=scene.duration) # ffmpeg-python might not expose pattern_type easily in input(), checking args...
                
                # We'll use kwargs for pattern_type
                image_in = ffmpeg.input(str(scene_data['image']), loop=1, t=scene.duration, **{'pattern_type': 'none'})
                
                video_stream = image_in.filter('scale', '3840x2160').filter('zoompan', z='min(zoom+0.0015,1.5)', d=scene.duration*30, s='1920x1080')
                
                # Audio Mix
                audio_path = scene_data.get('audio')
                music_path = scene_data.get('music')
                
                if audio_path:
                    narration = ffmpeg.input(str(audio_path)).audio
                else:
                    narration = ffmpeg.input('anullsrc', f='lavfi', t=scene.duration).audio

                if music_path:
                    music = ffmpeg.input(str(music_path)).audio.filter('volume', 0.3)
                    audio_mix = ffmpeg.filter([narration, music], 'amix', inputs=2, duration='first')
                else:
                    audio_mix = narration
                
                # Render
                ffmpeg.output(video_stream, audio_mix, scene_out, vcodec='libx264', acodec='aac', video_bitrate='5M', audio_bitrate='192k', r=30, pix_fmt='yuv420p', shortest=None).run(overwrite_output=True, quiet=True)
                scene_clips.append(scene_out)
                
            except ffmpeg.Error as e:
                print(f"FFmpeg error on scene {scene.id}: {e.stderr.decode('utf8') if e.stderr else str(e)}")

        # Final Concatenation
        if not scene_clips:
            print("  [Error] No scenes to render.")
            return output_path
            
        try:
            # Safe concat
            list_file = output_path.parent / "concat_list.txt"
            with open(list_file, 'w') as f:
                for clip in scene_clips:
                    f.write(f"file '{clip}'\n")
            
            ffmpeg.input(str(list_file), format='concat', safe=0).output(str(output_path), c='copy').run(overwrite_output=True, quiet=True)
            list_file.unlink() 
            
        except ffmpeg.Error as e:
            print(f"FFmpeg concat error: {e.stderr.decode('utf8') if e.stderr else str(e)}")

        # Cleanup
        for clip in scene_clips:
            Path(clip).unlink(missing_ok=True)

        return output_path