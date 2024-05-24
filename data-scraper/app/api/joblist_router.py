import traceback

from icecream import ic
from fastapi import APIRouter, Depends, HTTPException

from app.common.core.joblist import JobList

joblist_router = APIRouter()
joblist = JobList()


@joblist_router.post("/scrape")
async def scrape_job_ids():
    try:
        joblist.scrape_and_insert()
        return {"status": "success"}
    except Exception as e:
        ic(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
