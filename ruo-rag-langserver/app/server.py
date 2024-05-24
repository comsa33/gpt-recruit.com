from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from gpt_recruit_rag import chain as gpt_recruit_rag_chain
from patent_rag import chain as patent_rag_chain
from elastic_query_generator import chain as elastic_query_generator_chain

app = FastAPI(
    title="Langchain Server",
    version="0.1.0",
    description="A server to run langchain chains",
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
add_routes(app, gpt_recruit_rag_chain, path="/gpt-recruit-rag", enable_feedback_endpoint=True)
add_routes(app, patent_rag_chain, path="/patent-rag")
add_routes(app, elastic_query_generator_chain, path="/elastic-query-generator")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
