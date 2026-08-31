"""
Abstract Classifier base class.

Used by the Classification stage: turns raw failure context (e.g. a
payment's error_code/error_description) into a ClassificationResult. Concrete
rule-based bucketing plus an Ollama LLM fallback for unmatched strings lives
in app/failure_points/payment_failure/classifier.py.
"""

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel


class ClassificationResult(BaseModel):
    """Result of classifying one payment failure."""

    category: str
    confidence: float
    method: Literal["rule", "llm"]


class Classifier(ABC):
    """Base class for turning failure context into a ClassificationResult."""

    @abstractmethod
    def classify(self, context: dict[str, Any]) -> ClassificationResult:
        """Classify a payment failure.

        The concrete rule taxonomy and LLM fallback behavior needs to be
        implemented here.
        """
        raise NotImplementedError(
            "TODO: implement classification rules and LLM fallback logic"
        )
