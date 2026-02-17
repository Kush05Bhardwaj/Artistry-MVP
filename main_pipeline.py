# main_pipeline.py

import json
import os
import cv2
import numpy as np

from detect import run_detection
from segment import Segmenter
from scene_builder import build_scene_data
from llm_engine import LLMEngine
from budget_engine import calculate_total_cost, evaluate_budget
from output_manager import OutputManager

from sam_engine import SAMEngine
from diffusion_renderer import DiffusionRenderer


IMAGE_PATH = "room.jpg"
LLM_MODEL_PATH = r"F:\llama\models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"


def resize_for_diffusion(image, max_width=768):
    h, w = image.shape[:2]
    if w > max_width:
        scale = max_width / w
        image = cv2.resize(image, (int(w * scale), int(h * scale)))
    return image


def run_pipeline():

    os.makedirs("outputs", exist_ok=True)

    output = OutputManager()
    output.save_input_image(IMAGE_PATH)

    print("Running detection...")
    detected_objects = run_detection(IMAGE_PATH, output)

    print("Running segmentation...")
    segmenter = Segmenter()
    seg_map = segmenter.segment(IMAGE_PATH)
    region_stats = segmenter.extract_region_stats(seg_map)

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
    structured_plan, raw_response = llm_engine.generate_design(
        scene_data,
        user_input
    )

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

    print("Loading SAM...")
    sam_engine = SAMEngine()

    print("Loading Diffusion Renderer...")
    diff_renderer = DiffusionRenderer()

    print("Rendering with AI Inpainting...")

    image = cv2.imread(IMAGE_PATH)
    image = resize_for_diffusion(image)

    final_image = image.copy()

    # Example logic: apply change to curtain if LLM suggests replacing it
    if "changes" in structured_plan:

        for change in structured_plan["changes"]:

            if change["target"] == "curtain":

                # find curtain box from YOLO
                for obj in detected_objects:
                    if obj["type"] == "curtain":

                        box = obj["box"]  # [x1, y1, x2, y2]

                        mask = sam_engine.get_mask_from_box(
                            final_image,
                            box
                        )

                        prompt = change.get(
                            "prompt",
                            "modern light beige linen curtain, soft folds"
                        )

                        print(f"Inpainting: {prompt}")

                        final_image = diff_renderer.inpaint(
                            final_image,
                            mask,
                            prompt
                        )

    cv2.imwrite("outputs/rendered_ai.jpg", final_image)

    # Save full pipeline summary
    pipeline_summary = {
        "image_path": IMAGE_PATH,
        "detected_objects_count": len(detected_objects),
        "scene_data": scene_data,
        "user_input": user_input,
        "budget_result": budget_data,
        "llm_model": LLM_MODEL_PATH,
        "renderer": "SAM + Stable Diffusion Inpainting"
    }

    output.save_pipeline_summary(pipeline_summary)

    print("Pipeline complete.")
    print("AI rendered image saved at outputs/rendered_ai.jpg")


if __name__ == "__main__":
    run_pipeline()