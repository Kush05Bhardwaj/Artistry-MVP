import json
from datetime import datetime
from app.core.config import SAVE_DIR

def save_design(data):
    path = f"{SAVE_DIR}/design_{int(datetime.now().timestamp())}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path
