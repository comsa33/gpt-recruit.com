import os

import logging
from logging import handlers


def setup_logger(name, log_file, level=logging.DEBUG, backup_count=1):
    """로그 파일을 설정하는 함수
    Args:
        name (str): 로거 이름
        log_file (str): 로그 파일 경로
        level (int): 로그 레벨
        backup_count (int): 백업 파일 개수
    Returns:
        logger (Logger): 로거
    """
    
    # 로그 파일의 디렉토리 경로를 추출
    log_dir = os.path.dirname(log_file)

    # 디렉토리가 없으면 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 로그 포매터 설정
    formatter = logging.Formatter("%(asctime)s,%(filename)s,%(lineno)d,%(message)s")

    # 로그 핸들러 설정
    # 예를 들어, when="midnight", interval=1, backupCount=1로 설정한 경우,
    # 매일 자정에 로그 파일이 새로운 파일로 전환되며, 최대 1개의 이전 로그 파일만 유지됩니다.
    # 즉, 현재 로그 파일과 이전 날짜의 로그 파일 1개만 유지되며, 나머지는 삭제됩니다.
    handler = handlers.TimedRotatingFileHandler(
        filename=log_file,  # 로그 파일 경로
        when="midnight",    # 매일 자정
        interval=1,         # 1일 간격
        backupCount=backup_count,   # 로그 파일 보관 개수
        encoding="utf-8",   # 인코딩
    )
    handler.setFormatter(formatter)
    handler.suffix = "%Y%m%d"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
