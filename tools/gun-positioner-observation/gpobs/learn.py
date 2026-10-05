"""Dry-session learning workflow behind `observe.py learn`.

Steps and the files they write:
    check     validate the operator files (cameras, features, target, plan)
    plan      jog-plan.json: bounded ± jogs per axis
    record    a session of observations without motion; feature-summary.json
    jog       a session of jog trials: move receipts, observations, trial outcomes
    fit       model.json and split.json (training and held-out trials)
    validate  validation.json and validation-report.txt: PASS or FAIL
    propose   proposal.json: a review proposal from a recorded observation; never executed
    execute   a session of observe → propose → move, one bounded move at a time

`record`, `jog` and `execute` default to the simulator: a simulated mechanism and
feature observations named by the features file, persisted in a world file so
consecutive commands continue from the same state.

Real motion (`--backend controller`) is refused unless the
--i-understand-this-moves-hardware flag is given; the camera configuration passes
measurement validation; the clock check passes; the features file (and the plan
or the target, validation and model) pass; the operator, at this tool's prompt,
has typed the controls console's own `clear`, `reference central` and `arm`
and then `go`; the controller then reports drivers_ok, microsteps verified as
16, referenced, armed, no fault, and the current scales, VSENSE and rate the
controls package exports for its profile; and each move is within the firmware's
per-axis bound, the plan's or proposal's step bound and the soft limits from the
controller's reported counts. This tool never sends CLEAR, REF or ARM unless the
operator types it, and never commands laser emission.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
import time

import numpy as np

from . import config as gconfig
from .clock import Clock, FakeClock
from .controls import AXES, COUNTS_PER_MM, MAX_JOG_COUNTS, SOFT_MAX, SOFT_MIN, profile_problems
from .features import REGISTRY
from .moves import BackendInfo, MoveOutcome, PositionerBackend
from .proposal import Observation

PLACEHOLDER = gconfig.PLACEHOLDER
FORMAT_VERSION = 1
HARDWARE_FLAG = "--i-understand-this-moves-hardware"
KEYS = {"dot": ("u", "v"), "wire": ("u", "v"), "seam": ("theta_deg", "rho")}
POINT_TYPES = ("dot", "wire")
LABEL = re.compile(r"[a-z][a-z0-9_]*")
PARAMS = {
    "dot": {"threshold_sigma": ("num", 0, None), "min_pixels": ("int", 1, None), "max_pixels": ("int", 1, None),
            "channel": ("enum", ("red", "green", "blue", "gray"))},
    "wire": {"approach_deg": ("num", -360, 360), "polarity": ("enum", ("dark", "bright")),
             "threshold_sigma": ("num", 0, None), "min_pixels": ("int", 1, None), "min_elongation": ("num", 1, None)},
    "seam": {"orientation": ("enum", ("horizontal", "vertical")), "inlier_px": ("num", 0, None),
             "min_inlier_fraction": ("num", 0, 1), "min_edge_sigma": ("num", 0, None)},
}


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and np.isfinite(v)


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _read(path) -> tuple[dict, list[str]]:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        return {}, [f"{path}: unreadable: {exc}"]
    if not isinstance(data, dict):
        return {}, [f"{path}: not a JSON object"]
    return data, []


# ---- features file ---------------------------------------------------------------------------------

@dataclass
class FeatureDef:
    camera_id: str
    label: str
    type: str
    roi: tuple
    params: dict

    @property
    def names(self) -> list[str]:
        return [f"{self.camera_id}.{self.label}.{k}" for k in KEYS[self.type]]

    def extractor(self):
        params = dict(self.params)
        if self.type == "dot" and params.get("channel") == "gray":
            params["channel"] = None
        return REGISTRY[self.type](roi=self.roi, label=self.label, **params)


@dataclass
class FeatureConfig:
    path: Path
    data: dict
    features: list
    frames_per_observation: int
    min_valid_fraction: float
    settle_s: float
    problems: list

    def names(self) -> list[str]:
        return [n for f in self.features for n in f.names]

    def types(self) -> dict:
        return {f"{f.camera_id}.{f.label}": f.type for f in self.features}

    def extractors(self) -> dict:
        out: dict = {}
        for f in self.features:
            out.setdefault(f.camera_id, []).append(f.extractor())
        return out


def _param_problems(prefix: str, kind: str, params) -> list[str]:
    if not isinstance(params, dict):
        return [f"{prefix} must be an object"]
    problems = []
    for name, spec in PARAMS[kind].items():
        v = params.get(name)
        if spec[0] == "enum":
            if v not in spec[1]:
                problems.append(f"{prefix}.{name} must be one of {spec[1]}")
        elif spec[0] == "int":
            if not (_int(v) and v >= spec[1]):
                problems.append(f"{prefix}.{name} must be an integer of at least {spec[1]}")
        else:
            lo, hi = spec[1], spec[2]
            if not (_num(v) and v > lo and (hi is None or v <= hi)):
                problems.append(f"{prefix}.{name} must be a number above {lo}" + (f" and at most {hi}" if hi else ""))
    extra = set(params) - set(PARAMS[kind]) - {k for k in params if str(k).startswith("_")}
    if extra:
        problems.append(f"{prefix} has unknown parameters {sorted(extra)}")
    if kind == "dot" and _int(params.get("min_pixels")) and _int(params.get("max_pixels")) \
            and params["max_pixels"] <= params["min_pixels"]:
        problems.append(f"{prefix}.max_pixels must exceed min_pixels")
    return problems


def load_features(path, frame_sizes: dict | None = None) -> FeatureConfig:
    """Read and check a features file. `frame_sizes` ({camera_id: (w, h)}) bounds the ROIs."""
    path = Path(path)
    data, problems = _read(path)
    problems += [f"{p} still holds {PLACEHOLDER}" for p in gconfig.placeholders(data)]
    if data and data.get("format_version") != FORMAT_VERSION:
        problems.append(f"format_version must be {FORMAT_VERSION}")
    fpo, mvf, settle = data.get("frames_per_observation"), data.get("min_valid_fraction"), data.get("settle_s")
    if not (_int(fpo) and fpo >= 1):
        problems.append("frames_per_observation must be an integer of at least 1")
    if not (_num(mvf) and 0 < mvf <= 1):
        problems.append("min_valid_fraction must be above 0 and at most 1")
    if not (_num(settle) and settle >= 0):
        problems.append("settle_s must be a non-negative number of seconds")
    feats, seen = [], Counter()
    raw = data.get("features")
    if not isinstance(raw, list) or not raw:
        problems.append("features must list at least one feature")
        raw = []
    for i, f in enumerate(raw):
        p = f"features[{i}]"
        if not isinstance(f, dict):
            problems.append(f"{p} must be an object")
            continue
        cam, label, kind, roi = f.get("camera_id"), f.get("label"), f.get("type"), f.get("roi")
        if not (isinstance(cam, str) and gconfig.CAMERA_ID.fullmatch(cam)):
            problems.append(f"{p}.camera_id must name a camera of cameras.json")
        if not (isinstance(label, str) and LABEL.fullmatch(label)):
            problems.append(f"{p}.label must be lower-case letters, digits and '_'")
        if kind not in KEYS:
            problems.append(f"{p}.type must be one of {sorted(KEYS)}")
        roi_ok = isinstance(roi, dict) and all(_int(roi.get(k)) for k in ("x", "y", "width", "height"))
        if not roi_ok:
            problems.append(f"{p}.roi must give integer x, y, width and height in pixels")
        else:
            x, y, w, h = roi["x"], roi["y"], roi["width"], roi["height"]
            if x < 0 or y < 0 or w < 8 or h < 8:
                problems.append(f"{p}.roi must lie in the frame and be at least 8 x 8 pixels")
            size = (frame_sizes or {}).get(cam)
            if size and (x + w > size[0] or y + h > size[1]):
                problems.append(f"{p}.roi extends beyond the {size[0]} x {size[1]} frame")
            if size is None and frame_sizes is not None:
                problems.append(f"{p}.camera_id {cam!r} has no verified format in cameras.json")
        if kind in KEYS:
            problems += _param_problems(f"{p}.params", kind, f.get("params"))
        seen[(cam, label)] += 1
        if kind in KEYS and roi_ok and isinstance(cam, str) and isinstance(label, str):
            feats.append(FeatureDef(cam, label, kind, (roi["x"], roi["y"], roi["width"], roi["height"]),
                                    {k: v for k, v in (f.get("params") or {}).items() if not str(k).startswith("_")}))
    problems += [f"camera {c!r} has label {lab!r} {n} times" for (c, lab), n in seen.items() if n > 1]
    return FeatureConfig(path, data, feats, fpo if _int(fpo) else 1, mvf if _num(mvf) else 0.6,
                         settle if _num(settle) else 0.5, problems)


# ---- target file -------------------------------------------------------------------------------------

@dataclass
class Quantity:
    name: str
    kind: str                # value | difference | point_to_line
    refs: dict
    value_px: float
    tolerance_px: float

    def feature_names(self) -> list[str]:
        if self.kind == "value":
            return [self.refs["feature"]]
        if self.kind == "difference":
            return [self.refs["a"], self.refs["b"]]
        pt, line = self.refs["point"], self.refs["line"]
        return [f"{pt}.u", f"{pt}.v", f"{line}.theta_deg", f"{line}.rho"]

    def evaluate(self, y: dict):
        if self.kind == "value":
            return y[self.refs["feature"]]
        if self.kind == "difference":
            return y[self.refs["a"]] - y[self.refs["b"]]
        u, v, th, rho = (y[n] for n in self.feature_names())
        cx, cy = self.refs["center"]
        t = np.radians(th)
        return (u - cx) * np.cos(t) + (v - cy) * np.sin(t) - rho

    def gradient(self, y: dict) -> dict:
        if self.kind == "value":
            return {self.refs["feature"]: 1.0}
        if self.kind == "difference":
            return {self.refs["a"]: 1.0, self.refs["b"]: -1.0}
        nu, nv, nth, nrho = self.feature_names()
        cx, cy = self.refs["center"]
        t = np.radians(y[nth])
        return {nu: float(np.cos(t)), nv: float(np.sin(t)), nrho: -1.0,
                nth: float((-(y[nu] - cx) * np.sin(t) + (y[nv] - cy) * np.cos(t)) * np.pi / 180)}


@dataclass
class TargetConfig:
    path: Path
    data: dict
    quantities: list
    axes: list
    units: str | None
    problems: list

    def names(self) -> list[str]:
        return [q.name for q in self.quantities]

    def values(self) -> dict:
        return {q.name: q.value_px for q in self.quantities}

    def tolerances(self) -> dict:
        return {q.name: q.tolerance_px for q in self.quantities}

    def transform(self, obs: Observation) -> Observation:
        """The observation in target quantities: values, propagated sigma, least confidence."""
        values, sigma, conf = {}, {}, {}
        for q in self.quantities:
            names = q.feature_names()
            if any(obs.values.get(n) is None for n in names):
                values[q.name], sigma[q.name], conf[q.name] = None, None, 0.0
                continue
            values[q.name] = float(q.evaluate(obs.values))
            grad = q.gradient(obs.values)
            sigma[q.name] = float(np.sqrt(sum((g * (obs.sigma.get(n) or 0.0)) ** 2 for n, g in grad.items())))
            conf[q.name] = float(min(obs.confidence.get(n, 0.0) or 0.0 for n in names))
        return Observation(obs.obs_id, obs.t_start_ns, obs.t_end_ns, values, sigma, conf, obs.trial_id)

    def gradient_matrix(self, obs: Observation, feature_names: list[str]) -> np.ndarray:
        g = np.zeros((len(self.quantities), len(feature_names)))
        for i, q in enumerate(self.quantities):
            for n, d in q.gradient(obs.values).items():
                g[i, feature_names.index(n)] = d
        return g


def load_target(path, features: FeatureConfig) -> TargetConfig:
    path = Path(path)
    data, problems = _read(path)
    problems += [f"{p} still holds {PLACEHOLDER}" for p in gconfig.placeholders(data)]
    if data and data.get("format_version") != FORMAT_VERSION:
        problems.append(f"format_version must be {FORMAT_VERSION}")
    units, scale = data.get("units"), 1.0
    if units == "px":
        if data.get("px_per_mm") is not None or data.get("calibration") is not None:
            problems.append("px_per_mm and calibration must be null when units is px")
    elif units == "mm":
        if not (_num(data.get("px_per_mm")) and data["px_per_mm"] > 0):
            problems.append("units mm needs px_per_mm from an independent calibration")
        else:
            scale = float(data["px_per_mm"])
        if not gconfig._filled(data.get("calibration")):
            problems.append("units mm needs calibration: the calibration record px_per_mm comes from")
    else:
        problems.append("units must be px, or mm with px_per_mm and calibration")
    names = set(features.names())
    types = features.types()
    quantities = []
    raw = data.get("quantities")
    if not isinstance(raw, list) or not raw:
        problems.append("quantities must list at least one quantity")
        raw = []
    seen = Counter()
    for i, q in enumerate(raw):
        p = f"quantities[{i}]"
        if not isinstance(q, dict):
            problems.append(f"{p} must be an object")
            continue
        name, kind = q.get("name"), q.get("kind")
        if not gconfig._filled(name):
            problems.append(f"{p}.name must name the quantity")
        seen[name] += 1
        refs = {}
        if kind == "value":
            refs = {"feature": q.get("feature")}
            if refs["feature"] not in names:
                problems.append(f"{p}.feature must be a feature value such as cam_a.dot.u (from the features file)")
        elif kind == "difference":
            refs = {"a": q.get("a"), "b": q.get("b")}
            for k in ("a", "b"):
                if refs[k] not in names:
                    problems.append(f"{p}.{k} must be a feature value such as cam_a.wire.u (from the features file)")
        elif kind == "point_to_line":
            refs = {"point": q.get("point"), "line": q.get("line")}
            line_def = next((f for f in features.features if f"{f.camera_id}.{f.label}" == refs["line"]), None)
            if line_def is not None:
                from .features import roi_center
                refs["center"] = list(roi_center(line_def.roi))   # the seam's rho is measured about it
            if types.get(refs["point"]) not in POINT_TYPES:
                problems.append(f"{p}.point must be a dot or wire feature such as cam_a.dot")
            if types.get(refs["line"]) != "seam":
                problems.append(f"{p}.line must be a seam feature such as cam_a.seam")
            if isinstance(refs["point"], str) and isinstance(refs["line"], str) \
                    and refs["point"].split(".")[0] != refs["line"].split(".")[0]:
                problems.append(f"{p}.point and line must be in the same camera")
        else:
            problems.append(f"{p}.kind must be value, difference or point_to_line")
        value, tol = q.get("value"), q.get("tolerance")
        if not _num(value):
            problems.append(f"{p}.value must be the desired value in {units if units in ('px', 'mm') else 'px'}")
        if not (_num(tol) and tol > 0):
            problems.append(f"{p}.tolerance must be a positive number")
        if not any(x.startswith(p + ".") or x.startswith(p + " ") for x in problems) and gconfig._filled(name):
            quantities.append(Quantity(name, kind, refs, float(value) * scale, float(tol) * scale))
    problems += [f"quantity name {n!r} appears {k} times" for n, k in seen.items() if k > 1 and gconfig._filled(n)]
    axes = data.get("axes")
    if not (isinstance(axes, list) and axes and all(a in AXES for a in axes) and len(set(axes)) == len(axes)):
        problems.append(f"axes must list the axes allowed to move, from {list(AXES)}")
        axes = []
    elif isinstance(raw, list) and len(axes) > len(raw):
        problems.append(f"{len(axes)} axes cannot be solved from {len(raw)} quantities: list no more axes than quantities")
    return TargetConfig(path, data, quantities, list(axes), units, problems)


class TargetModel:
    """A response model re-expressed in target quantities, linearized at one observation."""

    def __init__(self, base, gradient: np.ndarray, names: list[str]):
        self.base = base
        self.feature_names = list(names)
        self.j_plus = gradient @ np.nan_to_num(base.j_plus)
        self.j_minus = gradient @ np.nan_to_num(base.j_minus)
        self.residual_scale = np.sqrt((gradient ** 2) @ (np.nan_to_num(base.residual_scale) ** 2))
        self.deadband = base.deadband
        self.deadband_halfwidth = base.deadband_halfwidth

    @property
    def model_id(self) -> str:
        return self.base.model_id


# ---- jog plan ----------------------------------------------------------------------------------------

def make_plan(axes=AXES, sizes=(16, 32, 64, 256), repeats: int = 3, trials_per_size: int = 2,
              max_step: int = 256, engage_counts: int = 256, min_motion_z: float = 8.0) -> dict:
    from .experiment import PROBE_PATTERN
    return {"format_version": FORMAT_VERSION, "kind": "jog_plan", "axes": list(axes), "sizes": [int(s) for s in sizes],
            "repeats": int(repeats), "trials_per_size": int(trials_per_size), "max_step_counts": int(max_step),
            "engage_counts": int(engage_counts), "min_motion_z": float(min_motion_z), "pattern": PROBE_PATTERN,
            "enlarge_rule": "the next size runs only after the previous size moved the features by at least "
                            "min_motion_z noise units on two steps",
            "firmware_max_jog_counts": MAX_JOG_COUNTS, "counts_per_mm": COUNTS_PER_MM}


def plan_problems(plan) -> list[str]:
    if not isinstance(plan, dict):
        return ["the plan is not a JSON object"]
    problems = []
    if plan.get("format_version") != FORMAT_VERSION or plan.get("kind") != "jog_plan":
        problems.append("not a jog plan written by observe.py learn plan")
    axes = plan.get("axes")
    if not (isinstance(axes, list) and axes and all(a in AXES for a in axes)):
        problems.append(f"axes must be from {list(AXES)}")
    max_step = plan.get("max_step_counts")
    if not (_int(max_step) and 1 <= max_step <= MAX_JOG_COUNTS):
        problems.append(f"max_step_counts must be 1..{MAX_JOG_COUNTS} (the firmware's per-axis bound)")
        max_step = 0
    sizes = plan.get("sizes")
    if not (isinstance(sizes, list) and sizes and all(_int(s) and s >= 1 for s in sizes)):
        problems.append("sizes must be positive integer counts")
    elif any(s > max_step for s in sizes):
        problems.append(f"sizes {sizes} exceed max_step_counts {max_step}")
    engage = plan.get("engage_counts")
    if not (_int(engage) and 1 <= engage <= max(max_step, 0)):
        problems.append("engage_counts must be at least 1 and at most max_step_counts")
    for key in ("repeats", "trials_per_size"):
        if not (_int(plan.get(key)) and plan[key] >= 1):
            problems.append(f"{key} must be an integer of at least 1")
    if not (_num(plan.get("min_motion_z")) and plan["min_motion_z"] > 0):
        problems.append("min_motion_z must be positive")
    return problems


# ---- simulated world -----------------------------------------------------------------------------------

class SimWorld:
    """A simulated mechanism whose features are those of a features file, persisted between commands.

    Point features (dot, wire) move with the axes through a random well-conditioned
    response with direction-dependent gains and backlash; seam features stay still,
    as the tube does.
    """

    def __init__(self, names: list[str], seed: int = 7, frame=(3840, 2160), starts: dict | None = None,
                 backlash=(60, 35, 90, 120, 45, 75), noise_px: float = 0.15, profile: str = "loaded-development"):
        from .simulation import MechanismTruth, SimulatedMechanism, SimulatedPositioner
        rng = np.random.default_rng(seed)
        m, n = len(names), len(AXES)
        moving = np.array([name.endswith((".u", ".v")) for name in names])
        while True:
            base = 0.08 * rng.normal(size=(m, n)) * moving[:, None]
            k = int(moving.sum())
            if k < n or np.linalg.cond(base[moving]) < 8:
                break
        start = np.array([rng.uniform(0.35, 0.65) * (frame[0] if nm.endswith(".u") else frame[1])
                          if nm.endswith((".u", ".v")) else
                          (90.0 + rng.uniform(-3, 3) if nm.endswith(".theta_deg") else rng.uniform(-30, 30))
                          for nm in names])          # a seam's rho is about its ROI centre
        for i, nm in enumerate(names):
            if starts and nm in starts:
                start[i] = starts[nm]
        # Per-frame noise: noise_px for positions and rho; a few hundredths of a degree for a
        # seam angle fitted over hundreds of pixels.
        noise = np.array([0.02 if nm.endswith(".theta_deg") else noise_px for nm in names])
        truth = MechanismTruth(tuple(names), base * (1 + 0.15 * rng.uniform(-1, 1, size=n)),
                               base * (1 + 0.15 * rng.uniform(-1, 1, size=n)), np.asarray(backlash, float),
                               0.004 * rng.normal(size=m) * moving, 0.002, noise, start=start)
        self.clock = FakeClock(wall_start_ns=time.time_ns())     # simulated monotonic time, real wall time
        self.mechanism = SimulatedMechanism(truth, seed=seed + 4)
        self.positioner = SimulatedPositioner(self.mechanism, self.clock, profile=profile)
        self.observer_rng_state = np.random.default_rng(seed + 9).bit_generator.state
        self.meta = {"seed": seed, "frame": list(frame), "profile": profile}

    @property
    def names(self) -> list[str]:
        return list(self.mechanism.truth.feature_names)

    def observer(self, writer, frames: int):
        from .experiment import SimulatedObserver
        obs = SimulatedObserver(self.mechanism, writer, self.clock, frames=frames)
        obs.rng.bit_generator.state = self.observer_rng_state
        self._observer = obs
        return obs

    def to_dict(self) -> dict:
        t, mech, pos = self.mechanism.truth, self.mechanism, self.positioner
        if getattr(self, "_observer", None) is not None:
            self.observer_rng_state = self._observer.rng.bit_generator.state
        arr = lambda a: np.asarray(a, float).tolist()
        return {"format_version": FORMAT_VERSION, "kind": "simulated_world", "meta": self.meta,
                "names": list(t.feature_names), "j_plus": arr(t.j_plus), "j_minus": arr(t.j_minus),
                "backlash": arr(t.backlash), "drift_per_s": arr(t.drift_per_s), "drift_walk": t.drift_walk,
                "noise": arr(t.noise), "start": arr(t.start), "input": arr(mech.input), "output": arr(mech.output),
                "features": arr(mech.features), "drift": arr(mech.drift), "t_ns": mech.t_ns,
                "mechanism_rng": mech.rng.bit_generator.state, "observer_rng": self.observer_rng_state,
                "clock_ns": self.clock.monotonic_ns(), "positioner": {"counts": pos.counts, "seq": pos.seq}}

    def save(self, path) -> None:
        Path(path).write_text(json.dumps(self.to_dict()) + "\n")

    @classmethod
    def load(cls, path) -> "SimWorld":
        from .simulation import MechanismTruth, SimulatedMechanism, SimulatedPositioner
        d = json.loads(Path(path).read_text())
        w = cls.__new__(cls)
        truth = MechanismTruth(tuple(d["names"]), np.array(d["j_plus"]), np.array(d["j_minus"]),
                               np.array(d["backlash"]), np.array(d["drift_per_s"]), d["drift_walk"],
                               np.array(d["noise"]), start=np.array(d["start"]))
        w.clock = FakeClock(start_ns=d["clock_ns"], wall_start_ns=time.time_ns())
        w.mechanism = SimulatedMechanism(truth)
        w.mechanism.rng.bit_generator.state = d["mechanism_rng"]
        w.mechanism.input, w.mechanism.output = np.array(d["input"]), np.array(d["output"])
        w.mechanism.features, w.mechanism.drift = np.array(d["features"]), np.array(d["drift"])
        w.mechanism.t_ns = d["t_ns"]
        w.meta = d["meta"]
        w.positioner = SimulatedPositioner(w.mechanism, w.clock, profile=w.meta["profile"])
        w.positioner.counts, w.positioner.seq = list(d["positioner"]["counts"]), d["positioner"]["seq"]
        w.observer_rng_state = d["observer_rng"]
        return w


def world_starts(features: FeatureConfig, seed: int) -> dict:
    """Each simulated feature starts near the centre of its ROI; a seam lies across its ROI."""
    from .features import roi_center
    rng = np.random.default_rng(seed + 21)
    starts = {}
    for f in features.features:
        cx, cy = roi_center(f.roi)
        prefix = f"{f.camera_id}.{f.label}"
        if f.type in POINT_TYPES:
            starts[f"{prefix}.u"], starts[f"{prefix}.v"] = cx + rng.uniform(-5, 5), cy + rng.uniform(-5, 5)
        else:
            base = 90.0 if f.params.get("orientation") == "horizontal" else 0.0
            starts[f"{prefix}.theta_deg"], starts[f"{prefix}.rho"] = base + rng.uniform(-2, 2), rng.uniform(-5, 5)
    return starts


def world_for(path, features: FeatureConfig, seed: int) -> SimWorld:
    path = Path(path)
    names = features.names()
    if path.exists():
        world = SimWorld.load(path)
        if world.names != list(names):
            raise SystemExit(f"{path} simulates other features; remove it or pass another --world")
        return world
    return SimWorld(names, seed=seed, starts=world_starts(features, seed))


# ---- gates in front of real motion ----------------------------------------------------------------------

def controller_refusals(status: dict | None) -> list[str]:
    """Reasons the controller is not ready for a move, from its STATUS."""
    if not status:
        return ["no controller status"]
    reasons = []
    if status.get("drivers_ok") is not True:
        reasons.append("drivers_ok is not true")
    micro = status.get("microsteps")
    if not (micro == 16 or (isinstance(micro, list) and len(micro) == 6 and all(m == 16 for m in micro))):
        reasons.append(f"microsteps not verified as 16 on every axis: {micro}")
    if status.get("referenced") is not True:
        reasons.append("not referenced: establish the physical central datum, then type 'reference central'")
    if status.get("state") != "armed":
        reasons.append(f"controller state is {status.get('state')!r}, not armed: type 'arm'")
    if status.get("fault") not in (None, "none"):
        reasons.append(f"controller fault {status.get('fault')!r}: clear it and re-establish the datum")
    if status.get("counts_per_mm") != COUNTS_PER_MM:
        reasons.append(f"controller counts_per_mm {status.get('counts_per_mm')} is not {COUNTS_PER_MM}")
    if not _int(status.get("max_rate")):
        reasons.append("controller did not report max_rate")
    reasons += [f"driver profile: {p}" for p in profile_problems(status)]
    return reasons


def move_refusals(counts, current_counts, max_step: int) -> list[str]:
    """Reasons one move may not be sent: bounds, zero move, soft limits."""
    reasons = []
    if not (isinstance(counts, (list, tuple)) and len(counts) == 6 and all(_int(c) for c in counts)):
        return ["a move is six integer counts"]
    bound = min(int(max_step), MAX_JOG_COUNTS)
    over = [AXES[i] for i, c in enumerate(counts) if abs(c) > bound]
    if over:
        reasons.append(f"counts on {over} exceed the {bound}-count bound")
    if not any(counts):
        reasons.append("zero move")
    if current_counts is None:
        reasons.append("the controller's issued counts are unknown")
    else:
        bad = [AXES[i] for i, (now, c) in enumerate(zip(current_counts, counts))
               if not SOFT_MIN[i] <= now + c <= SOFT_MAX[i]]
        if bad:
            reasons.append(f"move would leave the soft limits on {bad}")
    return reasons


class GatedBackend(PositionerBackend):
    """The controls backend behind per-move checks. The first refusal or non-done move halts it."""

    def __init__(self, inner, max_step: int, clock: Clock | None = None):
        self.inner, self.max_step = inner, int(max_step)
        self.clock = clock or inner.clock
        self.max_rate = inner.max_rate
        self.halted: list[str] | None = None
        self.info = BackendInfo("controls_client_gated", "controller", True,
                                f"per-move gate: controller ready, |counts| <= {min(self.max_step, MAX_JOG_COUNTS)}, "
                                "soft limits")

    def execute(self, cmd):
        status = self.inner.last_status
        reasons = list(self.halted) if self.halted else (
            controller_refusals(status) + move_refusals(list(cmd.counts), status.get("count") if status else None,
                                                        self.max_step))
        if reasons:
            self.halted = self.halted or reasons
            now = self.clock.monotonic_ns()
            return MoveOutcome("rejected", now, now, error="refused before sending: " + "; ".join(reasons))
        out = self.inner.execute(cmd)
        self.max_rate = self.inner.max_rate
        if out.status != "done":
            self.halted = [f"move {cmd.cmd_id} ended {out.status}"]
        return out

    def status(self) -> dict:
        return self.inner.status()

    def stop(self) -> None:
        self.inner.stop()


CONSOLE_HELP = "type: status | clear | reference central | arm | go | stop | quit"


def operator_console(client, input_fn=input, print_fn=print) -> bool:
    """The operator prepares the controller; True once it is ready and the operator typed go.

    Only operator-typed lines send CLEAR, REF or ARM. `reference central` asserts
    that the physical central datum has been established, as in the controls console.
    """
    print_fn("Motion needs the controller cleared, referenced at the physical central datum, and armed.")
    print_fn("Establish the datum physically before typing 'reference central'. " + CONSOLE_HELP)
    while True:
        try:
            line = input_fn("observe learn> ").strip()
        except EOFError:
            return False
        try:
            if line == "status":
                s = client.status()
                print_fn(json.dumps({k: s.get(k) for k in ("state", "fault", "referenced", "drivers_ok", "microsteps",
                                                           "profile", "max_rate", "count", "vm_epoch")}))
            elif line == "clear":
                client.request("CLEAR")
            elif line == "reference central":
                client.request("REF")
            elif line == "arm":
                client.request("ARM")
                client.start_heartbeat()
            elif line == "stop":
                client.stop()
            elif line == "quit":
                return False
            elif line == "go":
                reasons = controller_refusals(client.status())
                if not reasons:
                    return True
                print_fn("not ready: " + "; ".join(reasons))
            elif line:
                print_fn(CONSOLE_HELP)
        except Exception as exc:  # a rejected request is reported; the operator decides what next
            print_fn(f"{type(exc).__name__}: {exc}")


def static_refusals(flag: bool, cameras_path, features_path, plan: dict | None = None, target_path=None,
                    validation: dict | None = None) -> list[str]:
    """Everything checkable before connecting to the controller."""
    from . import helper_stream
    reasons = [] if flag else [f"real motion needs the explicit {HARDWARE_FLAG} flag"]
    if cameras_path is None:
        reasons.append("real motion needs --cameras (a configuration that passes measurement validation)")
        frame_sizes = None
    else:
        cfg = gconfig.load_config(Path(cameras_path).expanduser())
        reasons += [f"cameras: {p}" for p in cfg.problems("measurement")]
        if cfg.clock_receipt is None:
            reasons.append("clock check: no receipt named in the camera configuration")
        else:
            clock_problems = gconfig.clock_receipt_problems(cfg.clock_receipt, helper_stream.BINARY)
            reasons += [f"clock check: {p}" for p in clock_problems]
        frame_sizes = {c.camera_id: (c.verified_format["width"], c.verified_format["height"])
                       for c in cfg.cameras if c.verified_format}
    features = load_features(Path(features_path).expanduser(), frame_sizes)
    reasons += [f"features: {p}" for p in features.problems]
    if plan is not None:
        reasons += [f"plan: {p}" for p in plan_problems(plan)]
    if target_path is not None:
        reasons += [f"target: {p}" for p in load_target(Path(target_path).expanduser(), features).problems]
    if validation is not None and validation.get("passed") is not True:
        reasons.append("validation: the model's held-out validation did not pass")
    return reasons


# ---- shared pieces of the workflow ----------------------------------------------------------------------

def optics_provider(cfg, clock: Clock):
    """Optics states for a validated camera configuration: receipts, or live VISCA read-back."""
    from . import optics, visca
    provider = optics.OpticsProvider()
    for cam in cfg.cameras:
        if cam.optics_source == "operator" and cam.receipt is not None and cam.receipt.state is not None \
                and not cam.receipt.problems:
            provider.set_state(cam.receipt.state)
        elif cam.optics_source == "visca" and cam.visca is not None:
            v = cam.visca
            transport = (visca.SerialTransport(v["serial_port"], v["baud"]) if v["transport"] == "serial" else
                         visca.TcpTransport(v["host"], v["port"]) if v["transport"] == "tcp" else
                         visca.UdpTransport(v["host"], v["port"]))
            client = visca.ViscaClient(transport, v["address"], clock=clock)
            provider.set_reader(cam.camera_id, lambda c=client, i=cam.camera_id: visca.read_optics(c, i)[0])
    return provider


def open_cameras(cfg, writer, clock: Clock, launch: str = "open", synchronous: bool = False,
                 source_factory=None, store: str = "window_first"):
    """A CaptureSession over the configuration's verified formats (measurement-validated cfg)."""
    from . import helper_stream
    from .capture import CameraCapture, CameraSpec, CaptureSession, StorePolicy
    captures = []
    for cam in cfg.cameras:
        vf = cam.verified_format
        spec = CameraSpec(cam.camera_id, cam.unique_id, cam.name or "", cam.position or "", vf["width"],
                          vf["height"], cam.codec, vf["fps"], cam.require_native_4k)
        source = source_factory(cam) if source_factory else helper_stream.HelperSource(
            cam.camera_id, cam.unique_id, vf["width"], vf["height"], vf["fps"], subtypes=vf["pixel_format"],
            chroma=vf["chroma"], mode=launch, name=cam.name or "", log_path=writer.path / f"helper-{cam.camera_id}.log")
        captures.append(CameraCapture(spec, source, writer, clock, StorePolicy(store)))
    return CaptureSession(writer, captures, optics_provider(cfg, clock), clock, synchronous=synchronous,
                          receipt_max_age_s=cfg.receipt_max_age_s)


def feature_summary(observations: list, names: list[str]) -> dict:
    out = {}
    for n in names:
        vals = [o.values.get(n) for o in observations]
        good = [v for v in vals if v is not None]
        out[n] = {"valid": f"{len(good)}/{len(vals)}",
                  "mean": round(float(np.mean(good)), 4) if good else None,
                  "spread": round(float(np.std(good)), 4) if len(good) > 1 else None,
                  "last_sigma": observations[-1].sigma.get(n) if observations else None,
                  "mean_confidence": round(float(np.mean([o.confidence.get(n) or 0.0 for o in observations])), 3)
                  if observations else None}
    return out


def _refuse(print_fn, reasons: list[str], code: int = 2) -> int:
    print_fn("refused:\n  " + "\n  ".join(reasons))
    return code


def _session_state(reader) -> dict:
    """Direction state, issued counts and last completion from a session's move receipts."""
    records = reader.records()
    done = {r["cmd_id"]: r for r in records if r["kind"] == "move_complete" and r["status"] == "done"}
    if not done:
        return {"direction": None, "counts": None, "last_complete_ns": None}
    direction, counts, last = [0] * len(AXES), None, None
    for r in records:
        if r["kind"] == "move_command" and r["cmd_id"] in done:
            for i, c in enumerate(r["counts"]):
                if c:
                    direction[i] = 1 if c > 0 else -1
            d = done[r["cmd_id"]]
            counts = d.get("reported_counts") or counts
            last = d["complete_mono_ns"]
    return {"direction": direction, "counts": counts, "last_complete_ns": last}


def _observation_from(rec: dict) -> Observation:
    return Observation(rec["obs_id"], rec["t_start_ns"], rec["t_end_ns"], rec["values"], rec.get("sigma", {}),
                       rec.get("confidence", {}), rec.get("trial_id"))


# ---- the steps ------------------------------------------------------------------------------------------

def run_check(args, print_fn=print) -> int:
    report = {}
    cfg = None
    if args.cameras:
        cfg = gconfig.load_config(Path(args.cameras).expanduser())
        report["cameras"] = cfg.problems("measurement")
    frame_sizes = ({c.camera_id: (c.verified_format["width"], c.verified_format["height"])
                    for c in cfg.cameras if c.verified_format} if cfg else None)
    feats = load_features(Path(args.features).expanduser(), frame_sizes)
    report["features"] = feats.problems
    if args.target:
        report["target"] = load_target(Path(args.target).expanduser(), feats).problems
    if args.plan:
        plan, problems = _read(Path(args.plan).expanduser())
        report["plan"] = problems + (plan_problems(plan) if plan else [])
    ok = not any(report.values())
    print_fn(json.dumps({"ok": ok, "problems": report}, indent=1))
    return 0 if ok else 1


def run_plan(args, print_fn=print) -> int:
    plan = make_plan(args.axes, args.sizes, args.repeats, args.trials_per_size, args.max_step, args.engage_counts,
                     args.min_motion_z)
    problems = plan_problems(plan)
    if problems:
        return _refuse(print_fn, problems)
    out = Path(args.out).expanduser()
    out.write_text(json.dumps(plan, indent=1) + "\n")
    per_trial = len(plan["sizes"]) * plan["trials_per_size"] * 4 * plan["repeats"]
    print_fn(f"{out}\n{len(plan['axes'])} axes x {len(plan['sizes'])} sizes x {plan['trials_per_size']} trials; "
             f"up to {per_trial} jog moves per axis plus engagement; every move <= {plan['max_step_counts']} counts")
    return 0


def run_record(args, clock=None, synchronous=False, source_factory=None, print_fn=print) -> int:
    from .capture import CameraObserver, MeasurementRefused
    from .dataset import SessionWriter
    root = Path(args.root).expanduser()
    observations = []
    if args.backend == "simulator":
        feats = load_features(Path(args.features).expanduser())
        if feats.problems:
            return _refuse(print_fn, [f"features: {p}" for p in feats.problems])
        world_path = Path(args.world).expanduser() if args.world else root / "simulated-world.json"
        root.mkdir(parents=True, exist_ok=True)
        world = world_for(world_path, feats, args.seed)
        writer = SessionWriter(root, args.label, world.clock,
                               config={"step": "record", "backend": "simulator", "features": feats.data})
        observer = world.observer(writer, feats.frames_per_observation)
        prev = None
        for _ in range(args.observations):
            o = observer.observe(None, prev, [], world.clock.monotonic_ns() + int(args.interval_s * 1e9))
            observations.append(o)
            prev = o.obs_id
        world.save(world_path)
    else:
        try:
            cfg = gconfig.validate(Path(args.cameras).expanduser(), "measurement")
        except (gconfig.ConfigError, TypeError) as exc:
            return _refuse(print_fn, getattr(exc, "problems", [str(exc)]))
        sizes = {c.camera_id: (c.verified_format["width"], c.verified_format["height"]) for c in cfg.cameras}
        feats = load_features(Path(args.features).expanduser(), sizes)
        if feats.problems:
            return _refuse(print_fn, [f"features: {p}" for p in feats.problems])
        clock = clock or Clock()
        writer = SessionWriter(root, args.label, clock,
                               config={"step": "record", "backend": "cameras", "capture_config": cfg.data,
                                       "features": feats.data})
        session = open_cameras(cfg, writer, clock, args.launch, synchronous, source_factory, args.store_frames)
        session.start()
        try:
            observer = CameraObserver(session, feats.extractors(), writer, clock,
                                      frames_per_camera=feats.frames_per_observation,
                                      min_valid_fraction=feats.min_valid_fraction)
            prev = None
            for _ in range(args.observations):
                o = observer.observe(None, prev, [], clock.monotonic_ns() + int(args.interval_s * 1e9))
                observations.append(o)
                prev = o.obs_id
        except MeasurementRefused as exc:
            print_fn(f"measurement refused: {exc.reasons}")
        finally:
            session.stop()
    summary = {"session": str(writer.path), "observations": len(observations),
               "features": feature_summary(observations, feats.names())}
    if args.target:
        target = load_target(Path(args.target).expanduser(), feats)
        if target.problems:
            summary["target_problems"] = target.problems
        elif observations:
            q = target.transform(observations[-1])
            summary["target_quantities"] = {n: {"value": q.values[n], "sigma": q.sigma[n], "desired": target.values()[n],
                                                "error": None if q.values[n] is None else
                                                round(target.values()[n] - q.values[n], 4),
                                                "tolerance": target.tolerances()[n]} for n in target.names()}
    with open(writer.path / "feature-summary.json", "x") as fh:
        fh.write(json.dumps(summary, indent=1) + "\n")
    writer.close()
    print_fn(json.dumps(summary, indent=1))
    complete = observations and all(all(o.values.get(n) is not None for n in feats.names()) for o in observations)
    return 0 if complete else 1


def _connect(args, writer, clock):
    from .controls import ControlsClientBackend
    return ControlsClientBackend.for_session(args.port, writer, clock)


def run_jog(args, clock=None, synchronous=False, source_factory=None, input_fn=input, print_fn=print) -> int:
    from .capture import CameraObserver
    from .dataset import SessionWriter
    from .experiment import Runner
    from .moves import MoveRecorder
    root = Path(args.root).expanduser()
    plan, problems = _read(Path(args.plan).expanduser())
    problems += plan_problems(plan) if plan else []
    axes = [AXES.index(a) for a in plan.get("axes", [])] if not problems else []
    if args.backend == "simulator":
        feats = load_features(Path(args.features).expanduser())
        problems += [f"features: {p}" for p in feats.problems]
        if problems:
            return _refuse(print_fn, problems)
        world_path = Path(args.world).expanduser() if args.world else root / "simulated-world.json"
        root.mkdir(parents=True, exist_ok=True)
        world = world_for(world_path, feats, args.seed)
        writer = SessionWriter(root, args.label, world.clock,
                               config={"step": "jog", "backend": "simulator", "plan": plan, "features": feats.data})
        recorder = MoveRecorder(world.positioner, writer, world.clock)
        runner = Runner(recorder, world.observer(writer, feats.frames_per_observation), writer, world.clock,
                        settle_s=feats.settle_s)
        runner.engage(plan["engage_counts"], 2, axes)
        runner.identify(axes, plan["sizes"], plan["trials_per_size"], plan["repeats"], plan["min_motion_z"])
        world.save(world_path)
        halted = None
    else:
        problems += static_refusals(args.i_understand_this_moves_hardware, args.cameras, args.features, plan=plan)
        if not args.port:
            problems.append("--port names the controller's USB serial device")
        if problems:
            return _refuse(print_fn, problems)
        cfg = gconfig.validate(Path(args.cameras).expanduser(), "measurement")
        sizes = {c.camera_id: (c.verified_format["width"], c.verified_format["height"]) for c in cfg.cameras}
        feats = load_features(Path(args.features).expanduser(), sizes)
        clock = clock or Clock()
        writer = SessionWriter(root, args.label, clock,
                               config={"step": "jog", "backend": "controller", "plan": plan,
                                       "capture_config": cfg.data, "features": feats.data})
        backend = _connect(args, writer, clock)
        session = None
        halted = None
        try:
            if not operator_console(backend.client, input_fn, print_fn):
                writer.append("session_note", author="learn jog", text="operator ended before motion")
                writer.close("no motion")
                print_fn("no motion: the operator ended the session")
                return 3
            backend.status()
            gated = GatedBackend(backend, plan["max_step_counts"], clock)
            recorder = MoveRecorder(gated, writer, clock, allow_hardware=True)
            session = open_cameras(cfg, writer, clock, args.launch, synchronous, source_factory, args.store_frames)
            session.start()
            observer = CameraObserver(session, feats.extractors(), writer, clock,
                                      frames_per_camera=feats.frames_per_observation,
                                      min_valid_fraction=feats.min_valid_fraction)
            runner = Runner(recorder, observer, writer, clock, settle_s=feats.settle_s)

            def stop():
                last = runner.results[-1] if runner.results else None
                return gated.halted is not None or (last is not None and last.outcome == "failed"
                                                    and (last.reason or "").startswith("measurement refused"))

            runner.engage(plan["engage_counts"], 2, axes)
            if not stop():
                runner.identify(axes, plan["sizes"], plan["trials_per_size"], plan["repeats"], plan["min_motion_z"],
                                should_stop=stop)
            halted = gated.halted
        finally:
            if session is not None:
                session.stop()
            backend.client.close(stop_motion=True)
    writer.close("closed" if not halted else "halted")
    from .dataset import SessionReader
    reader = SessionReader(writer.path)
    outcomes = Counter(r["outcome"] for r in reader.records("trial_end"))
    moves = Counter(r["status"] for r in reader.records("move_complete"))
    print_fn(json.dumps({"session": str(writer.path), "trial_outcomes": dict(outcomes), "moves": dict(moves),
                         "observations": len(reader.records("observation")), "halted": halted}, indent=1))
    return 0 if not halted else 4


def _groups(readers):
    groups, purposes = {}, {}
    for r in readers:
        for rec in r.records("trial_start"):
            groups[rec["trial_id"]] = rec["plan"].get("group", rec["purpose"])
            purposes[rec["trial_id"]] = rec["purpose"]
    return groups, purposes


def run_fit(args, print_fn=print) -> int:
    from . import response, validation
    from .dataset import SessionReader
    feats = load_features(Path(args.features).expanduser())
    if feats.problems:
        return _refuse(print_fn, [f"features: {p}" for p in feats.problems])
    readers = [SessionReader(Path(s).expanduser()) for s in args.sessions]
    data = response.assemble(readers, feats.names())
    groups, purposes = _groups(readers)
    probes = [t for t in data.trials() if purposes.get(t) == "probe"]
    if len(probes) < 2:
        return _refuse(print_fn, [f"only {len(probes)} probe trials with usable steps; run learn jog first"])
    train, holdout = validation.split_trials(probes, args.holdout_fraction, args.seed, groups)
    train += [t for t in data.trials() if t not in set(probes)]
    try:
        model = response.fit(data, train, max_deadband=args.max_deadband)
    except ValueError as exc:
        return _refuse(print_fn, [str(exc), "a step counts only once its axis's take-up state is known: after a "
                                  f"one-direction run of at least --max-deadband ({args.max_deadband:g}) counts. "
                                  "Keep 2 x engage_counts of the plan at or above it, or lower --max-deadband."])
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    (out / "model.json").write_text(model.to_json() + "\n")
    split = {"format_version": FORMAT_VERSION, "sessions": [str(r.path) for r in readers], "seed": args.seed,
             "holdout_fraction": args.holdout_fraction, "train": sorted(train), "holdout": sorted(holdout),
             "rule": "whole trials, stratified by probed axis; no trial is split"}
    (out / "split.json").write_text(json.dumps(split, indent=1) + "\n")
    print_fn(json.dumps({"model": str(out / "model.json"), "split": str(out / "split.json"), "model_id": model.model_id,
                         "training_trials": len(train), "held_out_trials": len(holdout), "training_rows": model.n_rows,
                         "training_outliers": len(model.outliers),
                         "deadband_counts": dict(zip(AXES, np.round(model.deadband, 1).tolist()))}, indent=1))
    return 0


def validation_text(report, model) -> str:
    lines = [f"VALIDATION: {'PASS' if report.passed else 'FAIL'}",
             f"model {model.model_id}; trained on {len(model.train_trials)} trials; "
             f"held out {len(report.holdout_trials)} trials (whole trials, never split)",
             f"held-out steps: {report.n_steps} (outliers {report.n_outliers}; "
             f"excluded with unknown take-up {report.n_unknown_takeup_excluded})",
             "criteria: " + ", ".join(f"{k}={v}" for k, v in report.criteria.items()), "",
             f"{'feature':<28}{'rms':>9}{'null_rms':>10}{'skill':>9}{'bias':>9}  verdict"]
    for name, st in report.per_feature.items():
        skill = "-" if st["skill"] is None else f"{st['skill']:.4f}"
        verdict = ("not exercised" if not st["exercised"] else
                   "ok" if st["skill"] >= report.criteria["min_skill"] else "FAIL")
        bias = "-" if st["bias"] is None else f"{st['bias']:.3f}"
        lines.append(f"{name:<28}{st['rms']:>9.3f}{st['null_rms']:>10.3f}{skill:>9}{bias:>9}  {verdict}")
    lines += ["", f"{'axis-direction':<16}{'steps':>7}{'skill':>9}  verdict"]
    for ad, st in report.axis_directions.items():
        skill = "-" if st["skill"] is None else f"{st['skill']:.4f}"
        lines.append(f"{ad:<16}{st['held_out_steps']:>7}{skill:>9}  {'validated' if st['validated'] else 'not validated'}")
    base = report.baseline_visual_servo
    if base.get("available"):
        lines += ["", "baseline visual_servo.fit_jacobian held-out rms: " +
                  ", ".join(f"{k}={v['rms']:.3f}" for k, v in base["per_feature"].items())]
    lines += ["", "reasons: " + ("none" if not report.reasons else "; ".join(report.reasons))]
    return "\n".join(lines) + "\n"


def run_validate(args, print_fn=print) -> int:
    from . import response, validation
    from .dataset import SessionReader
    model = response.ResponseModel.from_dict(json.loads(Path(args.model).expanduser().read_text()))
    readers = [SessionReader(Path(s).expanduser()) for s in args.sessions]
    data = response.assemble(readers, model.feature_names)
    if args.split:
        holdout = json.loads(Path(args.split).expanduser().read_text())["holdout"]
    else:
        _, purposes = _groups(readers)
        holdout = [t for t in data.trials() if purposes.get(t) == "probe" and t not in set(model.train_trials)]
    report = validation.validate(model, data, holdout, min_skill=args.min_skill)
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    (out / "validation.json").write_text(report.to_json() + "\n")
    text = validation_text(report, model)
    (out / "validation-report.txt").write_text(text)
    print_fn(text + f"{out / 'validation.json'}\n{out / 'validation-report.txt'}")
    return 0 if report.passed else 1


def _load_model_and_report(args):
    from . import response, validation
    model = response.ResponseModel.from_dict(json.loads(Path(args.model).expanduser().read_text()))
    report_data = json.loads(Path(args.validation).expanduser().read_text())
    return model, validation.ValidationReport.from_dict(report_data), report_data


def run_propose(args, print_fn=print) -> int:
    from .dataset import SessionReader
    from .proposal import ProposalConfig, propose
    feats = load_features(Path(args.features).expanduser())
    target = load_target(Path(args.target).expanduser(), feats)
    problems = [f"features: {p}" for p in feats.problems] + [f"target: {p}" for p in target.problems]
    if problems:
        return _refuse(print_fn, problems)
    model, report, _ = _load_model_and_report(args)
    state = {"direction": None, "counts": None, "last_complete_ns": None}
    if args.session:
        reader = SessionReader(Path(args.session).expanduser())
        obs_records = reader.records("observation")
        if not obs_records:
            return _refuse(print_fn, [f"{args.session} holds no observation"])
        obs = _observation_from(obs_records[-1])
        state = _session_state(reader)
    else:
        obs = _observation_from(json.loads(Path(args.observation).expanduser().read_text()))
    missing = [n for n in model.feature_names if obs.values.get(n) is None]
    q_obs = target.transform(obs)
    sensitivity = {}
    if missing:
        p = {"status": "zero", "counts": [0] * 6, "reasons": [f"missing_feature:{n}" for n in missing]}
    else:
        tm = TargetModel(model, target.gradient_matrix(obs, model.feature_names), target.names())
        mean = 0.5 * (tm.j_plus + tm.j_minus)
        sensitivity = {n: dict(zip(AXES, np.round(mean[i], 5).tolist())) for i, n in enumerate(target.names())}
        cfg = ProposalConfig(max_step_counts=(args.max_step,) * 6, tolerance=target.tolerances(),
                             features=target.names(), settle_s=feats.settle_s)
        hold = [a for a in AXES if a not in target.axes]
        p = propose(tm, report, q_obs, target.values(), cfg, obs.t_end_ns + 1, state["last_complete_ns"],
                    state["counts"], state["direction"], None, hold).as_dict()
    result = {"format_version": FORMAT_VERSION, "kind": "review_proposal", "review_only": True,
              "note": "never executed; learn execute recomputes every move from a fresh observation",
              "created_at": gconfig.iso_time(time.time_ns()), "observation_id": obs.obs_id,
              "evaluated_as_of_observation": True, "model_id": model.model_id,
              "validation_passed": report.passed, "axes": target.axes, "max_step_counts": args.max_step,
              "quantities": {n: {"observed": q_obs.values[n], "desired": target.values()[n],
                                 "tolerance": target.tolerances()[n]} for n in target.names()},
              "sensitivity_px_per_count": sensitivity,
              "takeup_state": ("from the session's moves" if state["direction"] is not None else
                               "unknown (no moves in this session); learn execute engages the target axes first"),
              "proposal": p}
    out = Path(args.out).expanduser()
    out.write_text(json.dumps(result, indent=1) + "\n")
    print_fn(json.dumps(result, indent=1))
    return 0


def engagement_moves(model, axes: list[str], max_step: int) -> list[list[int]]:
    """Moves that make each axis's take-up state known: + then − runs of 1.5 dead-bands plus 16 counts.

    The runs end on the negative side of each gap with the position nearly where it began.
    """
    moves = []
    for sign in (1, -1):
        for a in axes:
            j = AXES.index(a)
            total = int(np.ceil(1.5 * float(np.nan_to_num(model.deadband[j])))) + 16
            while total > 0:
                step = min(total, max_step)
                counts = [0] * len(AXES)
                counts[j] = sign * step
                moves.append(counts)
                total -= step
    return moves


def correction_loop(recorder, observer, target: TargetConfig, model, report, cfg, writer, clock, settle_s: float,
                    confirm, max_moves: int, status_fn, print_fn=print) -> dict:
    """Engage the target axes, then observe, propose, confirm and move, within one session."""
    from .capture import MeasurementRefused
    from .proposal import CorrectionController
    trial_id = f"loop-{writer.session_id[-4:]}"
    writer.append("trial_start", trial_id=trial_id, purpose="closed_loop",
                  plan={"target": str(target.path), "axes": target.axes, "max_moves": max_moves},
                  direction_state=list(recorder.direction))
    settle_ns = int(settle_s * 1e9)
    outcome, reason, moves = "failed", None, 0

    def end(result):
        writer.append("trial_end", trial_id=trial_id, outcome=result["outcome"], reason=result["reason"])
        return result

    def observe(prev, cmd_ids):
        base = recorder.last_complete_ns
        start = max(base + settle_ns, clock.monotonic_ns()) if base else clock.monotonic_ns()
        return observer.observe(trial_id, prev.obs_id if prev else None, cmd_ids, start)

    unknown = [a for a in target.axes if recorder.direction[AXES.index(a)] == 0]
    if unknown:
        plan = engagement_moves(model, unknown, int(cfg.max_step_counts[0]))
        if not confirm({"purpose": "engage", "axes": unknown, "moves": plan,
                        "note": "take-up engagement before correction; ends near the starting position"}):
            return end({"outcome": "aborted", "reason": "the operator declined the engagement", "moves": 0,
                        "quantities": {}})
        for counts in plan:
            cmd, out = recorder.execute(counts, "engage", trial_id)
            moves += 1
            if out.status != "done":
                return end({"outcome": "fault", "reason": f"engagement move {cmd.cmd_id} {out.status}: {out.error}",
                            "moves": moves, "quantities": {}})
    try:
        obs = observe(None, [])
    except MeasurementRefused as exc:
        return end({"outcome": "failed", "reason": f"measurement refused: {exc.reasons}", "moves": moves,
                    "quantities": {}})
    corrections = 0
    if any(obs.values.get(n) is None for n in model.feature_names):
        reason = "features missing from the first observation"
    else:
        tm = TargetModel(model, target.gradient_matrix(obs, model.feature_names), target.names())
        ctl = CorrectionController(tm, report, cfg, hold=[a for a in AXES if a not in target.axes])
        while True:
            q = target.transform(obs)
            p = ctl.propose(q, target.values(), clock.monotonic_ns(), recorder.last_complete_ns, recorder.counts,
                            list(recorder.direction), status_fn())
            writer.append("proposal", proposal={**p.as_dict(), "trial_id": trial_id})
            if p.reasons == ["observation_inconsistent_with_last_move"]:
                obs = observe(obs, [])
                continue
            if p.status == "zero":
                reason = ";".join(p.reasons)
                outcome = "completed" if p.reasons == ["within_tolerance"] else "failed"
                break
            if corrections >= max_moves:
                outcome, reason = "aborted", f"stopped after {max_moves} correction moves"
                break
            if not confirm({"purpose": p.purpose, "proposed_counts": dict(zip(AXES, p.counts)), "error": p.error,
                            "predicted_change": p.predicted_change}):
                outcome, reason = "aborted", "the operator declined the move"
                break
            cmd, out = recorder.execute(p.counts, p.purpose, trial_id)
            moves += 1
            corrections += 1
            if out.status != "done":
                outcome, reason = "fault", f"move {cmd.cmd_id} {out.status}: {out.error}"
                break
            try:
                obs = observe(obs, [cmd.cmd_id])
            except MeasurementRefused as exc:
                outcome, reason = "failed", f"measurement refused after a move: {exc.reasons}"
                break
    final = target.transform(obs)
    return end({"outcome": outcome, "reason": reason, "moves": moves,
                "quantities": {n: {"observed": final.values[n], "desired": target.values()[n],
                                   "tolerance": target.tolerances()[n]} for n in target.names()}})


def run_execute(args, clock=None, synchronous=False, source_factory=None, input_fn=input, print_fn=print) -> int:
    from .capture import CameraObserver
    from .dataset import SessionWriter
    from .moves import MoveRecorder
    from .proposal import ProposalConfig
    root = Path(args.root).expanduser()
    model, report, report_data = _load_model_and_report(args)
    cfg_prop = None
    if args.backend == "simulator":
        feats = load_features(Path(args.features).expanduser())
        target = load_target(Path(args.target).expanduser(), feats)
        problems = [f"features: {p}" for p in feats.problems] + [f"target: {p}" for p in target.problems]
        if not report.passed:
            problems.append("validation: the model's held-out validation did not pass")
        if problems:
            return _refuse(print_fn, problems)
        world_path = Path(args.world).expanduser() if args.world else root / "simulated-world.json"
        root.mkdir(parents=True, exist_ok=True)
        world = world_for(world_path, feats, args.seed)
        writer = SessionWriter(root, args.label, world.clock,
                               config={"step": "execute", "backend": "simulator", "target": target.data})
        recorder = MoveRecorder(world.positioner, writer, world.clock)
        observer = world.observer(writer, feats.frames_per_observation)
        cfg_prop = ProposalConfig(max_step_counts=(args.max_step,) * 6, tolerance=target.tolerances(),
                                  features=target.names(), settle_s=feats.settle_s)
        result = correction_loop(recorder, observer, target, model, report, cfg_prop, writer, world.clock,
                                 feats.settle_s, lambda p: True, args.max_moves, world.positioner.status, print_fn)
        world.save(world_path)
    else:
        problems = static_refusals(args.i_understand_this_moves_hardware, args.cameras, args.features,
                                   target_path=args.target, validation=report_data)
        if not (1 <= args.max_step <= MAX_JOG_COUNTS):
            problems.append(f"--max-step must be 1..{MAX_JOG_COUNTS}")
        if not args.port:
            problems.append("--port names the controller's USB serial device")
        if problems:
            return _refuse(print_fn, problems)
        cfg = gconfig.validate(Path(args.cameras).expanduser(), "measurement")
        sizes = {c.camera_id: (c.verified_format["width"], c.verified_format["height"]) for c in cfg.cameras}
        feats = load_features(Path(args.features).expanduser(), sizes)
        target = load_target(Path(args.target).expanduser(), feats)
        clock = clock or Clock()
        writer = SessionWriter(root, args.label, clock,
                               config={"step": "execute", "backend": "controller", "capture_config": cfg.data,
                                       "features": feats.data, "target": target.data})
        backend = _connect(args, writer, clock)
        session = None
        try:
            if not operator_console(backend.client, input_fn, print_fn):
                print_fn("no motion: the operator ended the session")
                writer.close("no motion")
                return 3
            backend.status()
            gated = GatedBackend(backend, args.max_step, clock)
            recorder = MoveRecorder(gated, writer, clock, allow_hardware=True)
            session = open_cameras(cfg, writer, clock, args.launch, synchronous, source_factory, args.store_frames)
            session.start()
            observer = CameraObserver(session, feats.extractors(), writer, clock,
                                      frames_per_camera=feats.frames_per_observation,
                                      min_valid_fraction=feats.min_valid_fraction)
            cfg_prop = ProposalConfig(max_step_counts=(args.max_step,) * 6, tolerance=target.tolerances(),
                                      features=target.names(), settle_s=feats.settle_s)

            def confirm(summary: dict) -> bool:
                print_fn(json.dumps(summary))
                try:
                    return input_fn("move? type y to send: ").strip() == "y"
                except EOFError:
                    return False

            result = correction_loop(recorder, observer, target, model, report, cfg_prop, writer, clock,
                                     feats.settle_s, confirm, args.max_moves, lambda: backend.last_status, print_fn)
        finally:
            if session is not None:
                session.stop()
            backend.client.close(stop_motion=True)
    writer.close()
    result["session"] = str(writer.path)
    print_fn(json.dumps(result, indent=1))
    return 0 if result["outcome"] == "completed" else 1
