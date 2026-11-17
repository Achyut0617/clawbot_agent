# Clawbot Agent — Robot Execution Modules

These modules implement the JSON-to-command and command-orchestration layer.

## Included modules

- `command_models.py`: immutable typed command objects.
- `action_compiler.py`: validates JSON and compiles allowlisted actions.
- `command_executor.py`: dispatches commands to an abstract robot interface.
- `execution_manager.py`: sequences commands, handles cancellation and failures.
- `state_manager.py`: thread-safe high-level state.
- `feedback_manager.py`: execution event history and summaries.

## Expected JSON format

```json
{
  "task_id": "task_001",
  "robot": "mobile_robot",
  "actions": [
    {"action": "move", "direction": "forward", "duration": 1.0},
    {"action": "turn", "direction": "left", "duration": 0.5},
    {"action": "stop"}
  ]
}
```

Supported actions: `move`, `turn`, `stop`, `wait`, `speak`.

The compiler currently applies conservative duration limits:
- move: 0.1–2.0 seconds
- turn: 0.1–2.0 seconds
- wait: 0–30 seconds
- at most 20 actions per plan

These are software policy limits, not guarantees of physical distance or safe
motion. Tune them only after testing the robot in a controlled environment.

## Integration example

```python
import json

from app.robot import (
    ActionCompiler, CommandExecutor, ExecutionManager,
    StateManager, FeedbackManager,
)

class DemoRobot:
    """Safe console-only stand-in. It does not control physical hardware."""
    def move(self, direction, duration, cancel_event=None):
        print(f"[SIM] move {direction} for {duration}s")

    def turn(self, direction, duration, cancel_event=None):
        print(f"[SIM] turn {direction} for {duration}s")

    def stop(self, reason="requested"):
        print(f"[SIM] stop: {reason}")

    def speak(self, text):
        print(f"[SIM] speak: {text}")

    def emergency_stop(self):
        print("[SIM] emergency stop")


plan = {
    "task_id": "demo_001",
    "robot": "mobile_robot",
    "actions": [
        {"action": "move", "direction": "forward", "duration": 1.0},
        {"action": "stop"}
    ]
}

compiler = ActionCompiler()
commands = compiler.compile(plan)

robot = DemoRobot()
executor = CommandExecutor(robot)
state = StateManager()
feedback = FeedbackManager()
manager = ExecutionManager(executor, state, feedback)

result = manager.execute_plan(commands, task_id=plan["task_id"])
print(result)
print(state.snapshot())
print(feedback.history())
```

Run this from the repository root:

```bash
python -m your_entry_module
```

Use the example as a starting point inside your existing application entry point.

## Important integration notes

1. Confirm your current JSON schema and adapt the compiler's field names if needed.
2. Keep the simulator and physical robot behind the same `RobotInterface`.
3. Implement physical communication in a separate hardware adapter; do not put
   GPIO/PWM or motor-driver code in these modules.
4. The physical controller must independently enforce its own watchdog,
   command validation and emergency-stop behavior. A Python exception handler
   is not a physical emergency-stop system.
5. This starter implementation runs synchronously. If your voice/UI loop must
   remain responsive during execution, run the execution manager in a worker
   thread or move to an async architecture.
