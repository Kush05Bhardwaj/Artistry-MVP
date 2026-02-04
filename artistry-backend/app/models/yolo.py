from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_objects(image_path):
    results = model(image_path)
    labels = [box.cls for box in results[0].boxes]
    return labels
