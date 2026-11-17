"""Validate proposed robot actions before any execution."""

ALLOWED_ACTIONS = {
    "move_forward",
    "move_backward",
    "turn_left",
    "turn_right",
    "stop",
    "open_claw",
    "close_claw",
}

MAX_ACTIONS = 10
MAX_DURATION_MS = 3000


def validate_plan(plan):
    """Return a validated plan or a list of validation errors."""
    errors = []

    if not isinstance(plan, dict) or set(plan) != {"actions"}:
        return {"ok": False, "errors": ["Plan must contain only an 'actions' list."]}

    actions = plan["actions"]
    if not isinstance(actions, list) or not actions:
        return {"ok": False, "errors": ["Actions must be a non-empty list."]}

    if len(actions) > MAX_ACTIONS:
        return {"ok": False, "errors": [f"Too many actions; maximum is {MAX_ACTIONS}."]}

    validated = []

    for index, item in enumerate(actions):
        prefix = f"Action {index + 1}"

        if not isinstance(item, dict) or set(item) != {"action", "duration_ms"}:
            errors.append(f"{prefix}: expected only action and duration_ms.")
            continue

        name = item["action"]
        duration = item["duration_ms"]

        if not isinstance(name, str) or name not in ALLOWED_ACTIONS:
            errors.append(f"{prefix}: action is not allowlisted.")
            continue

        if isinstance(duration, bool) or not isinstance(duration, int):
            errors.append(f"{prefix}: duration_ms must be an integer.")
            continue

        if duration < 0 or duration > MAX_DURATION_MS:
            errors.append(f"{prefix}: duration must be between 0 and {MAX_DURATION_MS} ms.")
            continue

        if name in {"move_forward", "move_backward", "turn_left", "turn_right"} and duration == 0:
            errors.append(f"{prefix}: movement duration must be greater than zero.")
            continue

        if name == "stop" and duration != 0:
            errors.append(f"{prefix}: stop must use duration_ms = 0.")
            continue

        validated.append({"action": name, "duration_ms": duration})

    if errors:
        return {"ok": False, "errors": errors}

    return {"ok": True, "errors": [], "actions": validated}


if __name__ == "__main__":
    example = {
        "actions": [
            {"action": "move_forward", "duration_ms": 1000},
            {"action": "stop", "duration_ms": 0},
            {"action": "close_claw", "duration_ms": 500},
        ]
    }
    print(validate_plan(example))
