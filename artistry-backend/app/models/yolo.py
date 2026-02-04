from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_objects(image_path):
    results = model(image_path, conf=0.35)[0]
    detections = []

    for box in results.boxes:
        label = model.names[int(box.cls)]
        conf = float(box.conf)
        detections.append({"label": label, "confidence": round(conf, 2)})

    return detections
