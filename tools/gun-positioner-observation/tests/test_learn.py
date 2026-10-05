"""observe.py learn: templates refused until filled, the simulated sequence, and every gate before real motion.

Real motion is exercised only against the fake controls Client (tests/support.py)
driving a simulated mechanism whose state is rendered into synthetic frames.
"""

import argparse
import contextlib
import io
import itertools
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

import numpy as np

from support import (EXAMPLES, SMALL_ROIS, FakeClient, FakeDevice, scene_source, tmpdir, write_features,
                     write_filled_setup, write_target)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import observe  # noqa: E402

from gpobs import helper_stream, learn  # noqa: E402
from gpobs.clock import FakeClock  # noqa: E402
from gpobs.controls import AXES, MAX_JOG_COUNTS, PROFILES, SOFT_MAX, host_modules  # noqa: E402
from gpobs.dataset import SessionReader  # noqa: E402
from gpobs.experiment import probe_trial  # noqa: E402
from gpobs.moves import MoveCommand  # noqa: E402


def run(*argv) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = observe.main([str(a) for a in argv])
    return code, out.getvalue()


def latest(root: Path, label: str) -> Path:
    return sorted(root.glob(f"*-{label}-*"))[-1]


def operator(lines):
    """Typed operator input; running out is end of input, as Ctrl-D at the prompt."""
    it = iter(lines)

    def read(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError from None
    return read


class Templates(unittest.TestCase):
    def setUp(self):
        self.dir = tmpdir(f"learn-templates-{self.id().split('.')[-1]}")
        self.features = write_features(self.dir / "features.json")

    def test_features_template_refused(self):
        problems = learn.load_features(EXAMPLES / "features.example.json").problems
        text = "\n".join(problems)
        for path in ("frames_per_observation", "min_valid_fraction", "settle_s", "features[0].roi.x",
                     "features[0].params.threshold_sigma", "features[5].params.min_edge_sigma"):
            self.assertIn(f"{path} still holds FILL_ME", text)
        self.assertEqual(run("learn", "check", "--features", EXAMPLES / "features.example.json")[0], 1)

    def test_target_template_refused(self):
        feats = learn.load_features(self.features)
        problems = learn.load_target(EXAMPLES / "target.example.json", feats).problems
        text = "\n".join(problems)
        for path in ("units", "axes", "quantities[0].point", "quantities[0].value", "quantities[1].tolerance"):
            self.assertIn(f"{path} still holds FILL_ME", text)
        self.assertEqual(run("learn", "check", "--features", self.features,
                             "--target", EXAMPLES / "target.example.json")[0], 1)

    def test_filled_files_pass(self):
        target = write_target(self.dir / "target.json", [
            {"name": "a dot to seam", "kind": "point_to_line", "point": "cam_a.dot", "line": "cam_a.seam",
             "value": 0.0, "tolerance": 0.5},
            {"name": "b wire ahead", "kind": "difference", "a": "cam_b.wire.u", "b": "cam_b.dot.u", "value": 40,
             "tolerance": 0.5}], ["X", "Z"])
        helper = self.dir / "helper"
        helper.write_bytes(b"stand-in")
        cameras = write_filled_setup(self.dir / "setup", helper)
        plan = self.dir / "plan.json"
        plan.write_text(json.dumps(learn.make_plan()))
        with mock.patch.object(helper_stream, "BINARY", helper):
            code, text = run("learn", "check", "--features", self.features, "--target", target, "--plan", plan,
                             "--cameras", cameras)
        self.assertEqual(code, 0, text)

    def test_feature_file_gaps(self):
        sizes = {"cam_a": (3840, 2160), "cam_b": (3840, 2160)}
        self.assertEqual(learn.load_features(self.features, sizes).problems, [])
        cases = {
            "roi beyond frame": lambda d: d["features"][0]["roi"].update(x=3800),
            "tiny roi": lambda d: d["features"][0]["roi"].update(width=4),
            "duplicate label": lambda d: d["features"][1].update(label="dot", type="dot",
                                                                 params=d["features"][0]["params"]),
            "negative threshold": lambda d: d["features"][0]["params"].update(threshold_sigma=-1),
            "unknown parameter": lambda d: d["features"][0]["params"].update(gain=3),
            "max below min pixels": lambda d: d["features"][0]["params"].update(max_pixels=2),
            "unknown type": lambda d: d["features"][0].update(type="blob"),
            "no frames": lambda d: d.update(frames_per_observation=0),
            "camera without verified format": lambda d: d["features"][0].update(camera_id="cam_c"),
        }
        for name, fn in cases.items():
            with self.subTest(name):
                data = json.loads(self.features.read_text())
                fn(data)
                path = self.dir / "mutated.json"
                path.write_text(json.dumps(data))
                self.assertTrue(learn.load_features(path, sizes).problems, name)

    def test_target_file_gaps(self):
        feats = learn.load_features(self.features)
        good = {"name": "q", "kind": "value", "feature": "cam_a.dot.u", "value": 1.0, "tolerance": 0.5}
        cases = {
            "unknown feature": ([dict(good, feature="cam_a.dot.w")], ["X"]),
            "point is a seam": ([{"name": "q", "kind": "point_to_line", "point": "cam_a.seam", "line": "cam_a.seam",
                                  "value": 0, "tolerance": 1}], ["X"]),
            "line is a dot": ([{"name": "q", "kind": "point_to_line", "point": "cam_a.dot", "line": "cam_a.dot",
                                "value": 0, "tolerance": 1}], ["X"]),
            "point and line in two cameras": ([{"name": "q", "kind": "point_to_line", "point": "cam_a.dot",
                                                "line": "cam_b.seam", "value": 0, "tolerance": 1}], ["X"]),
            "more axes than quantities": ([good], ["X", "Y"]),
            "unknown axis": ([good], ["Q"]),
            "zero tolerance": ([dict(good, tolerance=0)], ["X"]),
            "duplicate names": ([good, dict(good, feature="cam_a.dot.v")], ["X"]),
            "unknown kind": ([dict(good, kind="ratio")], ["X"]),
        }
        for name, (quantities, axes) in cases.items():
            with self.subTest(name):
                path = write_target(self.dir / "t.json", quantities, axes)
                self.assertTrue(learn.load_target(path, feats).problems, name)
        path = write_target(self.dir / "t.json", [good], ["X"])
        data = json.loads(path.read_text())
        data.update(units="mm", px_per_mm=None)
        path.write_text(json.dumps(data))
        self.assertTrue(any("calibration" in p or "px_per_mm" in p for p in learn.load_target(path, feats).problems))
        data.update(px_per_mm=500.0, calibration="synthetic calibration record")
        path.write_text(json.dumps(data))
        target = learn.load_target(path, feats)
        self.assertEqual(target.problems, [])
        self.assertEqual(target.values()["q"], 500.0)              # 1 mm at 500 px/mm
        self.assertEqual(target.tolerances()["q"], 250.0)

    def test_point_to_line_quantity_and_gradient(self):
        feats = learn.load_features(self.features)
        path = write_target(self.dir / "t.json", [{"name": "d", "kind": "point_to_line", "point": "cam_a.dot",
                                                   "line": "cam_a.seam", "value": 0, "tolerance": 1}], ["X"])
        q = learn.load_target(path, feats).quantities[0]
        x, y, w, h = learn.load_features(self.features).features[2].roi
        self.assertEqual(q.refs["center"], [x + (w - 1) / 2, y + (h - 1) / 2])
        cx, cy = q.refs["center"]
        y0 = {"cam_a.dot.u": cx + 30.0, "cam_a.dot.v": cy + 12.0, "cam_a.seam.theta_deg": 91.5, "cam_a.seam.rho": 2.0}
        t = np.radians(91.5)
        self.assertAlmostEqual(q.evaluate(y0), 30 * np.cos(t) + 12 * np.sin(t) - 2.0)
        grad = q.gradient(y0)
        for name in y0:
            step = 1e-4 if name.endswith("theta_deg") else 1e-3
            hi, lo = dict(y0), dict(y0)
            hi[name] += step
            lo[name] -= step
            self.assertAlmostEqual(grad[name], (q.evaluate(hi) - q.evaluate(lo)) / (2 * step), places=5)


class Plans(unittest.TestCase):
    def test_plan_bounds(self):
        self.assertEqual(learn.plan_problems(learn.make_plan()), [])
        self.assertTrue(learn.plan_problems(learn.make_plan(sizes=(16, 512), max_step=256)))
        self.assertTrue(learn.plan_problems(learn.make_plan(max_step=MAX_JOG_COUNTS + 60, sizes=(16,))))
        self.assertTrue(learn.plan_problems(learn.make_plan(engage_counts=300, max_step=256)))
        self.assertTrue(learn.plan_problems(learn.make_plan(axes=("X", "Q"))))
        code, text = run("learn", "plan", "--out", tmpdir("plans") / "p.json", "--max-step", 700, "--sizes", 16)
        self.assertEqual(code, 2)
        self.assertIn("max_step_counts must be 1..640", text)

    def test_probe_pattern_is_net_zero(self):
        plan = probe_trial(2, 64, 3)
        total = np.sum([s for s in plan.steps if s is not None], axis=0)
        self.assertEqual(total.tolist(), [0] * 6)
        signs = [int(np.sign(s[2])) for s in plan.steps if s is not None]
        self.assertEqual(sum(1 for a, b in zip(signs, signs[1:]) if a != b), 2)   # two reversals

    def test_engagement_moves(self):
        class M:
            deadband = np.array([60.0, 35, 90, 120, 45, 75])
        moves = learn.engagement_moves(M, ["X", "U"], 64)
        self.assertTrue(all(max(map(abs, m)) <= 64 for m in moves))
        x = [m[0] for m in moves]
        self.assertEqual(sum(c for c in x if c > 0), int(np.ceil(1.5 * 60)) + 16)
        self.assertEqual(sum(x), 0)
        self.assertLess(moves[-1][3], 0)                        # ends on the negative side


class SimulatedSequence(unittest.TestCase):
    """plan → record → jog → fit → validate → propose → execute, all on the default simulator."""

    @classmethod
    def setUpClass(cls):
        d = cls.dir = tmpdir("learn-sim")
        cls.features = write_features(d / "features.json", frames=5, settle_s=0.5)
        cls.sessions = d / "sessions"
        cls.analysis = d / "analysis"
        cls.codes = {}
        cls.codes["plan"], _ = run("learn", "plan", "--out", d / "jog-plan.json", "--sizes", 16, 64, 256)
        cls.codes["record"], _ = run("learn", "record", "--features", cls.features, "--root", cls.sessions,
                                     "--observations", 2)
        cls.codes["jog"], cls.jog_text = run("learn", "jog", "--plan", d / "jog-plan.json", "--features",
                                             cls.features, "--root", cls.sessions)
        cls.jog = latest(cls.sessions, "jog")
        cls.codes["fit"], _ = run("learn", "fit", cls.jog, "--features", cls.features, "--out", cls.analysis)
        cls.codes["validate"], cls.validate_text = run("learn", "validate", cls.jog, "--model",
                                                       cls.analysis / "model.json", "--split",
                                                       cls.analysis / "split.json", "--out", cls.analysis)
        probe = write_target(d / "target0.json", [
            {"name": "a dot to seam", "kind": "point_to_line", "point": "cam_a.dot", "line": "cam_a.seam",
             "value": 0, "tolerance": 0.5},
            {"name": "b wire ahead", "kind": "difference", "a": "cam_b.wire.u", "b": "cam_b.dot.u", "value": 0,
             "tolerance": 0.5}], ["X", "Y"])
        run("learn", "record", "--features", cls.features, "--root", cls.sessions, "--observations", 2,
            "--target", probe)
        cls.record = latest(cls.sessions, "record")
        code, text = run("learn", "propose", "--model", cls.analysis / "model.json", "--validation",
                         cls.analysis / "validation.json", "--features", cls.features, "--target", probe,
                         "--session", cls.record, "--out", d / "probe-proposal.json")
        review = json.loads(text)
        sens = review["sensitivity_px_per_count"]
        axes = sorted("XYZUVW", key=lambda a: -sum(abs(sens[n][a]) for n in sens))[:2]
        quantities = json.loads(probe.read_text())["quantities"]
        for q in quantities:
            q["value"] = round(review["quantities"][q["name"]]["observed"] + 6.0, 2)
        cls.target = write_target(d / "target.json", quantities, axes)
        cls.codes["propose"], cls.propose_text = run(
            "learn", "propose", "--model", cls.analysis / "model.json", "--validation",
            cls.analysis / "validation.json", "--features", cls.features, "--target", cls.target, "--session",
            cls.record, "--out", d / "proposal.json")
        cls.codes["execute"], cls.execute_text = run(
            "learn", "execute", "--model", cls.analysis / "model.json", "--validation",
            cls.analysis / "validation.json", "--features", cls.features, "--target", cls.target, "--root",
            cls.sessions, "--max-moves", 40)

    def test_each_step_succeeds_and_writes_its_files(self):
        self.assertEqual(self.codes, {"plan": 0, "record": 0, "jog": 0, "fit": 0, "validate": 0, "propose": 0,
                                      "execute": 0})
        for f in ("jog-plan.json", "analysis/model.json", "analysis/split.json", "analysis/validation.json",
                  "analysis/validation-report.txt", "proposal.json", "sessions/simulated-world.json"):
            self.assertTrue((self.dir / f).exists(), f)
        self.assertTrue((self.record / "feature-summary.json").exists())
        jog = SessionReader(self.jog)
        self.assertTrue(jog.integrity().ok, jog.integrity().problems)
        self.assertGreater(len(jog.records("move_complete")), 100)
        self.assertEqual({r["outcome"] for r in jog.records("trial_end")}, {"completed"})

    def test_validation_report_is_explicit(self):
        self.assertTrue(self.validate_text.startswith("VALIDATION: PASS"))
        report = (self.analysis / "validation-report.txt").read_text()
        self.assertIn("whole trials, never split", report)
        self.assertIn("X+", report)
        split = json.loads((self.analysis / "split.json").read_text())
        self.assertFalse(set(split["train"]) & set(split["holdout"]))

    def test_review_proposal_is_bounded_and_never_executed(self):
        proposal = json.loads((self.dir / "proposal.json").read_text())
        self.assertTrue(proposal["review_only"])
        self.assertTrue(all(abs(c) <= 64 for c in proposal["proposal"]["counts"]))
        held = [a for a in "XYZUVW" if a not in proposal["axes"]]
        self.assertTrue(all(proposal["proposal"]["counts"]["XYZUVW".index(a)] == 0 for a in held))
        self.assertNotIn("propose", [r["config"].get("step") for r in
                                     [SessionReader(p).manifest for p in self.sessions.glob("*-*-*")
                                      if p.is_dir()]])

    def test_execute_converges_in_simulation(self):
        result = json.loads(self.execute_text)
        self.assertEqual(result["outcome"], "completed", result["reason"])
        for q in result["quantities"].values():
            self.assertLessEqual(abs(q["observed"] - q["desired"]), 2 * q["tolerance"])
        session = SessionReader(Path(result["session"]))
        purposes = {r["purpose"] for r in session.records("move_command")}
        self.assertIn("engage", purposes)
        self.assertTrue(all(max(map(abs, r["counts"])) <= 64 for r in session.records("move_command")))

    def test_validation_fails_for_another_mechanism(self):
        other = self.dir / "other"
        run("learn", "jog", "--plan", self.dir / "jog-plan.json", "--features", self.features, "--root", other,
            "--seed", 99)
        code, text = run("learn", "validate", latest(other, "jog"), "--model", self.analysis / "model.json",
                         "--out", self.dir / "other-analysis")
        self.assertEqual(code, 1)
        self.assertTrue(text.startswith("VALIDATION: FAIL"))


class HardwareGates(unittest.TestCase):
    """Every refusal before real motion, then the full path, against the fake controls Client."""

    def setUp(self):
        d = self.dir = tmpdir(f"learn-hw-{self.id().split('.')[-1]}")
        self.helper = d / "stand-in-helper"
        self.helper.write_bytes(b"stand-in helper build")
        self.patches = [mock.patch.object(helper_stream, "BINARY", self.helper)]
        for p in self.patches:
            p.start()
        self.cameras = write_filled_setup(d / "setup", self.helper, width=320, height=240, fps=30.0,
                                          pixel_format="420v", require_native_4k=False)
        self.features = write_features(d / "features.json", SMALL_ROIS, frames=3, settle_s=0.2)
        self.plan = d / "jog-plan.json"
        self.plan.write_text(json.dumps(learn.make_plan(axes=["X"], sizes=[16, 64], repeats=2, trials_per_size=2,
                                                        max_step=64, engage_counts=64)))
        self.feats = learn.load_features(self.features)
        self.clock = FakeClock()
        self.world = learn.SimWorld(self.feats.names(), seed=5, frame=(320, 240),
                                    starts=learn.world_starts(self.feats, 5))
        self.device = FakeDevice(self.clock, state="unreferenced", on_move=self.apply_move)
        self.constructed = []

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def apply_move(self, delta):
        self.world.mechanism.advance_to(self.clock.monotonic_ns())
        self.world.mechanism.move(delta)

    def client_factory(self, port, log):
        self.constructed.append(port)
        return FakeClient.with_device(self.device, log)

    def args(self, **kw):
        base = dict(plan=self.plan, features=self.features, root=self.dir / "sessions", label="jog",
                    backend="controller", world=None, seed=7, cameras=self.cameras, port="/dev/cu.fake",
                    launch="exec", store_frames="window_first", i_understand_this_moves_hardware=True)
        base.update(kw)
        return argparse.Namespace(**base)

    def jog(self, inputs, **kw):
        out = io.StringIO()
        with mock.patch.object(host_modules().positioner, "Client", self.client_factory):
            code = learn.run_jog(self.args(**kw), clock=self.clock, synchronous=True,
                                 source_factory=lambda cam: scene_source(self.world, self.feats, self.clock,
                                                                         cam.camera_id),
                                 input_fn=operator(inputs), print_fn=lambda *a: print(*a, file=out))
        return code, out.getvalue()

    def execute(self, analysis, target, inputs):
        out = io.StringIO()
        args = argparse.Namespace(model=analysis / "model.json", validation=analysis / "validation.json",
                                  features=self.features, target=target, root=self.dir / "sessions",
                                  label="execute", max_moves=30, max_step=64, backend="controller", world=None,
                                  seed=7, cameras=self.cameras, port="/dev/cu.fake", launch="exec",
                                  store_frames="window_first", i_understand_this_moves_hardware=True)
        with mock.patch.object(host_modules().positioner, "Client", self.client_factory):
            code = learn.run_execute(args, clock=self.clock, synchronous=True,
                                     source_factory=lambda cam: scene_source(self.world, self.feats, self.clock,
                                                                             cam.camera_id),
                                     input_fn=inputs, print_fn=lambda *a: print(*a, file=out))
        text = out.getvalue()
        return code, text, json.loads(text[text.rindex('{\n "outcome"'):])

    def moves_sent(self):
        return [line for line in self.device.sent if line.startswith("MOVE6")]

    def test_refusals_before_connecting(self):
        template_features = EXAMPLES / "features.example.json"
        bad_plan = self.dir / "bad-plan.json"
        bad_plan.write_text(json.dumps(dict(learn.make_plan(), max_step_counts=700, sizes=[16])))
        failing_clock = self.dir / "setup" / "clock-check-failed.json"
        receipt = json.loads((self.dir / "setup" / "clock-check.json").read_text())
        failing_clock.write_text(json.dumps(dict(receipt, passed=False)))
        failing_cameras = self.dir / "setup" / "cameras-failing-clock.json"
        cams = json.loads(self.cameras.read_text())
        cams["clock_check"]["receipt"] = failing_clock.name
        failing_cameras.write_text(json.dumps(cams))
        cases = {
            "no explicit flag": (dict(i_understand_this_moves_hardware=False), "--i-understand-this-moves-hardware"),
            "camera template": (dict(cameras=EXAMPLES / "cameras.example.json"), "cameras: "),
            "failing clock check": (dict(cameras=failing_cameras), "clock check: "),
            "features template": (dict(features=template_features), "features: "),
            "plan beyond firmware bound": (dict(plan=bad_plan), "plan: max_step_counts must be 1..640"),
            "no port": (dict(port=None), "--port"),
            "no cameras": (dict(cameras=None), "--cameras"),
        }
        for name, (change, expected) in cases.items():
            with self.subTest(name):
                code, text = self.jog([], **change)
                self.assertEqual(code, 2, text)
                self.assertIn(expected, text)
                self.assertEqual(self.constructed, [], "nothing may connect to the controller")

    def test_controller_not_ready_refuses_motion(self):
        cases = {
            "operator quits": (["status", "quit"], {}),
            "go without arming": (["go", "quit"], {}),
            "arm without reference": (["clear", "arm", "go", "quit"], {}),
            "drivers not ok": (["clear", "reference central", "arm", "go", "quit"], {"drivers_ok": False}),
            "microsteps unverified": (["clear", "reference central", "arm", "go", "quit"],
                                      {"microsteps": [16, 16, None, 16, 16, 16]}),
            "input ends": (["clear"], {}),
        }
        for name, (inputs, device_state) in cases.items():
            with self.subTest(name):
                self.device = FakeDevice(self.clock, state="unreferenced", on_move=self.apply_move)
                for k, v in device_state.items():
                    setattr(self.device, k, v)
                code, text = self.jog(inputs)
                self.assertEqual(code, 3, text)
                self.assertEqual(self.moves_sent(), [])
                if "go" in inputs:
                    self.assertIn("not ready", text)
                self.assertEqual(self.device.state, "fault")            # the session ends with STOP

    def test_go_refuses_a_driver_profile_other_than_the_export(self):
        loaded = PROFILES["loaded-development"]
        flipped = list(loaded["vsense"])
        flipped[AXES.index("Z")] ^= 1
        pitch = list(loaded["current_scales"])
        pitch[AXES.index("V")] += 2
        cases = {
            "decoded VSENSE differs while drivers_ok": ({"vsense": flipped}, "decoded vsense"),
            "configured VSENSE differs": ({"configured_vsense": flipped}, "configured_vsense"),
            "pitch current scale differs": ({"current_scales": pitch}, "current_scales"),
        }
        for name, (fields, reason) in cases.items():
            with self.subTest(name):
                self.device = FakeDevice(self.clock, state="unreferenced", on_move=self.apply_move)
                self.device.status_overrides = fields
                self.assertTrue(self.device.status()["drivers_ok"])
                code, text = self.jog(["clear", "reference central", "arm", "go", "quit"])
                self.assertEqual(code, 3, text)
                self.assertEqual(self.moves_sent(), [])
                self.assertIn("not ready: ", text)
                self.assertIn("driver profile: " + reason, text)

    def test_gate_refuses_out_of_bound_and_soft_limit_moves(self):
        class Inner:
            clock = self.clock
            max_rate = 1000
            info = None
            sent = []

            def __init__(self, status):
                self.last_status = status

            def execute(self, cmd):
                Inner.sent.append(cmd)
                raise AssertionError("a refused move reached the controller")

        ready = dict(FakeDevice(self.clock).status(), count=[0] * 6)
        self.assertEqual(learn.controller_refusals(ready), [])
        loaded = PROFILES[ready["profile"]]
        flipped = list(loaded["vsense"])
        flipped[AXES.index("Z")] ^= 1
        cases = {
            "decoded VSENSE differs": (dict(ready, vsense=flipped), (10, 0, 0, 0, 0, 0)),
            "other profile's currents": (dict(ready, current_scales=PROFILES["bench"]["current_scales"]),
                                         (10, 0, 0, 0, 0, 0)),
            "beyond the step bound": (ready, (65, 0, 0, 0, 0, 0)),
            "beyond the soft limit": (dict(ready, count=[SOFT_MAX[0] - 10, 0, 0, 0, 0, 0]), (20, 0, 0, 0, 0, 0)),
            "drivers not ok": (dict(ready, drivers_ok=False), (10, 0, 0, 0, 0, 0)),
            "not armed": (dict(ready, state="referenced"), (10, 0, 0, 0, 0, 0)),
            "fault": (dict(ready, fault="driver"), (10, 0, 0, 0, 0, 0)),
            "counts unknown": (dict(ready, count=None), (10, 0, 0, 0, 0, 0)),
        }
        for name, (status, counts) in cases.items():
            with self.subTest(name):
                gate = learn.GatedBackend(Inner(status), 64, self.clock)
                out = gate.execute(MoveCommand("m", counts, 200_000, "probe_jog"))
                self.assertEqual(out.status, "rejected")
                self.assertTrue(gate.halted)
                again = gate.execute(MoveCommand("n", (1, 0, 0, 0, 0, 0), 200_000, "probe_jog"))
                self.assertEqual(again.status, "rejected")               # halted: nothing further is sent
        self.assertEqual(Inner.sent, [])

    def test_default_backend_never_connects(self):
        with mock.patch.object(host_modules().positioner, "Client",
                               side_effect=AssertionError("the simulator must not connect")):
            code, text = run("learn", "jog", "--plan", self.plan, "--features", self.features, "--root",
                             self.dir / "sim")
        self.assertEqual(code, 0, text)

    def test_full_path_jog_fit_validate_execute_with_fakes(self):
        code, text = self.jog(["status", "clear", "reference central", "arm", "go"])
        self.assertEqual(code, 0, text)
        self.assertEqual(self.constructed, ["/dev/cu.fake"])
        sent = self.moves_sent()
        self.assertGreater(len(sent), 30)
        self.assertTrue(all(max(abs(int(t)) for t in line.split()[4:]) <= 64 for line in sent))
        self.assertEqual(self.device.state, "fault")                    # STOP on exit, as the controls console
        session = latest(self.dir / "sessions", "jog")
        reader = SessionReader(session)
        self.assertTrue(reader.integrity().ok, reader.integrity().problems)
        self.assertEqual({r["status"] for r in reader.records("move_complete")}, {"done"})
        self.assertTrue(all(r["vm_epoch"] == 1 for r in reader.records("move_complete")))
        obs = reader.records("observation")
        self.assertTrue(obs and all(all(v is not None for v in o["values"].values()) for o in obs))
        self.assertTrue(any(f["stored"] for f in reader.records("frame")))
        analysis = self.dir / "analysis"
        self.assertEqual(run("learn", "fit", session, "--features", self.features, "--out", analysis,
                             "--holdout-fraction", 0.5, "--max-deadband", 120)[0], 0)
        code, text = run("learn", "validate", session, "--model", analysis / "model.json", "--split",
                         analysis / "split.json", "--out", analysis)
        self.assertEqual(code, 0, text)
        report = json.loads((analysis / "validation.json").read_text())
        self.assertEqual(sorted(report["validated_axis_directions"]), ["X+", "X-"])
        # execute: one quantity, axis X only; the operator arms and confirms each move.
        y = dict(zip(self.world.names, self.world.mechanism.true_features()))
        target = write_target(self.dir / "target.json", [
            {"name": "a dot u", "kind": "value", "feature": "cam_a.dot.u",
             "value": round(y["cam_a.dot.u"] + 3.0, 2), "tolerance": 0.3}], ["X"])
        self.device.state, self.device.fault = "unreferenced", "none"
        before = len(self.moves_sent())
        answers = itertools.chain(["clear", "reference central", "arm", "go"], itertools.repeat("y"))
        code, text, result = self.execute(analysis, target, lambda prompt="": next(answers))
        self.assertEqual(code, 0, text)
        self.assertEqual(result["outcome"], "completed", result["reason"])
        new_moves = self.moves_sent()[before:]
        self.assertTrue(new_moves)
        self.assertTrue(all(int(t) == 0 for line in new_moves for t in line.split()[5:]))   # only X moved
        y = dict(zip(self.world.names, self.world.mechanism.true_features()))
        self.assertLess(abs(y["cam_a.dot.u"] - result["quantities"]["a dot u"]["desired"]), 0.6)
        # The operator declines: nothing moves after arming.
        self.device.state, self.device.fault = "unreferenced", "none"
        before = len(self.moves_sent())
        code, text, result = self.execute(analysis, target,
                                          operator(["clear", "reference central", "arm", "go", "n"]))
        self.assertEqual(code, 1, text)
        self.assertEqual(result["outcome"], "aborted")
        self.assertIn("declined", result["reason"])
        self.assertEqual(self.moves_sent()[before:], [])

    def test_execute_declined_and_unvalidated(self):
        # A failing validation report refuses execution on either backend.
        model = self.dir / "model.json"
        report = self.dir / "validation.json"
        model.write_text(json.dumps({"placeholder": True}))
        report.write_text(json.dumps({"passed": False}))
        with mock.patch.object(learn, "_load_model_and_report",
                               return_value=(mock.Mock(model_id="rm-x"), mock.Mock(passed=False), {"passed": False})):
            target = write_target(self.dir / "t.json", [{"name": "q", "kind": "value", "feature": "cam_a.dot.u",
                                                         "value": 1.0, "tolerance": 0.5}], ["X"])
            for backend in ("simulator", "controller"):
                with self.subTest(backend):
                    out = io.StringIO()
                    args = argparse.Namespace(model=model, validation=report, features=self.features, target=target,
                                              root=self.dir / "s", label="execute", max_moves=5, max_step=64,
                                              backend=backend, world=None, seed=7, cameras=self.cameras,
                                              port="/dev/cu.fake", launch="exec", store_frames="window_first",
                                              i_understand_this_moves_hardware=True)
                    with mock.patch.object(host_modules().positioner, "Client", self.client_factory):
                        code = learn.run_execute(args, clock=self.clock, synchronous=True,
                                                 print_fn=lambda *a: print(*a, file=out))
                    self.assertEqual(code, 2, out.getvalue())
                    self.assertIn("validation", out.getvalue())
        self.assertEqual(self.constructed, [])


if __name__ == "__main__":
    unittest.main()
