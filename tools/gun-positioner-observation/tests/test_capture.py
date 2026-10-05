"""Capture: receipt stamps, sequence numbers, drop evidence, sizes, optics-gated measurement windows."""

import json
import struct
import unittest

import numpy as np

from support import filled_receipt, tmpdir

from gpobs import helper_stream
from gpobs.capture import (ArraySource, CameraCapture, CameraObserver, CameraSpec, CaptureSession, MeasurementRefused,
                           RawFrame, SourceDrop, StorePolicy)
from gpobs.clock import Clock, FakeClock
from gpobs.dataset import SessionReader, SessionWriter
from gpobs.features import AimingDot, SeamLine, WireTip
from gpobs.config import iso_time, load_receipt
from gpobs.optics import OpticsProvider, OpticsState
from gpobs.simulation import render_scene


def jpeg_header(width: int, height: int) -> bytes:
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 17, 8, height, width, 3) + bytes([1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1])
    sos = b"\xff\xda" + struct.pack(">H", 12) + bytes([3, 1, 0, 2, 0x11, 3, 0x11, 0, 0x3F, 0])
    return b"\xff\xd8" + sof + sos + b"\x00" * 16 + b"\xff\xd9"


def locked_state(camera_id, clock, zoom=0x2000, source="visca_inquiry", tracking="off_commanded"):
    return OpticsState(camera_id, source, clock.monotonic_ns(), focus_mode="manual", exposure_mode="manual",
                       tracking=tracking, zoom_position=zoom, focus_position=0x0300, pan_position=16, tilt_position=32)


class Drops(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.writer = SessionWriter(tmpdir("drops"), "drops", self.clock)
        spec = CameraSpec("cam_a", "u1", width=64, height=36, codec="gray8", require_native_4k=False)
        self.cap = CameraCapture(spec, None, self.writer, self.clock, StorePolicy("none"))

    def tearDown(self):
        self.writer.close()

    def feed(self, source_seq, pts_ns):
        self.clock.advance_ns(5_000_000)
        return self.cap.process(RawFrame(np.zeros((36, 64), np.uint8), "gray8", 64, 36, source_seq, pts_ns))

    def test_sequence_receipt_and_gap_evidence(self):
        interval = 33_333_333
        pts = [0, 1, 2, 5, 6]                      # source frames 3 and 4 missing
        for k, s in enumerate(pts):
            self.feed(s + 1, 1_000_000_000 + s * interval)
        self.cap.process(SourceDrop(1_000_000_000 + 7 * interval, "late"))
        self.feed(9, 1_000_000_000 + 8 * interval)  # frame 8 (seq 8) reported dropped above
        records = SessionReader(self.writer.path).records()
        frames = [r for r in records if r["kind"] == "frame"]
        self.assertEqual([f["seq"] for f in frames], list(range(6)))
        recv = [f["recv_mono_ns"] for f in frames]
        self.assertEqual(recv, sorted(recv))
        self.assertTrue(all(f["recv_wall_ns"] > 0 for f in frames))
        gaps = [(g["evidence"], g["missing_estimate"]) for g in records if g["kind"] == "frame_gap"]
        self.assertIn(("source_seq", 2), gaps)
        self.assertIn(("pts_gap", 2), gaps)
        self.assertIn(("source_notice", 1), gaps)
        self.assertIn(("source_seq", 1), gaps)       # 7 -> 9
        notice_gap = [g for g in records if g["kind"] == "frame_gap" and g["evidence"] == "pts_gap"][-1]
        self.assertEqual(notice_gap["detail"]["explained_by_source_notices"], 1)


class SyntheticDrops(unittest.TestCase):
    def test_drop_notice_precedes_frame_and_explains_pts_gap(self):
        clock = FakeClock()
        with SessionWriter(tmpdir("synthdrops"), "synthdrops", clock) as w:
            src = ArraySource("cam_a", lambda: np.zeros((4, 6), np.uint8), clock, drop_every=3)
            cap = CameraCapture(CameraSpec("cam_a", "u", width=6, height=4, require_native_4k=False), src, w,
                                clock, StorePolicy("none"))
            for _ in range(8):
                cap.process(src.read(1.0))
        records = SessionReader(w.path).records()
        kinds = [r["kind"] if r["kind"] != "frame_gap" else r["evidence"] for r in records
                 if r["kind"] in ("frame", "frame_gap")]
        self.assertEqual(kinds[:5], ["frame", "frame", "source_notice", "pts_gap", "frame"])
        self.assertNotIn("source_seq", kinds)                  # delivered frames are numbered without gaps
        gap = next(r for r in records if r.get("evidence") == "pts_gap")
        self.assertEqual((gap["missing_estimate"], gap["detail"]["explained_by_source_notices"]), (1, 1))


class Sizes(unittest.TestCase):
    def test_native_4k_and_size_checks(self):
        clock = FakeClock()
        with SessionWriter(tmpdir("sizes"), "sizes", clock) as w:
            cap = CameraCapture(CameraSpec("cam_a", "u1"), None, w, clock, StorePolicy("none"))
            jpeg4k = cap.process(RawFrame(jpeg_header(3840, 2160), "jpeg"))
            jpeg_hd = cap.process(RawFrame(jpeg_header(1920, 1080), "jpeg"))
            gray = cap.process(RawFrame(np.zeros((2160, 3840), np.uint8), "gray8"))
            nv12 = cap.process(RawFrame(bytes(3840 * 2160 * 3 // 2), "nv12", 3840, 2160))
            bad = cap.process(RawFrame(bytes(100), "nv12", 3840, 2160))
            junk = cap.process(RawFrame(b"not a jpeg", "jpeg"))
        self.assertTrue(jpeg4k["native_4k"] and jpeg4k["dims_verified"] and not jpeg4k["excluded_reasons"])
        self.assertFalse(jpeg_hd["native_4k"])
        self.assertIn("not_native_4k", jpeg_hd["excluded_reasons"])
        self.assertTrue(gray["native_4k"] and nv12["native_4k"])
        self.assertIn("nv12_size_mismatch", bad["excluded_reasons"])
        self.assertTrue(any(r.startswith("unreadable_jpeg") for r in junk["excluded_reasons"]))


class Windows(unittest.TestCase):
    def make(self, name, provider, on_unknown="refuse"):
        self.clock = getattr(self, "clock", None) or FakeClock()
        self.writer = SessionWriter(tmpdir("windows"), name, self.clock)
        caps = []
        for cam in ("cam_a", "cam_b"):
            src = ArraySource(cam, lambda: np.full((24, 32), 50, np.uint8), self.clock)
            caps.append(CameraCapture(CameraSpec(cam, f"u-{cam}", width=32, height=24, codec="gray8",
                                                 require_native_4k=False), src, self.writer, self.clock))
        self.session = CaptureSession(self.writer, caps, provider, self.clock, on_unknown=on_unknown, synchronous=True)
        self.session.start()

    def tearDown(self):
        self.session.stop()
        self.writer.close()

    def test_unknown_optics_refuse_measurement(self):
        self.make("refuse", OpticsProvider())
        with self.assertRaises(MeasurementRefused) as cm:
            with self.session.measurement("observation"):
                pass
        self.assertIn("no_optics_record", cm.exception.reasons["cam_a"])
        refused = SessionReader(self.writer.path).records("measurement_refused")
        self.assertEqual(len(refused), 1)

    def test_unknown_optics_logged_not_measurement(self):
        self.clock = FakeClock()
        provider = OpticsProvider()
        provider.set_state(OpticsState("cam_a", "visca_inquiry", self.clock.monotonic_ns(), focus_mode="auto",
                                       exposure_mode="unknown", tracking="unknown"))
        provider.set_state(locked_state("cam_b", self.clock))
        self.make("log", provider, on_unknown="log")
        with self.session.measurement("observation") as w:
            got = self.session.collect(w, 3)
        frames = [r for r, _ in got["cam_a"]]
        self.assertTrue(all(not f["measurement"] for f in frames))
        self.assertTrue(any("optics:autofocus_state_unknown" in r or "optics:focus_mode_auto" in r
                            for f in frames for r in f["excluded_reasons"]))
        self.assertTrue(any("optics:auto_exposure_state_unknown" in r for f in frames for r in f["excluded_reasons"]))
        end = SessionReader(self.writer.path).records("measurement_end")[-1]
        self.assertFalse(end["valid"])

    def test_verified_optics_store_measurement_frames(self):
        self.clock = FakeClock()
        provider = OpticsProvider()
        for cam in ("cam_a", "cam_b"):
            provider.set_reader(cam, lambda c=cam: locked_state(c, self.clock))
        self.make("verified", provider)
        with self.session.measurement("observation", "t1") as w:
            got = self.session.collect(w, 4)
        self.assertTrue(w.valid)
        reader = SessionReader(self.writer.path)
        frames = [r for r, _ in got["cam_a"]]
        self.assertTrue(all(f["measurement"] and f["stored"] for f in frames))
        self.assertEqual(reader.load_frame(frames[0]).shape, (24, 32))
        contexts = [r["context"] for r in reader.records("optics")]
        self.assertEqual(contexts.count("window_start"), 2)
        self.assertEqual(contexts.count("window_end"), 2)
        self.assertTrue(all(f["optics_id"] for f in frames))

    def test_optics_change_invalidates_window(self):
        self.clock = FakeClock()
        zooms = iter([0x2000, 0x2000, 0x2400])
        provider = OpticsProvider()
        provider.set_reader("cam_a", lambda: locked_state("cam_a", self.clock, zoom=next(zooms)))
        provider.set_reader("cam_b", lambda: locked_state("cam_b", self.clock))
        self.make("changed", provider)
        with self.session.measurement("observation") as w:
            self.session.collect(w, 2)
        self.assertFalse(w.valid)
        end = SessionReader(self.writer.path).records("measurement_end")[-1]
        self.assertEqual(end["changed_fields"]["cam_a"]["zoom_position"], [0x2000, 0x2400])
        self.assertIn("optics_changed_during_window", end["reasons"])

    def test_receipt_optics_and_staleness(self):
        self.clock = FakeClock()
        path = tmpdir("receipt-windows") / "cam_a-optics.json"
        recorded = iso_time(self.clock.wall_ns() - int(3600e9))          # read an hour ago
        path.write_text(json.dumps(filled_receipt("cam_a", recorded)))
        receipt = load_receipt(path, "cam_a", self.clock.monotonic_ns(), self.clock.wall_ns())
        self.assertEqual(receipt.problems, [])
        provider = OpticsProvider()
        provider.set_state(receipt.state)
        provider.set_state(locked_state("cam_b", self.clock))
        self.make("operator", provider)
        with self.session.measurement("observation") as w:
            self.session.collect(w, 1)
        self.assertTrue(w.valid)
        rec = [r for r in SessionReader(self.writer.path).records("optics") if r["camera_id"] == "cam_a"][0]
        self.assertIn("operator_entered_not_read_back", rec["warnings"])
        self.assertEqual(rec["state"]["extra"]["lens_attachment"], "Raynox DCR-250")
        self.assertEqual(rec["state"]["extra"]["recorded_at"], recorded)
        self.clock.advance_ns(int(11.5 * 3600e9))                       # receipt now 12.5 h old
        with self.assertRaises(MeasurementRefused) as cm:
            with self.session.measurement("observation"):
                pass
        self.assertIn("optics_record_stale", cm.exception.reasons["cam_a"])


class ObserverOnImages(unittest.TestCase):
    """Rendered frames through capture, measurement windows, extractors and averaging."""

    def test_observation_recovers_rendered_features(self):
        clock = FakeClock()
        truth = {"cam_a": {"dot": (101.3, 62.7), "wire": (70.4, 58.2), "approach": 180.0, "wire_roi": (20, 40, 75, 40)},
                 "cam_b": {"dot": (88.6, 71.1), "wire": (120.2, 66.9), "approach": 0.0, "wire_roi": (100, 40, 80, 40)}}
        rng = np.random.default_rng(1)

        def renderer(cam):
            t = truth[cam]
            return lambda: render_scene(180, 120, dot=t["dot"], wire_tip=t["wire"], wire_angle_deg=t["approach"],
                                        seam=(90.0, 95.0), noise=1.5, rng=rng)

        with SessionWriter(tmpdir("observer"), "observer", clock) as w:
            provider = OpticsProvider()
            caps = []
            for cam in truth:
                provider.set_state(locked_state(cam, clock))
                caps.append(CameraCapture(CameraSpec(cam, cam, width=180, height=120, codec="gray8",
                                                     require_native_4k=False),
                                          ArraySource(cam, renderer(cam), clock), w, clock))
            session = CaptureSession(w, caps, provider, clock, synchronous=True)
            session.start()
            ex = {cam: [AimingDot(roi=(75, 45, 40, 40)),
                        WireTip(roi=t["wire_roi"], approach_deg=t["approach"]),
                        SeamLine(roi=(0, 85, 180, 25))] for cam, t in truth.items()}
            observer = CameraObserver(session, ex, w, clock, frames_per_camera=6)
            obs = observer.observe("t1", None, [], clock.monotonic_ns())
            session.stop()
        for cam, t in truth.items():
            self.assertAlmostEqual(obs.values[f"{cam}.dot.u"], t["dot"][0], delta=0.1)
            self.assertAlmostEqual(obs.values[f"{cam}.dot.v"], t["dot"][1], delta=0.1)
            self.assertAlmostEqual(obs.values[f"{cam}.wire.u"], t["wire"][0], delta=0.3)
            self.assertAlmostEqual(obs.values[f"{cam}.wire.v"], t["wire"][1], delta=0.3)
            self.assertAlmostEqual(obs.values[f"{cam}.seam.rho"], 95.0 - 97.0, delta=0.3)   # about the ROI centre
            self.assertGreater(obs.confidence[f"{cam}.dot.u"], 0.5)
            self.assertLess(obs.sigma[f"{cam}.dot.u"], 0.1)


@unittest.skipUnless(helper_stream.BINARY.exists(), "capture helper not built (helper/build.sh --adhoc)")
class HelperIntegration(unittest.TestCase):
    def test_threaded_capture_from_helper_stream(self):
        clock = Clock()
        with SessionWriter(tmpdir("helper"), "helper", clock) as w:
            src = helper_stream.HelperSource.synthetic("cam_a", frames=12, width=64, height=36, fps=60,
                                                       codec="gray8", drop_at=(4, 5))
            cap = CameraCapture(CameraSpec("cam_a", "synthetic", width=64, height=36, codec="gray8", fps=60,
                                           require_native_4k=False), src, w, clock, StorePolicy("all"))
            provider = OpticsProvider()
            provider.set_state(locked_state("cam_a", clock))
            session = CaptureSession(w, [cap], provider, clock)
            session.start()
            for t in cap._threads:
                t.join(10)
            session.stop()
        reader = SessionReader(w.path)
        frames = reader.records("frame")
        self.assertEqual(len(frames), 10)
        self.assertEqual([f["source_seq"] for f in frames], list(range(1, 11)))
        for f in frames:
            self.assertLessEqual(f["source_host_ns"], f["recv_mono_ns"])   # helper stamp precedes receipt
            self.assertLessEqual(f["device_pts_ns"], f["source_host_ns"])
        notices = [g for g in reader.records("frame_gap") if g["evidence"] == "source_notice"]
        self.assertEqual(len(notices), 2)
        self.assertEqual(reader.load_frame(frames[0]).shape, (36, 64))
        self.assertTrue(reader.integrity().ok, reader.integrity().problems)

    def test_clock_agreement(self):
        result = helper_stream.clock_check()
        self.assertTrue(result["uptime_raw_within_bracket"])
        self.assertTrue(result["host_time_clock_within_bracket"])


if __name__ == "__main__":
    unittest.main()
