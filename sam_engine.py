import torch
import cv2
import numpy as np
from segment_anything import sam_model_registry, SamPredictor


class SAMEngine:
    def __init__(self, model_path="models/sam_vit_b_01ec64.pth"):
        # Automatically detect available device (CUDA if available, else CPU)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"SAM using device: {device}")
        
        sam = sam_model_registry["vit_b"](checkpoint=model_path)
        sam.to(device=device)
        self.predictor = SamPredictor(sam)
        self.device = device

    def get_mask_from_box(self, image, box):
        self.predictor.set_image(image)

        input_box = np.array(box)
        masks, scores, _ = self.predictor.predict(
            box=input_box,
            multimask_output=False
        )

        return masks[0]