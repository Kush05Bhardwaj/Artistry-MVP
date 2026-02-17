import torch
import numpy as np
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image


class DiffusionRenderer:

    def __init__(self):
        self.pipe = StableDiffusionInpaintPipeline.from_pretrained(
            "runwayml/stable-diffusion-inpainting",
            torch_dtype=torch.float16
        ).to("cuda")

    def inpaint(self, image, mask, prompt):
        image_pil = Image.fromarray(image)
        mask_pil = Image.fromarray(
            (mask * 255).astype(np.uint8)
        )

        result = self.pipe(
            prompt=prompt,
            image=image_pil,
            mask_image=mask_pil,
            guidance_scale=7.5,
            num_inference_steps=30
        ).images[0]

        return np.array(result)