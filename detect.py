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
    "Houseplant": 258,
    "Shelf": 453,
    "Drawer": 168,
    "Waste container": 576
}

from ultralytics import YOLO
import cv2

model = YOLO("yolov8m-oiv7.pt")

img = cv2.imread("room.jpg")
h, w, _ = img.shape

tile_size = 768
overlap = 200

for y in range(0, h, tile_size - overlap):
    for x in range(0, w, tile_size - overlap):
        tile = img[y:y+tile_size, x:x+tile_size]
        results = model.predict(tile, conf=0.25)


furniture_ids = list(INTERIOR_CLASSES.values())

results = model.predict(
    source="room.jpg",
    imgsz=1536,
    conf=0.25,
    classes=furniture_ids,
    agnostic_nms=True,
    augment=True,
    save=True
)

