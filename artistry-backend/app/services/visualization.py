from PIL import Image, ImageEnhance

def generate_before_after(image_path):
    img = Image.open(image_path)
    enhancer = ImageEnhance.Color(img)
    after = enhancer.enhance(1.4)

    after_path = image_path.replace(".", "_after.")
    after.save(after_path)

    return {
        "before": image_path,
        "after": after_path
    }
