# scene_builder.py

from collections import Counter
import cv2
import numpy as np


def calculate_brightness(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return round(float(np.mean(gray)), 2)


def build_scene_data(image_path, detected_objects, region_stats):

    # Count objects
    object_counts = Counter()
    for obj in detected_objects:
        object_counts[obj["type"]] += 1

    clutter_score = round(
        sum(object_counts.values()) / (region_stats["floor_percent"] + 1), 2
    )

    brightness_score = calculate_brightness(image_path)

    scene_data = {
        "room_type": "bedroom",
        "object_counts": dict(object_counts),
        "regions": region_stats,
        "brightness_score": brightness_score,
        "avg_brightness": brightness_score,  # Alias for fallback compatibility
        "clutter_score": clutter_score,
    }

    return scene_data