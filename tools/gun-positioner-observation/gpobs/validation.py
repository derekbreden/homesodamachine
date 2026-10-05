"""Held-out validation of a fitted response, split by trial.

Trials, never individual steps or frames, are assigned to training or
validation: steps of one trial share the same take-up history, drift and
lighting, so splitting inside a trial would let the model see its own test
conditions. `split_trials` stratifies by a group label (normally the probed
axis) so every group appears on both sides where possible.

The report gives per-feature residual statistics against a zero-change null
prediction, per axis-direction coverage and skill, the residual of every held-out
step, and the same statistics for the controls package's
`visual_servo.fit_jacobian` (one direction, no take-up, no drift) fitted on the
same training trials. The correction proposer uses only axis-directions this
report validates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json

import numpy as np

from .controls import AXES, COUNTS_PER_MM, host_modules
from .response import N_AXES, ResponseModel, StepData, design


def split_trials(trial_ids, holdout_fraction: float = 0.3, seed: int = 0,
                 groups: dict[str, str] | None = None) -> tuple[list[str], list[str]]:
    ids = sorted(set(trial_ids))
    if len(ids) < 2:
        raise ValueError("a held-out split needs at least two trials")
    rng = np.random.default_rng(seed)
    by_group: dict[str, list[str]] = {}
    for t in ids:
        by_group.setdefault((groups or {}).get(t, ""), []).append(t)
    holdout = []
    for g in sorted(by_group):
        members = list(by_group[g])
        rng.shuffle(members)
        k = int(round(holdout_fraction * len(members)))
        if len(members) >= 2:
            k = min(max(k, 1), len(members) - 1)
        else:
            k = 0
        holdout += members[:k]
    if not holdout:
        holdout = [ids[int(rng.integers(len(ids)))]]
    train = [t for t in ids if t not in set(holdout)]
    return train, sorted(holdout)


def check_split(data: StepData, train: list[str], holdout: list[str]) -> None:
    overlap = set(train) & set(holdout)
    if overlap:
        raise ValueError(f"trials in both training and validation: {sorted(overlap)}")
    stray = set(holdout) - set(data.trials())
    if stray:
        raise ValueError(f"held-out trials absent from the data: {sorted(stray)}")


@dataclass
class ValidationReport:
    model_id: str
    train_trials: list[str]
    holdout_trials: list[str]
    n_steps: int
    n_unknown_takeup_excluded: int
    n_outliers: int
    per_feature: dict
    axis_directions: dict
    validated_axis_directions: list[str]
    baseline_visual_servo: dict
    passed: bool
    reasons: list[str]
    criteria: dict
    residuals: list = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=1)

    @classmethod
    def from_dict(cls, d: dict) -> "ValidationReport":
        return cls(**d)


def _stats(r: np.ndarray, y: np.ndarray, scale: float, exercised_floor: float) -> dict:
    rms = float(np.sqrt(np.mean(r ** 2))) if len(r) else float("nan")
    null = float(np.sqrt(np.mean(y ** 2))) if len(y) else float("nan")
    exercised = bool(len(y)) and null > exercised_floor
    return {
        "rms": rms, "null_rms": null,
        "skill": float(1 - (rms / null) ** 2) if exercised else None,
        "bias": float(np.mean(r)) if len(r) else None,
        "median_abs": float(np.median(np.abs(r))) if len(r) else None,
        "p95_abs": float(np.quantile(np.abs(r), 0.95)) if len(r) else None,
        "within_2_scale": float(np.mean(np.abs(r) <= 2 * scale)) if len(r) else None,
        "exercised": exercised,
    }


def _baseline(data: StepData, model: ResponseModel, holdout_steps) -> dict:
    vs = host_modules().visual_servo
    train = [s for s in data.steps if s.valid and s.trial_id in set(model.train_trials)]

    def delta_mm(step):
        moves = data.histories[step.session_id].moves
        total = moves[step.move_index].sum(axis=0) if step.move_index else np.zeros(N_AXES)
        return (total / COUNTS_PER_MM).tolist()

    trials = [{"delta_mm": delta_mm(s), "delta_feature": s.dy.tolist()} for s in train if s.move_index]
    try:
        jac = np.array(vs.fit_jacobian(trials))
    except ValueError as exc:
        return {"available": False, "reason": str(exc)}
    out = {"available": True, "function": "visual_servo.fit_jacobian", "per_feature": {}}
    if not holdout_steps:
        return out
    x = np.array([delta_mm(s) for s in holdout_steps])
    y = np.array([s.dy for s in holdout_steps])
    r = y - x @ jac.T
    for i, name in enumerate(data.feature_names):
        out["per_feature"][name] = _stats(r[:, i], y[:, i], float(model.residual_scale[i]),
                                          3 * float(model.residual_scale[i]))
    return out


def validate(model: ResponseModel, data: StepData, holdout_trials: list[str], min_trials: int = 2,
             min_skill: float = 0.8, min_axis_direction_steps: int = 2, reject_z: float = 6.0,
             max_outlier_fraction: float = 0.1, include_baseline: bool = True) -> ValidationReport:
    """Score `model` on the held-out trials.

    A held-out step whose combined normalized residual exceeds `reject_z` (the
    fit's own rejection rule) is reported as an outlier and left out of the
    statistics; more than `max_outlier_fraction` outliers fails validation, so a
    wrong model cannot pass by having its misses called outliers.
    """
    check_split(data, model.train_trials, holdout_trials)
    if data.feature_names != model.feature_names:
        raise ValueError("validation data and model use different feature lists")
    steps = [s for s in data.steps if s.valid and s.trial_id in set(holdout_trials)]
    x, known = design(data, steps, model.deadband, model.engage_counts) if steps else (
        np.zeros((0, 2 * N_AXES + 1)), np.zeros(0, dtype=bool))
    excluded = int(np.count_nonzero(~known))
    steps = [s for s, k in zip(steps, known) if k]
    x = x[known] if len(known) else x
    y = np.array([s.dy for s in steps]).reshape(-1, len(model.feature_names))
    p = model.predict(x) if len(x) else np.zeros_like(y)
    r = y - p
    scale = model.residual_scale
    z = np.sqrt(np.mean((r / scale) ** 2, axis=1)) if len(r) else np.zeros(0)
    outlier = z > reject_z
    keep = ~outlier
    all_steps, all_p, all_r, all_y = steps, p, r, y
    steps = [s for s, k in zip(steps, keep) if k]
    x, y, p, r = x[keep], y[keep], p[keep], r[keep]
    per_feature = {name: _stats(r[:, i], y[:, i], float(scale[i]), 3 * float(scale[i]))
                   for i, name in enumerate(model.feature_names)}
    axis_dirs = {}
    validated = []
    for j, axis in enumerate(AXES):
        for sign, col, ident in (("+", j, model.identified_plus[j]), ("-", N_AXES + j, model.identified_minus[j])):
            moved = np.abs(x[:, col]) > 0 if len(x) else np.zeros(0, dtype=bool)
            n = int(np.count_nonzero(moved))
            if n:
                rn, yn = r[moved] / scale, y[moved] / scale
                skill = float(1 - np.sum(rn ** 2) / max(np.sum(yn ** 2), 1e-12))
            else:
                skill = None
            ok = bool(ident) and n >= min_axis_direction_steps and skill is not None and skill >= min_skill
            axis_dirs[axis + sign] = {"held_out_steps": n, "skill": skill, "identified": bool(ident),
                                      "validated": ok}
            if ok:
                validated.append(axis + sign)
    reasons = []
    trials_with_steps = sorted({s.trial_id for s in steps})
    if len(trials_with_steps) < min_trials:
        reasons.append(f"only {len(trials_with_steps)} held-out trials with usable steps (< {min_trials})")
    for name, st in per_feature.items():
        if st["exercised"] and st["skill"] < min_skill:
            reasons.append(f"{name}: held-out skill {st['skill']:.3f} < {min_skill}")
    if not validated:
        reasons.append("no axis-direction validated")
    n_out = int(np.count_nonzero(outlier))
    if len(all_steps) and n_out / len(all_steps) > max_outlier_fraction:
        reasons.append(f"{n_out} of {len(all_steps)} held-out steps are outliers (> {max_outlier_fraction:.0%})")
    residuals = [{"trial_id": s.trial_id, "obs_id": s.obs_id, "observed": s.dy.round(4).tolist(),
                  "predicted": all_p[i].round(4).tolist(), "residual": all_r[i].round(4).tolist(),
                  "z": round(float(z[i]), 3), "outlier": bool(outlier[i])}
                 for i, s in enumerate(all_steps)]
    return ValidationReport(
        model_id=model.model_id, train_trials=list(model.train_trials), holdout_trials=sorted(holdout_trials),
        n_steps=len(all_steps), n_unknown_takeup_excluded=excluded, n_outliers=n_out, per_feature=per_feature,
        axis_directions=axis_dirs, validated_axis_directions=validated,
        baseline_visual_servo=_baseline(data, model, steps) if include_baseline else {"available": False},
        passed=not reasons, reasons=reasons,
        criteria={"min_trials": min_trials, "min_skill": min_skill,
                  "min_axis_direction_steps": min_axis_direction_steps, "reject_z": reject_z,
                  "max_outlier_fraction": max_outlier_fraction,
                  "null_prediction": "zero feature change"},
        residuals=residuals)
