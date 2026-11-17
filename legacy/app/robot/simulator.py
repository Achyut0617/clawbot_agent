"""Simulation-only executor. Never sends commands to physical hardware."""

import json
from app.safety.validator import validate_plan


def simulate_plan(plan):
    result = validate_plan(plan)

    if not result["ok"]:
        return {
            "status": "rejected",
            "errors": result["errors"],
            "executed": [],
        }

    executed = []
    for index, action in enumerate(result["actions"], start=1):
        event = {
            "step": index,
            "action": action["action"],
            "duration_ms": action["duration_ms"],
            "mode": "simulation",
        }
        executed.append(event)
        print(f"SIMULATION step {index}: {action['action']} "
              f"({action['duration_ms']} ms)")

    return {"status": "simulated", "executed": executed}


if __name__ == "__main__":
    demo = {
        "actions": [
            {"action": "move_forward", "duration_ms": 1000},
            {"action": "stop", "duration_ms": 0},
            {"action": "close_claw", "duration_ms": 500},
        ]
    }

    output = simulate_plan(demo)
    print("\nResult:")
    print(json.dumps(output, indent=2))
