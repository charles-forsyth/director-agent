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
            output_file = settings.RUN_TEMP_DIR / "research_output.md"
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
        print("🧠 Synthesizing execution plan (Infographic & Presentation Mode)...")
        
        if not self.model:
             raise ValueError("Gemini API Key is missing.")

        prompt = f"""
        You are a Visual Director creating an educational video presentation.
        Goal: Create a slideshow about "{topic}" that mixes rich cinematic imagery with clear, modern infographics.
        Context: {context[:5000]} (truncated)
        
        Instructions:
        1. **Visual Variety:** You MUST alternate between styles.
           - Use **'Cinematic'** for establishing shots, mood, and real-world examples.
           - Use **'Infographic'** for explaining data, timelines, concepts, or processes.
           - Use **'Vintage Map'** or **'3D Model'** where appropriate.
        2. **Infographic Prompts:** When requesting an infographic, specify: "Minimalist vector art, clean lines, white background, clear iconography representing [concept]". Avoid requesting complex text.
        3. **Pacing:** Scenes 5-10 seconds.
        
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
                    "image_style": "Cinematic",
                    "visual_prompt": "A dramatic 4K shot of a stormy ocean...",
                    "audio_source": "generated",
                    "narration_text": "The ocean is a force of nature...",
                    "music_prompt": "Stormy orchestral"
                }},
                {{
                    "id": 2,
                    "duration": 8,
                    "visual_type": "image",
                    "image_style": "Infographic",
                    "visual_prompt": "A clean, modern infographic showing the water cycle. Flat design, blue and white color palette, simple icons for rain and evaporation.",
                    "audio_source": "generated",
                    "narration_text": "It functions through a continuous cycle of evaporation...",
                    "music_prompt": "Light electronic beat"
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
