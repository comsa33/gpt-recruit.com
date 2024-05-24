import time
import traceback
from contextlib import contextmanager

import requests
from icecream import ic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import insert

from app.models.joblist_model import WantedJobList
from app.config.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


class JobList:
    def __init__(self) -> None:
        self._mysql_url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        self._scrap_url = "https://www.wanted.co.kr/api/chaos/navigation/v1/results"
        self.engine = create_engine(self._mysql_url)

    @contextmanager
    def session_scope(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_unscraped_job_ids(self) -> list:
        with self.session_scope() as session:
            job_list = session.query(WantedJobList).filter(WantedJobList.is_scraped == False).all()
            return [job.as_dict() for job in job_list]

    def mark_as_scraped(self, job_id: int) -> bool:
        with self.session_scope() as session:
            job = session.query(WantedJobList).filter(WantedJobList.job_id == job_id).first()
            job.is_scraped = True
            session.commit()
            return True

    def mark_as_in_action(self, job_id: int) -> bool:
        with self.session_scope() as session:
            job = session.query(WantedJobList).filter(WantedJobList.job_id == job_id).first()
            job.in_action = True
            session.commit()
            return True

    def mark_as_not_in_action(self, job_id: int) -> bool:
        with self.session_scope() as session:
            job = session.query(WantedJobList).filter(WantedJobList.job_id == job_id).first()
            job.in_action = False
            session.commit()
            return True

    def _scrape_job_ids(self, params: dict) -> list:
        response = requests.get(self._scrap_url, params=params)
        response.raise_for_status()
        data = response.json()
        id_list = [job["id"] for job in data["data"]]
        return id_list

    def _insert_job_ids(self, job_ids: list) -> bool:
        with self.session_scope() as session:
            insert_stmt = insert(WantedJobList).values([{"job_id": job_id} for job_id in job_ids])
            do_nothing_stmt = insert_stmt.on_duplicate_key_update(job_id=insert_stmt.inserted.job_id)
            result = session.execute(do_nothing_stmt)
            session.commit()
            return result.rowcount

    def scrape_and_insert(self):
        params = {
            "years": -1,
            "locations": "all",
            "country": "kr",
            "job_sort": "job.latest_order",
            "limit": 100,
            "offset": 0,
        }
        for i in range(99):
            params["offset"] = i * 100
            try:
                job_ids = self._scrape_job_ids(params)
                rowcount = self._insert_job_ids(job_ids)
                ic(f"[{i+1}/100] Inserted {rowcount} rows out of {len(job_ids)}")
            except requests.RequestException as e:
                ic(e)
                ic(traceback.format_exc())
            except Exception as e:
                ic(e)
                ic(traceback.format_exc())
            time.sleep(1)

if __name__ == "__main__":
    joblist = JobList()
    result = joblist.get_unscraped_job_ids()
    ic(result[:5])
