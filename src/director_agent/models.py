from typing import List, Optional
from pydantic import BaseModel, Field

class Scene(BaseModel):
    id: int
    duration: int = Field(..., description="Duration in seconds (5-10)")
    visual_type: str = Field("image", description="Always 'image' for Presentation Mode")
    
    # Visual Details
    visual_prompt: str = Field(..., description="The specific prompt for the image.")
    image_style: str = Field("Cinematic", description="The artistic style. Options: 'Cinematic', 'Infographic', '3D Model', 'Vintage Map', 'Watercolor'.")
    
    # Consistency
    reference_group: Optional[str] = Field(None, description="Label for consistent subjects (optional)")
    reference_prompt: Optional[str] = Field(None, description="Prompt for the reference asset (optional)")
    
    # Audio
    audio_source: str = Field("generated", description="Always 'generated' for Presentation Mode")
    narration_text: Optional[str] = Field(None, description="Script for gen-tts")
    voice_id: str = Field("Charon", description="Voice ID for TTS")
    music_prompt: Optional[str] = Field(None, description="Prompt for gen-music")

class ProductionManifest(BaseModel):
    title: str
    topic: str
    scenes: List[Scene]
    total_duration: int
