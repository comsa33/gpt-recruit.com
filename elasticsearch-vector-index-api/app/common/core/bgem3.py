import traceback

from FlagEmbedding import BGEM3FlagModel

MODEL_NAME = 'BAAI/bge-m3'


def get_model(model_name: str) -> object:
    """모델을 반환하는 함수

    Args:
        model_name (str): 모델 이름

    Returns:
        object: 모델 객체
    """
    try:
        return BGEM3FlagModel(model_name, use_fp16=True, device="cuda")
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return None
