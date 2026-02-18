import torch
import numpy as np
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image


class DiffusionRenderer:

    def __init__(self):
        # Auto-detect device (CUDA if available, else CPU)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        print(f"🖼️  Loading Diffusion Renderer on {self.device.upper()}...")
        
        self.pipe = StableDiffusionInpaintPipeline.from_pretrained(
            "runwayml/stable-diffusion-inpainting",
            torch_dtype=dtype
        ).to(self.device)
        
        print(f"✅ Diffusion Renderer ready on {self.device.upper()}")

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