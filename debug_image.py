from pathlib import Path
from director_agent.executor import Executor
from director_agent.config import settings

# Setup
settings.RUN_TEMP_DIR = Path("/tmp/director_debug")
settings.RUN_TEMP_DIR.mkdir(parents=True, exist_ok=True)

executor = Executor()
output_path = settings.RUN_TEMP_DIR / "test_image.png"

print("🧪 Testing Image Generation...")
try:
    executor._run_image_gen(
        prompt="A cute robot eating a taco, 4k cinematic",
        output_path=output_path,
        style="Cinematic"
    )
    print("✅ Success! Image created.")
except Exception as e:
    print(f"💥 Failed: {e}")
