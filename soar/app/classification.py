from langchain_core.prompts import ChatPromptTemplate
from app.llm import get_llm
from app.context import build_alerts, build_findings
from app.parsing import safe_json_parse

llm = get_llm()


CLASSIFICATION_PROMPT = ChatPromptTemplate.from_template("""
You are a SOC analyst performing final classification.

CONTEXT:

Alerts:
{alerts}

Findings:
{findings}

Return STRICT JSON only:
{{
  "summary": "factual description",
  "classification": "True Positive | False Positive | Benign",
  "confidence": 0.0-1.0,
  "reasoning": "short explanation"
}}
""")


def classify(state):
    chain = CLASSIFICATION_PROMPT | llm

    raw = chain.invoke({
        "alerts": build_alerts(state),
        "findings": build_findings(state)
    }).content

    return safe_json_parse(
        raw,
        required_fields=["summary", "classification", "confidence", "reasoning"],
        fallback={
            "summary": "parse failure",
            "classification": "Benign",
            "confidence": 0.0,
            "reasoning": "invalid model output"
        }
    )