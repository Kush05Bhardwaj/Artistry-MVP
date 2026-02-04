COST_MAP = {
    "sofa": 12000,
    "bed": 15000,
    "table": 6000,
    "chair": 3000,
    "lamp": 2500,
}

def estimate_cost(objects):
    cost = 0
    for obj in objects:
        cost += COST_MAP.get(obj["label"], 4000)

    return {"estimated_cost_inr": cost}
