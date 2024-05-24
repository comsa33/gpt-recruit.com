import time
import ast
import traceback
from typing import Generator, Any

import requests
import streamlit as st
from dotenv import dotenv_values
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

config = dotenv_values(".env")
uri = config["GPT_RECURIT_LLM_URI"]

def stream_response_generator(query: str, chat_history: list) -> Generator[str, Any, None]:
    """
    GPT RECURIT LLM API로부터 스트리밍 응답을 생성하는 제너레이터 함수

    Args:
        query (str): 질문
        chat_history (list): 대화 기록

    Yields:
        str: 응답 메시지
    """
    data = {
        "input": {
            "question": query,
            "chat_history": chat_history
        }
    }
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        with session.post(uri, json=data, stream=True, timeout=10) as response:
            if response.status_code == 200:
                current_event_type = None
                for chunk in response.iter_lines():
                    if chunk:
                        decoded_chunk = chunk.decode('utf-8').strip()
                        if decoded_chunk.startswith("event:"):
                            current_event_type = decoded_chunk.split(": ")[1]
                        elif decoded_chunk.startswith("data:") and current_event_type == "data":
                            message_content = decoded_chunk.split("data: ")[1]
                            yield ast.literal_eval(message_content)
                            time.sleep(0.02)
            else:
                print(f"서버 응답 오류: {response.status_code}")
                yield "서버 응답에 오류가 발생했습니다. 다시 시도하거나, 페이지를 새로고침해주세요."
    except requests.exceptions.RequestException as e:
        print(f"서버 요청 실패: {str(e)}\n{traceback.format_exc()}")
        yield "서버 요청에 실패했습니다. 다시 시도하거나, 페이지를 새로고침해주세요."
