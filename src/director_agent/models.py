from typing import List, Optional
from pydantic import BaseModel, Field

class Scene(BaseModel):
    id: int
    duration: int = Field(..., description="Duration in seconds")
    visual_prompt: str = Field(..., description="Prompt for generate-veo or generate-gemini-image")
    visual_type: str = Field("video", description="Type of visual: 'video' or 'image'")
    narration_text: Optional[str] = Field(None, description="Script for gen-tts")
    voice_id: str = Field("Charon", description="Voice ID for TTS")
    music_prompt: Optional[str] = Field(None, description="Prompt for gen-music")
    music_mood: Optional[str] = Field(None, description="Mood for music generation")

class ProductionManifest(BaseModel):
    title: str
    topic: str
    scenes: List[Scene]
    total_duration: int
