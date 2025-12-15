import pytest
from pathlib import Path
from director_agent.models import ProductionManifest, Scene

def test_manifest_hero_prompt():
    manifest = ProductionManifest(
        title="Test Movie",
        topic="Testing",
        hero_prompt="A consistency test character",
        scenes=[
            Scene(
                id=1, 
                duration=4, 
                visual_prompt="Shot 1", 
                visual_type="video"
            )
        ],
        total_duration=4
    )
    assert manifest.hero_prompt == "A consistency test character"
    assert len(manifest.scenes) == 1

def test_scene_defaults():
    scene = Scene(id=1, duration=4, visual_prompt="Test")
    assert scene.voice_id == "Charon"
    assert scene.visual_type == "video"
