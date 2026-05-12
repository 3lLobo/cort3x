from autogen import AssistantAgent, UserProxyAgent
from app.state import CaseState

def run_autogen_analysis(state: CaseState) -> str:

    analyst = AssistantAgent(
        name="Analyst",
        system_message="Analyze findings factually. No speculation."
    )

    challenger = AssistantAgent(
        name="Challenger",
        system_message="Challenge assumptions and suggest benign explanations."
    )

    controller = UserProxyAgent(name="controller")

    findings = "\n".join([f["summary"] for f in state["findings"]])

    result = controller.initiate_chat(
        analyst,
        message=f"Findings:\n{findings}"
    )

    return result.summary
    