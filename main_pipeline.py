# main_pipeline.py

import os
import json
import cv2
import numpy as np

from detect import run_detection
from segment import Segmenter
from scene_builder import build_scene_data
from llm_engine import LLMEngine
from budget_engine import calculate_total_cost, evaluate_budget

IMAGE_PATH = "room.jpg"
LLM_MODEL_PATH = r"F:\llama\models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"


def run_pipeline():

    print("Running detection...")
    detected_objects = run_detection(IMAGE_PATH)

    print("Running segmentation...")
    segmenter = Segmenter()
    seg_map = segmenter.segment(IMAGE_PATH)
    region_stats = segmenter.extract_region_stats(seg_map)

    print("Building scene...")
    scene_data = build_scene_data(
        IMAGE_PATH,
        detected_objects,
        region_stats
    )

    print("Scene Data:")
    print(scene_data)

    user_input = {
        "style": "modern minimal",
        "budget": 50000,
        "priority": "make room brighter",
        "constraints": "do not replace bed"
    }

    print("Loading LLM...")
    llm_engine = LLMEngine(LLM_MODEL_PATH)

    print("Generating suggestions...")
    structured_plan = llm_engine.generate_design(scene_data, user_input)

    print("Structured Plan:")
    print(structured_plan)

    total_cost = calculate_total_cost(structured_plan)
    budget_status = evaluate_budget(total_cost, user_input["budget"])

    print("\nTotal Estimated Cost:", total_cost)
    print("User Budget:", user_input["budget"])
    print(budget_status)

    ensure_output_folder()


def ensure_output_folder():
    os.makedirs("outputs", exist_ok=True)



if __name__ == "__main__":
    run_pipeline()
    