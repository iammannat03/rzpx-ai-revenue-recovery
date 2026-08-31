"""
Event base class + event registry.

Every pipeline stage (Classifier, Decision, Policy Gate, Execution, Outcome
Tracker) communicates purely through named events -- an event-chaining
pipeline, not a synchronous agentic loop. An Event's fields mirror
`EventLog` in app/db/models.py: every event that gets emitted is also
durably written there as the audit trail, so this base class intentionally
carries the same minimum fields.

This is mechanical/infra glue (a base dataclass + a name -> class registry),
not business logic. Concrete event subclasses live in
app/failure_points/payment_failure/events.py.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_EVENT_REGISTRY: dict[str, type["Event"]] = {}


def register_event(cls: type["Event"]) -> type["Event"]:
    """Class decorator: registers a concrete Event subclass under its `event_type`.

    Usage:
        @register_event
        @dataclass
        class PaymentFailedEvent(Event):
            event_type: str = "payment.failed"

    The subclass MUST be re-decorated with @dataclass (below @register_event,
    so it runs first) -- Event's own @dataclass only bakes ITS field defaults
    into Event.__init__; a plain (non-dataclass) subclass would inherit that
    __init__ unchanged and silently ignore its own `event_type` default.
    """
    # `dataclasses.is_dataclass(cls)` is not enough here: it's True for ANY
    # subclass of a dataclass (inherited), even one never itself decorated.
    # `__dataclass_fields__` must be set directly on this class -- i.e. in
    # its own __dict__, not just reachable through inheritance -- to prove
    # @dataclass actually re-ran on it and rebuilt __init__ with its defaults.
    if "__dataclass_fields__" not in cls.__dict__:
        raise TypeError(
            f"{cls.__name__} must be decorated with @dataclass (applied below "
            "@register_event) so its own field defaults, like event_type, "
            "actually take effect -- see register_event's docstring"
        )
    event_type = cls.event_type
    if not event_type:
        raise ValueError(
            f"{cls.__name__} must set a non-empty `event_type` class default "
            "before using @register_event"
        )
    existing = _EVENT_REGISTRY.get(event_type)
    if existing is not None and existing is not cls:
        raise ValueError(
            f"event_type '{event_type}' is already registered to {existing!r}"
        )
    _EVENT_REGISTRY[event_type] = cls
    return cls


def get_event_class(event_type: str) -> type["Event"]:
    """Look up a registered Event subclass by its `event_type` string."""
    try:
        return _EVENT_REGISTRY[event_type]
    except KeyError:
        raise KeyError(f"no Event class registered for event_type '{event_type}'") from None


@dataclass
class Event:
    """Base class for every event in the pipeline.

    Fields mirror app.db.models.EventLog: `correlation_id` is the Razorpay
    payment_id tying every event for one payment together across stages;
    `payload` is the event-specific data; `id`/`created_at` are audit
    metadata. Concrete subclasses should override the `event_type` default
    and register themselves with `@register_event`.
    """

    correlation_id: str
    payload: dict[str, Any]
    event_type: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
