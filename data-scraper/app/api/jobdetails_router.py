import traceback

from icecream import ic
from fastapi import APIRouter, Depends, HTTPException

from app.common.core.jobdetails import JobDetails

jobdetails_router = APIRouter()
jobdetails = JobDetails()


@jobdetails_router.post("/scrape")
async def scrape_job_details():
    try:
        jobdetails.scrape_and_insert()
        return {"status": "success"}
    except Exception as e:
        ic(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
