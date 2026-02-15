# segment.py

from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
from PIL import Image
import torch
import cv2
import numpy as np

class Segmenter:
    def __init__(self):
        self.processor = SegformerImageProcessor.from_pretrained(
            "nvidia/segformer-b0-finetuned-ade-512-512"
        )
        self.model = SegformerForSemanticSegmentation.from_pretrained(
            "nvidia/segformer-b0-finetuned-ade-512-512"
        )
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

        return seg_resized, image

    def get_mask(self, seg_map, label_name):
        label_name = label_name.strip()
        class_id = [k for k, v in self.labels.items() if v.strip() == label_name][0]
        return seg_map == class_id