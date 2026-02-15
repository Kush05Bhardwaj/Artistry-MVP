# main_pipeline.py

from segment import Segmenter
from scene_builder import build_scene
from llm_engine import get_design_suggestions
from budget_engine import estimate_cost
from detect import results, model

# ----------------------------------
# STEP 1: Detection already done
# ----------------------------------

# Simulate YOLO output (replace with real one)
detected_objects = []

for r in results:
    for box in r.boxes:
        cls_id = int(box.cls)
        label = model.names[cls_id]
        conf = float(box.conf)
        
        detected_objects.append({
            "type": label.lower(),
            "confidence": round(conf, 2)
        })

# ----------------------------------
# STEP 2: Segmentation
# ----------------------------------

segmenter = Segmenter()
seg_map, image = segmenter.segment("room.jpg")

# ----------------------------------
# STEP 3: Build Scene
# ----------------------------------

scene_data = build_scene(detected_objects, seg_map, segmenter, image)

# ----------------------------------
# STEP 4: User Input
# ----------------------------------

user_input = {
    "style": "modern minimal",
    "budget": 50000,
    "priority": "make room brighter",
    "constraints": ["do not replace bed"]
}

# ----------------------------------
# STEP 5: LLM Suggestions
# ----------------------------------

suggestions = get_design_suggestions(scene_data, user_input)
print("\nLLM Suggestions:\n")
print(suggestions)

# ----------------------------------
# STEP 6: Budget Estimation
# ----------------------------------

estimated_cost = estimate_cost(suggestions)

print("\nEstimated Cost:", estimated_cost)
print("User Budget:", user_input["budget"])

if estimated_cost > user_input["budget"]:
    print("⚠ Suggestions exceed budget.")
else:
    print("✅ Within budget.")