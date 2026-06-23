from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="GenAI Document Assistant",
    description="REST API for uploading documents and asking questions using LLM models",
    version="1.0.0"
)

app.include_router(router)