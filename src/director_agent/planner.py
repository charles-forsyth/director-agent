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
        # Step 1: Direct Synthesis (Brainstorming)
        return self._synthesize_plan(topic)

    def _synthesize_plan(self, topic: str) -> ProductionManifest:
        print(f"🧠 Brainstorming plan for '{topic}'...")
        
        if not self.model:
             raise ValueError("Gemini API Key is missing.")

        prompt = f"""
        You are a Visual Director creating an educational video presentation.
        Topic: "{topic}"
        Goal: Create a cinematic slideshow presentation that mixes rich cinematic imagery with clear, modern infographics.
        
        Instructions:
        1. **Brainstorming:** Use your internal knowledge to identify key facts, dates, and concepts about the topic.
        2. **Visual Variety:** You MUST alternate between styles.
           - Use **'Cinematic'** for establishing shots, mood, and real-world examples.
           - Use **'Infographic'** for explaining data, timelines, concepts, or processes.
           - Use **'Vintage Map'** or **'3D Model'** where appropriate.
        3. **Infographic Prompts:** When requesting an infographic, specify: "Minimalist vector art, clean lines, white background, clear iconography representing [concept]". Avoid requesting complex text.
        4. **Pacing:** Scenes 5-10 seconds.
        
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
                    "visual_prompt": "A dramatic 4K shot of...",
                    "audio_source": "generated",
                    "narration_text": "Narration script...",
                    "music_prompt": "Background music mood..."
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
