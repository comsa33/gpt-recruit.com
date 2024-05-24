import time
import random
import traceback
from contextlib import contextmanager

import requests
from icecream import ic
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from app.config.settings import MONGO_URI
from app.common.core.joblist import JobList


class JobDetails:
    def __init__(self) -> None:
        self._scrap_url = "https://www.wanted.co.kr/api/chaos/jobs/v1/{}/details"
        self.joblist = JobList()

    @contextmanager
    def mongo_client(self):
        client = MongoClient(MONGO_URI)
        try:
            yield client
        except ConnectionFailure as e:
            ic(traceback.format_exc())
            raise e
        finally:
            client.close()

    def _scrape_job_details(self, job_id: int) -> dict:
        self.joblist.mark_as_in_action(job_id)
        response = requests.get(self._scrap_url.format(job_id))
        response.raise_for_status()
        data = response.json()
        return data

    def _insert_job_details(self, collection, job_id: int, data: dict) -> bool:
        collection.insert_one({"job_id": job_id, "data": data})
        return True

    def scrape_and_insert(self):
        job_list = self.joblist.get_unscraped_job_ids()
        with self.mongo_client() as client:
            db = client["scrap"]
            collection = db["wanted_job_details"]
            for job in job_list:
                try:
                    job_id = job.get("job_id")
                    if not job.get("in_action"):
                        ic(f"Scraping job_id: {job_id}")
                        data = self._scrape_job_details(job_id)
                        self._insert_job_details(collection, job_id, data)
                        self.joblist.mark_as_scraped(job_id)
                except Exception as e:
                    if "429" in str(e):
                        ic("429 error occurred. Waiting for 10 seconds.")
                        time.sleep(10)
                        continue
                    if "404" in str(e):
                        ic(f"404 error occurred. job_id: {job_id}")
                        self.joblist.mark_as_scraped(job_id)
                        continue
                    if job_id is not None:
                        self.joblist.mark_as_not_in_action(job_id)
                    ic(traceback.format_exc())
                    ic(e)
                    time.sleep(10)
                    continue
                finally:
                    time.sleep(random.randint(1, 3))
