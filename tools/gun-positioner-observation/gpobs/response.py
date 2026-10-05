"""Local command-to-feature response, fitted offline from logged steps.

A step is the change in the observed feature vector between two settled
observations of one trial, with the moves executed between them. The model is

    Δy = J⁺ · m⁺ + J⁻ · m⁻ + d · Δt + ε

where m is the output motion per axis after reversal take-up, split into its
positive part m⁺ and negative part m⁻ (so each axis has its own response in
each direction), d is a feature drift rate and Δt the time between the two
observations. Take-up: after a reversal an axis absorbs up to `b` counts
(its dead-band) before its output moves. The take-up state is carried through
the session's complete ordered move history, which is known at prediction time;
only observations are split between training and validation.

J⁺, J⁻ and d are fitted by iteratively reweighted least squares (Huber weights
on each step's combined normalized residual; steps beyond `reject_z` get zero
weight and are reported as outliers). Each axis's dead-band is chosen by a
profile search of the same robust loss. Steps taken while an axis's take-up
state is unknown (session start, after a fault) are excluded until a run of
moves in one direction exceeds the largest dead-band searched.

Units: features in their observed units (pixels until a calibration exists),
moves in controller counts. `jacobian_mm()` gives the same response per mm of
screw extension, the unit of the controls `visual_servo` functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json

import numpy as np

from .controls import AXES, COUNTS_PER_MM

N_AXES = len(AXES)


# ---- take-up -----------------------------------------------------------------------------------

def axis_takeup(moves: np.ndarray, b: float, unknown_before: np.ndarray,
                engage: float) -> tuple[np.ndarray, np.ndarray]:
    """One axis: output motion of each issued move after take-up, and whether it is known."""
    eff = np.zeros(len(moves))
    known = np.ones(len(moves), dtype=bool)
    slack_plus = None          # counts still to absorb before positive output motion
    run = 0.0
    for i, c in enumerate(moves):
        if unknown_before[i]:
            slack_plus, run = None, 0.0
        if c == 0:
            continue
        if slack_plus is None:
            eff[i] = np.sign(c) * max(0.0, abs(c) - b)
            known[i] = False
            run = run + c if run == 0 or np.sign(run) == np.sign(c) else c
            if abs(run) >= engage:
                slack_plus = 0.0 if run > 0 else b
            continue
        if c > 0:
            eff[i] = max(0.0, c - slack_plus)
            slack_plus = max(0.0, slack_plus - c)
        else:
            eff[i] = -max(0.0, -c - (b - slack_plus))
            slack_plus = min(b, slack_plus - c)
    return eff, known


def takeup_motion(moves: np.ndarray, deadband: np.ndarray, unknown_before: np.ndarray,
                  engage_counts: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Output motion of each move after reversal take-up, and whether it is known.

    moves: K x 6 issued counts in execution order. unknown_before: K x 6 booleans,
    True where the take-up state became unknown before that move. An unknown axis
    becomes known after a one-direction run of at least `engage_counts` counts.
    """
    moves = np.asarray(moves, dtype=float)
    deadband = np.asarray(deadband, dtype=float)
    engage = deadband if engage_counts is None else np.asarray(engage_counts, dtype=float)
    eff = np.zeros_like(moves)
    known = np.ones_like(moves, dtype=bool)
    for j in range(moves.shape[1]):
        eff[:, j], known[:, j] = axis_takeup(moves[:, j], deadband[j], unknown_before[:, j], engage[j])
    return eff, known


# ---- data assembly ------------------------------------------------------------------------------

@dataclass
class History:
    """Executed moves of one session, in order."""
    session_id: str
    move_ids: list[str]
    moves: np.ndarray              # K x 6
    unknown_before: np.ndarray     # K x 6


@dataclass
class Step:
    session_id: str
    trial_id: str
    obs_id: str
    move_index: list[int]          # rows of the session History
    dy: np.ndarray
    dt_s: float
    sigma: np.ndarray
    valid: bool
    reason: str | None = None


@dataclass
class StepData:
    feature_names: list[str]
    histories: dict[str, History]
    steps: list[Step]

    def trials(self) -> list[str]:
        return sorted({s.trial_id for s in self.steps})


def assemble(readers, feature_names: list[str] | None = None, min_confidence: float = 0.5) -> StepData:
    """Steps from one or more SessionReaders' move and observation records."""
    histories, steps = {}, []
    names = list(feature_names) if feature_names else None
    for reader in readers:
        sid = reader.session_id
        records = reader.records()
        completes = {r["cmd_id"]: r for r in records if r["kind"] == "move_complete"}
        move_ids, moves, unknown = [], [], []
        pending_unknown = np.ones(N_AXES, dtype=bool)          # session start: take-up unknown
        status_of = {}
        for r in records:
            if r["kind"] != "move_command":
                continue
            done = completes.get(r["cmd_id"])
            status = done["status"] if done else "missing"
            status_of[r["cmd_id"]] = status
            counts = np.array(r["counts"], dtype=float)
            if status == "done":
                move_ids.append(r["cmd_id"])
                moves.append(counts)
                unknown.append(pending_unknown.copy())
                pending_unknown[:] = False
            elif status in ("rejected", "not_executed"):
                continue
            else:  # fault, stopped, timeout, missing: partly issued, state unknown
                pending_unknown |= counts != 0
        hist = History(sid, move_ids, np.array(moves).reshape(-1, N_AXES),
                       np.array(unknown, dtype=bool).reshape(-1, N_AXES))
        histories[sid] = hist
        index = {m: i for i, m in enumerate(move_ids)}
        obs = {r["obs_id"]: r for r in records if r["kind"] == "observation"}
        if names is None:
            first = next(iter(obs.values()), None)
            names = sorted(first["values"]) if first else []
        for r in obs.values():
            prev = obs.get(r.get("prev_obs_id"))
            if prev is None or prev.get("trial_id") != r.get("trial_id") or r.get("trial_id") is None:
                continue
            reason = None
            if any(status_of.get(c) != "done" for c in r["cmd_ids"]):
                reason = "move_not_done"
            vals = [r["values"].get(f) for f in names]
            pvals = [prev["values"].get(f) for f in names]
            if any(v is None for v in vals + pvals):
                reason = reason or "missing_feature"
            conf = [r["confidence"].get(f, 0) for f in names] + [prev["confidence"].get(f, 0) for f in names]
            if reason is None and min((c if c is not None else 0) for c in conf) < min_confidence:
                reason = "low_confidence"
            if reason is None:
                dy = np.array(vals, dtype=float) - np.array(pvals, dtype=float)
                sig = np.hypot(np.array([r["sigma"].get(f) or 0 for f in names], dtype=float),
                               np.array([prev["sigma"].get(f) or 0 for f in names], dtype=float))
            else:
                dy = np.full(len(names), np.nan)
                sig = np.full(len(names), np.nan)
            mid = (r["t_start_ns"] + r["t_end_ns"]) / 2
            pmid = (prev["t_start_ns"] + prev["t_end_ns"]) / 2
            steps.append(Step(sid, r["trial_id"], r["obs_id"],
                              [index[c] for c in r["cmd_ids"] if c in index], dy, (mid - pmid) / 1e9, sig,
                              reason is None, reason))
    return StepData(names or [], histories, steps)


def design(data: StepData, steps: list[Step], deadband: np.ndarray, engage: np.ndarray,
           cache: dict | None = None):
    """Rows [m⁺ (6), m⁻ (6), Δt] for steps; also a per-row known flag.

    `cache` holds per-(session, axis, dead-band) take-up results between calls.
    """
    cache = {} if cache is None else cache
    motion = {}
    for sid, hist in data.histories.items():
        eff = np.zeros(hist.moves.shape)
        kn = np.ones(hist.moves.shape, dtype=bool)
        for j in range(N_AXES):
            key = (sid, j, float(deadband[j]), float(engage[j]))
            if key not in cache:
                cache[key] = axis_takeup(hist.moves[:, j], deadband[j], hist.unknown_before[:, j], engage[j])
            eff[:, j], kn[:, j] = cache[key]
        motion[sid] = (eff, kn)
    rows, known = [], []
    for s in steps:
        eff, kn = motion[s.session_id]
        pos = np.zeros(N_AXES)
        neg = np.zeros(N_AXES)
        ok = True
        for i in s.move_index:
            pos += np.maximum(eff[i], 0)
            neg += np.minimum(eff[i], 0)
            ok &= bool(np.all(kn[i] | (data.histories[s.session_id].moves[i] == 0)))
        rows.append(np.concatenate([pos, neg, [s.dt_s]]))
        known.append(ok)
    return np.array(rows).reshape(-1, 2 * N_AXES + 1), np.array(known, dtype=bool)


# ---- fitting ------------------------------------------------------------------------------------

def _robust_scale(r: np.ndarray, floor: float = 1e-9) -> np.ndarray:
    med = np.median(r, axis=0)
    return np.maximum(1.4826 * np.median(np.abs(r - med), axis=0), floor)


def _irls(x, y, huber_k=1.345, reject_z=6.0, iters=25, scale=None):
    w = np.ones(len(x))
    theta = np.zeros((x.shape[1], y.shape[1]))
    s = scale
    for _ in range(iters):
        sw = np.sqrt(w)[:, None]
        theta, *_ = np.linalg.lstsq(sw * x, sw * y, rcond=None)
        r = y - x @ theta
        if scale is None:
            s = _robust_scale(r[w > 0] if np.any(w > 0) else r)
        z = np.sqrt(np.mean((r / s) ** 2, axis=1))
        w_new = np.where(z <= huber_k, 1.0, huber_k / np.maximum(z, 1e-12))
        w_new[z > reject_z] = 0.0
        if np.allclose(w_new, w, atol=1e-6):
            w = w_new
            break
        w = w_new
    r = y - x @ theta
    z = np.sqrt(np.mean((r / s) ** 2, axis=1))
    rho = np.where(z <= huber_k, 0.5 * z ** 2, huber_k * z - 0.5 * huber_k ** 2)
    rho[z > reject_z] = huber_k * reject_z - 0.5 * huber_k ** 2
    return theta, r, s, w, float(np.sum(rho))


@dataclass
class ResponseModel:
    feature_names: list[str]
    axes: list[str]
    j_plus: np.ndarray
    j_minus: np.ndarray
    j_plus_se: np.ndarray
    j_minus_se: np.ndarray
    drift_per_s: np.ndarray
    deadband: np.ndarray
    deadband_halfwidth: np.ndarray
    deadband_identified: np.ndarray
    reversal_steps: np.ndarray
    identified_plus: np.ndarray
    identified_minus: np.ndarray
    residual_scale: np.ndarray
    engage_counts: np.ndarray
    n_rows: int
    outliers: list[dict]
    train_trials: list[str]
    sessions: list[str]
    deadband_profile: dict = field(default_factory=dict)
    units: str = "feature units per controller count"

    @property
    def model_id(self) -> str:
        body = json.dumps({k: v for k, v in self.to_dict().items() if k != "model_id"}, sort_keys=True)
        return "rm-" + hashlib.sha256(body.encode()).hexdigest()[:16]

    def theta(self) -> np.ndarray:
        return np.vstack([self.j_plus.T, self.j_minus.T, self.drift_per_s[None, :]])

    def predict(self, rows: np.ndarray) -> np.ndarray:
        return np.nan_to_num(rows) @ np.nan_to_num(self.theta())

    def jacobian(self, signs) -> np.ndarray:
        """Per-count response for a planned move with these per-axis signs (+1/-1)."""
        signs = np.asarray(signs)
        return np.where(signs[None, :] >= 0, self.j_plus, self.j_minus)

    def jacobian_mm(self, signs) -> np.ndarray:
        return self.jacobian(signs) * COUNTS_PER_MM

    def to_dict(self) -> dict:
        def arr(a):
            return [None if (isinstance(v, float) and not np.isfinite(v)) else v
                    for v in np.asarray(a, dtype=float).ravel().tolist()]
        return {
            "feature_names": self.feature_names, "axes": self.axes, "units": self.units,
            "j_plus": [arr(r) for r in self.j_plus], "j_minus": [arr(r) for r in self.j_minus],
            "j_plus_se": [arr(r) for r in self.j_plus_se], "j_minus_se": [arr(r) for r in self.j_minus_se],
            "drift_per_s": arr(self.drift_per_s), "deadband": arr(self.deadband),
            "deadband_halfwidth": arr(self.deadband_halfwidth),
            "deadband_identified": [bool(v) for v in self.deadband_identified],
            "reversal_steps": [int(v) for v in self.reversal_steps],
            "identified_plus": [bool(v) for v in self.identified_plus],
            "identified_minus": [bool(v) for v in self.identified_minus],
            "residual_scale": arr(self.residual_scale), "engage_counts": arr(self.engage_counts),
            "n_rows": self.n_rows, "outliers": self.outliers, "train_trials": self.train_trials,
            "sessions": self.sessions, "deadband_profile": self.deadband_profile,
        }

    def to_json(self) -> str:
        return json.dumps({**self.to_dict(), "model_id": self.model_id}, indent=1)

    @classmethod
    def from_dict(cls, d: dict) -> "ResponseModel":
        f = lambda key: np.array([[np.nan if v is None else v for v in row] for row in d[key]], dtype=float)
        v = lambda key: np.array([np.nan if x is None else x for x in d[key]], dtype=float)
        model = cls(d["feature_names"], d["axes"], f("j_plus"), f("j_minus"), f("j_plus_se"), f("j_minus_se"),
                    v("drift_per_s"), v("deadband"), v("deadband_halfwidth"), np.array(d["deadband_identified"]),
                    np.array(d["reversal_steps"]), np.array(d["identified_plus"]),
                    np.array(d["identified_minus"]), v("residual_scale"), v("engage_counts"),
                    d["n_rows"], d["outliers"], d["train_trials"], d["sessions"], d.get("deadband_profile", {}))
        if "model_id" in d and d["model_id"] != model.model_id:
            raise ValueError("model file content does not match its model_id")
        return model


def _reversal_counts(data: StepData, steps: list[Step]) -> np.ndarray:
    counts = np.zeros(N_AXES, dtype=int)
    for sid, hist in data.histories.items():
        last = np.zeros(N_AXES)
        used = {i for s in steps if s.session_id == sid for i in s.move_index}
        for i, mv in enumerate(hist.moves):
            sign = np.sign(mv)
            rev = (sign != 0) & (last != 0) & (sign != last)
            if i in used:
                counts += rev
            last = np.where(sign != 0, sign, last)
    return counts


def fit(data: StepData, train_trials: list[str] | None = None, max_deadband: float = 400.0,
        grid_step: float = 10.0, min_obs: int = 3, huber_k: float = 1.345, reject_z: float = 6.0,
        sweeps: int = 2) -> ResponseModel:
    """Fit the response on the steps of `train_trials` (all trials when None)."""
    chosen = set(train_trials) if train_trials is not None else set(data.trials())
    steps = [s for s in data.steps if s.valid and s.trial_id in chosen]
    if not steps:
        raise ValueError("no valid steps in the training trials")
    engage = np.full(N_AXES, max_deadband)
    _, known = design(data, steps, np.full(N_AXES, max_deadband), engage)
    steps = [s for s, k in zip(steps, known) if k]
    if len(steps) < 2 * N_AXES + 2:
        raise ValueError(f"only {len(steps)} usable steps; the model has {2 * N_AXES + 1} columns per feature")
    y = np.array([s.dy for s in steps])
    m = y.shape[1]
    cache: dict = {}

    def solve(deadband, scale=None, iters=25):
        x, _ = design(data, steps, deadband, engage, cache)
        cols = np.array([np.count_nonzero(x[:, c]) >= min_obs for c in range(x.shape[1])])
        cols[-1] = True
        theta = np.full((x.shape[1], m), np.nan)
        th, r, s, w, loss = _irls(x[:, cols], y, huber_k, reject_z, iters=iters, scale=scale)
        theta[cols] = th
        return theta, r, s, w, loss, x, cols

    deadband = np.zeros(N_AXES)
    halfwidth = np.full(N_AXES, np.nan)
    _, _, scale, _, _, _, _ = solve(deadband)
    grid = np.arange(0.0, max_deadband + 1e-9, grid_step)
    profiles = {}
    for _ in range(sweeps):
        for j in range(N_AXES):
            losses = []
            for b in grid:
                trial = deadband.copy()
                trial[j] = b
                losses.append(solve(trial, scale, iters=8)[4])
            best = grid[int(np.argmin(losses))]
            fine = np.arange(max(0.0, best - grid_step), min(max_deadband, best + grid_step) + 1e-9, grid_step / 10)
            fine_losses = []
            for b in fine:
                trial = deadband.copy()
                trial[j] = b
                fine_losses.append(solve(trial, scale, iters=8)[4])
            deadband[j] = fine[int(np.argmin(fine_losses))]
            # Profile interval: dead-bands whose robust loss is within 2 of the minimum
            # (about two standard deviations for one parameter); a window edge bounds it.
            near = fine[np.array(fine_losses) <= min(fine_losses) + 2.0]
            halfwidth[j] = float(max(deadband[j] - near.min(), near.max() - deadband[j]))
            profiles[AXES[j]] = {"grid": grid.tolist(), "loss": [float(v) for v in losses],
                                 "fine_grid": fine.tolist(), "fine_loss": [float(v) for v in fine_losses]}
        _, _, scale, _, _, _, _ = solve(deadband)
    theta, r, s, w, loss, x, cols = solve(deadband)
    used = w > 0
    xw = x[:, cols] * np.sqrt(w)[:, None]
    try:
        cov = np.linalg.inv(xw.T @ xw)
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(xw.T @ xw)
    se = np.full_like(theta, np.nan)
    se[cols] = np.sqrt(np.clip(np.diag(cov), 0, None))[:, None] * s[None, :]
    reversals = _reversal_counts(data, steps)
    ident_db = np.zeros(N_AXES, dtype=bool)
    for j in range(N_AXES):
        prof = np.array(profiles[AXES[j]]["loss"])
        ident_db[j] = reversals[j] >= 3 and (prof.max() - prof.min()) > 1.0
    outliers = [{"session_id": st.session_id, "trial_id": st.trial_id, "obs_id": st.obs_id}
                for st, wt in zip(steps, w) if wt == 0]
    return ResponseModel(
        feature_names=list(data.feature_names), axes=list(AXES),
        j_plus=theta[:N_AXES].T.copy(), j_minus=theta[N_AXES:2 * N_AXES].T.copy(),
        j_plus_se=se[:N_AXES].T.copy(), j_minus_se=se[N_AXES:2 * N_AXES].T.copy(),
        drift_per_s=theta[-1].copy(), deadband=deadband.copy(), deadband_halfwidth=halfwidth,
        deadband_identified=ident_db,
        reversal_steps=reversals, identified_plus=cols[:N_AXES].copy(),
        identified_minus=cols[N_AXES:2 * N_AXES].copy(), residual_scale=s.copy(), engage_counts=engage,
        n_rows=int(np.count_nonzero(used)), outliers=outliers, train_trials=sorted(chosen),
        sessions=sorted(data.histories), deadband_profile=profiles)
