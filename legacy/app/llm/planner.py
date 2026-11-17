"""Generate structured robot plans using the local Ollama model."""

import json
import urllib.request

MODEL = "qwen2.5:1.5b"
API_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """
You plan actions for a simulated claw robot.

Return JSON only, with exactly one key: actions.
Each action has exactly two keys: action and duration_ms.

Allowed actions:
move_forward, move_backward, turn_left, turn_right, stop,
open_claw, close_claw

Rules:
- Only include actions explicitly requested by the user.
- Never add an extra movement, turn, or claw action.
- Never infer a multi-step sequence from a vague direction.
- "Turn right" means only turn_right.
- "Turn left" means only turn_left.
- "Move forward" means only move_forward.
- "Move backward" means only move_backward.
- "Open the claw" means only open_claw.
- "Close the claw" means only close_claw.
- If the intended action or target is unclear, return {"actions": []}.
- Do not guess what "move motor to right" means; ask for clarification.
- Maximum 10 actions.
- Every duration_ms must be an integer from 0 to 3000.
- Movement actions require duration_ms greater than 0.
- stop requires duration_ms = 0.
- Output JSON only, without markdown.
- This planner never controls physical hardware.
"""

def generate_plan(user_request):
    payload = {
        "model": MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_request},
        ],
        "options": {"temperature": 0},
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    content = result.get("message", {}).get("content", "")
    plan = json.loads(content)

    if not isinstance(plan, dict):
        raise ValueError("Model did not return a JSON object.")

    return plan


if __name__ == "__main__":
    prompt = input("Enter a Clawbot instruction: ").strip()
    if not prompt:
        raise SystemExit("No instruction provided.")

    try:
        print(json.dumps(generate_plan(prompt), indent=2))
    except Exception as exc:
        raise SystemExit(f"Planning failed safely: {exc}")
