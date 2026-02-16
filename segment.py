# segment.py

import torch
import numpy as np
import cv2
from PIL import Image
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation


class Segmenter:
    _model = None
    _processor = None

    def __init__(self):
        if Segmenter._model is None:
            print("Loading segmentation model (one-time)...")

            Segmenter._processor = SegformerImageProcessor.from_pretrained(
                "nvidia/segformer-b0-finetuned-ade-512-512"
            )

            Segmenter._model = SegformerForSemanticSegmentation.from_pretrained(
                "nvidia/segformer-b0-finetuned-ade-512-512"
            )

        self.processor = Segmenter._processor
        self.model = Segmenter._model
        self.labels = self.model.config.id2label

    def segment(self, image_path):
        image = Image.open(image_path)
        inputs = self.processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        segmentation = outputs.logits.argmax(dim=1)[0].cpu().numpy()

        seg_resized = cv2.resize(
            segmentation.astype(np.uint8),
            (image.width, image.height),
            interpolation=cv2.INTER_NEAREST
        )

        return seg_resized

    def extract_region_stats(self, seg_map):
        total_pixels = seg_map.size

        def get_percent(label_name):
            label_id = next(
                (k for k, v in self.labels.items() if v.strip() == label_name),
                None
            )
            if label_id is None:
                return 0
            return round(float(np.sum(seg_map == label_id)) / total_pixels * 100, 2)

        return {
            "wall_percent": get_percent("wall"),
            "floor_percent": get_percent("floor"),
            "bed_percent": get_percent("bed"),
            "curtain_percent": get_percent("curtain"),
            "segmented_image": seg_resized,
            "overlay": overlay
        }
    
        