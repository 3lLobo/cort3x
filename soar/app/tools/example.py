class CodeAnalysisTool(Tool):
    name = "code_analysis"
    description = "Analyze scripts or command lines for malicious patterns"

    def is_applicable(self, context: CaseContext) -> bool:
        for alert in context.case.alerts:
            if "script" in str(alert).lower():
                return True
        return False

    def execute(self, context: CaseContext) -> Finding:
        # placeholder logic
        return Finding(
            source=self.name,
            summary="Suspicious PowerShell obfuscation detected",
            data={"confidence": 0.78}
        )