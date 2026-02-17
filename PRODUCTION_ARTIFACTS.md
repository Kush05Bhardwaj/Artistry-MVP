# Production Artifact Saving - Complete Implementation

## Overview
Upgraded output management to save **ALL** intermediate artifacts for production-grade debugging, auditing, and reproduction.

---

## 📦 Complete Artifact Inventory

### **Core Outputs** (Already existed)
1. ✅ `detection.json` - YOLOv8 detected objects
2. ✅ `detection_annotated.jpg` - Annotated image with bounding boxes
3. ✅ `segmentation_overlay.jpg` - Colored segmentation visualization
4. ✅ `segmentation_stats.json` - Region percentages (wall, floor, bed, curtain)
5. ✅ `scene_data.json` - Combined scene analysis
6. ✅ `structured_plan.json` - LLM-generated design plan
7. ✅ `llm_raw.txt` - Raw LLM response
8. ✅ `budget_result.json` - Cost analysis
9. ✅ `rendered_v1.jpg` - Final rendered image
10. ✅ `input.jpg` - Copy of original input

### **NEW Production Artifacts** ⭐
11. ✅ `segmentation_raw.npy` - **Raw numpy array** (exact reproduction)
12. ✅ `renderer_applied_actions.json` - **Action tracking & timings**
13. ✅ `pipeline_summary.json` - **Comprehensive execution summary**
14. ✅ `renderer_debug_masks/` - **Full mask visualizations** (12 files)
15. ✅ `debug/` - **Debug images directory** (extensible)

---

## 🔬 Detailed Breakdown

### 1. `segmentation_raw.npy` ✨ NEW

**Purpose**: Exact reproduction of segmentation output

**Format**: NumPy binary array
```python
seg_map = np.load("segmentation_raw.npy")
# Shape: (867, 1156), dtype: uint8
# Values: 0-150 (label IDs from SegFormer)
```

**Why Critical**:
- PNG/JPG compression loses exact pixel values
- `.npy` preserves exact uint8 label IDs
- Can reproduce renderer behavior exactly
- Essential for debugging edge cases

**Use Cases**:
```python
# Load and inspect
seg_map = np.load("segmentation_raw.npy")

# Check what labels are present
unique_labels = np.unique(seg_map)

# Verify wall detection
wall_id = 4  # From model.config.id2label
wall_pixels = np.sum(seg_map == wall_id)

# Reproduce exact mask used in rendering
wall_mask = (seg_map == wall_id)
```

---

### 2. `renderer_applied_actions.json` ✨ NEW

**Purpose**: Track every operation the renderer performed

**Format**: JSON with action details and performance metrics
```json
{
  "timestamp": "2026-02-17T12:07:51.404128",
  "actions_applied": [
    {
      "action": "brighten_room",
      "intensity": 0.3,
      "status": "success"
    },
    {
      "action": "recolor_wall",
      "pixels_affected": 328856,
      "preserve_lighting": true,
      "status": "success"
    }
  ],
  "total_actions": 4,
  "processing_times_ms": {
    "brighten_room": 121.13,
    "warm_lighting": 29.57,
    "recolor_wall": 98.61,
    "replace_curtain": 73.14,
    "tone_mapping": 40.43
  }
}
```

**Why Critical**:
- Audit trail of what was actually applied
- Performance profiling per operation
- Failed operations tracked (e.g., "no_mask_found")
- Essential for production monitoring

**Use Cases**:
```python
# Load and analyze
with open("renderer_applied_actions.json") as f:
    actions = json.load(f)

# Check success rate
total = len(actions["actions_applied"])
success = sum(1 for a in actions["actions_applied"] if a["status"] == "success")
print(f"Success rate: {success}/{total}")

# Performance analysis
times = actions["processing_times_ms"]
slowest = max(times.items(), key=lambda x: x[1])
print(f"Slowest operation: {slowest[0]} ({slowest[1]}ms)")

# Verify specific action
wall_action = next(a for a in actions["actions_applied"] if a["action"] == "recolor_wall")
print(f"Wall pixels affected: {wall_action['pixels_affected']}")
```

---

### 3. `pipeline_summary.json` ✨ NEW

**Purpose**: Complete end-to-end execution summary

**Format**: Comprehensive JSON with all pipeline data
```json
{
  "run_id": "run_20260217_120707",
  "timestamp": "2026-02-17T12:07:51.411132",
  "image_path": "room.jpg",
  "detected_objects_count": 21,
  "scene_data": {
    "brightness_score": 109.04,
    "clutter_score": 1.15,
    "regions": {"wall_percent": 32.81, ...}
  },
  "user_input": {
    "style": "modern minimal",
    "budget": 50000,
    "priority": "make room brighter"
  },
  "budget_result": {
    "total_cost": 16500,
    "status": "✅ Within budget."
  },
  "llm_model": "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
  "renderer_version": "v2"
}
```

**Why Critical**:
- Single file with complete execution context
- Perfect for API response auditing
- A/B testing comparison
- Client reporting

**Use Cases**:
```python
# Load complete context
with open("pipeline_summary.json") as f:
    summary = json.load(f)

# Audit trail
print(f"Run ID: {summary['run_id']}")
print(f"Brightness: {summary['scene_data']['brightness_score']}")
print(f"Budget: {summary['budget_result']['total_cost']} / {summary['user_input']['budget']}")

# Reproduce run
llm_model = summary["llm_model"]
user_input = summary["user_input"]
# Re-run with exact same parameters

# Analytics
brightness = summary["scene_data"]["brightness_score"]
cost = summary["budget_result"]["total_cost"]
# Track correlations
```

---

### 4. `renderer_debug_masks/` ✨ NEW

**Purpose**: Visual debugging of every mask operation

**Files** (12 total):
```
renderer_debug_masks/
├── wall_mask_hard.png              # Original segmentation mask
├── wall_mask_hard_overlay.jpg      # Mask overlaid on image
├── wall_mask_soft.png              # After Gaussian blur
├── wall_mask_soft_overlay.jpg      # Soft mask visualization
├── wall_luminance_mask.png         # Shadow detection mask
├── wall_luminance_mask_overlay.jpg # Where recoloring applies
├── wall_combined_mask.png          # Final combined mask
├── wall_combined_mask_overlay.jpg  # What actually gets recolored
├── curtain_mask_hard.png           # Original curtain mask
├── curtain_mask_hard_overlay.jpg   # Hard mask visualization
├── curtain_mask_soft.png           # After Gaussian blur
└── curtain_mask_soft_overlay.jpg   # Soft blend visualization
```

**Why Critical**:
- Debug why walls didn't recolor properly
- Verify soft masking is working
- Understand shadow preservation
- Visual proof of operations

**Use Cases**:
```
Problem: "Walls look patchy"
Debug:
1. Check wall_mask_hard_overlay.jpg
   → Is segmentation accurate?
2. Check wall_mask_soft_overlay.jpg
   → Is Gaussian blur working?
3. Check wall_luminance_mask_overlay.jpg
   → Are shadows being preserved?
4. Check wall_combined_mask_overlay.jpg
   → Final mask looks correct?

Problem: "Some walls didn't change color"
Debug:
1. Check wall_luminance_mask_overlay.jpg
   → Those areas are in shadow (working as intended)
```

---

## 📊 Directory Structure

```
outputs/run_20260217_120707/
├── Core Outputs
│   ├── input.jpg                           # Original image
│   ├── detection.json                      # YOLO results
│   ├── detection_annotated.jpg             # Annotated image
│   ├── segmentation_overlay.jpg            # Colored segmentation
│   ├── segmentation_stats.json             # Region percentages
│   ├── scene_data.json                     # Scene analysis
│   ├── llm_raw.txt                         # Raw LLM response
│   ├── structured_plan.json                # Design plan
│   ├── budget_result.json                  # Cost analysis
│   └── rendered_v1.jpg                     # Final output
│
├── Production Artifacts ⭐ NEW
│   ├── segmentation_raw.npy                # Raw numpy array
│   ├── renderer_applied_actions.json       # Action tracking
│   └── pipeline_summary.json               # Complete summary
│
├── Debug Masks ⭐ NEW
│   └── renderer_debug_masks/
│       ├── wall_mask_hard.png
│       ├── wall_mask_hard_overlay.jpg
│       ├── wall_mask_soft.png
│       ├── wall_mask_soft_overlay.jpg
│       ├── wall_luminance_mask.png
│       ├── wall_luminance_mask_overlay.jpg
│       ├── wall_combined_mask.png
│       ├── wall_combined_mask_overlay.jpg
│       ├── curtain_mask_hard.png
│       ├── curtain_mask_hard_overlay.jpg
│       ├── curtain_mask_soft.png
│       └── curtain_mask_soft_overlay.jpg
│
└── Debug Images (extensible)
    └── debug/
        └── (future intermediate visualizations)
```

---

## 🔧 Code Implementation

### OutputManager Enhancements

```python
class OutputManager:
    def __init__(self, base_dir="outputs"):
        # Create organized subdirectories
        self.debug_dir = os.path.join(self.run_dir, "debug")
        self.masks_dir = os.path.join(self.run_dir, "renderer_debug_masks")
    
    def save_numpy(self, filename, array):
        """Save raw numpy array (.npy format)"""
        np.save(path, array)
    
    def save_mask_visualization(self, mask_name, mask, original_image):
        """Save mask + overlay visualization"""
        # Grayscale mask
        cv2.imwrite(f"{mask_name}.png", mask_vis)
        # Blue overlay on original
        cv2.imwrite(f"{mask_name}_overlay.jpg", overlay)
    
    def save_renderer_metadata(self, actions_applied, processing_times):
        """Save action tracking + performance data"""
        json.dump({
            "actions_applied": actions_applied,
            "processing_times_ms": processing_times
        }, f)
    
    def save_pipeline_summary(self, summary_data):
        """Save complete execution summary"""
        json.dump(summary_data, f)
```

### Renderer Integration

```python
class Renderer:
    def __init__(self, seg_map, labels, output_manager=None):
        self.output_manager = output_manager
        self.actions_applied = []  # Track operations
    
    def render(self, image_path, structured_plan):
        # Track timing
        start_time = time.time()
        
        # ... apply operation ...
        
        # Save debug masks
        if self.output_manager:
            self.output_manager.save_mask_visualization(
                "wall_mask_hard", wall_mask, self.original_image
            )
        
        # Record action
        self.actions_applied.append({
            "action": action,
            "status": "success",
            "pixels_affected": pixels
        })
        
        # Record timing
        processing_times[action] = time.time() - start_time
```

---

## 🚀 Production Benefits

### 1. **Debugging** 🐛
```
Customer: "The wall didn't change color"

Without artifacts:
❌ "I don't know why, let me investigate..."

With artifacts:
✅ Check renderer_applied_actions.json
   → Action status: "failed", reason: "no_mask_found"
✅ Check segmentation_raw.npy
   → Load and verify: wall_percent = 0%
✅ Root cause: Segmentation didn't detect walls
```

### 2. **Performance Monitoring** 📊
```python
# Analyze performance across runs
for run in runs:
    with open(f"{run}/renderer_applied_actions.json") as f:
        data = json.load(f)
    
    total_time = sum(data["processing_times_ms"].values())
    print(f"{run}: {total_time}ms")

# Track average
avg_brighten = np.mean([r["brighten_room"] for r in all_runs])
```

### 3. **A/B Testing** 🧪
```python
# Compare v1 vs v2 renderer
v1_summary = load_json("run_v1/pipeline_summary.json")
v2_summary = load_json("run_v2/pipeline_summary.json")

print(f"v1 renderer: {v1_summary['renderer_version']}")
print(f"v2 renderer: {v2_summary['renderer_version']}")

# Same input, different results
assert v1_summary["user_input"] == v2_summary["user_input"]
```

### 4. **Exact Reproduction** 🔄
```python
# Reproduce exact run from artifacts
seg_map = np.load("segmentation_raw.npy")
summary = load_json("pipeline_summary.json")

# Re-run with exact same parameters
user_input = summary["user_input"]
scene_data = summary["scene_data"]

# Should produce identical output
```

### 5. **Client Reporting** 📈
```python
# Generate client report from summary
summary = load_json("pipeline_summary.json")

report = f"""
Design Report
=============
Run ID: {summary['run_id']}
Date: {summary['timestamp']}

Room Analysis:
- Brightness Score: {summary['scene_data']['brightness_score']}/255
- Wall Coverage: {summary['scene_data']['regions']['wall_percent']}%

Design Changes:
{len(structured_plan['changes'])} actions applied

Budget:
- Total Cost: ₹{summary['budget_result']['total_cost']}
- Budget: ₹{summary['user_input']['budget']}
- Status: {summary['budget_result']['status']}
"""
```

---

## 📈 Storage Analysis

### File Sizes (Typical)
```
input.jpg                      ~800 KB
detection.json                 ~2 KB
detection_annotated.jpg        ~900 KB
segmentation_raw.npy           ~1 MB    ⭐ NEW
segmentation_overlay.jpg       ~850 KB
segmentation_stats.json        ~1 KB
scene_data.json                ~2 KB
llm_raw.txt                    ~1 KB
structured_plan.json           ~1 KB
renderer_applied_actions.json  ~2 KB    ⭐ NEW
pipeline_summary.json          ~3 KB    ⭐ NEW
budget_result.json             ~1 KB
rendered_v1.jpg                ~850 KB
renderer_debug_masks/          ~8 MB    ⭐ NEW (12 files)
--------------------------------------
TOTAL PER RUN:                 ~12 MB
```

**Storage Recommendations**:
- Development: Keep all (~12 MB/run)
- Production API: Keep for 30 days, archive to S3
- Long-term: Keep summary + final image only (~1 MB)

---

## 🎯 API Service Integration

When this becomes an API:

```python
@app.post("/api/design")
async def generate_design(image: UploadFile, params: DesignParams):
    # Run pipeline
    output = OutputManager()
    result = run_pipeline(image, params, output)
    
    # Return response with artifact URLs
    return {
        "run_id": output.get_run_dir(),
        "result_image_url": f"/outputs/{run_id}/rendered_v1.jpg",
        "debug_artifacts": {
            "masks": f"/outputs/{run_id}/renderer_debug_masks/",
            "summary": f"/outputs/{run_id}/pipeline_summary.json",
            "actions": f"/outputs/{run_id}/renderer_applied_actions.json"
        },
        "metadata": load_json(f"{run_id}/pipeline_summary.json")
    }
```

**Benefits**:
- Client can download debug artifacts if needed
- Support team can investigate issues
- Analytics team can track performance
- Legal team has audit trail

---

## ✅ Implementation Checklist

All requirements met:

- ✅ `segmentation_raw.npy` - Raw numpy array saved
- ✅ `renderer_debug_masks/` - 12 mask visualizations
- ✅ `renderer_applied_actions.json` - Action tracking + timing
- ✅ `pipeline_summary.json` - Comprehensive summary
- ✅ `debug/` - Extensible debug directory
- ✅ Organized subdirectories
- ✅ Backward compatible (all old artifacts still saved)

**Bonus**:
- ✅ Performance timing for each operation
- ✅ Failed action tracking with reasons
- ✅ Mask overlays for visual debugging
- ✅ Complete execution context in single JSON

---

## 📚 Documentation Generated

1. ✅ Code comments and docstrings
2. ✅ This comprehensive guide
3. ✅ Usage examples for each artifact
4. ✅ Production integration patterns
5. ✅ Storage recommendations
6. ✅ Debugging workflows

---

## 🎉 Status: COMPLETE

**Artifact Saving**: ✅ **Production Ready**  
**Debug Capability**: 🟢 **Comprehensive**  
**API Ready**: 🟢 **Yes**  
**Storage Efficient**: 🟢 **~12 MB/run**  

**When this becomes an API service, this debugging power is GOLD.** 💰✨
