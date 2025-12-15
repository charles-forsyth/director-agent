import json
import time
import subprocess
import google.generativeai as genai
from typing import Optional
from pathlib import Path
from director_agent.config import settings
from director_agent.core import ProductionManifest

class Planner:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY.get_secret_value())
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def generate_manifest(self, topic: str) -> ProductionManifest:
        """
        Full planning pipeline:
        1. Deep Research (gather facts)
        2. Gemini Synthesis (create structured plan)
        """
        # Step 1: Research
        research_content = self._run_deep_research(topic)
        
        # Step 2: Synthesis
        return self._synthesize_plan(topic, research_content)

    def _run_deep_research(self, topic: str) -> str:
        """
        Calls the deep-research CLI tool.
        Since deep-research is async/long-running, we might need to handle 'start' vs 'research'.
        For simplicity in v1, we'll use the blocking 'research' command if available, 
        or 'start' and poll.
        """
        print(f"🕵️  Researching: {topic}...")
        # Using the streaming research command but capturing output
        # In a real scenario, we'd want to use 'start' and poll 'list'
        try:
            # We use --output to get a clean JSON or Markdown file we can read back
            output_file = settings.TEMP_DIR / "research_output.md"
            cmd = [
                settings.DEEP_RESEARCH_CMD, "research", topic,
                "--output", str(output_file)
            ]
            
            # This is a blocking call. 
            subprocess.run(cmd, check=True, capture_output=True)
            
            if output_file.exists():
                return output_file.read_text()
            else:
                return f"Research failed to produce output for {topic}"
                
        except Exception as e:
            print(f"Research error: {e}")
            return f"Basic knowledge about {topic}"

    def _synthesize_plan(self, topic: str, context: str) -> ProductionManifest:
        """
        Uses Gemini to convert raw research into a Director's Manifest (JSON).
        """
        print("🧠 Synthesizing execution plan...")
        
        prompt = f"""
        You are a Movie Director Agent.
        Goal: Create a short, engaging video documentary about "{topic}".
        Context: {context[:10000]} (truncated)
        
        Output: A strictly valid JSON object adhering to this schema:
        {{
            "title": "Movie Title",
            "topic": "{topic}",
            "total_duration": 32,
            "scenes": [
                {{
                    "id": 1,
                    "duration": 4,
                    "visual_prompt": "Detailed prompt for AI video generator (Veo), cinematic, 16:9",
                    "narration_text": "Script for the narrator.",
                    "voice_id": "Charon",
                    "music_prompt": "Mood description for AI music generator",
                    "music_mood": "Tense"
                }}
            ]
        }}
        
        Constraints:
        1. Total duration should be between 30-60 seconds.
        2. Each scene must be exactly 4, 6, or 8 seconds (Veo limitations).
        3. Visual prompts must be descriptive and visual.
        4. Narration must fit within the duration (approx 2.5 words per second).
        """
        
        response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        
        try:
            data = json.loads(response.text)
            return ProductionManifest(**data)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            raise
