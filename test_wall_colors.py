import cv2
import numpy as np
from segment import Segmenter
from renderer import RendererV2

# Load and segment
segmenter = Segmenter()
seg_map = segmenter.segment("room.jpg")
image = cv2.imread("room.jpg")

# Get wall mask
label_to_id = {v.strip(): k for k, v in segmenter.labels.items()}
wall_id = label_to_id["wall"]
wall_mask = (seg_map == wall_id).astype(np.float32)

print(f"Wall mask: {wall_mask.sum():,} pixels")

# Apply renderer's recolor_wall method
renderer = RendererV2()

# Test with VERY different color - bright blue
test_colors = [
    ("#F7F7F7", "Light gray (LLM's choice)"),
    ("#D0E8F0", "Blue-gray (override)"),
    ("#0000FF", "Pure BLUE (test)"),
]

for hex_color, desc in test_colors:
    output = renderer.recolor_wall(image.copy(), wall_mask, hex_color)
    
    # Sample some wall pixels to see the change
    wall_coords = np.where(wall_mask > 0)
    sample_idx = len(wall_coords[0]) // 2  # Middle wall pixel
    y, x = wall_coords[0][sample_idx], wall_coords[1][sample_idx]
    
    orig_pixel = image[y, x]
    new_pixel = output[y, x]
    
    print(f"\n{desc} ({hex_color}):")
    print(f"  Sample pixel at [{y},{x}]:")
    print(f"    Original (BGR): {orig_pixel}")
    print(f"    New (BGR):      {new_pixel}")
    print(f"    Change:         {new_pixel - orig_pixel}")
    
    cv2.imwrite(f"outputs/test_wall_{hex_color.replace('#', '')}.jpg", output)

print("\n✓ Test outputs saved to outputs/test_wall_*.jpg")
