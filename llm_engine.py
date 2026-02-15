# llm_engine.py

from llama_cpp import Llama

def get_local_llama():
    return Llama(
        model_path="F:/llama/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        n_ctx=2048,  # context window
        n_threads=4,  # adjust based on your CPU
        n_gpu_layers=0  # set to > 0 if you have GPU support
    )

def build_prompt(scene_data, user_input):
    return f"""You are an expert interior designer.

Room Type: {scene_data['room_type']}

Detected Objects:
{scene_data['objects']}

Wall Coverage: {scene_data['regions']['wall_percent']}%
Floor Coverage: {scene_data['regions']['floor_percent']}%

User Style: {user_input['style']}
Budget: ₹{user_input['budget']}
Priority: {user_input['priority']}
Constraints: {user_input['constraints']}

Provide concise suggestions:
1. What to change
2. What to keep
3. Rough cost allocation
4. Priority improvements"""

def get_design_suggestions(scene_data, user_input):
    llm = get_local_llama()
    prompt = build_prompt(scene_data, user_input)

    response = llm(
        prompt,
        max_tokens=500,
        temperature=0.7,
        stop=["Human:", "User:"],
        echo=False
    )

    return response['choices'][0]['text']