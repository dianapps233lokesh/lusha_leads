from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Lusha API Integration")

app.include_router(router, prefix="/api")
