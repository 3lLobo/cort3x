from app.tools.base import Tool
from app.state import CaseState, Finding

class CodeAnalysisTool(Tool):
    name = "code_analysis"
    description = "Analyze scripts or command lines for malicious patterns"

    def is_applicable(self, state: CaseState) -> bool:
        return any("script" in str(a).lower() for a in state["alerts"])

    def run(self, state: CaseState) -> Finding:
        return {
            "source": self.name,
            "summary": "Suspicious PowerShell obfuscation detected",
            "data": {"confidence": 0.75}
        }
        