import unittest
from app.safety.validator import validate_plan


class ValidatorTests(unittest.TestCase):
    def test_valid_multistep_plan(self):
        plan = {"actions": [
            {"action": "move_forward", "duration_ms": 1000},
            {"action": "stop", "duration_ms": 0},
            {"action": "close_claw", "duration_ms": 500},
        ]}
        self.assertTrue(validate_plan(plan)["ok"])

    def test_reject_unknown_action(self):
        result = validate_plan({"actions": [
            {"action": "launch_rocket", "duration_ms": 100}
        ]})
        self.assertFalse(result["ok"])

    def test_reject_excessive_duration(self):
        result = validate_plan({"actions": [
            {"action": "move_forward", "duration_ms": 999999}
        ]})
        self.assertFalse(result["ok"])

    def test_reject_empty_plan(self):
        self.assertFalse(validate_plan({"actions": []})["ok"])

    def test_reject_extra_fields(self):
        result = validate_plan({"actions": [
            {"action": "move_forward", "duration_ms": 1000, "speed": 999}
        ]})
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
