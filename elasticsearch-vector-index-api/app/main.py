from fastapi import FastAPI

import app.config.settings
from app.routers.wanted_job_indexing_router import router as wanted_job_indexing_router

app = FastAPI()

app.include_router(wanted_job_indexing_router, prefix="/api/v1/index/wanted", tags=["wanted_job_indexing"])


@app.get("/health")
async def health_check():
    return {"message": "I'm alive!"}
