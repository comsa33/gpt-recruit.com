from patent_rag import chain

if __name__ == "__main__":
    import asyncio


    questions = [
        "2차전지 관련 특허 정보를 알려주세요.",
    ]
    follow_up_question = "2차전지 관련 특허 정보를 알려주세요."


    async def main(question: str, chat_history: list = []) -> str:
        chunks = []
        async for chunk in chain.astream(
            {
                "question": question,
                "chat_history": chat_history,
            }
        ):
            chunks.append(chunk)
            print(chunk, end="", flush=True)

        response = ''.join(chunks)
        return response
    
    response = asyncio.run(main(questions[0]))
    chat_history = [questions[0], response]
    response2 = asyncio.run(main(follow_up_question, chat_history))
