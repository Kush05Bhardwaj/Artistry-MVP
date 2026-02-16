from llama_cpp import Llama

llm = Llama(
    model_path=r"F:\llama\models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0  # set 35 if GPU working
)

output = llm(
    "Explain interior design in 3 bullet points.",
    max_tokens=200
)

print(output["choices"][0]["text"])