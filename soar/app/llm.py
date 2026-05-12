from langchain.chat_models import ChatOpenAI

def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )
    