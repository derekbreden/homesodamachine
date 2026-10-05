"""Camera optics state and the measurement gate.

A frame is a measurement only when the camera's optics are known to be fixed:
manual focus, manual exposure and auto-tracking off. The state comes from a
VISCA inquiry (`source="visca_inquiry"`, read back from the camera) or from an
optics receipt file (`source="operator"`, loaded by `config.load_receipt` and
recorded as not read back in this session). Anything unknown fails the gate. The FoMaKo manual documents no inquiry for
auto-tracking, so tracking is "off_commanded" only after this session sent the
manual's Tracking OFF packet and received its Completion, or "off_operator"
when an operator file states it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json

FOCUS_MODES = {"manual", "auto", "one_push", "unknown"}
EXPOSURE_MODES = {"manual", "full_auto", "shutter_priority", "iris_priority", "bright", "unknown"}
TRACKING_STATES = {"off_commanded", "off_operator", "on", "unknown"}

# Fields whose change between the start and end of a measurement window
# invalidates that window's frames: they move the image or change its scale.
GEOMETRY_FIELDS = ("zoom_position", "focus_position", "pan_position", "tilt_position",
                   "focus_mode", "exposure_mode", "shutter_position", "iris_position",
                   "gain_limit", "bright_position", "video_system", "power")


@dataclass
class OpticsState:
    camera_id: str
    source: str                      # visca_inquiry | operator | none
    taken_mono_ns: int
    focus_mode: str = "unknown"
    exposure_mode: str = "unknown"
    tracking: str = "unknown"
    zoom_position: int | None = None
    focus_position: int | None = None
    shutter_position: int | None = None
    iris_position: int | None = None
    gain_limit: int | None = None
    bright_position: int | None = None
    white_balance: str | None = None
    pan_position: int | None = None
    tilt_position: int | None = None
    power: str | None = None
    video_system: str | None = None
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.focus_mode not in FOCUS_MODES:
            raise ValueError(f"focus_mode {self.focus_mode!r} not in {sorted(FOCUS_MODES)}")
        if self.exposure_mode not in EXPOSURE_MODES:
            raise ValueError(f"exposure_mode {self.exposure_mode!r} not in {sorted(EXPOSURE_MODES)}")
        if self.tracking not in TRACKING_STATES:
            raise ValueError(f"tracking {self.tracking!r} not in {sorted(TRACKING_STATES)}")

    @property
    def verified(self) -> bool:
        return self.source == "visca_inquiry"

    def as_dict(self) -> dict:
        return asdict(self)

    def optics_id(self) -> str:
        body = {k: v for k, v in self.as_dict().items() if k not in ("taken_mono_ns", "extra")}
        digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
        return f"{self.camera_id}-{digest}"


@dataclass
class GateResult:
    ok: bool
    reasons: list[str]
    warnings: list[str]


def gate(state: OpticsState | None, now_ns: int, max_age_s: float = 600.0,
         receipt_max_age_s: float = 12 * 3600.0) -> GateResult:
    """Whether frames may be recorded as measurements under this optics state.

    A VISCA read-back is stale after `max_age_s`; a receipt (source "operator",
    loaded by `config.load_receipt` with its recorded time) after
    `receipt_max_age_s`.
    """
    if state is None or state.source == "none":
        return GateResult(False, ["no_optics_record"], [])
    reasons, warnings = [], []
    if state.focus_mode == "unknown":
        reasons.append("autofocus_state_unknown")
    elif state.focus_mode != "manual":
        reasons.append(f"focus_mode_{state.focus_mode}")
    if state.exposure_mode == "unknown":
        reasons.append("auto_exposure_state_unknown")
    elif state.exposure_mode != "manual":
        reasons.append(f"exposure_mode_{state.exposure_mode}")
    if state.tracking == "unknown":
        reasons.append("tracking_state_unknown")
    elif state.tracking == "on":
        reasons.append("tracking_on")
    limit = receipt_max_age_s if state.source == "operator" else max_age_s
    if now_ns - state.taken_mono_ns > limit * 1e9:
        reasons.append("optics_record_stale")
    if state.source == "operator":
        warnings.append("operator_entered_not_read_back")
    for name in ("zoom_position", "focus_position"):
        if getattr(state, name) is None:
            warnings.append(f"{name}_not_recorded")
    return GateResult(not reasons, reasons, warnings)


def changed_fields(before: OpticsState, after: OpticsState) -> dict:
    """Geometry-relevant fields that differ, as {field: [before, after]}.

    Only fields known in both states are compared; an operator file cannot
    show a change, which is why operator-sourced windows are flagged unverified.
    """
    out = {}
    for name in GEOMETRY_FIELDS:
        a, b = getattr(before, name), getattr(after, name)
        if a is not None and b is not None and a != b:
            out[name] = [a, b]
    return out


class OpticsProvider:
    """Supplies the current optics state of each camera.

    `refresh(camera_id)` re-reads it where a reading is possible (VISCA) and
    returns the stored state otherwise (operator file, unknown).
    """

    def __init__(self):
        self._states: dict[str, OpticsState] = {}
        self._readers: dict = {}

    def set_state(self, state: OpticsState) -> None:
        self._states[state.camera_id] = state

    def set_reader(self, camera_id: str, reader) -> None:
        """`reader()` returns a fresh OpticsState (e.g. a VISCA inquiry)."""
        self._readers[camera_id] = reader

    def can_refresh(self, camera_id: str) -> bool:
        return camera_id in self._readers

    def current(self, camera_id: str) -> OpticsState | None:
        return self._states.get(camera_id)

    def refresh(self, camera_id: str) -> OpticsState | None:
        reader = self._readers.get(camera_id)
        if reader is not None:
            self._states[camera_id] = reader()
        return self._states.get(camera_id)
