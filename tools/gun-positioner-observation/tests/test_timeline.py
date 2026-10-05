"""Frames and moves on one monotonic timeline; controller clock mapping; two-camera pairing."""

import unittest

import numpy as np

from support import tmpdir

from gpobs.clock import ClockExchange, ClockMap, FakeClock
from gpobs.dataset import SessionReader, SessionWriter
from gpobs.moves import MoveRecorder
from gpobs.simulation import SimulatedMechanism, SimulatedPositioner, default_truth
from gpobs.timeline import clock_map_from_records, label_frames, move_intervals, pair_frames, settled_frames


def frame(cam, seq, pts=None, recv=None):
    return {"camera_id": cam, "seq": seq, "device_pts_ns": pts, "recv_mono_ns": recv if recv is not None else pts}


class Alignment(unittest.TestCase):
    def test_frames_labelled_against_receipts(self):
        clock = FakeClock(start_ns=10_000_000_000)
        backend = SimulatedPositioner(SimulatedMechanism(default_truth()), clock, profile="loaded-development")
        with SessionWriter(tmpdir("timeline"), "timeline", clock) as w:
            rec = MoveRecorder(backend, w, clock)
            clock.advance_ns(200_000_000)
            rec.execute([100, 0, 0, 0, 0, 0], "probe_jog")
            clock.advance_ns(1_000_000_000)
            rec.execute([0, -100, 0, 0, 0, 0], "probe_jog")
        records = SessionReader(w.path).records()
        moves = move_intervals(records)
        self.assertEqual([m["status"] for m in moves], ["done", "done"])
        m0, m1 = moves
        settle = 300_000_000
        t = lambda ns: frame("cam_a", ns, pts=ns)
        frames = [t(m0["issued_ns"] - 1), t(m0["issued_ns"] + 1), t(m0["complete_ns"] - 1),
                  t(m0["complete_ns"] + 1), t(m0["complete_ns"] + settle - 1), t(m0["complete_ns"] + settle),
                  t(m1["issued_ns"] - 1), t(m1["issued_ns"])]
        labels = label_frames(frames, moves, settle)
        got = [labels[("cam_a", f["seq"])][0] for f in frames]
        self.assertEqual(got, ["before_first_move", "moving", "moving", "settling", "settling", "settled",
                               "settled", "moving"])
        self.assertEqual(len(settled_frames(frames, moves, m0["cmd_id"], settle)), 2)
        # Without presentation times, receipt time minus the latency allowance is the capture estimate.
        late = frame("cam_b", 99, pts=None, recv=m0["complete_ns"] + settle + 50_000_000)
        self.assertEqual(label_frames([late], moves, settle, latency_allowance_ns=100_000_000)[("cam_b", 99)][0],
                         "settling")

    def test_clock_map_recovers_controller_clock(self):
        rng = np.random.default_rng(4)
        offset_us, rate = -42_000_000, 1 + 55e-6

        def controller_us(host_ns):
            return host_ns / 1000 * rate + offset_us

        exchanges = []
        for k in range(200):
            send = 1_000_000_000 + k * 100_000_000
            up, down = rng.uniform(0.2e6, 3e6), rng.uniform(0.2e6, 3e6)
            exchanges.append(ClockExchange(send, int(send + up + down), int(controller_us(send + up))))
        cmap = ClockMap.fit(exchanges)
        for host_ns in (2_500_000_000, 15_000_000_000, 21_000_000_000):
            self.assertLessEqual(abs(cmap.to_host_ns(controller_us(host_ns)) - host_ns), cmap.uncertainty_ns)
        self.assertLess(cmap.uncertainty_ns, 3.5e6)
        self.assertAlmostEqual(1 / cmap.rate, rate, delta=3e-5)
        with self.assertRaises(ValueError):
            ClockMap.fit(exchanges[:1])

    def test_clock_map_from_session_records(self):
        clock = FakeClock()
        backend = SimulatedPositioner(SimulatedMechanism(default_truth()), clock)
        with SessionWriter(tmpdir("cmap"), "cmap", clock) as w:
            rec = MoveRecorder(backend, w, clock)
            for _ in range(5):
                rec.execute([10, 0, 0, 0, 0, 0], "probe_jog")
        records = SessionReader(w.path).records()
        cmap = clock_map_from_records(records, boot=backend.boot)
        done = [r for r in records if r["kind"] == "move_complete"][-1]
        # The simulator completes 30 ms + latency before the completion receipt.
        self.assertLess(cmap.to_host_ns(done["controller_time_us"]), done["complete_mono_ns"])
        self.assertGreater(cmap.to_host_ns(done["controller_time_us"]), done["complete_mono_ns"] - 60_000_000)

    def test_pairing_two_cameras(self):
        a = [frame("cam_a", i, pts=1_000_000_000 + i * 33_333_333) for i in range(10)]
        b = [frame("cam_b", i, pts=1_000_000_000 + i * 33_333_333 + 4_000_000) for i in range(10) if i != 5]
        pairs = pair_frames(a, b, max_skew_ns=8_000_000)
        self.assertEqual(len(pairs), 9)
        self.assertTrue(all(abs(skew) <= 8_000_000 for _, _, skew in pairs))
        self.assertNotIn(5, [fa["seq"] for fa, _, _ in pairs])
        self.assertEqual(len({fb["seq"] for _, fb, _ in pairs}), 9)


if __name__ == "__main__":
    unittest.main()
