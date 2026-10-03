import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from ker_ros2_bridge.contracts import JointCommand
from ker_ros2_bridge.safety_gate import ACTIVE, SafetyGate

def cmd(sequence=1, position=0.2, expires=11.0):
    return JointCommand(
        stamp=9.9,
        source="expression_planner",
        sequence=sequence,
        expires_at=expires,
        correlation_id=f"c-{sequence}",
        positions={"neck_yaw": position},
    )

class GateTest(unittest.TestCase):
    def setUp(self):
        self.gate = SafetyGate({"neck_yaw": (-1.0, 1.0)})

    def test_safe_stop_rejects(self):
        self.assertFalse(self.gate.evaluate(cmd(), 10.0).accepted)

    def test_active_accepts_valid_command(self):
        self.gate.set_state(ACTIVE)
        self.assertTrue(self.gate.evaluate(cmd(), 10.0).accepted)

    def test_limit_rejects(self):
        self.gate.set_state(ACTIVE)
        self.assertEqual("limit:neck_yaw", self.gate.evaluate(cmd(position=1.1), 10.0).reason)

    def test_expired_rejects(self):
        self.gate.set_state(ACTIVE)
        self.assertEqual("stale_or_future_command", self.gate.evaluate(cmd(expires=9.9), 10.0).reason)

    def test_duplicate_rejects(self):
        self.gate.set_state(ACTIVE)
        self.assertTrue(self.gate.evaluate(cmd(sequence=2), 10.0).accepted)
        self.assertEqual("duplicate_or_out_of_order", self.gate.evaluate(cmd(sequence=2), 10.0).reason)

if __name__ == "__main__":
    unittest.main()
