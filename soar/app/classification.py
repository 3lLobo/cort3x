from langchain.prompts import ChatPromptTemplate
from app.llm import get_llm
from app.state import CaseState

llm = get_llm()

def classify(state: CaseState) -> dict:
    findings = "\n".join([f["summary"] for f in state["findings"]])

    prompt = ChatPromptTemplate.from_template("""
Classify the case.

Findings:
{findings}

Return JSON:
{{
  "classification": "True Positive | False Positive | Benign",
  "confidence": float,
  "reasoning": "short explanation"
}}
""")

    chain = prompt | llm
    return chain.invoke({"findings": findings}).content
    