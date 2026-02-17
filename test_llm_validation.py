# test_llm_validation.py
"""
Test script to verify LLM engine validation and fallback mechanisms.
"""

import json
from llm_engine import LLMEngine

def test_validation():
    """Test the validation logic without requiring actual LLM."""
    
    engine = LLMEngine.__new__(LLMEngine)  # Create instance without __init__
    engine.ALLOWED_ACTIONS = LLMEngine.ALLOWED_ACTIONS
    
    print("🧪 Testing LLM Engine Validation\n")
    print("=" * 60)
    
    # Test 1: Valid JSON
    print("\n✅ Test 1: Valid JSON with all actions")
    valid_json = '''
    {
      "changes": [
        {
          "action": "brighten_room",
          "intensity": 0.4,
          "estimated_cost": 2000
        },
        {
          "action": "warm_lighting",
          "temperature_shift": 15,
          "estimated_cost": 1500
        },
        {
          "action": "recolor_wall",
          "color": "warm white",
          "estimated_cost": 5000
        },
        {
          "action": "replace_curtain",
          "new_curtain": "white linen",
          "estimated_cost": 3000
        }
      ]
    }
    '''
    result = engine._extract_and_validate_json(valid_json)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result is not None
    assert len(result['changes']) == 4
    print("✓ PASSED")
    
    # Test 2: JSON with invalid action
    print("\n⚠️  Test 2: JSON with invalid action (should filter out)")
    invalid_action = '''
    {
      "changes": [
        {
          "action": "paint_ceiling",
          "color": "blue"
        },
        {
          "action": "brighten_room",
          "intensity": 0.3
        }
      ]
    }
    '''
    result = engine._extract_and_validate_json(invalid_action)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result is not None
    assert len(result['changes']) == 1  # Only valid action remains
    assert result['changes'][0]['action'] == 'brighten_room'
    print("✓ PASSED (invalid action filtered)")
    
    # Test 3: JSON with out-of-range values
    print("\n🔧 Test 3: JSON with out-of-range values (should clamp)")
    out_of_range = '''
    {
      "changes": [
        {
          "action": "brighten_room",
          "intensity": 0.9,
          "estimated_cost": 2000
        },
        {
          "action": "warm_lighting",
          "temperature_shift": 50,
          "estimated_cost": 1500
        }
      ]
    }
    '''
    result = engine._extract_and_validate_json(out_of_range)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result['changes'][0]['intensity'] <= 0.5  # Clamped
    assert result['changes'][1]['temperature_shift'] <= 25  # Clamped
    print(f"✓ PASSED (intensity clamped to {result['changes'][0]['intensity']}, temp clamped to {result['changes'][1]['temperature_shift']})")
    
    # Test 4: Missing parameters (should use defaults)
    print("\n🔧 Test 4: Missing parameters (should use defaults)")
    missing_params = '''
    {
      "changes": [
        {
          "action": "brighten_room"
        },
        {
          "action": "recolor_wall"
        }
      ]
    }
    '''
    result = engine._extract_and_validate_json(missing_params)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert 'intensity' in result['changes'][0]  # Default added
    assert 'estimated_cost' in result['changes'][0]  # Default added
    assert 'color' in result['changes'][1]  # Default added
    print("✓ PASSED (defaults applied)")
    
    # Test 5: Completely invalid JSON
    print("\n❌ Test 5: Completely invalid JSON (should return None)")
    invalid = "This is not JSON at all!"
    result = engine._extract_and_validate_json(invalid)
    print(f"Result: {result}")
    assert result is None
    print("✓ PASSED (returns None)")
    
    # Test 6: JSON embedded in text
    print("\n🔍 Test 6: JSON embedded in markdown/text (should extract)")
    embedded = '''
    Sure! Here's the design plan:
    
    ```json
    {
      "changes": [
        {
          "action": "brighten_room",
          "intensity": 0.3,
          "estimated_cost": 2000
        }
      ]
    }
    ```
    
    Hope this helps!
    '''
    result = engine._extract_and_validate_json(embedded)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result is not None
    assert len(result['changes']) == 1
    print("✓ PASSED (extracted JSON from text)")
    
    # Test 7: Fallback plan generation
    print("\n🛡️  Test 7: Fallback plan generation")
    scene_data = {
        "brightness_score": 100,  # Low brightness
        "regions": {
            "wall_percent": 30.0,
            "curtain_percent": 8.0
        }
    }
    user_input = {
        "budget": 50000,
        "priority": "make room brighter"
    }
    result = engine._generate_fallback_plan(scene_data, user_input)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result is not None
    assert len(result['changes']) > 0
    # Should include brighten_room due to low brightness
    actions = [c['action'] for c in result['changes']]
    assert 'brighten_room' in actions
    print("✓ PASSED (fallback plan generated)")
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    test_validation()
