from typing import List, Dict, Any, TypedDict

class Finding(TypedDict):
    source: str
    summary: str
    data: Dict[str, Any]

class CaseState(TypedDict):
    case_id: str
    alerts: List[Dict[str, Any]]
    findings: List[Finding]
    decisions: List[str]
    next_tool: str | None
    classification: Dict[str, Any] | None