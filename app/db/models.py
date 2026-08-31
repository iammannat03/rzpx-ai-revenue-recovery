import uuid
from datetime import datetime

from sqlalchemy import String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventLog(Base):
    """Append-only log of every event in the pipeline. This IS the audit trail."""

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    correlation_id: Mapped[str] = mapped_column(
        String, index=True
    )  # razorpay payment_id
    event_type: Mapped[str] = mapped_column(
        String, index=True
    )  # e.g. "payment.classified"
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Payment(Base):
    """Current-state snapshot per payment."""

    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(
        String, primary_key=True
    )  # razorpay payment_id
    order_id: Mapped[str | None] = mapped_column(String, nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(
        String
    )  # failed, recovering, recovered, exhausted
    failure_category: Mapped[str | None] = mapped_column(String, nullable=True)
    last_action: Mapped[str | None] = mapped_column(String, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)
    is_control_group: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Action(Base):
    """One row per proposed/executed action."""

    __tablename__ = "actions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    payment_id: Mapped[str] = mapped_column(
        String, ForeignKey("payments.payment_id"), index=True
    )
    action_type: Mapped[str] = mapped_column(String)  # e.g. "send_payment_link"
    expected_value: Mapped[float] = mapped_column(Float)
    cost: Mapped[float] = mapped_column(Float)
    policy_decision: Mapped[str] = mapped_column(String)  # "approved" | "rejected"
    policy_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Outcome(Base):
    """Recovery results, with attribution."""

    __tablename__ = "outcomes"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    payment_id: Mapped[str] = mapped_column(
        String, ForeignKey("payments.payment_id"), index=True
    )
    recovered: Mapped[bool] = mapped_column(Boolean)
    recovered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    attributed: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # recovered BECAUSE of our action vs would've paid anyway
