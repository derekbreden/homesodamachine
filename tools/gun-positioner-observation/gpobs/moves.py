"""Move commands and receipts on the session timeline.

A move is six signed count deltas in the controls axis order (X, Y, Z, U, V, W),
`COUNTS_PER_MM` counts per mm of screw extension, at most `MAX_JOG_COUNTS` per
axis, with a duration in microseconds; these are the controls `Client.move()`
arguments. The duration is never shorter than the firmware's rate and
acceleration limits allow at the backend's `max_rate` (the controller's STATUS
value; 1,000 counts/s when unreported). `MoveRecorder` writes, for every move:

    move_command   cmd_id, counts, duration_us, purpose, trial_id, backend,
                   issued_mono_ns (host stamp before the backend is called)
    move_ack       ack_mono_ns (host receipt of the controller's MOVE6 ack for
                   the move's sequence), the controller's time_us and vm_epoch,
                   when the backend observed one
    move_complete  status; complete_mono_ns (host receipt of the completion
                   report); controller completed_us and its host-clock mapping
                   with uncertainty; reported issued counts; vm_epoch; every
                   other status field (state, fault, health, profile, current
                   scales, configured and decoded VSENSE, microsteps, max_rate,
                   timer_ticks); driver rows; fault and error text. `unverified`
                   is a move the controls Client completed whose log lacks its
                   MOVE6 command, ack or completion: the receipt is refused.

`vm_epoch` changes when the controller observes a motor-supply transition. A
change between receipts marks a supply cycle: frames between them are suspect,
and every axis's take-up state becomes unknown.
    clock_exchange host send/receive stamps around each controller time reply

A backend that can move hardware is refused unless `allow_hardware=True`.
Backends here and in `simulation.py` cannot: there is no laser, trigger or
emission vocabulary in this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .clock import Clock
from .controls import (AXES, CONSERVATIVE_MAX_RATE, MAX_DURATION_US, MAX_JOG_COUNTS, MIN_DURATION_US,
                       minimum_duration_us, split_target)

PURPOSES = ("probe_jog", "engage", "correction", "reversal_takeup", "return")


@dataclass(frozen=True)
class MoveCommand:
    cmd_id: str
    counts: tuple[int, ...]
    duration_us: int
    purpose: str
    trial_id: str | None = None

    def __post_init__(self):
        if len(self.counts) != len(AXES) or not all(isinstance(c, int) for c in self.counts):
            raise ValueError("a move is six integer count deltas in X, Y, Z, U, V, W order")
        if any(abs(c) > MAX_JOG_COUNTS for c in self.counts):
            raise ValueError(f"each axis delta is limited to ±{MAX_JOG_COUNTS} counts")
        if not any(self.counts):
            raise ValueError("the controller rejects a zero move; observe again instead")
        if not MIN_DURATION_US <= self.duration_us <= MAX_DURATION_US:
            raise ValueError(f"duration must be {MIN_DURATION_US}..{MAX_DURATION_US} µs")
        if self.purpose not in PURPOSES:
            raise ValueError(f"purpose must be one of {PURPOSES}")


@dataclass
class MoveOutcome:
    status: str                      # done | fault | stopped | rejected | timeout | unverified | not_executed
    issued_mono_ns: int
    returned_mono_ns: int
    ack_mono_ns: int | None = None
    ack_controller_us: int | None = None
    complete_mono_ns: int | None = None
    completed_controller_us: int | None = None
    completion_mapped_mono_ns: int | None = None
    completion_mapping_uncertainty_ns: float | None = None
    reported_counts: list[int] | None = None
    controller: dict | None = None
    driver_state: list | None = None
    fault: str | None = None
    error: str | None = None
    seq: int | None = None
    clock_exchanges: list = field(default_factory=list)
    ack_vm_epoch: int | None = None     # controller supply epoch in the ack
    vm_epoch: int | None = None         # controller supply epoch in the completion status


@dataclass(frozen=True)
class BackendInfo:
    name: str
    kind: str              # simulator | record_only | controller
    moves_hardware: bool
    notes: str = ""


class PositionerBackend(ABC):
    info: BackendInfo
    max_rate: int = CONSERVATIVE_MAX_RATE      # counts/s/axis peak, as the controller reports it

    @abstractmethod
    def execute(self, cmd: MoveCommand) -> MoveOutcome:
        """Perform (or decline) one move and return its receipt. Blocks until done."""

    def status(self) -> dict | None:
        """The controller's status dict, where the backend has one."""
        return None

    def stop(self) -> None:
        """Stop motion where the backend can."""


class RecordOnlyBackend(PositionerBackend):
    """Logs what would be sent and executes nothing."""

    def __init__(self, clock: Clock | None = None):
        self.clock = clock or Clock()
        self.max_rate = CONSERVATIVE_MAX_RATE
        self.info = BackendInfo("record_only", "record_only", False, "executes nothing")

    def execute(self, cmd: MoveCommand) -> MoveOutcome:
        now = self.clock.monotonic_ns()
        return MoveOutcome("not_executed", now, now, error="record-only backend")


class MoveRecorder:
    """Issues moves through one backend and writes their receipts.

    `direction` holds, per axis, the sign of the last executed nonzero delta
    (0 = unknown). A move that faults, times out or is stopped makes its axes'
    direction unknown, because a partly issued segment leaves the mechanism's
    take-up state unknown; a rejected move changes nothing.
    """

    def __init__(self, backend: PositionerBackend, writer, clock: Clock | None = None,
                 allow_hardware: bool = False):
        if backend.info.moves_hardware and not allow_hardware:
            raise PermissionError(f"backend {backend.info.name} moves hardware; pass allow_hardware=True")
        self.backend = backend
        self.writer = writer
        self.clock = clock or Clock()
        self.direction = [0] * len(AXES)
        self.counts: list[int] | None = None
        self.last_complete_ns: int | None = None
        self.last_controller: dict | None = None
        self.vm_epoch: int | None = None
        self._n = 0

    def controller_status(self) -> dict | None:
        """The controller's latest status: from the last receipt, else the backend."""
        if self.last_controller is None:
            status = self.backend.status()
            if status is not None:
                self.last_controller = {k: v for k, v in status.items() if k != "count"}
                if self.counts is None and "count" in status:
                    self.counts = list(status["count"])
                if status.get("vm_epoch") is not None and self.vm_epoch is None:
                    self.vm_epoch = status["vm_epoch"]
        return self.last_controller

    def execute(self, counts, purpose: str, trial_id: str | None = None,
                duration_us: int | None = None) -> tuple[MoveCommand, MoveOutcome]:
        counts = tuple(int(c) for c in counts)
        rate = getattr(self.backend, "max_rate", None) or CONSERVATIVE_MAX_RATE
        shortest = minimum_duration_us(counts, rate)
        if duration_us is not None and duration_us < shortest:
            raise ValueError(f"{duration_us} µs is shorter than {shortest} µs allowed at {rate} counts/s")
        duration = int(duration_us if duration_us is not None else shortest)
        cmd = MoveCommand(f"{self.writer.session_id[-4:]}-m{self._n:06d}", counts, duration, purpose, trial_id)
        self._n += 1
        issued = self.clock.monotonic_ns()
        self.writer.append("move_command", cmd_id=cmd.cmd_id, counts=list(counts), duration_us=duration,
                           purpose=purpose, trial_id=trial_id, backend=self.backend.info.name,
                           issued_mono_ns=issued, issued_wall_ns=self.clock.wall_ns(), max_rate=rate)
        outcome = self.backend.execute(cmd)
        for ex in outcome.clock_exchanges:
            self.writer.append("clock_exchange", host_send_ns=ex["host_send_ns"], host_recv_ns=ex["host_recv_ns"],
                               controller_us=ex["controller_us"], boot=ex.get("boot"))
        if outcome.ack_mono_ns is not None:
            self.writer.append("move_ack", cmd_id=cmd.cmd_id, accepted=True, reason=None,
                               ack_mono_ns=outcome.ack_mono_ns, controller_time_us=outcome.ack_controller_us,
                               vm_epoch=outcome.ack_vm_epoch)
        complete_ns = outcome.complete_mono_ns if outcome.complete_mono_ns is not None else outcome.returned_mono_ns
        self.writer.append(
            "move_complete", cmd_id=cmd.cmd_id, status=outcome.status, complete_mono_ns=complete_ns,
            controller_time_us=outcome.completed_controller_us, reported_counts=outcome.reported_counts,
            driver_state=outcome.driver_state, fault=outcome.fault, error=outcome.error,
            controller=outcome.controller, seq=outcome.seq, vm_epoch=outcome.vm_epoch,
            backend_issued_mono_ns=outcome.issued_mono_ns, returned_mono_ns=outcome.returned_mono_ns,
            completion_mapped_mono_ns=outcome.completion_mapped_mono_ns,
            completion_mapping_uncertainty_ns=outcome.completion_mapping_uncertainty_ns)
        if outcome.status == "done":
            for i, c in enumerate(counts):
                if c:
                    self.direction[i] = 1 if c > 0 else -1
            self.last_complete_ns = complete_ns
        elif outcome.status not in ("rejected", "not_executed"):
            for i, c in enumerate(counts):       # partly issued: take-up state unknown
                if c:
                    self.direction[i] = 0
        if outcome.reported_counts is not None:
            self.counts = list(outcome.reported_counts)
        if outcome.controller is not None:
            self.last_controller = outcome.controller
        for epoch in (outcome.ack_vm_epoch, outcome.vm_epoch):
            if epoch is None:
                continue
            if self.vm_epoch is not None and epoch != self.vm_epoch:
                self.direction = [0] * len(AXES)
                self.writer.append("session_note", author="move_recorder",
                                   text=f"controller vm_epoch {self.vm_epoch} -> {epoch} at {cmd.cmd_id}: "
                                        "supply cycle; take-up state unknown on every axis")
            self.vm_epoch = epoch
        return cmd, outcome

    def execute_split(self, delta, purpose: str, trial_id: str | None = None) -> list[tuple[MoveCommand, MoveOutcome]]:
        """A relative move of any size, split by the controls `split_target` into ≤MAX_JOG_COUNTS segments.

        Needs the issued-count position (from the last receipt or backend status)
        to check soft limits. Stops at the first segment that is not done.
        """
        current = self.counts
        if current is None:
            status = self.backend.status()
            current = list(status["count"]) if status and "count" in status else None
        if current is None:
            raise RuntimeError("issued-count position unknown; cannot check soft limits for a split move")
        target = [int(a) + int(d) for a, d in zip(current, delta)]
        done = []
        for segment in split_target(list(current), target, MAX_JOG_COUNTS):
            cmd, out = self.execute(segment, purpose, trial_id)
            done.append((cmd, out))
            if out.status != "done":
                break
        return done
