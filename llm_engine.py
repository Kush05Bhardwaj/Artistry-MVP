# llm_engine.py

import json
import re
from llama_cpp import Llama


class LLMEngine:
    def __init__(self, model_path):
        print("Loading LLM...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=8,
            verbose=False
        )

    def generate_design(self, scene_data, user_input):
        """Generate design suggestions based on scene data and user input.
        
        Args:
            scene_data: Dictionary with scene information
            user_input: Dictionary with style, budget, priority, constraints
            
        Returns:
            tuple: (structured_plan, raw_response)
        """
        
        system_prompt = """
You are an interior design planning engine.

You MUST respond ONLY in valid JSON.

Output format:

{
  "changes": [
    {
      "action": "brighten_room",
      "intensity": 0.2
    },
    {
      "action": "warm_lighting",
      "temperature_shift": 15
    },
    {
      "action": "recolor_wall",
      "color": "warm white"
    }
  ]
}

Allowed actions:
- brighten_room
- warm_lighting
- recolor_wall
- recolor_curtain

DO NOT explain.
DO NOT add text.
ONLY JSON.
"""

        user_message = f"""
Scene Data:
{json.dumps(scene_data, indent=2)}

User Input:
{json.dumps(user_input, indent=2)}
"""

        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4
        )

        raw_text = response["choices"][0]["message"]["content"]

        # Save raw for debugging
        with open("outputs/llm_raw.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)

        structured = self._extract_json(raw_text)

        # Save parsed output
        with open("outputs/structured_plan.json", "w", encoding="utf-8") as f:
            json.dump(structured, f, indent=4)

        return structured, raw_text

    def _extract_json(self, text):
        try:
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        print("⚠ LLM JSON parse failed. Returning empty plan.")
        return {"changes": []}