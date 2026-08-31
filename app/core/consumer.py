"""
Abstract Consumer base class.

Every pipeline stage (Classifier, Decision, Policy Gate, Execution, Outcome
Tracker) is an independent, stateless Celery consumer that reacts to one
Event and, if it does its job, chains to the next Event -- an
event-chaining pipeline. A Consumer never holds cross-step memory: whatever
state it needs comes from the Event's payload and Postgres, not from any
in-process state.
"""

from abc import ABC, abstractmethod

from app.core.events import Event


class Consumer(ABC):
    """Base class for a single pipeline stage's event handler."""

    @abstractmethod
    def handle(self, event: Event) -> None:
        """Process one Event.

        Concrete stage logic -- what this actually does with the event (e.g.
        classification rules, expected-value scoring, policy checks) --
        needs to be implemented per stage.
        """
        raise NotImplementedError("TODO: implement stage-specific event handling")
