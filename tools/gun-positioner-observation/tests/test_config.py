"""Shipped templates are refused for measurement; a filled synthetic setup passes; every gap is named."""

import json
import time
import unittest

from support import EXAMPLES, clock_receipt_for, filled_receipt, tmpdir, write_filled_setup

from gpobs.config import ConfigError, iso_time, load_config, load_receipt, placeholders, validate

TEMPLATE = EXAMPLES / "cameras.example.json"
RECEIPT_TEMPLATE = EXAMPLES / "operator-optics.example.json"


class ShippedTemplates(unittest.TestCase):
    def test_cameras_template_refused_for_measurement_and_dry_capture(self):
        with self.assertRaises(ConfigError) as cm:
            validate(TEMPLATE, "measurement")
        text = "\n".join(cm.exception.problems)
        for path in ("clock_check.receipt", "cameras[0].unique_id", "cameras[1].unique_id", "cameras[0].position",
                     "cameras[1].optics.source", "cameras[0].optics.visca.host"):
            self.assertIn(f"{path} still holds FILL_ME", text)
        for key in ("width", "height", "fps", "pixel_format", "chroma", "measured_at", "measured_with"):
            self.assertIn(f"cameras[0].verified_format.{key} is null", text)
            self.assertIn(f"cameras[1].verified_format.{key} is null", text)
        with self.assertRaises(ConfigError) as cm:
            validate(TEMPLATE, "dry")
        self.assertTrue(all("unique_id" in p for p in cm.exception.problems))

    def test_template_never_states_a_verified_format(self):
        data = json.loads(TEMPLATE.read_text())
        for cam in data["cameras"]:
            vf = {k: v for k, v in cam["verified_format"].items() if not k.startswith("_")}
            self.assertEqual(set(vf), {"width", "height", "fps", "pixel_format", "chroma", "measured_at",
                                       "measured_with"})
            self.assertTrue(all(v is None for v in vf.values()), vf)

    def test_receipt_template_refused(self):
        receipt = load_receipt(RECEIPT_TEMPLATE, "cam_a")
        self.assertIsNone(receipt.state)
        fields = {"camera_id", "recorded_at", "recorded_by", "method", "focus_mode", "exposure_mode", "tracking",
                  "zoom", "focus", "shutter", "iris", "gain", "white_balance", "lens_attachment"}
        self.assertEqual(set(placeholders(receipt.data)), fields)
        self.assertEqual(len(receipt.problems), len(fields))

    def test_templates_are_documented_json(self):
        for path in (TEMPLATE, RECEIPT_TEMPLATE):
            data = json.loads(path.read_text())
            self.assertEqual(data["format_version"], 1)
            self.assertIn("_about", data)


class FilledSetup(unittest.TestCase):
    def setUp(self):
        self.dir = tmpdir(f"setup-{self.id().split('.')[-1]}")
        self.helper = self.dir / "stand-in-helper"
        self.helper.write_bytes(b"stand-in helper build")
        self.path = write_filled_setup(self.dir, self.helper)

    def problems(self, purpose="measurement"):
        return load_config(self.path, self.helper).problems(purpose)

    def edit(self, fn):
        data = json.loads(self.path.read_text())
        fn(data)
        self.path.write_text(json.dumps(data))

    def edit_receipt(self, which, **changes):
        p = self.dir / f"{which}-optics.json"
        data = json.loads(p.read_text())
        data.update(changes)
        p.write_text(json.dumps(data))

    def test_filled_synthetic_setup_passes(self):
        cfg = validate(self.path, "measurement", self.helper)
        self.assertEqual([c.camera_id for c in cfg.cameras], ["cam_a", "cam_b"])
        self.assertEqual(cfg.cameras[0].codec, "gray8")
        self.assertEqual(cfg.cameras[0].verified_format["width"], 3840)
        state = cfg.cameras[1].receipt.state
        self.assertEqual((state.focus_mode, state.exposure_mode, state.tracking), ("manual", "manual", "off_operator"))
        self.assertEqual(state.zoom_position, 8192)
        self.assertEqual(state.extra["displayed"]["shutter"], "1/250")
        self.assertEqual(cfg.receipt_max_age_s, 12 * 3600)

    def test_each_gap_refuses_measurement(self):
        cases = {
            "placeholder back in a note-free field": lambda d: d["cameras"][1].update(position="FILL_ME: later"),
            "verified width unfilled": lambda d: d["cameras"][0]["verified_format"].update(width=None),
            "verified fps not a number": lambda d: d["cameras"][0]["verified_format"].update(fps="30"),
            "unknown pixel format": lambda d: d["cameras"][0]["verified_format"].update(pixel_format="avc1"),
            "native 4K required but 1080p measured":
                lambda d: d["cameras"][0]["verified_format"].update(width=1920, height=1080),
            "measured_at in the future":
                lambda d: d["cameras"][0]["verified_format"].update(measured_at="2099-01-01T00:00:00+00:00"),
            "duplicate unique id": lambda d: d["cameras"][1].update(unique_id=d["cameras"][0]["unique_id"]),
            "missing clock receipt": lambda d: d["clock_check"].update(receipt="no-such-file.json"),
            "receipt for operator source missing": lambda d: d["cameras"][0]["optics"].update(receipt=None),
            "visca block left with operator source":
                lambda d: d["cameras"][0]["optics"].update(visca={"transport": "serial"}),
            "no optics source": lambda d: d["cameras"][0]["optics"].update(source=None),
            "bad max age": lambda d: d.update(receipt_max_age_hours=0),
        }
        for name, fn in cases.items():
            with self.subTest(name):
                self.path = write_filled_setup(self.dir, self.helper)
                self.edit(fn)
                self.assertTrue(self.problems(), name)
        self.path = write_filled_setup(self.dir, self.helper)
        self.assertEqual(self.problems(), [])

    def test_receipt_gaps_refuse_measurement(self):
        old = iso_time(time.time_ns() - int(13 * 3600e9))
        future = iso_time(time.time_ns() + int(3600e9))
        cases = {"autofocus": dict(focus_mode="auto"), "auto exposure": dict(exposure_mode="full_auto"),
                 "tracking on": dict(tracking="on"), "tracking unknown": dict(tracking="unknown"),
                 "stale": dict(recorded_at=old), "future": dict(recorded_at=future),
                 "no offset": dict(recorded_at="2026-10-05T09:30:00"), "wrong camera": dict(camera_id="cam_b"),
                 "unfilled value": dict(iris=None), "empty recorder": dict(recorded_by=""),
                 "unknown method": dict(method="guess"), "placeholder": dict(zoom="FILL_ME: zoom")}
        for name, change in cases.items():
            with self.subTest(name):
                self.path = write_filled_setup(self.dir, self.helper)
                self.edit_receipt("cam_a", **change)
                problems = self.problems()
                self.assertTrue(any("cameras[0].optics.receipt" in p for p in problems), (name, problems))

    def test_clock_receipt_gaps_refuse_measurement(self):
        failed = clock_receipt_for(self.helper, passed=False)
        other_clock = dict(clock_receipt_for(self.helper), monotonic_implementation="clock_gettime(CLOCK_REALTIME)")
        cases = {"failed check": failed, "other python clock": other_clock}
        for name, receipt in cases.items():
            with self.subTest(name):
                (self.dir / "clock-check.json").write_text(json.dumps(receipt))
                self.assertTrue(any("clock" in p for p in self.problems()), name)
        (self.dir / "clock-check.json").write_text(json.dumps(clock_receipt_for(self.helper)))
        self.assertEqual(self.problems(), [])
        self.helper.write_bytes(b"rebuilt helper")
        self.assertIn("the capture helper changed since the clock check: run clock-check again", self.problems())
        self.helper.unlink()
        self.assertTrue(any("not built" in p for p in self.problems()))

    def test_visca_source(self):
        def serial(d):
            d["cameras"][0]["optics"] = {"source": "visca", "receipt": None,
                                         "visca": {"transport": "serial", "serial_port": "/dev/cu.test", "baud": 9600,
                                                   "host": None, "port": None, "address": 1}}
        self.edit(serial)
        self.assertEqual(self.problems(), [])
        cfg = load_config(self.path, self.helper)
        self.assertEqual(cfg.cameras[0].visca["serial_port"], "/dev/cu.test")
        bad = {"serial with host": {"host": "192.168.5.163"}, "unlisted baud": {"baud": 57600},
               "address 9": {"address": 9}, "tcp with serial fields": {"transport": "tcp", "host": "10.0.0.2",
                                                                       "port": 1259},
               "tcp without host": {"transport": "tcp", "serial_port": None, "baud": None, "port": 1259}}
        for name, change in bad.items():
            with self.subTest(name):
                self.path = write_filled_setup(self.dir, self.helper)
                self.edit(serial)
                self.edit(lambda d: d["cameras"][0]["optics"]["visca"].update(change))
                self.assertTrue(self.problems(), name)
        self.path = write_filled_setup(self.dir, self.helper)
        self.edit(serial)
        self.edit(lambda d: d["cameras"][0]["optics"]["visca"].update(
            transport="udp", serial_port=None, baud=None, host="192.168.5.163", port=1259))
        self.assertEqual(self.problems(), [])

    def test_dry_capture_needs_only_unique_ids(self):
        data = json.loads(TEMPLATE.read_text())
        for i, cam in enumerate(data["cameras"]):
            cam["unique_id"] = f"0x1{i}0000000aaaa0001"
        path = self.dir / "dry.json"
        path.write_text(json.dumps(data))
        cfg = validate(path, "dry", self.helper)
        self.assertTrue(cfg.measurement_problems)
        with self.assertRaises(ConfigError):
            validate(path, "measurement", self.helper)


if __name__ == "__main__":
    unittest.main()
