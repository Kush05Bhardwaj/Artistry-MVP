def suggest_decor(objects):
    ideas = []

    labels = [o["label"] for o in objects]

    if "sofa" in labels:
        ideas.append("Add textured cushions and a neutral rug")
    if "bed" in labels:
        ideas.append("Use layered bedding and warm bedside lighting")
    if "window" in labels:
        ideas.append("Install sheer curtains for soft daylight")

    return ideas or ["Minimal modern decor with neutral tones"]
