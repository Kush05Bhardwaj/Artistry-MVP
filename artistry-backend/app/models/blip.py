from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

def caption_image(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(
        image,
        text="Describe this interior room in detail",
        return_tensors="pt"
    )
    output = model.generate(**inputs, max_length=60)
    return processor.decode(output[0], skip_special_tokens=True)
