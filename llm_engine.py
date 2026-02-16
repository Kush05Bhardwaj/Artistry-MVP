# llm_engine.py

import json
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

        prompt = f"""
You are a professional interior designer AI.

Scene Data:
{json.dumps(scene_data, indent=2)}

User Requirements:
{json.dumps(user_input, indent=2)}

Return ONLY valid JSON in this format:

{{
  "changes": [
    {{
      "item": "",
      "reason": "",
      "estimated_cost": 0
    }}
  ]
}}
"""

        output = self.llm(
            prompt,
            max_tokens=600,
            temperature=0.7,
            stop=["</s>"]
        )

        text = output["choices"][0]["text"]

        # Extract JSON safely
        try:
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            structured = json.loads(text[json_start:json_end])
            return structured
        except:
            print("⚠ LLM JSON parse failed.")
            return {"changes": []}