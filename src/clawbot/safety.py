from dataclasses import dataclass


@dataclass
class SafetyDecision:
    allowed: bool
    requires_approval: bool
    reason: str


def inspect_request(text: str, require_approval: bool = True) -> SafetyDecision:
    cleaned = text.strip()
    if not cleaned:
        return SafetyDecision(False, False, "Empty command.")
    if len(cleaned) > 4000:
        return SafetyDecision(False, False, "Command exceeds the configured length limit.")
    # This is a policy boundary, not a complete security sandbox. OpenClaw tool
    # permissions must also be configured restrictively.
    return SafetyDecision(True, require_approval, "Accepted for orchestration; review consequential actions.")
