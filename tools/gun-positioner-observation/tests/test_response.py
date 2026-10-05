"""Response fitting on a simulated mechanism with backlash, direction gains, coupling, drift, noise, outliers."""

import unittest

import numpy as np

from support import groups_and_purposes, simulated_dataset

from gpobs import response, validation
from gpobs.controls import COUNTS_PER_MM, host_modules
from gpobs.dataset import SessionReader
from gpobs.response import StepData, History, Step, axis_takeup, takeup_motion


class Takeup(unittest.TestCase):
    def test_play_bookkeeping(self):
        moves = np.array([300, 40, -40, -40, -40, -40, 40, 40, 40], dtype=float)
        unknown = np.zeros(len(moves), dtype=bool)
        unknown[0] = True
        eff, known = axis_takeup(moves, 100.0, unknown, 250.0)
        self.assertFalse(known[0])
        self.assertTrue(np.all(known[1:]))
        np.testing.assert_allclose(eff[1:], [40, 0, 0, -20, -40, 0, 0, 20])

    def test_unknown_until_engaged_after_fault(self):
        moves = np.array([[200, 0, 0, 0, 0, 0], [200, 0, 0, 0, 0, 0], [-50, 0, 0, 0, 0, 0], [100, 0, 0, 0, 0, 0]])
        unknown = np.zeros_like(moves, dtype=bool)
        unknown[0] = True
        unknown[2, 0] = True         # e.g. a fault before the third move
        eff, known = takeup_motion(moves, np.full(6, 60.0), unknown, np.full(6, 150.0))
        self.assertEqual(known[:, 0].tolist(), [False, True, False, False])


class Recovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path, cls.truth = simulated_dataset(seed=7, outlier_prob=0.03)
        cls.reader = SessionReader(path)
        cls.data = response.assemble([cls.reader])
        groups, purposes = groups_and_purposes(cls.reader)
        probes = [t for t in cls.data.trials() if purposes[t] == "probe"]
        cls.train, cls.hold = validation.split_trials(probes, 0.34, seed=1, groups=groups)
        cls.train += [t for t in cls.data.trials() if purposes[t] != "probe"]
        cls.model = response.fit(cls.data, cls.train)

    def test_jacobians_recovered(self):
        t, m = self.truth, self.model
        self.assertLess(np.linalg.norm(m.j_plus - t.j_plus) / np.linalg.norm(t.j_plus), 0.01)
        self.assertLess(np.linalg.norm(m.j_minus - t.j_minus) / np.linalg.norm(t.j_minus), 0.01)
        # Directions differ by up to 30 % in the truth; the fit resolves that difference.
        diff_true = t.j_plus - t.j_minus
        diff_fit = m.j_plus - m.j_minus
        self.assertLess(np.linalg.norm(diff_fit - diff_true) / np.linalg.norm(diff_true), 0.05)
        # Standard errors are honest: the truth lies within ~4 SE nearly everywhere.
        z = np.abs(m.j_plus - t.j_plus) / m.j_plus_se
        self.assertGreater(np.mean(z < 4), 0.95)

    def test_deadband_recovered(self):
        np.testing.assert_allclose(self.model.deadband, self.truth.backlash, atol=3.0)
        self.assertTrue(np.all(self.model.deadband_identified))

    def test_outliers_rejected(self):
        self.assertGreater(len(self.model.outliers), 0)
        self.assertLess(len(self.model.outliers), 0.15 * self.model.n_rows)

    def test_model_roundtrip(self):
        again = response.ResponseModel.from_dict(__import__("json").loads(self.model.to_json()))
        self.assertEqual(again.model_id, self.model.model_id)
        np.testing.assert_allclose(again.j_minus, self.model.j_minus)
        tampered = __import__("json").loads(self.model.to_json())
        tampered["deadband"][0] += 1
        with self.assertRaises(ValueError):
            response.ResponseModel.from_dict(tampered)

    def test_units_match_controls_visual_servo(self):
        """On clean one-direction data, our J⁺ per mm equals visual_servo.fit_jacobian's."""
        rng = np.random.default_rng(9)
        j = 0.08 * rng.normal(size=(8, 6))
        moves = [rng.integers(1, 200, size=6) * (np.arange(6) == k) for k in range(6) for _ in range(4)]
        moves = [np.array([300] * 6)] + moves               # engagement run
        hist = History("s", [f"m{i}" for i in range(len(moves))], np.array(moves, float),
                       np.vstack([np.ones(6, bool), np.zeros((len(moves) - 1, 6), bool)]))
        steps = [Step("s", "t", f"o{i}", [i], j @ moves[i], 1.0, np.full(8, 0.01), True)
                 for i in range(1, len(moves))]
        data = StepData([f"f{i}" for i in range(8)], {"s": hist}, steps)
        ours = response.fit(data, max_deadband=200.0, grid_step=50.0)
        theirs = np.array(host_modules().visual_servo.fit_jacobian(
            [{"delta_mm": (moves[s.move_index[0]] / COUNTS_PER_MM).tolist(), "delta_feature": s.dy.tolist()}
             for s in steps]))
        np.testing.assert_allclose(ours.jacobian_mm(np.ones(6)), theirs, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(ours.deadband, 0.0, atol=1e-9)


class Validation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rec = Recovery
        if not hasattr(rec, "model"):
            rec.setUpClass()
        cls.rec = rec

    def test_split_is_by_trial(self):
        r = self.rec
        self.assertFalse(set(r.train) & set(r.hold))
        groups, _ = groups_and_purposes(r.reader)
        held_axes = {groups[t] for t in r.hold}
        self.assertEqual(held_axes, {"X", "Y", "Z", "U", "V", "W"})     # stratified: every axis held out
        with self.assertRaises(ValueError):
            validation.check_split(r.data, r.train, r.hold + r.train[:1])
        report = validation.validate(r.model, r.data, r.hold)
        self.assertEqual({x["trial_id"] for x in report.residuals}, set(r.hold) & {s.trial_id for s in r.data.steps})

    def test_held_out_validation_passes_and_reports_residuals(self):
        r = self.rec
        report = validation.validate(r.model, r.data, r.hold)
        self.assertTrue(report.passed, report.reasons)
        self.assertEqual(len(report.validated_axis_directions), 12)
        for name, st in report.per_feature.items():
            self.assertGreater(st["skill"], 0.99, name)
            self.assertLess(st["rms"], 0.15, name)
        self.assertGreater(report.n_steps, 100)
        self.assertTrue(all(len(x["residual"]) == 8 for x in report.residuals))
        base = report.baseline_visual_servo
        self.assertTrue(base["available"])
        # Direction/take-up modelling beats the one-direction least-squares baseline on held-out steps.
        for name, st in report.per_feature.items():
            self.assertLess(st["rms"], base["per_feature"][name]["rms"])

    def test_wrong_model_fails_validation(self):
        """A model fitted on one mechanism does not validate on another's trials."""
        r = self.rec
        other_path, _ = simulated_dataset(seed=21, outlier_prob=0.0, backlash=(10, 150, 20, 40, 160, 15))
        other = response.assemble([SessionReader(other_path)])
        groups, purposes = groups_and_purposes(SessionReader(other_path))
        trials = [t for t in other.trials() if purposes[t] == "probe"]
        model = response.fit(r.data, r.train)
        mixed = response.StepData(other.feature_names, other.histories, other.steps)
        # Re-label: validate the first mechanism's model against the second mechanism's held-out trials.
        model.train_trials = [t for t in model.train_trials if t not in trials]
        report = validation.validate(model, mixed, trials[:12])
        self.assertFalse(report.passed)
        self.assertTrue(any("skill" in x or "outliers" in x for x in report.reasons))


if __name__ == "__main__":
    unittest.main()
