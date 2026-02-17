# output_manager.py

import os
import json
import shutil
from datetime import datetime
import cv2
import numpy as np


class OutputManager:
    """
    Production-grade output manager with comprehensive artifact saving.
    Saves all intermediate data for debugging, auditing, and reproduction.
    """

    def __init__(self, base_dir="outputs"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(base_dir, f"run_{timestamp}")
        os.makedirs(self.run_dir, exist_ok=True)
        
        # Create subdirectories for organized storage
        self.debug_dir = os.path.join(self.run_dir, "debug")
        self.masks_dir = os.path.join(self.run_dir, "renderer_debug_masks")
        os.makedirs(self.debug_dir, exist_ok=True)
        os.makedirs(self.masks_dir, exist_ok=True)
        
        print(f"📁 Output directory: {self.run_dir}")

    def save_input_image(self, image_path):
        """Save copy of input image."""
        shutil.copy(image_path, os.path.join(self.run_dir, "input.jpg"))

    def save_json(self, filename, data):
        """Save JSON data with numpy type conversion."""
        path = os.path.join(self.run_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=self._convert_numpy)

    def save_text(self, filename, text):
        """Save text file."""
        path = os.path.join(self.run_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def save_image(self, filename, image):
        """Save image file."""
        path = os.path.join(self.run_dir, filename)
        cv2.imwrite(path, image)

    def save_numpy(self, filename, array):
        """
        Save raw numpy array for exact reproduction.
        Essential for debugging segmentation issues.
        """
        path = os.path.join(self.run_dir, filename)
        np.save(path, array)
        print(f"  💾 Saved numpy array: {filename} (shape: {array.shape}, dtype: {array.dtype})")

    def save_debug_image(self, filename, image):
        """Save debug/intermediate image in debug subdirectory."""
        path = os.path.join(self.debug_dir, filename)
        cv2.imwrite(path, image)

    def save_mask_visualization(self, mask_name, mask, original_image=None):
        """
        Save mask visualization for debugging renderer operations.
        
        Args:
            mask_name: Name of the mask (e.g., "wall_mask", "soft_wall_mask")
            mask: Boolean or float mask array
            original_image: Optional - overlay mask on original image
        """
        # Convert mask to visualization
        if mask.dtype == bool:
            mask_vis = (mask.astype(np.uint8) * 255)
        elif mask.dtype == np.float32 or mask.dtype == np.float64:
            mask_vis = (mask * 255).astype(np.uint8)
        else:
            mask_vis = mask
        
        # Save grayscale mask
        mask_path = os.path.join(self.masks_dir, f"{mask_name}.png")
        cv2.imwrite(mask_path, mask_vis)
        
        # If original image provided, create overlay
        if original_image is not None:
            # Create colored overlay (blue tint)
            if len(mask_vis.shape) == 2:
                # Convert grayscale mask to 3-channel
                mask_3ch = cv2.cvtColor(mask_vis, cv2.COLOR_GRAY2BGR)
            else:
                mask_3ch = mask_vis
            
            # Resize mask to match image if needed
            if mask_3ch.shape[:2] != original_image.shape[:2]:
                mask_3ch = cv2.resize(mask_3ch, 
                                     (original_image.shape[1], original_image.shape[0]))
            
            # Create blue overlay
            overlay = original_image.copy()
            blue_mask = np.zeros_like(original_image)
            blue_mask[:, :, 0] = mask_vis  # Blue channel
            
            # Blend
            overlay = cv2.addWeighted(original_image, 0.7, blue_mask, 0.3, 0)
            
            overlay_path = os.path.join(self.masks_dir, f"{mask_name}_overlay.jpg")
            cv2.imwrite(overlay_path, overlay)
    
    def save_renderer_metadata(self, actions_applied, processing_times=None):
        """
        Save detailed renderer execution metadata.
        
        Args:
            actions_applied: List of actions that were successfully applied
            processing_times: Optional dict of operation -> time (ms)
        """
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "actions_applied": actions_applied,
            "total_actions": len(actions_applied),
            "processing_times_ms": processing_times or {}
        }
        
        path = os.path.join(self.run_dir, "renderer_applied_actions.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  📊 Saved renderer metadata: {len(actions_applied)} actions applied")

    def save_pipeline_summary(self, summary_data):
        """
        Save comprehensive pipeline execution summary.
        Useful for performance monitoring and debugging.
        
        Args:
            summary_data: Dict with pipeline execution details
        """
        summary = {
            "run_id": os.path.basename(self.run_dir),
            "timestamp": datetime.now().isoformat(),
            **summary_data
        }
        
        path = os.path.join(self.run_dir, "pipeline_summary.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=self._convert_numpy)
        
        print(f"  📋 Saved pipeline summary")

    def get_run_dir(self):
        """Get the current run directory path."""
        return self.run_dir

    def _convert_numpy(self, obj):
        """Convert numpy types to Python native types for JSON serialization."""
        try:
            if isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            if isinstance(obj, (np.int32, np.int64, np.int8, np.uint8)):
                return int(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.bool_):
                return bool(obj)
        except:
            pass
        return str(obj)  # Fallback to string representation