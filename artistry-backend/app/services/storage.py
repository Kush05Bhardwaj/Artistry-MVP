import json
from datetime import datetime

def save_design(data):
    filename = f"saved/design_{datetime.now().timestamp()}.json"
    with open(filename, "w") as f:
        json.dump(data, f)

    return filename
