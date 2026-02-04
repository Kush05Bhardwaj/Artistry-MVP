from app.models.llm import ask_llm

SYSTEM_PROMPT = """
You provide DIY interior improvement steps.
Steps should be safe, beginner-friendly, and affordable.
"""

def generate_diy(room_analysis):
    user_prompt = f"""
Room description:
{room_analysis['scene_description']}

Detected objects:
{room_analysis['objects']}

Provide step-by-step DIY improvement guidance.
"""

    return ask_llm(SYSTEM_PROMPT, user_prompt)
