"""
Abstract Action base class.

Used by the Decision stage to score candidate recovery actions (e.g. retry
payment, send payment link, SMS nudge, suggest alternate payment method) via
the expected-value formula, and by the Execution stage to actually run the
chosen one. Concrete actions live in
app/failure_points/payment_failure/actions.py.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ActionResult(BaseModel):
    """Outcome of actually running an Action.

    Deliberately minimal -- each concrete action's execute() body may want a
    richer result per action type.
    """

    success: bool
    detail: str | None = None


class Action(ABC):
    """Base class for one candidate recovery action."""

    @abstractmethod
    def estimate_cost(self, context: dict[str, Any]) -> float:
        """Estimated cost (e.g. SMS/payment-link cost) of running this action.

        Feeds the Decision stage's expected-value formula (see decision.py).
        """
        raise NotImplementedError("TODO: implement cost estimation for this action")

    @abstractmethod
    def estimate_recovery_probability(self, context: dict[str, Any]) -> float:
        """Estimated probability (0-1) this action recovers the payment.

        Feeds the Decision stage's expected-value formula (see decision.py).
        """
        raise NotImplementedError(
            "TODO: implement recovery probability estimation for this action"
        )

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> ActionResult:
        """Actually run this action (e.g. send the SMS/payment link).

        Concrete per-action behavior needs to be implemented here.
        """
        raise NotImplementedError("TODO: implement action execution logic")
