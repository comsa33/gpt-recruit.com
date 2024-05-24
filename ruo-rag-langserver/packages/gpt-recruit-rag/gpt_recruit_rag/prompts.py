from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# Used to condense a question and chat history into a single question
condense_question_prompt_template = """Given the following conversation and a follow up instruction, rephrase the follow up instruction to be a standalone question, in its original language. If there is no chat history, just rephrase the question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
"""  # noqa: E501
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
    condense_question_prompt_template
)

# RAG Prompt to provide the context and question for LLM to answer
# We also ask the LLM to cite the source of the passage it is answering from
llm_context_prompt_template = """
Use the following details to answer the user's Instruction.
Each Detail has a SOURCE which is the title of the job opening.

When answering, cite Job Opening of the Details.

If you don't find any proper information given below, just say that you can't find any information, don't try to make up an answer.

And You SHOULD provide the answer in Korean All the time.

----
{context}
----
Instruction: {question}
"""  # noqa: E501

LLM_CONTEXT_PROMPT = ChatPromptTemplate.from_template(llm_context_prompt_template)

# Used to build a context window from passages retrieved
document_prompt_template = """
---
Job Opening: [{name}] {position}
Hiring Company: {name}
Details::
{passage}
---
"""

DOCUMENT_PROMPT = PromptTemplate.from_template(document_prompt_template)
