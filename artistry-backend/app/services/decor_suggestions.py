from app.models.llm import ask_llm

SYSTEM_PROMPT = """
You are an interior designer AI.
You analyze rooms and propose decor changes based on space, lighting, and style.
Avoid generic advice. Be specific and practical.
"""

def generate_decor(room_analysis):
    user_prompt = f"""
Room description:
{room_analysis['scene_description']}

Detected objects:
{room_analysis['objects']}

Suggest decor improvements and design ideas.
"""

    return ask_llm(SYSTEM_PROMPT, user_prompt)
