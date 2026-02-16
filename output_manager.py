# output_manager.py

import os
import json
import shutil
from datetime import datetime
import cv2


class OutputManager:

    def __init__(self, base_dir="outputs"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(base_dir, f"run_{timestamp}")
        os.makedirs(self.run_dir, exist_ok=True)

    def save_input_image(self, image_path):
        shutil.copy(image_path, os.path.join(self.run_dir, "input.jpg"))

    def save_json(self, filename, data):
        path = os.path.join(self.run_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=self._convert_numpy)

    def save_text(self, filename, text):
        path = os.path.join(self.run_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def save_image(self, filename, image):
        path = os.path.join(self.run_dir, filename)
        cv2.imwrite(path, image)

    def _convert_numpy(self, obj):
        try:
            import numpy as np
            if isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            if isinstance(obj, (np.int32, np.int64)):
                return int(obj)
        except:
            pass
        return obj