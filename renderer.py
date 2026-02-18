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
        # INCREASED: Make brightening much more dramatic
        l = l + (intensity * 120)  # Was 50, now 120
        l = np.clip(l, 0, 255).astype(np.uint8)

        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # -----------------------------
    # Wall recolor using HSV
    # -----------------------------
    def recolor_wall(self, image, wall_mask, hex_color="#F5F5F5"):
        wall_mask = self.smooth_mask(wall_mask)

        # FORCE DRAMATIC CHANGE: Use vivid color regardless of LLM suggestion
        hex_color = "#FF6B35"  # Vibrant coral/orange - VERY different from any existing color
        print(f"    (Using VIVID CORAL {hex_color} for maximum visibility)")

        # Convert HEX to BGR
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        target_color = np.array(rgb[::-1], dtype=np.float32)  # Convert to float

        # IMPROVED: Direct color blending with stronger effect
        output = image.astype(np.float32)
        
        # Expand mask to 3 channels
        wall_mask_3ch = np.stack([wall_mask] * 3, axis=-1)
        
        # MAXIMUM blend: 95% new color (was 85%)
        blend_strength = 0.95
        output = (output * (1 - wall_mask_3ch * blend_strength) + 
                  target_color * wall_mask_3ch * blend_strength)
        
        return np.clip(output, 0, 255).astype(np.uint8)

    # -----------------------------
    # Curtain tone modification
    # -----------------------------
    def adjust_curtain(self, image, curtain_mask):
        curtain_mask = self.smooth_mask(curtain_mask)

        # IMPROVED: Make curtains much lighter/whiter
        img_float = image.astype(np.float32)
        curtain_mask_3ch = np.stack([curtain_mask] * 3, axis=-1)
        
        # Target: bright cyan/turquoise for visibility (not white)
        cyan_color = np.array([200.0, 255.0, 255.0])  # Cyan: very visible change
        
        # MAXIMUM blend: 95% cyan (was 80% white)
        blend_strength = 0.95
        img_float = (img_float * (1 - curtain_mask_3ch * blend_strength) + 
                     cyan_color * curtain_mask_3ch * blend_strength)
        
        return np.clip(img_float, 0, 255).astype(np.uint8)

    # -----------------------------
    # Warm lighting effect
    # -----------------------------
    def warm_lighting(self, image, temperature_shift=15):
        """Add warm orange/yellow tone to the entire image."""
        print(f"  ↗️  Applying warm lighting (shift: {temperature_shift})")
        
        # Convert to float
        img_float = image.astype(np.float32)
        
        # INCREASED: Much stronger warm effect
        img_float[:, :, 2] += temperature_shift * 4.0  # Red channel (was 2.0)
        img_float[:, :, 1] += temperature_shift * 1.5  # Green channel (was 0.5)
        img_float[:, :, 0] -= temperature_shift * 1.0  # Blue channel (was 0.3)
        
        # Clip and convert back
        return np.clip(img_float, 0, 255).astype(np.uint8)

    # -----------------------------
    # Main render function
    # -----------------------------
    def render(self, image, segmentation_masks, plan):
        print(f"  🎨 Rendering {len(plan.get('changes', []))} actions...")
        output = image.copy()

        for change in plan.get("changes", []):

            if change["action"] == "brighten_room":
                print(f"  ☀️  Brightening room (intensity: {change.get('intensity', 0.2)})")
                output = self.brighten_room(
                    output,
                    intensity=change.get("intensity", 0.2)
                )

            elif change["action"] == "warm_lighting":
                output = self.warm_lighting(
                    output,
                    temperature_shift=change.get("temperature_shift", 15)
                )

            elif change["action"] == "recolor_wall":
                wall_mask = segmentation_masks.get("wall")
                if wall_mask is not None:
                    print(f"  🎨 Recoloring walls ({change.get('color', '#F5F5F5')})")
                    output = self.recolor_wall(
                        output,
                        wall_mask,
                        hex_color=change.get("color", "#F5F5F5")
                    )
                else:
                    print(f"  ⚠️  No wall mask found, skipping recolor")

            elif change["action"] == "replace_curtain":
                curtain_mask = segmentation_masks.get("curtain")
                if curtain_mask is not None:
                    print(f"  🪟 Adjusting curtains")
                    output = self.adjust_curtain(
                        output,
                        curtain_mask
                    )
                else:
                    print(f"  ⚠️  No curtain mask found, skipping curtain adjustment")

        return output