"""Camera capture onto the session timeline, with optics-gated measurement windows.

For each frame a source delivers, `CameraCapture.process` stamps
`time.monotonic_ns()` and wall time at receipt, assigns the next per-camera
sequence number, checks for dropped frames, verifies the delivered size, and
writes a `frame` record (and the frame bytes, when the storage policy keeps
them). Drops are logged as `frame_gap` records with their evidence:

    source_seq      the source's counter of delivered frames skipped values
                    (frames lost between the source process and this one)
    pts_gap         presentation times jumped by more than `DropDetector.tolerance`
                    frame intervals; the detail says how many source notices
                    preceded it
    source_notice   the source reported a dropped frame (AVFoundation's didDrop)
    host_queue      this process could not keep up and discarded a frame

A measurement window (`CaptureSession.measurement`) is opened only when every
camera's optics pass `optics.gate`: known manual focus, manual exposure and
tracking off. Otherwise the window is refused (`on_unknown="refuse"`, default)
or opened with its frames recorded as non-measurement and the reasons logged
(`on_unknown="log"`). Optics are recorded when a window opens and, where they
can be re-read, when it closes; a change between the two invalidates the window.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
import queue
import secrets
import threading

import numpy as np

from .clock import Clock
from .imageio import (JpegError, decode_jpeg, decode_pgm, encode_pgm, encode_png, jpeg_dimensions, nv12_to_rgb,
                      split_nv12)
from .optics import OpticsProvider, changed_fields, gate

NATIVE_4K = (3840, 2160)


@dataclass
class RawFrame:
    payload: object                    # bytes (jpeg, nv12) or ndarray (gray8/gray16)
    codec: str                         # jpeg | gray8 | gray16 | nv12
    width: int | None = None
    height: int | None = None
    source_seq: int | None = None
    device_pts_ns: int | None = None   # presentation time on the host clock, where the source has one
    source_host_ns: int | None = None  # the source process's own receipt stamp
    duration_ns: int | None = None
    subtype: str | None = None         # AVFoundation format subtype the frame arrived in


@dataclass
class SourceDrop:
    device_pts_ns: int | None
    reason: str


@dataclass
class SourceEvent:
    event: str
    detail: dict


class FrameSource(ABC):
    camera_id: str
    unique_id: str
    name: str

    @abstractmethod
    def start(self) -> dict:
        """Begin delivery; returns source information for the camera record."""

    @abstractmethod
    def read(self, timeout_s: float):
        """Next RawFrame, SourceDrop or SourceEvent; None at end of stream; raises queue.Empty on timeout."""

    def stop(self) -> None:
        pass


@dataclass
class CameraSpec:
    camera_id: str
    unique_id: str
    name: str = ""
    role: str = ""
    width: int = NATIVE_4K[0]
    height: int = NATIVE_4K[1]
    codec: str = "gray8"               # requested; each frame records the codec it arrived in
    fps: float = 30.0
    require_native_4k: bool = True


@dataclass
class StorePolicy:
    mode: str = "measurement"          # measurement | window_first | all | none
    every_n: int = 0                   # also keep every Nth frame outside windows (0 = none)
    pixel_format: str = "pgm"          # pgm (uncompressed) | png (lossless, needs Pillow) for decoded frames


class DropDetector:
    def __init__(self, nominal_interval_ns: int | None, tolerance: float = 1.5):
        self.nominal = nominal_interval_ns
        self.tolerance = tolerance
        self.last_source_seq = None
        self.last_pts = None
        self.notices_since_last = 0

    def notice(self) -> None:
        self.notices_since_last += 1

    def check(self, frame: RawFrame) -> list[dict]:
        gaps = []
        if frame.source_seq is not None:
            if self.last_source_seq is not None and frame.source_seq != self.last_source_seq + 1:
                gaps.append({"evidence": "source_seq", "missing_estimate": frame.source_seq - self.last_source_seq - 1,
                             "detail": {"previous": self.last_source_seq, "current": frame.source_seq}})
            self.last_source_seq = frame.source_seq
        interval = frame.duration_ns or self.nominal
        if frame.device_pts_ns is not None:
            if self.last_pts is not None and interval:
                dt = frame.device_pts_ns - self.last_pts
                if dt > self.tolerance * interval:
                    gaps.append({"evidence": "pts_gap", "missing_estimate": int(round(dt / interval)) - 1,
                                 "detail": {"pts_delta_ns": dt, "interval_ns": interval,
                                            "explained_by_source_notices": self.notices_since_last}})
                elif dt <= 0:
                    gaps.append({"evidence": "pts_not_increasing", "missing_estimate": 0,
                                 "detail": {"pts_delta_ns": dt}})
            self.last_pts = frame.device_pts_ns
        self.notices_since_last = 0
        return gaps


class MeasurementRefused(RuntimeError):
    def __init__(self, reasons: dict):
        super().__init__(f"measurement refused: {reasons}")
        self.reasons = reasons


@dataclass
class Window:
    window_id: str
    purpose: str
    trial_id: str | None
    measurement: bool
    optics_ids: dict
    reasons: dict
    start_ns: int
    frames: dict = field(default_factory=dict)       # camera_id -> [(record, payload)]
    gaps: dict = field(default_factory=dict)         # camera_id -> frames missing while the window was open
    end_ns: int | None = None
    valid: bool | None = None


class CameraCapture:
    def __init__(self, spec: CameraSpec, source: FrameSource, writer, clock: Clock | None = None,
                 store: StorePolicy | None = None, queue_frames: int = 8):
        self.spec, self.source, self.writer = spec, source, writer
        self.clock = clock or Clock()
        self.store = store or StorePolicy()
        self.detector = DropDetector(int(1e9 / spec.fps) if spec.fps else None)
        self.seq = -1
        self.window: Window | None = None
        self.optics_id: str | None = None
        self.lock = threading.Condition()
        self._q: queue.Queue = queue.Queue(maxsize=queue_frames)
        self._threads: list[threading.Thread] = []
        self._stop = threading.Event()
        self.ended = False

    def _gap(self, after_seq, evidence, missing, detail):
        self.writer.append("frame_gap", camera_id=self.spec.camera_id, after_seq=after_seq,
                           missing_estimate=int(missing), evidence=evidence, detail=detail)
        with self.lock:
            if self.window is not None and evidence != "pts_gap":   # a pts gap re-counts a notice
                cam = self.spec.camera_id
                self.window.gaps[cam] = self.window.gaps.get(cam, 0) + int(missing)

    def process(self, item, recv_ns: int | None = None, recv_wall_ns: int | None = None):
        """Record one item from the source. Returns the frame record for frames."""
        recv_ns = self.clock.monotonic_ns() if recv_ns is None else recv_ns
        recv_wall_ns = self.clock.wall_ns() if recv_wall_ns is None else recv_wall_ns
        cam = self.spec.camera_id
        if isinstance(item, SourceDrop):
            self.detector.notice()
            self._gap(self.seq if self.seq >= 0 else None, "source_notice", 1,
                      {"device_pts_ns": item.device_pts_ns, "reason": item.reason})
            return None
        if isinstance(item, SourceEvent):
            self.writer.append("source_event", camera_id=cam, event=item.event, detail=item.detail)
            return None
        frame: RawFrame = item
        for g in self.detector.check(frame):
            self._gap(self.seq if self.seq >= 0 else None, g["evidence"], g["missing_estimate"], g["detail"])
        self.seq += 1
        excluded = []
        width, height, verified = frame.width, frame.height, False
        if frame.codec == "jpeg":
            try:
                width, height = jpeg_dimensions(frame.payload)
                verified = True
            except JpegError as exc:
                excluded.append(f"unreadable_jpeg:{exc}")
            size = len(frame.payload)
        elif frame.codec == "nv12":
            size = len(frame.payload)
            verified = bool(width and height and size == width * height * 3 // 2)
            if not verified:
                excluded.append("nv12_size_mismatch")
        else:
            arr = np.asarray(frame.payload)
            if arr.ndim != 2:
                excluded.append("not_a_single_plane")
            else:
                height, width = arr.shape
                verified = True
            size = int(arr.nbytes)
        native = verified and (width, height) == NATIVE_4K
        if verified and (width, height) != (self.spec.width, self.spec.height):
            excluded.append(f"size_{width}x{height}_not_requested_{self.spec.width}x{self.spec.height}")
        if self.spec.require_native_4k and not native:
            excluded.append("not_native_4k")
        with self.lock:
            window = self.window
        measurement = bool(window and window.measurement and not excluded)
        if window and not window.measurement:
            excluded += [f"optics:{r}" for r in window.reasons.get(cam, [])]
        first_in_window = window is not None and not window.frames.get(cam)
        keep = (self.store.mode == "all" or (self.store.mode == "measurement" and window is not None)
                or (self.store.mode == "window_first" and first_in_window)
                or (self.store.every_n and self.seq % self.store.every_n == 0)) and self.store.mode != "none"
        rel = None
        if keep:
            if frame.codec == "jpeg":
                rel = self.writer.store_frame(cam, self.seq, frame.payload, "jpg")
            else:
                pixels = (np.frombuffer(frame.payload, np.uint8).reshape(height * 3 // 2, width)
                          if frame.codec == "nv12" else np.asarray(frame.payload))
                if self.store.pixel_format == "png":
                    rel = self.writer.store_frame(cam, self.seq, encode_png(pixels), "png")
                else:
                    rel = self.writer.store_frame(cam, self.seq, encode_pgm(pixels), "pgm")
        record = self.writer.append(
            "frame", mono_ns=recv_ns, wall_ns=recv_wall_ns, camera_id=cam, seq=self.seq,
            source_seq=frame.source_seq, recv_mono_ns=recv_ns, recv_wall_ns=recv_wall_ns,
            device_pts_ns=frame.device_pts_ns, source_host_ns=frame.source_host_ns, codec=frame.codec,
            width=width, height=height, bytes=size, dims_verified=verified, native_4k=native,
            stored=rel is not None, file=rel, measurement=measurement,
            window_id=window.window_id if window else None, optics_id=self.optics_id,
            excluded_reasons=excluded, subtype=frame.subtype)
        if window is not None:
            with self.lock:
                if self.window is window:
                    window.frames.setdefault(cam, []).append((record, frame.payload))
                    self.lock.notify_all()
        return record

    # -- threaded operation -----------------------------------------------------------------
    def start_thread(self) -> None:
        def reader():
            while not self._stop.is_set():
                try:
                    item = self.source.read(0.5)
                except queue.Empty:
                    continue
                if item is None:
                    break
                stamp = (self.clock.monotonic_ns(), self.clock.wall_ns())
                try:
                    self._q.put_nowait((item, stamp))
                except queue.Full:
                    if isinstance(item, RawFrame):
                        self._gap(self.seq if self.seq >= 0 else None, "host_queue", 1,
                                  {"device_pts_ns": item.device_pts_ns, "source_seq": item.source_seq})
            self._q.put((None, None))

        def writer():
            while True:
                item, stamp = self._q.get()
                if item is None:
                    with self.lock:
                        self.ended = True
                        self.lock.notify_all()
                    return
                self.process(item, *stamp)

        self._threads = [threading.Thread(target=reader, daemon=True), threading.Thread(target=writer, daemon=True)]
        for t in self._threads:
            t.start()

    def stop_thread(self, timeout_s: float = 5.0) -> None:
        self._stop.set()
        self.source.stop()
        for t in self._threads:
            t.join(timeout=timeout_s)


class CaptureSession:
    """Cameras of one session, the optics gate and measurement windows.

    `synchronous=True` pulls frames from the sources inside `collect` (tests and
    simulation); otherwise each camera runs reader and writer threads.
    """

    def __init__(self, writer, captures: list[CameraCapture], optics: OpticsProvider,
                 clock: Clock | None = None, on_unknown: str = "refuse", optics_max_age_s: float = 600.0,
                 synchronous: bool = False, receipt_max_age_s: float = 12 * 3600.0):
        if on_unknown not in ("refuse", "log"):
            raise ValueError("on_unknown is 'refuse' or 'log'")
        self.writer, self.captures, self.optics = writer, {c.spec.camera_id: c for c in captures}, optics
        self.clock = clock or Clock()
        self.on_unknown, self.optics_max_age_s, self.synchronous = on_unknown, optics_max_age_s, synchronous
        self.receipt_max_age_s = receipt_max_age_s

    def _log_optics(self, camera_id: str, context: str):
        state = self.optics.current(camera_id)
        verdict = gate(state, self.clock.monotonic_ns(), self.optics_max_age_s, self.receipt_max_age_s)
        optics_id = state.optics_id() if state else f"{camera_id}-none"
        self.writer.append("optics", camera_id=camera_id, optics_id=optics_id,
                           source=state.source if state else "none", state=state.as_dict() if state else {},
                           gate_ok=verdict.ok, gate_reasons=verdict.reasons, warnings=verdict.warnings,
                           context=context)
        self.captures[camera_id].optics_id = optics_id
        return state, verdict, optics_id

    def start(self) -> None:
        for cam_id, cap in self.captures.items():
            info = cap.source.start()
            self.writer.append("camera", camera_id=cam_id, unique_id=cap.spec.unique_id, name=cap.spec.name,
                               role=cap.spec.role,
                               requested_format={"width": cap.spec.width, "height": cap.spec.height,
                                                 "codec": cap.spec.codec, "fps": cap.spec.fps},
                               source_info=info or {})
            if self.optics.can_refresh(cam_id):
                self.optics.refresh(cam_id)
            self._log_optics(cam_id, "session_start")
            if not self.synchronous:
                cap.start_thread()

    def stop(self) -> None:
        for cap in self.captures.values():
            if self.synchronous:
                cap.source.stop()
            else:
                cap.stop_thread()

    @contextmanager
    def measurement(self, purpose: str, trial_id: str | None = None):
        reasons, optics_ids, before = {}, {}, {}
        for cam_id in self.captures:
            if self.optics.can_refresh(cam_id):
                self.optics.refresh(cam_id)
            state, verdict, optics_id = self._log_optics(cam_id, "window_start")
            optics_ids[cam_id], before[cam_id] = optics_id, state
            if not verdict.ok:
                reasons[cam_id] = verdict.reasons
        if reasons and self.on_unknown == "refuse":
            self.writer.append("measurement_refused", trial_id=trial_id, purpose=purpose, reasons=reasons)
            raise MeasurementRefused(reasons)
        window = Window(f"w-{secrets.token_hex(4)}", purpose, trial_id, not reasons, optics_ids, reasons,
                        self.clock.monotonic_ns())
        self.writer.append("measurement_start", window_id=window.window_id, trial_id=trial_id, purpose=purpose,
                           cameras=sorted(self.captures), optics_ids=optics_ids, measurement=window.measurement,
                           reasons=reasons)
        for cap in self.captures.values():
            with cap.lock:
                cap.window = window
        end_reasons = []
        try:
            yield window
        finally:
            for cap in self.captures.values():
                with cap.lock:
                    cap.window = None
            window.end_ns = self.clock.monotonic_ns()
            changed, unchanged = {}, None
            refreshed = [c for c in self.captures if self.optics.can_refresh(c)]
            if refreshed:
                unchanged = True
                for cam_id in refreshed:
                    self.optics.refresh(cam_id)
                    after, verdict, _ = self._log_optics(cam_id, "window_end")
                    diff = changed_fields(before[cam_id], after) if before[cam_id] and after else {}
                    if diff:
                        changed[cam_id] = diff
                        unchanged = False
                    if not verdict.ok:
                        end_reasons.append(f"{cam_id}:gate_failed_at_end:{','.join(verdict.reasons)}")
            if changed:
                end_reasons.append("optics_changed_during_window")
            if not window.measurement:
                end_reasons.append("window_opened_without_measurement_optics")
            window.valid = window.measurement and not end_reasons
            counts = {c: len(window.frames.get(c, [])) for c in self.captures}
            self.writer.append("measurement_end", window_id=window.window_id, frames=counts,
                               optics_unchanged=unchanged, changed_fields=changed, valid=window.valid,
                               reasons=end_reasons, gaps=dict(window.gaps), pairing=self._pairing(window))

    def _pairing(self, window: Window) -> dict:
        """Capture-time skew between the first two cameras' nearest frames in the window."""
        from .timeline import pair_frames
        cams = sorted(self.captures)
        if len(cams) < 2:
            return {}
        a = [r for r, _ in window.frames.get(cams[0], [])]
        b = [r for r, _ in window.frames.get(cams[1], [])]
        interval = max(int(1e9 / (self.captures[cams[0]].spec.fps or 30)), 1)
        pairs = pair_frames(a, b, max_skew_ns=interval // 2)
        skews = [abs(s) for _, _, s in pairs]
        return {"cameras": cams[:2], "pairs": len(pairs), "unpaired": len(a) + len(b) - 2 * len(pairs),
                "max_skew_ns": max(skews) if skews else None}

    def collect(self, window: Window, frames_per_camera: int, timeout_s: float = 5.0) -> dict:
        """Wait (or pull, when synchronous) until each camera has frames in the window."""
        for cam_id, cap in self.captures.items():
            if self.synchronous:
                while len(window.frames.get(cam_id, [])) < frames_per_camera:
                    item = cap.source.read(timeout_s)
                    if item is None:
                        break
                    cap.process(item)
            else:
                deadline = self.clock.monotonic_ns() + int(timeout_s * 1e9)
                with cap.lock:
                    while (len(window.frames.get(cam_id, [])) < frames_per_camera and not cap.ended
                           and self.clock.monotonic_ns() < deadline):
                        cap.lock.wait(timeout=0.05)
        return {c: list(window.frames.get(c, []))[:frames_per_camera] for c in self.captures}


def decode_payload(record: dict, payload) -> np.ndarray:
    """Pixels of an in-memory frame: gray for gray8/gray16, RGB for nv12 (BT.709 video range)."""
    if record["codec"] == "jpeg":
        return decode_jpeg(payload)
    if record["codec"] == "nv12":
        stacked = np.frombuffer(payload, np.uint8).reshape(record["height"] * 3 // 2, record["width"])
        return nv12_to_rgb(*split_nv12(stacked, record["height"]))
    return np.asarray(payload) if not isinstance(payload, (bytes, bytearray)) else decode_pgm(payload)


class CameraObserver:
    """Settled observations from measurement windows: extract, then average over frames.

    `extractors` maps camera_id to FeatureExtractor instances. Only measurement
    frames of a valid window whose capture time is at or after `not_before_ns`
    are used; capture time is the presentation time where the source gives one,
    otherwise receipt time minus `latency_allowance_ns`. A value enters the
    observation when at least `min_valid_fraction` of those frames yield it; its
    sigma is the standard error over frames (the extractor's own estimate for a
    single frame) and its confidence the mean extractor confidence times the
    valid fraction. Missing values are recorded as null.
    """

    def __init__(self, session: CaptureSession, extractors: dict, writer, clock: Clock | None = None,
                 frames_per_camera: int = 5, min_valid_fraction: float = 0.6, timeout_s: float = 5.0,
                 latency_allowance_ns: int = 100_000_000):
        self.session, self.extractors, self.writer = session, extractors, writer
        self.clock = clock or Clock()
        self.frames_per_camera, self.min_valid_fraction = frames_per_camera, min_valid_fraction
        self.timeout_s, self.latency_allowance_ns = timeout_s, latency_allowance_ns
        self._n = 0

    def capture_time(self, record: dict) -> int:
        if record["device_pts_ns"] is not None:
            return record["device_pts_ns"]
        return record["recv_mono_ns"] - self.latency_allowance_ns

    def observe(self, trial_id, prev_obs_id, cmd_ids, not_before_ns: int):
        from .proposal import Observation
        self.clock.sleep_ns(not_before_ns - self.clock.monotonic_ns())
        with self.session.measurement("observation", trial_id) as window:
            got = self.session.collect(window, self.frames_per_camera, self.timeout_s)
        values, sigma, conf, n_frames, frames, versions, early = {}, {}, {}, {}, {}, {}, {}
        times = []
        for cam_id, items in got.items():
            usable = []
            for r, payload in items:
                if not (r["measurement"] and window.valid):
                    continue
                if self.capture_time(r) < not_before_ns:
                    early[cam_id] = early.get(cam_id, 0) + 1
                    continue
                usable.append((r, payload))
                times.append(self.capture_time(r))
            n_frames[cam_id] = len(usable)
            frames[cam_id] = [r["seq"] for r, _ in usable]
            images = [decode_payload(r, p) for r, p in usable]
            for ex in self.extractors.get(cam_id, []):
                versions[f"{cam_id}.{ex.label}"] = f"{ex.name}/{ex.version}"
                results = [ex.run(img) for img in images]
                for key in ex.keys:
                    name = f"{cam_id}.{ex.label}.{key}"
                    got_rows = [(res.values[key], res.sigma.get(key, np.nan), res.confidence)
                                for res in results if res.valid]
                    frac = len(got_rows) / max(len(usable), 1)
                    if not got_rows or frac < self.min_valid_fraction:
                        values[name], sigma[name], conf[name] = None, None, 0.0
                        continue
                    vals = np.array([v for v, _, _ in got_rows])
                    values[name] = float(vals.mean())
                    sigma[name] = (float(vals.std(ddof=1) / np.sqrt(len(vals))) if len(vals) > 1
                                   else float(got_rows[0][1]))
                    conf[name] = float(np.mean([c for _, _, c in got_rows]) * frac)
        now = self.clock.monotonic_ns()
        obs_id = f"o{self._n:06d}-{secrets.token_hex(2)}"
        self._n += 1
        rec = dict(obs_id=obs_id, trial_id=trial_id, prev_obs_id=prev_obs_id, cmd_ids=list(cmd_ids),
                   t_start_ns=int(min(times) if times else now), t_end_ns=int(max(times) if times else now),
                   values=values, sigma=sigma, confidence=conf, n_frames=n_frames, frames=frames,
                   source="camera", extractors=versions, window_id=window.window_id,
                   window_valid=window.valid, frames_before_settle=early)
        self.writer.append("observation", **rec)
        return Observation(obs_id, rec["t_start_ns"], rec["t_end_ns"], values, sigma, conf, trial_id)


class ArraySource(FrameSource):
    """Frames from a callable that renders the current scene; used with the simulator and tests."""

    def __init__(self, camera_id: str, render, clock: Clock, fps: float = 30.0, unique_id: str = "synthetic",
                 drop_every: int = 0, codec: str = "gray8"):
        self.camera_id, self.unique_id, self.name = camera_id, unique_id, f"synthetic {camera_id}"
        self.render, self.clock, self.interval = render, clock, int(1e9 / fps)
        self.drop_every, self.codec = drop_every, codec
        self.n = 0              # frame periods elapsed
        self.delivered = 0      # frames delivered: the source's own sequence, as the helper counts it
        self.pending: deque = deque()

    def start(self) -> dict:
        return {"kind": "synthetic", "interval_ns": self.interval}

    def read(self, timeout_s: float):
        if self.pending:
            return self.pending.popleft()
        self.clock.sleep_ns(self.interval)
        self.n += 1
        if self.drop_every and self.n % self.drop_every == 0:
            drop = SourceDrop(self.clock.monotonic_ns(), "synthetic drop")
            self.clock.sleep_ns(self.interval)
            self.n += 1
            self.pending.append(self._frame())
            return drop                     # the notice arrives before the next delivered frame
        return self._frame()

    def _frame(self) -> RawFrame:
        img = self.render()
        self.delivered += 1
        now = self.clock.monotonic_ns()
        return RawFrame(img, self.codec, img.shape[1], img.shape[0], self.delivered, now, now, self.interval)
