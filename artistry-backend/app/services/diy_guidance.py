def diy_steps(objects):
    steps = []
    if "bed" in objects:
        steps.append("Change bedsheets and add a headboard panel")
    if "wall" in objects:
        steps.append("Apply peel-and-stick wallpaper")

    return steps
