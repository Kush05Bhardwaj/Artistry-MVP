from app.models.llm import ask_llm

SYSTEM_PROMPT = """
You estimate interior redesign costs in INR.
Base your estimate on room size, furniture, and decor complexity.
Give a realistic approximate range.
"""

def estimate_cost(room_analysis):
    user_prompt = f"""
Room description:
{room_analysis['scene_description']}

Detected objects:
{room_analysis['objects']}

Estimate approximate redesign cost in INR.
"""

    return ask_llm(SYSTEM_PROMPT, user_prompt)
