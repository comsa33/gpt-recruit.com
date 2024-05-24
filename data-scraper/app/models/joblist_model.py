from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Boolean, DateTime, BigInteger

Base = declarative_base()

class WantedJobList(Base):
    __tablename__ = 'wanted_job_list'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(Integer, unique=True)
    in_action = Column(Boolean, default=False)
    is_scraped = Column(Boolean, default=False)
    scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
