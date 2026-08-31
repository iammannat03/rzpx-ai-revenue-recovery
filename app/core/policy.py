"""
OPA client wrapper.

HTTP plumbing around Open Policy Agent's REST Data API. The actual Rego
policy logic this calls into (policies/recovery_policy.rego -- retry caps,
compliance windows, amount thresholds) lives separately and can evolve
independently of this client.
"""

from dataclasses import dataclass
from typing import Any

import httpx

from app.config import get_settings


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str | None = None


class OPAClient:
    """Thin wrapper around OPA's REST Data API.

    `settings.opa_url` is expected to already point at a specific decision,
    e.g. `http://localhost:8181/v1/data/recovery/allow` (see .env.example),
    matching the `package recovery` policy in policies/recovery_policy.rego.
    """

    def __init__(self, opa_url: str | None = None, timeout: float = 5.0) -> None:
        self._opa_url = opa_url or get_settings().opa_url
        self._timeout = timeout

    def check(self, input_data: dict[str, Any]) -> PolicyDecision:
        """POST {"input": input_data} to OPA and interpret the decision.

        OPA's Data API returns `{"result": <value>}` when the queried rule is
        defined for the given input, and omits "result" entirely when it's
        undefined (Rego's way of saying "no decision"). Both an undefined
        result and a request/transport failure are treated as a deny, since
        a policy gate should fail closed, not open.
        """
        try:
            response = httpx.post(
                self._opa_url, json={"input": input_data}, timeout=self._timeout
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return PolicyDecision(allowed=False, reason=f"OPA request failed: {exc}")

        body = response.json()
        if "result" not in body:
            return PolicyDecision(
                allowed=False, reason="policy decision undefined for this input"
            )

        result = body["result"]
        if isinstance(result, bool):
            return PolicyDecision(allowed=result, reason=None)

        # Some policies may return a richer object, e.g. {"allow": true, "reason": "..."}
        if isinstance(result, dict):
            return PolicyDecision(
                allowed=bool(result.get("allow", False)),
                reason=result.get("reason"),
            )

        return PolicyDecision(
            allowed=False, reason=f"unexpected OPA result shape: {result!r}"
        )
