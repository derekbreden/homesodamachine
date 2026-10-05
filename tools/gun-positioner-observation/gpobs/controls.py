"""Thin layer over the controls package in `firmware/src_gun_positioner/host/`.

Axis order, count units and soft limits are imported from its `kinematics.py`;
moves go through its `positioner.Client.move()`; corrections are computed by its
`visual_servo.correction()` (see `proposal.py`). This module adds only what the
observation timeline needs:

* `receipt_from_client_move()` maps one `Client.move()` call onto the session
  timeline. Inputs: the host monotonic stamps taken immediately before the call
  and after it returns, the status dict it returned (or the exception it raised),
  and the records the `Client` appended to its `log_path` JSONL during the call
  (`host_command`, `device_reply`, `clock_bracket`; all host stamps are
  `time.monotonic_ns()`, the same clock as the session's). Only the ack whose
  `op` is MOVE6 and whose sequence is the move's counts as its acceptance.
* `ControlsClientBackend` executes `MoveCommand`s through a `Client` and returns
  that receipt. It can move hardware, so `moves.MoveRecorder` refuses it unless
  the caller passes `allow_hardware=True`.
* `PROFILES` are the firmware build profiles the controls host exports (per-axis
  current scales and VSENSE, peak rate), with nominal TMC2209 RMS currents;
  `profile_problems()` compares a STATUS with them.

The modules are loaded from their files without writing bytecode into that
directory and without adding its generic module names to `sys.modules`.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

from .clock import Clock, ClockExchange, ClockMap

REPO_ROOT = Path(__file__).resolve().parents[3]
FIRMWARE_DIR = REPO_ROOT / "firmware" / "src_gun_positioner"
HOST_DIR = FIRMWARE_DIR / "host"
MOTION_POLICY_H = FIRMWARE_DIR / "motion_policy.h"
GEOMETRY_H = FIRMWARE_DIR / "geometry_generated.h"
DRIVER_PROFILE_H = FIRMWARE_DIR / "driver_profile.h"
BUILD_MANIFEST = FIRMWARE_DIR / "assets" / "build-manifest.json"


@dataclass(frozen=True)
class HostModules:
    kinematics: object
    visual_servo: object
    positioner: object


_HOST: HostModules | None = None


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def host_modules() -> HostModules:
    """The controls host modules, loaded once from HOST_DIR."""
    global _HOST
    if _HOST is None:
        if not HOST_DIR.is_dir():
            raise ImportError(f"controls host package not found at {HOST_DIR}")
        saved_flag = sys.dont_write_bytecode
        saved_kinematics = sys.modules.get("kinematics")
        sys.dont_write_bytecode = True
        try:
            kinematics = _load("gun_positioner_host_kinematics", HOST_DIR / "kinematics.py")
            visual_servo = _load("gun_positioner_host_visual_servo", HOST_DIR / "visual_servo.py")
            # positioner.py does `from kinematics import ...`; satisfy it for the
            # duration of its import only.
            sys.modules["kinematics"] = kinematics
            positioner = _load("gun_positioner_host_positioner", HOST_DIR / "positioner.py")
        finally:
            sys.dont_write_bytecode = saved_flag
            if saved_kinematics is None:
                sys.modules.pop("kinematics", None)
            else:
                sys.modules["kinematics"] = saved_kinematics
        _HOST = HostModules(kinematics, visual_servo, positioner)
    return _HOST


def _int_constant(text: str, name: str, macros: dict) -> int | None:
    m = re.search(rf"\b{name}\s*=\s*([A-Za-z_][A-Za-z0-9_]*|-?\d+)\s*;", text)
    if not m:
        return None
    token = m.group(1)
    if re.fullmatch(r"-?\d+", token):
        return int(token)
    return macros.get(token)


def firmware_constants(motion_policy_h: Path = MOTION_POLICY_H, geometry_h: Path = GEOMETRY_H) -> dict:
    """Motion constants read from the firmware headers.

    `kCountsPerMm`, `kMinCount` and `kMaxCount` come from geometry_generated.h.
    A constant defined through a macro (kMaxRate = POSITIONER_MAX_RATE) resolves
    to the macro's in-header default and is reported under `macro_defaults`; the
    build may override it per profile, so the controller's STATUS `max_rate` is
    the value a session uses.
    """
    out: dict = {"macro_defaults": {}}
    policy = motion_policy_h.read_text()
    macros = {name: int(value) for name, value in
              re.findall(r"#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\s+(-?\d+)\b", policy)}
    for name in ("kMaxJogCounts", "kMinDurationUs", "kMaxDurationUs", "kMaxRate", "kMaxAcceleration",
                 "kHeartbeatTimeoutUs", "kTickUs"):
        value = _int_constant(policy, name, macros)
        if value is not None:
            out[name] = value
        ref = re.search(rf"\b{name}\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*;", policy)
        if ref and ref.group(1) in macros:
            out["macro_defaults"][name] = {"macro": ref.group(1), "default": macros[ref.group(1)]}
    geometry = geometry_h.read_text()
    value = _int_constant(geometry, "kCountsPerMm", {})
    if value is not None:
        out["kCountsPerMm"] = value
    for name in ("kMinCount", "kMaxCount"):
        m = re.search(rf"\b{name}\s*=\s*\{{([^}}]*)\}}", geometry)
        if m:
            out[name] = [int(v) for v in re.findall(r"-?\d+", m.group(1))]
    return out


_k = host_modules().kinematics
AXES: tuple[str, ...] = tuple(_k.AXES)            # X, Y, Z, U, V, W
COUNTS_PER_MM: int = int(_k.COUNTS_PER_MM)        # issued STEP edges per mm screw extension
SOFT_MIN: tuple[int, ...] = tuple(_k.SOFT_MIN)
SOFT_MAX: tuple[int, ...] = tuple(_k.SOFT_MAX)
mm_to_count = _k.mm_to_count
split_target = _k.split_target

_fw = firmware_constants()
MAX_JOG_COUNTS: int = _fw["kMaxJogCounts"]
MIN_DURATION_US: int = _fw["kMinDurationUs"]
MAX_DURATION_US: int = _fw["kMaxDurationUs"]
MAX_ACCEL_COUNTS_S2: int = _fw["kMaxAcceleration"]
# TMC2209 nominal RMS coil current (manufacturer datasheet):
#   I_rms = (CS + 1) / 32 * V_fs / (R_sense + 0.02 ohm) / sqrt(2)
# with V_fs = 0.325 V at VSENSE=0 and 0.18 V at VSENSE=1. R_sense is the R110 (0.110 ohm)
# sense resistor; the controls build manifest (BUILD_MANIFEST, `current_estimate_scope`) states
# it and the 0.02 ohm internal resistance, and the tests compare these constants with it.
# Results are nominal: the driver's internal reference (about +/-5 %) and the sense resistor
# tolerance are not calibrated.
RSENSE_OHM = 0.110
INTERNAL_SENSE_OHM = 0.020
VFS_V = {0: 0.325, 1: 0.180}
NOMINAL_CURRENT_BASIS = ("nominal TMC2209 (CS+1)/32 * Vfs/(Rsense+0.02 ohm)/sqrt(2), Vfs 0.325 V at VSENSE=0 "
                         "and 0.18 V at VSENSE=1, Rsense 0.110 ohm; internal reference (+/-5 %) and sense "
                         "resistor tolerance not calibrated; not a measured current")


def nominal_rms_current_a(current_scale: int, vsense: int, rsense_ohm: float = RSENSE_OHM) -> float:
    """Nominal RMS coil current for one driver; see NOMINAL_CURRENT_BASIS."""
    if vsense not in VFS_V:
        raise ValueError("VSENSE is 0 or 1")
    if not 0 <= int(current_scale) <= 31:
        raise ValueError("current scale is 0..31")
    return (int(current_scale) + 1) / 32 * VFS_V[vsense] / (rsense_ohm + INTERNAL_SENSE_OHM) / math.sqrt(2)


def _profiles_from_host() -> dict[str, dict]:
    """Firmware build profiles from the controls host module (what its Client.check_profile enforces).

    name -> per-axis current scales and VSENSE in AXES order, peak rate, and the
    nominal RMS current each pair gives.
    """
    pos = host_modules().positioner
    out = {}
    for name, (scales, rate) in pos.PROFILES.items():
        vsense = list(pos.VSENSE_PROFILES[name])
        out[name] = {"current_scales": list(scales), "vsense": vsense, "max_rate": int(rate),
                     "nominal_rms_current_a": [round(nominal_rms_current_a(c, v), 4)
                                               for c, v in zip(scales, vsense)]}
    return out


# STATUS reports `profile`, `current_scales`, `configured_vsense`, decoded `vsense` and `max_rate`.
PROFILES: dict[str, dict] = _profiles_from_host()
# Without a reported rate, durations assume the slowest profile.
CONSERVATIVE_MAX_RATE = min(p["max_rate"] for p in PROFILES.values())


def driver_profile_header(path: Path = DRIVER_PROFILE_H) -> dict:
    """kProfileName, kCurrentScales and kVsense from driver_profile.h, per POSITIONER_LOADED_PROFILE value.

    Each `POSITIONER_LOADED_PROFILE ? a : b` is evaluated for 0 and 1. Also returns
    the (CS, VSENSE, amps) triples the header's comment states as nominal currents.
    """
    text = path.read_text()

    def array(name: str, loaded: int) -> list[int]:
        body = re.search(rf"\b{name}\s*=\s*\{{([^}}]*)\}}", text).group(1)
        body = re.sub(r"POSITIONER_LOADED_PROFILE\s*\?\s*(\d+)\s*:\s*(\d+)",
                      lambda m: m.group(1) if loaded else m.group(2), body)
        return [int(v) for v in re.findall(r"\d+", body)]

    names = re.search(r'kProfileName\s*=\s*POSITIONER_LOADED_PROFILE\s*\?\s*"([^"]+)"\s*:\s*"([^"]+)"', text)
    out = {}
    for loaded, name in ((1, names.group(1)), (0, names.group(2))):
        out[name] = {"current_scales": array("kCurrentScales", loaded), "vsense": array("kVsense", loaded)}
    stated = [(int(cs), int(v), float(a)) for cs, v, a in
              re.findall(r"CS(\d+)/VSENSE([01])\s*=\s*(\d*\.\d+)\s*A RMS", text)]
    return {"profiles": out, "stated_nominal_rms": stated}


def profile_problems(status: dict | None) -> list[str]:
    """Reasons a STATUS does not match its named build profile, as the controls Client checks.

    Decoded `vsense` readings are compared only while drivers_ok; unverified
    readings are null.
    """
    if not status:
        return ["no controller status"]
    name = status.get("profile")
    if name not in PROFILES:
        return [f"controller profile {name!r} is not one the controls package defines: {sorted(PROFILES)}"]
    want = PROFILES[name]
    problems = []
    if status.get("current_scales") != want["current_scales"]:
        problems.append(f"current_scales {status.get('current_scales')} differ from the {name} profile "
                        f"{want['current_scales']}")
    if status.get("configured_vsense") != want["vsense"]:
        problems.append(f"configured_vsense {status.get('configured_vsense')} differs from the {name} profile "
                        f"{want['vsense']}")
    if status.get("drivers_ok") and status.get("vsense") != want["vsense"]:
        problems.append(f"decoded vsense {status.get('vsense')} differs from the {name} profile {want['vsense']}")
    if status.get("max_rate") != want["max_rate"]:
        problems.append(f"max_rate {status.get('max_rate')} differs from the {name} profile {want['max_rate']}")
    return problems


def profile_summary(status: dict) -> dict:
    """The STATUS's per-axis scales and VSENSE with their nominal RMS currents, labelled nominal."""
    scales, vsense = status.get("current_scales"), status.get("configured_vsense")
    currents = None
    if isinstance(scales, list) and isinstance(vsense, list) and len(scales) == len(vsense) == len(AXES):
        currents = dict(zip(AXES, (round(nominal_rms_current_a(c, v), 4) for c, v in zip(scales, vsense))))
    return {"profile": status.get("profile"), "axes": list(AXES), "current_scales": scales,
            "configured_vsense": vsense, "nominal_rms_current_a": currents, "basis": NOMINAL_CURRENT_BASIS,
            "matches_controls_export": not profile_problems(status)}


def minimum_duration_us(counts, max_rate: float | None = None) -> int:
    """Shortest duration the firmware's cubic profile accepts for these counts.

    control.md: a common cubic progress curve with peak rate and peak
    acceleration limits; impossible profiles are rejected. A cubic
    s = 3u² − 2u³ over N counts in T has peak rate 1.5 N/T and peak acceleration
    6 N/T², so T ≥ 1.5 N / max_rate (longer than N / max_rate) and
    T ≥ √(6 N / max_acceleration). `max_rate` is the controller's reported rate;
    None means CONSERVATIVE_MAX_RATE.
    """
    rate = float(max_rate or CONSERVATIVE_MAX_RATE)
    n = max(abs(int(c)) for c in counts)
    by_rate = 1.5 * n / rate * 1e6
    by_accel = math.sqrt(6.0 * n / MAX_ACCEL_COUNTS_S2) * 1e6
    need = max(MIN_DURATION_US, math.ceil(max(by_rate, by_accel) * 1.02) + 1)
    if need > MAX_DURATION_US:
        raise ValueError(f"{n} counts need {need} µs at {rate:g} counts/s, beyond {MAX_DURATION_US} µs")
    return int(need)


class ClientLogTail:
    """Reads records the controls `Client` appends to its `log_path` JSONL."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.offset = 0
        self._partial = b""

    def read_new(self) -> list[dict]:
        if not self.path.exists():
            return []
        with open(self.path, "rb") as fh:
            fh.seek(self.offset)
            data = fh.read()
        self.offset += len(data)
        lines = (self._partial + data).split(b"\n")
        self._partial = lines.pop()
        out = []
        for line in lines:
            if line.strip():
                out.append(json.loads(line))
        return out


def _classify_error(error: BaseException) -> tuple[str, str | None]:
    """Receipt status for an exception from Client.move().

    rejected: refused before any edge was issued (argument check or controller
    CommandRejected); fault/timeout: acceptance or completion unknown, so the
    take-up state is unknown afterwards.
    """
    text = str(error)
    rejected = getattr(host_modules().positioner, "CommandRejected", None)
    if isinstance(error, TimeoutError):
        return "timeout", None
    if isinstance(error, ValueError) or (rejected is not None and isinstance(error, rejected)):
        return "rejected", None
    if text.startswith("Motion fault: "):
        return "fault", text[len("Motion fault: "):]
    if text.startswith("Controller rejected command: "):
        return "rejected", None
    return "fault", None


class ReceiptError(RuntimeError):
    """The controls Client log cannot be tied to the move it should describe."""


def receipt_from_client_move(counts, duration_us: int, issued_mono_ns: int, returned_mono_ns: int,
                             result: dict | None, error: BaseException | None,
                             log_records: list[dict], clock_map: ClockMap | None, log_expected: bool = True):
    """Map one Client.move() call onto the session timeline. Returns a MoveOutcome.

    The move's sequence comes from the logged `MOVE6` host_command with these
    counts and duration. Its acceptance is the first later device reply of type
    `ack` whose `op` is `MOVE6` and whose `seq` is that sequence; an ack with the
    same sequence for another op (a late PING ack, say) is never used.
    complete_mono_ns is the host receipt of the first reply after that ack, from
    the same boot, whose `completed_seq` is the sequence; it follows the device's
    completion. completion_mapped_mono_ns places the device's `completed_us` on
    the host clock through `clock_map`, with its stated uncertainty. Device
    completion means issued edges ended, not that the gun settled.

    With `log_expected`, a move the Client reports done whose MOVE6 command,
    MOVE6 ack or completion reply is missing from the log raises ReceiptError.
    Without a log the receipt carries no ack, and completion is the return stamp.
    """
    from .moves import MoveOutcome

    expected = [int(duration_us), *[int(c) for c in counts]]
    seq = command_at = None
    for i, rec in enumerate(log_records):
        if rec.get("type") == "host_command" and rec.get("command", "").startswith("MOVE6 "):
            tokens = rec["command"].split()
            if len(tokens) == 10 and [int(t) for t in tokens[3:]] == expected:
                seq, command_at = int(tokens[2]), i
    ack_ns = ack_us = done_ns = ack_epoch = ack_boot = None
    other_ops = []
    for rec in log_records[command_at + 1:] if seq is not None else ():
        if rec.get("type") != "device_reply":
            continue
        device = rec.get("device", {})
        if ack_ns is None:
            if device.get("type") == "ack" and device.get("seq") == seq:
                if device.get("op") == "MOVE6":
                    ack_ns, ack_us, ack_epoch = rec["host_receive_ns"], device.get("time_us"), device.get("vm_epoch")
                    ack_boot = device.get("boot")
                else:
                    other_ops.append(device.get("op"))
            continue
        if done_ns is None and device.get("completed_seq") == seq and device.get("boot", ack_boot) == ack_boot:
            done_ns = rec["host_receive_ns"]
    exchanges = [{"host_send_ns": r["host_send_ns"], "host_recv_ns": r["host_receive_ns"],
                  "controller_us": r["device_time_us"], "boot": r.get("boot")}
                 for r in log_records if r.get("type") == "clock_bracket"]
    if error is None and result is not None:
        status, fault = "done", None
        if log_expected:
            ignored = f"; ack(s) with sequence {seq} for op {other_ops} were not used" if other_ops else ""
            if seq is None:
                raise ReceiptError(f"the controls Client log holds no MOVE6 command for {expected[0]} us and "
                                   f"counts {expected[1:]}; the move cannot be placed on the session timeline")
            if ack_ns is None:
                raise ReceiptError(f"the controls Client log holds no MOVE6 ack with sequence {seq}{ignored}; "
                                   "the move's acceptance cannot be placed on the session timeline")
            if done_ns is None:
                raise ReceiptError(f"the controls Client log holds no reply after the MOVE6 ack reporting "
                                   f"completed_seq {seq}; the move's completion cannot be placed on the timeline")
        elif seq is None and result.get("completed_seq"):
            seq = result["completed_seq"]
    else:
        status, fault = _classify_error(error) if error is not None else ("fault", None)
    completed_us = result.get("completed_us") if (result and status == "done") else None
    mapped = uncertainty = None
    if completed_us is not None and clock_map is not None:
        mapped, uncertainty = clock_map.to_host_ns(completed_us), clock_map.uncertainty_ns
    # Every status field the controller reported except `count` (kept as reported_counts): state, fault,
    # health, profile, current_scales, configured_vsense, vsense, microsteps, max_rate, vm_epoch, timer_ticks.
    controller = None if result is None else {k: v for k, v in result.items() if k != "count"}
    return MoveOutcome(
        status=status, issued_mono_ns=issued_mono_ns, returned_mono_ns=returned_mono_ns,
        ack_mono_ns=ack_ns, ack_controller_us=ack_us,
        complete_mono_ns=(done_ns if done_ns is not None else returned_mono_ns) if status == "done" else None,
        completed_controller_us=completed_us, completion_mapped_mono_ns=mapped,
        completion_mapping_uncertainty_ns=uncertainty,
        reported_counts=list(result["count"]) if result and "count" in result else None,
        controller=controller, driver_state=None, fault=fault, ack_vm_epoch=ack_epoch,
        vm_epoch=result.get("vm_epoch") if result else None,
        error=None if error is None else f"{type(error).__name__}: {error}", seq=seq,
        clock_exchanges=exchanges)


def unverified_receipt(issued_mono_ns: int, returned_mono_ns: int, result: dict, error: ReceiptError):
    """The record of a move the Client completed whose receipt was refused.

    Status `unverified`: no ack or completion times, the moved axes' take-up
    state becomes unknown, and a gated session halts. The returned status's
    counts and fields are kept.
    """
    from .moves import MoveOutcome

    return MoveOutcome(status="unverified", issued_mono_ns=issued_mono_ns, returned_mono_ns=returned_mono_ns,
                       reported_counts=list(result["count"]) if "count" in result else None,
                       controller={k: v for k, v in result.items() if k != "count"},
                       vm_epoch=result.get("vm_epoch"), error=f"ReceiptError: {error}")


class ControlsClientBackend:
    """Executes MoveCommands through a controls `Client` (real or test double).

    On construction it reads STATUS: `counts_per_mm` must equal the host
    geometry's COUNTS_PER_MM, and `max_rate` (bench or loaded-development
    profile) sets move durations; without it, CONSERVATIVE_MAX_RATE applies.
    The Client must be cleared, referenced at the physical central datum and
    armed, with its heartbeat running; `prepare()` makes those requests only when
    the caller states the datum has been established. After each move the
    driver rows (`gstat`, `drv_status`, `cs_actual`, `configured_cs`,
    `configured_vsense`, `sample_valid`, `microsteps`, `vsense`, `sample_us`) are
    read into the receipt when `read_drivers` is set. A receipt the Client log
    cannot support is recorded as `unverified` (see `receipt_from_client_move`).
    """

    def __init__(self, client, client_log_path: Path | None, clock: Clock | None = None,
                 read_drivers: bool = True):
        from .moves import BackendInfo
        self.client = client
        self.clock = clock or Clock()
        self.tail = ClientLogTail(client_log_path) if client_log_path else None
        self.read_drivers = read_drivers
        self._exchanges: deque = deque(maxlen=400)
        self._boot = None
        status = client.status()
        reported = status.get("counts_per_mm")
        if reported is not None and int(reported) != COUNTS_PER_MM:
            raise RuntimeError(f"controller reports {reported} counts/mm; host geometry has {COUNTS_PER_MM}")
        self.max_rate = int(status.get("max_rate") or CONSERVATIVE_MAX_RATE)
        self.max_rate_source = "status" if status.get("max_rate") else "conservative_default"
        self.last_status = status
        if self.tail:
            self._ingest(self.tail.read_new())
        self.info = BackendInfo(
            name="controls_client", kind="controller", moves_hardware=True,
            notes="firmware/src_gun_positioner/host/positioner.py Client.move(delta_counts6, duration_us)")

    @classmethod
    def connect(cls, port: str, client_log_path: Path, clock: Clock | None = None):
        client = host_modules().positioner.Client(port, str(client_log_path))
        return cls(client, client_log_path, clock)

    @classmethod
    def for_session(cls, port: str, writer, clock: Clock | None = None):
        """Connect with the Client's own JSONL log inside the session directory."""
        return cls.connect(port, Path(writer.path) / "controller-client.jsonl", clock)

    def prepare(self, datum_established: bool) -> list[dict]:
        """CLEAR, REF, ARM and heartbeat, as the controls console's clear/reference/arm."""
        if not datum_established:
            raise PermissionError("REF requires the physical central datum to be established first")
        replies = [self.client.request("CLEAR"), self.client.request("REF"), self.client.request("ARM")]
        self.client.start_heartbeat()
        return replies

    def status(self) -> dict:
        self.last_status = self.client.status()
        if self.last_status.get("max_rate"):
            self.max_rate, self.max_rate_source = int(self.last_status["max_rate"]), "status"
        return self.last_status

    def clock_map(self) -> ClockMap | None:
        usable = list(self._exchanges)
        return ClockMap.fit(usable) if len(usable) >= 2 else None

    def _ingest(self, records: list[dict]) -> None:
        for rec in records:
            if rec.get("type") == "clock_bracket":
                if rec.get("boot") != self._boot:
                    self._exchanges.clear()   # a reset starts a new device clock
                    self._boot = rec.get("boot")
                self._exchanges.append(ClockExchange(rec["host_send_ns"], rec["host_receive_ns"],
                                                     rec["device_time_us"]))

    def execute(self, cmd):
        issued = self.clock.monotonic_ns()
        result = error = None
        try:
            result = self.client.move(list(cmd.counts), cmd.duration_us)
        except Exception as exc:  # recorded, never retried: the controls host never retries a move
            error = exc
        returned = self.clock.monotonic_ns()
        drivers = None
        if self.read_drivers and hasattr(self.client, "drivers"):
            try:
                drivers = self.client.drivers()
            except Exception as exc:
                drivers = [{"error": f"{type(exc).__name__}: {exc}"}]
        records = self.tail.read_new() if self.tail else []
        self._ingest(records)
        try:
            outcome = receipt_from_client_move(cmd.counts, cmd.duration_us, issued, returned, result, error,
                                               records, self.clock_map(), log_expected=self.tail is not None)
        except ReceiptError as exc:
            outcome = unverified_receipt(issued, returned, result, exc)
        outcome.driver_state = drivers
        if result is not None:
            self.last_status = result
            if result.get("max_rate"):
                self.max_rate, self.max_rate_source = int(result["max_rate"]), "status"
        return outcome

    def stop(self) -> None:
        self.client.stop()
