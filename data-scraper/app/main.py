from fastapi import FastAPI

from app.models.joblist_model import Base
from app.common.core.joblist import JobList
from app.api.joblist_router import joblist_router
from app.api.jobdetails_router import jobdetails_router

joblist_engine = JobList().engine
Base.metadata.create_all(bind=joblist_engine)

app = FastAPI()
app.include_router(
    joblist_router,
    prefix="/api/v1/wanted-joblist",
    tags=["wanted-joblist"]
)
app.include_router(
    jobdetails_router,
    prefix="/api/v1/wanted-jobdetails",
    tags=["wanted-jobdetails"]
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
