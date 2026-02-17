# llm_engine.py

import json
import re
import cv2
import numpy as np
from llama_cpp import Llama


class LLMEngine:
    # Strict allowed actions schema
    ALLOWED_ACTIONS = {
        "brighten_room": {
            "required_params": ["intensity"],
            "optional_params": ["estimated_cost"],
            "defaults": {"intensity": 0.3, "estimated_cost": 2000}
        },
        "warm_lighting": {
            "required_params": ["temperature_shift"],
            "optional_params": ["estimated_cost"],
            "defaults": {"temperature_shift": 15, "estimated_cost": 1500}
        },
        "recolor_wall": {
            "required_params": [],
            "optional_params": ["color", "estimated_cost"],
            "defaults": {"color": "warm white", "estimated_cost": 5000}
        },
        "replace_curtain": {
            "required_params": [],
            "optional_params": ["new_curtain", "estimated_cost"],
            "defaults": {"new_curtain": "white linen", "estimated_cost": 3000}
        }
    }

    def __init__(self, model_path):
        print("Loading LLM...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=8,
            verbose=False
        )

    def generate_design(self, scene_data, user_input):
        """Generate design suggestions with strict validation and fail-safe fallback.
        
        Args:
            scene_data: Dictionary with scene information
            user_input: Dictionary with style, budget, priority, constraints
            
        Returns:
            tuple: (structured_plan, raw_response)
        """
        
        # Build strict system prompt with JSON-only output
        system_prompt = self._build_strict_prompt()
        
        user_message = f"""Scene Data:
{json.dumps(scene_data, indent=2)}

User Requirements:
- Style: {user_input.get('style', 'modern')}
- Budget: ₹{user_input.get('budget', 50000)}
- Priority: {user_input.get('priority', 'general improvement')}
- Constraints: {user_input.get('constraints', 'none')}

Output valid JSON only. No text. No explanation."""

        try:
            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more deterministic output
                max_tokens=512,
                stop=["```", "\n\n\n", "User:", "Scene:"]  # Stop sequences to prevent rambling
            )

            raw_text = response["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            print(f"⚠ LLM generation failed: {e}")
            raw_text = ""

        # Save raw for debugging
        with open("outputs/llm_raw.txt", "w", encoding="utf-8") as f:
            f.write(raw_text if raw_text else "LLM generation failed")

        # Extract and validate JSON
        structured = self._extract_and_validate_json(raw_text)
        
        # If extraction/validation failed, use fail-safe fallback
        if not structured or not structured.get("changes"):
            print("⚠ LLM output invalid. Using fail-safe fallback plan.")
            structured = self._generate_fallback_plan(scene_data, user_input)

        # Save parsed output
        with open("outputs/structured_plan.json", "w", encoding="utf-8") as f:
            json.dump(structured, f, indent=4)

        return structured, raw_text

    def _build_strict_prompt(self):
        """Build a strict system prompt that enforces JSON-only output."""
        return """You are a JSON-only interior design engine.

OUTPUT RULES:
1. Output ONLY valid JSON
2. NO explanations, NO markdown, NO commentary
3. Use ONLY the allowed actions below

REQUIRED JSON STRUCTURE:
{
  "changes": [
    {
      "action": "ACTION_NAME",
      "PARAM": VALUE,
      "estimated_cost": NUMBER
    }
  ]
}

ALLOWED ACTIONS:
1. brighten_room
   - intensity: 0.1 to 0.5 (float)
   - estimated_cost: number

2. warm_lighting
   - temperature_shift: 5 to 25 (integer)
   - estimated_cost: number

3. recolor_wall
   - color: string (optional)
   - estimated_cost: number

4. replace_curtain
   - new_curtain: string (optional)
   - estimated_cost: number

CRITICAL: Output JSON only. Nothing else."""

    def _extract_and_validate_json(self, text):
        """Extract JSON and validate against allowed schema."""
        if not text:
            return None
            
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*"changes"[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
            else:
                # Try parsing the whole text
                data = json.loads(text)
            
            # Validate structure
            if not isinstance(data, dict) or "changes" not in data:
                print("⚠ JSON missing 'changes' key")
                return None
            
            if not isinstance(data["changes"], list):
                print("⚠ 'changes' is not a list")
                return None
            
            # Validate and sanitize each change
            validated_changes = []
            for i, change in enumerate(data["changes"]):
                validated_change = self._validate_change(change, i)
                if validated_change:
                    validated_changes.append(validated_change)
            
            if not validated_changes:
                print("⚠ No valid changes after validation")
                return None
            
            return {"changes": validated_changes}
            
        except json.JSONDecodeError as e:
            print(f"⚠ JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"⚠ Validation error: {e}")
            return None

    def _validate_change(self, change, index):
        """Validate a single change against allowed actions schema."""
        if not isinstance(change, dict):
            print(f"⚠ Change {index} is not a dict")
            return None
        
        action = change.get("action")
        if not action or action not in self.ALLOWED_ACTIONS:
            print(f"⚠ Invalid action '{action}' at change {index}")
            return None
        
        schema = self.ALLOWED_ACTIONS[action]
        validated = {"action": action}
        
        # Apply defaults and validate parameters
        for param, default_value in schema["defaults"].items():
            if param in change:
                validated[param] = change[param]
            else:
                validated[param] = default_value
        
        # Validate ranges for specific parameters
        if action == "brighten_room" and "intensity" in validated:
            validated["intensity"] = max(0.1, min(0.5, float(validated["intensity"])))
        
        if action == "warm_lighting" and "temperature_shift" in validated:
            validated["temperature_shift"] = max(5, min(25, int(validated["temperature_shift"])))
        
        return validated

    def _generate_fallback_plan(self, scene_data, user_input):
        """Generate a safe, deterministic fallback plan based on scene analysis."""
        print("\n🛡️ Generating fail-safe fallback plan...")
        
        changes = []
        budget = user_input.get("budget", 50000)
        remaining_budget = budget
        
        # Analyze brightness from scene_data
        brightness_score = scene_data.get("brightness_score", 0)
        region_stats = scene_data.get("regions", {})
        wall_percent = region_stats.get("wall_percent", 0)
        curtain_percent = region_stats.get("curtain_percent", 0)
        
        priority = user_input.get("priority", "").lower()
        
        # Rule 1: If brightness is low or user wants brighter room
        if brightness_score < 120 or "bright" in priority:
            cost = 2000
            if remaining_budget >= cost:
                changes.append({
                    "action": "brighten_room",
                    "intensity": 0.4,
                    "estimated_cost": cost
                })
                remaining_budget -= cost
                print(f"  ✓ Added brighten_room (brightness={brightness_score})")
        
        # Rule 2: Add warm lighting for cozy feel
        if remaining_budget >= 1500 and ("cozy" in priority or "warm" in priority):
            cost = 1500
            changes.append({
                "action": "warm_lighting",
                "temperature_shift": 15,
                "estimated_cost": cost
            })
            remaining_budget -= cost
            print(f"  ✓ Added warm_lighting")
        
        # Rule 3: Recolor walls if significant wall area detected
        if wall_percent > 20 and remaining_budget >= 5000:
            cost = 5000
            changes.append({
                "action": "recolor_wall",
                "color": "warm white",
                "estimated_cost": cost
            })
            remaining_budget -= cost
            print(f"  ✓ Added recolor_wall (wall_percent={wall_percent}%)")
        
        # Rule 4: Replace curtains if curtains detected
        if curtain_percent > 5 and remaining_budget >= 3000:
            cost = 3000
            changes.append({
                "action": "replace_curtain",
                "new_curtain": "white linen",
                "estimated_cost": cost
            })
            remaining_budget -= cost
            print(f"  ✓ Added replace_curtain (curtain_percent={curtain_percent}%)")
        
        # If no changes added, add at least brighten_room
        if not changes:
            changes.append({
                "action": "brighten_room",
                "intensity": 0.3,
                "estimated_cost": 2000
            })
            print(f"  ✓ Added default brighten_room")
        
        print(f"  💰 Budget used: ₹{budget - remaining_budget} / ₹{budget}\n")
        
        return {"changes": changes}

        print("⚠ LLM JSON parse failed. Returning empty plan.")
        return {"changes": []}