import json
import pathlib
import unittest
import importlib.util

ROOT = pathlib.Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_contract.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

class ContractTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "config/topic_contract.json").read_text(encoding="utf-8"))

    def test_contract_is_valid(self):
        self.assertEqual([], validator.validate(self.data))

    def test_only_gate_owns_safe_command(self):
        topic = next(x for x in self.data["topics"] if x["name"] == "/ker/motion/joint_command_safe")
        self.assertEqual("motion_safety_gate", topic["publisher"])

    def test_command_trace_fields(self):
        self.assertEqual(
            {"stamp", "source", "sequence", "expires_at", "correlation_id"},
            set(self.data["required_command_fields"]),
        )

if __name__ == "__main__":
    unittest.main()
