import torch
import cv2
import numpy as np
from segment_anything import sam_model_registry, SamPredictor


class SAMEngine:
    def __init__(self, model_path="models/sam_vit_b.pth"):
        sam = sam_model_registry["vit_b"](checkpoint=model_path)
        sam.to(device="cuda")
        self.predictor = SamPredictor(sam)

    def get_mask_from_box(self, image, box):
        self.predictor.set_image(image)

        input_box = np.array(box)
        masks, scores, _ = self.predictor.predict(
            box=input_box,
            multimask_output=False
        )

        return masks[0]