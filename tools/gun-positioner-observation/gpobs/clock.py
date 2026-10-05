"""One host timeline: `time.monotonic_ns()` for ordering, wall clock for reference.

On this Mac `time.get_clock_info('monotonic').implementation` is
`mach_absolute_time()`. The capture helper stamps frames with
`clock_gettime_nsec_np(CLOCK_UPTIME_RAW)`, which counts the same ticks in
nanoseconds; `observe.py clock-check` verifies the agreement on a given machine.

A controller has its own microsecond clock. `ClockMap` estimates the mapping
from controller time to host monotonic time from request/reply exchanges.
"""

from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np


class Clock:
    """Host clock. Every timestamp in a session comes from one instance."""

    def monotonic_ns(self) -> int:
        return time.monotonic_ns()

    def wall_ns(self) -> int:
        return time.time_ns()

    def sleep_ns(self, ns: int) -> None:
        if ns > 0:
            time.sleep(ns / 1e9)


class FakeClock(Clock):
    """Deterministic clock for tests and the simulator; `sleep_ns` advances it."""

    def __init__(self, start_ns: int = 1_000_000_000, wall_start_ns: int = 1_790_000_000_000_000_000):
        self._mono = int(start_ns)
        self._wall_offset = int(wall_start_ns) - int(start_ns)

    def monotonic_ns(self) -> int:
        return self._mono

    def wall_ns(self) -> int:
        return self._mono + self._wall_offset

    def advance_ns(self, ns: int) -> None:
        if ns < 0:
            raise ValueError("a monotonic clock cannot go backwards")
        self._mono += int(ns)

    def sleep_ns(self, ns: int) -> None:
        if ns > 0:
            self.advance_ns(ns)


@dataclass(frozen=True)
class ClockExchange:
    """One request/reply: host send and receive stamps around a controller time."""

    host_send_ns: int
    host_recv_ns: int
    controller_us: int

    @property
    def rtt_ns(self) -> int:
        return self.host_recv_ns - self.host_send_ns

    @property
    def host_mid_ns(self) -> float:
        return (self.host_send_ns + self.host_recv_ns) / 2.0


@dataclass(frozen=True)
class ClockMap:
    """host_ns = offset_ns + rate * controller_ns, fitted on low-latency exchanges.

    `uncertainty_ns` is half the largest round trip among the exchanges used plus
    the fit's residual spread. The controller's reply time can fall anywhere
    inside its round trip, so the mapping is not better than that bound.
    """

    offset_ns: float
    rate: float
    uncertainty_ns: float
    exchanges_used: int
    exchanges_total: int

    def to_host_ns(self, controller_us: float) -> int:
        return int(round(self.offset_ns + self.rate * controller_us * 1000.0))

    @classmethod
    def fit(cls, exchanges: list[ClockExchange], keep_fraction: float = 0.5) -> "ClockMap":
        if len(exchanges) < 2:
            raise ValueError("a clock map needs at least two exchanges")
        rtts = np.array([e.rtt_ns for e in exchanges], dtype=float)
        if np.any(rtts < 0):
            raise ValueError("an exchange received before it was sent")
        cutoff = np.quantile(rtts, keep_fraction)
        kept = [e for e in exchanges if e.rtt_ns <= cutoff]
        if len(kept) < 2:
            kept = sorted(exchanges, key=lambda e: e.rtt_ns)[:2]
        c = np.array([e.controller_us * 1000.0 for e in kept])
        h = np.array([e.host_mid_ns for e in kept])
        if np.ptp(c) == 0:
            rate = 1.0
            offset = float(np.mean(h - c))
        else:
            c0 = c.mean()
            rate = float(np.sum((c - c0) * (h - h.mean())) / np.sum((c - c0) ** 2))
            offset = float(h.mean() - rate * c0)
        resid = h - (offset + rate * c)
        half_rtt = max(e.rtt_ns for e in kept) / 2.0
        spread = float(np.max(np.abs(resid))) if len(resid) else 0.0
        return cls(offset, rate, half_rtt + spread, len(kept), len(exchanges))
