"""Capture configuration, optics receipts and clock-check receipts: loading and validation.

The templates in `examples/` mark every operator entry with FILL_ME or null.
`validate(path, "measurement")` refuses a configuration while any FILL_ME
remains anywhere in it (keys starting with "_" are notes), while a required
field is null or malformed, while an optics receipt is unfilled, stale, for
another camera, or shows autofocus, automatic exposure or tracking, or while
the clock check is missing, failed, or made with another Python clock or helper
build. `validate(path, "dry")` needs only distinct camera ids and unique IDs:
enough to open the cameras and measure what they deliver.

Relative paths in a configuration resolve from the configuration's directory.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time

import numpy as np

from .optics import EXPOSURE_MODES, OpticsState, gate
from .visca import SERIAL_BAUDS

PLACEHOLDER = "FILL_ME"
FORMAT_VERSION = 1
NOT_AVAILABLE = "not_available"
CAPTURE_SUBTYPES = ("dmb1", "jpeg", "420v", "420f", "yuvs", "2vuy")
COMPRESSED_SUBTYPES = ("dmb1", "jpeg")
RECEIPT_METHODS = ("camera_menu", "web_interface", "visca_inquiry")
RECEIPT_VALUES = ("zoom", "focus", "shutter", "iris", "gain", "white_balance")
CAMERA_ID = re.compile(r"[A-Za-z0-9_-]+")
FUTURE_SKEW_S = 300


class ConfigError(ValueError):
    def __init__(self, path, purpose: str, problems: list[str]):
        super().__init__(f"{path} is not valid for {purpose}:\n  " + "\n  ".join(problems))
        self.problems = problems


def placeholders(obj, path: str = "") -> list[str]:
    """JSON paths of every string still holding FILL_ME. Keys starting with '_' are notes."""
    out = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not str(key).startswith("_"):
                out += placeholders(value, f"{path}.{key}" if path else str(key))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            out += placeholders(value, f"{path}[{i}]")
    elif isinstance(obj, str) and PLACEHOLDER in obj:
        out.append(path)
    return out


def _filled(value) -> bool:
    return value is not None and not (isinstance(value, str) and (PLACEHOLDER in value or not value.strip()))


def parse_time(value) -> datetime | None:
    """An ISO 8601 time with a UTC offset, or None."""
    if not isinstance(value, str):
        return None
    try:
        t = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo is not None else None


def iso_time(wall_ns: int) -> str:
    return datetime.fromtimestamp(wall_ns / 1e9, timezone.utc).astimezone().isoformat(timespec="seconds")


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and np.isfinite(v)


def _age_problems(label: str, value, now_wall_ns: int, max_age_s: float | None) -> list[str]:
    t = parse_time(value)
    if t is None:
        return [f"{label} must be an ISO 8601 time with a UTC offset, e.g. 2026-10-05T09:30:00-05:00"]
    age_s = now_wall_ns / 1e9 - t.timestamp()
    if age_s < -FUTURE_SKEW_S:
        return [f"{label} {value} is in the future"]
    if max_age_s is not None and age_s > max_age_s:
        return [f"{label} {value} is {age_s / 3600:.1f} h old (limit {max_age_s / 3600:.1f} h)"]
    return []


# ---- optics receipts ----------------------------------------------------------------------------

@dataclass
class Receipt:
    path: Path
    data: dict
    problems: list[str]
    state: OpticsState | None


def receipt_from_state(state: OpticsState, recorded_by: str, wall_ns: int, tracking: str,
                       exchanges: list | None = None) -> dict:
    """A receipt (format_version 1) holding a VISCA read-back."""
    def value(v):
        return NOT_AVAILABLE if v is None else v
    return {
        "format_version": FORMAT_VERSION, "camera_id": state.camera_id, "recorded_at": iso_time(wall_ns),
        "recorded_by": recorded_by, "method": "visca_inquiry", "focus_mode": state.focus_mode,
        "exposure_mode": state.exposure_mode, "tracking": tracking,
        "zoom": value(state.zoom_position), "focus": value(state.focus_position),
        "shutter": value(state.shutter_position), "iris": value(state.iris_position),
        "gain": value(state.gain_limit), "white_balance": value(state.white_balance),
        "lens_attachment": PLACEHOLDER + ": e.g. Raynox DCR-250, or none",
        "notes": "", "visca": {k: state.extra.get(k) for k in ("transport", "address", "version", "inquiry_failures")},
        "visca_exchanges": exchanges or [],
    }


def load_receipt(path, camera_id: str | None = None, now_mono_ns: int | None = None,
                 now_wall_ns: int | None = None, max_age_s: float | None = 12 * 3600) -> Receipt:
    """Read and check one optics receipt; build its OpticsState when its fields are usable.

    The state's taken time is the receipt's recorded_at, carried onto the
    monotonic clock, so a capture session's gate measures the receipt's real age.
    """
    path = Path(path)
    now_mono_ns = time.monotonic_ns() if now_mono_ns is None else now_mono_ns
    now_wall_ns = time.time_ns() if now_wall_ns is None else now_wall_ns
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return Receipt(path, {}, [f"{path}: unreadable: {exc}"], None)
    if not isinstance(data, dict):
        return Receipt(path, {}, [f"{path}: not a JSON object"], None)
    problems = [f"{p} still holds {PLACEHOLDER}" for p in placeholders(data)]
    pending = set(p.split(".")[0].split("[")[0] for p in placeholders(data))
    if data.get("format_version") != FORMAT_VERSION:
        problems.append(f"format_version must be {FORMAT_VERSION}")
    cid = data.get("camera_id")
    if "camera_id" not in pending:
        if not (isinstance(cid, str) and CAMERA_ID.fullmatch(cid)):
            problems.append("camera_id must be letters, digits, '_' or '-'")
        elif camera_id is not None and cid != camera_id:
            problems.append(f"camera_id {cid!r} does not match the configuration's {camera_id!r}")
    if "recorded_at" not in pending:
        problems += _age_problems("recorded_at", data.get("recorded_at"), now_wall_ns, max_age_s)
    if "recorded_by" not in pending and not _filled(data.get("recorded_by")):
        problems.append("recorded_by must name who recorded the settings")
    if "method" not in pending and data.get("method") not in RECEIPT_METHODS:
        problems.append(f"method must be one of {RECEIPT_METHODS}")
    checks = (("focus_mode", ("manual", "auto", "one_push")),
              ("exposure_mode", tuple(sorted(EXPOSURE_MODES - {"unknown"}))),
              ("tracking", ("off", "on", "unknown")))
    for key, allowed in checks:
        if key not in pending and data.get(key) not in allowed:
            problems.append(f"{key} must be one of {allowed}")
    for key in RECEIPT_VALUES:
        v = data.get(key)
        if key not in pending and not (_is_number(v) or (isinstance(v, str) and v.strip())):
            problems.append(f"{key} must be a value as displayed or read back, or {NOT_AVAILABLE!r}")
    if "lens_attachment" not in pending and not _filled(data.get("lens_attachment")):
        problems.append("lens_attachment must name the attached lens, or 'none'")
    state = None
    usable = (isinstance(cid, str) and CAMERA_ID.fullmatch(cid) and parse_time(data.get("recorded_at"))
              and all(data.get(k) in allowed for k, allowed in checks))
    if usable:
        age_ns = int(now_wall_ns - parse_time(data["recorded_at"]).timestamp() * 1e9)
        numbers = {k: data[k] for k in RECEIPT_VALUES if _is_number(data.get(k))}
        displays = {k: data[k] for k in RECEIPT_VALUES if isinstance(data.get(k), str)}
        state = OpticsState(
            camera_id=cid, source="operator", taken_mono_ns=now_mono_ns - age_ns,
            focus_mode=data["focus_mode"], exposure_mode=data["exposure_mode"],
            tracking={"off": "off_operator", "on": "on", "unknown": "unknown"}[data["tracking"]],
            zoom_position=numbers.get("zoom"), focus_position=numbers.get("focus"),
            shutter_position=numbers.get("shutter"), iris_position=numbers.get("iris"),
            gain_limit=numbers.get("gain"),
            white_balance=str(data["white_balance"]) if data.get("white_balance") is not None else None,
            extra={"receipt": str(path), "recorded_at": data.get("recorded_at"),
                   "recorded_by": data.get("recorded_by"), "method": data.get("method"),
                   "displayed": displays, "lens_attachment": data.get("lens_attachment"),
                   "notes": data.get("notes", "")})
    return Receipt(path, data, problems, state)


# ---- clock-check receipts -------------------------------------------------------------------------

def file_sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def clock_receipt(check: dict, helper_binary: Path, wall_ns: int) -> dict:
    import sys
    return {
        "format_version": FORMAT_VERSION, "checked_at": iso_time(wall_ns),
        "python": sys.executable, "python_version": sys.version.split()[0],
        "monotonic_implementation": time.get_clock_info("monotonic").implementation,
        "helper_binary": str(helper_binary), "helper_sha256": file_sha256(helper_binary),
        **check,
        "passed": bool(check.get("uptime_raw_within_bracket") and check.get("host_time_clock_within_bracket")),
    }


def clock_receipt_problems(path, helper_binary: Path) -> list[str]:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        return [f"clock-check receipt {path}: unreadable: {exc}"]
    problems = []
    if data.get("format_version") != FORMAT_VERSION:
        problems.append(f"clock-check receipt format_version must be {FORMAT_VERSION}")
    if data.get("passed") is not True:
        problems.append("clock check did not pass: a helper clock fell outside the time.monotonic_ns() bracket")
    current = time.get_clock_info("monotonic").implementation
    if data.get("monotonic_implementation") != current:
        problems.append(f"clock check used monotonic clock {data.get('monotonic_implementation')!r}; "
                        f"this Python uses {current!r}: run clock-check again")
    sha = file_sha256(helper_binary)
    if sha is None:
        problems.append(f"capture helper not built at {helper_binary}")
    elif data.get("helper_sha256") != sha:
        problems.append("the capture helper changed since the clock check: run clock-check again")
    return problems


# ---- capture configuration ------------------------------------------------------------------------

@dataclass
class CameraConfig:
    camera_id: str
    unique_id: str | None
    name: str | None
    position: str | None
    require_native_4k: bool
    verified_format: dict | None
    optics_source: str | None
    receipt: Receipt | None
    visca: dict | None

    @property
    def codec(self) -> str | None:
        vf = self.verified_format
        if not vf:
            return None
        if vf["pixel_format"] in COMPRESSED_SUBTYPES:
            return "jpeg"
        return "nv12" if vf["chroma"] else "gray8"


@dataclass
class CaptureConfig:
    path: Path
    data: dict
    cameras: list[CameraConfig]
    clock_receipt: Path | None
    receipt_max_age_s: float
    dry_problems: list[str] = field(default_factory=list)
    measurement_problems: list[str] = field(default_factory=list)

    def problems(self, purpose: str) -> list[str]:
        return self.dry_problems if purpose == "dry" else self.dry_problems + self.measurement_problems


def _verified_format_problems(prefix: str, vf, require_native_4k) -> list[str]:
    if not isinstance(vf, dict):
        return [f"{prefix} must be the block printed by observe.py format-report"]
    problems = []
    for key in ("width", "height", "fps", "pixel_format", "chroma", "measured_at", "measured_with"):
        if vf.get(key) is None:
            problems.append(f"{prefix}.{key} is null: fill it from observe.py format-report")
    w, h, fps = vf.get("width"), vf.get("height"), vf.get("fps")
    if w is not None and not (_is_int(w) and w > 0):
        problems.append(f"{prefix}.width must be a positive integer")
    if h is not None and not (_is_int(h) and h > 0):
        problems.append(f"{prefix}.height must be a positive integer")
    if fps is not None and not (_is_number(fps) and 0 < fps <= 240):
        problems.append(f"{prefix}.fps must be the measured frame rate")
    pf = vf.get("pixel_format")
    if pf is not None and pf not in CAPTURE_SUBTYPES:
        problems.append(f"{prefix}.pixel_format must be one of {CAPTURE_SUBTYPES}")
    chroma = vf.get("chroma")
    if chroma is not None and not isinstance(chroma, bool):
        problems.append(f"{prefix}.chroma must be true or false")
    if chroma is True and pf in COMPRESSED_SUBTYPES:
        problems.append(f"{prefix}.chroma applies only to decoded pixel formats")
    if vf.get("measured_at") is not None:
        problems += [f"{prefix}.{p}" for p in _age_problems("measured_at", vf.get("measured_at"), time.time_ns(), None)]
    if vf.get("measured_with") is not None and not _filled(vf.get("measured_with")):
        problems.append(f"{prefix}.measured_with must say how the format was measured")
    if require_native_4k is True and _is_int(w) and _is_int(h) and (w, h) != (3840, 2160):
        problems.append(f"{prefix} is {w}x{h}; require_native_4k accepts only 3840x2160")
    return problems


def _visca_problems(prefix: str, v) -> list[str]:
    if not isinstance(v, dict):
        return [f"{prefix} must describe the VISCA connection"]
    problems = []
    transport = v.get("transport")
    if transport not in ("serial", "tcp", "udp"):
        problems.append(f"{prefix}.transport must be serial, tcp or udp")
    address = v.get("address")
    if not (_is_int(address) and 1 <= address <= 7):
        problems.append(f"{prefix}.address must be the camera's VISCA address, 1-7")
    if transport == "serial":
        if not _filled(v.get("serial_port")):
            problems.append(f"{prefix}.serial_port must name the serial device")
        if v.get("baud") not in SERIAL_BAUDS:
            problems.append(f"{prefix}.baud must be one of {SERIAL_BAUDS}")
        for key in ("host", "port"):
            if v.get(key) is not None:
                problems.append(f"{prefix}.{key} must be null for a serial connection")
    elif transport in ("tcp", "udp"):
        if not _filled(v.get("host")):
            problems.append(f"{prefix}.host must be the camera's IP address")
        if not (_is_int(v.get("port")) and 1 <= v.get("port") <= 65535):
            problems.append(f"{prefix}.port must be a port number")
        for key in ("serial_port", "baud"):
            if v.get(key) is not None:
                problems.append(f"{prefix}.{key} must be null for a {transport} connection")
    return problems


def load_config(path, helper_binary: Path | None = None, now_mono_ns: int | None = None,
                now_wall_ns: int | None = None) -> CaptureConfig:
    """Parse a capture configuration and collect its problems for dry and measurement capture."""
    from . import helper_stream
    path = Path(path)
    helper_binary = Path(helper_binary) if helper_binary else helper_stream.BINARY
    now_mono_ns = time.monotonic_ns() if now_mono_ns is None else now_mono_ns
    now_wall_ns = time.time_ns() if now_wall_ns is None else now_wall_ns
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return CaptureConfig(path, {}, [], None, 0.0, [f"{path}: unreadable: {exc}"])
    base = path.parent
    dry, meas = [], []
    meas += [f"{p} still holds {PLACEHOLDER}" for p in placeholders(data)]
    if data.get("format_version") != FORMAT_VERSION:
        dry.append(f"format_version must be {FORMAT_VERSION}")
    hours = data.get("receipt_max_age_hours")
    if not (_is_number(hours) and hours > 0):
        meas.append("receipt_max_age_hours must be a positive number of hours")
        hours = 12
    max_age_s = float(hours) * 3600
    clock_path = None
    clock = data.get("clock_check")
    if not isinstance(clock, dict) or not _filled(clock.get("receipt")):
        meas.append("clock_check.receipt must name the file written by observe.py clock-check --out")
    else:
        clock_path = (base / clock["receipt"]).expanduser()
        meas += clock_receipt_problems(clock_path, helper_binary)
    cameras = []
    raw = data.get("cameras")
    if not isinstance(raw, list) or not raw:
        dry.append("cameras must list at least one camera")
        raw = []
    seen_ids, seen_uids = Counter(), Counter()
    for i, cam in enumerate(raw):
        p = f"cameras[{i}]"
        if not isinstance(cam, dict):
            dry.append(f"{p} must be an object")
            continue
        cid = cam.get("camera_id")
        if not (isinstance(cid, str) and CAMERA_ID.fullmatch(cid)):
            dry.append(f"{p}.camera_id must be letters, digits, '_' or '-'")
            cid = f"camera{i}"
        seen_ids[cid] += 1
        uid = cam.get("unique_id")
        if not _filled(uid):
            dry.append(f"{p}.unique_id must be the AVFoundation unique ID listed by observe.py cameras")
            uid = None
        else:
            seen_uids[uid] += 1
        if not _filled(cam.get("name")):
            meas.append(f"{p}.name must be the name listed with that unique ID")
        if not _filled(cam.get("position")):
            meas.append(f"{p}.position must label the camera's physical position")
        native = cam.get("require_native_4k")
        if not isinstance(native, bool):
            meas.append(f"{p}.require_native_4k must be true or false")
        vf = cam.get("verified_format")
        vf_problems = _verified_format_problems(f"{p}.verified_format", vf, native)
        meas += vf_problems
        optics = cam.get("optics") if isinstance(cam.get("optics"), dict) else {}
        source = optics.get("source")
        receipt = None
        if source == "operator":
            if not _filled(optics.get("receipt")):
                meas.append(f"{p}.optics.receipt must name this camera's filled optics receipt")
            else:
                receipt = load_receipt((base / optics["receipt"]).expanduser(), cid, now_mono_ns, now_wall_ns,
                                       max_age_s)
                meas += [f"{p}.optics.receipt: {x}" for x in receipt.problems]
                if receipt.state is not None and not receipt.problems:
                    verdict = gate(receipt.state, now_mono_ns, receipt_max_age_s=max_age_s)
                    meas += [f"{p}.optics.receipt: measurement gate: {r}" for r in verdict.reasons]
            if optics.get("visca") is not None:
                meas.append(f"{p}.optics.visca must be null when the source is operator")
        elif source == "visca":
            meas += _visca_problems(f"{p}.optics.visca", optics.get("visca"))
            if optics.get("receipt") is not None:
                meas.append(f"{p}.optics.receipt must be null when the source is visca (it is read back live)")
        else:
            meas.append(f"{p}.optics.source must be operator or visca")
        cameras.append(CameraConfig(
            camera_id=cid, unique_id=uid, name=cam.get("name") if _filled(cam.get("name")) else None,
            position=cam.get("position") if _filled(cam.get("position")) else None,
            require_native_4k=native if isinstance(native, bool) else True,
            verified_format=vf if isinstance(vf, dict) and not vf_problems else None,
            optics_source=source if source in ("operator", "visca") else None, receipt=receipt,
            visca=optics.get("visca") if source == "visca" and not _visca_problems("", optics.get("visca")) else None))
    dry += [f"camera_id {c!r} appears {n} times" for c, n in seen_ids.items() if n > 1]
    dry += [f"unique_id {u!r} appears {n} times" for u, n in seen_uids.items() if n > 1]
    return CaptureConfig(path, data, cameras, clock_path, max_age_s, dry, meas)


def validate(path, purpose: str, helper_binary: Path | None = None) -> CaptureConfig:
    if purpose not in ("dry", "measurement"):
        raise ValueError("purpose is dry or measurement")
    cfg = load_config(path, helper_binary)
    problems = cfg.problems(purpose)
    if problems:
        raise ConfigError(path, purpose, problems)
    return cfg


# ---- measured format ------------------------------------------------------------------------------

def measured_format(reader) -> dict:
    """Per camera: what a session's frames show about the delivered format, and a verified_format block.

    The block is filled only when every frame agrees on size, codec and pixel
    format; the frame rate is the median presentation-time interval.
    """
    records = reader.records()
    closed = reader.closing["closed_wall_utc"] if reader.closing else None
    out = {}
    for cam in sorted({r["camera_id"] for r in records if r["kind"] == "frame"}):
        frames = [r for r in records if r["kind"] == "frame" and r["camera_id"] == cam]
        sizes = Counter(f"{f['width']}x{f['height']}" for f in frames if f["dims_verified"])
        codecs = Counter(f["codec"] for f in frames)
        subtypes = Counter(f.get("subtype") for f in frames)
        pts = [f["device_pts_ns"] for f in frames if f["device_pts_ns"] is not None]
        intervals = np.diff(pts) if len(pts) > 1 else np.array([])
        intervals = intervals[intervals > 0]
        gaps = Counter()
        for g in records:
            if g["kind"] == "frame_gap" and g["camera_id"] == cam:
                gaps[g["evidence"]] += g["missing_estimate"]
        info = next((r["source_info"] for r in records if r["kind"] == "camera" and r["camera_id"] == cam), {})
        problems = []
        if len(sizes) != 1:
            problems.append(f"frame sizes not uniform or unverified: {dict(sizes)}")
        if len(codecs) != 1:
            problems.append(f"codecs not uniform: {dict(codecs)}")
        if len(subtypes) != 1 or None in subtypes:
            problems.append(f"pixel formats not uniform or not reported: {dict(subtypes)}")
        if len(intervals) < 10:
            problems.append("fewer than 10 presentation-time intervals: capture longer")
        vf = {"width": None, "height": None, "fps": None, "pixel_format": None, "chroma": None,
              "measured_at": closed, "measured_with": f"observe.py format-report {reader.session_id}"}
        if not problems:
            (size, _), = sizes.items()
            w, h = (int(v) for v in size.split("x"))
            codec = next(iter(codecs))
            vf.update(width=w, height=h, fps=round(1e9 / float(np.median(intervals)), 3),
                      pixel_format=next(iter(subtypes)), chroma=codec == "nv12")
        out[cam] = {
            "verified_format": vf, "consistent": not problems, "problems": problems,
            "evidence": {"frames": len(frames), "sizes": dict(sizes), "codecs": dict(codecs),
                         "pixel_formats": {str(k): v for k, v in subtypes.items()},
                         "median_interval_ms": round(float(np.median(intervals)) / 1e6, 3) if len(intervals) else None,
                         "p95_interval_ms": round(float(np.quantile(intervals, 0.95)) / 1e6, 3) if len(intervals) else None,
                         "frame_gaps": dict(gaps), "active_format": info.get("active_format"),
                         "device_name": info.get("name"), "unique_id": info.get("unique_id")},
        }
    return out
