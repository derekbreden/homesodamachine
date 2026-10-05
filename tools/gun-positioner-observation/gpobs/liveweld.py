"""Live-weld development channels: contact probes against an angle-indexed cold baseline.

Data channels, each a session record with a host receipt stamp:
    probe_sample    channel "radial" or "axial" contact probe reading
    table_encoder   rotator table angle as counts of counts_per_rev; source
                    "encoder" (a dedicated table encoder) or "camera_fiducial"
                    (an angle read from a fiducial in camera frames)
    cool_reference  a reading taken where weld heat does not reach (for
                    example the probe mount against a fixture datum); its change
                    is subtracted from the probe deviations

The rotator's own controller supplies no live phase stream, and USB arrival
times are not used as table angle. A cold baseline is fitted per probe channel
from dry laps (laser off) as a Fourier series in table angle, validated on
held-out laps, and live readings are compared with it at the same angle.

Nothing here observes the weld optically. Camera visibility during emission,
and the optical protection it needs, are not provided by this toolkit.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .clock import Clock

CHANNELS = ("radial", "axial")
ANGLE_SOURCES = ("encoder", "camera_fiducial")


class ChannelLogger:
    def __init__(self, writer, clock: Clock | None = None):
        self.writer, self.clock = writer, clock or Clock()

    def probe(self, channel: str, value: float, units: str = "mm", source: str = "contact_probe",
              sample_mono_ns: int | None = None) -> dict:
        if channel not in CHANNELS:
            raise ValueError(f"probe channel is one of {CHANNELS}")
        t = self.clock.monotonic_ns() if sample_mono_ns is None else sample_mono_ns
        return self.writer.append("probe_sample", channel=channel, value=float(value), units=units,
                                  sample_mono_ns=t, source=source)

    def table(self, counts: int, counts_per_rev: int, source: str = "encoder",
              sample_mono_ns: int | None = None) -> dict:
        if source not in ANGLE_SOURCES:
            raise ValueError(f"table angle source is one of {ANGLE_SOURCES}")
        t = self.clock.monotonic_ns() if sample_mono_ns is None else sample_mono_ns
        return self.writer.append("table_encoder", counts=int(counts), counts_per_rev=int(counts_per_rev),
                                  sample_mono_ns=t, source=source)

    def cool_reference(self, channel: str, value: float, units: str = "mm", source: str = "contact_probe",
                       sample_mono_ns: int | None = None) -> dict:
        t = self.clock.monotonic_ns() if sample_mono_ns is None else sample_mono_ns
        return self.writer.append("cool_reference", channel=channel, value=float(value), units=units,
                                  sample_mono_ns=t, source=source)


def unwrap_counts(counts, counts_per_rev: int) -> np.ndarray:
    """Cumulative counts from a reading that wraps at counts_per_rev (or does not wrap)."""
    c = np.asarray(counts, dtype=float)
    d = np.diff(c)
    d = np.where(d > counts_per_rev / 2, d - counts_per_rev, np.where(d < -counts_per_rev / 2, d + counts_per_rev, d))
    return np.concatenate([[c[0]], c[0] + np.cumsum(d)]) if len(c) else c


def table_angles(records: list[dict], source: str | None = None) -> tuple[np.ndarray, np.ndarray]:
    """(sample times ns, cumulative table angle deg) from table_encoder records."""
    rows = sorted((r for r in records if r["kind"] == "table_encoder" and (source is None or r["source"] == source)),
                  key=lambda r: r["sample_mono_ns"])
    if not rows:
        return np.zeros(0, dtype=np.int64), np.zeros(0)
    cpr = rows[0]["counts_per_rev"]
    if any(r["counts_per_rev"] != cpr for r in rows):
        raise ValueError("mixed counts_per_rev in one angle stream")
    t = np.array([r["sample_mono_ns"] for r in rows], dtype=np.int64)
    return t, unwrap_counts([r["counts"] for r in rows], cpr) * 360.0 / cpr


def angle_at(times_ns, enc_t_ns, enc_angle_deg, max_gap_ns: int = 200_000_000) -> np.ndarray:
    """Interpolated table angle; NaN outside the encoder record or across a gap. No extrapolation."""
    t = np.asarray(times_ns, dtype=np.int64)
    out = np.interp(t.astype(float), enc_t_ns.astype(float), enc_angle_deg)
    outside = (t < enc_t_ns[0]) | (t > enc_t_ns[-1])
    k = np.clip(np.searchsorted(enc_t_ns, t), 1, len(enc_t_ns) - 1)
    gap = (enc_t_ns[k] - enc_t_ns[k - 1]) > max_gap_ns
    out[outside | gap] = np.nan
    return out


def lap_of(angle_cumulative_deg, start_deg: float = 0.0) -> np.ndarray:
    return np.floor((np.asarray(angle_cumulative_deg) - start_deg) / 360.0).astype(int)


def _basis(angle_deg, harmonics: int) -> np.ndarray:
    th = np.radians(np.asarray(angle_deg, dtype=float))
    cols = [np.ones_like(th)]
    for k in range(1, harmonics + 1):
        cols += [np.cos(k * th), np.sin(k * th)]
    return np.stack(cols, axis=1)


@dataclass
class ColdBaseline:
    channel: str
    harmonics: int
    coef: np.ndarray
    residual_sigma: float
    laps: list = field(default_factory=list)
    max_coverage_gap_deg: float = 0.0
    n_samples: int = 0

    def predict(self, angle_deg) -> np.ndarray:
        return _basis(angle_deg, self.harmonics) @ self.coef

    def deviation(self, angle_deg, value) -> np.ndarray:
        return np.asarray(value, dtype=float) - self.predict(angle_deg)

    @classmethod
    def fit(cls, channel: str, angle_deg, values, laps, harmonics: int = 6, max_gap_deg: float = 20.0,
            huber_k: float = 1.345, iters: int = 20) -> "ColdBaseline":
        a = np.asarray(angle_deg, dtype=float)
        v = np.asarray(values, dtype=float)
        ok = np.isfinite(a) & np.isfinite(v)
        a, v = a[ok], v[ok]
        wrapped = np.sort(np.mod(a, 360.0))
        if len(wrapped) < 4 * harmonics + 2:
            raise ValueError("too few samples for the requested harmonics")
        gaps = np.diff(np.concatenate([wrapped, [wrapped[0] + 360.0]]))
        if gaps.max() > max_gap_deg:
            raise ValueError(f"angular coverage has a {gaps.max():.1f}° gap (> {max_gap_deg}°)")
        x = _basis(a, harmonics)
        w = np.ones(len(v))
        for _ in range(iters):
            sw = np.sqrt(w)
            coef, *_ = np.linalg.lstsq(x * sw[:, None], v * sw, rcond=None)
            r = v - x @ coef
            s = max(1.4826 * float(np.median(np.abs(r - np.median(r)))), 1e-12)
            w_new = np.where(np.abs(r) / s <= huber_k, 1.0, huber_k * s / np.maximum(np.abs(r), 1e-12))
            if np.allclose(w_new, w, atol=1e-6):
                break
            w = w_new
        return cls(channel, harmonics, coef, s, sorted(set(int(l) for l in np.asarray(laps)[ok])),
                   float(gaps.max()), int(len(v)))

    def score(self, angle_deg, values) -> dict:
        d = self.deviation(angle_deg, values)
        d = d[np.isfinite(d)]
        return {"rms": float(np.sqrt(np.mean(d ** 2))), "max_abs": float(np.max(np.abs(d))),
                "n": int(len(d)), "residual_sigma": self.residual_sigma}


def compare(probe_t_ns, probe_values, enc_t_ns, enc_angle_deg, baseline: ColdBaseline,
            cool_t_ns=None, cool_values=None, cool_ref_t0_ns: int | None = None,
            max_gap_ns: int = 200_000_000) -> dict:
    """Probe deviations from the cold baseline at the table angle of each sample.

    With a cool reference, its change since `cool_ref_t0_ns` (default: its first
    sample) is interpolated at each probe time and subtracted.
    """
    angle = angle_at(probe_t_ns, enc_t_ns, enc_angle_deg, max_gap_ns)
    dev = baseline.deviation(angle, probe_values)
    out = {"angle_deg": angle, "deviation": dev}
    if cool_t_ns is not None and len(cool_t_ns):
        ct = np.asarray(cool_t_ns, dtype=float)
        cv = np.asarray(cool_values, dtype=float)
        ref = np.interp(float(cool_ref_t0_ns if cool_ref_t0_ns is not None else ct[0]), ct, cv)
        drift = np.interp(np.asarray(probe_t_ns, dtype=float), ct, cv) - ref
        out["cool_drift"] = drift
        out["corrected"] = dev - drift
    return out
