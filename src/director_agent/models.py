from typing import List, Optional
from pydantic import BaseModel, Field

class Scene(BaseModel):
    id: int
    duration: int = Field(..., description="Duration in seconds (4, 6, or 8)")
    visual_type: str = Field("video", description="Type of visual: 'video' (Veo) or 'image' (NanoBanana)")
    visual_prompt: str = Field(..., description="The specific prompt for this shot/image")
    
    # Consistency & Audio Controls
    reference_group: Optional[str] = Field(None, description="A label for the visual reference (e.g. 'captain', 'boat'). Scenes with the same label share the same reference image.")
    reference_prompt: Optional[str] = Field(None, description="The prompt to generate the reference image if this is the first scene in the group.")
    
    audio_source: str = Field("default", description="'native' (Veo audio), 'generated' (TTS+Music), or 'silent'")
    
    # Generated Audio Content
    narration_text: Optional[str] = Field(None, description="Script for gen-tts (if audio_source='generated')")
    voice_id: str = Field("Charon", description="Voice ID for TTS")
    music_prompt: Optional[str] = Field(None, description="Prompt for gen-music (if audio_source='generated')")

class ProductionManifest(BaseModel):
    title: str
    topic: str
    scenes: List[Scene]
    total_duration: int