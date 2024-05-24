import os
import datetime


def make_dir(path):
    """디렉토리 생성 함수

    Args:
        path (str): 생성할 디렉토리 경로
    """
    if not os.path.exists(path):
        os.makedirs(path)
        msg = f'Directory created: {path}'
        print(msg)
        return msg
    else:
        msg = f'Directory already exists: {path}'
        print(msg)
        return msg


def get_current_datetime():
    """현재 시간을 반환하는 함수

    Returns:
        str: 현재 시간 문자열
    """
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')
