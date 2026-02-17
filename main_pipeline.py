# main_pipeline.py

import json

import cv2

from detect import run_detection
from segment import Segmenter
from scene_builder import build_scene_data
from llm_engine import LLMEngine
from budget_engine import calculate_total_cost, evaluate_budget
from output_manager import OutputManager
from renderer import RendererV2

IMAGE_PATH = "room.jpg"
LLM_MODEL_PATH = r"F:\llama\models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"


def run_pipeline():

    output = OutputManager()
    output.save_input_image(IMAGE_PATH)

    print("Running detection...")
    detected_objects = run_detection(IMAGE_PATH, output)

    print("Running segmentation...")
    segmenter = Segmenter()
    seg_map = segmenter.segment(IMAGE_PATH)
    region_stats = segmenter.extract_region_stats(seg_map)

    # Save raw segmentation numpy array for exact reproduction
    output.save_numpy("segmentation_raw.npy", seg_map)

    overlay = segmenter.create_overlay(IMAGE_PATH, seg_map)

    output.save_json("segmentation_stats.json", region_stats)
    output.save_image("segmentation_overlay.jpg", overlay)

    print("Building scene...")
    scene_data = build_scene_data(
        IMAGE_PATH,
        detected_objects,
        region_stats
    )

    output.save_json("scene_data.json", scene_data)

    print("Loading LLM...")
    llm_engine = LLMEngine(LLM_MODEL_PATH)

    user_input = {
        "style": "modern minimal",
        "budget": 50000,
        "priority": "make room brighter",
        "constraints": "do not replace bed"
    }

    print("Generating suggestions...")
    structured_plan, raw_response = llm_engine.generate_design(scene_data, user_input)

    output.save_json("structured_plan.json", structured_plan)
    output.save_text("llm_raw.txt", raw_response)

    total_cost = calculate_total_cost(structured_plan)
    budget_status = evaluate_budget(total_cost, user_input["budget"])

    budget_data = {
        "total_cost": total_cost,
        "user_budget": user_input["budget"],
        "status": budget_status
    }

    output.save_json("budget_result.json", budget_data)

    print("Rendering design...")

    renderer = RendererV2()

    input_image = cv2.imread(IMAGE_PATH)
    wall_mask = (seg_map == 0).astype('uint8') * 255  # Assuming wall is region 0
    curtain_mask = (seg_map == 1).astype('uint8') * 255  # Assuming curtain is region 1

    rendered_image = renderer.render(
        image=input_image,
        segmentation_masks={
            "wall": wall_mask,
            "curtain": curtain_mask
        },
        plan=structured_plan
    )

    cv2.imwrite("outputs/rendered_v2.jpg", rendered_image)

    # Save comprehensive pipeline summary
    pipeline_summary = {
        "image_path": IMAGE_PATH,
        "detected_objects_count": len(detected_objects),
        "scene_data": scene_data,
        "user_input": user_input,
        "budget_result": budget_data,
        "llm_model": LLM_MODEL_PATH,
        "renderer_version": "v2"
    }
    output.save_pipeline_summary(pipeline_summary)

    print("Pipeline complete. Outputs saved.")


if __name__ == "__main__":
    run_pipeline()