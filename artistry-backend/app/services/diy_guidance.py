def diy_steps(objects):
    steps = []
    labels = [o["label"] for o in objects]

    if "wall" in labels:
        steps.append("Apply peel-and-stick wallpaper")
    if "lamp" in labels:
        steps.append("Replace bulbs with warm LEDs")
    if "sofa" in labels:
        steps.append("Add throws and cushion covers")

    return steps or ["Rearrange furniture for better space usage"]
