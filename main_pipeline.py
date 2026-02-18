# main_pipeline.py

import json
import os
import cv2
import numpy as np
import urllib.request
from pathlib import Path

from detect import run_detection
from segment import Segmenter
from scene_builder import build_scene_data
from llm_engine import LLMEngine
from budget_engine import calculate_total_cost, evaluate_budget
from output_manager import OutputManager

from renderer import RendererV2
# from sam_engine import SAMEngine
# from diffusion_renderer import DiffusionRenderer


IMAGE_PATH = "room.jpg"
LLM_MODEL_PATH = r"F:\llama\models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
SAM_MODEL_PATH = "models/sam_vit_b_01ec64.pth"
SAM_MODEL_URL = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"


def ensure_sam_model():
    """Download SAM model if not present."""
    if os.path.exists(SAM_MODEL_PATH):
        file_size = os.path.getsize(SAM_MODEL_PATH) / (1024 * 1024)
        print(f"✅ SAM model found ({file_size:.1f} MB)")
        return
    
    print(f"📥 SAM model not found. Downloading...")
    print(f"   Size: ~375 MB (this may take a few minutes)")
    
    os.makedirs("models", exist_ok=True)
    
    def progress_hook(count, block_size, total_size):
        downloaded = count * block_size
        percent = min(100, int(downloaded * 100 / total_size))
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\r   [{bar}] {percent}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)
    
    try:
        urllib.request.urlretrieve(SAM_MODEL_URL, SAM_MODEL_PATH, progress_hook)
        print("\n✅ SAM model downloaded successfully!")
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print(f"\nPlease download manually from:")
        print(f"   {SAM_MODEL_URL}")
        print(f"   Save to: {SAM_MODEL_PATH}")
        raise


def resize_for_diffusion(image, max_width=768):
    h, w = image.shape[:2]
    if w > max_width:
        scale = max_width / w
        image = cv2.resize(image, (int(w * scale), int(h * scale)))
    return image


def run_pipeline():
    # Ensure SAM model is available before starting
    ensure_sam_model()
    
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

    # Apply traditional rendering (fast, reliable)
    print("🎨 Applying design changes with Renderer v2...")
    
    renderer = RendererV2()
    image = cv2.imread(IMAGE_PATH)
    
    # Create mask dictionary from segmentation map
    segmentation_masks = {}
    
    # Get label mapping from segmenter
    label_to_id = {v.strip(): k for k, v in segmenter.labels.items()}
    
    print(f"  Available labels: {', '.join(sorted(label_to_id.keys())[:20])}...")
    
    # Extract individual masks
    if "wall" in label_to_id:
        wall_id = label_to_id["wall"]
        segmentation_masks["wall"] = (seg_map == wall_id).astype(np.uint8)
        wall_pixels = segmentation_masks["wall"].sum()
        print(f"  ✓ Wall mask created ({wall_pixels:,} pixels)")
    else:
        print(f"  ⚠️  No 'wall' label found")
    
    if "curtain" in label_to_id:
        curtain_id = label_to_id["curtain"]
        segmentation_masks["curtain"] = (seg_map == curtain_id).astype(np.uint8)
        curtain_pixels = segmentation_masks["curtain"].sum()
        print(f"  ✓ Curtain mask created ({curtain_pixels:,} pixels)")
    else:
        print(f"  ⚠️  No 'curtain' label found")
    
    # Apply rendering with LLM plan
    rendered_image = renderer.render(
        image=image,
        segmentation_masks=segmentation_masks,
        plan=structured_plan
    )
    
    # Save rendered result to run folder
    output.save_image("rendered_design.jpg", rendered_image)
    
    # Also save to outputs root for easy access
    cv2.imwrite("outputs/rendered_v2.jpg", rendered_image)

    # Save full pipeline summary
    pipeline_summary = {
        "image_path": IMAGE_PATH,
        "detected_objects_count": len(detected_objects),
        "scene_data": scene_data,
        "user_input": user_input,
        "budget_result": budget_data,
        "llm_model": LLM_MODEL_PATH,
        "renderer": "Traditional Renderer v2 (OpenCV + Advanced CV)"
    }

    output.save_pipeline_summary(pipeline_summary)

    print("\n✅ Pipeline complete!")
    print(f"📁 All outputs saved to: {output.run_dir}")
    print(f"🎨 Rendered image: outputs/rendered_v2.jpg")


if __name__ == "__main__":
    run_pipeline()