"""Bounded correction proposals with no-motion defaults. Nothing here moves hardware.

The step itself is computed by the controls package's
`visual_servo.correction(jacobian, feature_error, trust_mm)`, which solves the
normal equations and scales the result so no screw change exceeds `trust_mm`.
This module feeds it a weighted, column-scaled Jacobian with damping rows
appended (`[W·J·S; λ·I]`, `[W·e; 0]`), which makes its normal equations the
damped least-squares system, and chooses λ so the step lies inside the trust
region. Around that core it decides whether any motion is proposed at all.

Zero motion is proposed, with reasons, when:
  * there is no model, no validation report, a report for a different model,
    or a report that did not pass (`model_not_validated`);
  * the controller status shows drivers not OK, microsteps unverified (null),
    a fault, or no physical reference;
  * a required feature is missing, its confidence is below `min_confidence`, or
    its uncertainty exceeds `max_sigma`;
  * the observation is older than `max_obs_age_s`, or began before the last
    move's completion plus `settle_s` (stale or unsettled data);
  * no validated axis-direction can act on the error, or the allowed axes
    cannot observe it (`insufficiently_observable`);
  * the undamped step exceeds the trust region by more than
    `max_unconstrained_ratio` (the target is outside the local model's range);
  * the rounded step is zero, or exceeds a per-axis bound or the controller
    soft limits;
  * the predicted feature change is below `min_predicted_snr` times its noise;
  * an axis to be moved has an unknown take-up state.
`within_tolerance` is the zero-motion result when the target is already met.

Per-axis bounds: the column scaling S makes one unit equal one per-axis maximum
step, so `||u/max_step||₂ ≤ trust_radius ≤ 1` keeps every axis within its bound.
Only axis-directions listed as validated by the held-out report are used.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np

from .controls import AXES, COUNTS_PER_MM, MAX_JOG_COUNTS, SOFT_MAX, SOFT_MIN, host_modules, mm_to_count
from .response import N_AXES, ResponseModel
from .validation import ValidationReport


@dataclass
class ProposalConfig:
    max_step_counts: tuple = (64,) * N_AXES   # 0.01 mm screw extension: commissioning's initial trust region
    trust_radius: float = 1.0
    max_unconstrained_ratio: float = 4.0
    tolerance: float | dict = 0.5           # feature units; weights are 1/tolerance
    max_obs_age_s: float = 5.0
    settle_s: float = 0.5
    min_confidence: float = 0.5
    max_sigma: float | None = None
    min_predicted_snr: float = 2.0
    base_damping: float = 1e-4              # relative to the largest singular value
    min_singular_ratio: float = 1e-3
    features: list | None = None
    soft_min: tuple = SOFT_MIN
    soft_max: tuple = SOFT_MAX


@dataclass
class Observation:
    obs_id: str
    t_start_ns: int
    t_end_ns: int
    values: dict
    sigma: dict
    confidence: dict
    trial_id: str | None = None


@dataclass
class Proposal:
    status: str                       # move | zero
    counts: list
    purpose: str = "correction"
    reasons: list = field(default_factory=list)
    error: dict = field(default_factory=dict)
    predicted_change: dict = field(default_factory=dict)
    predicted_error_after: dict = field(default_factory=dict)
    unconstrained_ratio: float | None = None
    scaled_norm: float | None = None
    damping: float | None = None
    reversal_axes: list = field(default_factory=list)
    model_id: str | None = None
    obs_id: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def _zero(reasons, **kw) -> Proposal:
    return Proposal(status="zero", counts=[0] * N_AXES, reasons=list(reasons), **kw)


def _tolerances(cfg: ProposalConfig, names) -> np.ndarray:
    if isinstance(cfg.tolerance, dict):
        return np.array([float(cfg.tolerance[n]) for n in names])
    return np.full(len(names), float(cfg.tolerance))


def solve_step(j_counts: np.ndarray, error: np.ndarray, weights: np.ndarray, max_step: np.ndarray,
               allowed: np.ndarray, trust_radius: float, base_damping: float,
               max_ratio: float, min_singular_ratio: float):
    """Damped, trust-bounded step in counts via visual_servo.correction.

    Returns (counts_float, info) or (None, reason).
    """
    vs = host_modules().visual_servo
    max_step_mm = max_step / COUNTS_PER_MM
    a = (weights[:, None] * j_counts * COUNTS_PER_MM) * max_step_mm[None, :]   # per unit of max step
    a[:, ~allowed] = 0.0                     # a held axis has no effect, so its solution is zero
    b = weights * error
    n_allowed = int(np.count_nonzero(allowed))
    sv = np.linalg.svd(a[:, allowed], compute_uv=False) if n_allowed else np.zeros(0)
    if n_allowed == 0 or len(sv) < n_allowed or sv[0] <= 0 or sv[-1] / sv[0] < min_singular_ratio:
        return None, "insufficiently_observable"

    def step(lam: float, trust: float) -> np.ndarray:
        damp = np.where(allowed, lam, sv[0])
        rows = np.vstack([a, np.diag(damp)]).tolist()
        rhs = np.concatenate([b, np.zeros(N_AXES)]).tolist()
        return np.array(vs.correction(rows, rhs, trust_mm=trust))

    lam0 = base_damping * sv[0]
    u0 = step(lam0, 1e12)
    norm0 = float(np.linalg.norm(u0))
    ratio = norm0 / trust_radius
    if ratio > max_ratio:
        return None, f"target_outside_trust_region (undamped step {ratio:.2f} x trust radius)"
    lam = lam0
    if norm0 > trust_radius:
        lo, hi = lam0, lam0 * 10
        while np.linalg.norm(step(hi, 1e12)) > trust_radius:
            hi *= 10
        for _ in range(60):
            mid = np.sqrt(lo * hi)
            if np.linalg.norm(step(mid, 1e12)) > trust_radius:
                lo = mid
            else:
                hi = mid
        lam = hi
    u = step(lam, 1.0)                       # visual_servo bounds every axis to one max step
    u[~allowed] = 0.0
    return u * max_step, {"unconstrained_ratio": ratio, "scaled_norm": float(np.linalg.norm(u)),
                          "damping": float(lam)}


def controller_reasons(status: dict | None) -> list[str]:
    """No-motion reasons from the controller's latest status (none when no status is given)."""
    if status is None:
        return []
    reasons = []
    if status.get("drivers_ok") is not True:
        reasons.append("drivers_not_ok")
    micro = status.get("microsteps")
    if micro is None or (isinstance(micro, list) and any(m is None for m in micro)):
        reasons.append("microsteps_unverified")
    if status.get("state") == "fault" or status.get("fault") not in (None, "none"):
        reasons.append(f"controller_fault:{status.get('fault')}")
    if status.get("referenced") is False:
        reasons.append("controller_not_referenced")
    return reasons


def propose(model: ResponseModel | None, report: ValidationReport | None, obs: Observation | None,
            target: dict, cfg: ProposalConfig, now_ns: int, last_complete_ns: int | None,
            counts_now=None, direction=None, controller_status: dict | None = None, hold=()) -> Proposal:
    """One bounded correction, or zero motion with reasons. `hold` names axes kept still."""
    if model is None:
        return _zero(["no_model"])
    if report is None:
        return _zero(["no_validation_report"], model_id=model.model_id)
    if report.model_id != model.model_id:
        return _zero(["validation_report_is_for_another_model"], model_id=model.model_id)
    if not report.passed:
        return _zero(["model_not_validated"] + list(report.reasons), model_id=model.model_id)
    blocked = controller_reasons(controller_status)
    if blocked:
        return _zero(blocked, model_id=model.model_id)
    if obs is None:
        return _zero(["no_observation"], model_id=model.model_id)
    names = list(cfg.features or model.feature_names)
    idx = [model.feature_names.index(n) for n in names]
    reasons = []
    for n in names:
        v = obs.values.get(n)
        if v is None or not np.isfinite(v):
            reasons.append(f"missing_feature:{n}")
        elif (obs.confidence.get(n) or 0.0) < cfg.min_confidence:
            reasons.append(f"low_confidence:{n}")
        elif cfg.max_sigma is not None and not (obs.sigma.get(n, np.inf) <= cfg.max_sigma):
            reasons.append(f"uncertainty_too_high:{n}")
        if target.get(n) is None:
            reasons.append(f"missing_target:{n}")
    if now_ns - obs.t_end_ns > cfg.max_obs_age_s * 1e9:
        reasons.append("stale_observation")
    if last_complete_ns is not None and obs.t_start_ns < last_complete_ns + cfg.settle_s * 1e9:
        reasons.append("observation_not_settled_after_last_move")
    common = {"model_id": model.model_id, "obs_id": obs.obs_id}
    if reasons:
        return _zero(reasons, **common)
    values = np.array([obs.values[n] for n in names], dtype=float)
    err = np.array([target[n] for n in names], dtype=float) - values
    tol = _tolerances(cfg, names)
    error = {n: float(e) for n, e in zip(names, err)}
    if np.all(np.abs(err) <= tol):
        return _zero(["within_tolerance"], error=error, **common)
    validated = set(report.validated_axis_directions)
    held = np.array([a in set(hold) for a in AXES])
    plus_ok = np.array([a + "+" in validated for a in AXES]) & ~held
    minus_ok = np.array([a + "-" in validated for a in AXES]) & ~held
    allowed = plus_ok | minus_ok
    if not np.any(allowed):
        return _zero(["no_axis_available"], error=error, **common)
    weights = 1.0 / tol
    max_step = np.array(cfg.max_step_counts, dtype=float)
    jp, jm = model.j_plus[idx], model.j_minus[idx]
    # Each moving axis uses its J⁺ or J⁻ column according to the sign it moves in;
    # start from the mean column where both directions are validated and iterate.
    signs = np.where(plus_ok & ~minus_ok, 1, np.where(minus_ok & ~plus_ok, -1, 0))
    for _ in range(2 * N_AXES + 2):
        j = np.where(signs[None, :] > 0, jp, np.where(signs[None, :] < 0, jm, 0.5 * (jp + jm)))
        u, info = solve_step(np.nan_to_num(j), err, weights, max_step, allowed, cfg.trust_radius,
                             cfg.base_damping, cfg.max_unconstrained_ratio, cfg.min_singular_ratio)
        if u is None:
            return _zero([info], error=error, **common)
        new = np.sign(np.round(u)).astype(int)
        bad = allowed & (((new > 0) & ~plus_ok) | ((new < 0) & ~minus_ok))
        if np.any(bad):
            allowed = allowed & ~bad          # that direction is not validated: hold the axis
            if not np.any(allowed):
                return _zero(["needed_axis_direction_not_validated"], error=error, **common)
            continue
        moving = allowed & (new != 0)
        if np.all(new[moving] == signs[moving]):
            break
        signs = np.where(moving, new, signs)
    else:
        return _zero(["direction_selection_did_not_settle"], error=error, **common)
    counts = np.array([mm_to_count(float(v / COUNTS_PER_MM)) for v in u], dtype=int)
    if np.any(np.abs(counts) > max_step) or np.any(np.abs(counts) > MAX_JOG_COUNTS):
        return _zero(["exceeds_axis_bound"], error=error, **common)
    if not np.any(counts):
        return _zero(["step_below_one_count"], error=error, **common)
    if counts_now is not None:
        end = np.asarray(counts_now) + counts
        if np.any(end < np.asarray(cfg.soft_min)) or np.any(end > np.asarray(cfg.soft_max)):
            return _zero(["exceeds_travel_bounds"], error=error, **common)
    j_used = np.nan_to_num(np.where(counts[None, :] > 0, jp, jm))
    pred = j_used @ counts
    noise = np.array([max(obs.sigma.get(n) or 0.0, float(model.residual_scale[i])) for n, i in zip(names, idx)])
    if np.max(np.abs(pred) / np.maximum(noise, 1e-12)) < cfg.min_predicted_snr:
        return _zero(["predicted_change_below_noise"], error=error, **common)
    reversal = []
    if direction is not None:
        for jx, c in enumerate(counts):
            if c and direction[jx] == 0:
                return _zero([f"takeup_state_unknown:{AXES[jx]}"], error=error, **common)
            if c and np.sign(c) != direction[jx]:
                reversal.append(AXES[jx])
    return Proposal(status="move", counts=[int(c) for c in counts], reasons=[], error=error,
                    predicted_change={n: float(p) for n, p in zip(names, pred)},
                    predicted_error_after={n: float(e - p) for n, e, p in zip(names, err, pred)},
                    unconstrained_ratio=info["unconstrained_ratio"], scaled_norm=info["scaled_norm"],
                    damping=info["damping"], reversal_axes=reversal, **common)


class CorrectionController:
    """Stateful wrapper: evaluates each executed move, takes up reversals, guards stalls.

    After every move the observed feature change is fitted as per-axis fractions
    of each commanded axis's predicted change (least squares in noise units).

    * A poor fit (chi-square per degree of freedom above `innovation_limit`) means
      the change is not explained by the move: a misdetection or a disturbance.
      Zero motion is proposed (`observation_inconsistent_with_last_move`) and the
      caller observes again; the move is evaluated against the next consistent
      observation. If two observations after the move agree with each other but
      not with the one before it, that earlier one was bad: the move's counts are
      left unverified and the loop continues. Otherwise repeated inconsistency
      stops the loop.
    * A reversal is taken up on that axis alone: one step of the estimated
      dead-band less a margin (`takeup_bulk`), then steps of twice the
      detectable motion, each evaluated, until motion is observed on the axis.
      The estimated dead-band is never added to a correction. A proposed
      reversal smaller than `reversal_threshold` is held instead unless the
      error cannot be reduced without it; one whose need is below a take-up
      step is never taken, because the step that ends a take-up overshoots by
      about that much (`remaining_error_below_reversal_resolution`). Once a
      take-up has begun only a significant opposite need ends it, and an unknown
      take-up state (a fault or supply cycle) ends it with zero motion.
    * Counts commanded on an axis without verified motion accumulate; beyond
      `takeup_limit_factor` x its dead-band plus one take-up step the axis is
      reported unresponsive, and `stall_limit` detectable corrections in a row
      that produce under a quarter of their predicted motion stop the loop.
      Neither lets an error accumulate into larger commands while the mechanism
      is stationary.
    * The error (in tolerance units) must improve by `1 - progress_fraction`
      within `progress_window` observations; otherwise zero motion is proposed
      (`no_progress_at_precision_floor`). Reversal take-up limits how finely the
      error can be closed, and a tolerance finer than that would cycle.
    """

    def __init__(self, model: ResponseModel, report: ValidationReport, cfg: ProposalConfig,
                 takeup_limit_factor: float = 2.0, stall_limit: int = 2, motion_z: float = 4.0,
                 reversal_fraction: float = 0.25, innovation_limit: float = 16.0, max_inconsistent: int = 2,
                 bulk_margin: float = 0.1, progress_window: int = 15, progress_fraction: float = 0.9,
                 hold=()):
        self.model, self.report, self.cfg = model, report, cfg
        self.hold = tuple(hold)                 # axes this controller never moves
        self.takeup_limit_factor, self.stall_limit, self.motion_z = takeup_limit_factor, stall_limit, motion_z
        self.reversal_fraction, self.innovation_limit, self.max_inconsistent = (reversal_fraction,
                                                                                 innovation_limit, max_inconsistent)
        self.bulk_margin = bulk_margin
        self.progress_window, self.progress_fraction = progress_window, progress_fraction
        self.best_error = np.inf
        self.since_best = 0
        self.takeup_axis: int | None = None
        self.takeup_sign = 0
        self.takeup_accum = 0
        self.unverified = np.zeros(N_AXES)
        self.unresponsive: set[str] = set()
        self.stalls = 0
        self.inconsistent = 0
        self.pending: tuple[Proposal, Observation] | None = None
        self.suspect_obs: Observation | None = None
        self.last: Proposal | None = None
        self.names = list(cfg.features or model.feature_names)
        self.idx = [model.feature_names.index(n) for n in self.names]
        self.evaluations: list[dict] = []

    # -- sizes ------------------------------------------------------------------------------
    def _column(self, axis: int, sign: int) -> np.ndarray:
        return np.nan_to_num((self.model.j_plus if sign > 0 else self.model.j_minus)[self.idx, axis])

    def _scale(self) -> np.ndarray:
        return np.nan_to_num(self.model.residual_scale[self.idx], nan=1.0)

    def detectable_counts(self, axis: int, sign: int) -> float:
        """Counts whose predicted change reaches `motion_z` noise units on this axis."""
        col = self._column(axis, sign) / self._scale()
        return self.motion_z / max(float(np.linalg.norm(col)), 1e-12)

    def takeup_step(self, axis: int, sign: int) -> int:
        """Counts per small take-up step: twice the detectable motion."""
        return int(np.clip(np.ceil(2 * self.detectable_counts(axis, sign)), 1, self.cfg.max_step_counts[axis]))

    def takeup_bulk(self, axis: int) -> int:
        """First take-up step: the estimated dead-band less a margin, when that exceeds two small steps.

        The margin is the largest of the fitted dead-band's profile half-width,
        two small steps and `bulk_margin` of the dead-band (variation from place to
        place along the screw). The step stays inside the estimate, so no output
        motion is expected; it is still evaluated, and motion observed early ends
        the take-up there.
        """
        b = float(self.model.deadband[axis])
        hw = float(np.nan_to_num(self.model.deadband_halfwidth[axis], nan=b))
        small = self.takeup_step(axis, 1)
        bulk = int(b - max(hw, 2 * small, self.bulk_margin * b))
        return min(bulk, int(self.cfg.max_step_counts[axis])) if bulk >= 2 * small else 0

    def reversal_threshold(self, axis: int, sign: int) -> int:
        """A proposed reversal smaller than this is held instead of taken up."""
        return max(2 * self.takeup_step(axis, sign), int(self.reversal_fraction * self.cfg.max_step_counts[axis]))

    def axis_limit(self, axis: int, sign: int) -> float:
        return self.takeup_limit_factor * float(self.model.deadband[axis]) + self.takeup_step(axis, sign)

    # -- evaluation of the last move --------------------------------------------------------
    def _evaluate(self, obs: Observation, before: Observation, move: Proposal) -> dict:
        c = np.array(move.counts, dtype=float)
        moving = np.nonzero(c)[0]
        sig = np.array([np.hypot(obs.sigma.get(n) or 0, before.sigma.get(n) or 0) for n in self.names])
        sig = np.maximum(sig, self._scale())
        dy = np.array([obs.values[n] - before.values[n] for n in self.names]) / sig
        cols = np.stack([self._column(j, int(np.sign(c[j]))) * c[j] / sig for j in moving], axis=1)
        frac, *_ = np.linalg.lstsq(cols, dy, rcond=None)
        resid = dy - cols @ frac
        dof = len(dy) - len(moving)
        chi2 = float(resid @ resid) / dof if dof > 0 else 0.0
        out = {"chi2_per_dof": chi2, "axes": {}}
        for k, j in enumerate(moving):
            observed = float(frac[k] * c[j])
            out["axes"][AXES[j]] = {"commanded": int(c[j]), "observed_counts": observed,
                                    "detectable_counts": self.detectable_counts(j, int(np.sign(c[j])))}
        out["suspect"] = dof > 0 and chi2 > self.innovation_limit
        return out

    def _progress(self, obs: Observation, target: dict) -> str | None:
        """No-progress guard: the error must improve within `progress_window` evaluated observations.

        Near the mechanism's precision floor every reversal's completing step can
        overshoot by up to one small take-up step; a tolerance finer than that
        would otherwise cycle through reversals indefinitely.
        """
        if obs is None or any(obs.values.get(n) is None or target.get(n) is None for n in self.names):
            return None
        tol = _tolerances(self.cfg, self.names)
        err = float(np.max(np.abs(np.array([target[n] - obs.values[n] for n in self.names]) / tol)))
        if err < self.progress_fraction * self.best_error:
            self.best_error, self.since_best = err, 0
        elif not (self.last is not None and self.last.purpose == "reversal_takeup"):
            self.since_best += 1           # take-up steps are not expected to reduce the error
        if err > 1.0 and self.since_best >= self.progress_window:
            return (f"no_progress_at_precision_floor (best {self.best_error:.2f} x tolerance, "
                    f"{self.since_best} observations without {1 - self.progress_fraction:.0%} improvement)")
        return None

    def _agree(self, a: Observation, b: Observation) -> bool:
        """Two observations of an unmoved mechanism agree within noise."""
        sig = np.maximum(np.array([np.hypot(a.sigma.get(n) or 0, b.sigma.get(n) or 0) for n in self.names]),
                         self._scale())
        d = np.array([a.values[n] - b.values[n] for n in self.names]) / sig
        return float(d @ d) / len(d) <= self.innovation_limit

    def _apply(self, ev: dict, move: Proposal) -> None:
        if move.purpose == "reversal_takeup":
            a = ev["axes"][AXES[self.takeup_axis]]
            if a["observed_counts"] * self.takeup_sign >= a["detectable_counts"]:
                self.unverified[self.takeup_axis] = 0
                self.takeup_axis, self.takeup_accum = None, 0
            elif self.takeup_accum > self.axis_limit(self.takeup_axis, self.takeup_sign):
                self.unresponsive.add(AXES[self.takeup_axis])
            return
        detectable_failures = detectable_moves = 0
        for name, a in ev["axes"].items():
            j = AXES.index(name)
            sign = np.sign(a["commanded"])
            moved = a["observed_counts"] * sign >= max(a["detectable_counts"], 0.25 * abs(a["commanded"]))
            if moved:
                self.unverified[j] = 0
            else:
                self.unverified[j] += abs(a["commanded"])
                if self.unverified[j] > self.axis_limit(j, int(sign)):
                    self.unresponsive.add(name)
            if abs(a["commanded"]) >= 2 * a["detectable_counts"]:
                detectable_moves += 1
                detectable_failures += a["observed_counts"] * sign < 0.25 * abs(a["commanded"])
        if detectable_moves:
            self.stalls = self.stalls + 1 if detectable_failures == detectable_moves else 0

    # -- proposals --------------------------------------------------------------------------
    def _plain(self, obs, target, now_ns, last_complete_ns, counts_now, direction, status) -> Proposal:
        """A correction with insignificant reversals held: noise-sized sign flips cost a take-up cycle.

        If holding them leaves no useful motion, the first proposal's reversals are
        used, those whose need is at least one take-up step; when none is, zero
        motion is proposed (`remaining_error_below_reversal_resolution`).
        """
        first = propose(self.model, self.report, obs, target, self.cfg, now_ns, last_complete_ns, counts_now,
                        direction, status, hold=self.hold)
        if first.status != "move" or not first.reversal_axes:
            return first
        p, held = first, []
        for _ in range(len(AXES)):
            small = [a for a in p.reversal_axes if a not in held and abs(p.counts[AXES.index(a)])
                     < self.reversal_threshold(AXES.index(a), int(np.sign(p.counts[AXES.index(a)])))]
            if not small:
                return p
            trial = propose(self.model, self.report, obs, target, self.cfg, now_ns, last_complete_ns,
                            counts_now, direction, status, hold=self.hold + tuple(held + small))
            if trial.status != "move" and trial.reasons != ["within_tolerance"]:
                break
            held += small
            p = trial
            if p.status != "move" or not p.reversal_axes:
                return p
        resolvable = [a for a in first.reversal_axes
                      if abs(first.counts[AXES.index(a)])
                      >= self.takeup_step(AXES.index(a), int(np.sign(first.counts[AXES.index(a)])))]
        if not resolvable:
            return _zero([f"remaining_error_below_reversal_resolution:{','.join(first.reversal_axes)}"],
                         error=first.error, model_id=first.model_id, obs_id=first.obs_id)
        first.reversal_axes = sorted(resolvable, key=lambda a: -abs(first.counts[AXES.index(a)]))
        return first

    def propose(self, obs: Observation, target: dict, now_ns: int, last_complete_ns: int | None,
                counts_now=None, direction=None, controller_status: dict | None = None) -> Proposal:
        if self.pending is not None and obs is not None:
            move, before = self.pending
            if all(obs.values.get(n) is not None and before.values.get(n) is not None for n in self.names):
                ev = self._evaluate(obs, before, move)
                self.evaluations.append({"obs_id": obs.obs_id, **ev})
                if ev["suspect"] and self.suspect_obs is not None and self._agree(obs, self.suspect_obs):
                    # Two observations after the move agree with each other but not with the one
                    # before it: that one was bad, and the move cannot be evaluated. Its counts
                    # stay unverified on every moved axis.
                    for j, c in enumerate(move.counts):
                        if c:
                            self.unverified[j] += abs(c)
                            if self.unverified[j] > self.axis_limit(j, int(np.sign(c))):
                                self.unresponsive.add(AXES[j])
                    self.pending = self.suspect_obs = None
                    self.inconsistent = 0
                elif ev["suspect"]:
                    self.inconsistent += 1
                    self.suspect_obs = obs
                    reason = ("observation_repeatedly_inconsistent" if self.inconsistent > self.max_inconsistent
                              else "observation_inconsistent_with_last_move")
                    self.last = _zero([reason], model_id=self.model.model_id, obs_id=obs.obs_id)
                    return self.last
                else:
                    self.inconsistent = 0
                    self.pending = self.suspect_obs = None
                    self._apply(ev, move)
        progress = self._progress(obs, target)
        if self.unresponsive:
            p = _zero([f"axis_unresponsive:{a}" for a in sorted(self.unresponsive)])
        elif self.stalls >= self.stall_limit:
            p = _zero([f"no_observed_response_after_{self.stalls}_moves"])
        elif progress:
            p = _zero([progress])
        else:
            p = None
            if self.takeup_axis is not None and direction is not None and direction[self.takeup_axis] == 0:
                p = _zero([f"takeup_state_unknown:{AXES[self.takeup_axis]}"], model_id=self.model.model_id)
                self.takeup_axis, self.takeup_accum = None, 0
            elif self.takeup_axis is not None:
                q = propose(self.model, self.report, obs, target, self.cfg, now_ns, last_complete_ns,
                            counts_now, None, controller_status, hold=self.hold)
                axis, sign = self.takeup_axis, self.takeup_sign
                need = q.counts[axis] if q.status == "move" else 0
                if q.status == "move" and (np.sign(need) == sign
                                           or abs(need) < self.reversal_threshold(axis, -sign)):
                    p = self._takeup(q, obs, counts_now)  # hysteresis: only a significant opposite need ends it
                elif q.status == "zero" and q.reasons != ["within_tolerance"]:
                    p = q                                  # e.g. stale data: no motion, take-up continues later
                else:
                    self.takeup_axis, self.takeup_accum = None, 0
                    p = q if q.status == "zero" else None
            if p is None:
                p = self._plain(obs, target, now_ns, last_complete_ns, counts_now, direction, controller_status)
                if p.status == "move" and p.reversal_axes:
                    axis = max((AXES.index(a) for a in p.reversal_axes), key=lambda j: abs(p.counts[j]))
                    self.takeup_axis, self.takeup_sign, self.takeup_accum = axis, int(np.sign(p.counts[axis])), 0
                    p = self._takeup(p, obs, counts_now)
        if p.status == "move":
            self.pending = (p, obs)
        self.last = p
        return p

    def _takeup(self, base: Proposal, obs: Observation, counts_now=None) -> Proposal:
        axis, sign = self.takeup_axis, self.takeup_sign
        step = (self.takeup_bulk(axis) if self.takeup_accum == 0 else 0) or self.takeup_step(axis, sign)
        counts = [0] * N_AXES
        counts[axis] = sign * step
        if counts_now is not None:
            end = counts_now[axis] + counts[axis]
            if not self.cfg.soft_min[axis] <= end <= self.cfg.soft_max[axis]:
                self.takeup_axis, self.takeup_accum = None, 0
                return _zero(["exceeds_travel_bounds"], error=base.error, model_id=self.model.model_id,
                             obs_id=obs.obs_id if obs else None)
        self.takeup_accum += step
        return Proposal(status="move", counts=counts, purpose="reversal_takeup",
                        reasons=[f"reversal_takeup:{AXES[axis]}"], error=base.error,
                        model_id=self.model.model_id, obs_id=obs.obs_id if obs else None,
                        reversal_axes=[AXES[axis]])
