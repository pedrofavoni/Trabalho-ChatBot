from abc import ABC, abstractmethod


class ILLMFallback(ABC):

    @abstractmethod
    def answer(self, question: str, context: str) -> str:
        """Responde uma pergunta que a base de conhecimento não conseguiu tratar."""
        pass

    @abstractmethod
    def refine(self, question: str, raw_response: str, context: str = "") -> str:
        """Melhora o estilo de uma resposta já gerada pela base."""
        pass
