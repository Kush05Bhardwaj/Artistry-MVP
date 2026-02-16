# detect.py
from ultralytics import YOLO
import cv2

INTERIOR_CLASSES = {
    "Bed": 34,
    "Infant bed": 275,
    "Couch": 136,
    "Sofa bed": 477,
    "Loveseat": 317,
    "Studio couch": 499,
    "Chair": 104,
    "Stool": 494,
    "Desk": 153,
    "Table": 514,
    "Coffee table": 122,
    "Kitchen & dining room table": 290,
    "Nightstand": 352,
    "Wardrobe": 574,
    "Closet": 114,
    "Cabinetry": 77,
    "Cupboard": 147,
    "Chest of drawers": 107,
    "Drawer": 168,
    "Bookcase": 55,
    "Shelf": 453,
    "Lamp": 301,
    "Mirror": 335,
    "Pillow": 388,
    "Curtain": 148,
    "Door": 164,
    "Window": 587,
    "Refrigerator": 419,
    "Microwave oven": 332,
    "Oven": 360,
    "Sink": 460,
    "Toilet": 538,
    "Bathtub": 31,
    "Shower": 458,
    "Washing machine": 575,
    "Houseplant": 258,
    "Picture frame": 386,
    "Flowerpot": 196,
    "Waste container": 576,
    "Bench": 41,
}

MODEL_PATH = "yolov8m-oiv7.pt"

model = YOLO(MODEL_PATH)


def run_detection(image_path, output_manager=None):

    results = model.predict(
        source=image_path,
        imgsz=1536,
        conf=0.25,
        agnostic_nms=True,
        augment=True,
        save=False
    )

    detections = []
    annotated_img = None

    for r in results:
        boxes = r.boxes
        annotated_img = r.plot()

        for box in boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])

            detections.append({
                "type": label.lower(),
                "confidence": round(conf, 2)
            })

    if output_manager:
        output_manager.save_json("detection.json", detections)
        output_manager.save_image("detection_annotated.jpg", annotated_img)

    return detections