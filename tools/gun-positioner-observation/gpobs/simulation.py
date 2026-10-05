"""Simulated mechanism, observation and images for dry development and tests.

The mechanism has, per axis, a play gap (backlash: the output does not move
until the input crosses the gap after a reversal), different gains for positive
and negative output motion, a full cross-coupled response matrix from counts
to image features, slow drift, observation noise and occasional gross outliers.
Its play is implemented as a gap between input and output positions, separately
from the take-up bookkeeping in `response.py`, so fitting is checked against an
independent model. Nothing here touches hardware.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .clock import Clock, FakeClock
from .controls import (AXES, COUNTS_PER_MM, MAX_ACCEL_COUNTS_S2, MAX_DURATION_US, MAX_JOG_COUNTS, MIN_DURATION_US,
                       PROFILES, SOFT_MAX, SOFT_MIN)
from .moves import BackendInfo, MoveCommand, MoveOutcome, PositionerBackend

FEATURES = ("cam_a.dot.u", "cam_a.dot.v", "cam_a.wire.u", "cam_a.wire.v",
            "cam_b.dot.u", "cam_b.dot.v", "cam_b.wire.u", "cam_b.wire.v")


@dataclass
class MechanismTruth:
    feature_names: tuple[str, ...]
    j_plus: np.ndarray          # features per count of positive output motion (m x 6)
    j_minus: np.ndarray         # features per count of negative output motion (m x 6)
    backlash: np.ndarray        # play gap in counts (6)
    drift_per_s: np.ndarray     # linear feature drift (m)
    drift_walk: float           # random-walk σ per √s
    noise: np.ndarray           # per-frame feature noise σ (m)
    outlier_prob: float = 0.0   # chance an observation carries one gross error
    outlier_scale: float = 20.0
    start: np.ndarray = field(default_factory=lambda: np.zeros(8))


def default_truth(seed: int = 7, noise_px: float = 0.15, backlash=(60, 35, 90, 120, 45, 75),
                  outlier_prob: float = 0.0) -> MechanismTruth:
    """A well-conditioned eight-feature, six-axis response in pixels per count.

    Scale: about 2 µm per pixel and 6,400 counts per mm make one count about
    0.08 px, so one 640-count jog moves a feature by tens of pixels.
    """
    rng = np.random.default_rng(seed)
    m, n = len(FEATURES), len(AXES)
    while True:
        base = 0.08 * rng.normal(size=(m, n))
        if np.linalg.cond(base) < 6:
            break
    j_plus = base * (1 + 0.15 * rng.uniform(-1, 1, size=n))
    j_minus = base * (1 + 0.15 * rng.uniform(-1, 1, size=n))
    return MechanismTruth(
        feature_names=FEATURES, j_plus=j_plus, j_minus=j_minus,
        backlash=np.asarray(backlash, dtype=float), drift_per_s=0.004 * rng.normal(size=m),
        drift_walk=0.002, noise=np.full(m, noise_px), outlier_prob=outlier_prob,
        start=np.array([1900.0, 1100.0, 1850.0, 1180.0, 2000.0, 1000.0, 2060.0, 1090.0]))


class SimulatedMechanism:
    def __init__(self, truth: MechanismTruth, seed: int = 11, jammed=()):
        self.truth = truth
        self.rng = np.random.default_rng(seed)
        n = len(AXES)
        self.input = np.zeros(n)                   # issued counts
        self.output = np.zeros(n)                  # counts that reached the output; starts mid-gap
        self.features = truth.start.astype(float).copy()
        self.drift = np.zeros(len(truth.feature_names))
        self.jammed = set(jammed)
        self.t_ns: int | None = None

    def advance_to(self, t_ns: int) -> None:
        if self.t_ns is None:
            self.t_ns = t_ns
            return
        dt = max(0.0, (t_ns - self.t_ns) / 1e9)
        self.t_ns = t_ns
        tr = self.truth
        self.drift += tr.drift_per_s * dt + tr.drift_walk * np.sqrt(dt) * self.rng.normal(size=self.drift.shape)

    def move(self, counts) -> np.ndarray:
        """Apply issued counts; return the output motion per axis (counts)."""
        counts = np.asarray(counts, dtype=float)
        half = self.truth.backlash / 2.0
        moved = np.zeros_like(counts)
        for j, c in enumerate(counts):
            if c == 0 or j in self.jammed:
                self.input[j] += c
                continue
            new_input = self.input[j] + c
            out = self.output[j]
            if new_input - out > half[j]:
                out = new_input - half[j]
            elif out - new_input > half[j]:
                out = new_input + half[j]
            moved[j] = out - self.output[j]
            self.output[j], self.input[j] = out, new_input
        dy = self.truth.j_plus @ np.where(moved > 0, moved, 0) + self.truth.j_minus @ np.where(moved < 0, moved, 0)
        self.features += dy
        return moved

    def true_features(self) -> np.ndarray:
        return self.features + self.drift

    def frame_features(self) -> np.ndarray:
        return self.true_features() + self.truth.noise * self.rng.normal(size=self.features.shape)


class SimulatedPositioner(PositionerBackend):
    """Executes moves on a SimulatedMechanism on a (normally fake) clock.

    Status dicts mirror the controls Client's keys, including the build
    profile's `max_rate`, so receipts look alike. Requests the firmware would
    reject (duration range, jog bound, soft limit, cubic peak rate or
    acceleration at this profile, zero move) are rejected here too and move
    nothing. The simulated controller clock runs at an offset and rate error from
    the host clock, as a real microcontroller clock would.
    """

    def __init__(self, mechanism: SimulatedMechanism, clock: Clock, latency_ns: int = 4_000_000,
                 controller_rate: float = 1.0 + 40e-6, controller_offset_us: int = -987_654,
                 profile: str = "bench"):
        self.mechanism = mechanism
        self.clock = clock
        self.latency_ns = latency_ns
        self.rate = controller_rate
        self.offset_us = controller_offset_us
        self.max_rate = PROFILES[profile]["max_rate"]
        self.profile = profile
        self.seq = 0
        self.counts = [0] * len(AXES)
        self.boot = "51a1ab1e"
        self.vm_epoch = 1
        self.rejected: list[str] = []
        self.info = BackendInfo("simulator", "simulator", False, f"simulated mechanism, {profile} profile; no hardware")

    def firmware_check(self, counts, duration_us: int) -> str | None:
        """The firmware's MOVE6 acceptance rules, in its integer arithmetic."""
        if not MIN_DURATION_US <= duration_us <= MAX_DURATION_US:
            return "duration"
        nonzero = False
        for i, d in enumerate(counts):
            n = abs(int(d))
            nonzero |= n != 0
            if n > MAX_JOG_COUNTS:
                return "jog_bound"
            end = self.counts[i] + int(d)
            if end < SOFT_MIN[i] or end > SOFT_MAX[i]:
                return "soft_limit"
            if 3 * n * 1_000_000 > 2 * self.max_rate * duration_us:
                return "rate"
            if 6 * n * 1_000_000_000_000 > MAX_ACCEL_COUNTS_S2 * duration_us * duration_us:
                return "acceleration"
        return None if nonzero else "zero_move"

    def status(self) -> dict:
        now = self.clock.monotonic_ns()
        return {"type": "status", "boot": self.boot, "seq": 0, "last_seq": self.seq,
                "time_us": self.controller_us(now), "state": "armed", "fault": "none", "referenced": True,
                "count": list(self.counts), "completed_seq": self.seq, "completed_us": 0, "stop_closed": True,
                "open_limit_mask": 0, "supply_adc": 2600, "drivers_ok": True, "profile": self.profile,
                "current_scales": list(PROFILES[self.profile]["current_scales"]),
                "configured_vsense": list(PROFILES[self.profile]["vsense"]),
                "vsense": list(PROFILES[self.profile]["vsense"]),
                "microsteps": [16] * 6, "counts_per_mm": COUNTS_PER_MM, "max_rate": self.max_rate,
                "vm_epoch": self.vm_epoch, "timer_ticks": int(now // 250_000) & 0xFFFFFFFF}

    def controller_us(self, host_ns: int) -> int:
        return int(host_ns / 1000.0 * self.rate + self.offset_us)

    def _exchange(self, send_ns: int) -> dict:
        reply_ns = send_ns + self.latency_ns // 2
        return {"host_send_ns": send_ns, "host_recv_ns": send_ns + self.latency_ns,
                "controller_us": self.controller_us(reply_ns), "boot": self.boot}

    def execute(self, cmd: MoveCommand) -> MoveOutcome:
        clock = self.clock
        issued = clock.monotonic_ns()
        self.mechanism.advance_to(issued)
        why = self.firmware_check(cmd.counts, cmd.duration_us)
        if why is not None:
            self.rejected.append(why)
            clock.sleep_ns(self.latency_ns)
            return MoveOutcome("rejected", issued, clock.monotonic_ns(), error=f"Controller rejected command: {why}",
                               controller={k: v for k, v in self.status().items() if k != "count"})
        self.seq += 1
        ack_ex = self._exchange(issued)
        clock.sleep_ns(self.latency_ns)
        ack_ns = clock.monotonic_ns()
        self.mechanism.move(cmd.counts)
        start = ack_ns + 10_000_000
        clock.sleep_ns(start + cmd.duration_us * 1000 - clock.monotonic_ns())
        completed_host = clock.monotonic_ns()
        self.mechanism.advance_to(completed_host)
        self.counts = [a + b for a, b in zip(self.counts, cmd.counts)]
        poll = self._exchange(completed_host + 20_000_000)
        clock.sleep_ns(20_000_000 + self.latency_ns)
        done_ns = clock.monotonic_ns()
        status = {**self.status(), "time_us": poll["controller_us"],
                  "completed_us": self.controller_us(completed_host)}
        return MoveOutcome(
            status="done", issued_mono_ns=issued, returned_mono_ns=done_ns, ack_mono_ns=ack_ns,
            ack_controller_us=ack_ex["controller_us"], complete_mono_ns=done_ns,
            completed_controller_us=status["completed_us"], reported_counts=list(self.counts),
            controller={k: v for k, v in status.items() if k != "count"}, vm_epoch=self.vm_epoch,
            ack_vm_epoch=self.vm_epoch,
            seq=self.seq, clock_exchanges=[ack_ex, poll])


# ---- synthetic images -------------------------------------------------------------------------

def render_scene(width: int, height: int, dot=None, dot_sigma: float = 2.2, dot_peak: float = 180.0,
                 wire_tip=None, wire_angle_deg: float = 180.0, wire_width: float = 5.0,
                 wire_contrast: float = -70.0, seam=None, seam_contrast: float = 40.0,
                 background: float = 60.0, noise: float = 2.0, rng=None, bit_depth: int = 8,
                 extra_dots=()) -> np.ndarray:
    """Gray image with an aiming dot (Gaussian), a wire ending at a tip, and a seam edge.

    `wire_angle_deg` is the direction from the tip back along the wire, in image
    coordinates (0 = +x, 90 = +y). `seam` is (angle_deg, offset): the seam is the
    line x·cosθ + y·sinθ = offset, rendered as a blurred intensity step.
    """
    rng = rng or np.random.default_rng(0)
    yy, xx = np.mgrid[0:height, 0:width].astype(float)
    img = np.full((height, width), background, dtype=float)
    if seam is not None:
        theta = np.radians(seam[0])
        d = xx * np.cos(theta) + yy * np.sin(theta) - seam[1]
        img += seam_contrast * 0.5 * (1 + np.tanh(d / 1.2))
    if wire_tip is not None:
        a = np.radians(wire_angle_deg)
        ux, uy = np.cos(a), np.sin(a)
        rx, ry = xx - wire_tip[0], yy - wire_tip[1]
        along = rx * ux + ry * uy
        across = -rx * uy + ry * ux
        body = 0.5 * (1 + np.tanh(along / 0.7))          # 0 beyond the tip, 1 along the wire
        profile = np.exp(-0.5 * (across / (wire_width / 2.355)) ** 2)
        img += wire_contrast * body * profile
    for (dx, dy, peak) in ([(dot[0], dot[1], dot_peak)] if dot is not None else []) + list(extra_dots):
        img += peak * np.exp(-0.5 * ((xx - dx) ** 2 + (yy - dy) ** 2) / dot_sigma ** 2)
    img += noise * rng.normal(size=img.shape)
    top = 255 if bit_depth == 8 else 65535
    img = np.clip(np.round(img), 0, top)
    return img.astype(np.uint8 if bit_depth == 8 else np.uint16)


__all__ = ["FEATURES", "MechanismTruth", "default_truth", "SimulatedMechanism",
           "SimulatedPositioner", "render_scene", "FakeClock"]
