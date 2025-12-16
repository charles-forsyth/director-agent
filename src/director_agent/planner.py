import json
import subprocess
import google.generativeai as genai
from director_agent.config import settings
from director_agent.models import ProductionManifest

class Planner:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY.get_secret_value())
            self.model = genai.GenerativeModel('gemini-2.5-pro')
        else:
            self.model = None

    def generate_manifest(self, topic: str) -> ProductionManifest:
        # Step 1: Research
        research_content = self._run_deep_research(topic)
        
        # Step 2: Synthesis
        return self._synthesize_plan(topic, research_content)

    def _run_deep_research(self, topic: str) -> str:
        print(f"🕵️  Researching: {topic}...")
        try:
            output_file = settings.TEMP_DIR / "research_output.md"
            cmd = [
                settings.DEEP_RESEARCH_CMD, "research", topic,
                "--output", str(output_file)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            if output_file.exists():
                return output_file.read_text()
            else:
                return f"Basic facts about {topic}"
        except Exception as e:
            print(f"Research error (using fallback): {e}")
            return f"Basic knowledge about {topic}"

    def _synthesize_plan(self, topic: str, context: str) -> ProductionManifest:
        print("🧠 Synthesizing execution plan (Presentation Mode)...")
        
        if not self.model:
             raise ValueError("Gemini API Key is missing.")

        prompt = f"""
        You are a Documentary Director specializing in "Ken Burns" style visual storytelling.
        Goal: Create a cinematic slideshow presentation about "{topic}" using high-resolution static imagery, narration, and music.
        Context: {context[:5000]} (truncated)
        
        Instructions:
        1. **Visuals:** All scenes MUST use `visual_type="image"`. Describe rich, detailed, 4K static images (diagrams, photos, art).
        2. **Audio:** Every scene needs `narration_text` and a `music_prompt`.
        3. **Pacing:** Scenes should be 5-10 seconds long to allow for reading/viewing.
        
        Output: A strictly valid JSON object adhering to this schema:
        {{
            "title": "Movie Title",
            "topic": "{topic}",
            "total_duration": 60,
            "scenes": [
                {{
                    "id": 1,
                    "duration": 6,
                    "visual_type": "image",
                    "visual_prompt": "A high-resolution map of the ancient world, parchment texture, detailed labels, cinematic lighting",
                    "audio_source": "generated",
                    "narration_text": "In the beginning, the world was vast and unknown...",
                    "music_prompt": "Epic orchestral opening"
                }}
            ]
        }}
        """
        
        response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            data = json.loads(response.text)
            return ProductionManifest(**data)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            raise