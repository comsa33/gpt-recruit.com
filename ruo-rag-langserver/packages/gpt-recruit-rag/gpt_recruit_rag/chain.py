import os
from dotenv import dotenv_values

from operator import itemgetter
from typing import List, Tuple

# from langchain_openai import ChatOpenAI
from langchain_community.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import format_document
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough, RunnableMap
from langchain_elasticsearch import ElasticsearchStore
from langchain_community.embeddings import HuggingFaceHubEmbeddings

from gpt_recruit_rag.prompts import CONDENSE_QUESTION_PROMPT, DOCUMENT_PROMPT, LLM_CONTEXT_PROMPT

config = dotenv_values("packages/gpt-recruit-rag/.env")

os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
# os.environ["OPENAI_API_KEY"] = config["SIONIC_LLAMA3_API_KEY"]

# llm = ChatOpenAI(
#     # base_url=config["RUO_LLM_URI"],
#     # model=config["RUO_LLM_MODEL"],
#     base_url=config["SIONIC_LLAMA3_URI"],
#     model=config["SIONIC_LLAMA3_MODEL"],
#     temperature=0.5
# )

# Setup OpenAI
openai_mode = config["OPENAI_MODE"]
if openai_mode == "azure":
    # Azure Chat OpenAI : Azure Chat OpenAI 모델을 사용하여 구조화된 쿼리 생성
    llm = AzureChatOpenAI(
        azure_deployment=config["AZURE_OPENAI_MODEL"],
        azure_endpoint=config["AZURE_OPENAI_ENDPOINT"],
        api_key=config["AZURE_OPENAI_API_KEY"],
        api_version=config["AZURE_OPENAI_API_VERSION"],
        temperature=0.7,
    )
elif openai_mode == "openai":
    # Chat OpenAI : Chat OpenAI 모델을 사용하여 구조화된 쿼리 생성
    llm = ChatOpenAI(
        api_key=config["OPENAI_API_KEY"],
        model=config["OPENAI_MODEL"],
        temperature=0.7,
    )

embedding = HuggingFaceHubEmbeddings(model=config["EMBEDDING_URI"])

vectorstore = ElasticsearchStore(
    es_url=config["ES_URI"],
    es_api_key=config["ES_API_KEY"],
    index_name="wanted_job_detail_index_v1",
    vector_query_field='embedding',
    # query_field='metadata.intro',
    embedding=embedding
)

retriever = vectorstore.as_retriever(
    search_kwargs={'k': 3},
)


def _combine_documents(
    docs, document_prompt=DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def _format_chat_history(chat_history: List[Tuple]) -> str:
    buffer = ""
    for dialogue_turn in chat_history:
        human = "Human: " + dialogue_turn[0]
        ai = "Assistant: " + dialogue_turn[1]
        buffer += "\n" + "\n".join([human, ai])
    return buffer


_inputs = RunnableMap(
    standalone_question=RunnablePassthrough.assign(
        chat_history=lambda x: _format_chat_history(x["chat_history"])
    )
    | CONDENSE_QUESTION_PROMPT
    | llm
    | StrOutputParser(),
)

_context = {
    "context": itemgetter("standalone_question") | retriever | _combine_documents,
    "question": lambda x: x["standalone_question"],
}


class ChatHistory(BaseModel):
    """Chat history with the bot."""

    chat_history: List[Tuple[str, str]] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "question"}},
    )
    question: str

conversational_qa_chain = (
    _inputs | _context | LLM_CONTEXT_PROMPT | llm | StrOutputParser()
)

chain = conversational_qa_chain.with_types(input_type=ChatHistory)
