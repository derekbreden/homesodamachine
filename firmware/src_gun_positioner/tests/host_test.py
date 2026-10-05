import math
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
import kinematics as k
import visual_servo as s
import positioner as p

class HostTests(unittest.TestCase):
    def test_host_firmware_bounds_agree(self):
        source = Path(__file__).resolve().parents[1]
        header = (source / "geometry_generated.h").read_text()
        for name, expected in (("kMinCount", k.SOFT_MIN), ("kMaxCount", k.SOFT_MAX)):
            actual = re.search(rf"{name}\s*=\s*\{{([^}}]+)\}}", header)
            self.assertIsNotNone(actual)
            self.assertEqual([int(v.strip()) for v in actual[1].split(",")], expected)
        policy = (source / "motion_policy.h").read_text()
        for cpp, host in (("kMaxJogCounts", p.MAX_JOG_COUNTS),
                          ("kMinDurationUs", p.MIN_DURATION_US),
                          ("kMaxDurationUs", p.MAX_DURATION_US),
                          ("kMaxAcceleration", p.MAX_ACCELERATION)):
            actual = re.search(rf"constexpr\s+\w+\s+{cpp}\s*=\s*(\d+)", policy)
            self.assertIsNotNone(actual)
            self.assertEqual(int(actual[1]), host)

    def test_clevis_inverse_and_soft_quantization(self):
        self.assertAlmostEqual(k.actuator_length(0), k.NEUTRAL_LENGTH_MM)
        for degrees in (-20, -10, -0.01, 0, 0.01, 10, 20):
            self.assertAlmostEqual(k.actuator_angle(k.actuator_length(degrees)), degrees, places=9)
        self.assertEqual(k.pose_to_counts([0] * 6), [0] * 6)
        self.assertEqual(k.mm_to_count(0.0025), 16)
        with self.assertRaises(ValueError):
            k.pose_to_counts([101, 0, 0, 0, 0, 0])
        # Endpoints clamp inward by a fractional count rather than cross the soft limit.
        self.assertEqual(k.pose_to_counts([0, 0, 0, k.ANGULAR_SOFT[0][0], k.ANGULAR_SOFT[1][1], 0])[3:5],
                         [k.SOFT_MIN[3], k.SOFT_MAX[4]])
        for axis, (lo, hi) in enumerate(k.ANGULAR_SOFT):
            pose = [0] * 6; pose[axis+3] = hi + 0.001
            with self.assertRaises(ValueError): k.pose_to_counts(pose)

    def test_dot_compensation(self):
        vector = [100, 20, -5]
        current = [3, 4, 5, 0, 0, 0]
        angles = [0.1, -0.2, 0.05]
        target = k.dot_rotation(current, angles, vector)
        a = k.rotation(105, 60, 0)
        b = k.rotation(105.1, 59.8, 0.05)
        before = [current[i] + sum(a[i][j] * vector[j] for j in range(3)) for i in range(3)]
        after = [target[i] + sum(b[i][j] * vector[j] for j in range(3)) for i in range(3)]
        for x, y in zip(before, after):
            self.assertAlmostEqual(x, y, places=10)

    def test_segment_counts_exact(self):
        start = [0] * 6
        target = [999, -1972, 16, -7, 63, -640]
        rows = list(k.split_target(start, target))
        self.assertTrue(all(max(map(abs, row)) <= 640 for row in rows))
        self.assertEqual([sum(row[i] for row in rows) for i in range(6)], target)

    def test_identification_and_bounded_correction(self):
        response = [[(1 if i == j else 0) + 0.1 * ((i + j) % 2) for j in range(6)] for i in range(6)]
        trials = []
        for axis in range(6):
            for sign in (-1, 1):
                delta = [0] * 6; delta[axis] = sign * 0.005
                feature = [sum(row[i] * delta[i] for i in range(6)) for row in response]
                trials.append(dict(delta_mm=delta, delta_feature=feature))
        fitted = s.fit_jacobian(trials)
        for actual, expected in zip(fitted, response):
            for a, b in zip(actual, expected):
                self.assertAlmostEqual(a, b, places=9)
        delta = s.correction(fitted, [1, -1, 2, 0, 1, -2], trust_mm=0.01)
        self.assertLessEqual(max(map(abs, delta)), 0.0100000001)
        with self.assertRaises(ValueError):
            s.correction([[1] * 6] * 6, [1] * 6)
        with self.assertRaises(ValueError):
            s.fit_jacobian([trials[0]] * 6)

if __name__ == "__main__":
    unittest.main()
