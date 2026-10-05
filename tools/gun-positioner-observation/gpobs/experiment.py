"""Dry learning runs: engagement, probe trials, closed-loop correction.

Works with any `moves.PositionerBackend` (through a `MoveRecorder`) and any
observer with `observe(trial_id, prev_obs_id, cmd_ids, not_before_ns)` that
writes an `observation` record: `capture.CameraObserver` for cameras,
`SimulatedObserver` for the simulator.

Every trial is logged between `trial_start` and `trial_end`; a trial that stops
on a move fault, a refused measurement or a missing observation ends with that
outcome and stays in the dataset.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import secrets

import numpy as np

from .capture import MeasurementRefused
from .clock import Clock
from .controls import AXES
from .proposal import CorrectionController, Observation

N_AXES = len(AXES)


@dataclass
class TrialPlan:
    trial_id: str
    purpose: str                 # probe | engage | closed_loop
    group: str                   # stratification label for held-out splits (the probed axis)
    steps: list                  # six-count tuples, or None for "observe again without moving"
    plan: dict = field(default_factory=dict)


PROBE_PATTERN = "+s x r, hold, -s x 2r, hold, +s x r (net zero)"


def probe_trial(axis: int, size: int, repeats: int = 3, tag: str = "") -> TrialPlan:
    """+s ×r, hold, −s ×2r, hold, +s ×r on one axis.

    Both directions, two reversals and two drift holds, ending where it began,
    so a long run of probes stays centred in the travel.
    """
    v = [0] * N_AXES
    v[axis] = int(size)
    neg = [-c for c in v]
    steps = [tuple(v)] * repeats + [None] + [tuple(neg)] * (2 * repeats) + [None] + [tuple(v)] * repeats
    tid = f"probe-{AXES[axis]}-{size}-{tag or secrets.token_hex(3)}"
    return TrialPlan(tid, "probe", AXES[axis], steps, {"axis": AXES[axis], "size_counts": size, "repeats": repeats})


class SimulatedObserver:
    """Observations of a SimulatedMechanism: N frames of noisy features, averaged."""

    def __init__(self, mechanism, writer, clock: Clock, frames: int = 8, frame_interval_ns: int = 33_333_333,
                 seed: int = 3):
        self.mechanism, self.writer, self.clock = mechanism, writer, clock
        self.frames, self.frame_interval_ns = frames, frame_interval_ns
        self.rng = np.random.default_rng(seed)
        self._n = 0

    def observe(self, trial_id, prev_obs_id, cmd_ids, not_before_ns: int) -> Observation:
        self.clock.sleep_ns(not_before_ns - self.clock.monotonic_ns())
        names = self.mechanism.truth.feature_names
        rows, t0 = [], self.clock.monotonic_ns()
        for _ in range(self.frames):
            self.mechanism.advance_to(self.clock.monotonic_ns())
            rows.append(self.mechanism.frame_features())
            self.clock.sleep_ns(self.frame_interval_ns)
        t1 = self.clock.monotonic_ns() - self.frame_interval_ns
        rows = np.array(rows)
        if self.rng.random() < self.mechanism.truth.outlier_prob:   # a sustained misdetection
            f = int(self.rng.integers(len(names)))
            rows[:, f] += self.mechanism.truth.outlier_scale * self.rng.choice([-1, 1])
        mean = rows.mean(axis=0)
        sem = rows.std(axis=0, ddof=1) / np.sqrt(len(rows))
        values = {n: float(v) for n, v in zip(names, mean)}
        sigma = {n: float(v) for n, v in zip(names, sem)}
        conf = {n: 1.0 for n in names}
        obs_id = f"s{self._n:06d}"
        self._n += 1
        self.writer.append("observation", obs_id=obs_id, trial_id=trial_id, prev_obs_id=prev_obs_id,
                           cmd_ids=list(cmd_ids), t_start_ns=t0, t_end_ns=t1, values=values, sigma=sigma,
                           confidence=conf, n_frames={"simulated": self.frames}, frames={}, source="simulator",
                           extractors={"simulator": "true features + noise"})
        return Observation(obs_id, t0, t1, values, sigma, conf, trial_id)


@dataclass
class TrialResult:
    trial_id: str
    outcome: str
    observations: list
    commands: list
    reason: str | None = None
    steps_moved: list = field(default_factory=list)   # per observation after the first: was there a move


class Runner:
    def __init__(self, recorder, observer, writer, clock: Clock, settle_s: float = 0.5):
        self.recorder, self.observer, self.writer, self.clock = recorder, observer, writer, clock
        self.settle_ns = int(settle_s * 1e9)
        self._trials = 0
        self.results: list[TrialResult] = []

    def tag(self) -> str:
        """Trial-id suffix unique within the session and tied to it."""
        self._trials += 1
        return f"{self.writer.session_id[-4:]}-{self._trials:04d}"

    def _observe(self, trial_id, prev, cmd_ids):
        base = self.recorder.last_complete_ns or self.clock.monotonic_ns()
        return self.observer.observe(trial_id, prev.obs_id if prev else None, cmd_ids,
                                     max(base + self.settle_ns, self.clock.monotonic_ns()))

    def _end(self, trial_id, outcome, reason=None):
        self.writer.append("trial_end", trial_id=trial_id, outcome=outcome, reason=reason)

    def run_trial(self, plan: TrialPlan) -> TrialResult:
        self.writer.append("trial_start", trial_id=plan.trial_id, purpose=plan.purpose,
                           plan={**plan.plan, "group": plan.group}, direction_state=list(self.recorder.direction))
        result = TrialResult(plan.trial_id, "completed", [], [])
        try:
            obs = self._observe(plan.trial_id, None, [])
            result.observations.append(obs)
            for step in plan.steps:
                cmd_ids = []
                if step is not None:
                    purpose = "engage" if plan.purpose == "engage" else "probe_jog"
                    cmd, out = self.recorder.execute(step, purpose, plan.trial_id)
                    result.commands.append(cmd.cmd_id)
                    if out.status != "done":
                        result.outcome = "fault" if out.status in ("fault", "timeout", "stopped") else "failed"
                        result.reason = f"move {cmd.cmd_id} {out.status}"
                        break
                    cmd_ids = [cmd.cmd_id]
                obs = self._observe(plan.trial_id, obs, cmd_ids)
                result.observations.append(obs)
                result.steps_moved.append(bool(cmd_ids))
        except MeasurementRefused as exc:
            result.outcome, result.reason = "failed", f"measurement refused: {exc.reasons}"
        self._end(plan.trial_id, result.outcome, result.reason)
        self.results.append(result)
        return result

    def engage(self, counts: int = 320, repeats: int = 2, axes=None) -> TrialResult:
        """Positive runs on the given axes (all by default) so their take-up state becomes known."""
        chosen = range(N_AXES) if axes is None else axes
        step = tuple(int(counts) if i in chosen else 0 for i in range(N_AXES))
        return self.run_trial(TrialPlan(f"engage-{self.tag()}", "engage", "engage", [step] * repeats,
                                        {"counts": counts, "repeats": repeats,
                                         "axes": [AXES[i] for i in chosen]}))

    @staticmethod
    def moving_steps(result: TrialResult, min_motion_z: float) -> int:
        """Move steps whose largest feature change exceeds `min_motion_z` times its noise.

        Steps inside a reversal's take-up legitimately show no motion, so motion
        counts as observed when at least two move steps show it.
        """
        count = 0
        obs = result.observations
        for i, (a, b) in enumerate(zip(obs, obs[1:])):
            names = [n for n in a.values if a.values.get(n) is not None and b.values.get(n) is not None]
            if not names or i >= len(result.steps_moved) or not result.steps_moved[i]:
                continue
            dy = np.array([b.values[n] - a.values[n] for n in names])
            sg = np.array([np.hypot(a.sigma.get(n) or 0, b.sigma.get(n) or 0) for n in names])
            count += float(np.max(np.abs(dy) / np.maximum(sg, 1e-9))) >= min_motion_z
        return count

    def identify(self, axes=None, sizes=(16, 32, 64, 256), trials_per_size: int = 2, repeats: int = 3,
                 min_motion_z: float = 8.0, should_stop=None) -> list[TrialResult]:
        """Probe each axis, enlarging the jog only after the previous size produced observed motion.

        The default sizes are the commissioning sequence's 16, 32, 64 and 256 counts.
        """
        results = []
        for axis in (range(N_AXES) if axes is None else axes):
            for size in sizes:
                if should_stop is not None and should_stop():
                    return results
                batch = [self.run_trial(probe_trial(axis, size, repeats, self.tag())) for _ in range(trials_per_size)]
                results += batch
                done = [r for r in batch if r.outcome == "completed"]
                if not done or max(self.moving_steps(r, min_motion_z) for r in done) < 2:
                    self.writer.append("session_note", author="runner",
                                       text=f"{AXES[axis]}: no clear motion at {size} counts; not enlarging")
                    break
        return results

    def closed_loop(self, controller: CorrectionController, target: dict, max_iters: int = 40,
                    tag: str = "") -> TrialResult:
        trial_id = f"loop-{tag or self.tag()}"
        self.writer.append("trial_start", trial_id=trial_id, purpose="closed_loop", plan={"target": target},
                           direction_state=list(self.recorder.direction))
        result = TrialResult(trial_id, "failed", [], [])
        try:
            obs = self._observe(trial_id, None, [])
            result.observations.append(obs)
            for _ in range(max_iters):
                p = controller.propose(obs, target, self.clock.monotonic_ns(), self.recorder.last_complete_ns,
                                       self.recorder.counts, list(self.recorder.direction),
                                       self.recorder.controller_status())
                self.writer.append("proposal", proposal={**p.as_dict(), "trial_id": trial_id})
                if p.reasons == ["observation_inconsistent_with_last_move"]:
                    obs = self._observe(trial_id, obs, [])          # observe again without moving
                    result.observations.append(obs)
                    result.steps_moved.append(False)
                    continue
                if p.status == "zero":
                    result.reason = ";".join(p.reasons)
                    if p.reasons == ["within_tolerance"]:
                        result.outcome = "completed"
                    break
                cmd, out = self.recorder.execute(p.counts, p.purpose, trial_id)
                result.commands.append(cmd.cmd_id)
                if out.status != "done":
                    result.outcome, result.reason = "fault", f"move {cmd.cmd_id} {out.status}"
                    break
                obs = self._observe(trial_id, obs, [cmd.cmd_id])
                result.observations.append(obs)
                result.steps_moved.append(True)
            else:
                result.reason = f"not within tolerance after {max_iters} proposals"
        except MeasurementRefused as exc:
            result.outcome, result.reason = "failed", f"measurement refused: {exc.reasons}"
        self._end(trial_id, result.outcome, result.reason)
        return result
