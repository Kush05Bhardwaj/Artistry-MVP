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
        prompt = f"""You are an interior design AI assistant. Based on the scene data and user input, generate design suggestions.

Scene Data:
{json.dumps(scene_data, indent=2)}

User Input:
{json.dumps(user_input, indent=2)}

Return ONLY a valid JSON object with this exact structure (no additional text):
{{
    "changes": [
        {{
            "item": "item name",
            "action": "description of change",
            "estimated_cost": 100
        }}
    ]
}}

JSON:"""

        response = self.llm(prompt, max_tokens=512, stop=["\n\n", "User:", "Scene:"], temperature=0.7)

        raw_text = response["choices"][0]["text"].strip()

        try:
            # Try to extract JSON if there's extra text
            if "{" in raw_text and "}" in raw_text:
                start = raw_text.find("{")
                end = raw_text.rfind("}") + 1
                json_text = raw_text[start:end]
                structured = json.loads(json_text)
            else:
                raise ValueError("No JSON found")
        except Exception as e:
            print(f"⚠ LLM JSON parse failed: {e}")
            print(f"Raw response: {raw_text[:200]}...")
            structured = {"changes": []}

        return structured, raw_text