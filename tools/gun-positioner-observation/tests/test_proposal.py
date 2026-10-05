"""Bounded corrections, no-motion defaults, and closed-loop behaviour on the simulator."""

import copy
import unittest
from unittest import mock

import numpy as np

from support import groups_and_purposes, simulated_dataset, tmpdir

from gpobs import response, validation
from gpobs.clock import FakeClock
from gpobs.controls import SOFT_MAX, host_modules
from gpobs.dataset import SessionReader, SessionWriter
from gpobs.experiment import Runner, SimulatedObserver
from gpobs.moves import MoveRecorder
from gpobs.proposal import CorrectionController, Observation, ProposalConfig, propose
from gpobs.simulation import SimulatedMechanism, SimulatedPositioner


class Fixture:
    model = report = truth = None

    @classmethod
    def load(cls):
        if cls.model is None:
            path, cls.truth = simulated_dataset(seed=7, outlier_prob=0.03)
            reader = SessionReader(path)
            data = response.assemble([reader])
            groups, purposes = groups_and_purposes(reader)
            probes = [t for t in data.trials() if purposes[t] == "probe"]
            train, hold = validation.split_trials(probes, 0.34, seed=1, groups=groups)
            cls.model = response.fit(data, train + [t for t in data.trials() if purposes[t] != "probe"])
            cls.report = validation.validate(cls.model, data, hold)
        return cls


def observation(values, t_start=10_000_000_000, t_end=10_200_000_000, sigma=0.02, conf=1.0, obs_id="o1"):
    return Observation(obs_id, t_start, t_end, dict(values), {k: sigma for k in values}, {k: conf for k in values})


class Proposals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f = Fixture.load()
        cls.model, cls.report, cls.truth = f.model, f.report, f.truth
        cls.names = cls.model.feature_names
        cls.start = {n: 1000.0 + i for i, n in enumerate(cls.names)}
        cls.now = 10_300_000_000
        cls.last = 9_000_000_000

    def target_for(self, counts):
        c = np.array(counts, float)
        dy = self.truth.j_plus @ np.maximum(c, 0) + self.truth.j_minus @ np.minimum(c, 0)
        return {n: self.start[n] + d for n, d in zip(self.names, dy)}

    def p(self, target, obs=None, cfg=None, report=None, now_ns=None, last_complete_ns=None,
          counts_now=(0,) * 6, direction=(1,) * 6):
        return propose(self.model, report or self.report, obs or observation(self.start), target,
                       cfg or ProposalConfig(), self.now if now_ns is None else now_ns,
                       self.last if last_complete_ns is None else last_complete_ns,
                       None if counts_now is None else list(counts_now),
                       None if direction is None else list(direction))

    def test_trust_region_and_axis_bounds(self):
        cfg = ProposalConfig(max_step_counts=(200, 200, 100, 300, 200, 50), trust_radius=0.8)
        for counts in ([150, 0, 0, 0, 0, 0], [250, 180, 90, 200, 160, 40], [300, 240, 120, 330, 240, 60]):
            pr = self.p(self.target_for(counts), cfg=cfg)
            self.assertEqual(pr.status, "move", pr.reasons)
            c = np.array(pr.counts)
            self.assertTrue(np.all(np.abs(c) <= np.array(cfg.max_step_counts)))
            self.assertLessEqual(np.linalg.norm(c / np.array(cfg.max_step_counts)), cfg.trust_radius + 0.02)
        small = self.p(self.target_for([60, 0, 0, 0, 0, 0]), cfg=cfg)
        self.assertEqual(small.counts[0], 60)       # inside the trust region: the full step
        self.assertTrue(all(abs(c) <= 1 for c in small.counts[1:]))

    def test_uses_controls_correction_with_damping_rows(self):
        vs = host_modules().visual_servo
        calls = []
        real = vs.correction

        def spy(jacobian, error, trust_mm=0.01):
            calls.append((len(jacobian), len(error), trust_mm))
            return real(jacobian, error, trust_mm)

        with mock.patch.object(vs, "correction", spy):
            pr = self.p(self.target_for([100, -40, 0, 30, 0, 0]), direction=[1, -1, 1, 1, 1, 1])
        self.assertEqual(pr.status, "move")
        self.assertTrue(calls)
        self.assertTrue(all(rows == len(self.names) + 6 and err == rows for rows, err, _ in calls))
        self.assertEqual(calls[-1][2], 1.0)

    def test_zero_motion_defaults(self):
        tgt = self.target_for([100, 0, 0, 0, 0, 0])
        ok = self.p(tgt)
        self.assertEqual(ok.status, "move")

        def reasons(pr):
            self.assertEqual(pr.status, "zero")
            self.assertEqual(pr.counts, [0] * 6)
            return " ".join(pr.reasons)

        self.assertIn("no_model", reasons(propose(None, self.report, observation(self.start), tgt, ProposalConfig(),
                                                  self.now, self.last)))
        self.assertIn("no_validation_report", reasons(propose(self.model, None, observation(self.start), tgt,
                                                              ProposalConfig(), self.now, self.last)))
        other = copy.deepcopy(self.report)
        other.model_id = "rm-somethingelse"
        self.assertIn("another_model", reasons(self.p(tgt, report=other)))
        failed = copy.deepcopy(self.report)
        failed.passed, failed.reasons = False, ["held-out skill too low"]
        self.assertIn("model_not_validated", reasons(self.p(tgt, report=failed)))
        missing = dict(self.start)
        missing[self.names[3]] = None
        self.assertIn("missing_feature", reasons(self.p(tgt, obs=observation(missing))))
        nan = dict(self.start)
        nan[self.names[0]] = float("nan")
        self.assertIn("missing_feature", reasons(self.p(tgt, obs=observation(nan))))
        self.assertIn("low_confidence", reasons(self.p(tgt, obs=observation(self.start, conf=0.2))))
        self.assertIn("uncertainty_too_high", reasons(self.p(tgt, cfg=ProposalConfig(max_sigma=0.01))))
        self.assertIn("stale_observation", reasons(self.p(tgt, now_ns=self.now + int(60e9))))
        self.assertIn("not_settled", reasons(self.p(tgt, last_complete_ns=9_900_000_000)))
        self.assertIn("outside_trust_region", reasons(self.p(self.target_for([3000, 0, 0, 0, 0, 0]))))
        near_limit = list(SOFT_MAX)
        self.assertIn("exceeds_travel_bounds", reasons(self.p(tgt, counts_now=near_limit)))
        self.assertIn("insufficiently_observable",
                      reasons(self.p(tgt, cfg=ProposalConfig(features=self.names[:2]))))
        self.assertIn("takeup_state_unknown", reasons(self.p(tgt, direction=[0] * 6)))
        tiny = self.target_for([1, 0, 0, 0, 0, 0])
        self.assertIn("below_noise", reasons(self.p(tiny, cfg=ProposalConfig(tolerance=0.01, min_predicted_snr=50))))
        self.assertEqual(reasons(self.p(dict(self.start))), "within_tolerance")
        missing_target = dict(tgt)
        del missing_target[self.names[1]]
        self.assertIn("missing_target", reasons(self.p(missing_target)))

    def test_unvalidated_direction_is_held(self):
        rep = copy.deepcopy(self.report)
        rep.validated_axis_directions = [a for a in rep.validated_axis_directions if a != "X-"]
        pr = self.p(self.target_for([-120, 60, 0, 0, 0, 0]), report=rep, direction=[-1, 1, 1, 1, 1, 1])
        self.assertGreaterEqual(pr.counts[0], 0)
        rep.validated_axis_directions = []
        self.assertEqual(self.p(self.target_for([100, 0, 0, 0, 0, 0]), report=rep).status, "zero")

    def test_controller_status_blocks_motion(self):
        tgt = self.target_for([100, 0, 0, 0, 0, 0])
        good = {"state": "armed", "fault": "none", "referenced": True, "drivers_ok": True, "microsteps": [16] * 6}
        self.assertEqual(propose(self.model, self.report, observation(self.start), tgt, ProposalConfig(), self.now,
                                 self.last, [0] * 6, [1] * 6, controller_status=good).status, "move")
        self.assertEqual(propose(self.model, self.report, observation(self.start), tgt, ProposalConfig(), self.now,
                                 self.last, [0] * 6, [1] * 6, controller_status={**good, "microsteps": 16}).status,
                         "move")                                       # the scalar form some builds report
        for bad, reason in (({"drivers_ok": False}, "drivers_not_ok"), ({"microsteps": None}, "microsteps_unverified"),
                            ({"microsteps": [16, 16, None, 16, 16, 16]}, "microsteps_unverified"),
                            ({"state": "fault", "fault": "driver"}, "controller_fault"),
                            ({"referenced": False}, "controller_not_referenced")):
            pr = propose(self.model, self.report, observation(self.start), tgt, ProposalConfig(), self.now,
                         self.last, [0] * 6, [1] * 6, controller_status={**good, **bad})
            self.assertEqual(pr.status, "zero")
            self.assertTrue(any(r.startswith(reason) for r in pr.reasons), pr.reasons)
        missing = {k: v for k, v in good.items() if k != "microsteps"}
        self.assertIn("microsteps_unverified", propose(self.model, self.report, observation(self.start), tgt,
                                                       ProposalConfig(), self.now, self.last, [0] * 6, [1] * 6,
                                                       controller_status=missing).reasons)

    def test_reversal_flagged(self):
        pr = self.p(self.target_for([-100, 0, 0, 0, 0, 0]), direction=[1] * 6)
        self.assertEqual(pr.status, "move")
        self.assertIn("X", pr.reversal_axes)


class ClosedLoop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f = Fixture.load()
        cls.model, cls.report, cls.truth = f.model, f.report, f.truth

    def run_loop(self, offset, jammed=(), max_iters=60, cfg=None):
        clock = FakeClock()
        mech = SimulatedMechanism(self.truth, seed=99, jammed=jammed)
        writer = SessionWriter(tmpdir("loops"), "loop", clock)
        rec = MoveRecorder(SimulatedPositioner(mech, clock, profile="loaded-development"), writer, clock)
        runner = Runner(rec, SimulatedObserver(mech, writer, clock), writer, clock)
        runner.engage()
        start = mech.true_features()
        c = np.array(offset, float)
        goal = start + self.truth.j_plus @ np.maximum(c, 0) + self.truth.j_minus @ np.minimum(c, 0)
        target = {n: float(v) for n, v in zip(self.truth.feature_names, goal)}
        cfg = cfg or ProposalConfig(max_step_counts=(150,) * 6, tolerance=0.3)
        ctl = CorrectionController(self.model, self.report, cfg)
        result = runner.closed_loop(ctl, target, max_iters=max_iters)
        writer.close()
        records = SessionReader(writer.path).records()
        moves = [r for r in records if r["kind"] == "move_command" and r["trial_id"] == result.trial_id]
        return result, mech, goal, moves, ctl, records

    def test_converges_within_bounds_with_reversal_takeup(self):
        result, mech, goal, moves, _, records = self.run_loop([280, -220, 120, -90, 160, -150])
        self.assertEqual(result.outcome, "completed", result.reason)
        self.assertLess(np.max(np.abs(mech.true_features() - goal)), 0.4)
        self.assertTrue(all(max(map(abs, m["counts"])) <= 150 for m in moves))
        purposes = {m["purpose"] for m in moves}
        self.assertIn("reversal_takeup", purposes)
        self.assertIn("correction", purposes)
        takeups = [m for m in moves if m["purpose"] == "reversal_takeup"]
        self.assertTrue(all(sum(1 for c in m["counts"] if c) == 1 for m in takeups))
        proposals = [r["proposal"] for r in records if r["kind"] == "proposal"]
        self.assertEqual(proposals[-1]["reasons"], ["within_tolerance"])

    def test_several_targets_converge_or_stop_at_precision_floor(self):
        offsets = ([150, -120, 60, -40, 90, -70], [-200, 180, -90, 140, -30, 60], [10, -10, 10, -10, 10, -10])
        floor_reasons = ("no_progress_at_precision_floor", "remaining_error_below_reversal_resolution")
        for tol, must_complete in ((0.6, True), (0.3, False)):
            for off in offsets:
                cfg = ProposalConfig(max_step_counts=(150,) * 6, tolerance=tol)
                result, mech, goal, moves, _, _ = self.run_loop(off, max_iters=100, cfg=cfg)
                self.assertTrue(all(max(map(abs, m["counts"])) <= 150 for m in moves))
                self.assertLessEqual(len(moves), 100)
                if must_complete or result.outcome == "completed":
                    self.assertEqual(result.outcome, "completed", (tol, off, result.reason))
                    self.assertLess(np.max(np.abs(mech.true_features() - goal)), 2 * tol)
                else:
                    self.assertTrue(result.reason.startswith(floor_reasons), (tol, off, result.reason))

    def test_jammed_axis_stops_without_accumulating(self):
        result, _, _, moves, ctl, _ = self.run_loop([200, 0, 0, 0, 0, 0], jammed=(0,))
        self.assertNotEqual(result.outcome, "completed")
        self.assertTrue("axis_unresponsive:X" in result.reason or "no_observed_response" in result.reason,
                        result.reason)
        self.assertLessEqual(len(moves), 3)
        self.assertLessEqual(sum(abs(m["counts"][0]) for m in moves), ctl.axis_limit(0, 1) + 150)

    def test_jammed_axis_reversal_reported_unresponsive(self):
        result, _, _, moves, ctl, _ = self.run_loop([-200, 0, 0, 0, 0, 0], jammed=(0,))
        self.assertIn("axis_unresponsive:X", result.reason)
        takeups = [m for m in moves if m["purpose"] == "reversal_takeup"]
        self.assertTrue(takeups)
        total = sum(abs(m["counts"][0]) for m in takeups)
        self.assertLessEqual(total, ctl.axis_limit(0, -1) + max(ctl.takeup_bulk(0), ctl.takeup_step(0, -1)))
        self.assertEqual(abs(takeups[0]["counts"][0]), ctl.takeup_bulk(0))   # stays inside the dead-band estimate
        self.assertLess(ctl.takeup_bulk(0), self.model.deadband[0])

    def test_takeup_respects_travel_limits_and_unknown_state(self):
        f = Fixture.load()
        cfg = ProposalConfig(max_step_counts=(150,) * 6, tolerance=0.3)
        names = f.model.feature_names
        start = {n: 1000.0 + i for i, n in enumerate(names)}
        c = np.array([-120, 0, 0, 0, 0, 0], float)
        dy = f.truth.j_minus @ c
        target = {n: start[n] + d for n, d in zip(names, dy)}
        obs = observation(start)
        ctl = CorrectionController(f.model, f.report, cfg)
        near_floor = list(cfg.soft_min)
        near_floor[0] += 10                      # X sits 10 counts above its lower soft limit
        p = ctl.propose(obs, target, 10_300_000_000, 9_000_000_000, near_floor, [1] * 6)
        self.assertEqual(p.status, "zero")
        self.assertIn("exceeds_travel_bounds", p.reasons)
        ctl = CorrectionController(f.model, f.report, cfg)
        p = ctl.propose(obs, target, 10_300_000_000, 9_000_000_000, [0] * 6, [1] * 6)
        self.assertEqual(p.purpose, "reversal_takeup")
        later = observation(start, t_start=11_000_000_000, t_end=11_200_000_000, obs_id="o2")
        p2 = ctl.propose(later, target, 11_300_000_000, 10_400_000_000, [0] * 6, [0, 1, 1, 1, 1, 1])
        self.assertEqual(p2.status, "zero")
        self.assertIn("takeup_state_unknown:X", p2.reasons)

    def test_outlier_observation_is_reobserved_not_acted_on(self):
        truth = copy.deepcopy(self.truth)
        truth.outlier_prob = 0.15
        saved, ClosedLoop.truth = ClosedLoop.truth, truth
        try:
            result, mech, goal, moves, ctl, records = self.run_loop([150, -120, 60, -40, 90, -70])
        finally:
            ClosedLoop.truth = saved
        reasons = [r["proposal"]["reasons"] for r in records if r["kind"] == "proposal"]
        self.assertIn(["observation_inconsistent_with_last_move"], reasons)
        self.assertEqual(result.outcome, "completed", result.reason)
        self.assertLess(np.max(np.abs(mech.true_features() - goal)), 0.4)
        flagged = [e for e in ctl.evaluations if e["suspect"]]
        self.assertTrue(all(e["chi2_per_dof"] > ctl.innovation_limit for e in flagged))


if __name__ == "__main__":
    unittest.main()
