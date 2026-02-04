def estimate_cost(objects):
    base_cost = 5000
    return {
        "estimated_cost": base_cost + len(objects) * 2000
    }
