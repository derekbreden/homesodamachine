"""Contact-probe channels against an angle-indexed cold baseline, with a table angle and cool reference."""

import unittest

import numpy as np

from support import tmpdir

from gpobs import validation
from gpobs.clock import FakeClock
from gpobs.dataset import SessionReader, SessionWriter
from gpobs.liveweld import (ChannelLogger, ColdBaseline, angle_at, compare, lap_of, table_angles,
                            unwrap_counts)

LAP_S = 48.6                          # 8 mm/s bead travel: one table revolution
COUNTS_PER_REV = 14_400               # e.g. an encoder of 14,400 counts per table revolution


def runout(theta_deg):
    th = np.radians(theta_deg)
    return 0.12 * np.cos(th - 0.4) + 0.03 * np.cos(2 * th + 1.0) + 0.01 * np.sin(3 * th)


def record_laps(writer, clock, laps, hot_lap=None, rng=None):
    rng = rng or np.random.default_rng(0)
    log = ChannelLogger(writer, clock)
    t0 = clock.monotonic_ns()
    probe_t, probe_v = [], []
    for k in range(int(laps * LAP_S * 50)):                 # 50 Hz probe, 100 Hz encoder
        for _ in range(2):
            clock.advance_ns(10_000_000)
            t = clock.monotonic_ns()
            angle = (t - t0) / 1e9 / LAP_S * 360.0
            log.table(int(round(angle / 360.0 * COUNTS_PER_REV)) % COUNTS_PER_REV, COUNTS_PER_REV, "encoder", t)
        t = clock.monotonic_ns()
        angle = (t - t0) / 1e9 / LAP_S * 360.0
        lap = int(angle // 360)
        mount_drift = 0.0
        value = 5.0 + runout(angle) + 0.003 * rng.normal()
        if hot_lap is not None and lap == hot_lap:
            mount_drift = 0.02 * ((angle % 360) / 360.0)        # probe mount warming through the lap
            local = (angle % 360)
            value += mount_drift + (0.05 if 100 <= local <= 140 else 0.0)
            log.cool_reference("mount", 1.0 + mount_drift + 0.001 * rng.normal(), "mm", "contact_probe", t)
        elif hot_lap is not None:
            log.cool_reference("mount", 1.0 + 0.001 * rng.normal(), "mm", "contact_probe", t)
        log.probe("radial", value, "mm", "contact_probe", t)
        probe_t.append(t)
        probe_v.append(value)
    return np.array(probe_t), np.array(probe_v)


class ColdBaselineTests(unittest.TestCase):
    def test_wrap_and_interpolation(self):
        counts = [14_000, 14_390, 5, 300, 14_350]
        np.testing.assert_array_equal(unwrap_counts(counts, 14_400), [14_000, 14_390, 14_405, 14_700, 14_350])
        t = np.array([0, 100, 200, 400], dtype=np.int64)
        a = np.array([0.0, 10.0, 20.0, 40.0])
        got = angle_at([50, 150, 300, 500, -1], t, a, max_gap_ns=150)
        self.assertEqual(got[:2].tolist(), [5.0, 15.0])
        self.assertTrue(np.isnan(got[2]) and np.isnan(got[3]) and np.isnan(got[4]))   # gap, and no extrapolation

    def test_baseline_fit_validated_by_lap_and_hot_deviation(self):
        clock = FakeClock()
        with SessionWriter(tmpdir("liveweld"), "cold-laps", clock) as w:
            probe_t, probe_v = record_laps(w, clock, laps=5)
            hot_t, hot_v = record_laps(w, clock, laps=1, hot_lap=0)
        records = SessionReader(w.path).records()
        enc_t, enc_angle = table_angles(records, "encoder")
        self.assertGreater(len(enc_t), 1000)
        cold = [r for r in records if r["kind"] == "probe_sample" and r["sample_mono_ns"] <= probe_t[-1]]
        t = np.array([r["sample_mono_ns"] for r in cold])
        v = np.array([r["value"] for r in cold])
        angle = angle_at(t, enc_t, enc_angle)
        laps = lap_of(angle - angle[0])
        train, hold = validation.split_trials([f"lap-{k}" for k in sorted(set(laps.tolist()))], 0.4, seed=2)
        train_mask = np.isin([f"lap-{k}" for k in laps], train)
        base = ColdBaseline.fit("radial", angle[train_mask], v[train_mask], laps[train_mask], harmonics=6)
        held = base.score(angle[~train_mask], v[~train_mask])
        self.assertLess(held["rms"], 0.006)                     # probe noise is 0.003 mm
        self.assertLess(base.residual_sigma, 0.005)
        # A hot lap: thermal bump 100–140° plus probe-mount drift seen by the cool reference.
        cool = [r for r in records if r["kind"] == "cool_reference" and r["sample_mono_ns"] > probe_t[-1]]
        ct = np.array([r["sample_mono_ns"] for r in cool])
        cv = np.array([r["value"] for r in cool])
        out = compare(hot_t, hot_v, enc_t, enc_angle, base, ct, cv)
        local = np.mod(out["angle_deg"], 360)
        bump = (local > 105) & (local < 135)
        quiet = (local < 90) | (local > 150)
        self.assertGreater(np.median(out["corrected"][bump]), 0.04)
        self.assertLess(np.abs(np.median(out["corrected"][quiet])), 0.006)
        self.assertGreater(np.max(np.abs(out["deviation"][quiet])), 0.012)   # uncorrected drift is visible

    def test_coverage_required(self):
        a = np.linspace(0, 200, 400)
        with self.assertRaises(ValueError):
            ColdBaseline.fit("axial", a, runout(a), np.zeros(400, int))

    def test_channel_vocabularies(self):
        clock = FakeClock()
        with SessionWriter(tmpdir("liveweld2"), "vocab", clock) as w:
            log = ChannelLogger(w, clock)
            with self.assertRaises(ValueError):
                log.probe("tangential", 1.0)
            with self.assertRaises(ValueError):
                log.table(10, 100, source="usb_arrival_time")
            log.table(10, 100, source="camera_fiducial")
            log.probe("axial", 0.5)


if __name__ == "__main__":
    unittest.main()
