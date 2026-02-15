# main_pipeline.py

from detect import run_detection
from segment import Segmenter
from scene_builder import build_scene
from llm_engine import get_design_suggestions
from budget_engine import estimate_cost

# ----------------------------------
# STEP 1: Real detection
print("Running object detection...")
detected_objects = run_detection("room.jpg")
print("Detected:", detected_objects)

# ----------------------------------
# STEP 2: Segmentation
segmenter = Segmenter()
seg_map, image = segmenter.segment("room.jpg")

# ----------------------------------
# STEP 3: Build Scene
scene_data = build_scene(detected_objects, seg_map, segmenter, image)

print("\nScene Data:")
print(scene_data)

# ----------------------------------
# STEP 4: User Input (example)
user_input = {
    "style": "modern minimal",
    "budget": 50000,
    "priority": "make room brighter",
    "constraints": ["do not replace bed"]
}

# ----------------------------------
# STEP 5: LLM Suggestions
print("\nGetting design suggestions...")
suggestions = get_design_suggestions(scene_data, user_input)
print("\nLLM Suggestions:\n")
print(suggestions)

# ----------------------------------
# STEP 6: Budget Estimation
estimated_cost = estimate_cost(suggestions)
print("\nEstimated Cost:", estimated_cost)
print("User Budget:", user_input["budget"])
if estimated_cost > user_input["budget"]:
    print("⚠ Suggestions exceed budget.")
else:
    print("✅ Within budget.")