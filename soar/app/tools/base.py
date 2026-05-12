from abc import ABC, abstractmethod
from app.state import CaseState, Finding

class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def is_applicable(self, state: CaseState) -> bool:
        pass

    @abstractmethod
    def run(self, state: CaseState) -> Finding:
        pass
        