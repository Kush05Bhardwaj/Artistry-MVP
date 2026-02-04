from app.models.yolo import detect_objects
from app.models.blip import caption_image

def analyze_room(image_path):
    objects = detect_objects(image_path)
    caption = caption_image(image_path)

    return {
        "detected_objects": objects,
        "room_description": caption
    }
