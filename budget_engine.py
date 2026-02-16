# budget_engine.py

def calculate_total_cost(structured_plan):
    total = 0

    for change in structured_plan.get("changes", []):
        total += change.get("estimated_cost", 0)

    return total


def evaluate_budget(total_cost, user_budget):
    if total_cost <= user_budget:
        return "✅ Within budget."
    else:
        return "❌ Over budget."