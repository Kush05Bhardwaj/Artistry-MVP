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
        # Brightening using gamma correction
        # Higher intensity = brighter image
        gamma = 1.0 / (1.0 + intensity * 1.5)  # Amplify the effect
        
        table = np.array([
            ((i / 255.0) ** gamma) * 255
            for i in np.arange(0, 256)
        ]).astype("uint8")

        result = cv2.LUT(image, table)
        # Also increase brightness slightly
        result = cv2.convertScaleAbs(result, alpha=1.0, beta=10)
        return result

    def warm_lighting(self, image, shift=10):
        # Shift towards warmer tones (increase red/yellow, decrease blue)
        # Work in BGR color space for more visible effect
        b, g, r = cv2.split(image.astype(np.float32))
        
        # Increase red channel (warm)
        r = np.clip(r + shift * 2, 0, 255)
        # Increase green slightly
        g = np.clip(g + shift * 0.5, 0, 255)
        # Decrease blue (reduce cool tones)
        b = np.clip(b - shift * 1.5, 0, 255)
        
        return cv2.merge([b, g, r]).astype(np.uint8)

    def recolor_region(self, image, mask, color_bgr):
        overlay = image.copy()
        overlay[mask] = color_bgr

        # Increase blend ratio for more visible effect
        return cv2.addWeighted(overlay, 0.6, image, 0.4, 0)

    def replace_curtain(self, image, mask):
        # More visible white/cream curtains
        cream_white = np.array([245, 245, 250])  # BGR: light cream color
        return self.recolor_region(image, mask, cream_white)

    def render(self, image_path, structured_plan):
        # Load image from path
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Failed to load image from: {image_path}")
        
        output = image.copy()
        
        print(f"\n🎨 Rendering {len(structured_plan.get('changes', []))} changes...")

        for i, change in enumerate(structured_plan.get("changes", []), 1):

            action = change.get("action")
            print(f"  {i}. Applying {action}...", end=" ")

            if action == "brighten_room":
                intensity = change.get("intensity", 0.3)
                output = self.brighten_room(output, intensity)
                print(f"✓ (intensity={intensity})")

            elif action == "warm_lighting":
                shift = change.get("temperature_shift", 10)
                output = self.warm_lighting(output, shift)
                print(f"✓ (shift={shift})")

            elif action == "recolor_wall":
                wall_mask = self.get_mask("wall")
                if wall_mask is not None:
                    pixels_affected = np.sum(wall_mask)
                    # Use a more visible soft white/cream color
                    output = self.recolor_region(
                        output,
                        wall_mask,
                        np.array([235, 240, 245])  # BGR: soft warm white
                    )
                    print(f"✓ ({pixels_affected} pixels)")
                else:
                    print("⚠ No wall mask found")

            elif action == "replace_curtain":
                curtain_mask = self.get_mask("curtain")
                if curtain_mask is not None:
                    pixels_affected = np.sum(curtain_mask)
                    output = self.replace_curtain(output, curtain_mask)
                    print(f"✓ ({pixels_affected} pixels)")
                else:
                    print("⚠ No curtain mask found")
            
            else:
                print(f"⚠ Unknown action: {action}")

        print("✓ Rendering complete\n")
        return output