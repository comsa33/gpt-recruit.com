from elasticsearch import Elasticsearch
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_community.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel
from dotenv import dotenv_values

from .elastic_index_info import get_indices_infos
from .prompts import DSL_PROMPT

config = dotenv_values("packages/elastic-query-generator/.env")

# Setup Elasticsearch
ES_API_KEY = config["ES_API_KEY"]
ES_URI = config["ES_URI"]

# Create the client instance
db = Elasticsearch(
    ES_URI,
    api_key=ES_API_KEY,
    )

# Specify indices to include
INCLUDE_INDICES = ["wanted_job_detail_index_v2"]

# Setup OpenAI
openai_mode = config["OPENAI_MODE"]
if openai_mode == "azure":
    # Azure Chat OpenAI : Azure Chat OpenAI 모델을 사용하여 구조화된 쿼리 생성
    _model = AzureChatOpenAI(
        azure_deployment=config["AZURE_OPENAI_MODEL"],
        azure_endpoint=config["AZURE_OPENAI_ENDPOINT"],
        api_key=config["AZURE_OPENAI_API_KEY"],
        api_version=config["AZURE_OPENAI_API_VERSION"],
        temperature=0,
    )
elif openai_mode == "openai":
    # Chat OpenAI : Chat OpenAI 모델을 사용하여 구조화된 쿼리 생성
    _model = ChatOpenAI(
        api_key=config["OPENAI_API_KEY"],
        model=config["OPENAI_MODEL"],
        temperature=0,
    )

chain = (
    {
        "input": lambda x: x["input"],
        "indices_info": lambda _: get_indices_infos(
            db,
            sample_documents_in_index_info=3,
            include_indices=INCLUDE_INDICES
        ),
        "top_k": lambda x: x.get("top_k", 5),
    }
    | DSL_PROMPT
    | _model
    | SimpleJsonOutputParser()
)


# Nicely typed inputs for playground
class ChainInputs(BaseModel):
    input: str
    top_k: int = 5


chain = chain.with_types(input_type=ChainInputs)
