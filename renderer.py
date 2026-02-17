# renderer.py

import cv2
import numpy as np


class Renderer:
    """
    Renderer v2 - Professional image processing with:
    - Soft mask blending (blurred edges)
    - Shadow-aware recoloring (preserves lighting)
    - Contrast boost after brightening
    - Tone mapping for natural results
    - Debug artifact saving for production
    """

    def __init__(self, segmentation_map, labels, output_manager=None):
        self.seg_map = segmentation_map
        self.labels = labels
        self.output_manager = output_manager
        self.actions_applied = []  # Track successful operations
        self.original_image = None  # Store for mask visualization

    def get_mask(self, label_name):
        """Get boolean mask for a specific label."""
        label_id = None
        for k, v in self.labels.items():
            if v.strip() == label_name:
                label_id = k
                break

        if label_id is None:
            return None

        return (self.seg_map == label_id)

    def create_soft_mask(self, mask, blur_kernel_size=21):
        """
        Create soft-edged mask with Gaussian blur.
        Prevents hard edges and patchy results.
        """
        # Convert boolean mask to uint8
        mask_uint8 = (mask.astype(np.uint8) * 255)
        
        # Apply Gaussian blur for soft edges
        soft_mask = cv2.GaussianBlur(mask_uint8, (blur_kernel_size, blur_kernel_size), 0)
        
        # Normalize to 0-1 range for blending
        return soft_mask.astype(np.float32) / 255.0

    def get_luminance_mask(self, image, threshold=100):
        """
        Extract luminance (brightness) mask for shadow-aware operations.
        Returns mask where pixels are above threshold (lit areas).
        """
        # Convert to grayscale to get luminance
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create mask for bright areas only
        luminance_mask = (gray > threshold).astype(np.float32)
        
        # Smooth the transition
        luminance_mask = cv2.GaussianBlur(luminance_mask, (15, 15), 0)
        
        return luminance_mask

    def brighten_room(self, image, intensity=0.3):
        """
        v2: Brighten with gamma + contrast boost.
        Prevents washed-out look.
        """
        # Step 1: Gamma correction for brightening
        gamma = 1.0 / (1.0 + intensity * 1.5)
        
        table = np.array([
            ((i / 255.0) ** gamma) * 255
            for i in np.arange(0, 256)
        ]).astype("uint8")

        brightened = cv2.LUT(image, table)
        
        # Step 2: Add slight exposure boost
        brightened = cv2.convertScaleAbs(brightened, alpha=1.0, beta=10)
        
        # Step 3: CONTRAST BOOST (prevents washed-out look)
        # Convert to LAB, boost L channel contrast
        lab = cv2.cvtColor(brightened, cv2.COLOR_BGR2LAB).astype(np.float32)
        l, a, b = cv2.split(lab)
        
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_uint8 = l.astype(np.uint8)
        l_enhanced = clahe.apply(l_uint8).astype(np.float32)
        
        # Merge back
        lab_enhanced = cv2.merge([l_enhanced, a, b]).astype(np.uint8)
        result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        
        return result

    def warm_lighting(self, image, shift=10):
        """
        v2: Warm lighting with tone-aware adjustment.
        Preserves natural color relationships.
        """
        # Work in float32 for precision
        img_float = image.astype(np.float32)
        b, g, r = cv2.split(img_float)
        
        # Calculate current warmth level
        warmth = (r + g) - (b * 2)
        warmth_normalized = np.clip(warmth / 255.0, 0, 1)
        
        # Adaptive shift: less shift where already warm
        adaptive_shift = shift * (1.0 - warmth_normalized * 0.5)
        
        # Apply warm tone shift
        r = np.clip(r + adaptive_shift * 2, 0, 255)
        g = np.clip(g + adaptive_shift * 0.5, 0, 255)
        b = np.clip(b - adaptive_shift * 1.5, 0, 255)
        
        result = cv2.merge([b, g, r]).astype(np.uint8)
        
        return result

    def recolor_region_v2(self, image, mask, target_color_bgr, preserve_lighting=True):
        """
        v2: Shadow-aware recoloring with soft mask blending.
        
        Args:
            image: Input image
            mask: Boolean mask of region
            target_color_bgr: Target color (B, G, R)
            preserve_lighting: If True, only recolor lit areas
        """
        if mask is None or not np.any(mask):
            return image
        
        # Step 1: Create soft-edged mask (prevents hard edges)
        soft_mask = self.create_soft_mask(mask, blur_kernel_size=31)
        
        # Step 2: Shadow-aware masking (only recolor lit areas)
        if preserve_lighting:
            luminance_mask = self.get_luminance_mask(image, threshold=80)
            # Combine segmentation mask with luminance mask
            combined_mask = soft_mask * luminance_mask
        else:
            combined_mask = soft_mask
        
        # Step 3: Extract current lighting from original image
        # Convert to LAB to separate luminance from color
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Convert target color to LAB
        target_pixel = np.uint8([[target_color_bgr]])
        target_lab = cv2.cvtColor(target_pixel, cv2.COLOR_BGR2LAB)[0][0].astype(np.float32)
        
        # Step 4: Recolor while preserving luminance variation
        # Keep original L channel, replace A and B with target color
        a_recolored = np.full_like(a_channel, target_lab[1])
        b_recolored = np.full_like(b_channel, target_lab[2])
        
        # Blend original and recolored using the combined mask
        for i, (orig, new) in enumerate([(a_channel, a_recolored), (b_channel, b_recolored)]):
            if i == 0:
                a_final = orig * (1 - combined_mask) + new * combined_mask
            else:
                b_final = orig * (1 - combined_mask) + new * combined_mask
        
        # Merge back to LAB then to BGR
        lab_final = cv2.merge([l_channel, a_final, b_final]).astype(np.uint8)
        result = cv2.cvtColor(lab_final, cv2.COLOR_LAB2BGR)
        
        return result

    def replace_curtain_v2(self, image, mask):
        """v2: Curtain replacement with soft blending."""
        cream_white = np.array([245, 245, 250])  # BGR: light cream color
        return self.recolor_region_v2(image, mask, cream_white, preserve_lighting=True)

    def apply_tone_mapping(self, image):
        """
        Final tone mapping step for natural, balanced results.
        Uses Reinhard tone mapping to prevent over-saturation.
        """
        # Convert to float32 for processing
        img_float = image.astype(np.float32) / 255.0
        
        # Simple Reinhard tone mapping
        # Formula: L_out = L_in / (1 + L_in)
        img_mapped = img_float / (1.0 + img_float)
        
        # Slight saturation boost for vibrant results
        hsv = cv2.cvtColor((img_mapped * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        
        # Boost saturation by 10%
        s = np.clip(s * 1.1, 0, 255)
        
        hsv_final = cv2.merge([h, s, v]).astype(np.uint8)
        result = cv2.cvtColor(hsv_final, cv2.COLOR_HSV2BGR)
        
        return result

    def render(self, image_path, structured_plan):
        """
        Render v2: Apply design changes with professional image processing.
        Saves all debug artifacts for production debugging.
        """
        import time
        
        # Load image from path
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Failed to load image from: {image_path}")
        
        self.original_image = image.copy()
        output = image.copy()
        processing_times = {}
        
        print(f"\n🎨 Rendering v2 - {len(structured_plan.get('changes', []))} changes...")

        for i, change in enumerate(structured_plan.get("changes", []), 1):

            action = change.get("action")
            print(f"  {i}. Applying {action}...", end=" ")
            
            start_time = time.time()

            if action == "brighten_room":
                intensity = change.get("intensity", 0.3)
                output = self.brighten_room(output, intensity)
                
                self.actions_applied.append({
                    "action": action,
                    "intensity": intensity,
                    "status": "success"
                })
                
                print(f"✓ (intensity={intensity}, with contrast boost)")

            elif action == "warm_lighting":
                shift = change.get("temperature_shift", 10)
                output = self.warm_lighting(output, shift)
                
                self.actions_applied.append({
                    "action": action,
                    "temperature_shift": shift,
                    "status": "success"
                })
                
                print(f"✓ (shift={shift}, adaptive)")

            elif action == "recolor_wall":
                wall_mask = self.get_mask("wall")
                if wall_mask is not None:
                    pixels_affected = np.sum(wall_mask)
                    
                    # Save debug masks if output_manager available
                    if self.output_manager:
                        # Save original hard mask
                        self.output_manager.save_mask_visualization(
                            "wall_mask_hard", wall_mask, self.original_image
                        )
                        
                        # Create and save soft mask
                        soft_mask = self.create_soft_mask(wall_mask, blur_kernel_size=31)
                        self.output_manager.save_mask_visualization(
                            "wall_mask_soft", soft_mask, self.original_image
                        )
                        
                        # Save luminance mask
                        luminance_mask = self.get_luminance_mask(output, threshold=80)
                        self.output_manager.save_mask_visualization(
                            "wall_luminance_mask", luminance_mask, self.original_image
                        )
                        
                        # Save combined mask
                        combined_mask = soft_mask * luminance_mask
                        self.output_manager.save_mask_visualization(
                            "wall_combined_mask", combined_mask, self.original_image
                        )
                    
                    # Use shadow-aware v2 recoloring
                    output = self.recolor_region_v2(
                        output,
                        wall_mask,
                        np.array([235, 240, 245]),  # BGR: soft warm white
                        preserve_lighting=True
                    )
                    
                    self.actions_applied.append({
                        "action": action,
                        "pixels_affected": int(pixels_affected),
                        "preserve_lighting": True,
                        "status": "success"
                    })
                    
                    print(f"✓ ({pixels_affected} pixels, shadow-aware)")
                else:
                    self.actions_applied.append({
                        "action": action,
                        "status": "failed",
                        "reason": "no_mask_found"
                    })
                    print("⚠ No wall mask found")

            elif action == "replace_curtain":
                curtain_mask = self.get_mask("curtain")
                if curtain_mask is not None:
                    pixels_affected = np.sum(curtain_mask)
                    
                    # Save debug masks if output_manager available
                    if self.output_manager:
                        # Save original hard mask
                        self.output_manager.save_mask_visualization(
                            "curtain_mask_hard", curtain_mask, self.original_image
                        )
                        
                        # Create and save soft mask
                        soft_mask = self.create_soft_mask(curtain_mask, blur_kernel_size=31)
                        self.output_manager.save_mask_visualization(
                            "curtain_mask_soft", soft_mask, self.original_image
                        )
                    
                    output = self.replace_curtain_v2(output, curtain_mask)
                    
                    self.actions_applied.append({
                        "action": action,
                        "pixels_affected": int(pixels_affected),
                        "status": "success"
                    })
                    
                    print(f"✓ ({pixels_affected} pixels, soft blend)")
                else:
                    self.actions_applied.append({
                        "action": action,
                        "status": "failed",
                        "reason": "no_mask_found"
                    })
                    print("⚠ No curtain mask found")
            
            else:
                self.actions_applied.append({
                    "action": action,
                    "status": "failed",
                    "reason": "unknown_action"
                })
                print(f"⚠ Unknown action: {action}")
            
            # Record processing time
            processing_times[action] = round((time.time() - start_time) * 1000, 2)

        # FINAL STEP: Tone mapping for natural results
        print("  🎨 Applying final tone mapping...", end=" ")
        start_time = time.time()
        output = self.apply_tone_mapping(output)
        processing_times["tone_mapping"] = round((time.time() - start_time) * 1000, 2)
        print("✓")
        
        # Save renderer metadata
        if self.output_manager:
            self.output_manager.save_renderer_metadata(
                self.actions_applied,
                processing_times
            )
        
        print("✓ Rendering v2 complete\n")
        return output
        print("✓")
        
        print("✓ Rendering v2 complete\n")
        return output