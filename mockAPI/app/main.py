from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Mock Government API",
    description="Mock for GビズID + Myna Portal (リダイレクト指定あり)",
    version="1.0"
)

app.include_router(router)
