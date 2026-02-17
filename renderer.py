# renderer.py

import cv2
import numpy as np


class Renderer:

    def __init__(self, segmentation_map, labels):
        self.seg_map = segmentation_map
        self.labels = labels

    def get_mask(self, label_name):
        label_id = None
        for k, v in self.labels.items():
            if v.strip() == label_name:
                label_id = k
                break

        if label_id is None:
            return None

        return (self.seg_map == label_id)

    def brighten_room(self, image, intensity=0.3):
        gamma = 1.0 - intensity
        inv_gamma = 1.0 / gamma

        table = np.array([
            ((i / 255.0) ** inv_gamma) * 255
            for i in np.arange(0, 256)
        ]).astype("uint8")

        return cv2.LUT(image, table)

    def warm_lighting(self, image, shift=10):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        b = cv2.add(b, shift)

        merged = cv2.merge([l, a, b])
        return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    def recolor_region(self, image, mask, color_bgr):
        overlay = image.copy()
        overlay[mask] = color_bgr

        return cv2.addWeighted(overlay, 0.4, image, 0.6, 0)

    def replace_curtain(self, image, mask):
        white_linen = np.array([220, 220, 220])
        return self.recolor_region(image, mask, white_linen)

    def render(self, image_path, structured_plan):
        # Load image from path
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Failed to load image from: {image_path}")
        
        output = image.copy()

        for change in structured_plan.get("changes", []):

            action = change.get("action")

            if action == "brighten_room":
                output = self.brighten_room(output, change.get("intensity", 0.3))

            elif action == "warm_lighting":
                output = self.warm_lighting(output, change.get("temperature_shift", 10))

            elif action == "recolor_wall":
                wall_mask = self.get_mask("wall")
                if wall_mask is not None:
                    output = self.recolor_region(
                        output,
                        wall_mask,
                        np.array([200, 200, 200])  # soft gray
                    )

            elif action == "replace_curtain":
                curtain_mask = self.get_mask("curtain")
                if curtain_mask is not None:
                    output = self.replace_curtain(output, curtain_mask)

        return output