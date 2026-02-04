from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="Artistry AI Backend",
    version="0.1.0"
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"status": "Artistry backend running"}
