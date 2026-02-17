import cv2
import numpy as np


class RendererV2:
    def __init__(self):
        pass

    # -----------------------------
    # Utility: smooth mask edges
    # -----------------------------
    def smooth_mask(self, mask, ksize=7):
        kernel = np.ones((ksize, ksize), np.uint8)
        mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
        mask = cv2.GaussianBlur(mask, (ksize, ksize), 0)
        mask = mask / 255.0
        return mask

    # -----------------------------
    # Brightness enhancement (LAB)
    # -----------------------------
    def brighten_room(self, image, intensity=0.2):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        l = l.astype(np.float32)
        l = l + (intensity * 50)
        l = np.clip(l, 0, 255).astype(np.uint8)

        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # -----------------------------
    # Wall recolor using HSV
    # -----------------------------
    def recolor_wall(self, image, wall_mask, hex_color="#F5F5F5"):
        wall_mask = self.smooth_mask(wall_mask)

        # Convert HEX to BGR
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        target_color = np.array(rgb[::-1], dtype=np.uint8)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # Convert target to HSV
        target_hsv = cv2.cvtColor(
            np.uint8([[target_color]]), cv2.COLOR_BGR2HSV
        )[0][0]

        # Blend hue + reduce saturation
        h = (h * (1 - wall_mask) + target_hsv[0] * wall_mask).astype(np.uint8)
        s = (s * (1 - wall_mask) + (target_hsv[1] * 0.3) * wall_mask).astype(np.uint8)

        new_hsv = cv2.merge([h, s, v])
        return cv2.cvtColor(new_hsv, cv2.COLOR_HSV2BGR)

    # -----------------------------
    # Curtain tone modification
    # -----------------------------
    def adjust_curtain(self, image, curtain_mask):
        curtain_mask = self.smooth_mask(curtain_mask)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # Reduce saturation + slightly brighten
        s = (s * (1 - 0.5 * curtain_mask)).astype(np.uint8)
        v = (v + 20 * curtain_mask).clip(0, 255).astype(np.uint8)

        new_hsv = cv2.merge([h, s, v])
        return cv2.cvtColor(new_hsv, cv2.COLOR_HSV2BGR)

    # -----------------------------
    # Main render function
    # -----------------------------
    def render(self, image, segmentation_masks, plan):
        output = image.copy()

        for change in plan.get("changes", []):

            if change["action"] == "brighten_room":
                output = self.brighten_room(
                    output,
                    intensity=change.get("intensity", 0.2)
                )

            elif change["action"] == "recolor_wall":
                wall_mask = segmentation_masks.get("wall")
                if wall_mask is not None:
                    output = self.recolor_wall(
                        output,
                        wall_mask,
                        hex_color=change.get("color", "#F5F5F5")
                    )

            elif change["action"] == "replace_curtain":
                curtain_mask = segmentation_masks.get("curtain")
                if curtain_mask is not None:
                    output = self.adjust_curtain(
                        output,
                        curtain_mask
                    )

        return output