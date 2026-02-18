import cv2
import numpy as np
from segment import Segmenter

# Load image
image = cv2.imread("room.jpg")

# Get wall mask
segmenter = Segmenter()
seg_map = segmenter.segment("room.jpg")
label_to_id = {v.strip(): k for k, v in segmenter.labels.items()}

wall_id = label_to_id["wall"]
wall_mask = (seg_map == wall_id).astype(np.float32)

print(f"Wall mask stats:")
print(f"  Total pixels: {wall_mask.sum():,}")
print(f"  Min: {wall_mask.min()}, Max: {wall_mask.max()}")
print(f"  Unique values: {np.unique(wall_mask)}")

# Apply Gaussian blur (smoothing)
wall_mask_smooth = cv2.GaussianBlur(wall_mask, (7, 7), 0)
print(f"\nSmoothed mask stats:")
print(f"  Min: {wall_mask_smooth.min():.3f}, Max: {wall_mask_smooth.max():.3f}")

# Target color: #F7F7F7 (very light gray, almost white)
hex_color = "#F7F7F7"
hex_color = hex_color.lstrip("#")
rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
target_color = np.array(rgb[::-1], dtype=np.float32)  # BGR
print(f"\nTarget color (BGR): {target_color}")

# Apply recoloring with 70% blend
img_float = image.astype(np.float32)
wall_mask_3ch = np.stack([wall_mask_smooth] * 3, axis=-1)

blend_strength = 0.7
output = (img_float * (1 - wall_mask_3ch * blend_strength) + 
          target_color * wall_mask_3ch * blend_strength)

output = np.clip(output, 0, 255).astype(np.uint8)

# Save test output
cv2.imwrite("outputs/test_wall_recolor.jpg", output)
print(f"\n✓ Test wall recolor saved to outputs/test_wall_recolor.jpg")

# Show sample pixels
print(f"\nSample original wall pixels (BGR):")
wall_coords = np.where(wall_mask > 0)
for i in range(min(5, len(wall_coords[0]))):
    y, x = wall_coords[0][i], wall_coords[1][i]
    orig = image[y, x]
    new = output[y, x]
    print(f"  [{y:3d},{x:3d}] {orig} -> {new}")
