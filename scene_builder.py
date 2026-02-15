# scene_builder.py

def build_scene(detected_objects, seg_map, segmenter, image):

    total_pixels = image.width * image.height

    wall_mask = segmenter.get_mask(seg_map, "wall")
    floor_mask = segmenter.get_mask(seg_map, "floor")
    bed_mask = segmenter.get_mask(seg_map, "bed")
    curtain_mask = segmenter.get_mask(seg_map, "curtain")

    regions = {
        "wall_percent": round(100 * wall_mask.sum() / total_pixels, 2),
        "floor_percent": round(100 * floor_mask.sum() / total_pixels, 2),
        "bed_percent": round(100 * bed_mask.sum() / total_pixels, 2),
        "curtain_percent": round(100 * curtain_mask.sum() / total_pixels, 2),
    }

    scene_data = {
        "room_type": "bedroom",
        "objects": detected_objects,
        "regions": regions
    }

    return scene_data