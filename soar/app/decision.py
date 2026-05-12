from langchain_core.prompts import ChatPromptTemplate
from app.llm import get_llm
from app.context import build_context
from app.parsing import safe_json_parse

llm = get_llm()


def build_tools(tools: list) -> str:
    return "\n".join(f"{t.name}: {t.description}" for t in tools)


DECISION_PROMPT = ChatPromptTemplate.from_template("""
You are a SOC analyst selecting the next investigation tool.

TOOLS:
{tools}

CONTEXT:
{context}

Return STRICT JSON only:
{{
  "tool": "tool_name | NONE",
  "reason": "short explanation"
}}
""")


def decide_next_tool(state, tools):
    chain = DECISION_PROMPT | llm

    raw = chain.invoke({
        "tools": build_tools(tools),
        "context": build_context(state)
    }).content

    result = safe_json_parse(
        raw,
        required_fields=["tool", "reason"],
        fallback={"tool": "NONE", "reason": "parse failure"}
    )

    state.setdefault("decisions", []).append(result)

    return None if result["tool"] == "NONE" else result["tool"]