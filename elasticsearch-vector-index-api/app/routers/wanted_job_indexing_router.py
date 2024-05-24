import traceback

from fastapi import APIRouter

from app.config.settings import FILE_PATHS
from app.common.log.log_config import setup_logger
from app.common.core.utils import get_current_datetime, make_dir



router = APIRouter()

file_path = FILE_PATHS["log"] + 'api'
make_dir(file_path)
file_path += f'/wanted_job_indexing_{get_current_datetime()}.log'
logger = setup_logger('wanted_job_indexing', file_path)
