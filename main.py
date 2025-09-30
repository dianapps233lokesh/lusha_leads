from fastapi import FastAPI

from app.api.routes import router
from app.api.serp_api_routes import router as serp_router

app = FastAPI(title="Lusha API Integration")

app.include_router(router, prefix="/api")
app.include_router(serp_router, prefix="/serp")
