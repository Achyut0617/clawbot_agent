"""Text-to-plan-to-simulation pipeline. Simulation only."""

import json
from app.safety.instruction_gate import check_instruction
from app.llm.planner import generate_plan
from app.safety.validator import validate_plan
from app.robot.simulator import simulate_plan


def main():
    prompt = input("Enter a Clawbot instruction: ").strip()

    allowed, message = check_instruction(prompt)
    if not allowed:
        print(f"CLARIFICATION REQUIRED: {message}")
        return

    try:
        plan = generate_plan(prompt)
    except Exception as exc:
        print(f"Planning failed; nothing executed: {exc}")
        return

    print("\nModel proposed:")
    print(json.dumps(plan, indent=2))

    checked = validate_plan(plan)
    if not checked["ok"]:
        print("\nREJECTED by safety validator:")
        for error in checked["errors"]:
            print(f"- {error}")
        return

    print("\nValidated plan — simulation only:")
    print(json.dumps(simulate_plan(plan), indent=2))


if __name__ == "__main__":
    main()
