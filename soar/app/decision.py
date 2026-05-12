from langchain.prompts import ChatPromptTemplate
from app.state import CaseState
from app.llm import get_llm

llm = get_llm()

def decide_next_tool(state: CaseState, tools: list) -> str | None:
    tool_desc = "\n".join([f"{t.name}: {t.description}" for t in tools])
    findings = "\n".join([f["summary"] for f in state["findings"]])

    prompt = ChatPromptTemplate.from_template("""
You are a SOC analyst.

Available tools:
{tools}

Current findings:
{findings}

Return ONLY one tool name or NONE.
""")

    chain = prompt | llm
    result = chain.invoke({
        "tools": tool_desc,
        "findings": findings
    }).content.strip()

    return None if result == "NONE" else result
    