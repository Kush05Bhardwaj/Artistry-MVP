from app.services.room_analysis import analyze_room
from app.services.decor_suggestions import generate_decor
from app.services.diy_guidance import generate_diy
from app.services.cost_estimation import estimate_cost
from app.services.visualization import generate_before_after
from app.services.storage import save_design

def redesign_room(image_path):
    # 1. Analyze room (vision)
    analysis = analyze_room(image_path)

    # 2. AI decor suggestions
    decor = generate_decor(analysis)

    # 3. AI DIY guidance
    diy = generate_diy(analysis)

    # 4. AI cost estimation
    cost = estimate_cost(analysis)

    # 5. Before/After visuals
    visuals = generate_before_after(image_path)

    # 6. Save full design
    payload = {
        "analysis": analysis,
        "decor_suggestions": decor,
        "diy_guidance": diy,
        "cost_estimate": cost,
        "visuals": visuals
    }

    design_path = save_design(payload)

    return {
        "design_id": design_path,
        **payload
    }
