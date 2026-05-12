from autogen import AssistantAgent, UserProxyAgent
from app.state import CaseState
from app.context import build_context
import os


llm_config = {
    "config_list": [
        {
            "model": os.getenv("LLM_MODEL"),
            "base_url": os.getenv("LLM_BASE_URL"),
            "api_key": os.getenv("LLM_API_KEY"),
        }
    ],
    "temperature": 0.7,
}

AssistantAgent(
    name="Analyst", llm_config=llm_config, system_message="Analyze findings factually."
)


def run_autogen_analysis(state: CaseState) -> str:

    analyst = AssistantAgent(
        name="Analyst", system_message="Analyze findings factually. No speculation."
    )

    challenger = AssistantAgent(
        name="Challenger",
        system_message="Challenge assumptions and suggest benign explanations.",
    )

    controller = UserProxyAgent(name="controller")

    context = build_context(state)

    result = controller.initiate_chat(analyst, message=f"Context:\n{context}")

    return result.summary
