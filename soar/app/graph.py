from langgraph.graph import StateGraph, END
from app.state import CaseState
from app.decision import decide_next_tool
from app.tools.code_analysis import CodeAnalysisTool
from app.agents.autogen_module import run_autogen_analysis
from app.classification import classify

tools = [CodeAnalysisTool()]


def tool_node(state: CaseState) -> CaseState:
    tool_name = state["next_tool"]

    tool = next((t for t in tools if t.name == tool_name), None)
    if not tool:
        return state

    if tool.is_applicable(state):
        result = tool.run(state)
        state["findings"].append(result)

    return state


def decision_node(state: CaseState) -> CaseState:
    next_tool = decide_next_tool(state, tools)
    state["next_tool"] = next_tool
    return state


def should_continue(state: CaseState):
    if state["next_tool"] is None:
        return "autogen_check"
    return "tool"


def autogen_check_node(state: CaseState) -> CaseState:
    if len(state["findings"]) < 2:
        summary = run_autogen_analysis(state)
        state["findings"].append(
            {"source": "autogen", "summary": summary, "data": {"confidence": 0.6}}
        )
    return state


def classify_node(state: CaseState) -> CaseState:
    state["classification"] = classify(state)
    return state


def build_graph():
    graph = StateGraph(CaseState)

    graph.add_node("decision", decision_node)
    graph.add_node("tool", tool_node)
    graph.add_node("autogen_check", autogen_check_node)
    graph.add_node("classify", classify_node)

    graph.set_entry_point("decision")

    graph.add_conditional_edges(
        "decision", should_continue, {"tool": "tool", "autogen_check": "autogen_check"}
    )

    graph.add_edge("tool", "decision")
    graph.add_edge("autogen_check", "classify")
    graph.add_edge("classify", END)

    return graph.compile()
