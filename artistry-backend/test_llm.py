from app.models.llm import ask_llm

print(
    ask_llm(
        "You are a helpful assistant",
        "Give 3 interior design tips for a small bedroom"
    )
)
