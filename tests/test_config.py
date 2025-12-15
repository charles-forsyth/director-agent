import pytest
from pathlib import Path
from director_agent.config import settings

def test_config_defaults():
    assert settings.DEEP_RESEARCH_CMD == "deep-research"
    assert settings.VEO_CMD == "generate-veo"
    assert settings.OUTPUT_DIR == Path.home() / "Movies"

def test_ensure_dirs(tmp_path):
    settings.TEMP_DIR = tmp_path / "tmp"
    settings.OUTPUT_DIR = tmp_path / "out"
    settings.ensure_dirs()
    assert settings.TEMP_DIR.exists()
    assert settings.OUTPUT_DIR.exists()
