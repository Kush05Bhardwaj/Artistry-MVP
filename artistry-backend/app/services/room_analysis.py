from app.models.yolo import detect_objects
from app.models.blip import caption_image

def analyze_room(image_path):
    objects = detect_objects(image_path)
    description = caption_image(image_path)

    return {
        "objects": objects,
        "description": description
    }
