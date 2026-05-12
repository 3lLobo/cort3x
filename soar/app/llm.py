from langchain_openai import ChatOpenAI
import os


def get_llm():
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        base_url=os.getenv("LLM_BASE_URL"),  # your endpoint
        api_key=os.getenv("LLM_API_KEY"),
        temperature=0.7,
    )
