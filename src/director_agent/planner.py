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
        print("🧠 Synthesizing execution plan (Mixed Media)...")
        
        if not self.model:
             raise ValueError("Gemini API Key is missing.")

        prompt = f"""
        You are a Mixed-Media Movie Director.
        Goal: Create a documentary about "{topic}" combining realistic video clips (Veo) and static illustrative images (NanoBanana).
        Context: {context[:5000]} (truncated)
        
        Instructions:
        1. **Mixed Media:** Use 'video' (Veo) for action/movement. Use 'image' (NanoBanana) for diagrams, establishing shots, or conceptual visuals.
        2. **Consistency:** Group related video scenes using `reference_group`. Define a `reference_prompt` for the first scene of each group (e.g. "Main character face").
        3. **Audio Strategy:**
           - For **Video** scenes: Set `audio_source` to "native" (Let Veo generate the sound/voice).
           - For **Image** scenes: Set `audio_source` to "generated" and provide `narration_text` + `music_prompt`.
        
        Output: A strictly valid JSON object adhering to this schema:
        {{
            "title": "Movie Title",
            "topic": "{topic}",
            "total_duration": 40,
            "scenes": [
                {{
                    "id": 1,
                    "duration": 4,
                    "visual_type": "image",
                    "visual_prompt": "Wide shot of a misty harbor, oil painting style",
                    "audio_source": "generated",
                    "narration_text": "It began in the harbor...",
                    "music_prompt": "Ocean waves and piano"
                }},
                {{
                    "id": 2,
                    "duration": 6,
                    "visual_type": "video",
                    "visual_prompt": "A sailor pulling ropes on a boat, cinematic",
                    "reference_group": "sailor_1",
                    "reference_prompt": "A weathered sailor in a yellow raincoat, detailed portrait",
                    "audio_source": "native"
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
