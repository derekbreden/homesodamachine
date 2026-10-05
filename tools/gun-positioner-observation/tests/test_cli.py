"""observe.py end to end: simulate, fit, propose, check, optics check, schema, capture (synthetic helper)."""

import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

from support import EXAMPLES, filled_receipt, tmpdir

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import observe  # noqa: E402

from gpobs import helper_stream  # noqa: E402
from gpobs.config import iso_time  # noqa: E402
from gpobs.dataset import SessionReader  # noqa: E402


def run(*argv) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = observe.main(list(map(str, argv)))
    return code, out.getvalue()


def run_err(*argv) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = observe.main(list(map(str, argv)))
    return code, out.getvalue(), err.getvalue()


class Cli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tmpdir("cli")
        code, text = run("simulate", "--root", cls.root / "sessions", "--out", cls.root / "analysis",
                         "--sizes", 16, 64, 256, "--trials-per-size", 2, "--closed-loop")
        cls.code, cls.summary = code, json.loads(text)

    def test_simulate_learns_and_validates(self):
        self.assertEqual(self.code, 0)
        s = self.summary
        self.assertTrue(s["validation_passed"], s["validation_reasons"])
        for got, true in zip(s["deadband_counts"], s["true_deadband_counts"]):
            self.assertAlmostEqual(got, true, delta=3)
        self.assertLess(s["j_plus_relative_error"], 0.01)
        self.assertIn(s["closed_loop"]["outcome"], ("completed", "failed"))
        if s["closed_loop"]["outcome"] == "failed":
            self.assertTrue(s["closed_loop"]["reason"].startswith(
                ("no_progress_at_precision_floor", "remaining_error_below_reversal_resolution")))

    def test_fit_check_and_propose(self):
        session = self.summary["session"]
        code, text = run("check", session)
        self.assertEqual(code, 0, text)
        out = self.root / "refit"
        code, text = run("fit", session, "--out", out, "--holdout-fraction", 0.34, "--seed", 3)
        self.assertEqual(code, 0, text)
        model = json.loads((out / "model.json").read_text())
        report = json.loads((out / "validation.json").read_text())
        self.assertEqual(report["model_id"], model["model_id"])
        obs = next(r for r in SessionReader(Path(session)).records("observation"))
        (out / "obs.json").write_text(json.dumps(obs))
        target = {k: v + (0.8 if k.endswith(".u") else 0.0) for k, v in obs["values"].items()}
        (out / "target.json").write_text(json.dumps(target))
        code, text = run("propose", "--model", out / "model.json", "--report", out / "validation.json",
                         "--observation", out / "obs.json", "--target", out / "target.json",
                         "--now-ns", obs["t_end_ns"] + 1000, "--counts", *([0] * 6), "--direction", *([1] * 6))
        proposal = json.loads(text)
        self.assertIn(proposal["status"], ("move", "zero"))
        self.assertTrue(all(abs(c) <= 64 for c in proposal["counts"]))
        code, text = run("propose", "--model", out / "model.json", "--report", out / "validation.json",
                         "--observation", out / "obs.json", "--target", out / "target.json",
                         "--now-ns", obs["t_end_ns"] + int(60e9))
        self.assertIn("stale_observation", json.loads(text)["reasons"])

    def test_optics_check_and_schema(self):
        now = iso_time(__import__("time").time_ns())
        good = self.root / "cam_a-optics.json"
        good.write_text(json.dumps(filled_receipt("cam_a", now)))
        bad = self.root / "cam_a-auto.json"
        bad.write_text(json.dumps(filled_receipt("cam_a", now, focus_mode="auto")))
        self.assertEqual(run("optics", "check", good, "--camera-id", "cam_a")[0], 0)
        code, text = run("optics", "check", bad, "--camera-id", "cam_a")
        self.assertEqual(code, 1)
        self.assertIn("measurement gate: focus_mode_auto", json.loads(text)["problems"])
        code, text = run("optics", "check", EXAMPLES / "operator-optics.example.json", "--camera-id", "cam_a")
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(text)["ok"])
        code, text = run("schema")
        self.assertEqual(json.loads(text)["$id"], "gpobs/1")

    def test_shipped_template_refused_before_any_capture(self):
        root = self.root / "refused"
        code, out, err = run_err("capture", "--config", EXAMPLES / "cameras.example.json", "--root", root,
                                 "--measure", "--seconds", 0.1)
        self.assertEqual(code, 2)
        self.assertIn("capture refused", err)
        self.assertIn("cameras[0].unique_id still holds FILL_ME", err)
        self.assertFalse(root.exists())
        code, _, err = run_err("capture", "--config", EXAMPLES / "cameras.example.json", "--root", root,
                               "--seconds", 0.1)
        self.assertEqual(code, 2)                          # a dry capture still needs real unique IDs
        code, text = run("validate-config", EXAMPLES / "cameras.example.json", "--measurement")
        self.assertEqual(code, 1)
        self.assertGreater(len(json.loads(text)["problems"]), 20)

    def test_cameras_new_since(self):
        before = {"source": "test", "devices": [{"unique_id": "u1", "name": "FaceTime"}, {"unique_id": "u2"}]}
        after = {"source": "test", "devices": before["devices"] + [{"unique_id": "0xA", "name": "K20UH",
                                                                    "model_id": "m"}]}
        saved = self.root / "cams-none.json"
        with mock.patch.object(helper_stream, "list_cameras", return_value=before):
            self.assertEqual(run("cameras", "--save", saved)[0], 0)
        with mock.patch.object(helper_stream, "list_cameras", return_value=after):
            code, text = run("cameras", "--new-since", saved)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(text)["new_devices"], [{"unique_id": "0xA", "name": "K20UH", "model_id": "m"}])
        two = {"source": "test", "devices": after["devices"] + [{"unique_id": "0xB"}]}
        with mock.patch.object(helper_stream, "list_cameras", return_value=two):
            self.assertEqual(run("cameras", "--new-since", saved)[0], 1)      # ambiguous: repeat the step

    @unittest.skipUnless(helper_stream.BINARY.exists(), "capture helper not built (helper/build.sh --adhoc)")
    def test_operator_flow_dry_capture_format_report_then_measurement(self):
        setup = self.root / "setup"
        setup.mkdir()
        sessions = self.root / "flow-sessions"
        real = helper_stream.HelperSource

        def synthetic(camera_id, unique_id, *a, **k):
            return real.synthetic(camera_id, frames=40, width=64, height=36, fps=60, drop_at=(30,), mode="exec")

        # 1. Unique IDs only: a dry capture runs, measurement is refused.
        data = json.loads((EXAMPLES / "cameras.example.json").read_text())
        for i, cam in enumerate(data["cameras"]):
            cam["unique_id"] = f"synthetic-{cam['camera_id']}"
        cfg = setup / "cameras.json"
        cfg.write_text(json.dumps(data, indent=1))
        self.assertEqual(run("validate-config", cfg)[0], 0)
        self.assertEqual(run("validate-config", cfg, "--measurement")[0], 1)
        with mock.patch.object(helper_stream, "HelperSource", side_effect=synthetic):
            code, text = run("capture", "--config", cfg, "--root", sessions, "--label", "format-check",
                             "--seconds", 4.0, "--store", "none", "--launch", "exec", "--request-width", 64,
                             "--request-height", 36, "--request-fps", 60)
        self.assertEqual(code, 0, text)
        dry = Path(text.splitlines()[0])
        self.assertFalse(any(f["measurement"] for f in SessionReader(dry).records("frame")))
        # 2. The format report measures what arrived.
        code, text = run("format-report", dry)
        self.assertEqual(code, 0, text)
        report = json.loads(text)
        for cam in ("cam_a", "cam_b"):
            vf = report[cam]["verified_format"]
            self.assertEqual((vf["width"], vf["height"], vf["pixel_format"], vf["chroma"]), (64, 36, "420v", False))
            median_ms = report[cam]["evidence"]["median_interval_ms"]
            self.assertAlmostEqual(vf["fps"], 1000 / median_ms, delta=0.01)     # the measured rate, not a nominal one
            self.assertGreaterEqual(median_ms, 1000 / 60 - 0.5)                 # paced no faster than requested
            self.assertEqual(report[cam]["evidence"]["frames"], 39)
            self.assertEqual(report[cam]["evidence"]["frame_gaps"].get("source_notice"), 1)
        # 3. Fill the rest: measured format, receipts, the real clock check.
        now = iso_time(__import__("time").time_ns())
        for cam in data["cameras"]:
            cid = cam["camera_id"]
            cam["verified_format"].update(report[cid]["verified_format"])
            cam.update(name="GPOCapture synthetic", position=f"test stage {cid}", require_native_4k=False)
            cam["optics"].update(source="operator", receipt=f"{cid}-optics.json", visca=None)
            (setup / f"{cid}-optics.json").write_text(json.dumps(filled_receipt(cid, now)))
        code, text = run("clock-check", "--out", setup / "clock-check.json")
        self.assertEqual(code, 0, text)
        data["clock_check"]["receipt"] = "clock-check.json"
        cfg.write_text(json.dumps(data, indent=1))
        code, text = run("validate-config", cfg, "--measurement")
        self.assertEqual(code, 0, text)
        # 4. Measurement capture.
        with mock.patch.object(helper_stream, "HelperSource", side_effect=synthetic):
            code, text = run("capture", "--config", cfg, "--root", sessions, "--label", "measure",
                             "--seconds", 4.0, "--measure", "--store", "all", "--launch", "exec")
        self.assertEqual(code, 0, text)
        reader = SessionReader(Path(text.splitlines()[0]))
        self.assertTrue(reader.integrity().ok, reader.integrity().problems)
        frames = reader.records("frame")
        self.assertEqual(len(frames), 2 * 39)
        in_window = [f for f in frames if f["window_id"]]
        self.assertTrue(in_window and all(f["measurement"] and f["subtype"] == "420v" for f in in_window))
        self.assertTrue(reader.records("measurement_end")[-1]["valid"])
        self.assertEqual(reader.manifest["config"]["purpose"], "measurement")
        self.assertTrue(reader.manifest["config"]["clock_check"]["passed"])
        optics = reader.records("optics")
        self.assertTrue(all(r["gate_ok"] for r in optics))
        self.assertEqual({r["state"]["extra"]["recorded_by"] for r in optics}, {"synthetic test"})


if __name__ == "__main__":
    unittest.main()
