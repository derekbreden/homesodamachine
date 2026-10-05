"""Shared test fixtures: a cached simulated dataset and a fake controls Client.

FakeClient has the controls `positioner.Client` method signatures
(test_controls checks them against the real class), matches replies by type,
sequence and `op` as the Client does, and writes the same JSONL records to
`log_path`: host_command, device_reply and clock_bracket, with host stamps from
an injected clock. Its device side reports the build profile the controls
package exports for its max_rate (current scales, configured and decoded
VSENSE), applies the firmware's MOVE6 acceptance rules and completes moves on
that clock. It opens no serial port.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from gpobs.clock import FakeClock  # noqa: E402
from gpobs.controls import (MAX_ACCEL_COUNTS_S2, MAX_DURATION_US, MAX_JOG_COUNTS, MIN_DURATION_US,  # noqa: E402
                            PROFILES, SOFT_MAX, SOFT_MIN, COUNTS_PER_MM, host_modules)
from gpobs.dataset import SessionReader, SessionWriter  # noqa: E402

TMP = tempfile.TemporaryDirectory(prefix="gpobs-tests-")


def tmpdir(name: str) -> Path:
    path = Path(TMP.name) / name
    path.mkdir(parents=True, exist_ok=True)
    return path


@functools.lru_cache(maxsize=None)
def simulated_dataset(seed: int = 7, outlier_prob: float = 0.03, profile: str = "bench",
                      sizes: tuple = (40, 80, 160), trials_per_size: int = 3, backlash=(60, 35, 90, 120, 45, 75)):
    """Engage + identification on the simulator; returns (session path, truth)."""
    from gpobs.experiment import Runner, SimulatedObserver
    from gpobs.moves import MoveRecorder
    from gpobs.simulation import SimulatedMechanism, SimulatedPositioner, default_truth
    clock = FakeClock()
    truth = default_truth(seed=seed, outlier_prob=outlier_prob, backlash=backlash)
    mech = SimulatedMechanism(truth, seed=seed + 4)
    writer = SessionWriter(tmpdir(f"sim-{seed}-{outlier_prob}-{profile}"), "sim", clock)
    recorder = MoveRecorder(SimulatedPositioner(mech, clock, profile=profile), writer, clock)
    runner = Runner(recorder, SimulatedObserver(mech, writer, clock), writer, clock)
    runner.engage()
    runner.identify(sizes=sizes, trials_per_size=trials_per_size)
    writer.close()
    return writer.path, truth


def groups_and_purposes(reader: SessionReader):
    g, p = {}, {}
    for rec in reader.records("trial_start"):
        g[rec["trial_id"]] = rec["plan"].get("group", rec["purpose"])
        p[rec["trial_id"]] = rec["purpose"]
    return g, p


class FakeDevice:
    """Firmware-side behaviour on a fake clock: STATUS/DRIVERS fields as main.cpp prints them,
    sequencing, and MOVE6 acceptance rules for the profile with this max_rate."""

    def __init__(self, clock: FakeClock, max_rate: int = 1000, report_max_rate: bool = True,
                 latency_ns: int = 2_000_000, rate_error: float = 30e-6, offset_us: int = 123_456_789,
                 fault_on_move: int | None = None, state: str = "armed", on_move=None):
        self.clock, self.max_rate, self.report_max_rate = clock, max_rate, report_max_rate
        self.profile = next(n for n, p in PROFILES.items() if p["max_rate"] == max_rate)
        self.vm_epoch = 1
        self.microsteps = [16] * 6
        self.drivers_ok = True
        self.latency_ns, self.rate_error, self.offset_us = latency_ns, rate_error, offset_us
        self.boot = "0badc0de"
        self.last_seq = 0
        self.state = state
        self.on_move = on_move                  # called with each accepted MOVE6 delta
        self.sent: list[str] = []
        self.fault = "none"
        self.count = [0] * 6
        self.completed_seq = 0
        self.completed_us = 0
        self.moving_until_ns = None
        self.pending_seq = None
        self.moves = 0
        self.fault_on_move = fault_on_move
        self.completion_host_ns: dict[int, int] = {}
        self.status_overrides: dict = {}       # fields of a controller built or wired otherwise
        self.stale_before_next_ack: dict | None = None   # a late reply delivered just before the next MOVE6 ack

    def time_us(self, host_ns=None) -> int:
        host_ns = self.clock.monotonic_ns() if host_ns is None else host_ns
        return int(host_ns / 1000 * (1 + self.rate_error)) + self.offset_us

    def _update(self):
        if self.moving_until_ns is not None and self.clock.monotonic_ns() >= self.moving_until_ns:
            self.completed_seq = self.pending_seq
            self.completed_us = self.time_us(self.moving_until_ns)
            self.completion_host_ns[self.pending_seq] = self.moving_until_ns
            self.moving_until_ns = None
            self.state = "armed"

    def status(self, kind="status", seq=0, error=None, op=None) -> dict:
        self._update()
        out = {"type": kind, "boot": self.boot, "seq": seq, "last_seq": self.last_seq, "time_us": self.time_us(),
               "state": self.state, "fault": self.fault,
               "referenced": self.state in ("referenced", "armed", "moving"),
               "count": list(self.count), "completed_seq": self.completed_seq, "completed_us": self.completed_us,
               "stop_closed": True, "open_limit_mask": 0, "supply_adc": 2600, "drivers_ok": self.drivers_ok,
               "counts_per_mm": COUNTS_PER_MM, "vm_epoch": self.vm_epoch,
               "timer_ticks": int(self.clock.monotonic_ns() // 250_000) & 0xFFFFFFFF}
        spec = PROFILES[self.profile]
        out.update(profile=self.profile, current_scales=list(spec["current_scales"]),
                   configured_vsense=list(spec["vsense"]),
                   vsense=list(spec["vsense"]) if self.drivers_ok else [None] * 6, microsteps=self.microsteps)
        if self.report_max_rate:
            out["max_rate"] = self.max_rate
        out.update(self.status_overrides)
        if op:
            out["op"] = op
        if error:
            out["error"] = error
        return out

    def check_move(self, duration: int, delta: list[int]) -> str | None:
        if self.state != "armed":
            return "move_requires_healthy_armed"
        if not MIN_DURATION_US <= duration <= MAX_DURATION_US:
            return "duration"
        nonzero = False
        for i, d in enumerate(delta):
            n = abs(d)
            nonzero |= n != 0
            if n > MAX_JOG_COUNTS:
                return "jog_bound"
            if not SOFT_MIN[i] <= self.count[i] + d <= SOFT_MAX[i]:
                return "soft_limit"
            if 3 * n * 1_000_000 > 2 * self.max_rate * duration:
                return "rate"
            if 6 * n * 1_000_000_000_000 > MAX_ACCEL_COUNTS_S2 * duration * duration:
                return "acceleration"
        return None if nonzero else "zero_move"

    def command(self, line: str) -> list[dict]:
        self._update()
        self.sent.append(line)
        tokens = line.split()
        if tokens == ["STATUS"]:
            return [self.status()]
        if tokens == ["STOP"]:
            self.state, self.fault = "fault", "user_stop"
            return [self.status("stopped", op="STOP")]
        if tokens == ["DRIVERS"]:
            spec = PROFILES[self.profile]
            return [{"type": "driver", "axis": i, "gstat": 0, "drv_status": spec["current_scales"][i] << 16,
                     "bus": i // 3, "address": i % 3, "cs_actual": spec["current_scales"][i],
                     "configured_cs": spec["current_scales"][i], "configured_vsense": spec["vsense"][i],
                     "sample_valid": True, "sample_us": self.time_us() - 1000 * i, "microsteps": 16,
                     "vsense": spec["vsense"][i]} for i in range(6)]
        op, boot, seq = tokens[0], tokens[1], int(tokens[2])
        if boot != self.boot:
            return [self.status("error", 0, "boot_or_sequence_format", op)]
        if seq != self.last_seq + 1:
            return [self.status("error", seq, "sequence", op)]
        if op == "MOVE6":
            duration, delta = int(tokens[3]), [int(t) for t in tokens[4:10]]
            why = self.check_move(duration, delta)
            if why:
                return [self.status("error", seq, why, op)]
            self.last_seq = seq
            self.moves += 1
            if self.fault_on_move == self.moves:
                self.state, self.fault = "fault", "driver"
                self.count = [c + d // 2 for c, d in zip(self.count, delta)]
                return [self.status("ack", seq, op=op)]
            self.state = "moving"
            self.count = [c + d for c, d in zip(self.count, delta)]
            self.pending_seq = seq
            self.moving_until_ns = self.clock.monotonic_ns() + 10_000_000 + duration * 1000
            if self.on_move is not None:
                self.on_move(delta)
            stale, self.stale_before_next_ack = self.stale_before_next_ack, None
            return ([{**self.status("ack", seq, op=op), **stale}] if stale else []) + [self.status("ack", seq, op=op)]
        healthy = self.drivers_ok
        if op == "CLEAR":
            if self.state in ("armed", "moving") or not healthy:
                return [self.status("error", seq, "not_safe_to_clear", op)]
            self.state, self.fault = "unreferenced", "none"
        elif op == "REF":
            if self.state != "unreferenced" or not healthy:
                return [self.status("error", seq, "reference_requires_healthy_unreferenced", op)]
            self.state, self.count = "referenced", [0] * 6
        elif op == "ARM":
            if self.state != "referenced" or not healthy:
                return [self.status("error", seq, "arm_requires_healthy_reference", op)]
            self.state = "armed"
        elif op == "DISARM":
            if self.state == "fault":
                return [self.status("error", seq, "fault_requires_clear", op)]
            self.state = "unreferenced"
        self.last_seq = seq
        return [self.status("ack", seq, op=op)]


class FakeClient:
    """Same public methods and signatures as the controls positioner.Client; no serial port."""

    clock: FakeClock
    device: FakeDevice

    def __init__(self, port, log_path=None):
        self.port = port
        self.log = open(log_path, "a") if log_path else None
        self.boot = None
        self.seq = 0
        self.last = {}
        self.heartbeat = None
        self.status()
        self.seq = self.last["last_seq"]

    @classmethod
    def with_device(cls, device: FakeDevice, log_path=None):
        obj = cls.__new__(cls)
        obj.clock, obj.device = device.clock, device
        obj.__init__("fake", log_path)
        return obj

    def record(self, record):
        if self.log:
            self.log.write(json.dumps(record, separators=(",", ":")) + "\n")
            self.log.flush()

    def _exchange(self, command, desired_type, seq=None, op=None):
        sent = self.clock.monotonic_ns()
        self.record({"type": "host_command", "host_send_ns": sent, "command": command})
        self.clock.advance_ns(self.device.latency_ns // 2)
        replies = self.device.command(command)
        self.clock.advance_ns(self.device.latency_ns - self.device.latency_ns // 2)
        result = None
        for r in replies:
            received = self.clock.monotonic_ns()
            self.record({"type": "device_reply", "host_receive_ns": received, "device": r})
            if "boot" in r:
                self.boot, self.last = r["boot"], r
            matches_op = op is None or r.get("op") == op
            if result is None and r["type"] == "error" and matches_op and (seq is None or r.get("seq") in (0, seq)):
                raise host_modules().positioner.CommandRejected("Controller rejected command: " +
                                                                r.get("error", "unknown"))
            if result is None and r["type"] == desired_type and matches_op and (seq is None or r.get("seq") == seq):
                if "time_us" in r:
                    self.record({"type": "clock_bracket", "host_send_ns": sent, "host_receive_ns": received,
                                 "device_time_us": r["time_us"], "boot": r["boot"]})
                result = r
        return result if result is not None else replies

    def request(self, operation, *args):
        seq = self.seq + 1
        result = self._exchange(" ".join(map(str, (operation, self.boot, seq, *args))), "ack", seq, operation)
        self.seq = seq
        return result

    def status(self):
        return self._exchange("STATUS", "status")

    def stop(self):
        return self._exchange("STOP", "stopped", op="STOP")

    def start_heartbeat(self):
        self.heartbeat = "fake"

    def move(self, delta, duration_us=1000000):
        if len(delta) != 6 or any(abs(v) > 640 for v in delta) or not any(delta):
            raise ValueError("Six signed nonzero total count deltas, ≤640 per axis, required")
        if not 100000 <= duration_us <= 2000000:
            raise ValueError("Duration must be100..2000ms")
        result = self.request("MOVE6", duration_us, *delta)
        move_seq = result["seq"]
        deadline = self.clock.monotonic_ns() + duration_us * 1000 + 500_000_000
        while self.clock.monotonic_ns() < deadline:
            result = self.status()
            if result["state"] == "fault":
                raise RuntimeError("Motion fault: " + result["fault"])
            if result["completed_seq"] == move_seq:
                return result
            self.clock.advance_ns(30_000_000)
        self.stop()
        raise TimeoutError("Move completion absent; reference invalidated")

    def move_to_counts(self, target, duration_us=1000000):
        raise NotImplementedError("not used by the observation adapter")

    def drivers(self):
        return self._exchange("DRIVERS", "never")

    def close(self, stop_motion=True):
        if stop_motion:
            try:
                self.stop()
            except Exception:
                pass
        if self.log:
            self.log.close()


# ---- filled configuration fixtures ----------------------------------------------------------------

EXAMPLES = HERE.parent / "examples"


def filled_receipt(camera_id: str, recorded_at: str, **overrides) -> dict:
    """A complete optics receipt with synthetic values (tests only)."""
    receipt = {"format_version": 1, "camera_id": camera_id, "recorded_at": recorded_at,
               "recorded_by": "synthetic test", "method": "camera_menu", "focus_mode": "manual",
               "exposure_mode": "manual", "tracking": "off", "zoom": 8192, "focus": "not_available",
               "shutter": "1/250", "iris": "F2.8", "gain": 0, "white_balance": "6500K",
               "lens_attachment": "Raynox DCR-250", "notes": "synthetic test receipt"}
    receipt.update(overrides)
    return receipt


def clock_receipt_for(helper: Path, passed: bool = True) -> dict:
    import time
    from gpobs.config import clock_receipt
    check = {"python_before_ns": 1, "python_after_ns": 3, "uptime_raw_ns": 2, "host_time_clock_ns": 2,
             "uptime_raw_within_bracket": passed, "host_time_clock_within_bracket": True}
    return clock_receipt(check, helper, time.time_ns())


def write_filled_setup(directory: Path, helper: Path | None = None, width: int = 3840, height: int = 2160,
                       fps: float = 29.97, pixel_format: str = "420v", require_native_4k: bool = True,
                       clock: dict | None = None, unique_ids=("0x14100000aaaa0001", "0x14200000aaaa0001")) -> Path:
    """The shipped cameras template with every operator entry filled with synthetic values.

    Returns the path of cameras.json. The clock receipt is tied to `helper`
    (a stand-in file unless one is given) so validation can be run anywhere.
    """
    import time
    from gpobs.config import iso_time
    directory.mkdir(parents=True, exist_ok=True)
    if helper is None:
        helper = directory / "stand-in-helper"
        helper.write_bytes(b"stand-in helper build for configuration tests")
    now = iso_time(time.time_ns())
    data = json.loads((EXAMPLES / "cameras.example.json").read_text())
    data["clock_check"]["receipt"] = "clock-check.json"
    (directory / "clock-check.json").write_text(json.dumps(clock or clock_receipt_for(helper)))
    for i, cam in enumerate(data["cameras"]):
        cid = cam["camera_id"]
        cam.update(unique_id=unique_ids[i], name="FoMaKo 4K camera (synthetic)", position=f"stage {cid}")
        cam["require_native_4k"] = require_native_4k
        cam["verified_format"].update(width=width, height=height, fps=fps, pixel_format=pixel_format,
                                      chroma=False, measured_at=now,
                                      measured_with="observe.py format-report (synthetic)")
        cam["optics"].update(source="operator", receipt=f"{cid}-optics.json", visca=None)
        (directory / f"{cid}-optics.json").write_text(json.dumps(filled_receipt(cid, now)))
    path = directory / "cameras.json"
    path.write_text(json.dumps(data, indent=1))
    return path


# ---- learn fixtures -------------------------------------------------------------------------------------

DETECTOR_DEFAULTS = {
    "dot": {"threshold_sigma": 6, "min_pixels": 3, "max_pixels": 20000, "channel": "gray"},
    "wire": {"approach_deg": 0, "polarity": "dark", "threshold_sigma": 5, "min_pixels": 30, "min_elongation": 3},
    "seam": {"orientation": "horizontal", "inlier_px": 1.0, "min_inlier_fraction": 0.6, "min_edge_sigma": 5},
}
# ROIs for 320 x 240 synthetic frames: the wire runs from its tip toward +x, the seam lies below.
# Each ROI keeps its feature inside over the jog plans' excursions (tens of pixels).
SMALL_ROIS = {"dot": (30, 30, 120, 100), "wire": (170, 40, 120, 80), "seam": (20, 160, 280, 60)}
LARGE_ROIS = {"dot": (1800, 980, 240, 200), "wire": (1950, 1000, 300, 160), "seam": (1650, 1060, 600, 160)}


def write_features(path: Path, rois=None, frames: int = 3, settle_s: float = 0.2) -> Path:
    """The shipped features template filled with synthetic ROIs and the detector defaults."""
    rois = rois or LARGE_ROIS
    data = json.loads((EXAMPLES / "features.example.json").read_text())
    data.update(frames_per_observation=frames, min_valid_fraction=0.6, settle_s=settle_s)
    for f in data["features"]:
        x, y, w, h = rois[f["type"]]
        f["roi"] = {"x": x, "y": y, "width": w, "height": h}
        f["params"] = dict(DETECTOR_DEFAULTS[f["type"]])
    path.write_text(json.dumps(data, indent=1))
    return path


def write_target(path: Path, quantities: list[dict], axes: list[str]) -> Path:
    data = json.loads((EXAMPLES / "target.example.json").read_text())
    data.update(units="px", px_per_mm=None, calibration=None, axes=axes, quantities=quantities)
    path.write_text(json.dumps(data, indent=1))
    return path


def scene_source(world, features, clock, camera_id: str, width: int = 320, height: int = 240):
    """An ArraySource rendering this camera's dot, wire and seam where the simulated world has them."""
    import numpy as np
    from gpobs.capture import ArraySource
    from gpobs.features import roi_center
    from gpobs.simulation import render_scene
    defs = {f.type: f for f in features.features if f.camera_id == camera_id}
    names = list(world.mechanism.truth.feature_names)
    rng = np.random.default_rng(abs(hash(camera_id)) % 2**31)

    def render():
        world.mechanism.advance_to(clock.monotonic_ns())
        y = dict(zip(names, world.mechanism.true_features()))
        seam = defs["seam"]
        th = y[f"{camera_id}.{seam.label}.theta_deg"]
        cx, cy = roi_center(seam.roi)
        t = np.radians(th)
        rho0 = y[f"{camera_id}.{seam.label}.rho"] + cx * np.cos(t) + cy * np.sin(t)
        dot, wire = defs["dot"], defs["wire"]
        return render_scene(width, height, dot=(y[f"{camera_id}.{dot.label}.u"], y[f"{camera_id}.{dot.label}.v"]),
                            wire_tip=(y[f"{camera_id}.{wire.label}.u"], y[f"{camera_id}.{wire.label}.v"]),
                            wire_angle_deg=wire.params["approach_deg"], seam=(th, rho0), noise=1.5, rng=rng)

    return ArraySource(camera_id, render, clock, fps=30, unique_id=f"synthetic-{camera_id}")
