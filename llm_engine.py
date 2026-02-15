# llm_engine.py

from llama_cpp import Llama

MODEL_PATH = r"F:\llama\models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

# Load once (global model instance)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=8,         # adjust to CPU cores
    n_gpu_layers=35      # set >0 if GPU available
)

def build_prompt(scene_data, user_input):
    return f"""
You are a professional interior designer AI.

Room Type: {scene_data['room_type']}

Detected Objects:
{scene_data['objects']}

Region Coverage:
Wall: {scene_data['regions']['wall_percent']}%
Floor: {scene_data['regions']['floor_percent']}%
Bed: {scene_data['regions']['bed_percent']}%
Curtain: {scene_data['regions']['curtain_percent']}%

User Style Preference: {user_input['style']}
Budget: ₹{user_input['budget']}
Priority: {user_input['priority']}
Constraints: {user_input['constraints']}

Give structured suggestions in bullet points:
- What to change
- What to keep
- Budget-aware improvements
- Estimated rough cost reasoning
"""

def get_design_suggestions(scene_data, user_input):

    prompt = build_prompt(scene_data, user_input)

    output = llm(
        prompt,
        max_tokens=800,
        temperature=0.7,
        top_p=0.9,
        stop=["</s>"]
    )

    return output["choices"][0]["text"].strip()