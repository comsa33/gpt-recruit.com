import os
from dotenv import dotenv_values

from operator import itemgetter
from typing import List, Optional, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import format_document
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_elasticsearch import ElasticsearchStore
from langchain_community.embeddings import HuggingFaceHubEmbeddings

from patent_rag.prompts import CONDENSE_QUESTION_PROMPT, DOCUMENT_PROMPT, LLM_CONTEXT_PROMPT

config = dotenv_values("packages/patent-rag/.env")

# os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
os.environ["OPENAI_API_KEY"] = config["SIONIC_LLAMA3_API_KEY"]

llm = ChatOpenAI(
    # base_url=config["RUO_LLM_URI"],
    # model=config["RUO_LLM_MODEL"],
    base_url=config["SIONIC_LLAMA3_URI"],
    model=config["SIONIC_LLAMA3_MODEL"],
    temperature=0.1
)

embedding = HuggingFaceHubEmbeddings(model=config["EMBEDDING_URI"])

vectorstore = ElasticsearchStore(
    es_url=config["ES_URI"],
    es_api_key=config["ES_API_KEY"],
    index_name="patent_vector_index_v1",
    vector_query_field='embedding',
    embedding=embedding
)

retriever = vectorstore.as_retriever()


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


class ChainInput(BaseModel):
    chat_history: Optional[List[BaseMessage]] = Field(
        description="Previous chat messages."
    )
    question: str = Field(..., description="The question to answer.")


_inputs = RunnableParallel(
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

chain = _inputs | _context | LLM_CONTEXT_PROMPT | llm | StrOutputParser()

chain = chain.with_types(input_type=ChainInput)
