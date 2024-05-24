from gpt_recruit_rag import chain

if __name__ == "__main__":
    import asyncio


    questions = [
        "파이썬 (python) 개발자 채용 정보를 알려주세요.",
        "오케스트로 회사의 채용 정보를 알려주세요.",
        "데이터 엔지니어 채용 회사는 어디인가요?",
        "IT 관련 채용 회사는 어디인가요?",
        "디자인 관련 채용 회사는 어디인가요?",
        "마케팅 관련 채용 회사는 어디인가요?",
        "데이터 관련 채용 회사는 어디인가요?",
    ]
    follow_up_question = "파이썬 개발자를 채용하는 회사의 채용공고를 확인하고, 그 중 한 곳 회사의 적합한 한국식 자기소개서를 작성해주세요."


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
