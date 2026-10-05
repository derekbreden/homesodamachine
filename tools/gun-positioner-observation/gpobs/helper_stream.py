"""The capture helper's stream, its launch, and camera enumeration on macOS.

`helper/GPOCapture` (Swift, AVFoundation) selects a camera by its AVFoundation
unique ID, sets a 3840x2160 format, asks for samples in the device's native
format, and writes each sample to stdout as

    b"GPO1" | u32le header length | u32le payload length | header JSON | payload

Header types: hello (device and active format), frame (seq, pts_ns, host_ns,
duration_ns, subtype, codec, width, height), drop (AVFoundation's didDrop
notice), error, bye. Frame payloads: codec "jpeg" is a compressed native sample
byte for byte; "gray8" is the luma plane of a decoded sample; "nv12" is luma
followed by interleaved CbCr. On this Mac AVFoundation lists the bench's UVC
Motion-JPEG camera only in decoded formats ('420v', 'yuvs'), so a 4K Motion-JPEG
stream is expected to arrive as "gray8"/"nv12" pixels decoded by macOS. `pts_ns` is the sample's
presentation time converted to the host clock; `host_ns` is the helper's
CLOCK_UPTIME_RAW stamp in its sample callback. Python stamps
`time.monotonic_ns()` when the whole message has been read: that is the frame's
receipt time on the session timeline.

Launch: `exec` runs the helper as a child process (camera permission then
belongs to the terminal application that runs Python); `open` launches the
GPOCapture.app bundle through LaunchServices with its stdout connected to a
FIFO, so the bundle holds its own camera permission, as PanelCamShot does.

Neither capture path has run against a camera; the protocol, the parser, both
launch paths and the clock agreement are exercised with the helper's synthetic
mode.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import struct
import subprocess
import tempfile
import threading
import time

from .capture import FrameSource, RawFrame, SourceDrop, SourceEvent

MAGIC = b"GPO1"
HELPER_DIR = Path(__file__).resolve().parent.parent / "helper"
APP = HELPER_DIR / "build" / "GPOCapture.app"
BINARY = APP / "Contents" / "MacOS" / "GPOCapture"


class ProtocolError(RuntimeError):
    pass


def _read_exact(stream, n: int) -> bytes:
    chunks, got = [], 0
    while got < n:
        b = stream.read(n - got)
        if not b:
            break
        chunks.append(b)
        got += len(b)
    return b"".join(chunks)


def read_message(stream):
    """(header, payload), or None at a clean end of stream."""
    head = _read_exact(stream, 12)
    if not head:
        return None
    if len(head) < 12:
        raise ProtocolError("stream ended inside a message header")
    if head[:4] != MAGIC:
        raise ProtocolError(f"bad magic {head[:4]!r}")
    hlen, plen = struct.unpack("<II", head[4:])
    if hlen > 1 << 20 or plen > 256 << 20:
        raise ProtocolError("implausible message length")
    header = _read_exact(stream, hlen)
    payload = _read_exact(stream, plen)
    if len(header) < hlen or len(payload) < plen:
        raise ProtocolError("stream ended inside a message body")
    return json.loads(header), payload


def encode_message(header: dict, payload: bytes = b"") -> bytes:
    h = json.dumps(header, separators=(",", ":")).encode()
    return MAGIC + struct.pack("<II", len(h), len(payload)) + h + payload


def to_item(header: dict, payload: bytes):
    kind = header.get("type")
    if kind == "frame":
        codec = header.get("codec", "jpeg")
        w, h = header.get("width"), header.get("height")
        body = payload
        if codec == "gray8" and w and h and len(payload) == w * h:
            import numpy as np
            body = np.frombuffer(payload, dtype=np.uint8).reshape(h, w)
        return RawFrame(body, codec, w, h, header.get("seq"), header.get("pts_ns"), header.get("host_ns"),
                        header.get("duration_ns"), header.get("subtype"))
    if kind == "drop":
        return SourceDrop(header.get("pts_ns"), header.get("reason") or "unspecified")
    return SourceEvent(kind or "unknown", {k: v for k, v in header.items() if k != "type"})


class HelperProcess:
    """A running helper whose stdout is a binary stream of messages."""

    def __init__(self, args: list[str], mode: str = "exec", log_path: Path | None = None,
                 open_timeout_s: float = 20.0):
        if mode not in ("exec", "open"):
            raise ValueError("mode is exec or open")
        self.mode = mode
        self.log_path = Path(log_path) if log_path else Path(tempfile.mkstemp(prefix="gpocapture-", suffix=".log")[1])
        self._tmp = None
        if mode == "exec":
            if not BINARY.exists():
                raise FileNotFoundError(f"build the helper first: {HELPER_DIR / 'build.sh'}")
            self.log_fh = open(self.log_path, "ab")
            self.proc = subprocess.Popen([str(BINARY), *args], stdout=subprocess.PIPE, stderr=self.log_fh)
            self.stream = self.proc.stdout
            return
        if not APP.exists():
            raise FileNotFoundError(f"build the helper first: {HELPER_DIR / 'build.sh'}")
        self._tmp = tempfile.TemporaryDirectory(prefix="gpocapture-")
        fifo = Path(self._tmp.name) / "stream"
        os.mkfifo(fifo)
        self.proc = subprocess.Popen(["open", "-n", "-W", "-g", "-o", str(fifo), "--stderr", str(self.log_path),
                                      str(APP), "--args", *args])
        holder: dict = {}

        def opener():
            holder["fh"] = open(fifo, "rb")

        t = threading.Thread(target=opener, daemon=True)
        t.start()
        deadline = time.monotonic() + open_timeout_s
        while t.is_alive() and time.monotonic() < deadline and self.proc.poll() is None:
            t.join(0.05)
        if t.is_alive():
            # The app never opened its stdout: unblock our open with a writer of our own.
            os.close(os.open(fifo, os.O_WRONLY | os.O_NONBLOCK))
            t.join(1.0)
        self.stream = holder.get("fh")
        if self.stream is None:
            raise RuntimeError(f"helper did not connect its output; see {self.log_path}")

    def stop(self, timeout_s: float = 3.0) -> None:
        if self.mode == "exec" and self.proc.poll() is None:
            self.proc.terminate()
        try:
            self.proc.wait(timeout_s)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        if self.stream:
            self.stream.close()
        if getattr(self, "log_fh", None):
            self.log_fh.close()
        if self._tmp:
            self._tmp.cleanup()


class HelperSource(FrameSource):
    """Frames from the helper for one camera, selected by AVFoundation unique ID."""

    def __init__(self, camera_id: str, unique_id: str, width: int = 3840, height: int = 2160, fps: float = 30.0,
                 subtypes: str = "dmb1,jpeg,420v,420f,yuvs,2vuy", chroma: bool = False, mode: str = "open",
                 log_path: Path | None = None, extra_args: list[str] | None = None, name: str = ""):
        self.camera_id, self.unique_id, self.name = camera_id, unique_id, name
        self.args = ["capture", "--unique-id", unique_id, "--width", str(width), "--height", str(height),
                     "--fps", str(fps), "--subtypes", subtypes, "--chroma", "1" if chroma else "0"] + list(extra_args or [])
        self.mode, self.log_path = mode, log_path
        self.proc: HelperProcess | None = None
        self._q: queue.Queue = queue.Queue(maxsize=4)
        self._thread = None

    @classmethod
    def synthetic(cls, camera_id: str, frames: int = 10, width: int = 64, height: int = 36, fps: float = 30.0,
                  codec: str = "gray8", drop_at=(), mode: str = "exec") -> "HelperSource":
        """The helper's synthetic mode through the same stream path (no camera)."""
        src = cls(camera_id, "synthetic", width, height, fps, mode=mode, name="GPOCapture synthetic")
        src.args = ["synthetic", "--frames", str(frames), "--width", str(width), "--height", str(height),
                    "--fps", str(fps), "--codec", codec, "--drop-at", ",".join(map(str, drop_at))]
        return src

    def start(self) -> dict:
        self.proc = HelperProcess(self.args, self.mode, self.log_path)
        first = read_message(self.proc.stream)
        if first is None or first[0].get("type") != "hello":
            detail = first[0] if first else {}
            self.proc.stop()
            raise RuntimeError(f"helper did not start capture: {detail}")

        def pump():
            try:
                while True:
                    msg = read_message(self.proc.stream)
                    if msg is None:
                        break
                    self._q.put(to_item(*msg))
            except (ProtocolError, OSError, ValueError) as exc:
                self._q.put(SourceEvent("stream_error", {"error": str(exc)}))
            self._q.put(None)

        self._thread = threading.Thread(target=pump, daemon=True)
        self._thread.start()
        return {"kind": "gpocapture", "launch": self.mode, **first[0]}

    def read(self, timeout_s: float):
        return self._q.get(timeout=timeout_s)

    def stop(self) -> None:
        if self.proc:
            self.proc.stop()


def run_helper_json(args: list[str], timeout_s: float = 20.0):
    out = subprocess.run([str(BINARY), *args], capture_output=True, timeout=timeout_s, check=True)
    return json.loads(out.stdout)


def list_cameras() -> dict:
    """Video devices with their AVFoundation unique IDs.

    Uses the helper's `list` (unique ID, name, model, formats) when built, and
    `system_profiler SPCameraDataType` (unique ID, name, model) otherwise.
    Enumeration opens no stream.
    """
    if BINARY.exists():
        return {"source": "GPOCapture list", "devices": run_helper_json(["list"])}
    out = subprocess.run(["system_profiler", "SPCameraDataType", "-json"], capture_output=True, text=True,
                         timeout=60, check=True)
    devices = [{"unique_id": d.get("spcamera_unique-id"), "name": d.get("_name"),
                "model_id": d.get("spcamera_model-id"), "formats": None}
               for d in json.loads(out.stdout).get("SPCameraDataType", [])]
    return {"source": "system_profiler SPCameraDataType", "devices": devices}


def clock_check() -> dict:
    """Bracket the helper's CLOCK_UPTIME_RAW stamp between two time.monotonic_ns() reads."""
    before = time.monotonic_ns()
    got = run_helper_json(["clock"])
    after = time.monotonic_ns()
    return {"python_before_ns": before, "python_after_ns": after, **got,
            "uptime_raw_within_bracket": before <= got["uptime_raw_ns"] <= after,
            "host_time_clock_within_bracket": before <= got["host_time_clock_ns"] <= after}
