from PIL import Image, ImageEnhance

def generate_before_after(image_path):
    img = Image.open(image_path).convert("RGB")

    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = ImageEnhance.Sharpness(img).enhance(1.3)

    after_path = image_path.replace(".jpg", "_after.jpg")
    img.save(after_path)

    return {"before": image_path, "after": after_path}
