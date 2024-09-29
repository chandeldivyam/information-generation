from fastapi import FastAPI
from app.api.routes import hello

app = FastAPI(title="Your RAG Microservice")

app.include_router(hello.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Your RAG Microservice"}