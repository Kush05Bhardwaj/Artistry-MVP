# budget_engine.py

PRICE_CATALOG = {
    "curtain replacement": 3500,
    "wall repaint per sqft": 25,
    "add rug": 8000,
    "new lamp": 2500,
    "plant decor": 2000
}

def estimate_cost(suggestions_text):
    total = 0

    for item, price in PRICE_CATALOG.items():
        if item in suggestions_text.lower():
            total += price

    return total