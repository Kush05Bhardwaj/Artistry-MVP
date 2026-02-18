import cv2
import numpy as np
from segment import Segmenter

# Load and segment the image
segmenter = Segmenter()
seg_map = segmenter.segment("room.jpg")

# Get label mapping
label_to_id = {v.strip(): k for k, v in segmenter.labels.items()}

print("Available labels with pixel counts:")
for label, label_id in sorted(label_to_id.items())[:30]:
    pixel_count = (seg_map == label_id).sum()
    if pixel_count > 1000:  # Only show labels with significant presence
        print(f"  {label}: {pixel_count:,} pixels ({pixel_count/seg_map.size*100:.2f}%)")

# Create visualization for wall and curtain masks
image = cv2.imread("room.jpg")
h, w = image.shape[:2]

# Wall mask
if "wall" in label_to_id:
    wall_id = label_to_id["wall"]
    wall_mask = (seg_map == wall_id).astype(np.uint8) * 255
    
    # Overlay wall mask in red
    wall_viz = image.copy()
    wall_viz[:, :, 2] = np.maximum(wall_viz[:, :, 2], wall_mask)  # Red channel
    cv2.imwrite("outputs/debug_wall_mask.jpg", wall_viz)
    print(f"\n✓ Wall mask saved: {wall_mask.sum()/255:,} pixels")

# Curtain mask
if "curtain" in label_to_id:
    curtain_id = label_to_id["curtain"]
    curtain_mask = (seg_map == curtain_id).astype(np.uint8) * 255
    
    # Overlay curtain mask in green
    curtain_viz = image.copy()
    curtain_viz[:, :, 1] = np.maximum(curtain_viz[:, :, 1], curtain_mask)  # Green channel
    cv2.imwrite("outputs/debug_curtain_mask.jpg", curtain_viz)
    print(f"✓ Curtain mask saved: {curtain_mask.sum()/255:,} pixels")

# Combined visualization
combined = image.copy()
if "wall" in label_to_id:
    wall_mask_3ch = np.stack([wall_mask] * 3, axis=-1)
    combined = cv2.addWeighted(combined, 0.7, wall_mask_3ch // 3, 0.3, 0)
if "curtain" in label_to_id:
    combined[:, :, 1] = np.maximum(combined[:, :, 1], curtain_mask // 2)

cv2.imwrite("outputs/debug_combined_masks.jpg", combined)
print("✓ Combined mask visualization saved")

print("\nCheck outputs/debug_*_mask.jpg to see what's being detected")
