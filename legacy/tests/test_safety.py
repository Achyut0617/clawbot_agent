import unittest
from app.safety.instruction_gate import check_instruction
from app.safety.validator import validate_plan


class SafetyTests(unittest.TestCase):
    def test_ambiguous_motor_command_is_blocked(self):
        allowed, message = check_instruction("move motor to right")
        self.assertFalse(allowed)
        self.assertIn("clarify", message.lower())

    def test_clear_turn_instruction_passes_gate(self):
        allowed, _ = check_instruction("Turn right for one second.")
        self.assertTrue(allowed)

    def test_unknown_action_is_rejected(self):
        result = validate_plan({
            "actions": [{"action": "launch_rocket", "duration_ms": 100}]
        })
        self.assertFalse(result["ok"])

    def test_movement_duration_limit(self):
        result = validate_plan({
            "actions": [{"action": "turn_right", "duration_ms": 5000}]
        })
        self.assertFalse(result["ok"])

    def test_valid_multistep_plan(self):
        result = validate_plan({"actions": [
            {"action": "move_forward", "duration_ms": 1000},
            {"action": "stop", "duration_ms": 0},
            {"action": "close_claw", "duration_ms": 500}
        ]})
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
