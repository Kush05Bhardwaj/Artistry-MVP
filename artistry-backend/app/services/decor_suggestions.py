def suggest_decor(room_analysis):
    objects = room_analysis["detected_objects"]

    suggestions = []
    if "sofa" in objects:
        suggestions.append("Add accent cushions and a rug")
    if "window" in objects:
        suggestions.append("Use sheer curtains for natural light")

    return suggestions
