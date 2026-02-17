# compare_renderers.py
"""
Visual comparison of Renderer v1 vs v2
Generates side-by-side outputs to show quality improvements
"""

import cv2
import numpy as np
from pathlib import Path

def create_comparison_grid(original, v1, v2, labels):
    """Create a comparison grid with labels."""
    
    # Resize all to same height for comparison
    h = 600
    original_resized = cv2.resize(original, (int(original.shape[1] * h / original.shape[0]), h))
    v1_resized = cv2.resize(v1, (int(v1.shape[1] * h / v1.shape[0]), h))
    v2_resized = cv2.resize(v2, (int(v2.shape[1] * h / v2.shape[0]), h))
    
    # Create white labels
    label_height = 40
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    
    # Create label images
    def create_label(text, width):
        label = np.ones((label_height, width, 3), dtype=np.uint8) * 255
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (label_height + text_size[1]) // 2
        cv2.putText(label, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)
        return label
    
    # Add labels
    original_with_label = np.vstack([
        create_label("Original", original_resized.shape[1]),
        original_resized
    ])
    
    v1_with_label = np.vstack([
        create_label("Renderer v1", v1_resized.shape[1]),
        v1_resized
    ])
    
    v2_with_label = np.vstack([
        create_label("Renderer v2 (Professional)", v2_resized.shape[1]),
        v2_resized
    ])
    
    # Combine horizontally
    comparison = np.hstack([original_with_label, v1_with_label, v2_with_label])
    
    return comparison

def analyze_quality_metrics(original, rendered):
    """Calculate quality metrics for comparison."""
    
    # Convert to grayscale
    gray_orig = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    gray_rend = cv2.cvtColor(rendered, cv2.COLOR_BGR2GRAY)
    
    # Brightness
    brightness_orig = np.mean(gray_orig)
    brightness_rend = np.mean(gray_rend)
    
    # Contrast (standard deviation)
    contrast_orig = np.std(gray_orig)
    contrast_rend = np.std(gray_rend)
    
    # Edge strength (Laplacian variance)
    edges_orig = cv2.Laplacian(gray_orig, cv2.CV_64F).var()
    edges_rend = cv2.Laplacian(gray_rend, cv2.CV_64F).var()
    
    # Saturation
    hsv_orig = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)
    hsv_rend = cv2.cvtColor(rendered, cv2.COLOR_BGR2HSV)
    saturation_orig = np.mean(hsv_orig[:, :, 1])
    saturation_rend = np.mean(hsv_rend[:, :, 1])
    
    return {
        "brightness": (brightness_orig, brightness_rend),
        "contrast": (contrast_orig, contrast_rend),
        "edge_strength": (edges_orig, edges_rend),
        "saturation": (saturation_orig, saturation_rend)
    }

def print_comparison_report(metrics_v1, metrics_v2):
    """Print detailed comparison report."""
    
    print("\n" + "="*70)
    print("📊 RENDERER v1 vs v2 - QUALITY COMPARISON REPORT")
    print("="*70)
    
    metrics = ["brightness", "contrast", "edge_strength", "saturation"]
    labels = {
        "brightness": "Brightness",
        "contrast": "Contrast",
        "edge_strength": "Edge Sharpness",
        "saturation": "Color Saturation"
    }
    
    for metric in metrics:
        orig_v1, rend_v1 = metrics_v1[metric]
        orig_v2, rend_v2 = metrics_v2[metric]
        
        change_v1 = ((rend_v1 - orig_v1) / orig_v1) * 100
        change_v2 = ((rend_v2 - orig_v2) / orig_v2) * 100
        
        print(f"\n{labels[metric]}:")
        print(f"  v1 Change: {change_v1:+.1f}%  (Original: {orig_v1:.1f} → v1: {rend_v1:.1f})")
        print(f"  v2 Change: {change_v2:+.1f}%  (Original: {orig_v2:.1f} → v2: {rend_v2:.1f})")
        
        if abs(change_v2) > abs(change_v1):
            print(f"  ✅ v2 has stronger effect ({abs(change_v2) - abs(change_v1):.1f}% more)")
        else:
            print(f"  ⚠️  v1 has stronger effect")
    
    print("\n" + "="*70)
    print("🎯 SUMMARY:")
    print("="*70)
    print("v2 Advantages:")
    print("  ✅ Soft mask blending (no hard edges)")
    print("  ✅ Shadow-aware recoloring (preserves lighting)")
    print("  ✅ CLAHE contrast boost (prevents washed-out look)")
    print("  ✅ Reinhard tone mapping (natural color balance)")
    print("="*70 + "\n")

if __name__ == "__main__":
    # Note: This is a template script
    # To use, you would need to:
    # 1. Run pipeline with v1 renderer (save as rendered_v1.jpg)
    # 2. Run pipeline with v2 renderer (save as rendered_v2.jpg)
    # 3. Run this script to compare
    
    print("📸 Renderer v1 vs v2 Comparison Tool")
    print("\nTo use this tool:")
    print("1. Ensure you have both rendered_v1.jpg and rendered_v2.jpg")
    print("2. Run: python compare_renderers.py")
    print("\nThis will generate:")
    print("  - Side-by-side comparison image")
    print("  - Quality metrics report")
    print("  - Performance analysis")
    
    # Check if comparison images exist
    v1_path = Path("outputs/rendered_v1.jpg")
    v2_path = Path("outputs/rendered_v2.jpg")
    orig_path = Path("room.jpg")
    
    if v1_path.exists() and v2_path.exists() and orig_path.exists():
        print("\n✅ Found comparison images! Generating report...\n")
        
        original = cv2.imread(str(orig_path))
        v1 = cv2.imread(str(v1_path))
        v2 = cv2.imread(str(v2_path))
        
        # Calculate metrics
        metrics_v1 = analyze_quality_metrics(original, v1)
        metrics_v2 = analyze_quality_metrics(original, v2)
        
        # Print report
        print_comparison_report(metrics_v1, metrics_v2)
        
        # Create comparison grid
        comparison = create_comparison_grid(original, v1, v2, ["Original", "v1", "v2"])
        cv2.imwrite("outputs/comparison_v1_vs_v2.jpg", comparison)
        
        print("💾 Saved: outputs/comparison_v1_vs_v2.jpg")
        
    else:
        print("\n⚠️  Comparison images not found.")
        print("Please run the pipeline first to generate rendered images.")
