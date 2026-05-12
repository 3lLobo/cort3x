import json
from app.state import CaseState


def build_alerts(state: CaseState, max_alerts: int = 5) -> str:
    alerts = state["alerts"][:max_alerts]

    simplified = [
        {
            "message": a.get("message"),
            "source": a.get("source"),
            "user": a.get("user"),
            "host": a.get("host"),
        }
        for a in alerts
    ]

    return json.dumps(simplified, indent=2)


def build_findings(state: CaseState) -> str:
    if not state["findings"]:
        return "None"
    return "\n".join(f"- {f['summary']}" for f in state["findings"])


def build_context(state: CaseState) -> str:
    return f"""
Alerts:
{build_alerts(state)}

Findings:
{build_findings(state)}

Previous decisions:
{state.get("decisions", [])}
"""