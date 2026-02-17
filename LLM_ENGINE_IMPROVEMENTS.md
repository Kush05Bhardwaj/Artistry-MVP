# LLM Engine Improvements - Structured Output Reliability

## Overview
Upgraded the LLM engine to ensure **deterministic, reliable structured output** with strict validation and fail-safe fallbacks.

## Key Improvements

### 1. **Strict JSON-Only Output** ✅
- **Hard constraint**: LLM MUST output only valid JSON
- **No markdown**, no explanations, no commentary
- Stop sequences prevent the LLM from rambling
- Lower temperature (0.3) for more deterministic output

### 2. **Allowed Actions Schema** ✅
Enforced whitelist of exactly 4 allowed actions:

```json
{
  "brighten_room": {
    "intensity": 0.1-0.5,
    "estimated_cost": number
  },
  "warm_lighting": {
    "temperature_shift": 5-25,
    "estimated_cost": number
  },
  "recolor_wall": {
    "color": "string (optional)",
    "estimated_cost": number
  },
  "replace_curtain": {
    "new_curtain": "string (optional)",
    "estimated_cost": number
  }
}
```

**Validation Rules:**
- Invalid actions are rejected
- Parameters are clamped to safe ranges
- Missing parameters use sensible defaults
- All actions include `estimated_cost`

### 3. **Multi-Layer Validation** ✅

**Layer 1: JSON Extraction**
- Regex pattern matching to find JSON in response
- Fallback to full text parsing
- Handles malformed LLM output gracefully

**Layer 2: Structure Validation**
- Ensures `changes` array exists
- Validates each change is a dictionary
- Checks action names against whitelist

**Layer 3: Parameter Validation**
- Applies default values for missing parameters
- Clamps numeric values to safe ranges:
  - `intensity`: 0.1 to 0.5
  - `temperature_shift`: 5 to 25
- Type conversion and error handling

### 4. **Fail-Safe Fallback Plan** ✅

If LLM output is invalid or parsing fails, the system generates a **deterministic fallback plan** based on scene analysis:

#### Fallback Rules:
```python
# Rule 1: Low brightness → brighten room
if brightness_score < 120 or "bright" in priority:
    add brighten_room (intensity=0.4, cost=₹2000)

# Rule 2: Cozy/warm requested → warm lighting
if "cozy" in priority or "warm" in priority:
    add warm_lighting (shift=15, cost=₹1500)

# Rule 3: Significant wall area → recolor walls
if wall_percent > 20%:
    add recolor_wall (color="warm white", cost=₹5000)

# Rule 4: Curtains detected → replace curtains
if curtain_percent > 5%:
    add replace_curtain (new_curtain="white linen", cost=₹3000)

# Rule 5: Budget-aware
Only add changes if remaining budget allows
```

**Guarantee**: Renderer ALWAYS gets valid, meaningful changes - even if LLM fails completely.

## System Flow

```
┌─────────────────┐
│   LLM Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Generation  │ ← Lower temp, stop sequences
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ JSON Extraction │ ← Regex pattern matching
└────────┬────────┘
         │
    ┌────┴────┐
    │ Valid?  │
    └────┬────┘
         │
    NO ──┼── YES
         │         │
         ▼         ▼
┌─────────────┐ ┌──────────────┐
│  Fallback   │ │  Validate    │
│    Plan     │ │  Actions     │
└──────┬──────┘ └──────┬───────┘
       │               │
       │               ▼
       │        ┌──────────────┐
       │        │ Validate     │
       │        │ Parameters   │
       │        └──────┬───────┘
       │               │
       └───────┬───────┘
               ▼
        ┌─────────────┐
        │   Renderer  │ ← ALWAYS gets valid plan
        └─────────────┘
```

## Testing the System

### Test Case 1: Normal LLM Output
```bash
python main_pipeline.py
```
**Expected**: LLM generates valid JSON → validated → rendered

### Test Case 2: Malformed LLM Output
Simulate by setting temperature very high or modifying prompt.
**Expected**: Validation fails → Fallback plan activates → rendered

### Test Case 3: LLM Failure
Disconnect network or use invalid model path.
**Expected**: Generation fails → Fallback plan activates → rendered

## Benefits

✅ **Reliability**: System never crashes due to LLM output  
✅ **Determinism**: Fallback plan is predictable and scene-aware  
✅ **Safety**: All parameters validated and clamped  
✅ **Debuggability**: Raw LLM output saved to `llm_raw.txt`  
✅ **Budget-Aware**: Fallback respects user budget constraints  
✅ **Graceful Degradation**: System works even with LLM offline  

## Files Modified

1. **`llm_engine.py`** - Complete rewrite with validation layers
2. **`scene_builder.py`** - Added `avg_brightness` for fallback compatibility

## Configuration

Adjust these constants in `LLMEngine` class:

```python
# Temperature for LLM (lower = more deterministic)
temperature=0.3

# Max tokens (prevents excessive output)
max_tokens=512

# Stop sequences (prevents rambling)
stop=["```", "\n\n\n", "User:", "Scene:"]

# Brightness threshold for fallback
BRIGHTNESS_THRESHOLD = 120

# Wall/curtain percentage thresholds
WALL_THRESHOLD = 20  # %
CURTAIN_THRESHOLD = 5  # %
```

## Future Enhancements

- [ ] Add more sophisticated scene analysis for fallback
- [ ] Support user-defined custom actions
- [ ] Add confidence scores to LLM output
- [ ] Implement action priority/ordering logic
- [ ] Add A/B testing for different prompts
